<template>
  <div class="canvas-area" ref="area" @click="onAreaClick">
    <div class="slide-canvas-wrapper" :style="wrapperStyle">
      <div
        class="slide-canvas"
        ref="canvas"
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
        <div
          v-for="(guide, idx) in snapGuides"
          :key="`guide-${idx}`"
          class="alignment-guide"
          :class="guide.orientation"
          :style="guideStyle(guide)"
        />
        <div
          v-if="marquee"
          class="marquee"
          :class="{ intersect: marquee.intersect }"
          :style="marqueeStyle"
        />
        <div v-if="slideNumberLabel" class="slide-number-badge">{{ slideNumberLabel }}</div>
      </div>
    </div>
    <div class="canvas-meta">
      <span>{{ slideSize.ratio }}</span>
      <span>{{ slideSizeLabel }}</span>
    </div>
  </div>
</template>

<script>
import ElementFrame from './ElementFrame.vue';
import { useDocumentStore } from '../../stores/document.js';
import { useEditorStore } from '../../stores/editor.js';
import { emuToCm, fitScale, roundNumber } from '../../core/emu.js';

const ALIGN_SNAP_PX = 8;

function rectsIntersect(a, b) {
  return !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y);
}
function rectContains(outer, inner) {
  return inner.x >= outer.x
    && inner.y >= outer.y
    && inner.x + inner.w <= outer.x + outer.w
    && inner.y + inner.h <= outer.y + outer.h;
}

function rectFromFrame(frame) {
  return {
    x: frame.xEmu,
    y: frame.yEmu,
    w: frame.wEmu,
    h: frame.hEmu,
  };
}

function guide(orientation, positionEmu, startEmu, endEmu) {
  return {
    orientation,
    positionEmu,
    startEmu: Math.min(startEmu, endEmu),
    endEmu: Math.max(startEmu, endEmu),
  };
}

function buildAlignmentCandidates(elements, movingId, slideSize) {
  const vertical = [
    { value: 0, start: 0, end: slideSize.heightEmu },
    { value: slideSize.widthEmu / 2, start: 0, end: slideSize.heightEmu },
    { value: slideSize.widthEmu, start: 0, end: slideSize.heightEmu },
  ];
  const horizontal = [
    { value: 0, start: 0, end: slideSize.widthEmu },
    { value: slideSize.heightEmu / 2, start: 0, end: slideSize.widthEmu },
    { value: slideSize.heightEmu, start: 0, end: slideSize.widthEmu },
  ];

  elements.forEach((el) => {
    if (el.id === movingId) return;
    const r = rectFromFrame(el.frame);
    vertical.push(
      { value: r.x, start: r.y, end: r.y + r.h },
      { value: r.x + r.w / 2, start: r.y, end: r.y + r.h },
      { value: r.x + r.w, start: r.y, end: r.y + r.h },
    );
    horizontal.push(
      { value: r.y, start: r.x, end: r.x + r.w },
      { value: r.y + r.h / 2, start: r.x, end: r.x + r.w },
      { value: r.y + r.h, start: r.x, end: r.x + r.w },
    );
  });

  return { vertical, horizontal };
}

function findBestAlignmentMatch(anchors, candidates, thresholdEmu) {
  let best = null;
  anchors.forEach((anchor) => {
    candidates.forEach((candidate) => {
      const delta = candidate.value - anchor.value;
      const abs = Math.abs(delta);
      if (abs > thresholdEmu) return;
      if (!best || abs < best.abs) {
        best = { anchor, candidate, delta, abs };
      }
    });
  });
  return best;
}

function applyMoveAlignmentSnap(rect, candidates, thresholdEmu) {
  const next = { ...rect };
  const guides = [];

  const xMatch = findBestAlignmentMatch([
    { value: rect.x },
    { value: rect.x + rect.w / 2 },
    { value: rect.x + rect.w },
  ], candidates.vertical, thresholdEmu);
  if (xMatch) {
    next.x += xMatch.delta;
    guides.push(guide(
      'vertical',
      xMatch.candidate.value,
      Math.min(next.y, xMatch.candidate.start),
      Math.max(next.y + next.h, xMatch.candidate.end),
    ));
  }

  const yMatch = findBestAlignmentMatch([
    { value: rect.y },
    { value: rect.y + rect.h / 2 },
    { value: rect.y + rect.h },
  ], candidates.horizontal, thresholdEmu);
  if (yMatch) {
    next.y += yMatch.delta;
    guides.push(guide(
      'horizontal',
      yMatch.candidate.value,
      Math.min(next.x, yMatch.candidate.start),
      Math.max(next.x + next.w, yMatch.candidate.end),
    ));
  }

  return {
    rect: next,
    guides,
    snappedX: !!xMatch,
    snappedY: !!yMatch,
  };
}

function normalizeResizedRect(rect, handle, minW, minH) {
  const next = { ...rect };
  if (next.w < minW) {
    if (handle.includes('l')) next.x -= (minW - next.w);
    next.w = minW;
  }
  if (next.h < minH) {
    if (handle.includes('t')) next.y -= (minH - next.h);
    next.h = minH;
  }
  return next;
}

function applyResizeAlignmentSnap(rect, handle, candidates, thresholdEmu, minW, minH) {
  const next = { ...rect };
  const guides = [];
  let snappedX = false;
  let snappedY = false;

  if (handle.includes('l')) {
    const match = findBestAlignmentMatch([{ value: next.x }], candidates.vertical, thresholdEmu);
    if (match) {
      next.x += match.delta;
      next.w -= match.delta;
      snappedX = true;
      guides.push(guide(
        'vertical',
        match.candidate.value,
        Math.min(next.y, match.candidate.start),
        Math.max(next.y + next.h, match.candidate.end),
      ));
    }
  } else if (handle.includes('r')) {
    const match = findBestAlignmentMatch([{ value: next.x + next.w }], candidates.vertical, thresholdEmu);
    if (match) {
      next.w += match.delta;
      snappedX = true;
      guides.push(guide(
        'vertical',
        match.candidate.value,
        Math.min(next.y, match.candidate.start),
        Math.max(next.y + next.h, match.candidate.end),
      ));
    }
  }

  if (handle.includes('t')) {
    const match = findBestAlignmentMatch([{ value: next.y }], candidates.horizontal, thresholdEmu);
    if (match) {
      next.y += match.delta;
      next.h -= match.delta;
      snappedY = true;
      guides.push(guide(
        'horizontal',
        match.candidate.value,
        Math.min(next.x, match.candidate.start),
        Math.max(next.x + next.w, match.candidate.end),
      ));
    }
  } else if (handle.includes('b')) {
    const match = findBestAlignmentMatch([{ value: next.y + next.h }], candidates.horizontal, thresholdEmu);
    if (match) {
      next.h += match.delta;
      snappedY = true;
      guides.push(guide(
        'horizontal',
        match.candidate.value,
        Math.min(next.x, match.candidate.start),
        Math.max(next.x + next.w, match.candidate.end),
      ));
    }
  }

  return {
    rect: normalizeResizedRect(next, handle, minW, minH),
    guides,
    snappedX,
    snappedY,
  };
}

export default {
  name: 'SlideCanvas',
  components: { ElementFrame },
  data() {
    return {
      areaSize: { w: 0, h: 0 },
      ro: null,
      drag: null,
      resize: null,
      marquee: null, // { startX, startY, x, y, w, h, intersect }
      snapGuides: [],
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    editorStore() { return useEditorStore(); },
    doc() { return this.docStore.doc; },
    slide() { return this.docStore.activeSlide; },
    selection() { return this.docStore.selection; },
    editingId() { return this.editorStore.editingElementId; },
    slideSize() { return this.doc?.slideSize || { widthEmu: 12192000, heightEmu: 6858000, ratio: '16:9' }; },
    fitScaleVal() {
      return fitScale(
        this.areaSize.w,
        this.areaSize.h,
        this.slideSize.widthEmu,
        this.slideSize.heightEmu,
        32,
      ) || 0.0000001;
    },
    scale() {
      const z = this.editorStore.zoom;
      return this.editorStore.autoFit ? this.fitScaleVal : this.fitScaleVal * z;
    },
    canvasStyle() {
      const bg = this.slide?.background;
      const style = {
        width: `${this.slideSize.widthEmu * this.scale}px`,
        height: `${this.slideSize.heightEmu * this.scale}px`,
      };
      if (!bg || bg.type === 'color') {
        style.background = bg?.value || '#FFFFFF';
      } else if (bg.type === 'gradient') {
        style.background = `linear-gradient(${bg.angle || 0}deg, ${bg.from}, ${bg.to})`;
      } else if (bg.type === 'image') {
        const a = (this.doc.assets || []).find((x) => x.id === bg.assetId);
        if (a?.url) {
          const fit = bg.fit || 'cover';
          const sizeMap = { cover: 'cover', contain: 'contain', stretch: '100% 100%' };
          style.backgroundImage = `url("${a.url}")`;
          style.backgroundSize = sizeMap[fit] || 'cover';
          style.backgroundPosition = 'center';
          style.backgroundRepeat = 'no-repeat';
          style.backgroundColor = '#fff';
        } else {
          style.background = '#fff';
        }
      }
      return style;
    },
    wrapperStyle() { return { borderRadius: '6px' }; },
    sortedElements() {
      if (!this.slide) return [];
      return [...this.slide.elements].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
    },
    marqueeStyle() {
      if (!this.marquee) return {};
      return {
        left: `${this.marquee.x}px`,
        top: `${this.marquee.y}px`,
        width: `${this.marquee.w}px`,
        height: `${this.marquee.h}px`,
      };
    },
    slideSizeLabel() {
      const widthCm = roundNumber(emuToCm(this.slideSize.widthEmu), 2).toLocaleString('ru-RU');
      const heightCm = roundNumber(emuToCm(this.slideSize.heightEmu), 2).toLocaleString('ru-RU');
      return `${widthCm} × ${heightCm} см`;
    },
    slideNumberLabel() {
      if (this.docStore.mode !== 'presentation') return '';
      const cfg = this.doc?.slideNumbering;
      if (!cfg?.enabled) return '';
      const slides = this.doc.slides || [];
      const idx = slides.findIndex((s) => s.id === this.slide?.id);
      if (idx < 0) return '';
      const slide = slides[idx];
      if (cfg.hideOnTitle !== false && slide?.slideType === 'title') return '';
      if (slide?.hideSlideNumber) return '';
      const n = idx + 1;
      const total = slides.length;
      if (cfg.format === 'number') return `${n}`;
      if (cfg.format === 'page') return `Слайд ${n}`;
      return `${n} / ${total}`;
    },
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
      if (e.target === this.$refs.area || e.target.classList.contains('slide-canvas-wrapper')) {
        this.docStore.clearSelection();
        this.editorStore.stopEditing();
        this.snapGuides = [];
      }
    },
    guideStyle(guideData) {
      if (guideData.orientation === 'vertical') {
        return {
          left: `${guideData.positionEmu * this.scale}px`,
          top: `${guideData.startEmu * this.scale}px`,
          height: `${Math.max(1, (guideData.endEmu - guideData.startEmu) * this.scale)}px`,
        };
      }
      return {
        left: `${guideData.startEmu * this.scale}px`,
        top: `${guideData.positionEmu * this.scale}px`,
        width: `${Math.max(1, (guideData.endEmu - guideData.startEmu) * this.scale)}px`,
      };
    },
    alignmentCandidates(movingId) {
      return buildAlignmentCandidates(this.slide?.elements || [], movingId, this.slideSize);
    },
    onBackgroundMouseDown(e) {
      this.docStore.clearSelection();
      this.editorStore.stopEditing();
      this.snapGuides = [];
      if (e.button !== 0) return;
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const startX = e.clientX - rect.left;
      const startY = e.clientY - rect.top;
      this.marquee = {
        startX,
        startY,
        x: startX,
        y: startY,
        w: 0,
        h: 0,
        intersect: false,
        moved: false,
      };
      window.addEventListener('mousemove', this.onMarqueeMove);
      window.addEventListener('mouseup', this.onMarqueeEnd, { once: true });
      e.preventDefault();
    },
    onMarqueeMove(e) {
      if (!this.marquee) return;
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const cx = e.clientX - rect.left;
      const cy = e.clientY - rect.top;
      const dx = cx - this.marquee.startX;
      const dy = cy - this.marquee.startY;
      this.marquee.x = Math.min(this.marquee.startX, cx);
      this.marquee.y = Math.min(this.marquee.startY, cy);
      this.marquee.w = Math.abs(dx);
      this.marquee.h = Math.abs(dy);
      this.marquee.intersect = dx < 0;
      this.marquee.moved = this.marquee.w > 3 || this.marquee.h > 3;
    },
    onMarqueeEnd() {
      window.removeEventListener('mousemove', this.onMarqueeMove);
      const m = this.marquee;
      this.marquee = null;
      this.snapGuides = [];
      if (!m || !m.moved || !this.slide) return;
      const sel = { x: m.x, y: m.y, w: m.w, h: m.h };
      const ids = [];
      this.slide.elements.forEach((el) => {
        const r = {
          x: el.frame.xEmu * this.scale,
          y: el.frame.yEmu * this.scale,
          w: el.frame.wEmu * this.scale,
          h: el.frame.hEmu * this.scale,
        };
        const hit = m.intersect ? rectsIntersect(sel, r) : rectContains(sel, r);
        if (hit) ids.push(el.id);
      });
      this.docStore.setSelection(ids);
    },
    onElementSelect(id, e) {
      const slide = this.slide;
      const el = slide.elements.find((x) => x.id === id);
      if (el?.contentBehavior?.readonly && this.docStore.mode === 'presentation') return;
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
        w: el.frame.wEmu,
        h: el.frame.hEmu,
      };
      this.snapGuides = [];
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
      let guides = [];
      if (this.editorStore.snap) {
        const thresholdEmu = ALIGN_SNAP_PX / this.scale;
        const snapped = applyMoveAlignmentSnap({
          x: xEmu,
          y: yEmu,
          w: this.drag.start.w,
          h: this.drag.start.h,
        }, this.alignmentCandidates(this.drag.id), thresholdEmu);
        xEmu = Math.round(snapped.rect.x);
        yEmu = Math.round(snapped.rect.y);
        guides = snapped.guides;
        const step = this.editorStore.snapStepEmu;
        if (!snapped.snappedX) xEmu = Math.round(xEmu / step) * step;
        if (!snapped.snappedY) yEmu = Math.round(yEmu / step) * step;
      }
      this.snapGuides = guides;
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
      this.snapGuides = [];
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
        preserveAspect: el.type === 'image' && !!el.preserveAspect,
        ratio: el.frame.wEmu / Math.max(1, el.frame.hEmu),
      };
      this.snapGuides = [];
      this.resize = { id, start, moved: false };
      window.addEventListener('mousemove', this.onResizeMove);
      window.addEventListener('mouseup', this.onResizeEnd, { once: true });
      event.stopPropagation();
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
      if (h === 'tm' || h === 'bm') { f.xEmu = this.resize.start.frame.xEmu; f.wEmu = this.resize.start.frame.wEmu; }
      if (h === 'lm' || h === 'rm') { f.yEmu = this.resize.start.frame.yEmu; f.hEmu = this.resize.start.frame.hEmu; }

      f.wEmu = Math.max(minW, Math.round(f.wEmu));
      f.hEmu = Math.max(minH, Math.round(f.hEmu));

      if (this.resize.start.preserveAspect) {
        const ratio = this.resize.start.ratio;
        const cornerHandles = ['tl', 'tr', 'bl', 'br'];
        if (cornerHandles.includes(h)) {
          // Keep ratio by using width as the driver, then re-derive height
          const newW = f.wEmu;
          const newH = Math.max(minH, Math.round(newW / ratio));
          if (h.includes('t')) {
            f.yEmu = this.resize.start.frame.yEmu + (this.resize.start.frame.hEmu - newH);
          }
          f.hEmu = newH;
        }
      }

      f.xEmu = Math.round(f.xEmu);
      f.yEmu = Math.round(f.yEmu);
      let guides = [];
      if (this.editorStore.snap) {
        if (!this.resize.start.preserveAspect) {
          const thresholdEmu = ALIGN_SNAP_PX / this.scale;
          const snapped = applyResizeAlignmentSnap({
            x: f.xEmu,
            y: f.yEmu,
            w: f.wEmu,
            h: f.hEmu,
          }, h, this.alignmentCandidates(this.resize.id), thresholdEmu, minW, minH);
          f.xEmu = Math.round(snapped.rect.x);
          f.yEmu = Math.round(snapped.rect.y);
          f.wEmu = Math.round(snapped.rect.w);
          f.hEmu = Math.round(snapped.rect.h);
          guides = snapped.guides;

          const step = this.editorStore.snapStepEmu;
          if (!snapped.snappedX) {
            f.xEmu = Math.round(f.xEmu / step) * step;
            f.wEmu = Math.max(minW, Math.round(f.wEmu / step) * step);
          }
          if (!snapped.snappedY) {
            f.yEmu = Math.round(f.yEmu / step) * step;
            f.hEmu = Math.max(minH, Math.round(f.hEmu / step) * step);
          }
        } else {
          const step = this.editorStore.snapStepEmu;
          f.xEmu = Math.round(f.xEmu / step) * step;
          f.yEmu = Math.round(f.yEmu / step) * step;
          f.wEmu = Math.max(minW, Math.round(f.wEmu / step) * step);
          f.hEmu = Math.max(minH, Math.round(f.hEmu / step) * step);
        }
      }
      this.snapGuides = guides;
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
      this.snapGuides = [];
      window.removeEventListener('mousemove', this.onResizeMove);
    },
    onKey(e) {
      // Ignore shortcuts when focus is in an editable field — fixes Backspace
      // deleting elements while editing inspector inputs or contenteditable text.
      const t = e.target;
      const tag = t?.tagName;
      const isField =
        tag === 'INPUT' ||
        tag === 'TEXTAREA' ||
        tag === 'SELECT' ||
        t?.isContentEditable;

      const isEditing = !!this.editingId;
      const slide = this.slide;
      if (!slide) return;
      const sel = this.docStore.selection;

      // Undo/redo always available unless typing inside an input where the browser owns Z.
      const key = e.key.toLowerCase();
      const code = e.code;
      const isUndo = code === 'KeyZ' || key === 'z';
      const isRedo = code === 'KeyY' || key === 'y';

      if (!isField && (e.metaKey || e.ctrlKey) && isUndo && !e.shiftKey) {
        e.preventDefault();
        this.docStore.undo();
        return;
      }
      if (!isField && (e.metaKey || e.ctrlKey) && (isRedo || (isUndo && e.shiftKey))) {
        e.preventDefault();
        this.docStore.redo();
        return;
      }
      if (isField || isEditing) return;
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
