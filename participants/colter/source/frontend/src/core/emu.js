export const SLIDE_W_EMU_DEFAULT = 12192000;
export const SLIDE_H_EMU_DEFAULT = 6858000;
export const EMU_PER_INCH = 914400;
export const EMU_PER_CM = EMU_PER_INCH / 2.54;
export const EMU_PER_PT = EMU_PER_INCH / 72;

export function emuToPx(valueEmu, scale) {
  return valueEmu * scale;
}

export function pxToEmu(valuePx, scale) {
  return Math.round(valuePx / scale);
}

export function getEditorScale(canvasWidthPx, slideWidthEmu) {
  return canvasWidthPx / slideWidthEmu;
}

export function emuToCm(valueEmu) {
  return valueEmu / EMU_PER_CM;
}

export function cmToEmu(valueCm) {
  return Math.round(valueCm * EMU_PER_CM);
}

export function emuToPt(valueEmu) {
  return valueEmu / EMU_PER_PT;
}

export function ptToEmu(valuePt) {
  return Math.round(valuePt * EMU_PER_PT);
}

export function roundNumber(value, digits = 2) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

export function fitScale(containerW, containerH, slideW, slideH, padding = 24) {
  const w = Math.max(120, containerW - padding * 2);
  const h = Math.max(80, containerH - padding * 2);
  return Math.min(w / slideW, h / slideH);
}
