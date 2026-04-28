<template>
  <div class="select-chip-wrap" v-click-outside="close">
    <button class="select-chip-btn" @click="open = !open">
      <AcIcon v-if="icon" :name="icon" :size="13" />
      <span>{{ value || placeholder }}</span>
      <AcIcon name="chevronDown" :size="11" />
    </button>
    <div v-if="open" class="select-chip-menu">
      <div
        v-for="opt in options"
        :key="opt"
        class="select-chip-item"
        :class="{ active: opt === value }"
        @click="select(opt)"
      >
        {{ opt }}
      </div>
    </div>
  </div>
</template>

<script>
import AcIcon from './AcIcon.vue';

const directive = {
  beforeMount(el, binding) {
    el._clickOutside = (e) => {
      if (!el.contains(e.target)) binding.value(e);
    };
    document.addEventListener('mousedown', el._clickOutside);
  },
  unmounted(el) {
    document.removeEventListener('mousedown', el._clickOutside);
  },
};

export default {
  name: 'SelectChip',
  components: { AcIcon },
  directives: { 'click-outside': directive },
  props: {
    icon: { type: String, default: '' },
    value: { type: String, default: '' },
    options: { type: Array, default: () => [] },
    placeholder: { type: String, default: '' },
  },
  emits: ['update'],
  data() { return { open: false }; },
  methods: {
    select(opt) {
      this.$emit('update', opt);
      this.open = false;
    },
    close() { this.open = false; },
  },
};
</script>

<style scoped>
.select-chip-wrap { position: relative; }
.select-chip-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 10px;
  background: var(--ink-3);
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--fg-2);
  font-size: 12.5px;
  cursor: pointer;
}
.select-chip-btn:hover { background: var(--ink-4); color: var(--fg-1); }
.select-chip-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 50;
  min-width: 180px;
  background: var(--ink-2);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 4px;
  box-shadow: var(--shadow-lg);
}
.select-chip-item {
  padding: 7px 10px;
  font-size: 13px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--fg-2);
}
.select-chip-item:hover { background: var(--ink-3); color: var(--fg-1); }
.select-chip-item.active { color: var(--accent); background: rgba(255,181,71,0.10); }
</style>
