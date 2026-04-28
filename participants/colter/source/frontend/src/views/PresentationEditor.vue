<template>
  <div v-if="loaded" class="editor-shell">
    <EditorToolbar @save="save" @export-pptx="exportPptx" />
    <SlideNavigator :template="template" />
    <SlideCanvas />
    <InspectorPanel />
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
import { useToast } from 'primevue/usetoast';

export default {
  name: 'PresentationEditor',
  components: { EditorToolbar, SlideNavigator, SlideCanvas, InspectorPanel },
  props: { id: { type: String, required: true } },
  data() {
    return {
      loaded: false,
      template: null,
      _saveTimer: null,
      _toast: null,
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
  },
  watch: {
    'docStore.dirty'(val) {
      if (!val) return;
      if (this._saveTimer) clearTimeout(this._saveTimer);
      this._saveTimer = setTimeout(() => this.save(true), 2000);
    },
    id: {
      handler(newId, oldId) {
        if (newId !== oldId) this.load();
      },
    },
  },
  mounted() {
    this._toast = useToast();
    this.load();
    window.addEventListener('beforeunload', this.beforeUnload);
  },
  beforeUnmount() {
    window.removeEventListener('beforeunload', this.beforeUnload);
    if (this._saveTimer) clearTimeout(this._saveTimer);
  },
  methods: {
    async load() {
      this.loaded = false;
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
    },
    async save(silent = false) {
      if (!this.docStore.dirty) return;
      this.docStore.saving = true;
      try {
        await api.savePresentation(this.docStore.doc);
        this.docStore.markSaved();
        if (!silent && this._toast) {
          this._toast.add({ severity: 'success', summary: 'Сохранено', life: 1500 });
        }
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
      } finally {
        this.docStore.saving = false;
      }
    },
    async exportPptx() {
      // ensure latest is saved first
      if (this.docStore.dirty) await this.save(true);
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
