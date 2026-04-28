<template>
  <div class="canvas-area" ref="area" @click="onAreaClick">
    <div
      class="slide-canvas-wrapper"
      :style="wrapperStyle"
    >
      <div
        class="slide-canvas"
        :style="canvasStyle"
        @mousedown.self="onBackgroundMouseDown"
      >
        <ElementFrame
          v-for="el in sortedElements"
          :key="el.id"
          :element="el"
          :scale="scale"
          :assets="doc.assets"
          :selected="selection.includes(el.id)"
          :editing="editingId === el.id"
          @drag-start="onDragStart"
          @resize-start="onResizeStart"
          @select="(e) => onElementSelect(el.id, e)"
          @start-edit="onStartEdit(el.id)"
          @commit-text="(p) => onCommitText(el.id, p)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ElementFrame from './ElementFrame.vue';
import { useDocumentStore } from '../../stores/document.js';
import { useEditorStore } from '../../stores/editor.js';
import { fitScale } from '../../core/emu.js';

export default {
  name: 'SlideCanvas',
  components: { ElementFrame },
  data() {
    return {
      areaSize: { w: 0, h: 0 },
      ro: null,
      drag: null,
      resize: null,
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    editorStore() { return useEditorStore(); },
    doc() { return this.docStore.doc; },
    slide() { return this.docStore.activeSlide; },
    selection() { return this.docStore.selection; },
    editingId() { return this.editorStore.editingElementId; },
    slideSize() { return this.doc?.slideSize || { widthEmu: 12192000, heightEmu: 6858000 }; },
    fitScaleVal() {
      return fitScale(
        this.areaSize.w,
        this.areaSize.h,
        this.slideSize.widthEmu,
        this.slideSize.heightEmu,
        32
      ) || 0.0000001;
    },
    scale() {
      const z = this.editorStore.zoom;
      return this.editorStore.autoFit ? this.fitScaleVal : this.fitScaleVal * z;
    },
    canvasStyle() {
      return {
        width: `${this.slideSize.widthEmu * this.scale}px`,
        height: `${this.slideSize.heightEmu * this.scale}px`,
        background: this.slideBackgroundCss,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      };
    },
    wrapperStyle() { return { borderRadius: '6px' }; },
    slideBackgroundCss() {
      const bg = this.slide?.background;
      if (!bg) return '#fff';
      if (bg.type === 'color') return bg.value;
      if (bg.type === 'image') {
        const a = (this.doc.assets || []).find((x) => x.id === bg.assetId);
        return a?.url ? `url("${a.url}")` : '#fff';
      }
      if (bg.type === 'gradient') {
        return `linear-gradient(${bg.angle || 0}deg, ${bg.from}, ${bg.to})`;
      }
      return '#fff';
    },
    sortedElements() {
      if (!this.slide) return [];
      return [...this.slide.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
    },
  },
  watch: {
    'editorStore.zoom'() {},
  },
  mounted() {
    this.ro = new ResizeObserver(() => this.measure());
    this.ro.observe(this.$refs.area);
    this.measure();
    window.addEventListener('keydown', this.onKey);
  },
  beforeUnmount() {
    if (this.ro) this.ro.disconnect();
    window.removeEventListener('keydown', this.onKey);
  },
  methods: {
    measure() {
      const el = this.$refs.area;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      this.areaSize = { w: rect.width, h: rect.height };
      this.editorStore.setCanvasContainer(rect.width, rect.height);
    },
    onAreaClick(e) {
      // clicks on background clear selection
      if (e.target === this.$refs.area || e.target.classList.contains('slide-canvas-wrapper')) {
        this.docStore.clearSelection();
        this.editorStore.stopEditing();
      }
    },
    onBackgroundMouseDown() {
      this.docStore.clearSelection();
      this.editorStore.stopEditing();
    },
    onElementSelect(id, e) {
      const slide = this.slide;
      const el = slide.elements.find((x) => x.id === id);
      if (el?.contentBehavior?.readonly && this.docStore.mode === 'presentation') {
        // readonly placeholder elements shouldn't be selected/edited from presentation mode
        return;
      }
      if (e?.shiftKey) {
        this.docStore.addToSelection(id);
      } else {
        this.docStore.setSelection(id);
      }
      if (this.editingId && this.editingId !== id) this.editorStore.stopEditing();
    },
    onStartEdit(id) {
      this.editorStore.startEditing(id);
      this.docStore.setSelection(id);
    },
    onCommitText(id, payload) {
      this.docStore.run(
        {
          type: 'element.updateText',
          slideId: this.slide.id,
          elementId: id,
          payload: { text: payload.text },
        },
        { coalesce: payload.coalesce && !payload.finalize },
      );
      if (payload.finalize) this.editorStore.stopEditing();
    },
    onDragStart({ id, event }) {
      const el = this.slide.elements.find((x) => x.id === id);
      if (!el || el.locked || el.contentBehavior?.readonly) return;
      if (this.editingId === id) return;
      this.onElementSelect(id, event);
      const start = {
        clientX: event.clientX,
        clientY: event.clientY,
        x: el.frame.xEmu,
        y: el.frame.yEmu,
      };
      this.drag = { id, start, moved: false };
      window.addEventListener('mousemove', this.onDragMove);
      window.addEventListener('mouseup', this.onDragEnd, { once: true });
      event.preventDefault();
    },
    onDragMove(e) {
      if (!this.drag) return;
      const dx = (e.clientX - this.drag.start.clientX) / this.scale;
      const dy = (e.clientY - this.drag.start.clientY) / this.scale;
      let xEmu = Math.round(this.drag.start.x + dx);
      let yEmu = Math.round(this.drag.start.y + dy);
      if (this.editorStore.snap) {
        const step = this.editorStore.snapStepEmu;
        xEmu = Math.round(xEmu / step) * step;
        yEmu = Math.round(yEmu / step) * step;
      }
      this.docStore.run(
        {
          type: 'element.move',
          slideId: this.slide.id,
          elementId: this.drag.id,
          payload: { xEmu, yEmu },
        },
        { coalesce: this.drag.moved },
      );
      this.drag.moved = true;
    },
    onDragEnd() {
      this.drag = null;
      window.removeEventListener('mousemove', this.onDragMove);
    },
    onResizeStart({ id, handle, event }) {
      const el = this.slide.elements.find((x) => x.id === id);
      if (!el || el.locked || el.contentBehavior?.readonly) return;
      this.docStore.setSelection(id);
      const start = {
        clientX: event.clientX,
        clientY: event.clientY,
        frame: { ...el.frame },
        handle,
      };
      this.resize = { id, start, moved: false };
      window.addEventListener('mousemove', this.onResizeMove);
      window.addEventListener('mouseup', this.onResizeEnd, { once: true });
      event.preventDefault();
    },
    onResizeMove(e) {
      if (!this.resize) return;
      const dx = (e.clientX - this.resize.start.clientX) / this.scale;
      const dy = (e.clientY - this.resize.start.clientY) / this.scale;
      const f = { ...this.resize.start.frame };
      const h = this.resize.start.handle;
      const minW = 100000;
      const minH = 50000;
      if (h.includes('l')) { f.xEmu = this.resize.start.frame.xEmu + dx; f.wEmu = this.resize.start.frame.wEmu - dx; }
      if (h.includes('r')) { f.wEmu = this.resize.start.frame.wEmu + dx; }
      if (h.includes('t')) { f.yEmu = this.resize.start.frame.yEmu + dy; f.hEmu = this.resize.start.frame.hEmu - dy; }
      if (h.includes('b')) { f.hEmu = this.resize.start.frame.hEmu + dy; }
      // 'm' middles: lock the cross axis (already excluded above by absence)
      if (h === 'tm' || h === 'bm') { f.xEmu = this.resize.start.frame.xEmu; f.wEmu = this.resize.start.frame.wEmu; }
      if (h === 'lm' || h === 'rm') { f.yEmu = this.resize.start.frame.yEmu; f.hEmu = this.resize.start.frame.hEmu; }

      f.wEmu = Math.max(minW, Math.round(f.wEmu));
      f.hEmu = Math.max(minH, Math.round(f.hEmu));
      f.xEmu = Math.round(f.xEmu);
      f.yEmu = Math.round(f.yEmu);
      if (this.editorStore.snap) {
        const step = this.editorStore.snapStepEmu;
        f.xEmu = Math.round(f.xEmu / step) * step;
        f.yEmu = Math.round(f.yEmu / step) * step;
        f.wEmu = Math.max(minW, Math.round(f.wEmu / step) * step);
        f.hEmu = Math.max(minH, Math.round(f.hEmu / step) * step);
      }
      this.docStore.run(
        {
          type: 'element.resize',
          slideId: this.slide.id,
          elementId: this.resize.id,
          payload: { frame: f },
        },
        { coalesce: this.resize.moved },
      );
      this.resize.moved = true;
    },
    onResizeEnd() {
      this.resize = null;
      window.removeEventListener('mousemove', this.onResizeMove);
    },
    onKey(e) {
      const isEditing = !!this.editingId;
      if (isEditing) return;
      const slide = this.slide;
      if (!slide) return;
      const sel = this.docStore.selection;
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z' && !e.shiftKey) {
        e.preventDefault();
        this.docStore.undo();
        return;
      }
      if ((e.metaKey || e.ctrlKey) && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey))) {
        e.preventDefault();
        this.docStore.redo();
        return;
      }
      if (!sel.length) return;
      if (e.key === 'Delete' || e.key === 'Backspace') {
        e.preventDefault();
        sel.forEach((id) => this.docStore.run({ type: 'element.delete', slideId: slide.id, elementId: id }));
        this.docStore.clearSelection();
        return;
      }
      const arrowMap = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
      const dir = arrowMap[e.key];
      if (dir) {
        e.preventDefault();
        const step = e.shiftKey ? 91440 : 18288;
        sel.forEach((id) => {
          const el = slide.elements.find((x) => x.id === id);
          if (!el) return;
          this.docStore.run({
            type: 'element.move',
            slideId: slide.id,
            elementId: id,
            payload: {
              xEmu: el.frame.xEmu + dir[0] * step,
              yEmu: el.frame.yEmu + dir[1] * step,
            },
          });
        });
      }
    },
  },
};
</script>
