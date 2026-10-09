import { apiRequest } from '@/lib/api';

export type UserGenrePreference = {
  id: number;
  genre_id: number;
  created_at: string;
  updated_at: string;
};

type UserGenrePreferenceListResponse = {
  results: UserGenrePreference[];
};

type UserGenrePreferenceSetResponse = {
  results: UserGenrePreference[];
};

export type SetGenrePreferencesParams = {
  genreIds: number[];
};

/**
 * Fetch the authenticated user's explicit music
 * genre preferences.
 */
export async function getGenrePreferences(): Promise<
  UserGenrePreference[]
> {
  const response =
    await apiRequest<UserGenrePreferenceListResponse>(
      '/api/v1/music/preferences/genres/',
    );

  return response.results;
}

/**
 * Add one genre to the authenticated user's
 * explicit music preferences.
 */
export async function addGenrePreference(
  genreId: number,
): Promise<UserGenrePreference> {
  return apiRequest<UserGenrePreference>(
    '/api/v1/music/preferences/genres/',
    {
      method: 'POST',
      body: JSON.stringify({
        genre_id: genreId,
      }),
    },
  );
}

/**
 * Remove one genre from the authenticated user's
 * explicit music preferences.
 */
export async function removeGenrePreference(
  genreId: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/music/preferences/genres/${genreId}/`,
    {
      method: 'DELETE',
    },
  );
}

/**
 * Replace the authenticated user's complete set of
 * explicit music genre preferences.
 *
 * The backend treats this as the source of truth for
 * the user's current explicit genre selection.
 */
export async function setGenrePreferences({
  genreIds,
}: SetGenrePreferencesParams): Promise<
  UserGenrePreference[]
> {
  const response =
    await apiRequest<UserGenrePreferenceSetResponse>(
      '/api/v1/music/preferences/genres/set/',
      {
        method: 'POST',
        body: JSON.stringify({
          genre_ids: genreIds,
        }),
      },
    );

  return response.results;
}