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
          <option v-for="option in slideTypeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </div>

      <div v-if="docStore.mode === 'presentation'" class="inspector-row">
        <label>Номер</label>
        <label class="check-chip">
          <input type="checkbox" :checked="!slide.hideSlideNumber" @change="(e) => updateSlide({ hideSlideNumber: !e.target.checked })" />
          <span>Показывать на этом слайде</span>
        </label>
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
          <option v-for="option in backgroundTypeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </h4>

      <template v-if="slide.background?.type === 'color'">
        <div class="inspector-row">
          <label>Цвет</label>
          <ColorChip :value="slide.background.value" @change="(value) => updateSlide({ background: { type: 'color', value } })" />
        </div>
      </template>

      <template v-else-if="slide.background?.type === 'image'">
        <div class="inspector-row">
          <label>Файл</label>
          <select
            :value="slide.background.assetId || ''"
            @change="(e) => updateSlide({ background: { ...slide.background, type: 'image', assetId: e.target.value, fit: slide.background.fit || 'cover' } })"
          >
            <option value="">— не выбрано —</option>
            <option v-for="asset in imageAssets" :key="asset.id" :value="asset.id">{{ asset.fileName || asset.id }}</option>
          </select>
        </div>

        <div class="inspector-row">
          <label>Загрузить</label>
          <input type="file" accept="image/*" @change="onUploadBg" />
        </div>

        <div class="inspector-row">
          <label>Подгонка</label>
          <select :value="slide.background.fit || 'cover'" @change="(e) => updateSlide({ background: { ...slide.background, fit: e.target.value } })">
            <option v-for="option in fitOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </div>
      </template>

      <template v-else>
        <div class="inspector-row">
          <label>Начало</label>
          <ColorChip :value="slide.background.from || '#FFFFFF'" @change="(value) => updateSlide({ background: { ...slide.background, from: value } })" />
        </div>

        <div class="inspector-row">
          <label>Конец</label>
          <ColorChip :value="slide.background.to || '#000000'" @change="(value) => updateSlide({ background: { ...slide.background, to: value } })" />
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
      <textarea :value="slide.notes || ''" rows="4" @input="(e) => updateSlide({ notes: e.target.value })" />
    </div>

    <div v-if="docStore.mode === 'presentation'" class="inspector-section ai-section">
      <h4>
        <span>AI-перегенерация</span>
        <span v-if="hasPendingImage" class="ac-pill ai-pending">картинка готовится…</span>
      </h4>

      <div class="inspector-row">
        <label>Уточнения</label>
        <textarea
          v-model="regenerateInstructions"
          rows="3"
          placeholder="Например: добавь конкретные цифры за Q3 и упомяни enterprise-сегмент"
        />
      </div>
      <div class="inspector-row">
        <button
          class="tb-btn primary"
          :disabled="regenerating"
          style="width: 100%; justify-content: center;"
          @click="regenerateSlide"
        >
          {{ regenerating ? 'Перегенерируем…' : 'Перегенерировать слайд' }}
        </button>
      </div>

      <template v-if="hasImage">
        <div class="inspector-row" style="margin-top: 10px;">
          <label>Промпт картинки</label>
          <textarea
            v-model="imagePromptOverride"
            rows="3"
            :placeholder="defaultImagePromptPlaceholder"
          />
        </div>
        <div class="inspector-row">
          <button
            class="tb-btn"
            :disabled="regeneratingImage"
            style="width: 100%; justify-content: center;"
            @click="regenerateImage"
          >
            {{ regeneratingImage ? 'Запускаем…' : 'Перегенерировать картинку' }}
          </button>
        </div>
      </template>

      <div v-if="aiError" class="ai-error">{{ aiError }}</div>
    </div>
  </div>
</template>

<script>
import ColorChip from './ColorChip.vue';
import { useDocumentStore } from '../../stores/document.js';
import { api } from '../../api/client.js';

const SLIDE_TYPE_OPTIONS = [
  { value: 'title', label: 'Титульный' },
  { value: 'text', label: 'Текстовый' },
  { value: 'image', label: 'С изображением' },
  { value: 'bullets', label: 'Список' },
  { value: 'conclusion', label: 'Финальный' },
];

const BACKGROUND_TYPE_OPTIONS = [
  { value: 'color', label: 'Цвет' },
  { value: 'image', label: 'Изображение' },
  { value: 'gradient', label: 'Градиент' },
];

const FIT_OPTIONS = [
  { value: 'cover', label: 'Заполнить область' },
  { value: 'contain', label: 'Вписать целиком' },
  { value: 'stretch', label: 'Растянуть' },
];

export default {
  name: 'SlideInspector',
  components: { ColorChip },
  props: { slide: { type: Object, required: true } },
  data() {
    return {
      slideTypeOptions: SLIDE_TYPE_OPTIONS,
      backgroundTypeOptions: BACKGROUND_TYPE_OPTIONS,
      fitOptions: FIT_OPTIONS,
      regenerateInstructions: '',
      imagePromptOverride: '',
      regenerating: false,
      regeneratingImage: false,
      aiError: '',
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    imageAssets() {
      return (this.docStore.doc?.assets || []).filter((asset) => asset.type === 'image');
    },
    imageElement() {
      return this.slide.elements.find((el) => el.type === 'image') || null;
    },
    hasImage() {
      return Boolean(this.imageElement);
    },
    hasPendingImage() {
      const meta = this.imageElement?.meta?.imageGeneration;
      return Boolean(meta && (meta.status === 'pending' || meta.status === 'in_progress'));
    },
    defaultImagePromptPlaceholder() {
      const current = this.imageElement?.generation?.prompt
        || this.imageElement?.meta?.imageGeneration?.prompt;
      if (current) return current.slice(0, 140);
      return '(опционально) английский prompt для генерации изображения';
    },
  },
  watch: {
    'slide.id'() {
      this.regenerateInstructions = '';
      this.imagePromptOverride = '';
      this.aiError = '';
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
      let background;
      if (type === 'color') background = { type: 'color', value: '#FFFFFF' };
      else if (type === 'image') background = { type: 'image', assetId: '', fit: 'cover' };
      else background = { type: 'gradient', from: '#FFFFFF', to: '#111827', angle: 90 };
      this.updateSlide({ background });
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
    async ensureSaved() {
      if (!this.docStore.dirty) return true;
      try {
        await api.savePresentation(this.docStore.doc);
        this.docStore.markSaved(this.docStore.revision);
        return true;
      } catch (err) {
        this.aiError = this.errorText(err, 'Не удалось сохранить перед перегенерацией.');
        return false;
      }
    },
    async regenerateSlide() {
      if (this.regenerating) return;
      this.aiError = '';
      const presentationId = this.docStore.doc?.id;
      if (!presentationId) return;
      if (!(await this.ensureSaved())) return;
      this.regenerating = true;
      try {
        const updated = await api.regenerateSlideContent(presentationId, this.slide.id, {
          instructions: this.regenerateInstructions.trim() || null,
        });
        this.docStore.replacePresentation(updated);
        this.docStore.kickImagePolling();
        this.regenerateInstructions = '';
      } catch (err) {
        this.aiError = this.errorText(err, 'Не удалось перегенерировать слайд.');
      } finally {
        this.regenerating = false;
      }
    },
    async regenerateImage() {
      if (this.regeneratingImage) return;
      this.aiError = '';
      const presentationId = this.docStore.doc?.id;
      if (!presentationId) return;
      if (!(await this.ensureSaved())) return;
      this.regeneratingImage = true;
      try {
        const job = await api.regenerateSlideImage(presentationId, this.slide.id, {
          prompt: this.imagePromptOverride.trim() || null,
        });
        if (this.imageElement) {
          const meta = { ...(this.imageElement.meta || {}) };
          meta.imageGeneration = {
            ...(meta.imageGeneration || {}),
            status: job?.status || 'pending',
            prompt: job?.prompt,
          };
          this.docStore.run({
            type: 'element.updateProps',
            slideId: this.slide.id,
            elementId: this.imageElement.id,
            payload: { props: { meta, assetId: null, placeholder: 'Картинка генерируется…' } },
          });
        }
        this.docStore.kickImagePolling();
        this.imagePromptOverride = '';
      } catch (err) {
        this.aiError = this.errorText(err, 'Не удалось запустить перегенерацию картинки.');
      } finally {
        this.regeneratingImage = false;
      }
    },
    errorText(err, fallback) {
      const detail = err?.detail?.detail || err?.detail;
      if (typeof detail === 'string' && detail.trim()) return detail;
      if (detail && typeof detail === 'object') return JSON.stringify(detail);
      return fallback;
    },
  },
};
</script>

<style scoped>
.ai-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ai-pending {
  background: rgba(255, 181, 71, 0.14);
  border: 1px solid rgba(255, 181, 71, 0.32);
  color: var(--amber-200, #ffb547);
  padding: 2px 8px;
  font-size: 10.5px;
  border-radius: 999px;
  font-weight: 500;
}
.ai-error {
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(239, 93, 74, 0.10);
  border: 1px solid rgba(239, 93, 74, 0.32);
  color: #ef5d4a;
  font-size: 11.5px;
  line-height: 1.4;
}
</style>
