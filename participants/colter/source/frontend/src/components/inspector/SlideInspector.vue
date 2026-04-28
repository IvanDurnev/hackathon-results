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
      <div v-if="docStore.mode === 'presentation'" class="inspector-row">
        <label>Номер</label>
        <input type="checkbox" :checked="!slide.hideSlideNumber" @change="(e) => updateSlide({ hideSlideNumber: !e.target.checked })" />
        <span style="font-size: 11.5px; color: var(--fg-3); margin-left: 8px;">показывать на этом слайде</span>
      </div>
    </div>

    <div class="inspector-section">
      <h4>
        <span>Фон</span>
        <select
          :value="slide.background?.type || 'color'"
          @change="(e) => changeBgType(e.target.value)"
          style="width: auto; padding: 3px 6px; font-size: 11px;"
        >
          <option value="color">цвет</option>
          <option value="image">изображение</option>
          <option value="gradient">градиент</option>
        </select>
      </h4>

      <template v-if="slide.background?.type === 'color'">
        <div class="inspector-row">
          <label>Цвет</label>
          <ColorChip :value="slide.background.value" @change="(v) => updateSlide({ background: { type: 'color', value: v } })" />
        </div>
      </template>

      <template v-else-if="slide.background?.type === 'image'">
        <div class="inspector-row">
          <label>Asset</label>
          <select
            :value="slide.background.assetId || ''"
            @change="(e) => updateSlide({ background: { ...slide.background, type: 'image', assetId: e.target.value, fit: slide.background.fit || 'cover' } })"
          >
            <option value="">— не выбрано —</option>
            <option v-for="a in imageAssets" :key="a.id" :value="a.id">{{ a.fileName || a.id }}</option>
          </select>
        </div>
        <div class="inspector-row">
          <label>Загрузить</label>
          <input type="file" accept="image/*" @change="onUploadBg" />
        </div>
        <div class="inspector-row">
          <label>Fit</label>
          <select
            :value="slide.background.fit || 'cover'"
            @change="(e) => updateSlide({ background: { ...slide.background, fit: e.target.value } })"
          >
            <option value="cover">cover</option>
            <option value="contain">contain</option>
            <option value="stretch">stretch</option>
          </select>
        </div>
      </template>

      <template v-else>
        <div class="inspector-row">
          <label>From</label>
          <ColorChip :value="slide.background.from || '#FFFFFF'" @change="(v) => updateSlide({ background: { ...slide.background, from: v } })" />
        </div>
        <div class="inspector-row">
          <label>To</label>
          <ColorChip :value="slide.background.to || '#000000'" @change="(v) => updateSlide({ background: { ...slide.background, to: v } })" />
        </div>
        <div class="inspector-row">
          <label>Угол</label>
          <input type="number" :value="slide.background.angle || 0" @input="(e) => updateSlide({ background: { ...slide.background, angle: +e.target.value } })" />
          <span class="num-suffix">°</span>
        </div>
      </template>
    </div>

    <div class="inspector-section">
      <h4>Заметки</h4>
      <textarea :value="slide.notes || ''" @input="(e) => updateSlide({ notes: e.target.value })" rows="4" />
    </div>
  </div>
</template>

<script>
import ColorChip from './ColorChip.vue';
import { useDocumentStore } from '../../stores/document.js';
import { api } from '../../api/client.js';

export default {
  name: 'SlideInspector',
  components: { ColorChip },
  props: { slide: { type: Object, required: true } },
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
    async onUploadBg(event) {
      const file = event.target.files?.[0];
      if (!file) return;
      const asset = await api.uploadAsset(file);
      this.docStore.addAsset(asset);
      this.updateSlide({
        background: { type: 'image', assetId: asset.id, fit: this.slide.background?.fit || 'cover' },
      });
      event.target.value = '';
    },
  },
};
</script>
