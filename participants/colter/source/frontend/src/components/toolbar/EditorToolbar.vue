<template>
  <div class="editor-toolbar">
    <button class="tb-btn ghost icon" title="На главную" @click="$router.push('/')">
      <AcIcon name="home" :size="15" />
    </button>
    <div class="toolbar-divider" />

    <input
      class="title-input"
      :value="docStore.doc.name"
      @input="(e) => updateName(e.target.value)"
    />
    <span class="save-status" :class="{ dirty: docStore.dirty }">
      <span class="dot"></span>
      <span>{{ docStore.dirty ? 'не сохранено' : (docStore.lastSavedAt ? 'сохранено' : '') }}</span>
    </span>

    <div class="toolbar-divider" />

    <button class="tb-btn ghost icon" :disabled="!docStore.canUndo" @click="docStore.undo()" title="Undo (⌘Z)">
      <AcIcon name="undo" :size="15" />
    </button>
    <button class="tb-btn ghost icon" :disabled="!docStore.canRedo" @click="docStore.redo()" title="Redo (⌘⇧Z)">
      <AcIcon name="redo" :size="15" />
    </button>

    <div class="toolbar-divider" />

    <button class="tb-btn ghost" @click="addText"><AcIcon name="text" :size="14" /> Текст</button>
    <button class="tb-btn ghost" :title="imageButtonTitle" @click="handleImageAction"><AcIcon name="image" :size="14" /> {{ imageButtonLabel }}</button>
    <button class="tb-btn ghost" @click="addRect"><AcIcon name="shape" :size="14" /> Фигура</button>
    <button class="tb-btn ghost" @click="addLine"><AcIcon name="line" :size="14" /> Линия</button>

    <div class="spacer" />

    <button class="tb-btn amber-soft" title="Скоро: AI помощник" @click="askAiHint">
      <AcIcon name="sparkle" :size="13" /> AI помощник
      <span class="ac-kbd" style="background: rgba(255,181,71,0.10); border-color: rgba(255,181,71,0.25); color: var(--amber-200);">⌘K</span>
    </button>

    <div class="zoom-group">
      <button class="tb-btn icon" @click="zoomOut"><AcIcon name="zoomOut" :size="13" /></button>
      <span class="zoom-label">{{ zoomLabel }}</span>
      <button class="tb-btn icon" @click="zoomIn"><AcIcon name="zoomIn" :size="13" /></button>
      <button class="tb-btn icon" :title="editorStore.autoFit ? 'Уже Fit' : 'Fit'" @click="editorStore.enableAutoFit()" :class="{ 'amber-soft': editorStore.autoFit }">F</button>
    </div>

    <button class="tb-btn" :class="{ 'amber-soft': editorStore.snap }" :title="editorStore.snap ? 'Snap включён' : 'Snap выключен'" @click="editorStore.toggleSnap()">
      <AcIcon name="grid" :size="13" /> Snap
    </button>

    <div class="toolbar-divider" />

    <button class="tb-btn primary" :disabled="docStore.saving" @click="$emit('save')">
      <AcIcon name="save" :size="13" /> Сохранить
    </button>
    <button v-if="docStore.mode === 'presentation'" class="tb-btn" @click="$emit('export-pptx')">
      <AcIcon name="download" :size="13" /> PPTX
    </button>

    <input ref="upload" type="file" accept="image/*" style="display:none" @change="onUpload" />
  </div>
</template>

<script>
import AcIcon from '../AcIcon.vue';
import { useDocumentStore } from '../../stores/document.js';
import { useEditorStore } from '../../stores/editor.js';
import { api } from '../../api/client.js';
import {
  makeImageElement,
  makeImagePlaceholderElement,
  makeLineElement,
  makeShapeElement,
  makeTextElement,
} from '../../core/factories.js';

export default {
  name: 'EditorToolbar',
  components: { AcIcon },
  emits: ['save', 'export-pptx'],
  computed: {
    docStore() { return useDocumentStore(); },
    editorStore() { return useEditorStore(); },
    isTemplateMode() {
      return this.docStore.mode === 'template';
    },
    imageButtonLabel() {
      return this.isTemplateMode ? 'Изображение' : 'Картинка';
    },
    imageButtonTitle() {
      return this.isTemplateMode ? 'Добавить заполнитель изображения' : 'Загрузить изображение';
    },
    zoomLabel() {
      if (this.editorStore.autoFit) return 'fit';
      return `${Math.round(this.editorStore.zoom * 100)}%`;
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
    addText() {
      const theme = this.docStore.doc?.theme;
      this.addElement(makeTextElement({
        style: {
          fontFamily: theme?.fonts?.body || 'Inter',
          fontSize: 24,
          fontWeight: 400,
          color: theme?.colors?.text || '#111827',
          align: 'left',
          valign: 'top',
          lineHeight: 1.4,
        },
      }));
    },
    addRect() { this.addElement(makeShapeElement('rect')); },
    addLine() { this.addElement(makeLineElement()); },
    addImagePlaceholder() {
      this.addElement(makeImagePlaceholderElement());
    },
    handleImageAction() {
      if (this.isTemplateMode) {
        this.addImagePlaceholder();
        return;
      }
      this.$refs.upload.click();
    },
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
    askAiHint() {
      // Placeholder while AI panel is wired up — keeps the button responsive.
    },
  },
};
</script>
