<template>
  <div v-if="loaded" class="editor-shell">
    <EditorToolbar @save="save" @export-pptx="exportPptx" />
    <SlideNavigator :template="template" />
    <SlideCanvas />
    <InspectorPanel />
    <div v-if="pendingImageCount" class="image-jobs-banner">
      <span class="spinner-dot"></span>
      <span>Генерируем картинки: {{ pendingImageCount }} ещё в работе</span>
    </div>
  </div>
  <div v-else-if="loadError" style="padding: 24px;">
    <p style="margin-top:0;">Не удалось открыть презентацию.</p>
    <button class="tb-btn" @click="load">Повторить</button>
  </div>
  <div v-else style="padding: 24px;">Загрузка…</div>
</template>

<script>
import EditorToolbar from '../components/toolbar/EditorToolbar.vue';
import SlideNavigator from '../components/navigator/SlideNavigator.vue';
import SlideCanvas from '../components/editor/SlideCanvas.vue';
import InspectorPanel from '../components/inspector/InspectorPanel.vue';
import { useDocumentStore } from '../stores/document.js';
import { api } from '../api/client.js';

const POLL_INTERVAL_MS = 3000;

export default {
  name: 'PresentationEditor',
  components: { EditorToolbar, SlideNavigator, SlideCanvas, InspectorPanel },
  props: { id: { type: String, required: true } },
  data() {
    return {
      loaded: false,
      loadError: null,
      template: null,
      _saveTimer: null,
      _savePromise: null,
      _toast: null,
      _pollTimer: null,
      pendingImageCount: 0,
      appliedJobVersions: {},
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
  },
  watch: {
    'docStore.revision'() {
      if (!this.docStore.dirty) return;
      if (this._saveTimer) clearTimeout(this._saveTimer);
      this._saveTimer = setTimeout(() => this.save(true), 2000);
    },
    id: {
      handler(newId, oldId) {
        if (newId !== oldId) this.load();
      },
    },
    'docStore.imagePollKick'() {
      if (!this.loaded) return;
      this.startPolling();
      this.pollImageJobs(false);
    },
  },
  mounted() {
    this._toast = this.$toast;
    this.load();
    window.addEventListener('beforeunload', this.beforeUnload);
  },
  beforeUnmount() {
    window.removeEventListener('beforeunload', this.beforeUnload);
    this.stopPolling();
    if (this._saveTimer) clearTimeout(this._saveTimer);
  },
  async beforeRouteLeave() {
    return this.flushPendingSave();
  },
  methods: {
    async load() {
      this.loaded = false;
      this.loadError = null;
      this.appliedJobVersions = {};
      try {
        const doc = await api.getPresentation(this.id);
        this.docStore.loadPresentation(doc);
        if (doc.templateId) {
          try {
            this.template = await api.getTemplate(doc.templateId);
          } catch (_) {
            this.template = null;
          }
        }
        this.loaded = true;
        this.startPolling();
        this.pollImageJobs(true);
      } catch (err) {
        this.loadError = err;
        this._toast?.add({
          severity: 'error',
          summary: 'Не удалось открыть презентацию',
          detail: err?.detail ? JSON.stringify(err.detail).slice(0, 400) : String(err),
          life: 6000,
        });
      }
    },
    startPolling() {
      this.stopPolling();
      this._pollTimer = setInterval(() => this.pollImageJobs(false), POLL_INTERVAL_MS);
    },
    stopPolling() {
      if (this._pollTimer) {
        clearInterval(this._pollTimer);
        this._pollTimer = null;
      }
    },
    async pollImageJobs(initial) {
      if (!this.docStore.doc) return;
      try {
        const response = await api.getImageJobsStatus(this.id);
        const jobs = response?.jobs || [];
        if (!jobs.length) {
          this.pendingImageCount = 0;
          if (!initial) this.stopPolling();
          return;
        }
        let pending = 0;
        let mutated = false;
        for (const job of jobs) {
          if (job.status === 'pending' || job.status === 'in_progress') {
            pending += 1;
            continue;
          }
          if (job.status === 'failed') {
            const key = `${job.id}#v${job.version}`;
            if (!this.appliedJobVersions[key]) {
              this.appliedJobVersions[key] = true;
              this._toast?.add({
                severity: 'warn',
                summary: 'Не удалось сгенерировать картинку',
                detail: job.error || 'Попробуйте перегенерировать вручную.',
                life: 6000,
              });
            }
            continue;
          }
          if (job.status === 'ready' && job.assetId) {
            const key = `${job.id}#v${job.version}`;
            if (this.appliedJobVersions[key]) continue;
            this.appliedJobVersions[key] = true;
            if (this.applyImageJob(job)) mutated = true;
          }
        }
        this.pendingImageCount = pending;
        if (!pending && !initial) this.stopPolling();
        if (mutated && this._saveTimer == null) {
          this._saveTimer = setTimeout(() => this.save(true), 2000);
        }
      } catch (_) {
        // polling failures are silent — next tick retries
      }
    },
    applyImageJob(job) {
      const doc = this.docStore.doc;
      if (!doc) return false;
      const slide = doc.slides.find((s) => s.id === job.slideId);
      if (!slide) return false;
      const element = slide.elements.find((e) => e.id === job.elementId);
      if (!element || element.type !== 'image') return false;
      if (element.assetId === job.assetId) return false;
      if (job.asset && !doc.assets.some((a) => a.id === job.asset.id)) {
        doc.assets.push({
          id: job.asset.id,
          type: job.asset.type || 'image',
          mimeType: job.asset.mimeType,
          url: job.asset.url,
          fileName: job.asset.fileName,
        });
      }
      element.assetId = job.assetId;
      element.placeholder = null;
      const meta = { ...(element.meta || {}) };
      meta.imageGeneration = {
        ...(meta.imageGeneration || {}),
        status: 'ready',
        prompt: job.prompt,
        assetId: job.assetId,
      };
      element.meta = meta;
      this.docStore.markDirty();
      return true;
    },
    async save(silent = false) {
      if (this._savePromise) {
        await this._savePromise;
      }
      if (!this.docStore.dirty) return true;
      const revision = this.docStore.revision;
      this.docStore.saving = true;
      this._savePromise = (async () => {
        try {
          await api.savePresentation(this.docStore.doc);
          this.docStore.markSaved(revision);
          if (!silent && this._toast) {
            this._toast.add({ severity: 'success', summary: 'Сохранено', life: 1500 });
          }
          return true;
        } catch (err) {
          const detail = err?.detail?.detail?.issues || err?.detail || String(err);
          if (this._toast) {
            this._toast.add({
              severity: 'error',
              summary: 'Ошибка сохранения',
              detail: typeof detail === 'string' ? detail : JSON.stringify(detail).slice(0, 400),
              life: 6000,
            });
          }
          return false;
        } finally {
          this.docStore.saving = false;
          this._savePromise = null;
        }
      })();
      return this._savePromise;
    },
    async flushPendingSave() {
      if (this._saveTimer) {
        clearTimeout(this._saveTimer);
        this._saveTimer = null;
      }
      for (let attempt = 0; attempt < 3 && this.docStore.dirty; attempt += 1) {
        const ok = await this.save(true);
        if (!ok && this.docStore.dirty) return false;
      }
      return !this.docStore.dirty;
    },
    async exportPptx() {
      // ensure latest is saved first
      if (!(await this.flushPendingSave())) return;
      const url = api.exportPptxUrl(this.id);
      const res = await fetch(url, { method: 'POST' });
      if (!res.ok) {
        let detail;
        try { detail = await res.json(); } catch { detail = await res.text(); }
        this._toast?.add({
          severity: 'error',
          summary: 'Экспорт PPTX не выполнен',
          detail: typeof detail === 'string' ? detail : JSON.stringify(detail).slice(0, 400),
          life: 6000,
        });
        return;
      }
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${this.docStore.doc.name || this.id}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    beforeUnload(e) {
      if (this.docStore.dirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    },
  },
};
</script>

<style scoped>
.image-jobs-banner {
  position: fixed;
  bottom: 16px;
  right: 16px;
  background: rgba(20, 20, 32, 0.92);
  color: #fff;
  border: 1px solid rgba(255, 181, 71, 0.35);
  border-radius: 10px;
  padding: 8px 14px;
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.32);
  z-index: 50;
}
.spinner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffb547;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(0.7); opacity: 0.6; }
  50% { transform: scale(1); opacity: 1; }
}
</style>
