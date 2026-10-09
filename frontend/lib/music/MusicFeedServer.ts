import 'server-only';

import { cookies } from 'next/headers';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';

import type {
  MusicFeedResponse,
} from './MusicFeed';

export async function getInitialMusicFeed(): Promise<MusicFeedResponse> {
  const cookieStore = await cookies();

  const cookieHeader =
    cookieStore
      .getAll()
      .map(
        ({ name, value }) =>
          `${name}=${value}`,
      )
      .join('; ');

  const response = await fetch(
    `${API_URL}/api/v1/music/feed/`,
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
    throw new Error(
      `Music feed request failed with status ${response.status}.`,
    );
  }

  return response.json() as Promise<MusicFeedResponse>;
}