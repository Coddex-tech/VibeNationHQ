import 'server-only';

import { cookies } from 'next/headers';

import type { CommunityPost } from './CommunityPosts';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';

export class CommunityPostFetchError extends Error {
  status: number;

  constructor(status: number) {
    super(
      `Community post request failed with status ${status}.`,
    );

    this.name = 'CommunityPostFetchError';
    this.status = status;
  }
}

export async function getCommunityPostById(
  postId: number,
): Promise<CommunityPost> {
  const cookieStore = await cookies();

  const cookieHeader = cookieStore
    .getAll()
    .map(
      ({ name, value }) =>
        `${name}=${value}`,
    )
    .join('; ');

  const response = await fetch(
    `${API_URL}/api/v1/music/community/posts/${postId}/`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',

        ...(cookieHeader
          ? {
              Cookie: cookieHeader,
            }
          : {}),
      },
      cache: 'no-store',
    },
  );

  if (!response.ok) {
    throw new CommunityPostFetchError(
      response.status,
    );
  }

  return response.json() as Promise<CommunityPost>;
}