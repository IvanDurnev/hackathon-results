<template>
  <aside class="slide-navigator">
    <div v-if="mode === 'presentation'">
      <div
        v-for="(slide, idx) in slides"
        :key="slide.id"
        :class="['slide-thumb', { active: slide.id === activeSlideId }]"
        :style="thumbWrapperStyle"
        draggable="true"
        @click="select(slide.id)"
        @dragstart="onDragStart(idx, $event)"
        @dragover.prevent="onDragOver(idx)"
        @drop.prevent="onDrop(idx)"
      >
        <span class="thumb-index">{{ idx + 1 }}</span>
        <SlideThumbnail
          :slide="slide"
          :slide-size="doc.slideSize"
          :assets="doc.assets"
          :width-px="thumbWidth"
        />
      </div>
      <div class="add-element-bar" style="flex-direction: column; gap: 4px;">
        <button class="tb-btn primary" @click="openLayoutPicker">+ Слайд</button>
        <button class="tb-btn" :disabled="!activeSlide" @click="duplicateActive">Дублировать</button>
        <button class="tb-btn danger" :disabled="!activeSlide || slides.length <= 1" @click="deleteActive">Удалить</button>
      </div>
    </div>

    <div v-else>
      <div
        v-for="(layout, idx) in layouts"
        :key="layout.id"
        :class="['slide-thumb', { active: layout.id === activeLayoutId }]"
        :style="thumbWrapperStyle"
        @click="selectLayout(layout.id)"
      >
        <span class="thumb-index">{{ idx + 1 }}</span>
        <SlideThumbnail
          :slide="layout"
          :slide-size="doc.slideSize"
          :assets="doc.assets"
          :width-px="thumbWidth"
        />
        <div style="font-size:11px; padding:2px 6px; color:var(--muted);">{{ layout.name }}</div>
      </div>
      <div class="add-element-bar" style="flex-direction: column; gap: 4px;">
        <button class="tb-btn primary" @click="addLayout">+ Макет</button>
        <button class="tb-btn danger" :disabled="!activeLayout || layouts.length <= 1" @click="deleteLayout">Удалить макет</button>
      </div>
    </div>

    <Dialog v-model:visible="layoutPickerOpen" header="Выберите макет" modal :style="{ width: '420px' }">
      <div style="display:flex; flex-direction:column; gap:8px;">
        <button
          v-for="l in availableLayouts"
          :key="l.id"
          class="tb-btn"
          @click="addSlideFromLayout(l)"
          style="justify-content:flex-start;"
        >
          <i class="pi pi-plus" /> {{ l.name }} <span style="color:var(--muted); margin-left:auto;">{{ l.slideType }}</span>
        </button>
        <button class="tb-btn" @click="addBlankSlide" style="justify-content:flex-start;">
          <i class="pi pi-plus" /> Пустой слайд
        </button>
      </div>
    </Dialog>
  </aside>
</template>

<script>
import Dialog from 'primevue/dialog';
import SlideThumbnail from './SlideThumbnail.vue';
import { useDocumentStore } from '../../stores/document.js';
import { makeSlide, slideFromLayout } from '../../core/factories.js';
import { uid } from '../../core/ids.js';

export default {
  name: 'SlideNavigator',
  components: { Dialog, SlideThumbnail },
  props: {
    template: { type: Object, default: null }, // optional template doc when editing presentation
  },
  data() {
    return {
      thumbWidth: 180,
      dragFromIndex: null,
      layoutPickerOpen: false,
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    doc() { return this.docStore.doc; },
    mode() { return this.docStore.mode; },
    slides() { return this.doc?.slides || []; },
    layouts() { return this.doc?.layouts || []; },
    activeSlideId() { return this.docStore.activeSlideId; },
    activeLayoutId() { return this.docStore.activeLayoutId; },
    activeSlide() { return this.docStore.activeSlide; },
    activeLayout() {
      if (this.mode !== 'template') return null;
      return this.layouts.find((l) => l.id === this.activeLayoutId);
    },
    thumbWrapperStyle() {
      const ratio = this.doc.slideSize.heightEmu / this.doc.slideSize.widthEmu;
      return {
        width: `${this.thumbWidth + 4}px`,
        height: `${this.thumbWidth * ratio + 4}px`,
      };
    },
    availableLayouts() {
      if (this.template?.layouts?.length) return this.template.layouts;
      return [];
    },
  },
  methods: {
    select(id) {
      this.docStore.selectActiveSlide(id);
    },
    selectLayout(id) {
      this.docStore.selectActiveLayout(id);
    },
    onDragStart(idx, e) {
      this.dragFromIndex = idx;
      e.dataTransfer.effectAllowed = 'move';
    },
    onDragOver(idx) {
      // visual feedback handled by browser; nothing to do here
    },
    onDrop(toIdx) {
      if (this.dragFromIndex == null || this.dragFromIndex === toIdx) return;
      this.docStore.run({
        type: 'slide.reorder',
        payload: { fromIndex: this.dragFromIndex, toIndex: toIdx },
      });
      this.dragFromIndex = null;
    },
    openLayoutPicker() {
      if (!this.availableLayouts.length) {
        this.addBlankSlide();
        return;
      }
      this.layoutPickerOpen = true;
    },
    addBlankSlide() {
      const slide = makeSlide({ slideType: 'text' });
      this.docStore.run({ type: 'slide.add', payload: { slide } });
      this.docStore.selectActiveSlide(slide.id);
      this.layoutPickerOpen = false;
    },
    addSlideFromLayout(layout) {
      const slide = slideFromLayout(layout);
      this.docStore.run({ type: 'slide.add', payload: { slide } });
      this.docStore.selectActiveSlide(slide.id);
      this.layoutPickerOpen = false;
    },
    duplicateActive() {
      const slide = this.activeSlide;
      if (!slide) return;
      const copy = JSON.parse(JSON.stringify(slide));
      copy.id = uid('slide');
      copy.elements = copy.elements.map((el) => ({ ...el, id: uid('el') }));
      const idx = this.slides.findIndex((s) => s.id === slide.id);
      this.docStore.run({ type: 'slide.add', payload: { slide: copy, index: idx + 1 } });
      this.docStore.selectActiveSlide(copy.id);
    },
    deleteActive() {
      const slide = this.activeSlide;
      if (!slide) return;
      const idx = this.slides.findIndex((s) => s.id === slide.id);
      this.docStore.run({ type: 'slide.delete', slideId: slide.id });
      const next = this.slides[Math.max(0, idx - 1)];
      this.docStore.selectActiveSlide(next?.id || null);
    },
    addLayout() {
      const layout = {
        id: uid('layout'),
        name: 'Новый макет',
        slideType: 'text',
        background: { type: 'color', value: '#FFFFFF' },
        elements: [],
      };
      this.doc.layouts.push(layout);
      this.docStore.dirty = true;
      this.docStore.selectActiveLayout(layout.id);
    },
    deleteLayout() {
      const id = this.activeLayoutId;
      if (!id) return;
      const idx = this.layouts.findIndex((l) => l.id === id);
      this.doc.layouts = this.layouts.filter((l) => l.id !== id);
      this.docStore.dirty = true;
      const next = this.layouts[Math.max(0, idx - 1)];
      this.docStore.selectActiveLayout(next?.id || null);
    },
  },
};
</script>
