<template>
  <div class="home-shell">
    <header class="home-header">
      <nav class="home-nav">
        <a class="active">Главная</a>
        <a @click.prevent="scrollTo('decks')">Презентации</a>
        <a @click.prevent="scrollTo('templates')">Шаблоны</a>
      </nav>
      <div class="spacer" />
    </header>

    <!-- Hero composer -->
    <section class="hero">
      <div class="hero-top">
        <span class="ac-chip"><AcIcon name="sparkle" :size="12" /> AI генерация</span>
        <h1>
          Опиши идею
          <span class="accent">— получи презентацию</span>
        </h1>
        <p>Редактор собирает структуру, верстает слайды и экспортирует в PPTX. Вы редактируете — он подстраивается.</p>
      </div>

      <div class="composer">
        <textarea
          class="composer-textarea"
          placeholder="Презентация для совета директоров: итоги Q3, 14 слайдов, акцент на retention и новый сегмент enterprise…"
          v-model="prompt"
          rows="3"
          @keydown.meta.enter.prevent="generate"
          @keydown.ctrl.enter.prevent="generate"
        />
        <div class="composer-bar">
          <div class="composer-basis-toggle" role="radiogroup" aria-label="Основа генерации">
            <button
              type="button"
              :class="{ active: basisKind === 'layout' }"
              @click="setBasisKind('layout')"
            >
              <AcIcon name="layers" :size="13" />
              Макет
            </button>
            <button
              type="button"
              :class="{ active: basisKind === 'style' }"
              @click="setBasisKind('style')"
            >
              <AcIcon name="palette" :size="13" />
              Стиль
            </button>
          </div>
          <SelectChip
            v-if="basisKind === 'layout'"
            icon="layers"
            :value="composerTpl"
            :options="templateOptionLabels"
            @update="setComposerTpl"
            placeholder="Макет"
          />
          <SelectChip
            v-else
            icon="palette"
            :value="stylePreset"
            :options="styleOptions"
            @update="setStylePreset"
            placeholder="Стиль"
          />
          <div class="slide-count-chip" :title="`Количество слайдов: ${slideCount}`">
            <AcIcon name="grid" :size="13" />
            <button
              type="button"
              class="slide-count-step"
              :disabled="slideCount <= 1"
              @click="setSlideCount(slideCount - 1)"
              aria-label="Уменьшить количество слайдов"
            >−</button>
            <input
              type="number"
              class="slide-count-input"
              :min="1"
              :max="40"
              :value="slideCount"
              @input="(e) => setSlideCount(Number(e.target.value))"
              @blur="(e) => setSlideCount(Number(e.target.value))"
            />
            <span class="slide-count-suffix">{{ slideCountWord }}</span>
            <button
              type="button"
              class="slide-count-step"
              :disabled="slideCount >= 40"
              @click="setSlideCount(slideCount + 1)"
              aria-label="Увеличить количество слайдов"
            >+</button>
          </div>
          <button
            type="button"
            class="tb-btn ghost"
            :disabled="extractingDoc"
            :title="extractingDoc ? 'Извлекаем текст…' : 'Прикрепить PDF / DOCX / TXT'"
            @click="$refs.docUpload.click()"
          >
            <AcIcon name="plus" :size="13" />
            {{ extractingDoc ? 'Загружаем…' : 'Прикрепить файл' }}
          </button>
          <input
            ref="docUpload"
            type="file"
            accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
            style="display:none"
            @change="onDocUpload"
          />
          <span class="composer-counter">{{ prompt.length }}/4000</span>
          <button
            class="tb-btn primary"
            style="padding:8px 14px;"
            :disabled="!canGenerate || generationLoading"
            @click="generate"
          >
            <AcIcon name="sparkle" :size="14" />
            {{ generationLoading ? 'Готовим оглавление…' : 'Сгенерировать' }}
            <span class="ac-kbd" style="background:rgba(255,255,255,0.30); color:rgba(255,255,255,0.92); border-color:rgba(255,255,255,0.35);">⏎</span>
          </button>
        </div>
        <div v-if="attachedDocs.length" class="composer-attachments">
          <span
            v-for="(doc, i) in attachedDocs"
            :key="`${doc.fileName}-${i}`"
            class="composer-attachment"
            :title="`${doc.fileName} · ${doc.length} симв.`"
          >
            <AcIcon name="file" :size="11" />
            {{ doc.fileName }}
            <button
              type="button"
              class="composer-attachment-remove"
              @click="removeAttachment(i)"
              aria-label="Убрать файл"
            >×</button>
          </span>
        </div>
      </div>

      <div v-if="generationError" class="generation-error">
        {{ generationError }}
      </div>

      <div class="examples">
        <button v-for="ex in examples" :key="ex" class="example-pill" @click="prompt = ex">
          <AcIcon name="sparkle" :size="11" /> {{ ex }}
        </button>
      </div>
    </section>

    <!-- Recent decks -->
    <section id="decks" class="section-row">
      <div class="section-head">
        <h2>Недавние презентации</h2>
        <span class="count">{{ presentations.length }}</span>
        <div class="spacer" />
        <button class="tb-btn primary" @click="openCreateDialog">
          <AcIcon name="plus" :size="13" /> Новая презентация
        </button>
      </div>
      <div v-if="presentations.length" class="deck-grid">
        <router-link
          v-for="(p, i) in presentations"
          :key="p.id"
          class="deck-card"
          :to="`/presentations/${p.id}`"
        >
          <div class="deck-card-preview" :style="previewStyle(i)">
            <div class="accent-bar" :style="{ background: accentFor(i) }" />
            <div class="preview-title">{{ p.name }}</div>
            <div class="preview-sub">{{ p.slideCount }} слайдов</div>
          </div>
          <div class="deck-card-meta">
            <div class="name">{{ p.name }}</div>
            <div class="info">
              <span>{{ p.slideCount }} слайдов</span>
              <span>·</span>
              <span style="font-family: var(--font-mono); color: var(--fg-3);">{{ p.id.slice(-8) }}</span>
            </div>
          </div>
        </router-link>
      </div>
      <div v-else class="empty-state">
        Пока нет презентаций. Опишите идею в композере выше или создайте новую вручную.
      </div>
    </section>

    <!-- Templates row -->
    <section id="templates" class="section-row" style="padding-bottom: 64px;">
      <div class="section-head">
        <h2>Шаблоны</h2>
        <span class="count">{{ templates.length }}</span>
        <div class="spacer" />
        <button
          class="tb-btn"
          :disabled="importingTemplate"
          @click="$refs.tplUpload.click()"
        >
          <AcIcon name="upload" :size="13" />
          {{ importingTemplate ? 'Импортируем…' : 'Импорт PPTX' }}
        </button>
        <input
          ref="tplUpload"
          type="file"
          accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation"
          style="display:none"
          @change="onTemplatePptxUpload"
        />
        <button class="tb-btn" @click="createTemplate">
          <AcIcon name="plus" :size="13" /> Новый шаблон
        </button>
      </div>
      <div v-if="templateImportError" class="generation-error" style="margin: 8px 0;">
        {{ templateImportError }}
      </div>
      <div v-if="templates.length" class="template-grid">
        <router-link
          v-for="(t, i) in templates"
          :key="t.id"
          class="template-card"
          :to="`/templates/${t.id}`"
        >
          <div class="preview" :style="{ background: `linear-gradient(140deg, ${accentFor(i)}30, rgba(20,20,32,0.40))` }">
            <div class="bars">
              <div class="bar accent" :style="{ background: accentFor(i) }"></div>
              <div class="bar"></div>
              <div class="bar"></div>
            </div>
          </div>
          <div>
            <div class="name">{{ t.name }}</div>
            <div class="meta">шаблон · {{ t.id.slice(-8) }}</div>
          </div>
        </router-link>
      </div>
      <div v-else class="empty-state">Шаблонов нет. Создайте новый, чтобы начать.</div>
    </section>

    <!-- Create dialog -->
    <div v-if="createOpen" class="modal-backdrop" @click.self="createOpen = false">
      <div class="modal">
        <div class="modal-head">
          <span>Новая презентация</span>
          <button class="tb-btn ghost icon" @click="createOpen = false">
            <AcIcon name="plus" :size="14" :stroke-width="2" style="transform: rotate(45deg);" />
          </button>
        </div>
        <div class="modal-body">
          <div class="inspector-row" style="margin:0;">
            <label>Название</label>
            <input type="text" v-model="createName" />
          </div>
          <div class="inspector-row" style="margin:0;">
            <label>{{ basisKind === 'layout' ? 'Макет' : 'Стиль' }}</label>
            <select v-if="basisKind === 'layout'" v-model="createTemplateId">
              <option :value="null" disabled>— выберите шаблон —</option>
              <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
            <select v-else v-model="stylePreset">
              <option v-for="style in styleOptions" :key="style" :value="style">{{ style }}</option>
            </select>
          </div>
        </div>
        <div class="modal-foot">
          <button class="tb-btn ghost" @click="createOpen = false">Отмена</button>
          <button class="tb-btn primary" :disabled="!canCreatePresentation" @click="createPresentation">
            <AcIcon name="plus" :size="13" /> Создать
          </button>
        </div>
      </div>
    </div>

    <!-- Outline approval dialog -->
    <div v-if="outlineOpen" class="modal-backdrop" @click.self="closeOutline">
      <div class="modal outline-modal">
        <div class="modal-head">
          <span>Оглавление презентации</span>
          <button class="tb-btn ghost icon" :disabled="generationLoading || buildingPresentation" @click="closeOutline">
            <AcIcon name="plus" :size="14" :stroke-width="2" style="transform: rotate(45deg);" />
          </button>
        </div>
        <div class="modal-body">
          <div v-if="generationError" class="generation-error modal-error">
            {{ generationError }}
          </div>
          <div v-if="outline" class="outline-summary">
            <h3>{{ outline.title }}</h3>
            <div class="outline-meta">
              <span v-if="outline.audience">{{ outline.audience }}</span>
              <span v-if="outline.goal">{{ outline.goal }}</span>
            </div>
          </div>
          <div v-if="outline?.slides?.length" class="outline-list">
            <div v-for="slide in outline.slides" :key="slide.order" class="outline-slide">
              <div class="outline-slide-number">{{ slide.order }}</div>
              <div class="outline-slide-content">
                <div class="outline-slide-title">{{ slide.title }}</div>
                <div v-if="slide.purpose" class="outline-slide-purpose">{{ slide.purpose }}</div>
                <ul v-if="slide.keyPoints?.length">
                  <li v-for="point in slide.keyPoints" :key="point">{{ point }}</li>
                </ul>
              </div>
            </div>
          </div>
          <textarea
            class="outline-feedback"
            v-model="outlineFeedback"
            rows="3"
            placeholder="Что изменить в структуре?"
          />
        </div>
        <div class="modal-foot">
          <button class="tb-btn ghost" :disabled="generationLoading || buildingPresentation" @click="closeOutline">
            Отмена
          </button>
          <button class="tb-btn" :disabled="!outlineFeedback.trim() || generationLoading || buildingPresentation" @click="retryOutline">
            <AcIcon name="redo" :size="13" /> Переделать
          </button>
          <button class="tb-btn primary" :disabled="generationLoading || buildingPresentation" @click="approveOutline">
            <AcIcon name="check" :size="13" /> {{ buildingPresentation ? 'Собираем…' : 'Собрать презентацию' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AcIcon from '../components/AcIcon.vue';
import SelectChip from '../components/SelectChip.vue';
import { api } from '../api/client.js';
import { makePresentation, makeSlide, makeTextElement, slideFromLayout } from '../core/factories.js';
import { uid } from '../core/ids.js';

const ACCENTS = ['#ffb547', '#5a8ff0', '#38d2a4', '#ef5d4a', '#a85a05', '#92b8ff'];
const STYLE_PRESETS = ['Деловой', 'Дружелюбный', 'Академичный', 'Рекламный'];
const STYLE_IDS = {
  Деловой: 'business',
  Дружелюбный: 'friendly',
  Академичный: 'academic',
  Рекламный: 'promo',
};
const STYLE_THEMES = {
  Деловой: {
    fonts: { heading: 'Inter', body: 'Inter' },
    colors: {
      background: '#0C1016',
      text: '#F4F5F7',
      primary: '#FFB547',
      secondary: '#5A8FF0',
      accent: '#38D2A4',
    },
  },
  Дружелюбный: {
    fonts: { heading: 'Inter', body: 'Inter' },
    colors: {
      background: '#F7F2EA',
      text: '#20242C',
      primary: '#2F80ED',
      secondary: '#F2994A',
      accent: '#27AE60',
    },
  },
  Академичный: {
    fonts: { heading: 'Inter', body: 'Inter' },
    colors: {
      background: '#F8FAFC',
      text: '#102033',
      primary: '#1D4ED8',
      secondary: '#475569',
      accent: '#0F766E',
    },
  },
  Рекламный: {
    fonts: { heading: 'Inter', body: 'Inter' },
    colors: {
      background: '#101014',
      text: '#FFFFFF',
      primary: '#EF5D4A',
      secondary: '#FFB547',
      accent: '#5A8FF0',
    },
  },
};

export default {
  name: 'HomeView',
  components: { AcIcon, SelectChip },
  data() {
    return {
      presentations: [],
      templates: [],
      createOpen: false,
      createName: '',
      createTemplateId: null,
      prompt: '',
      slideCount: 12,
      basisKind: 'layout',
      stylePreset: STYLE_PRESETS[0],
      composerTpl: null,
      generationId: null,
      outline: null,
      outlineOpen: false,
      outlineFeedback: '',
      generationLoading: false,
      buildingPresentation: false,
      generationError: '',
      attachedDocs: [],
      extractingDoc: false,
      importingTemplate: false,
      templateImportError: '',
      examples: [
        'Презентация для инвесторов: SaaS B2B, 10 слайдов, упор на трекшн',
        'Внутренний отчёт по итогам Q3 для команды product-маркетинга',
        'Курс по основам аналитики для джуниоров — 15 уроков-слайдов',
      ],
    };
  },
  computed: {
    templateOptionLabels() {
      return this.templates.map((t) => t.name);
    },
    styleOptions() {
      return STYLE_PRESETS;
    },
    selectedTemplateId() {
      return this.templates.find((t) => t.name === this.composerTpl)?.id || null;
    },
    selectedStyleId() {
      return STYLE_IDS[this.stylePreset] || 'business';
    },
    slideCountWord() {
      const n = this.slideCount;
      const last2 = n % 100;
      const last = n % 10;
      if (last2 >= 11 && last2 <= 14) return 'слайдов';
      if (last === 1) return 'слайд';
      if (last >= 2 && last <= 4) return 'слайда';
      return 'слайдов';
    },
    canGenerate() {
      if (!this.prompt.trim()) return false;
      if (this.basisKind === 'layout') {
        return Boolean(this.selectedTemplateId);
      }
      return Boolean(this.selectedStyleId);
    },
    canCreatePresentation() {
      return Boolean(this.createName) && (
        this.basisKind === 'style' || Boolean(this.createTemplateId)
      );
    },
  },
  beforeRouteEnter(_to, _from, next) {
    next((vm) => vm.loadHome());
  },
  async mounted() {
    await this.loadHome();
    window.addEventListener('focus', this.refresh);
  },
  activated() {
    this.loadHome();
  },
  beforeUnmount() {
    window.removeEventListener('focus', this.refresh);
  },
  methods: {
    async loadHome() {
      await this.refresh();
      if (!this.composerTpl && this.templates.length) {
        this.composerTpl = this.templates[0].name;
      }
    },
    async refresh() {
      [this.presentations, this.templates] = await Promise.all([
        api.listPresentations(),
        api.listTemplates(),
      ]);
    },
    accentFor(i) { return ACCENTS[i % ACCENTS.length]; },
    previewStyle(i) {
      const c = this.accentFor(i);
      return { background: `linear-gradient(135deg, ${c}28, ${c}08)` };
    },
    setSlideCount(value) {
      const n = Math.round(Number(value));
      if (!Number.isFinite(n)) return;
      this.slideCount = Math.max(1, Math.min(40, n));
    },
    setBasisKind(kind) {
      this.basisKind = kind;
      if (kind === 'layout') {
        if (!this.composerTpl && this.templates.length) {
          this.composerTpl = this.templates[0].name;
        }
      } else {
        this.composerTpl = null;
        if (!this.stylePreset) {
          this.stylePreset = STYLE_PRESETS[0];
        }
      }
    },
    setComposerTpl(name) {
      this.basisKind = 'layout';
      this.composerTpl = name;
    },
    setStylePreset(name) {
      this.basisKind = 'style';
      this.composerTpl = null;
      this.stylePreset = name;
    },
    themeForStyle(style) {
      return JSON.parse(JSON.stringify(STYLE_THEMES[style] || STYLE_THEMES[STYLE_PRESETS[0]]));
    },
    scrollTo(id) {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },
    openCreateDialog() {
      if (this.basisKind === 'layout' && !this.templates.length) {
        this.createTemplate();
        return;
      }
      this.createName = this.prompt
        ? this.prompt.split(/[.\n]/)[0].slice(0, 60)
        : 'Новая презентация';
      this.createTemplateId = this.basisKind === 'layout'
        ? this.templates.find((t) => t.name === this.composerTpl)?.id || this.templates[0].id
        : null;
      this.createOpen = true;
    },
    generationPayload() {
      const basis = this.basisKind === 'layout'
        ? { kind: 'layout', templateId: this.selectedTemplateId }
        : { kind: 'style', styleId: this.selectedStyleId };
      return {
        prompt: this.prompt.trim(),
        slideCount: this.slideCount,
        language: 'ru',
        basis,
      };
    },
    async generate() {
      if (!this.canGenerate || this.generationLoading) return;
      this.generationError = '';
      this.generationLoading = true;
      try {
        const response = await api.createGenerationOutline(this.generationPayload());
        this.generationId = response.generationId;
        this.outline = response.outline;
        this.outlineFeedback = '';
        this.outlineOpen = true;
      } catch (err) {
        this.generationError = this.apiErrorMessage(err, 'Не удалось получить оглавление.');
      } finally {
        this.generationLoading = false;
      }
    },
    async retryOutline() {
      if (!this.generationId || !this.outline || !this.outlineFeedback.trim()) return;
      this.generationError = '';
      this.generationLoading = true;
      try {
        const response = await api.retryGenerationOutline(this.generationId, {
          feedback: this.outlineFeedback.trim(),
          outline: this.outline,
        });
        this.outline = response.outline;
        this.outlineFeedback = '';
      } catch (err) {
        this.generationError = this.apiErrorMessage(err, 'Не удалось переделать оглавление.');
      } finally {
        this.generationLoading = false;
      }
    },
    async approveOutline() {
      if (!this.generationId || !this.outline || this.buildingPresentation) return;
      this.generationError = '';
      this.buildingPresentation = true;
      try {
        const saved = await api.buildGeneratedPresentation(this.generationId, {
          outline: this.outline,
          imagePolicy: { generateImages: true, imageType: 'png' },
        });
        this.presentations = [
          {
            id: saved.id,
            name: saved.name,
            templateId: saved.templateId,
            slideCount: saved.slides?.length || 0,
          },
          ...this.presentations.filter((p) => p.id !== saved.id),
        ];
        this.outlineOpen = false;
        this.$router.push(`/presentations/${saved.id}`);
      } catch (err) {
        this.generationError = this.apiErrorMessage(err, 'Не удалось собрать презентацию.');
      } finally {
        this.buildingPresentation = false;
      }
    },
    closeOutline() {
      if (this.generationLoading || this.buildingPresentation) return;
      this.outlineOpen = false;
    },
    apiErrorMessage(err, fallback) {
      const detail = err?.detail?.detail || err?.detail;
      if (typeof detail === 'string' && detail.trim()) return detail;
      if (detail && typeof detail === 'object') return JSON.stringify(detail);
      return fallback;
    },
    async createPresentation() {
      if (this.basisKind === 'style') {
        const theme = this.themeForStyle(this.stylePreset);
        const doc = makePresentation({
          name: this.createName,
          theme,
        });
        const firstSlide = makeSlide({
          slideType: 'title',
          name: 'Title',
          background: { type: 'color', value: theme.colors.background },
        });
        firstSlide.notes = this.prompt;
        firstSlide.elements.push(makeTextElement({
          role: 'title',
          text: this.createName,
          frame: {
            xEmu: 914400,
            yEmu: 914400,
            wEmu: 10363200,
            hEmu: 1400000,
            rotate: 0,
          },
          style: {
            fontFamily: theme.fonts.heading,
            fontSize: 40,
            fontWeight: 700,
            color: theme.colors.text,
            align: 'left',
            lineHeight: 1.1,
          },
        }));
        doc.slides.push(firstSlide);
        doc.meta = {
          generationDraft: {
            basis: { kind: 'style', style: this.stylePreset },
            prompt: this.prompt,
            slideCount: this.slideCount,
          },
        };
        const saved = await api.createPresentation(doc);
        this.presentations = [
          {
            id: saved.id,
            name: saved.name,
            templateId: saved.templateId,
            slideCount: saved.slides?.length || 0,
          },
          ...this.presentations.filter((p) => p.id !== saved.id),
        ];
        this.createOpen = false;
        this.$router.push(`/presentations/${saved.id}`);
        return;
      }

      const tpl = await api.getTemplate(this.createTemplateId);
      const doc = makePresentation({
        name: this.createName,
        templateId: tpl.id,
        theme: tpl.theme,
      });
      doc.slideSize = JSON.parse(JSON.stringify(tpl.slideSize));
      const titleLayout = tpl.layouts.find((l) => l.slideType === 'title') || tpl.layouts[0];
      if (titleLayout) doc.slides.push(slideFromLayout(titleLayout));
      if (this.prompt && doc.slides[0]) {
        doc.slides[0].notes = this.prompt;
      }
      const saved = await api.createPresentation(doc);
      this.presentations = [
        {
          id: saved.id,
          name: saved.name,
          templateId: saved.templateId,
          slideCount: saved.slides?.length || 0,
        },
        ...this.presentations.filter((p) => p.id !== saved.id),
      ];
      this.createOpen = false;
      this.$router.push(`/presentations/${saved.id}`);
    },
    async onDocUpload(e) {
      const file = e.target.files?.[0];
      e.target.value = '';
      if (!file) return;
      this.extractingDoc = true;
      this.generationError = '';
      try {
        const result = await api.extractDocumentText(file);
        const text = (result?.text || '').trim();
        if (!text) {
          this.generationError = 'В файле не нашлось текста.';
          return;
        }
        this.attachedDocs.push({
          fileName: result.fileName || file.name,
          length: result.length || text.length,
          text,
        });
        this.appendDocToPrompt(result.fileName || file.name, text);
      } catch (err) {
        this.generationError = this.apiErrorMessage(err, 'Не удалось прочитать файл.');
      } finally {
        this.extractingDoc = false;
      }
    },
    appendDocToPrompt(fileName, text) {
      const block = `\n\n--- Источник: ${fileName} ---\n${text}`;
      let next = (this.prompt || '') + block;
      if (next.length > 4000) {
        next = next.slice(0, 4000);
      }
      this.prompt = next;
    },
    removeAttachment(index) {
      const removed = this.attachedDocs[index];
      if (!removed) return;
      this.attachedDocs.splice(index, 1);
      const marker = `--- Источник: ${removed.fileName} ---`;
      const idx = this.prompt.indexOf(marker);
      if (idx < 0) return;
      let endIdx = this.prompt.indexOf('--- Источник:', idx + marker.length);
      if (endIdx < 0) endIdx = this.prompt.length;
      const before = this.prompt.slice(0, idx).replace(/\n+$/, '');
      const after = this.prompt.slice(endIdx);
      this.prompt = (before + (after ? '\n\n' + after : '')).trimEnd();
    },
    async onTemplatePptxUpload(e) {
      const file = e.target.files?.[0];
      e.target.value = '';
      if (!file) return;
      this.importingTemplate = true;
      this.templateImportError = '';
      try {
        const saved = await api.importTemplatePptx(file, file.name.replace(/\.pptx$/i, ''));
        this.templates = [
          { id: saved.id, name: saved.name, slideSize: saved.slideSize },
          ...this.templates.filter((t) => t.id !== saved.id),
        ];
        this.composerTpl = saved.name;
        this.$router.push(`/templates/${saved.id}`);
      } catch (err) {
        this.templateImportError = this.apiErrorMessage(err, 'Не удалось импортировать PPTX.');
      } finally {
        this.importingTemplate = false;
      }
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
          colors: {
            background: '#0C1016',
            text: '#F4F5F7',
            primary: '#FFB547',
            secondary: '#5A8FF0',
            accent: '#38D2A4',
          },
        },
        layouts: [
          {
            id: uid('layout'),
            name: 'Title',
            slideType: 'title',
            background: { type: 'color', value: '#0C1016' },
            elements: [],
          },
        ],
        assets: [],
      };
      const saved = await api.createTemplate(tpl);
      this.templates = [
        { id: saved.id, name: saved.name, slideSize: saved.slideSize },
        ...this.templates.filter((t) => t.id !== saved.id),
      ];
      if (!this.composerTpl) this.composerTpl = saved.name;
      this.$router.push(`/templates/${saved.id}`);
    },
  },
};
</script>
