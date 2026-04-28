<template>
  <component
    :is="comp"
    :element="element"
    :scale="scale"
    :assets="assets"
    :readonly="readonly"
    :editing="editing"
    @select="$emit('select', $event)"
    @start-edit="$emit('start-edit')"
    @commit-text="(p) => $emit('commit-text', p)"
  />
</template>

<script>
import TextElement from './elements/TextElement.vue';
import ImageElement from './elements/ImageElement.vue';
import ShapeElement from './elements/ShapeElement.vue';
import LineElement from './elements/LineElement.vue';

const map = {
  text: TextElement,
  image: ImageElement,
  shape: ShapeElement,
  line: LineElement,
  icon: ImageElement, // v1: icon uses image renderer
};

export default {
  name: 'ElementRenderer',
  components: { TextElement, ImageElement, ShapeElement, LineElement },
  props: {
    element: { type: Object, required: true },
    scale: { type: Number, required: true },
    assets: { type: Array, default: () => [] },
    readonly: { type: Boolean, default: false },
    editing: { type: Boolean, default: false },
  },
  emits: ['select', 'start-edit', 'commit-text'],
  computed: {
    comp() {
      return map[this.element.type] || null;
    },
  },
};
</script>
