export const SLIDE_W_EMU_DEFAULT = 12192000;
export const SLIDE_H_EMU_DEFAULT = 6858000;

export function emuToPx(valueEmu, scale) {
  return valueEmu * scale;
}

export function pxToEmu(valuePx, scale) {
  return Math.round(valuePx / scale);
}

export function getEditorScale(canvasWidthPx, slideWidthEmu) {
  return canvasWidthPx / slideWidthEmu;
}

export function fitScale(containerW, containerH, slideW, slideH, padding = 24) {
  const w = Math.max(120, containerW - padding * 2);
  const h = Math.max(80, containerH - padding * 2);
  return Math.min(w / slideW, h / slideH);
}
