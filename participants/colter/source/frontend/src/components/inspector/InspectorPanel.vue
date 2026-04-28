<template>
  <aside class="element-inspector">
    <div class="inspector-section" style="display:flex; gap:6px;">
      <button class="tb-btn" :class="{ primary: tab === 'doc' }" @click="tab = 'doc'">Документ</button>
      <button class="tb-btn" :class="{ primary: tab === 'slide' }" @click="tab = 'slide'">{{ docStore.mode === 'template' ? 'Макет' : 'Слайд' }}</button>
      <button class="tb-btn" :class="{ primary: tab === 'element' }" :disabled="!selected" @click="tab = 'element'">Элемент</button>
    </div>
    <DocumentInspector v-if="tab === 'doc'" :doc="docStore.doc" />
    <SlideInspector v-else-if="tab === 'slide' && currentSlide" :slide="currentSlide" />
    <ElementInspector
      v-else-if="tab === 'element' && selected"
      :element="selected"
      :slide="currentSlide"
    />
    <div v-else class="inspector-section" style="color:var(--muted); font-size:13px;">
      Выберите элемент на слайде, чтобы редактировать его свойства.
    </div>
  </aside>
</template>

<script>
import { useDocumentStore } from '../../stores/document.js';
import DocumentInspector from './DocumentInspector.vue';
import SlideInspector from './SlideInspector.vue';
import ElementInspector from './ElementInspector.vue';

export default {
  name: 'InspectorPanel',
  components: { DocumentInspector, SlideInspector, ElementInspector },
  data() { return { tab: 'slide' }; },
  computed: {
    docStore() { return useDocumentStore(); },
    currentSlide() { return this.docStore.activeSlide; },
    selected() { return this.docStore.selectedElements[0] || null; },
  },
  watch: {
    selected(val) { if (val) this.tab = 'element'; },
  },
};
</script>
