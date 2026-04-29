export const TEXT_ROLE_PRESETS = {
  title: {
    fontFamilyKey: 'heading',
    fontSize: 40,
    fontWeight: 700,
    lineHeight: 1.1,
    colorKey: 'text',
    placeholder: 'Заголовок',
  },
  subtitle: {
    fontFamilyKey: 'body',
    fontSize: 28,
    fontWeight: 400,
    lineHeight: 1.2,
    colorKey: 'secondary',
    placeholder: 'Подзаголовок',
  },
  body: {
    fontFamilyKey: 'body',
    fontSize: 22,
    fontWeight: 400,
    lineHeight: 1.5,
    colorKey: 'text',
    placeholder: 'Текст слайда',
  },
  caption: {
    fontFamilyKey: 'body',
    fontSize: 16,
    fontWeight: 400,
    lineHeight: 1.35,
    colorKey: 'secondary',
    placeholder: 'Подпись',
  },
  bulletList: {
    fontFamilyKey: 'body',
    fontSize: 24,
    fontWeight: 400,
    lineHeight: 1.6,
    colorKey: 'text',
    placeholder: 'Пункт 1\nПункт 2\nПункт 3',
  },
  footer: {
    fontFamilyKey: 'body',
    fontSize: 14,
    fontWeight: 400,
    lineHeight: 1.2,
    colorKey: 'secondary',
    placeholder: 'Подвал',
  },
  slideNumber: {
    fontFamilyKey: 'body',
    fontSize: 12,
    fontWeight: 500,
    lineHeight: 1,
    colorKey: 'secondary',
    placeholder: '1',
  },
};

export function resolveTextRolePreset(role, theme) {
  const preset = TEXT_ROLE_PRESETS[role];
  if (!preset) return null;
  return {
    fontFamily: theme?.fonts?.[preset.fontFamilyKey] || 'Inter',
    fontSize: preset.fontSize,
    fontWeight: preset.fontWeight,
    lineHeight: preset.lineHeight,
    color: theme?.colors?.[preset.colorKey] || '#111827',
    placeholder: preset.placeholder,
  };
}
