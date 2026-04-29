<template>
  <aside class="slide-navigator">
    <div v-if="mode === 'presentation'">
      <div class="slide-navigator-head">
        <span>Слайды · {{ slides.length }}</span>
        <div class="slide-navigator-head-actions">
          <button
            class="tb-btn ghost icon"
            style="width:22px;height:22px;"
            title="Дублировать активный слайд"
            :disabled="!activeSlide"
            @click="duplicateActive"
          >
            <AcIcon name="duplicate" :size="13" />
          </button>
          <button class="tb-btn ghost icon" style="width:22px;height:22px;" title="Добавить слайд" @click="openLayoutPicker">
            <AcIcon name="plus" :size="13" />
          </button>
        </div>
      </div>
      <div class="slide-navigator-list">
        <div
          v-for="(slide, idx) in slides"
          :key="slide.id"
          :class="['slide-thumb', { active: slide.id === activeSlideId }]"
          draggable="true"
          @click="select(slide.id)"
          @dragstart="onDragStart(idx, $event)"
          @dragenter.prevent
          @dragover.prevent="onDragOver(idx, $event)"
          @drop.prevent="onDrop(idx, $event)"
          @dragend="onDragEnd"
        >
          <div class="thumb-index">{{ String(idx + 1).padStart(2, '0') }}</div>
          <div class="thumb-frame">
            <SlideThumbnail
              :slide="slide"
              :slide-size="doc.slideSize"
              :assets="doc.assets"
              :width-px="170"
            />
          </div>
        </div>
        <button class="add-slide-btn" @click="openLayoutPicker">
          <AcIcon name="plus" :size="13" /> Слайд
        </button>
      </div>
      <div class="nav-actions">
        <button class="tb-btn" :disabled="!activeSlide" @click="duplicateActive">
          <AcIcon name="duplicate" :size="13" /> Дублировать
        </button>
        <button class="tb-btn danger" :disabled="!activeSlide || slides.length <= 1" @click="deleteActive">
          <AcIcon name="trash" :size="13" /> Удалить слайд
        </button>
      </div>
    </div>

    <div v-else>
      <div class="slide-navigator-head">
        <span>Макеты · {{ layouts.length }}</span>
        <div class="slide-navigator-head-actions">
          <button
            class="tb-btn ghost icon"
            style="width:22px;height:22px;"
            title="Дублировать активный макет"
            :disabled="!activeLayout"
            @click="duplicateLayout"
          >
            <AcIcon name="duplicate" :size="13" />
          </button>
          <button class="tb-btn ghost icon" style="width:22px;height:22px;" title="Добавить макет" @click="addLayout">
            <AcIcon name="plus" :size="13" />
          </button>
        </div>
      </div>
      <div class="slide-navigator-list">
        <div
          v-for="(layout, idx) in layouts"
          :key="layout.id"
          :class="['slide-thumb', { active: layout.id === activeLayoutId }]"
          @click="selectLayout(layout.id)"
        >
          <div class="thumb-index">{{ String(idx + 1).padStart(2, '0') }}</div>
          <div style="flex:1;">
            <div class="thumb-frame">
              <SlideThumbnail
                :slide="layout"
                :slide-size="doc.slideSize"
                :assets="doc.assets"
                :width-px="170"
              />
            </div>
            <div class="thumb-name">{{ layout.name }}</div>
          </div>
        </div>
      </div>
      <div class="nav-actions">
        <button class="tb-btn" :disabled="!activeLayout" @click="duplicateLayout">
          <AcIcon name="duplicate" :size="13" /> Дублировать макет
        </button>
        <button class="tb-btn danger" :disabled="!activeLayout || layouts.length <= 1" @click="deleteLayout">
          <AcIcon name="trash" :size="13" /> Удалить макет
        </button>
      </div>
    </div>

    <div v-if="layoutPickerOpen" class="modal-backdrop" @click.self="layoutPickerOpen = false">
      <div class="modal" style="width: 460px;">
        <div class="modal-head">
          <span>Добавить слайд</span>
          <button class="tb-btn ghost icon" @click="layoutPickerOpen = false">
            <AcIcon name="plus" :size="14" :stroke-width="2" style="transform: rotate(45deg);" />
          </button>
        </div>
        <div class="modal-body" style="gap:6px;">
          <button
            v-for="l in availableLayouts"
            :key="l.id"
            class="tb-btn"
            style="justify-content: flex-start;"
            @click="addSlideFromLayout(l)"
          >
            <AcIcon name="plus" :size="13" />
            {{ l.name }}
            <span style="color: var(--fg-4); margin-left: auto; font-family: var(--font-mono); font-size: 11px;">{{ l.slideType }}</span>
          </button>
          <button class="tb-btn" style="justify-content: flex-start;" @click="addBlankSlide">
            <AcIcon name="plus" :size="13" /> Пустой слайд
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
import AcIcon from '../AcIcon.vue';
import SlideThumbnail from './SlideThumbnail.vue';
import { useDocumentStore } from '../../stores/document.js';
import { makeBackgroundColor, makeSlide, slideFromLayout } from '../../core/factories.js';
import { uid } from '../../core/ids.js';

export default {
  name: 'SlideNavigator',
  components: { AcIcon, SlideThumbnail },
  props: { template: { type: Object, default: null } },
  data() {
    return {
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
    availableLayouts() {
      if (this.template?.layouts?.length) return this.template.layouts;
      return [];
    },
  },
  methods: {
    select(id) { this.docStore.selectActiveSlide(id); },
    selectLayout(id) { this.docStore.selectActiveLayout(id); },
    onDragStart(idx, e) {
      this.dragFromIndex = idx;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', String(idx));
    },
    onDragOver(idx, e) {
      if (this.dragFromIndex == null || this.dragFromIndex === idx) return;
      e.dataTransfer.dropEffect = 'move';
    },
    onDrop(toIdx, e) {
      const raw = e.dataTransfer.getData('text/plain');
      const fromIdx = this.dragFromIndex ?? (raw === '' ? null : Number(raw));
      if (!Number.isInteger(fromIdx) || fromIdx === toIdx) return;
      this.docStore.run({
        type: 'slide.reorder',
        payload: { fromIndex: fromIdx, toIndex: toIdx },
      });
      this.dragFromIndex = null;
    },
    onDragEnd() {
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
      const slide = makeSlide({
        slideType: 'text',
        background: makeBackgroundColor(this.doc?.theme?.colors?.background || '#FFFFFF'),
      });
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
        background: makeBackgroundColor(this.doc?.theme?.colors?.background || '#FFFFFF'),
        elements: [],
      };
      this.doc.layouts.push(layout);
      this.docStore.markDirty();
      this.docStore.selectActiveLayout(layout.id);
    },
    duplicateLayout() {
      const layout = this.activeLayout;
      if (!layout) return;
      const copy = JSON.parse(JSON.stringify(layout));
      copy.id = uid('layout');
      copy.name = `${layout.name} (копия)`;
      copy.elements = (copy.elements || []).map((el) => ({ ...el, id: uid('el') }));
      const idx = this.layouts.findIndex((item) => item.id === layout.id);
      this.doc.layouts.splice(idx + 1, 0, copy);
      this.docStore.markDirty();
      this.docStore.selectActiveLayout(copy.id);
    },
    deleteLayout() {
      const id = this.activeLayoutId;
      if (!id) return;
      const idx = this.layouts.findIndex((l) => l.id === id);
      this.doc.layouts = this.layouts.filter((l) => l.id !== id);
      this.docStore.markDirty();
      const next = this.layouts[Math.max(0, idx - 1)];
      this.docStore.selectActiveLayout(next?.id || null);
    },
  },
};
</script>
