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

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(
    `${API_URL}${path}`,
    {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    },
  );

  let data: unknown = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const errorData =
      data &&
      typeof data === 'object'
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