/**
 * Parse a timestamp string from the backend as UTC time.
 *
 * The backend uses `datetime.now()` on a UTC server, producing strings like
 * "2026-03-29T12:54:52.087036" without a timezone marker. Without a 'Z' suffix,
 * JavaScript's `new Date()` treats them as local time, causing an 8-hour offset
 * in UTC+8 regions. This function ensures they are always parsed as UTC.
 */
export function parseUTCTime(timestamp: string): Date {
  if (!timestamp) return new Date();
  // Already has timezone info (Z, +HH:MM, -HH:MM)
  if (timestamp.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(timestamp)) {
    return new Date(timestamp);
  }
  return new Date(timestamp + 'Z');
}
