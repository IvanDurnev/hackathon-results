import { defineStore } from 'pinia';
import { applyCommand, clone } from '../core/commands.js';

const HISTORY_LIMIT = 100;

export const useDocumentStore = defineStore('document', {
  state: () => ({
    doc: null, // PresentationDocument | TemplateDocument
    mode: 'presentation', // 'presentation' | 'template'
    activeSlideId: null,
    activeLayoutId: null,
    selection: [], // element ids
    pastStack: [],
    futureStack: [],
    saving: false,
    dirty: false,
    revision: 0,
    lastSavedAt: null,
  }),
  getters: {
    activeSlide(state) {
      if (!state.doc) return null;
      if (state.mode === 'presentation') {
        return state.doc.slides.find((s) => s.id === state.activeSlideId) || state.doc.slides[0] || null;
      }
      const layout = state.doc.layouts.find((l) => l.id === state.activeLayoutId) || state.doc.layouts[0];
      return layout || null;
    },
    activeSlideIndex(state) {
      if (!state.doc || state.mode !== 'presentation') return -1;
      return state.doc.slides.findIndex((s) => s.id === state.activeSlideId);
    },
    selectedElements(state) {
      const slide = this.activeSlide;
      if (!slide) return [];
      const ids = new Set(state.selection);
      return slide.elements.filter((e) => ids.has(e.id));
    },
    canUndo: (s) => s.pastStack.length > 0,
    canRedo: (s) => s.futureStack.length > 0,
  },
  actions: {
    loadPresentation(doc) {
      this.doc = doc;
      this.mode = 'presentation';
      this.activeSlideId = doc.slides[0]?.id || null;
      this.selection = [];
      this.pastStack = [];
      this.futureStack = [];
      this.dirty = false;
      this.revision = 0;
    },
    loadTemplate(doc) {
      this.doc = doc;
      this.mode = 'template';
      this.activeLayoutId = doc.layouts[0]?.id || null;
      this.selection = [];
      this.pastStack = [];
      this.futureStack = [];
      this.dirty = false;
      this.revision = 0;
    },
    selectActiveSlide(slideId) {
      this.activeSlideId = slideId;
      this.selection = [];
    },
    selectActiveLayout(layoutId) {
      this.activeLayoutId = layoutId;
      this.selection = [];
    },
    setSelection(ids) {
      this.selection = Array.isArray(ids) ? ids : [ids].filter(Boolean);
    },
    addToSelection(id) {
      if (!this.selection.includes(id)) this.selection.push(id);
    },
    clearSelection() {
      this.selection = [];
    },
    /**
     * Snapshots current doc, runs the command, marks dirty.
     * For continuous gestures (drag, resize, typing) pass `coalesce: true`
     * after the first call so we keep just the original snapshot.
     */
    run(cmd, { coalesce = false } = {}) {
      if (!this.doc) return;
      if (!coalesce) {
        this.pastStack.push(JSON.stringify(this._snapshot()));
        if (this.pastStack.length > HISTORY_LIMIT) this.pastStack.shift();
        this.futureStack = [];
      }
      // For template mode, route element/slide commands to the active layout
      const target = this._documentTargetForCommand(cmd);
      applyCommand(target, cmd);
      this.markDirty();
    },
    markDirty() {
      this.dirty = true;
      this.revision += 1;
    },
    /** Internal: returns the object that command applier should mutate. */
    _documentTargetForCommand(cmd) {
      if (this.mode === 'presentation') return this.doc;
      // In template mode, element/slide commands operate on the active layout,
      // wrapped in a presentation-like shape that command applier can mutate.
      const layout = this.doc.layouts.find((l) => l.id === this.activeLayoutId);
      if (!layout) return this.doc;
      if (cmd.type === 'doc.update' || cmd.type === 'doc.replaceAssets') {
        return this.doc;
      }
      // Adapter object so applyCommand finds slides[0]
      return new Proxy(this.doc, {
        get(target, prop) {
          if (prop === 'slides') return [layout];
          if (prop === 'assets') return target.assets;
          return target[prop];
        },
        set(target, prop, value) {
          target[prop] = value;
          return true;
        },
      });
    },
    _snapshot() {
      return {
        doc: this.doc,
        mode: this.mode,
        activeSlideId: this.activeSlideId,
        activeLayoutId: this.activeLayoutId,
        selection: this.selection.slice(),
      };
    },
    undo() {
      if (!this.pastStack.length) return;
      const past = this.pastStack.pop();
      this.futureStack.push(JSON.stringify(this._snapshot()));
      const snap = JSON.parse(past);
      this._restore(snap);
      this.markDirty();
    },
    redo() {
      if (!this.futureStack.length) return;
      const future = this.futureStack.pop();
      this.pastStack.push(JSON.stringify(this._snapshot()));
      const snap = JSON.parse(future);
      this._restore(snap);
      this.markDirty();
    },
    _restore(snap) {
      this.doc = snap.doc;
      this.mode = snap.mode;
      this.activeSlideId = snap.activeSlideId;
      this.activeLayoutId = snap.activeLayoutId;
      this.selection = snap.selection;
    },
    markSaved(revision = this.revision) {
      if (revision !== this.revision) return;
      this.dirty = false;
      this.lastSavedAt = new Date();
    },
    addAsset(asset) {
      if (!this.doc) return;
      if (!this.doc.assets) this.doc.assets = [];
      if (!this.doc.assets.find((a) => a.id === asset.id)) {
        this.doc.assets.push(asset);
        this.markDirty();
      }
    },
  },
});
