/**
 * Command applier. All mutations go through here so undo/redo and history work.
 *
 * Each `apply` returns a deep-merged change object that we keep on the history
 * stack via JSON snapshots taken outside this module.
 */

function findSlide(doc, slideId) {
  return doc.slides.find((s) => s.id === slideId);
}

function findElement(slide, elementId) {
  return slide?.elements.find((e) => e.id === elementId);
}

export function applyCommand(doc, cmd) {
  switch (cmd.type) {
    case 'element.move': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el) return;
      el.frame.xEmu = cmd.payload.xEmu;
      el.frame.yEmu = cmd.payload.yEmu;
      return;
    }
    case 'element.resize': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el) return;
      el.frame = { ...el.frame, ...cmd.payload.frame };
      return;
    }
    case 'element.updateText': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el || el.type !== 'text') return;
      el.text = cmd.payload.text;
      return;
    }
    case 'element.updateStyle': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el || !el.style) return;
      el.style = { ...el.style, ...cmd.payload.style };
      return;
    }
    case 'element.updateProps': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el) return;
      Object.assign(el, cmd.payload.props);
      return;
    }
    case 'element.updateBehavior': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el) return;
      el.contentBehavior = { ...el.contentBehavior, ...cmd.payload.contentBehavior };
      return;
    }
    case 'element.delete': {
      const slide = findSlide(doc, cmd.slideId);
      if (!slide) return;
      slide.elements = slide.elements.filter((e) => e.id !== cmd.elementId);
      return;
    }
    case 'element.add': {
      const slide = findSlide(doc, cmd.slideId);
      if (!slide) return;
      slide.elements.push(cmd.payload.element);
      return;
    }
    case 'element.reorderZ': {
      const slide = findSlide(doc, cmd.slideId);
      const el = findElement(slide, cmd.elementId);
      if (!el) return;
      el.zIndex = cmd.payload.zIndex;
      return;
    }
    case 'slide.add': {
      const idx = typeof cmd.payload.index === 'number' ? cmd.payload.index : doc.slides.length;
      doc.slides.splice(idx, 0, cmd.payload.slide);
      return;
    }
    case 'slide.delete': {
      doc.slides = doc.slides.filter((s) => s.id !== cmd.slideId);
      return;
    }
    case 'slide.reorder': {
      const { fromIndex, toIndex } = cmd.payload;
      const [moved] = doc.slides.splice(fromIndex, 1);
      doc.slides.splice(toIndex, 0, moved);
      return;
    }
    case 'slide.update': {
      const slide = findSlide(doc, cmd.slideId);
      if (!slide) return;
      Object.assign(slide, cmd.payload.props);
      return;
    }
    case 'image.replace': {
      const el = findElement(findSlide(doc, cmd.slideId), cmd.elementId);
      if (!el || el.type !== 'image') return;
      el.assetId = cmd.payload.assetId;
      return;
    }
    case 'doc.replaceAssets': {
      doc.assets = cmd.payload.assets;
      return;
    }
    case 'doc.update': {
      Object.assign(doc, cmd.payload.props);
      return;
    }
    default:
      // unknown command — ignore
      return;
  }
}

export function clone(doc) {
  return JSON.parse(JSON.stringify(doc));
}
