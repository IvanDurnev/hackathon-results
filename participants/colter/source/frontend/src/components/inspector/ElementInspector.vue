<template>
  <div>
    <div class="inspector-section">
      <h4>Геометрия (EMU)</h4>
      <div class="inspector-row">
        <label>X</label>
        <input type="number" :value="el.frame.xEmu" @input="(e) => updateFrame({ xEmu: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Y</label>
        <input type="number" :value="el.frame.yEmu" @input="(e) => updateFrame({ yEmu: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Ширина</label>
        <input type="number" :value="el.frame.wEmu" @input="(e) => updateFrame({ wEmu: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Высота</label>
        <input type="number" :value="el.frame.hEmu" @input="(e) => updateFrame({ hEmu: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Поворот</label>
        <input type="number" step="1" :value="el.frame.rotate || 0" @input="(e) => updateFrame({ rotate: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>z-index</label>
        <input type="number" :value="el.zIndex" @input="(e) => updateProps({ zIndex: +e.target.value })" />
      </div>
    </div>

    <div class="inspector-section">
      <h4>Поведение</h4>
      <div class="inspector-row">
        <label>Роль</label>
        <select :value="el.role || 'custom'" @change="(e) => updateProps({ role: e.target.value })">
          <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Тип контента</label>
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
      </div>
      <div class="inspector-row">
        <label>Locked</label>
        <input type="checkbox" :checked="!!el.locked" @change="(e) => updateProps({ locked: e.target.checked })" />
      </div>
      <div class="inspector-row">
        <label>Видим</label>
        <input type="checkbox" :checked="el.visible !== false" @change="(e) => updateProps({ visible: e.target.checked })" />
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
        <input type="text" :value="el.style.fontFamily" @input="(e) => updateStyle({ fontFamily: e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Размер</label>
        <input type="number" min="6" :value="el.style.fontSize" @input="(e) => updateStyle({ fontSize: +e.target.value })" />
      </div>
      <div class="inspector-row">
        <label>Толщина</label>
        <select :value="el.style.fontWeight || 400" @change="(e) => updateStyle({ fontWeight: +e.target.value })">
          <option value="300">Light</option>
          <option value="400">Regular</option>
          <option value="500">Medium</option>
          <option value="600">Semibold</option>
          <option value="700">Bold</option>
          <option value="800">Extra</option>
        </select>
      </div>
      <div class="inspector-row">
        <label>Italic</label>
        <input type="checkbox" :checked="!!el.style.italic" @change="(e) => updateStyle({ italic: e.target.checked })" />
      </div>
      <div class="inspector-row">
        <label>Underline</label>
        <input type="checkbox" :checked="!!el.style.underline" @change="(e) => updateStyle({ underline: e.target.checked })" />
      </div>
      <div class="inspector-row">
        <label>Цвет</label>
        <input type="color" :value="el.style.color || '#111111'" @input="(e) => updateStyle({ color: e.target.value.toUpperCase() })" />
        <input type="text" :value="el.style.color || '#111111'" @input="(e) => updateStyle({ color: e.target.value })" style="max-width:100px;" />
      </div>
      <div class="inspector-row">
        <label>Выравн.</label>
        <select :value="el.style.align" @change="(e) => updateStyle({ align: e.target.value })">
          <option value="left">left</option>
          <option value="center">center</option>
          <option value="right">right</option>
          <option value="justify">justify</option>
        </select>
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
        <input type="color" :value="el.style.fill || '#ffffff'" @input="(e) => updateStyle({ fill: e.target.value.toUpperCase() })" />
        <input type="text" :value="el.style.fill || ''" @input="(e) => updateStyle({ fill: e.target.value })" style="max-width:100px;" />
      </div>
      <div class="inspector-row">
        <label>Контур</label>
        <input type="color" :value="el.style.stroke || '#111111'" @input="(e) => updateStyle({ stroke: e.target.value.toUpperCase() })" />
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
        <input type="color" :value="el.style.color || '#111111'" @input="(e) => updateStyle({ color: e.target.value.toUpperCase() })" />
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
      <button class="tb-btn danger" style="width:100%;" @click="del">Удалить элемент</button>
    </div>
  </div>
</template>

<script>
import { useDocumentStore } from '../../stores/document.js';
import { api } from '../../api/client.js';

export default {
  name: 'ElementInspector',
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
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    el() { return this.element; },
    imageAssets() {
      return (this.docStore.doc?.assets || []).filter((a) => a.type === 'image');
    },
  },
  methods: {
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
