<template>
  <div class="element-image" :style="bgStyle" @mousedown="$emit('select', $event)">
    <span v-if="!resolvedUrl">Изображение не выбрано</span>
  </div>
</template>

<script>
export default {
  name: 'ImageElementView',
  props: {
    element: { type: Object, required: true },
    assets: { type: Array, default: () => [] },
  },
  emits: ['select'],
  computed: {
    resolvedUrl() {
      if (!this.element.assetId) return null;
      const asset = this.assets.find((a) => a.id === this.element.assetId);
      return asset?.url || null;
    },
    bgStyle() {
      const fit = this.element.fit || 'cover';
      const sizeMap = { cover: 'cover', contain: 'contain', stretch: '100% 100%' };
      return this.resolvedUrl
        ? {
            width: '100%',
            height: '100%',
            backgroundImage: `url("${this.resolvedUrl}")`,
            backgroundSize: sizeMap[fit] || 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
          }
        : { width: '100%', height: '100%' };
    },
  },
};
</script>
