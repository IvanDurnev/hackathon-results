<template>
  <div>
    <div class="inspector-section">
      <h4>Документ</h4>

      <div class="inspector-row">
        <label>Имя</label>
        <input type="text" :value="doc.name" @input="(e) => updateDoc({ name: e.target.value })" />
      </div>

      <div class="inspector-row">
        <label>Формат</label>
        <select :value="doc.slideSize.ratio" @change="(e) => setRatio(e.target.value)">
          <option value="16:9">16:9</option>
          <option value="4:3">4:3</option>
        </select>
      </div>
    </div>

    <div v-if="docStore.mode === 'presentation'" class="inspector-section">
      <h4>Нумерация слайдов</h4>

      <div class="inspector-row">
        <label>Включить</label>
        <input type="checkbox" :checked="!!numberingEnabled" @change="(e) => setNumbering({ enabled: e.target.checked })" />
      </div>

      <div v-if="numberingEnabled" class="inspector-row">
        <label>Титульный</label>
        <input type="checkbox" :checked="!!numberingHideTitle" @change="(e) => setNumbering({ hideOnTitle: e.target.checked })" />
        <span style="font-size: 11.5px; color: var(--fg-3); margin-left: 8px;">скрывать номер</span>
      </div>

      <div v-if="numberingEnabled" class="inspector-row">
        <label>Формат</label>
        <select :value="numberingFormat" @change="(e) => setNumbering({ format: e.target.value })">
          <option value="number">1</option>
          <option value="number-of">1 / 12</option>
          <option value="page">Слайд 1</option>
        </select>
      </div>
    </div>

    <div class="inspector-section">
      <h4>
        <span>Тема - шрифты</span>
        <button class="tb-btn ghost" style="font-size:10.5px; padding:3px 8px;" :disabled="!hasTextElements" @click="applyThemeFonts">Применить</button>
      </h4>

      <div class="inspector-row">
        <label>Заголовки</label>
        <select :value="doc.theme.fonts.heading" @change="(e) => updateThemeFont('heading', e.target.value)">
          <option v-for="font in fonts" :key="font.name" :value="font.name">{{ font.name }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Текст</label>
        <select :value="doc.theme.fonts.body" @change="(e) => updateThemeFont('body', e.target.value)">
          <option v-for="font in fonts" :key="font.name" :value="font.name">{{ font.name }}</option>
        </select>
      </div>

      <div class="inspector-note">
        Кнопка применит выбранные шрифты ко всем текстовым элементам по ролям.
      </div>
    </div>

    <div class="inspector-section">
      <h4>
        <span>Тема - цвета</span>
        <button class="tb-btn ghost" style="font-size:10.5px; padding:3px 8px;" @click="applyThemeColors">Применить</button>
      </h4>

      <div v-for="key in colorKeys" :key="key" class="inspector-row">
        <label>{{ colorLabels[key] }}</label>
        <ColorChip :value="doc.theme.colors[key]" @change="(value) => updateThemeColor(key, value)" />
      </div>

      <div class="inspector-note">
        Фон применится к однотонным слайдам, цвет текста - ко всем текстовым элементам.
      </div>
    </div>
  </div>
</template>

<script>
import ColorChip from './ColorChip.vue';
import { useDocumentStore } from '../../stores/document.js';
import { FONT_FAMILIES, ensureFont } from '../../core/fonts.js';

const COLOR_LABELS = {
  background: 'Фон',
  text: 'Текст',
  primary: 'Основной',
  secondary: 'Вторичный',
  accent: 'Акцент',
};

export default {
  name: 'DocumentInspector',
  components: { ColorChip },
  props: { doc: { type: Object, required: true } },
  data() {
    return {
      colorKeys: ['background', 'text', 'primary', 'secondary', 'accent'],
      colorLabels: COLOR_LABELS,
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    fonts() { return FONT_FAMILIES; },
    slidesOrLayouts() {
      return this.docStore.mode === 'template' ? (this.doc.layouts || []) : (this.doc.slides || []);
    },
    hasTextElements() {
      return this.slidesOrLayouts.some((slide) => (slide.elements || []).some((element) => element.type === 'text'));
    },
    numbering() { return this.doc.slideNumbering || {}; },
    numberingEnabled() { return !!this.numbering.enabled; },
    numberingHideTitle() { return this.numbering.hideOnTitle !== false; },
    numberingFormat() { return this.numbering.format || 'number-of'; },
  },
  methods: {
    updateDoc(props) {
      this.docStore.run({ type: 'doc.update', payload: { props } });
    },
    setRatio(ratio) {
      let widthEmu = this.doc.slideSize.widthEmu;
      let heightEmu = this.doc.slideSize.heightEmu;
      if (ratio === '16:9') {
        widthEmu = 12192000;
        heightEmu = 6858000;
      } else if (ratio === '4:3') {
        widthEmu = 9144000;
        heightEmu = 6858000;
      }
      this.updateDoc({ slideSize: { widthEmu, heightEmu, ratio } });
    },
    setNumbering(patch) {
      const next = {
        enabled: this.numberingEnabled,
        hideOnTitle: this.numberingHideTitle,
        format: this.numberingFormat,
        ...patch,
      };
      this.updateDoc({ slideNumbering: next });
    },
    updateThemeFont(key, value) {
      ensureFont(value);
      const theme = JSON.parse(JSON.stringify(this.doc.theme));
      theme.fonts[key] = value;
      this.updateDoc({ theme });
    },
    updateThemeColor(key, value) {
      const theme = JSON.parse(JSON.stringify(this.doc.theme));
      theme.colors[key] = value;
      this.updateDoc({ theme });
    },
    applyThemeFonts() {
      const theme = this.doc.theme;
      ensureFont(theme.fonts.heading);
      ensureFont(theme.fonts.body);
      this.slidesOrLayouts.forEach((slide) => {
        (slide.elements || []).forEach((element) => {
          if (element.type !== 'text') return;
          const isHeading = ['title', 'subtitle'].includes(element.role);
          const family = isHeading ? theme.fonts.heading : theme.fonts.body;
          this.docStore.run({
            type: 'element.updateStyle',
            slideId: slide.id,
            elementId: element.id,
            payload: { style: { fontFamily: family } },
          });
        });
      });
    },
    applyThemeColors() {
      const theme = this.doc.theme;
      this.slidesOrLayouts.forEach((slide) => {
        if (slide.background?.type === 'color') {
          this.docStore.run({
            type: 'slide.update',
            slideId: slide.id,
            payload: { props: { background: { type: 'color', value: theme.colors.background } } },
          });
        }
        (slide.elements || []).forEach((element) => {
          if (element.type !== 'text') return;
          this.docStore.run({
            type: 'element.updateStyle',
            slideId: slide.id,
            elementId: element.id,
            payload: { style: { color: theme.colors.text } },
          });
        });
      });
    },
  },
};
</script>
