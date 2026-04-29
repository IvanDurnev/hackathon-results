import { uid } from './ids.js';

export const DEFAULT_SLIDE_SIZE = {
  widthEmu: 12192000,
  heightEmu: 6858000,
  ratio: '16:9',
};

export const DEFAULT_THEME = {
  fonts: { heading: 'Inter', body: 'Inter' },
  colors: {
    background: '#FFFFFF',
    text: '#111827',
    primary: '#2563EB',
    secondary: '#64748B',
    accent: '#F97316',
  },
};

export function makeBackgroundColor(value = '#FFFFFF') {
  return { type: 'color', value };
}

export function makeFrame({ xEmu = 914400, yEmu = 914400, wEmu = 4000000, hEmu = 1200000 } = {}) {
  return { xEmu, yEmu, wEmu, hEmu, rotate: 0 };
}

export function makeBehavior(kind = 'manual', readonly = false, fillRole) {
  const b = { kind, readonly };
  if (fillRole) b.fillRole = fillRole;
  return b;
}

export function makeTextElement(overrides = {}) {
  return {
    id: uid('el'),
    type: 'text',
    role: overrides.role || 'body',
    contentBehavior: overrides.contentBehavior || makeBehavior('manual'),
    text: overrides.text ?? 'Двойной клик для редактирования',
    placeholder: overrides.placeholder,
    frame: overrides.frame || makeFrame({ wEmu: 6000000, hEmu: 800000 }),
    style: overrides.style || {
      fontFamily: 'Inter',
      fontSize: 24,
      fontWeight: 400,
      color: '#111827',
      align: 'left',
      valign: 'top',
      lineHeight: 1.4,
    },
    constraints: overrides.constraints,
    zIndex: overrides.zIndex ?? 10,
    locked: false,
    visible: true,
  };
}

export function makeImageElement(overrides = {}) {
  return {
    id: uid('el'),
    type: 'image',
    role: 'image',
    contentBehavior: overrides.contentBehavior || makeBehavior('manual'),
    assetId: overrides.assetId,
    placeholder: overrides.placeholder,
    fit: overrides.fit || 'cover',
    frame: overrides.frame || makeFrame({ wEmu: 5000000, hEmu: 3500000 }),
    zIndex: overrides.zIndex ?? 10,
    locked: false,
    visible: true,
  };
}

export function makeImagePlaceholderElement(overrides = {}) {
  const {
    placeholder = 'Изображение',
    contentBehavior = makeBehavior('placeholder', false, 'image'),
    ...rest
  } = overrides;
  return makeImageElement({
    ...rest,
    placeholder,
    contentBehavior,
  });
}

export function makeShapeElement(shape = 'rect', overrides = {}) {
  return {
    id: uid('el'),
    type: 'shape',
    role: 'decorative',
    shape,
    contentBehavior: overrides.contentBehavior || makeBehavior('manual'),
    frame: overrides.frame || makeFrame({ wEmu: 3000000, hEmu: 2000000 }),
    style: overrides.style || {
      fill: '#2563EB',
      stroke: '#1E40AF',
      strokeWidth: 9525,
      radiusEmu: shape === 'roundRect' ? 100000 : undefined,
    },
    zIndex: overrides.zIndex ?? 5,
    locked: false,
    visible: true,
  };
}

export function makeLineElement(overrides = {}) {
  return {
    id: uid('el'),
    type: 'line',
    role: 'decorative',
    contentBehavior: makeBehavior('manual'),
    frame: overrides.frame || makeFrame({ wEmu: 4000000, hEmu: 19050 }),
    style: { color: '#111827', widthEmu: 19050, dash: 'solid' },
    zIndex: 4,
    locked: false,
    visible: true,
  };
}

export function makeSlide({ slideType = 'text', layoutId, name, background } = {}) {
  return {
    id: uid('slide'),
    name: name || 'Новый слайд',
    slideType,
    layoutId,
    background: background || makeBackgroundColor('#FFFFFF'),
    elements: [],
    notes: '',
  };
}

/**
 * Build a slide from a layout. Placeholder elements are converted into
 * editable elements that keep `sourcePlaceholderId` and become `manual`.
 */
export function slideFromLayout(layout) {
  const elements = layout.elements.map((el) => {
    const copy = JSON.parse(JSON.stringify(el));
    copy.id = uid('el');
    if (el.contentBehavior?.kind === 'placeholder') {
      copy.sourcePlaceholderId = el.id;
      copy.contentBehavior = {
        kind: 'manual',
        readonly: false,
        fillRole: el.contentBehavior.fillRole,
      };
    }
    return copy;
  });
  return {
    id: uid('slide'),
    name: layout.name,
    slideType: layout.slideType,
    layoutId: layout.id,
    background: JSON.parse(JSON.stringify(layout.background)),
    elements,
    notes: '',
  };
}

export function makePresentation({ name = 'Новая презентация', templateId, theme } = {}) {
  return {
    schemaVersion: '1.0.0',
    documentType: 'presentation',
    id: uid('pres'),
    name,
    templateId,
    slideSize: { ...DEFAULT_SLIDE_SIZE },
    theme: theme ? JSON.parse(JSON.stringify(theme)) : JSON.parse(JSON.stringify(DEFAULT_THEME)),
    slides: [],
    assets: [],
  };
}

export function makeTemplate({ name = 'Новый шаблон', theme } = {}) {
  return {
    schemaVersion: '1.0.0',
    documentType: 'template',
    id: uid('tmpl'),
    name,
    slideSize: { ...DEFAULT_SLIDE_SIZE },
    theme: theme ? JSON.parse(JSON.stringify(theme)) : JSON.parse(JSON.stringify(DEFAULT_THEME)),
    layouts: [],
    assets: [],
  };
}
