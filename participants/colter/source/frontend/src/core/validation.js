/**
 * Light client-side validation that mirrors the backend.
 * Used for non-blocking warnings on the canvas and inspector.
 */

export function textOverflowIssues(el) {
  if (el.type !== 'text' || !el.constraints) return null;
  const c = el.constraints;
  const text = el.text || '';
  if (c.maxChars && text.length > c.maxChars) {
    return {
      code: 'text.overflow.chars',
      message: `${text.length}/${c.maxChars} символов`,
    };
  }
  const lines = text.split('\n').length;
  if (c.maxLines && lines > c.maxLines) {
    return {
      code: 'text.overflow.lines',
      message: `${lines}/${c.maxLines} строк`,
    };
  }
  return null;
}
