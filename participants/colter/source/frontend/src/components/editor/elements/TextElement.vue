<template>
  <div
    v-if="!editing"
    :style="textStyle"
    class="text-content"
    @dblclick.stop="onDblClick"
    @mousedown="onMouseDown"
    v-html="display"
  />
  <div
    v-else
    ref="root"
    :style="textStyle"
    class="text-content text-editing"
    contenteditable="true"
    spellcheck="false"
    @input="onInput"
    @blur="onBlur"
    @mousedown="onMouseDown"
    @keydown.stop
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
      const ph = this.element.placeholder || 'Текст';
      return `<span class="placeholder">${this.escape(ph)}</span>`;
    },
    textStyle() {
      const s = this.element.style || {};
      const fontPx = (s.fontSize || 16) * 12700 * this.scale;
      const valignMap = { top: 'flex-start', middle: 'center', bottom: 'flex-end' };
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
        cursor: this.readonly ? 'default' : (this.editing ? 'text' : 'move'),
        display: 'flex',
        flexDirection: 'column',
        justifyContent: valignMap[s.valign || 'top'] || 'flex-start',
      };
    },
  },
  watch: {
    editing(val) {
      if (!val) return;
      this.$nextTick(() => this.initEditor());
    },
  },
  mounted() {
    if (this.editing) this.initEditor();
  },
  methods: {
    initEditor() {
      const el = this.$refs.root;
      if (!el) return;
      // Seed contenteditable with the current text. Using innerText so the browser
      // does not inject leading <div> wrappers that would later round-trip into a
      // leading "\n" (one of the reported bugs). innerText preserves \n via <br>.
      el.innerText = this.element.text || '';
      el.focus();
      // Place caret at end so subsequent typing appends rather than reverses.
      const range = document.createRange();
      range.selectNodeContents(el);
      range.collapse(false);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    },
    escape(s) {
      return String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    },
    onMouseDown(e) {
      this.$emit('select', e);
    },
    onDblClick() {
      if (this.readonly) return;
      this.$emit('start-edit');
    },
    onInput() {
      const el = this.$refs.root;
      if (!el) return;
      const text = (el.innerText || '').replace(/ /g, ' ');
      this.$emit('commit-text', { text, coalesce: true });
    },
    onBlur() {
      if (!this.editing) return;
      const el = this.$refs.root;
      const text = el ? (el.innerText || '').replace(/ /g, ' ') : (this.element.text || '');
      this.$emit('commit-text', { text, finalize: true });
    },
  },
};
</script>
