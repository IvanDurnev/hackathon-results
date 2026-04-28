<template>
  <svg
    :width="widthPx"
    :height="Math.max(heightPx, 4)"
    @mousedown="$emit('select', $event)"
    style="display:block; overflow:visible;"
  >
    <line
      x1="0" :y1="heightPx / 2"
      :x2="widthPx" :y2="heightPx / 2"
      :stroke="element.style.color || '#111827'"
      :stroke-width="strokePx"
      :stroke-dasharray="dasharray"
    />
  </svg>
</template>

<script>
export default {
  name: 'LineElementView',
  props: {
    element: { type: Object, required: true },
    scale: { type: Number, required: true },
  },
  emits: ['select'],
  computed: {
    widthPx() { return this.element.frame.wEmu * this.scale; },
    heightPx() { return this.element.frame.hEmu * this.scale; },
    strokePx() { return Math.max(1, (this.element.style.widthEmu || 19050) * this.scale); },
    dasharray() {
      const dash = this.element.style.dash;
      if (dash === 'dash') return '8 6';
      if (dash === 'dot') return '2 4';
      return null;
    },
  },
};
</script>
