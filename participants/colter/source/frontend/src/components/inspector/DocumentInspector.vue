<template>
  <div>
    <div class="inspector-section">
      <h4>Документ</h4>
      <div class="inspector-row">
        <label>Имя</label>
        <input type="text" :value="doc.name" @input="(e) => updateDoc({ name: e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Соотношение</label>
        <select :value="doc.slideSize.ratio" @change="(e) => setRatio(e.target.value)">
          <option value="16:9">16:9</option>
          <option value="4:3">4:3</option>
        </select>
      </div>
    </div>

    <div v-if="docStore.mode === 'presentation'" class="inspector-section">
      <h4>Нумерация слайдов</h4>
      <div class="inspector-row">
        <label>Включена</label>
        <input type="checkbox" :checked="!!numberingEnabled" @change="(e) => setNumbering({ enabled: e.target.checked })" />
      </div>
      <div class="inspector-row" v-if="numberingEnabled">
        <label>Скрыть на титульном</label>
        <input type="checkbox" :checked="!!numberingHideTitle" @change="(e) => setNumbering({ hideOnTitle: e.target.checked })" />
      </div>
      <div class="inspector-row" v-if="numberingEnabled">
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
        <span>Тема — шрифты</span>
        <button class="tb-btn ghost" style="font-size:10.5px; padding:3px 8px;" :disabled="!hasTextElements" @click="applyThemeFonts">Применить</button>
      </h4>
      <div class="inspector-row">
        <label>Heading</label>
        <select :value="doc.theme.fonts.heading" @change="(e) => updateThemeFont('heading', e.target.value)">
          <option v-for="f in fonts" :key="f.name" :value="f.name">{{ f.name }}</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Body</label>
        <select :value="doc.theme.fonts.body" @change="(e) => updateThemeFont('body', e.target.value)">
          <option v-for="f in fonts" :key="f.name" :value="f.name">{{ f.name }}</option>
        </select>
      </div>
      <div style="font-size: 11px; color: var(--fg-4); line-height: 1.4;">
        Нажми «Применить» — текстовые элементы по ролям получат тематический шрифт.
      </div>
    </div>

    <div class="inspector-section">
      <h4>
        <span>Тема — цвета</span>
        <button class="tb-btn ghost" style="font-size:10.5px; padding:3px 8px;" @click="applyThemeColors">Применить</button>
      </h4>
      <div v-for="key in colorKeys" :key="key" class="inspector-row">
        <label>{{ key }}</label>
        <ColorChip :value="doc.theme.colors[key]" @change="(v) => updateThemeColor(key, v)" />
      </div>
      <div style="font-size: 11px; color: var(--fg-4); line-height: 1.4;">
        «background» применится к фону всех слайдов с однотонным фоном; «text» — ко всем текстовым элементам, кроме явно перекрашенных.
      </div>
    </div>
  </div>
</template>

<script>
import ColorChip from './ColorChip.vue';
import { useDocumentStore } from '../../stores/document.js';
import { FONT_FAMILIES, ensureFont } from '../../core/fonts.js';

export default {
  name: 'DocumentInspector',
  components: { ColorChip },
  props: { doc: { type: Object, required: true } },
  data() {
    return { colorKeys: ['background', 'text', 'primary', 'secondary', 'accent'] };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    fonts() { return FONT_FAMILIES; },
    slidesOrLayouts() {
      return this.docStore.mode === 'template' ? (this.doc.layouts || []) : (this.doc.slides || []);
    },
    hasTextElements() {
      return this.slidesOrLayouts.some((s) => (s.elements || []).some((e) => e.type === 'text'));
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
      if (ratio === '16:9') { widthEmu = 12192000; heightEmu = 6858000; }
      else if (ratio === '4:3') { widthEmu = 9144000; heightEmu = 6858000; }
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
      this.slidesOrLayouts.forEach((s) => {
        (s.elements || []).forEach((el) => {
          if (el.type !== 'text') return;
          const headingRoles = ['title', 'subtitle'];
          const isHeading = headingRoles.includes(el.role);
          const family = isHeading ? theme.fonts.heading : theme.fonts.body;
          this.docStore.run({
            type: 'element.updateStyle',
            slideId: s.id,
            elementId: el.id,
            payload: { style: { fontFamily: family } },
          });
        });
      });
    },
    applyThemeColors() {
      const theme = this.doc.theme;
      this.slidesOrLayouts.forEach((s) => {
        if (s.background?.type === 'color') {
          this.docStore.run({
            type: 'slide.update',
            slideId: s.id,
            payload: { props: { background: { type: 'color', value: theme.colors.background } } },
          });
        }
        (s.elements || []).forEach((el) => {
          if (el.type === 'text') {
            this.docStore.run({
              type: 'element.updateStyle',
              slideId: s.id,
              elementId: el.id,
              payload: { style: { color: theme.colors.text } },
            });
          }
        });
      });
    },
  },
};
</script>
