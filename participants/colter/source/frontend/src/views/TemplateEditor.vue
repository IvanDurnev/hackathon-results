<template>
  <div v-if="loaded" class="editor-shell">
    <EditorToolbar @save="save" />
    <SlideNavigator />
    <SlideCanvas />
    <InspectorPanel />
  </div>
  <div v-else-if="loadError" style="padding: 24px;">
    <p style="margin-top:0;">Не удалось открыть шаблон.</p>
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

export default {
  name: 'TemplateEditor',
  components: { EditorToolbar, SlideNavigator, SlideCanvas, InspectorPanel },
  props: { id: { type: String, required: true } },
  data() { return { loaded: false, loadError: null, _toast: null, _saveTimer: null, _savePromise: null }; },
  computed: { docStore() { return useDocumentStore(); } },
  watch: {
    'docStore.revision'() {
      if (!this.docStore.dirty) return;
      if (this._saveTimer) clearTimeout(this._saveTimer);
      this._saveTimer = setTimeout(() => this.save(true), 2000);
    },
    id: { handler(n, o) { if (n !== o) this.load(); } },
  },
  mounted() {
    this._toast = this.$toast;
    this.load();
  },
  beforeUnmount() {
    if (this._saveTimer) clearTimeout(this._saveTimer);
  },
  async beforeRouteLeave() {
    return this.flushPendingSave();
  },
  methods: {
    async load() {
      this.loaded = false;
      this.loadError = null;
      try {
        const doc = await api.getTemplate(this.id);
        this.docStore.loadTemplate(doc);
        this.loaded = true;
      } catch (err) {
        this.loadError = err;
        this._toast?.add({
          severity: 'error',
          summary: 'Не удалось открыть шаблон',
          detail: err?.detail ? JSON.stringify(err.detail).slice(0, 400) : String(err),
          life: 6000,
        });
      }
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
          await api.saveTemplate(this.docStore.doc);
          this.docStore.markSaved(revision);
          if (!silent && this._toast) {
            this._toast.add({ severity: 'success', summary: 'Сохранено', life: 1500 });
          }
          return true;
        } catch (err) {
          const detail = err?.detail?.detail?.issues || err?.detail || String(err);
          this._toast?.add({
            severity: 'error',
            summary: 'Ошибка сохранения',
            detail: typeof detail === 'string' ? detail : JSON.stringify(detail).slice(0, 400),
            life: 6000,
          });
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
  },
};
</script>
