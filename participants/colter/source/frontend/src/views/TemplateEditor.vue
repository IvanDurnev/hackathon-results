<template>
  <div v-if="loaded" class="editor-shell">
    <EditorToolbar @save="save" />
    <SlideNavigator />
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
  name: 'TemplateEditor',
  components: { EditorToolbar, SlideNavigator, SlideCanvas, InspectorPanel },
  props: { id: { type: String, required: true } },
  data() { return { loaded: false, _toast: null, _saveTimer: null }; },
  computed: { docStore() { return useDocumentStore(); } },
  watch: {
    'docStore.dirty'(val) {
      if (!val) return;
      if (this._saveTimer) clearTimeout(this._saveTimer);
      this._saveTimer = setTimeout(() => this.save(true), 2000);
    },
    id: { handler(n, o) { if (n !== o) this.load(); } },
  },
  mounted() {
    this._toast = useToast();
    this.load();
  },
  beforeUnmount() {
    if (this._saveTimer) clearTimeout(this._saveTimer);
  },
  methods: {
    async load() {
      this.loaded = false;
      const doc = await api.getTemplate(this.id);
      this.docStore.loadTemplate(doc);
      this.loaded = true;
    },
    async save(silent = false) {
      if (!this.docStore.dirty) return;
      this.docStore.saving = true;
      try {
        await api.saveTemplate(this.docStore.doc);
        this.docStore.markSaved();
        if (!silent && this._toast) {
          this._toast.add({ severity: 'success', summary: 'Сохранено', life: 1500 });
        }
      } catch (err) {
        const detail = err?.detail?.detail?.issues || err?.detail || String(err);
        this._toast?.add({
          severity: 'error',
          summary: 'Ошибка сохранения',
          detail: typeof detail === 'string' ? detail : JSON.stringify(detail).slice(0, 400),
          life: 6000,
        });
      } finally {
        this.docStore.saving = false;
      }
    },
  },
};
</script>
