import { defineStore } from 'pinia';

export const useEditorStore = defineStore('editor', {
  state: () => ({
    zoom: 1,           // 1 = fit, multiplier of fit-scale
    autoFit: true,
    showGrid: false,
    snap: true,
    snapStepEmu: 91440, // 0.1 inch
    canvasContainer: { width: 0, height: 0 },
    editingElementId: null,
  }),
  actions: {
    setZoom(z) {
      this.zoom = Math.max(0.25, Math.min(4, z));
      this.autoFit = false;
    },
    enableAutoFit() {
      this.autoFit = true;
      this.zoom = 1;
    },
    setCanvasContainer(width, height) {
      this.canvasContainer = { width, height };
    },
    startEditing(id) {
      this.editingElementId = id;
    },
    stopEditing() {
      this.editingElementId = null;
    },
    toggleGrid() {
      this.showGrid = !this.showGrid;
    },
    toggleSnap() {
      this.snap = !this.snap;
    },
  },
});
