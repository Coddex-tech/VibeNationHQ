const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';

type ApiErrorResponse = {
  detail?: string;
  [key: string]: unknown;
};

export class ApiError extends Error {
  status: number;
  data: ApiErrorResponse | null;

  constructor(
    message: string,
    status: number,
    data: ApiErrorResponse | null = null,
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Resolves relative Django media paths against the configured backend URL.
 * Absolute URLs are preserved, including external provider URLs.
 */
export function getMediaUrl(
  path: string | null | undefined,
): string | null {
  if (!path) {
    return null;
  }

  try {
    return new URL(path, API_URL).toString();
  } catch {
    return path;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  const isFormData =
    typeof FormData !== 'undefined' &&
    options.body instanceof FormData;

  if (!isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers,
  });

  let data: unknown = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const errorData =
      data && typeof data === 'object'
        ? (data as ApiErrorResponse)
        : null;

    throw new ApiError(
      errorData?.detail ??
        'Something went wrong. Please try again.',
      response.status,
      errorData,
    );
  }

  return data as T;
}