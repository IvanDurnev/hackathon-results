<template>
  <div class="home-page">
    <h1>Amur Code — редактор презентаций</h1>
    <p style="color:var(--muted); margin-top:0;">
      MVP по техническому заданию: JSON-документ, координаты в EMU, экспорт в PPTX.
    </p>

    <div style="display:flex; align-items:center; gap:12px; margin: 24px 0 8px;">
      <h2 style="margin:0;">Презентации</h2>
      <Button label="Новая презентация" icon="pi pi-plus" @click="openCreateDialog" />
    </div>
    <div class="doc-grid">
      <router-link
        v-for="p in presentations"
        :key="p.id"
        :to="`/presentations/${p.id}`"
        class="doc-card"
      >
        <strong>{{ p.name }}</strong>
        <div class="meta">{{ p.slideCount }} слайд(ов) · id: {{ p.id }}</div>
      </router-link>
      <div v-if="presentations.length === 0" style="color:var(--muted);">Пока нет презентаций.</div>
    </div>

    <div style="display:flex; align-items:center; gap:12px; margin: 32px 0 8px;">
      <h2 style="margin:0;">Шаблоны</h2>
      <Button label="Новый шаблон" icon="pi pi-plus" severity="secondary" outlined @click="createTemplate" />
    </div>
    <div class="doc-grid">
      <router-link
        v-for="t in templates"
        :key="t.id"
        :to="`/templates/${t.id}`"
        class="doc-card"
      >
        <strong>{{ t.name }}</strong>
        <div class="meta">id: {{ t.id }}</div>
      </router-link>
      <div v-if="templates.length === 0" style="color:var(--muted);">Шаблонов нет.</div>
    </div>

    <Dialog v-model:visible="createOpen" header="Новая презентация" modal :style="{ width: '420px' }">
      <div style="display:flex; flex-direction:column; gap:8px;">
        <label>
          Название
          <InputText v-model="createName" style="width:100%; margin-top:4px;" />
        </label>
        <label style="margin-top:8px;">
          Шаблон
          <Dropdown v-model="createTemplateId" :options="templateOptions" optionLabel="name" optionValue="id" placeholder="Выберите шаблон" style="width:100%; margin-top:4px;" />
        </label>
      </div>
      <template #footer>
        <Button label="Отмена" severity="secondary" text @click="createOpen = false" />
        <Button label="Создать" :disabled="!createTemplateId || !createName" @click="createPresentation" />
      </template>
    </Dialog>
  </div>
</template>

<script>
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/select';
import { api } from '../api/client.js';
import { makePresentation, slideFromLayout } from '../core/factories.js';
import { uid } from '../core/ids.js';

export default {
  name: 'HomeView',
  components: { Button, Dialog, InputText, Dropdown },
  data() {
    return {
      presentations: [],
      templates: [],
      createOpen: false,
      createName: '',
      createTemplateId: null,
    };
  },
  computed: {
    templateOptions() {
      return this.templates.map((t) => ({ id: t.id, name: t.name }));
    },
  },
  async mounted() {
    await this.refresh();
  },
  methods: {
    async refresh() {
      [this.presentations, this.templates] = await Promise.all([
        api.listPresentations(),
        api.listTemplates(),
      ]);
    },
    async openCreateDialog() {
      if (!this.templates.length) await this.refresh();
      this.createName = 'Новая презентация';
      this.createTemplateId = this.templates[0]?.id || null;
      this.createOpen = true;
    },
    async createPresentation() {
      const tpl = await api.getTemplate(this.createTemplateId);
      const doc = makePresentation({ name: this.createName, templateId: tpl.id, theme: tpl.theme });
      doc.slideSize = JSON.parse(JSON.stringify(tpl.slideSize));
      const titleLayout = tpl.layouts.find((l) => l.slideType === 'title') || tpl.layouts[0];
      if (titleLayout) doc.slides.push(slideFromLayout(titleLayout));
      const saved = await api.createPresentation(doc);
      this.createOpen = false;
      this.$router.push(`/presentations/${saved.id}`);
    },
    async createTemplate() {
      const id = uid('tmpl');
      const tpl = {
        schemaVersion: '1.0.0',
        documentType: 'template',
        id,
        name: 'Новый шаблон',
        slideSize: { widthEmu: 12192000, heightEmu: 6858000, ratio: '16:9' },
        theme: {
          fonts: { heading: 'Inter', body: 'Inter' },
          colors: { background: '#FFFFFF', text: '#111827', primary: '#2563EB', secondary: '#64748B', accent: '#F97316' },
        },
        layouts: [
          {
            id: uid('layout'),
            name: 'Title',
            slideType: 'title',
            background: { type: 'color', value: '#FFFFFF' },
            elements: [],
          },
        ],
        assets: [],
      };
      const saved = await api.createTemplate(tpl);
      this.$router.push(`/templates/${saved.id}`);
    },
  },
};
</script>
