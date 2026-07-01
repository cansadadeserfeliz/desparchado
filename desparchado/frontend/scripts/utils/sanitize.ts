const ALLOWED_TAGS: Record<string, Set<string>> = {
  p: new Set(),
  a: new Set(['href', 'target', 'rel']),
  strong: new Set(),
  ul: new Set(),
  ol: new Set(),
  li: new Set(),
  i: new Set(),
  u: new Set(),
  em: new Set(),
  div: new Set(),
  span: new Set(),
  br: new Set(),
};

/**
 * Removes all whitespace and control characters from an attribute value
 * to prevent scheme bypasses like "java\nscript:".
 */
function cleanUrlValue(val: string): string {
  return val
    .split('')
    .filter((char) => {
      const code = char.charCodeAt(0);
      // Remove control characters (0-31, 127-159)
      if (code <= 31 || (code >= 127 && code <= 159)) {
        return false;
      }
      // Remove whitespace characters (spaces, tabs, newlines, etc.)
      return !/\s/.test(char);
    })
    .join('');
}

/**
 * Validates whether a scheme prefix conforms to RFC 3986 and
 * is part of our positive scheme allowlist.
 */
function isValidScheme(scheme: string): boolean {
  // RFC 3986 scheme: [a-zA-Z][a-zA-Z0-9+.-]*
  if (!/^[a-z][a-z0-9+\-.]*$/.test(scheme)) {
    return true; // Not a valid scheme format, treat as relative or safe url part
  }
  return scheme === 'http' || scheme === 'https' || scheme === 'mailto' || scheme === 'tel';
}

/**
 * Checks if a URL-bearing attribute (href or src) contains a safe scheme.
 */
function isSafeUrl(url: string): boolean {
  const cleanVal = cleanUrlValue(url);
  const colonIndex = cleanVal.indexOf(':');

  if (colonIndex === -1) {
    return true; // Relative URL, safe
  }

  const scheme = cleanVal.substring(0, colonIndex);
  return isValidScheme(scheme);
}

/**
 * Sanitizes attributes on a single element based on the ALLOWED_TAGS config.
 */
function sanitizeAttributes(el: Element, allowedAttrs: Set<string>): void {
  Array.from(el.attributes).forEach((attr) => {
    const attrName = attr.name.toLowerCase();

    // 1. Remove attributes not explicitly allowed on this tag
    if (!allowedAttrs.has(attrName)) {
      el.removeAttribute(attr.name);
      return;
    }

    // 2. Validate URL-bearing attributes against positive scheme list
    if (attrName === 'href' || attrName === 'src') {
      if (!isSafeUrl(attr.value)) {
        el.removeAttribute(attr.name);
      }
    }
  });
}

/**
 * Sanitizes a single DOM Element: removes it completely if its tag name is
 * not allowed, otherwise strips its disallowed attributes.
 */
function sanitizeElement(el: Element): void {
  const tagName = el.tagName.toLowerCase();
  if (!Object.prototype.hasOwnProperty.call(ALLOWED_TAGS, tagName)) {
    el.remove();
    return;
  }

  sanitizeAttributes(el, ALLOWED_TAGS[tagName]);
}

export function sanitizeHtml(html: string): string {
  if (!html) return '';
  if (typeof DOMParser === 'undefined') return html.replace(/<[^>]*>/g, '');

  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    doc.body.querySelectorAll('*').forEach(sanitizeElement);

    return doc.body.innerHTML;
  } catch (error) {
    console.error('HTML Sanitization error:', error);
    return html.replace(/<[^>]*>/g, '');
  }
}
