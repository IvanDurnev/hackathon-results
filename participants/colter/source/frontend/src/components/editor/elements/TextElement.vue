<template>
  <div
    v-if="!editing"
    ref="displayRoot"
    :style="textStyle"
    class="text-content"
    @dblclick.stop="onDblClick"
    @mousedown="onMouseDown"
  >
    <div ref="measureRoot" class="text-flow" v-html="display" />
  </div>
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
  data() {
    return {
      fittedFontScale: 1,
      fitRaf: 0,
      resizeObserver: null,
    };
  },
  computed: {
    isBulletList() {
      return this.element.role === 'bulletList';
    },
    display() {
      const text = this.element.text;
      if (text && text.length > 0) {
        return this.isBulletList
          ? this.renderBulletHtml(text)
          : this.escape(text).replace(/\n/g, '<br>');
      }
      const placeholder = this.element.placeholder
        || (this.isBulletList ? 'Пункт 1\nПункт 2\nПункт 3' : 'Текст');
      return this.isBulletList
        ? this.renderBulletHtml(placeholder, true)
        : `<span class="placeholder">${this.escape(placeholder)}</span>`;
    },
    textStyle() {
      const s = this.element.style || {};
      const fontPx = this.baseFontPx * (this.editing ? 1 : this.fittedFontScale);
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
        overflowWrap: 'anywhere',
        cursor: this.readonly ? 'default' : (this.editing ? 'text' : 'move'),
        display: 'flex',
        flexDirection: 'column',
        justifyContent: valignMap[s.valign || 'top'] || 'flex-start',
      };
    },
    baseFontPx() {
      const s = this.element.style || {};
      return (s.fontSize || 16) * 12700 * this.scale;
    },
    minFontPx() {
      const c = this.element.constraints || {};
      const byRole = {
        title: 14,
        subtitle: 12,
        body: 11,
        bulletList: 11,
        caption: 9,
      };
      const minPt = c.minFontSize || byRole[this.element.role] || 10;
      return minPt * 12700 * this.scale;
    },
    shouldAutoFit() {
      const c = this.element.constraints || {};
      return c.overflow === 'shrink' || this.element.contentBehavior?.kind === 'generated';
    },
  },
  watch: {
    editing(val) {
      if (val) {
        this.fittedFontScale = 1;
        this.$nextTick(() => this.initEditor());
        return;
      }
      this.$nextTick(() => {
        this.observeDisplay();
        this.scheduleFit(true);
      });
    },
    element: {
      handler() {
        this.scheduleFit(true);
      },
      deep: true,
    },
    scale() {
      this.scheduleFit(true);
    },
  },
  mounted() {
    if (this.editing) this.initEditor();
    this.$nextTick(() => {
      this.observeDisplay();
      this.scheduleFit(true);
    });
  },
  updated() {
    this.$nextTick(() => {
      this.observeDisplay();
      this.scheduleFit();
    });
  },
  beforeUnmount() {
    if (this.fitRaf) cancelAnimationFrame(this.fitRaf);
    if (this.resizeObserver) this.resizeObserver.disconnect();
  },
  methods: {
    observeDisplay() {
      if (this.editing) return;
      const el = this.$refs.displayRoot;
      if (!el || !window.ResizeObserver) return;
      if (this.resizeObserver?.target === el) return;
      if (this.resizeObserver) this.resizeObserver.disconnect();
      const observer = new ResizeObserver(() => this.scheduleFit(true));
      observer.observe(el);
      observer.target = el;
      this.resizeObserver = observer;
    },
    scheduleFit(reset = false) {
      if (reset && this.fittedFontScale !== 1) {
        this.fittedFontScale = 1;
      }
      if (this.editing || !this.shouldAutoFit) {
        if (this.fittedFontScale !== 1) this.fittedFontScale = 1;
        return;
      }
      if (this.fitRaf) cancelAnimationFrame(this.fitRaf);
      this.fitRaf = requestAnimationFrame(() => {
        this.fitRaf = 0;
        this.fitText();
      });
    },
    fitText() {
      const root = this.$refs.displayRoot;
      const inner = this.$refs.measureRoot;
      if (!root || !inner || !this.shouldAutoFit) return;

      const clientW = Math.max(1, root.clientWidth);
      const clientH = Math.max(1, root.clientHeight);
      const overflowX = inner.scrollWidth > clientW + 1;
      const overflowY = inner.scrollHeight > clientH + 1;
      if (!overflowX && !overflowY) return;

      const minScale = Math.min(1, this.minFontPx / Math.max(1, this.baseFontPx));
      const xScale = clientW / Math.max(1, inner.scrollWidth);
      const yScale = clientH / Math.max(1, inner.scrollHeight);
      const next = Math.max(
        minScale,
        Math.min(this.fittedFontScale, this.fittedFontScale * Math.min(xScale, yScale) * 0.97),
      );

      if (next < this.fittedFontScale - 0.01) {
        this.fittedFontScale = Number(next.toFixed(3));
        this.$nextTick(() => this.scheduleFit());
      }
    },
    bulletLines(text) {
      return String(text)
        .split('\n')
        .map((line) => line.replace(/^[\s\u2022*-]+\s*/, '').trim())
        .filter(Boolean);
    },
    renderBulletHtml(text, placeholder = false) {
      const lines = this.bulletLines(text);
      if (!lines.length) {
        return placeholder
          ? '<ul class="bullet-list"><li><span class="placeholder">Пункт списка</span></li></ul>'
          : '';
      }
      const items = lines.map((line) => {
        const content = this.escape(line);
        return placeholder
          ? `<li><span class="placeholder">${content}</span></li>`
          : `<li>${content}</li>`;
      }).join('');
      return `<ul class="bullet-list">${items}</ul>`;
    },
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
      const text = (el.innerText || '').replace(/\u00a0/g, ' ');
      this.$emit('commit-text', { text, coalesce: true });
    },
    onBlur() {
      if (!this.editing) return;
      const el = this.$refs.root;
      const text = el ? (el.innerText || '').replace(/\u00a0/g, ' ') : (this.element.text || '');
      this.$emit('commit-text', { text, finalize: true });
    },
  },
};
</script>

<style scoped>
.text-flow {
  min-width: 0;
  width: 100%;
}
</style>
