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
          <option value="custom">custom</option>
        </select>
      </div>
    </div>
    <div class="inspector-section">
      <h4>Тема — шрифты</h4>
      <div class="inspector-row">
        <label>Heading</label>
        <input type="text" :value="doc.theme.fonts.heading" @input="(e) => updateThemeFont('heading', e.target.value)" />
      </div>
      <div class="inspector-row">
        <label>Body</label>
        <input type="text" :value="doc.theme.fonts.body" @input="(e) => updateThemeFont('body', e.target.value)" />
      </div>
    </div>
    <div class="inspector-section">
      <h4>Тема — цвета</h4>
      <div v-for="key in colorKeys" :key="key" class="inspector-row">
        <label>{{ key }}</label>
        <input type="color" :value="doc.theme.colors[key]" @input="(e) => updateThemeColor(key, e.target.value.toUpperCase())" />
        <input type="text" :value="doc.theme.colors[key]" @input="(e) => updateThemeColor(key, e.target.value)" style="max-width:100px;" />
      </div>
    </div>
  </div>
</template>

<script>
import { useDocumentStore } from '../../stores/document.js';

export default {
  name: 'DocumentInspector',
  props: { doc: { type: Object, required: true } },
  data() {
    return { colorKeys: ['background', 'text', 'primary', 'secondary', 'accent'] };
  },
  computed: {
    docStore() { return useDocumentStore(); },
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
    updateThemeFont(key, value) {
      const theme = JSON.parse(JSON.stringify(this.doc.theme));
      theme.fonts[key] = value;
      this.updateDoc({ theme });
    },
    updateThemeColor(key, value) {
      const theme = JSON.parse(JSON.stringify(this.doc.theme));
      theme.colors[key] = value;
      this.updateDoc({ theme });
    },
  },
};
</script>
