/**
 * Helper to parse a date string and get a Date object assuming Bogota timezone if no offset is present.
 */
export const parseBogotaDate = (dateStr: string): Date | null => {
  if (!dateStr) return null;
  try {
    let date: Date;
    if (dateStr.length === 10) {
      date = new Date(dateStr + 'T00:00:00-05:00');
    } else {
      const timePart = dateStr.split('T')[1] || '';
      const hasOffset = timePart.includes('Z') || timePart.includes('+') || timePart.includes('-');
      if (dateStr.includes('T') && !hasOffset) {
        date = new Date(dateStr + '-05:00');
      } else {
        date = new Date(dateStr);
      }
    }
    return isNaN(date.getTime()) ? null : date;
  } catch {
    return null;
  }
};

/**
 * Converts a Date object or ISO string to Bogota local YYYY-MM-DDTHH:mm format.
 */
export const toBogotaLocalDateTimeString = (dateInput: Date | string): string => {
  if (!dateInput) return '';
  const date = typeof dateInput === 'string' ? parseBogotaDate(dateInput) : dateInput;
  if (!date || isNaN(date.getTime())) return '';

  try {
    const bogotaMs = date.getTime() - 5 * 60 * 60 * 1000;
    const bogotaDate = new Date(bogotaMs);
    const year = bogotaDate.getUTCFullYear();
    const month = String(bogotaDate.getUTCMonth() + 1).padStart(2, '0');
    const day = String(bogotaDate.getUTCDate()).padStart(2, '0');
    const hours = String(bogotaDate.getUTCHours()).padStart(2, '0');
    const minutes = String(bogotaDate.getUTCMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  } catch {
    return '';
  }
};

/**
 * Normalizes input date to Bogota ISO format with offset.
 */
export const fromInputToBogotaIso = (value: string): string => {
  if (!value) return '';
  const timePart = value.split('T')[1] || '';
  const hasOffset = timePart.includes('Z') || timePart.includes('+') || timePart.includes('-');
  if (hasOffset) {
    return value;
  }
  if (value.includes(':') && value.split(':').length === 2) {
    return `${value}:00-05:00`;
  }
  return `${value}-05:00`;
};
