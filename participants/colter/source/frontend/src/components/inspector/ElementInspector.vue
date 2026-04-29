<template>
  <div>
    <div class="inspector-section">
      <h4>
        <span>Элемент</span>
        <span class="ac-pill" style="padding:2px 8px; font-size:10.5px;">{{ typeLabel }}</span>
      </h4>

      <div class="inspector-row">
        <label>Роль</label>
        <select :value="el.role || 'custom'" @change="(e) => setRole(e.target.value)">
          <option v-for="option in roleOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Поведение</label>
        <select :value="el.contentBehavior?.kind || 'manual'" @change="(e) => updateBehavior({ kind: e.target.value })">
          <option v-for="option in behaviorOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Свойства</label>
        <div class="toggle-row">
          <label class="check-chip">
            <input
              type="checkbox"
              :checked="!!el.contentBehavior?.readonly"
              @change="(e) => updateBehavior({ readonly: e.target.checked })"
            />
            <span>Только чтение</span>
          </label>
          <label class="check-chip">
            <input
              type="checkbox"
              :checked="!!el.locked"
              @change="(e) => updateProps({ locked: e.target.checked })"
            />
            <span>Зафиксировать</span>
          </label>
        </div>
      </div>
    </div>

    <div class="inspector-section">
      <h4>Положение и размер</h4>

      <div class="inspector-row">
        <label>X</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatCm(el.frame.xEmu)" @change="(e) => updateFrameMetric('xEmu', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeFrameMetric('xEmu', -0.1)" title="Уменьшить X"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeFrameMetric('xEmu', 0.1)" title="Увеличить X"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">см</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Y</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatCm(el.frame.yEmu)" @change="(e) => updateFrameMetric('yEmu', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeFrameMetric('yEmu', -0.1)" title="Уменьшить Y"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeFrameMetric('yEmu', 0.1)" title="Увеличить Y"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">см</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Ширина</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatCm(el.frame.wEmu)" @change="(e) => updateFrameMetric('wEmu', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeFrameMetric('wEmu', -0.1)" title="Уменьшить ширину"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeFrameMetric('wEmu', 0.1)" title="Увеличить ширину"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">см</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Высота</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatCm(el.frame.hEmu)" @change="(e) => updateFrameMetric('hEmu', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeFrameMetric('hEmu', -0.1)" title="Уменьшить высоту"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeFrameMetric('hEmu', 0.1)" title="Увеличить высоту"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">см</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Поворот</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatPlain(el.frame.rotate || 0, 1)" @change="(e) => updateRotation(e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeRotation(-1)" title="Повернуть меньше"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeRotation(1)" title="Повернуть больше"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">°</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Слой</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="numeric" :value="formatPlain(el.zIndex, 0)" @change="(e) => updateZIndex(e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeZIndex(-1)" title="Опустить слой"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeZIndex(1)" title="Поднять слой"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="el.type === 'text'" class="inspector-section">
      <h4>Текст</h4>
      <div class="inspector-row">
        <label>Содержимое</label>
        <textarea :value="el.text" rows="4" @input="(e) => updateText(e.target.value)" />
      </div>
      <div v-if="el.role === 'bulletList'" class="inspector-note">
        Каждая строка станет отдельным пунктом списка.
      </div>
      <div class="inspector-row">
        <label>Подсказка</label>
        <input type="text" :value="el.placeholder || ''" @input="(e) => updateProps({ placeholder: e.target.value })" />
      </div>
    </div>

    <div v-if="el.type === 'text'" class="inspector-section">
      <h4>Стиль текста</h4>

      <div class="inspector-row">
        <label>Шрифт</label>
        <select :value="el.style.fontFamily" @change="(e) => onFontChange(e.target.value)">
          <optgroup label="Без засечек">
            <option v-for="font in fontsByCategory('sans')" :key="font.name" :value="font.name">{{ font.name }}</option>
          </optgroup>
          <optgroup label="С засечками">
            <option v-for="font in fontsByCategory('serif')" :key="font.name" :value="font.name">{{ font.name }}</option>
          </optgroup>
          <optgroup label="Моноширинные">
            <option v-for="font in fontsByCategory('mono')" :key="font.name" :value="font.name">{{ font.name }}</option>
          </optgroup>
        </select>
      </div>

      <div class="inspector-row">
        <label>Размер</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatPlain(el.style.fontSize, 0)" @change="(e) => updateFontSize(e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeFontSize(-1)" title="Уменьшить шрифт"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeFontSize(1)" title="Увеличить шрифт"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">pt</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Насыщенность</label>
        <select :value="el.style.fontWeight || 400" @change="(e) => updateStyle({ fontWeight: +e.target.value })">
          <option v-for="weight in availableWeightOptions" :key="weight" :value="weight">{{ weightLabel(weight) }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Начертание</label>
        <div class="btn-group">
          <button type="button" :class="{ active: !!el.style.italic }" @click="updateStyle({ italic: !el.style.italic })" title="Курсив">
            <AcIcon name="italic" :size="13" />
          </button>
          <button type="button" :class="{ active: !!el.style.underline }" @click="updateStyle({ underline: !el.style.underline })" title="Подчеркнуть">
            <AcIcon name="underline" :size="13" />
          </button>
        </div>
      </div>

      <div class="inspector-row">
        <label>Цвет</label>
        <ColorChip :value="el.style.color || '#111111'" @change="(value) => updateStyle({ color: value })" />
      </div>

      <div class="inspector-row">
        <label>Горизонталь</label>
        <div class="btn-group">
          <button
            v-for="option in alignOptions"
            :key="option.value"
            type="button"
            :class="{ active: (el.style.align || 'left') === option.value }"
            :title="option.label"
            @click="updateStyle({ align: option.value })"
          >
            <AcIcon :name="option.icon" :size="13" />
          </button>
        </div>
      </div>

      <div class="inspector-row">
        <label>Вертикаль</label>
        <div class="btn-group">
          <button
            v-for="option in valignOptions"
            :key="option.value"
            type="button"
            :class="{ active: (el.style.valign || 'top') === option.value }"
            :title="option.label"
            @click="updateStyle({ valign: option.value })"
          >
            <AcIcon :name="option.icon" :size="13" />
          </button>
        </div>
      </div>

      <div class="inspector-row">
        <label>Интервал</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatPlain(el.style.lineHeight || 1.4, 1)" @change="(e) => updateLineHeight(e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeLineHeight(-0.1)" title="Уменьшить интервал"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeLineHeight(0.1)" title="Увеличить интервал"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="el.type === 'shape'" class="inspector-section">
      <h4>Фигура</h4>

      <div class="inspector-row">
        <label>Тип</label>
        <select :value="el.shape" @change="(e) => updateProps({ shape: e.target.value })">
          <option v-for="option in shapeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Заливка</label>
        <ColorChip :value="el.style.fill || '#FFFFFF'" @change="(value) => updateStyle({ fill: value })" />
      </div>

      <div class="inspector-row">
        <label>Контур</label>
        <ColorChip :value="el.style.stroke || '#111111'" @change="(value) => updateStyle({ stroke: value })" />
      </div>

      <div class="inspector-row">
        <label>Толщина</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatPt(el.style.strokeWidth || 0)" @change="(e) => updateStylePt('strokeWidth', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeStylePt('strokeWidth', -0.25)" title="Уменьшить толщину"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeStylePt('strokeWidth', 0.25)" title="Увеличить толщину"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">pt</span>
        </div>
      </div>

      <div v-if="el.shape === 'roundRect'" class="inspector-row">
        <label>Радиус</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatCm(el.style.radiusEmu || 0)" @change="(e) => updateStyleCm('radiusEmu', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeStyleCm('radiusEmu', -0.1)" title="Уменьшить радиус"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeStyleCm('radiusEmu', 0.1)" title="Увеличить радиус"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">см</span>
        </div>
      </div>
    </div>

    <div v-if="el.type === 'line'" class="inspector-section">
      <h4>Линия</h4>

      <div class="inspector-row">
        <label>Цвет</label>
        <ColorChip :value="el.style.color || '#111111'" @change="(value) => updateStyle({ color: value })" />
      </div>

      <div class="inspector-row">
        <label>Толщина</label>
        <div class="field-group">
          <div class="stepper-field">
            <input type="text" inputmode="decimal" :value="formatPt(el.style.widthEmu || 0)" @change="(e) => updateStylePt('widthEmu', e.target.value)" />
            <div class="stepper-buttons">
              <button type="button" @click="nudgeStylePt('widthEmu', -0.25)" title="Уменьшить толщину"><AcIcon name="minus" :size="11" /></button>
              <button type="button" @click="nudgeStylePt('widthEmu', 0.25)" title="Увеличить толщину"><AcIcon name="plus" :size="11" /></button>
            </div>
          </div>
          <span class="num-suffix">pt</span>
        </div>
      </div>

      <div class="inspector-row">
        <label>Стиль</label>
        <select :value="el.style.dash || 'solid'" @change="(e) => updateStyle({ dash: e.target.value })">
          <option v-for="option in lineStyleOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </div>
    </div>

    <div v-if="el.type === 'image'" class="inspector-section">
      <h4>Изображение</h4>

      <div class="inspector-row">
        <label>Подсказка</label>
        <input type="text" :value="el.placeholder || ''" @input="(e) => updateProps({ placeholder: e.target.value })" />
      </div>

      <div class="inspector-row">
        <label>Файл</label>
        <select :value="el.assetId || ''" @change="(e) => replaceImage(e.target.value)">
          <option value="">— не выбрано —</option>
          <option v-for="asset in imageAssets" :key="asset.id" :value="asset.id">{{ asset.fileName || asset.id }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Подгонка</label>
        <select :value="el.fit || 'cover'" @change="(e) => updateProps({ fit: e.target.value })">
          <option v-for="option in fitOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </div>

      <div class="inspector-row">
        <label>Пропорции</label>
        <label class="check-chip">
          <input type="checkbox" :checked="!!el.preserveAspect" @change="(e) => onPreserveAspect(e.target.checked)" />
          <span>Сохранять при ресайзе</span>
        </label>
      </div>

      <div class="inspector-row">
        <label>Загрузить</label>
        <input type="file" accept="image/*" @change="onUpload" />
      </div>
    </div>

    <div class="inspector-section">
      <h4>Ограничения</h4>

      <div class="inspector-row">
        <label>Символы</label>
        <input type="number" :value="el.constraints?.maxChars || ''" @input="(e) => updateConstraints({ maxChars: e.target.value === '' ? null : +e.target.value })" />
      </div>

      <div class="inspector-row">
        <label>Строки</label>
        <input type="number" :value="el.constraints?.maxLines || ''" @input="(e) => updateConstraints({ maxLines: e.target.value === '' ? null : +e.target.value })" />
      </div>

      <div class="inspector-row">
        <label>Переполнение</label>
        <select :value="el.constraints?.overflow || ''" @change="(e) => updateConstraints({ overflow: e.target.value || null })">
          <option value="">— не задано —</option>
          <option v-for="option in overflowOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
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
import { resolveTextRolePreset } from '../../core/textRoles.js';
import {
  cmToEmu,
  emuToCm,
  emuToPt,
  ptToEmu,
  roundNumber,
} from '../../core/emu.js';

const WEIGHT_LABELS = {
  100: 'Тонкий',
  200: 'Очень тонкий',
  300: 'Лёгкий',
  400: 'Обычный',
  500: 'Средний',
  600: 'Полужирный',
  700: 'Жирный',
  800: 'Очень жирный',
  900: 'Чёрный',
};

const ROLE_OPTIONS = [
  { value: 'title', label: 'Заголовок' },
  { value: 'subtitle', label: 'Подзаголовок' },
  { value: 'body', label: 'Основной текст' },
  { value: 'caption', label: 'Подпись' },
  { value: 'bulletList', label: 'Список' },
  { value: 'image', label: 'Изображение' },
  { value: 'logo', label: 'Логотип' },
  { value: 'footer', label: 'Подвал' },
  { value: 'slideNumber', label: 'Номер слайда' },
  { value: 'decorative', label: 'Декор' },
  { value: 'custom', label: 'Своя роль' },
];

const ROLE_OPTION_VALUES_BY_TYPE = {
  text: ['title', 'subtitle', 'body', 'caption', 'bulletList', 'footer', 'slideNumber', 'custom'],
  image: ['image', 'logo', 'decorative', 'custom'],
  shape: ['decorative', 'custom'],
  line: ['decorative', 'custom'],
  icon: ['logo', 'decorative', 'custom'],
  group: ['decorative', 'custom'],
};

const BEHAVIOR_OPTIONS = [
  { value: 'static', label: 'Фиксированный' },
  { value: 'placeholder', label: 'Заполнитель' },
  { value: 'generated', label: 'Сгенерированный' },
  { value: 'manual', label: 'Ручной' },
];

const FIT_OPTIONS = [
  { value: 'cover', label: 'Заполнить область' },
  { value: 'contain', label: 'Вписать целиком' },
  { value: 'stretch', label: 'Растянуть' },
];

const SHAPE_OPTIONS = [
  { value: 'rect', label: 'Прямоугольник' },
  { value: 'roundRect', label: 'Скруглённый прямоугольник' },
  { value: 'ellipse', label: 'Овал' },
  { value: 'triangle', label: 'Треугольник' },
];

const LINE_STYLE_OPTIONS = [
  { value: 'solid', label: 'Сплошная' },
  { value: 'dash', label: 'Пунктир' },
  { value: 'dot', label: 'Точки' },
];

const OVERFLOW_OPTIONS = [
  { value: 'clip', label: 'Обрезать' },
  { value: 'shrink', label: 'Уменьшать текст' },
  { value: 'ellipsis', label: 'Показывать многоточие' },
  { value: 'error', label: 'Считать ошибкой' },
];

const TYPE_LABELS = {
  text: 'Текст',
  image: 'Изображение',
  shape: 'Фигура',
  line: 'Линия',
  icon: 'Иконка',
  group: 'Группа',
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
      behaviorOptions: BEHAVIOR_OPTIONS,
      fitOptions: FIT_OPTIONS,
      shapeOptions: SHAPE_OPTIONS,
      lineStyleOptions: LINE_STYLE_OPTIONS,
      overflowOptions: OVERFLOW_OPTIONS,
      alignOptions: [
        { value: 'left', icon: 'alignLeft', label: 'Слева' },
        { value: 'center', icon: 'alignCenter', label: 'По центру' },
        { value: 'right', icon: 'alignRight', label: 'Справа' },
        { value: 'justify', icon: 'alignJustify', label: 'По ширине' },
      ],
      valignOptions: [
        { value: 'top', icon: 'alignTop', label: 'По верху' },
        { value: 'middle', icon: 'alignMiddle', label: 'По центру' },
        { value: 'bottom', icon: 'alignBottom', label: 'По низу' },
      ],
    };
  },
  computed: {
    docStore() { return useDocumentStore(); },
    el() { return this.element; },
    roleOptions() {
      const allowedValues = ROLE_OPTION_VALUES_BY_TYPE[this.el.type];
      const options = allowedValues
        ? ROLE_OPTIONS.filter((option) => allowedValues.includes(option.value))
        : ROLE_OPTIONS;
      if (!this.el.role || options.some((option) => option.value === this.el.role)) {
        return options;
      }
      const current = ROLE_OPTIONS.find((option) => option.value === this.el.role)
        || { value: this.el.role, label: this.el.role };
      return [current, ...options];
    },
    imageAssets() {
      return (this.docStore.doc?.assets || []).filter((asset) => asset.type === 'image');
    },
    availableWeightOptions() {
      const family = this.el.style?.fontFamily;
      const weights = availableWeights(family);
      return weights.length ? weights : [400];
    },
    typeLabel() {
      return TYPE_LABELS[this.el.type] || this.el.type;
    },
  },
  watch: {
    'element.style.fontFamily': {
      handler(fontFamily) { ensureFont(fontFamily); },
      immediate: true,
    },
  },
  methods: {
    fontsByCategory(category) {
      return FONT_FAMILIES.filter((font) => font.category === category);
    },
    weightLabel(weight) {
      return `${WEIGHT_LABELS[weight] || weight} (${weight})`;
    },
    formatPlain(value, digits = 2) {
      return String(roundNumber(Number(value) || 0, digits));
    },
    formatCm(valueEmu) {
      return this.formatPlain(emuToCm(valueEmu), 2);
    },
    formatPt(valueEmu) {
      return this.formatPlain(emuToPt(valueEmu), 2);
    },
    parseNumber(value) {
      if (value === '' || value == null) return null;
      const normalized = String(value).trim().replace(',', '.');
      if (!normalized) return null;
      const number = Number(normalized);
      return Number.isFinite(number) ? number : null;
    },
    setRole(role) {
      const props = { role };
      let stylePatch = null;
      if (this.el.type === 'text') {
        const preset = resolveTextRolePreset(role, this.docStore.doc?.theme);
        if (preset) {
          stylePatch = {
            fontFamily: preset.fontFamily,
            fontSize: preset.fontSize,
            fontWeight: preset.fontWeight,
            color: preset.color,
            lineHeight: preset.lineHeight,
          };
          if (!this.el.text) {
            props.placeholder = preset.placeholder;
          }
        }
      }
      if (stylePatch) {
        this.docStore.run({
          type: 'element.updateStyle',
          slideId: this.slide.id,
          elementId: this.el.id,
          payload: { style: stylePatch },
        });
        this.docStore.run({
          type: 'element.updateProps',
          slideId: this.slide.id,
          elementId: this.el.id,
          payload: { props },
        }, { coalesce: true });
        return;
      }
      this.updateProps(props);
    },
    onFontChange(family) {
      ensureFont(family);
      const supported = availableWeights(family);
      const current = this.el.style.fontWeight || 400;
      const nextWeight = supported.includes(current)
        ? current
        : (supported.includes(400) ? 400 : supported[0]);
      this.updateStyle({ fontFamily: family, fontWeight: nextWeight });
    },
    onPreserveAspect(value) {
      this.updateProps({ preserveAspect: value });
    },
    updateFrameMetric(key, value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      const emu = cmToEmu(number);
      if (key === 'wEmu') {
        this.updateSize('w', emu);
        return;
      }
      if (key === 'hEmu') {
        this.updateSize('h', emu);
        return;
      }
      this.updateFrame({ [key]: Math.round(emu) });
    },
    nudgeFrameMetric(key, deltaCm) {
      const current = emuToCm(this.el.frame[key] || 0);
      this.updateFrameMetric(key, roundNumber(current + deltaCm, 2));
    },
    updateRotation(value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      this.updateFrame({ rotate: roundNumber(number, 1) });
    },
    nudgeRotation(delta) {
      this.updateRotation((this.el.frame.rotate || 0) + delta);
    },
    updateZIndex(value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      this.updateProps({ zIndex: Math.round(number) });
    },
    nudgeZIndex(delta) {
      this.updateZIndex((this.el.zIndex || 0) + delta);
    },
    updateFontSize(value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      this.updateStyle({ fontSize: Math.max(6, Math.round(number)) });
    },
    nudgeFontSize(delta) {
      this.updateFontSize((this.el.style.fontSize || 24) + delta);
    },
    updateLineHeight(value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      this.updateStyle({ lineHeight: Math.max(0.6, roundNumber(number, 1)) });
    },
    nudgeLineHeight(delta) {
      this.updateLineHeight((this.el.style.lineHeight || 1.4) + delta);
    },
    updateStylePt(key, value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      this.updateStyle({ [key]: Math.max(0, ptToEmu(number)) });
    },
    nudgeStylePt(key, deltaPt) {
      const current = emuToPt(this.el.style[key] || 0);
      this.updateStylePt(key, roundNumber(current + deltaPt, 2));
    },
    updateStyleCm(key, value) {
      const number = this.parseNumber(value);
      if (number == null) return;
      this.updateStyle({ [key]: Math.max(0, cmToEmu(number)) });
    },
    nudgeStyleCm(key, deltaCm) {
      const current = emuToCm(this.el.style[key] || 0);
      this.updateStyleCm(key, roundNumber(current + deltaCm, 2));
    },
    updateSize(axis, valueEmu) {
      if (!Number.isFinite(valueEmu)) return;
      const min = axis === 'w' ? 100000 : 50000;
      const nextValue = Math.max(min, Math.round(valueEmu));
      const frame = { ...this.el.frame };
      if (this.el.type === 'image' && this.el.preserveAspect) {
        const ratio = (this.el.frame.wEmu || 1) / Math.max(1, this.el.frame.hEmu || 1);
        if (axis === 'w') {
          frame.wEmu = nextValue;
          frame.hEmu = Math.max(50000, Math.round(nextValue / ratio));
        } else {
          frame.hEmu = nextValue;
          frame.wEmu = Math.max(100000, Math.round(nextValue * ratio));
        }
      } else if (axis === 'w') {
        frame.wEmu = nextValue;
      } else {
        frame.hEmu = nextValue;
      }
      this.docStore.run({
        type: 'element.resize',
        slideId: this.slide.id,
        elementId: this.el.id,
        payload: { frame },
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
      Object.keys(next).forEach((key) => {
        if (next[key] == null) delete next[key];
      });
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
