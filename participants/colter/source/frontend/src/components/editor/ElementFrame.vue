<template>
  <div
    class="element"
    :class="{ selected, locked: element.locked }"
    :data-readonly="String(!!element.contentBehavior?.readonly)"
    :style="frameStyle"
    @mousedown="onFrameMouseDown"
  >
    <ElementRenderer
      :element="element"
      :scale="scale"
      :assets="assets"
      :readonly="!!element.contentBehavior?.readonly"
      :editing="editing"
      @select="onSelect"
      @start-edit="$emit('start-edit')"
      @commit-text="(p) => $emit('commit-text', p)"
    />
    <div v-if="overflow" class="notice-bar">{{ overflow.message }}</div>
    <template v-if="selected && !element.locked && !editing">
      <div class="handle tl" data-handle="tl" @mousedown.stop="onHandleDown('tl', $event)" />
      <div class="handle tm" data-handle="tm" @mousedown.stop="onHandleDown('tm', $event)" />
      <div class="handle tr" data-handle="tr" @mousedown.stop="onHandleDown('tr', $event)" />
      <div class="handle lm" data-handle="lm" @mousedown.stop="onHandleDown('lm', $event)" />
      <div class="handle rm" data-handle="rm" @mousedown.stop="onHandleDown('rm', $event)" />
      <div class="handle bl" data-handle="bl" @mousedown.stop="onHandleDown('bl', $event)" />
      <div class="handle bm" data-handle="bm" @mousedown.stop="onHandleDown('bm', $event)" />
      <div class="handle br" data-handle="br" @mousedown.stop="onHandleDown('br', $event)" />
    </template>
  </div>
</template>

<script>
import ElementRenderer from './ElementRenderer.vue';
import { textOverflowIssues } from '../../core/validation.js';

export default {
  name: 'ElementFrame',
  components: { ElementRenderer },
  props: {
    element: { type: Object, required: true },
    scale: { type: Number, required: true },
    selected: { type: Boolean, default: false },
    editing: { type: Boolean, default: false },
    assets: { type: Array, default: () => [] },
  },
  emits: ['drag-start', 'resize-start', 'select', 'start-edit', 'commit-text'],
  computed: {
    frameStyle() {
      const f = this.element.frame;
      return {
        left: `${f.xEmu * this.scale}px`,
        top: `${f.yEmu * this.scale}px`,
        width: `${f.wEmu * this.scale}px`,
        height: `${f.hEmu * this.scale}px`,
        opacity: this.element.opacity != null ? this.element.opacity : 1,
        transform: f.rotate ? `rotate(${f.rotate}deg)` : null,
        zIndex: this.element.zIndex || 0,
        visibility: this.element.visible === false ? 'hidden' : 'visible',
      };
    },
    overflow() {
      return this.selected ? textOverflowIssues(this.element) : null;
    },
  },
  methods: {
    onFrameMouseDown(e) {
      // Ignore handle clicks (handled separately)
      if (e.target.dataset.handle) return;
      this.$emit('drag-start', { id: this.element.id, event: e });
    },
    onHandleDown(handle, e) {
      this.$emit('resize-start', { id: this.element.id, handle, event: e });
    },
    onSelect(e) {
      this.$emit('select', e);
    },
  },
};
</script>
