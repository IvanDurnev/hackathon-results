<template>
  <div
    class="thumb-canvas"
    :style="rootStyle"
  >
    <div
      v-for="el in visibleElements"
      :key="el.id"
      :style="elStyle(el)"
    >
      <span v-if="el.type === 'text'" :style="textStyle(el)">{{ el.text || el.placeholder || '' }}</span>
      <div v-else-if="el.type === 'image'" :style="imgStyle(el)" />
      <svg v-else-if="el.type === 'shape'" :width="emuW(el) * scale" :height="emuH(el) * scale" style="display:block;">
        <rect
          v-if="el.shape !== 'ellipse' && el.shape !== 'triangle'"
          x="0" y="0"
          :width="emuW(el) * scale" :height="emuH(el) * scale"
          :rx="(el.style.radiusEmu || 0) * scale"
          :fill="el.style.fill || 'transparent'"
          :stroke="el.style.stroke || 'transparent'"
        />
        <ellipse
          v-else-if="el.shape === 'ellipse'"
          :cx="emuW(el)*scale/2" :cy="emuH(el)*scale/2"
          :rx="emuW(el)*scale/2" :ry="emuH(el)*scale/2"
          :fill="el.style.fill || 'transparent'"
          :stroke="el.style.stroke || 'transparent'"
        />
        <polygon
          v-else
          :points="`${emuW(el)*scale/2},0 ${emuW(el)*scale},${emuH(el)*scale} 0,${emuH(el)*scale}`"
          :fill="el.style.fill || 'transparent'"
          :stroke="el.style.stroke || 'transparent'"
        />
      </svg>
      <svg v-else-if="el.type === 'line'" :width="emuW(el)*scale" :height="Math.max(2, emuH(el)*scale)">
        <line x1="0" :y1="emuH(el)*scale/2" :x2="emuW(el)*scale" :y2="emuH(el)*scale/2"
              :stroke="el.style.color || '#111'" :stroke-width="Math.max(1, el.style.widthEmu*scale)" />
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SlideThumbnail',
  props: {
    slide: { type: Object, required: true },
    slideSize: { type: Object, required: true },
    assets: { type: Array, default: () => [] },
    widthPx: { type: Number, default: 180 },
  },
  computed: {
    scale() { return this.widthPx / this.slideSize.widthEmu; },
    heightPx() { return this.slideSize.heightEmu * this.scale; },
    rootStyle() {
      const bg = this.slide.background;
      let background = '#fff';
      if (bg?.type === 'color') background = bg.value;
      else if (bg?.type === 'image') {
        const a = this.assets.find((x) => x.id === bg.assetId);
        if (a?.url) background = `center/cover no-repeat url("${a.url}")`;
      } else if (bg?.type === 'gradient') {
        background = `linear-gradient(${bg.angle || 0}deg, ${bg.from}, ${bg.to})`;
      }
      return {
        position: 'relative',
        width: `${this.widthPx}px`,
        height: `${this.heightPx}px`,
        overflow: 'hidden',
        background,
      };
    },
    visibleElements() {
      return [...(this.slide.elements || [])]
        .filter((e) => e.visible !== false)
        .sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
    },
  },
  methods: {
    emuW(el) { return el.frame.wEmu; },
    emuH(el) { return el.frame.hEmu; },
    elStyle(el) {
      return {
        position: 'absolute',
        left: `${el.frame.xEmu * this.scale}px`,
        top: `${el.frame.yEmu * this.scale}px`,
        width: `${el.frame.wEmu * this.scale}px`,
        height: `${el.frame.hEmu * this.scale}px`,
        overflow: 'hidden',
      };
    },
    textStyle(el) {
      const s = el.style || {};
      const px = (s.fontSize || 16) * 12700 * this.scale;
      return {
        display: 'block',
        fontFamily: s.fontFamily || 'Inter',
        fontSize: `${Math.max(2, px)}px`,
        fontWeight: s.fontWeight || 400,
        color: s.color || '#111',
        opacity: el.text ? 1 : 0.42,
        fontStyle: el.text ? (s.italic ? 'italic' : 'normal') : 'italic',
        textAlign: s.align || 'left',
        lineHeight: s.lineHeight || 1.2,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        width: '100%',
        height: '100%',
      };
    },
    imgStyle(el) {
      const a = this.assets.find((x) => x.id === el.assetId);
      const url = a?.url;
      if (!url) {
        return {
          width: '100%',
          height: '100%',
          background: '#e5e7eb',
        };
      }
      const sizeMap = { cover: 'cover', contain: 'contain', stretch: '100% 100%' };
      return {
        width: '100%',
        height: '100%',
        backgroundImage: `url("${url}")`,
        backgroundSize: sizeMap[el.fit || 'cover'] || 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      };
    },
  },
};
</script>
