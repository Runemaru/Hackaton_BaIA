export function percentage(value) {
  if (value === undefined || value === null) return "0%";
  return `${Number(value).toFixed(1)}%`;
}

export function formatDate(value) {
  if (!value) return "-";
  return value;
}
