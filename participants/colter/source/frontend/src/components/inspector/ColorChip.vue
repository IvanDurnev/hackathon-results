<template>
  <label class="color-chip" :title="value">
    <span class="swatch" :style="{ background: value }"></span>
    <span class="hex">{{ value }}</span>
    <input
      type="color"
      :value="normalized"
      @input="(e) => $emit('change', e.target.value.toUpperCase())"
    />
  </label>
</template>

<script>
export default {
  name: 'ColorChip',
  props: { value: { type: String, default: '#000000' } },
  emits: ['change'],
  computed: {
    normalized() {
      const v = this.value || '#000000';
      // input[type=color] only accepts 6-digit hex.
      return /^#[0-9a-fA-F]{6}$/.test(v) ? v : '#000000';
    },
  },
};
</script>

<style scoped>
.color-chip {
  position: relative;
  display: flex; align-items: center; gap: 6px;
  background: var(--ink-1);
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  padding: 3px 6px;
  cursor: pointer;
  flex: 1;
}
.color-chip:hover { border-color: var(--river-400); }
.color-chip .swatch {
  width: 22px; height: 22px;
  border-radius: 4px;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
  flex-shrink: 0;
}
.color-chip .hex {
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--fg-2);
  text-transform: uppercase;
  flex: 1;
}
.color-chip input[type="color"] {
  position: absolute;
  inset: 0;
  width: 100%; height: 100%;
  opacity: 0;
  border: none;
  padding: 0;
  cursor: pointer;
}
</style>
