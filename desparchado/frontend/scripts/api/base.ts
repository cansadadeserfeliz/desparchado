// Gets CSRF token from cookie (Django default) to be used in API requests.
export function getCsrfToken(): string {
  const name = 'csrftoken';
  let cookieValue = '';
  if (!document.cookie || document.cookie === '') return '';

  const cookies = document.cookie.split(';');

  for (const cookie of cookies) {
    const trimmedCookie = cookie.trim();
    if (trimmedCookie.startsWith(name + '=')) {
      cookieValue = decodeURIComponent(trimmedCookie.substring(name.length + 1));
      break;
    }
  }

  return cookieValue;
}

export interface IApiError {
  detail?: string;
  message?: string;
  non_field_errors?: string[] | string;
  [key: string]: string | string[] | undefined;
}

export class ValidationError extends Error {
  public data: IApiError;
  public status: number;
  constructor(data: IApiError, status: number) {
    super(`Validation failed with status ${status}`);
    this.name = 'ValidationError';
    this.data = data;
    this.status = status;
  }
}

/**
 * Asserts that a URL is trusted to prevent Server-Side Request Forgery (SSRF)
 * and unauthorized data exfiltration. A URL is trusted if it is relative (starts with '/')
 * or belongs to the current origin.
 *
 * @param url - The URL to validate.
 * @throws {Error} If the URL is untrusted.
 */
function assertTrustedUrl(url: string): void {
  const isTrusted =
    url.startsWith('/') ||
    (typeof window !== 'undefined' && url.startsWith(window.location.origin));
  if (!isTrusted) {
    throw new Error('Untrusted URL');
  }
}

export async function handleResponse<T>(
  res: Response,
  defaultErrorMessage = 'The server response is not valid JSON.',
): Promise<T> {
  try {
    const text = await res.text();
    const data = text ? (JSON.parse(text) as IApiError) : {};
    if (!res.ok) {
      throw new ValidationError(data, res.status);
    }
    return data as T;
  } catch (error) {
    if (error instanceof ValidationError) {
      throw error;
    }
    throw new Error(res.ok ? defaultErrorMessage : `Request failed with status ${res.status}`);
  }
}

export async function getData<T>(url: string): Promise<T> {
  assertTrustedUrl(url);

  const res = await fetch(url, {
    headers: { 'X-CSRFToken': getCsrfToken() },
    credentials: 'same-origin',
  });

  return handleResponse<T>(res);
}

export async function submitData(
  url: string,
  data: FormData,
  method: 'POST' | 'PATCH' = 'POST',
): Promise<Response> {
  assertTrustedUrl(url);

  return fetch(url, {
    method,
    body: data,
    headers: { 'X-CSRFToken': getCsrfToken() },
    credentials: 'same-origin',
  });
}
