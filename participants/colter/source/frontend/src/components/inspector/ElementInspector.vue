<template>
  <div>
    <div class="inspector-section">
      <h4>
        <span>Элемент</span>
        <span class="ac-pill" style="padding:2px 8px; font-size:10.5px;">{{ el.type }}</span>
      </h4>
      <div class="inspector-row">
        <label>Роль</label>
        <select :value="el.role || 'custom'" @change="(e) => updateProps({ role: e.target.value })">
          <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Поведение</label>
        <select :value="el.contentBehavior?.kind || 'manual'" @change="(e) => updateBehavior({ kind: e.target.value })">
          <option value="static">static</option>
          <option value="placeholder">placeholder</option>
          <option value="generated">generated</option>
          <option value="manual">manual</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Readonly</label>
        <input type="checkbox" :checked="!!el.contentBehavior?.readonly" @change="(e) => updateBehavior({ readonly: e.target.checked })" />
        <label style="margin-left: 24px;">Locked</label>
        <input type="checkbox" :checked="!!el.locked" @change="(e) => updateProps({ locked: e.target.checked })" />
      </div>
      <div class="inspector-row">
        <label>Видим</label>
        <input type="checkbox" :checked="el.visible !== false" @change="(e) => updateProps({ visible: e.target.checked })" />
      </div>
    </div>

    <div class="inspector-section">
      <h4>Геометрия (EMU)</h4>
      <div class="inspector-row">
        <label>X</label>
        <input type="number" :value="el.frame.xEmu" @input="(e) => updateFrameInput({ xEmu: e.target.value })" />
        <label style="width:auto;">Y</label>
        <input type="number" :value="el.frame.yEmu" @input="(e) => updateFrameInput({ yEmu: e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Ширина</label>
        <input type="number" :value="el.frame.wEmu" @input="(e) => updateSizeInput('w', e.target.value)" />
        <label style="width:auto;">Высота</label>
        <input type="number" :value="el.frame.hEmu" @input="(e) => updateSizeInput('h', e.target.value)" />
      </div>
      <div class="inspector-row">
        <label>Поворот</label>
        <input type="number" step="1" :value="el.frame.rotate || 0" @input="(e) => updateFrameInput({ rotate: e.target.value })" />
        <label style="width:auto;">z-index</label>
        <input type="number" :value="el.zIndex" @input="(e) => updateProps({ zIndex: +e.target.value })" />
      </div>
    </div>

    <div v-if="el.type === 'text'" class="inspector-section">
      <h4>Текст</h4>
      <div class="inspector-row">
        <label>Содержимое</label>
        <textarea :value="el.text" @input="(e) => updateText(e.target.value)" rows="3" />
      </div>
      <div class="inspector-row">
        <label>Плейсхолдер</label>
        <input type="text" :value="el.placeholder || ''" @input="(e) => updateProps({ placeholder: e.target.value })" />
      </div>
    </div>

    <div v-if="el.type === 'text'" class="inspector-section">
      <h4>Стиль текста</h4>
      <div class="inspector-row">
        <label>Шрифт</label>
        <select :value="el.style.fontFamily" @change="(e) => onFontChange(e.target.value)">
          <optgroup label="Sans">
            <option v-for="f in fontsByCategory('sans')" :key="f.name" :value="f.name">{{ f.name }}</option>
          </optgroup>
          <optgroup label="Serif">
            <option v-for="f in fontsByCategory('serif')" :key="f.name" :value="f.name">{{ f.name }}</option>
          </optgroup>
          <optgroup label="Mono">
            <option v-for="f in fontsByCategory('mono')" :key="f.name" :value="f.name">{{ f.name }}</option>
          </optgroup>
        </select>
      </div>
      <div class="inspector-row">
        <label>Размер</label>
        <input type="number" min="6" :value="el.style.fontSize" @input="(e) => updateStyle({ fontSize: +e.target.value })" />
        <span class="num-suffix">pt</span>
      </div>
      <div class="inspector-row">
        <label>Толщина</label>
        <select :value="el.style.fontWeight || 400" @change="(e) => updateStyle({ fontWeight: +e.target.value })">
          <option v-for="w in availableWeightOptions" :key="w" :value="w">{{ weightLabel(w) }}</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Стиль</label>
        <div class="btn-group">
          <button type="button" :class="{ active: !!el.style.italic }" @click="updateStyle({ italic: !el.style.italic })" title="Italic">
            <em>I</em>
          </button>
          <button type="button" :class="{ active: !!el.style.underline }" @click="updateStyle({ underline: !el.style.underline })" title="Underline">
            <u>U</u>
          </button>
        </div>
      </div>
      <div class="inspector-row">
        <label>Цвет</label>
        <ColorChip :value="el.style.color || '#111111'" @change="(v) => updateStyle({ color: v })" />
      </div>
      <div class="inspector-row">
        <label>Гориз.</label>
        <div class="btn-group">
          <button type="button" v-for="opt in alignOpts" :key="opt.v" :class="{ active: (el.style.align || 'left') === opt.v }" @click="updateStyle({ align: opt.v })" :title="opt.title">
            <AcIcon :name="opt.icon" :size="13" />
          </button>
        </div>
      </div>
      <div class="inspector-row">
        <label>Верт.</label>
        <div class="btn-group">
          <button type="button" v-for="opt in valignOpts" :key="opt.v" :class="{ active: (el.style.valign || 'top') === opt.v }" @click="updateStyle({ valign: opt.v })" :title="opt.title">
            <AcIcon :name="opt.icon" :size="13" />
          </button>
        </div>
      </div>
      <div class="inspector-row">
        <label>Line height</label>
        <input type="number" step="0.1" :value="el.style.lineHeight || 1.4" @input="(e) => updateStyle({ lineHeight: +e.target.value })" />
      </div>
    </div>

    <div v-if="el.type === 'shape'" class="inspector-section">
      <h4>Фигура</h4>
      <div class="inspector-row">
        <label>Тип</label>
        <select :value="el.shape" @change="(e) => updateProps({ shape: e.target.value })">
          <option value="rect">rect</option>
          <option value="roundRect">roundRect</option>
          <option value="ellipse">ellipse</option>
          <option value="triangle">triangle</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Заливка</label>
        <ColorChip :value="el.style.fill || '#ffffff'" @change="(v) => updateStyle({ fill: v })" />
      </div>
      <div class="inspector-row">
        <label>Контур</label>
        <ColorChip :value="el.style.stroke || '#111111'" @change="(v) => updateStyle({ stroke: v })" />
      </div>
      <div class="inspector-row">
        <label>Толщина</label>
        <input type="number" :value="el.style.strokeWidth || 0" @input="(e) => updateStyle({ strokeWidth: +e.target.value })" />
      </div>
      <div v-if="el.shape === 'roundRect'" class="inspector-row">
        <label>Радиус (EMU)</label>
        <input type="number" :value="el.style.radiusEmu || 0" @input="(e) => updateStyle({ radiusEmu: +e.target.value })" />
      </div>
    </div>

    <div v-if="el.type === 'line'" class="inspector-section">
      <h4>Линия</h4>
      <div class="inspector-row">
        <label>Цвет</label>
        <ColorChip :value="el.style.color || '#111111'" @change="(v) => updateStyle({ color: v })" />
      </div>
      <div class="inspector-row">
        <label>Ширина (EMU)</label>
        <input type="number" :value="el.style.widthEmu" @input="(e) => updateStyle({ widthEmu: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Стиль</label>
        <select :value="el.style.dash || 'solid'" @change="(e) => updateStyle({ dash: e.target.value })">
          <option value="solid">solid</option>
          <option value="dash">dash</option>
          <option value="dot">dot</option>
        </select>
      </div>
    </div>

    <div v-if="el.type === 'image'" class="inspector-section">
      <h4>Изображение</h4>
      <div class="inspector-row">
        <label>Asset</label>
        <select :value="el.assetId || ''" @change="(e) => replaceImage(e.target.value)">
          <option value="">— не выбрано —</option>
          <option v-for="a in imageAssets" :key="a.id" :value="a.id">{{ a.fileName || a.id }}</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Fit</label>
        <select :value="el.fit || 'cover'" @change="(e) => updateProps({ fit: e.target.value })">
          <option value="cover">cover</option>
          <option value="contain">contain</option>
          <option value="stretch">stretch</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Пропорции</label>
        <input type="checkbox" :checked="!!el.preserveAspect" @change="(e) => onPreserveAspect(e.target.checked)" />
        <span style="font-size: 11.5px; color: var(--fg-3); margin-left: 8px;">сохранять при ресайзе</span>
      </div>
      <div class="inspector-row">
        <label>Загрузить</label>
        <input type="file" accept="image/*" @change="onUpload" />
      </div>
    </div>

    <div class="inspector-section">
      <h4>Ограничения</h4>
      <div class="inspector-row">
        <label>maxChars</label>
        <input type="number" :value="el.constraints?.maxChars || ''" @input="(e) => updateConstraints({ maxChars: e.target.value === '' ? null : +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>maxLines</label>
        <input type="number" :value="el.constraints?.maxLines || ''" @input="(e) => updateConstraints({ maxLines: e.target.value === '' ? null : +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>overflow</label>
        <select :value="el.constraints?.overflow || ''" @change="(e) => updateConstraints({ overflow: e.target.value || null })">
          <option value="">—</option>
          <option value="clip">clip</option>
          <option value="shrink">shrink</option>
          <option value="ellipsis">ellipsis</option>
          <option value="error">error</option>
        </select>
      </div>
    </div>

    <div class="inspector-section">
      <button class="tb-btn danger" style="width:100%; justify-content:center;" @click="del">
        <AcIcon name="trash" :size="13" /> Удалить элемент
      </button>
    </div>
  </div>
</template>

<script>
import AcIcon from '../AcIcon.vue';
import ColorChip from './ColorChip.vue';
import { useDocumentStore } from '../../stores/document.js';
import { api } from '../../api/client.js';
import { FONT_FAMILIES, ensureFont, availableWeights } from '../../core/fonts.js';

const WEIGHT_LABELS = {
  100: 'Thin',
  200: 'Extra Light',
  300: 'Light',
  400: 'Regular',
  500: 'Medium',
  600: 'Semibold',
  700: 'Bold',
  800: 'Extra Bold',
  900: 'Black',
};

export default {
  name: 'ElementInspector',
  components: { AcIcon, ColorChip },
  props: {
    element: { type: Object, required: true },
    slide: { type: Object, required: true },
  },
  data() {
    return {
      roles: [
        'title', 'subtitle', 'body', 'caption', 'bulletList',
        'image', 'logo', 'footer', 'slideNumber', 'decorative', 'custom',
      ],
      alignOpts: [
        { v: 'left', icon: 'alignLeft', title: 'Слева' },
        { v: 'center', icon: 'alignCenter', title: 'По центру' },
        { v: 'right', icon: 'alignRight', title: 'Справа' },
        { v: 'justify', icon: 'alignJustify', title: 'По ширине' },
      ],
      valignOpts: [
        { v: 'top', icon: 'alignTop', title: 'По верху' },
        { v: 'middle', icon: 'alignMiddle', title: 'По центру' },
        { v: 'bottom', icon: 'alignBottom', title: 'По низу' },
      ],
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    el() { return this.element; },
    imageAssets() {
      return (this.docStore.doc?.assets || []).filter((a) => a.type === 'image');
    },
    availableWeightOptions() {
      const fam = this.el.style?.fontFamily;
      const w = availableWeights(fam);
      return w.length ? w : [400];
    },
  },
  watch: {
    'element.style.fontFamily': {
      handler(f) { ensureFont(f); },
      immediate: true,
    },
  },
  methods: {
    fontsByCategory(cat) { return FONT_FAMILIES.filter((f) => f.category === cat); },
    weightLabel(w) { return `${WEIGHT_LABELS[w] || w} (${w})`; },
    onFontChange(family) {
      ensureFont(family);
      const supported = availableWeights(family);
      const current = this.el.style.fontWeight || 400;
      const nextWeight = supported.includes(current)
        ? current
        : (supported.includes(400) ? 400 : supported[0]);
      this.updateStyle({ fontFamily: family, fontWeight: nextWeight });
    },
    onPreserveAspect(v) {
      this.updateProps({ preserveAspect: v });
    },
    numberFromInput(value) {
      if (value === '' || value == null) return null;
      const n = Number(value);
      return Number.isFinite(n) ? n : null;
    },
    updateSizeInput(axis, value) {
      const n = this.numberFromInput(value);
      if (n == null) return;
      const min = axis === 'w' ? 100000 : 50000;
      this.updateSize(axis, Math.max(min, Math.round(n)));
    },
    updateFrameInput(patch) {
      const next = {};
      Object.entries(patch).forEach(([key, value]) => {
        const n = this.numberFromInput(value);
        if (n == null) return;
        next[key] = key === 'rotate' ? n : Math.round(n);
      });
      if (Object.keys(next).length) this.updateFrame(next);
    },
    updateSize(axis, val) {
      if (!Number.isFinite(val)) return;
      const f = { ...this.el.frame };
      if (this.el.type === 'image' && this.el.preserveAspect) {
        const ratio = (this.el.frame.wEmu || 1) / (this.el.frame.hEmu || 1);
        if (axis === 'w') {
          f.wEmu = val;
          f.hEmu = Math.round(val / ratio);
        } else {
          f.hEmu = val;
          f.wEmu = Math.round(val * ratio);
        }
      } else if (axis === 'w') {
        f.wEmu = val;
      } else {
        f.hEmu = val;
      }
      this.docStore.run({
        type: 'element.resize',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { frame: f },
      });
    },
    updateFrame(patch) {
      this.docStore.run({
        type: 'element.resize',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { frame: { ...this.el.frame, ...patch } },
      });
    },
    updateProps(props) {
      this.docStore.run({
        type: 'element.updateProps',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { props },
      });
    },
    updateBehavior(patch) {
      this.docStore.run({
        type: 'element.updateBehavior',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { contentBehavior: { ...this.el.contentBehavior, ...patch } },
      });
    },
    updateStyle(patch) {
      this.docStore.run({
        type: 'element.updateStyle',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { style: patch },
      });
    },
    updateText(text) {
      this.docStore.run({
        type: 'element.updateText',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { text },
      });
    },
    updateConstraints(patch) {
      const next = { ...(this.el.constraints || {}), ...patch };
      Object.keys(next).forEach((k) => { if (next[k] == null) delete next[k]; });
      this.updateProps({ constraints: next });
    },
    replaceImage(assetId) {
      this.docStore.run({
        type: 'image.replace',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { assetId: assetId || null },
      });
    },
    async onUpload(event) {
      const file = event.target.files?.[0];
      if (!file) return;
      const asset = await api.uploadAsset(file);
      this.docStore.addAsset(asset);
      this.replaceImage(asset.id);
      event.target.value = '';
    },
    del() {
      this.docStore.run({
        type: 'element.delete',
        slideId: this.slide.id,
        elementId: this.el.id,
      });
      this.docStore.clearSelection();
    },
  },
};
</script>
