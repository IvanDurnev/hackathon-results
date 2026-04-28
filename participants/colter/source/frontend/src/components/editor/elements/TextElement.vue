<template>
  <div
    ref="root"
    :style="textStyle"
    :class="['text-content', { 'text-editing': editing }]"
    :contenteditable="editing"
    @dblclick.stop="onDblClick"
    @input="onInput"
    @blur="onBlur"
    @mousedown="onMouseDown"
    @keydown.stop
    spellcheck="false"
    v-html="display"
  />
</template>

<script>
export default {
  name: 'TextElementView',
  props: {
    element: { type: Object, required: true },
    scale: { type: Number, required: true },
    readonly: { type: Boolean, default: false },
    editing: { type: Boolean, default: false },
  },
  emits: ['start-edit', 'commit-text', 'select'],
  computed: {
    display() {
      const text = this.element.text;
      if (text && text.length > 0) {
        return this.escape(text).replace(/\n/g, '<br>');
      }
      if (this.editing) return '';
      const ph = this.element.placeholder || 'Текст';
      return `<span class="placeholder">${this.escape(ph)}</span>`;
    },
    textStyle() {
      const s = this.element.style || {};
      const f = this.element.frame;
      // Font size in EMU? Spec keeps it in pt; pt → px ≈ pt * 96/72
      // We scale visually with editor scale: pt -> px(in slide) = pt * (slidePx / slidePt)
      // Simpler: font-size in CSS px = pt * 96/72 * (scale * SLIDE_W_EMU / SLIDE_W_PX_AT_SCALE_1)
      // Since 1 EMU at scale 1 == 1 CSS px, and 914400 EMU == 1 inch, 1 pt = 12700 EMU.
      // So fontSize(px) = pt * 12700 * scale.
      const fontPx = (s.fontSize || 16) * 12700 * this.scale;
      return {
        fontFamily: s.fontFamily || 'Inter',
        fontWeight: s.fontWeight || 400,
        fontStyle: s.italic ? 'italic' : 'normal',
        textDecoration: s.underline ? 'underline' : 'none',
        color: s.color || '#111827',
        textAlign: s.align || 'left',
        lineHeight: s.lineHeight || 1.4,
        fontSize: `${fontPx}px`,
        padding: '4px',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        cursor: this.editing ? 'text' : 'move',
      };
    },
  },
  methods: {
    escape(s) {
      return String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    },
    onMouseDown(e) {
      this.$emit('select', e);
    },
    onDblClick() {
      if (this.readonly) return;
      this.$emit('start-edit');
      this.$nextTick(() => {
        const el = this.$refs.root;
        if (!el) return;
        el.focus();
        // place cursor at end
        const range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      });
    },
    onInput() {
      // Pull plain text out of the contenteditable, preserving line breaks.
      const el = this.$refs.root;
      const text = this.htmlToText(el.innerHTML);
      this.$emit('commit-text', { text, coalesce: true });
    },
    onBlur() {
      if (!this.editing) return;
      const el = this.$refs.root;
      const text = el ? this.htmlToText(el.innerHTML) : this.element.text;
      this.$emit('commit-text', { text, finalize: true });
    },
    htmlToText(html) {
      return html
        .replace(/<div>/gi, '\n')
        .replace(/<\/div>/gi, '')
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<[^>]+>/g, '')
        .replace(/&nbsp;/g, ' ')
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>');
    },
  },
};
</script>
