<template>
  <svg
    :width="widthPx"
    :height="heightPx"
    @mousedown="$emit('select', $event)"
    style="display:block; overflow:visible;"
  >
    <rect
      v-if="element.shape === 'rect' || element.shape === 'roundRect'"
      x="0" y="0"
      :width="widthPx" :height="heightPx"
      :rx="rx" :ry="rx"
      :fill="element.style.fill || 'transparent'"
      :stroke="element.style.stroke || 'transparent'"
      :stroke-width="strokePx"
    />
    <ellipse
      v-else-if="element.shape === 'ellipse'"
      :cx="widthPx / 2" :cy="heightPx / 2"
      :rx="widthPx / 2" :ry="heightPx / 2"
      :fill="element.style.fill || 'transparent'"
      :stroke="element.style.stroke || 'transparent'"
      :stroke-width="strokePx"
    />
    <polygon
      v-else-if="element.shape === 'triangle'"
      :points="`${widthPx / 2},0 ${widthPx},${heightPx} 0,${heightPx}`"
      :fill="element.style.fill || 'transparent'"
      :stroke="element.style.stroke || 'transparent'"
      :stroke-width="strokePx"
    />
  </svg>
</template>

<script>
export default {
  name: 'ShapeElementView',
  props: {
    element: { type: Object, required: true },
    scale: { type: Number, required: true },
  },
  emits: ['select'],
  computed: {
    widthPx() { return this.element.frame.wEmu * this.scale; },
    heightPx() { return this.element.frame.hEmu * this.scale; },
    strokePx() {
      return (this.element.style.strokeWidth || 0) * this.scale;
    },
    rx() {
      if (this.element.shape !== 'roundRect') return 0;
      return (this.element.style.radiusEmu || 100000) * this.scale;
    },
  },
};
</script>
