<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    v-html="path"
  />
</template>

<script>
const PATHS = {
  sparkle: '<path d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6L12 3z"/><path d="M19 15l.7 1.8L21.5 17.5l-1.8.7L19 20l-.7-1.8-1.8-.7 1.8-.7L19 15z"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  home: '<path d="M3 11l9-7 9 7v9a2 2 0 01-2 2h-4v-7H10v7H6a2 2 0 01-2-2v-9z"/>',
  save: '<path d="M5 4h11l3 3v13a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1zM7 4v5h8V4M8 14h8"/>',
  download: '<path d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16"/>',
  undo: '<path d="M9 14L4 9l5-5M4 9h11a5 5 0 010 10H8"/>',
  redo: '<path d="M15 14l5-5-5-5M20 9H9a5 5 0 000 10h7"/>',
  text: '<path d="M5 5h14"/><path d="M12 5v14"/><path d="M9 19h6"/>',
  image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M3 17l5-4 4 3 3-2 6 5"/>',
  shape: '<rect x="4" y="4" width="16" height="16" rx="2"/>',
  line: '<path d="M4 18L20 6"/>',
  layers: '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
  grid: '<rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/><rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/>',
  zoomIn: '<circle cx="10" cy="10" r="6"/><path d="M10 7v6M7 10h6M20 20l-5-5"/>',
  zoomOut: '<circle cx="10" cy="10" r="6"/><path d="M7 10h6M20 20l-5-5"/>',
  play: '<path d="M6 4l14 8-14 8V4z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>',
  duplicate: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 00-2-2H6a2 2 0 00-2 2v8a2 2 0 002 2h2"/>',
  trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13a1 1 0 001 1h8a1 1 0 001-1l1-13"/>',
  bold: '<path d="M7 5h6a3.5 3.5 0 010 7H7zm0 7h7a3.5 3.5 0 010 7H7z"/>',
  italic: '<path d="M14 5h-4M14 19h-4M15 5l-4 14"/>',
  underline: '<path d="M6 4v8a6 6 0 0012 0V4"/><path d="M5 20h14"/>',
  upload: '<path d="M12 16V4m0 0l-4 4m4-4l4 4M4 20h16"/>',
  eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  eyeOff: '<path d="M2 12s4-7 10-7c2 0 3.6.5 5 1.3M22 12s-4 7-10 7c-2 0-3.6-.5-5-1.3"/><path d="M3 3l18 18"/>',
  lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>',
  unlock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 017.5-2"/>',
  check: '<path d="M5 12l5 5L20 7"/>',
  chevronRight: '<path d="M9 6l6 6-6 6"/>',
  chevronDown: '<path d="M6 9l6 6 6-6"/>',
  align: '<path d="M3 6h18M3 12h12M3 18h18"/>',
  alignLeft: '<path d="M3 6h18M3 12h10M3 18h14"/>',
  alignCenter: '<path d="M3 6h18M6 12h12M5 18h14"/>',
  alignRight: '<path d="M3 6h18M11 12h10M7 18h14"/>',
  alignJustify: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  alignTop: '<path d="M4 4h16M12 8v12M8 12l4-4 4 4"/>',
  alignMiddle: '<path d="M4 12h16M12 4v6M12 14v6M9 7l3-3 3 3M9 17l3 3 3-3"/>',
  alignBottom: '<path d="M4 20h16M12 4v12M8 12l4 4 4-4"/>',
  palette: '<circle cx="12" cy="12" r="9"/><circle cx="7.5" cy="10.5" r="1.2" fill="currentColor"/><circle cx="12" cy="7.5" r="1.2" fill="currentColor"/><circle cx="16.5" cy="10.5" r="1.2" fill="currentColor"/><path d="M12 21a3 3 0 003-3 2 2 0 012-2h1.5a2.5 2.5 0 002.5-2.5"/>',
  bell: '<path d="M6 8a6 6 0 0112 0c0 7 3 9 3 9H3s3-2 3-9z"/><path d="M10 21a2 2 0 004 0"/>',
  arrowRight: '<path d="M5 12h14M12 5l7 7-7 7"/>',
  triangle: '<path d="M12 4l9 16H3z"/>',
  ellipse: '<ellipse cx="12" cy="12" rx="9" ry="6"/>',
  rect: '<rect x="3" y="6" width="18" height="12" rx="2"/>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15V4a1 1 0 011-1h11"/>',
  link: '<path d="M10 14a5 5 0 010-7l3-3a5 5 0 017 7l-1 1"/><path d="M14 10a5 5 0 010 7l-3 3a5 5 0 01-7-7l1-1"/>',
  type: '<path d="M5 7V5h14v2M9 5v14M9 19h6"/>',
  hash: '<path d="M4 9h16M4 15h16M10 4l-4 16M18 4l-4 16"/>',
};

export default {
  name: 'AcIcon',
  props: {
    name: { type: String, required: true },
    size: { type: [Number, String], default: 16 },
    strokeWidth: { type: [Number, String], default: 1.6 },
  },
  computed: {
    path() {
      return PATHS[this.name] || '';
    },
  },
};
</script>
