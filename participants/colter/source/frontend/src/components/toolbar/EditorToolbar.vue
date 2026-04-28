<template>
  <div class="editor-toolbar">
    <button class="tb-btn" @click="$router.push('/')"><i class="pi pi-home" /> На главную</button>
    <div class="toolbar-divider" />
    <input
      class="title"
      :value="docStore.doc.name"
      @input="(e) => updateName(e.target.value)"
      style="border:1px solid transparent; padding:4px 6px; border-radius:4px; min-width:240px;"
      @focus="(e) => e.target.style.border = '1px solid var(--panel-border)'"
      @blur="(e) => e.target.style.border = '1px solid transparent'"
    />
    <span style="color:var(--muted); font-size:12px;">{{ docStore.dirty ? '· не сохранено' : (docStore.lastSavedAt ? '✓ сохранено' : '') }}</span>

    <div class="toolbar-divider" />

    <button class="tb-btn" :disabled="!docStore.canUndo" @click="docStore.undo()" title="Undo (Ctrl/Cmd+Z)">
      <i class="pi pi-undo" />
    </button>
    <button class="tb-btn" :disabled="!docStore.canRedo" @click="docStore.redo()" title="Redo (Ctrl/Cmd+Shift+Z)">
      <i class="pi pi-refresh" />
    </button>

    <div class="toolbar-divider" />

    <button class="tb-btn" @click="addText"><i class="pi pi-pencil" /> Текст</button>
    <button class="tb-btn" @click="addImage"><i class="pi pi-image" /> Картинка</button>
    <button class="tb-btn" @click="addRect"><i class="pi pi-stop" /> Фигура</button>
    <button class="tb-btn" @click="addLine"><i class="pi pi-minus" /> Линия</button>

    <div class="spacer" />

    <div class="zoom-controls">
      <button class="tb-btn" @click="zoomOut">−</button>
      <span style="font-size:12px; min-width:50px; text-align:center;">{{ zoomPercent }}%</span>
      <button class="tb-btn" @click="zoomIn">+</button>
      <button class="tb-btn" @click="editorStore.enableAutoFit()">Fit</button>
    </div>

    <button class="tb-btn" :class="{ primary: editorStore.snap }" @click="editorStore.toggleSnap()">Snap</button>

    <div class="toolbar-divider" />

    <button class="tb-btn primary" :disabled="docStore.saving" @click="$emit('save')"><i class="pi pi-save" /> Сохранить</button>
    <button v-if="docStore.mode === 'presentation'" class="tb-btn" @click="$emit('export-pptx')"><i class="pi pi-download" /> PPTX</button>

    <input ref="upload" type="file" accept="image/*" style="display:none" @change="onUpload" />
  </div>
</template>

<script>
import { useDocumentStore } from '../../stores/document.js';
import { useEditorStore } from '../../stores/editor.js';
import { api } from '../../api/client.js';
import {
  makeImageElement,
  makeLineElement,
  makeShapeElement,
  makeTextElement,
} from '../../core/factories.js';

export default {
  name: 'EditorToolbar',
  emits: ['save', 'export-pptx'],
  computed: {
    docStore() { return useDocumentStore(); },
    editorStore() { return useEditorStore(); },
    zoomPercent() {
      if (this.editorStore.autoFit) return 'fit';
      return Math.round(this.editorStore.zoom * 100);
    },
  },
  methods: {
    updateName(name) {
      this.docStore.run({ type: 'doc.update', payload: { props: { name } } }, { coalesce: true });
    },
    addElement(el) {
      const slide = this.docStore.activeSlide;
      if (!slide) return;
      this.docStore.run({
        type: 'element.add',
        slideId: slide.id,
        payload: { element: el },
      });
      this.docStore.setSelection(el.id);
    },
    addText() { this.addElement(makeTextElement()); },
    addRect() { this.addElement(makeShapeElement('rect')); },
    addLine() { this.addElement(makeLineElement()); },
    addImage() { this.$refs.upload.click(); },
    async onUpload(e) {
      const file = e.target.files?.[0];
      if (!file) return;
      const asset = await api.uploadAsset(file);
      this.docStore.addAsset(asset);
      this.addElement(makeImageElement({ assetId: asset.id }));
      e.target.value = '';
    },
    zoomIn() {
      const cur = this.editorStore.autoFit ? 1 : this.editorStore.zoom;
      this.editorStore.setZoom(cur + 0.1);
    },
    zoomOut() {
      const cur = this.editorStore.autoFit ? 1 : this.editorStore.zoom;
      this.editorStore.setZoom(cur - 0.1);
    },
  },
};
</script>
