/**
 * Утилита для объединения классов
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}
