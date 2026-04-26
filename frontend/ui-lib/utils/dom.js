export function parseBooleanAttr(value, fallback = false) {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }

  return ['1', 'true', 'yes', 'on'].includes(String(value).toLowerCase());
}

export function parseNumberAttr(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  if (Number.isNaN(parsed)) {
    return fallback;
  }

  return parsed;
}

export function isEventOutside(event, container) {
  if (!container) {
    return true;
  }

  const eventTarget = event.target;
  return !(eventTarget instanceof Node) || !container.contains(eventTarget);
}
