<template>
  <div>
    <div class="inspector-section">
      <h4>Слайд</h4>
      <div class="inspector-row">
        <label>Имя</label>
        <input type="text" :value="slide.name || ''" @input="(e) => updateSlide({ name: e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Тип</label>
        <select :value="slide.slideType" @change="(e) => updateSlide({ slideType: e.target.value })">
          <option value="title">title</option>
          <option value="text">text</option>
          <option value="image">image</option>
          <option value="bullets">bullets</option>
          <option value="conclusion">conclusion</option>
        </select>
      </div>
    </div>
    <div class="inspector-section">
      <h4>Фон</h4>
      <div class="inspector-row">
        <label>Тип</label>
        <select :value="slide.background?.type || 'color'" @change="(e) => changeBgType(e.target.value)">
          <option value="color">color</option>
          <option value="image">image</option>
          <option value="gradient">gradient</option>
        </select>
      </div>
      <template v-if="slide.background?.type === 'color'">
        <div class="inspector-row">
          <label>Цвет</label>
          <input type="color" :value="slide.background.value" @input="(e) => updateSlide({ background: { type: 'color', value: e.target.value.toUpperCase() } })" />
          <input type="text" :value="slide.background.value" @input="(e) => updateSlide({ background: { type: 'color', value: e.target.value } })" style="max-width:100px;" />
        </div>
      </template>
      <template v-else-if="slide.background?.type === 'image'">
        <div class="inspector-row">
          <label>Asset</label>
          <select :value="slide.background.assetId || ''" @change="(e) => updateSlide({ background: { type: 'image', assetId: e.target.value, fit: slide.background.fit || 'cover' } })">
            <option value="">— не выбрано —</option>
            <option v-for="a in imageAssets" :key="a.id" :value="a.id">{{ a.fileName || a.id }}</option>
          </select>
        </div>
        <div class="inspector-row">
          <label>Fit</label>
          <select :value="slide.background.fit || 'cover'" @change="(e) => updateSlide({ background: { ...slide.background, fit: e.target.value } })">
            <option value="cover">cover</option>
            <option value="contain">contain</option>
            <option value="stretch">stretch</option>
          </select>
        </div>
      </template>
      <template v-else>
        <div class="inspector-row">
          <label>From</label>
          <input type="color" :value="slide.background.from || '#ffffff'" @input="(e) => updateSlide({ background: { ...slide.background, from: e.target.value.toUpperCase() } })" />
        </div>
        <div class="inspector-row">
          <label>To</label>
          <input type="color" :value="slide.background.to || '#000000'" @input="(e) => updateSlide({ background: { ...slide.background, to: e.target.value.toUpperCase() } })" />
        </div>
        <div class="inspector-row">
          <label>Угол</label>
          <input type="number" :value="slide.background.angle || 0" @input="(e) => updateSlide({ background: { ...slide.background, angle: +e.target.value } })" />
        </div>
      </template>
    </div>
    <div class="inspector-section">
      <h4>Заметки</h4>
      <div class="inspector-row">
        <textarea :value="slide.notes || ''" @input="(e) => updateSlide({ notes: e.target.value })" rows="4" style="width:100%;" />
      </div>
    </div>
  </div>
</template>

<script>
import { useDocumentStore } from '../../stores/document.js';

export default {
  name: 'SlideInspector',
  props: {
    slide: { type: Object, required: true },
  },
  computed: {
    docStore() { return useDocumentStore(); },
    imageAssets() {
      return (this.docStore.doc?.assets || []).filter((a) => a.type === 'image');
    },
  },
  methods: {
    updateSlide(props) {
      this.docStore.run({
        type: 'slide.update',
        slideId: this.slide.id,
        payload: { props },
      });
    },
    changeBgType(type) {
      let bg;
      if (type === 'color') bg = { type: 'color', value: '#FFFFFF' };
      else if (type === 'image') bg = { type: 'image', assetId: '', fit: 'cover' };
      else bg = { type: 'gradient', from: '#FFFFFF', to: '#111827', angle: 90 };
      this.updateSlide({ background: bg });
    },
  },
};
</script>
