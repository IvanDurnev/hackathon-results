/**
 * Curated list of editor fonts and a small Google Fonts loader.
 *
 * The loader injects a single <link> per (family + axes) combination so a chosen
 * font weight actually renders correctly — addresses the feedback that picking
 * weights for a font that was never loaded with that weight had no visible
 * effect.
 */

export const FONT_FAMILIES = [
  { name: 'Inter', google: 'Inter', weights: [300, 400, 500, 600, 700, 800], category: 'sans' },
  { name: 'Roboto', google: 'Roboto', weights: [300, 400, 500, 700, 900], category: 'sans' },
  { name: 'Open Sans', google: 'Open Sans', weights: [400, 500, 600, 700, 800], category: 'sans' },
  { name: 'Montserrat', google: 'Montserrat', weights: [300, 400, 500, 600, 700, 800], category: 'sans' },
  { name: 'Lato', google: 'Lato', weights: [300, 400, 700, 900], category: 'sans' },
  { name: 'Nunito', google: 'Nunito', weights: [300, 400, 600, 700, 800], category: 'sans' },
  { name: 'IBM Plex Sans', google: 'IBM Plex Sans', weights: [300, 400, 500, 600, 700], category: 'sans' },
  { name: 'Manrope', google: 'Manrope', weights: [300, 400, 500, 600, 700, 800], category: 'sans' },
  { name: 'Playfair Display', google: 'Playfair Display', weights: [400, 500, 600, 700, 800], category: 'serif' },
  { name: 'Merriweather', google: 'Merriweather', weights: [300, 400, 700, 900], category: 'serif' },
  { name: 'Instrument Serif', google: 'Instrument Serif', weights: [400], category: 'serif' },
  { name: 'JetBrains Mono', google: 'JetBrains Mono', weights: [400, 500, 600, 700], category: 'mono' },
  { name: 'Source Code Pro', google: 'Source Code Pro', weights: [300, 400, 500, 600, 700], category: 'mono' },
];

const loaded = new Set();

export function ensureFont(family) {
  if (!family || loaded.has(family)) return;
  const meta = FONT_FAMILIES.find((f) => f.name === family);
  if (!meta || !meta.google) {
    loaded.add(family);
    return;
  }
  const weights = meta.weights.join(';');
  const href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(meta.google).replace(/%20/g, '+')}:wght@${weights}&display=swap`;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = href;
  document.head.appendChild(link);
  loaded.add(family);
}

export function familyMeta(name) {
  return FONT_FAMILIES.find((f) => f.name === name);
}

export function availableWeights(name) {
  return familyMeta(name)?.weights || [400];
}
