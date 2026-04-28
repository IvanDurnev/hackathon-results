<template>
  <aside class="element-inspector">
    <div class="inspector-tabs">
      <button :class="{ active: tab === 'doc' }" @click="tab = 'doc'">Документ</button>
      <button :class="{ active: tab === 'slide' }" @click="tab = 'slide'">
        {{ docStore.mode === 'template' ? 'Макет' : 'Слайд' }}
      </button>
      <button :class="{ active: tab === 'element' }" :disabled="!selected" @click="tab = 'element'">Элемент</button>
    </div>
    <DocumentInspector v-if="tab === 'doc'" :doc="docStore.doc" />
    <SlideInspector v-else-if="tab === 'slide' && currentSlide" :slide="currentSlide" />
    <ElementInspector
      v-else-if="tab === 'element' && selected"
      :element="selected"
      :slide="currentSlide"
    />
    <div v-else class="inspector-section" style="color: var(--fg-3); font-size: 12.5px;">
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
