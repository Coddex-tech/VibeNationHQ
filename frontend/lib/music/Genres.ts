import { apiRequest } from '@/lib/api';

export type MusicGenre = {
  id: number;
  name: string;
  slug: string;
};

type MusicGenreListResponse = {
  results: MusicGenre[];
};

/**
 * Fetch all active music genres available on
 * VibeNationHQ.
 */
export async function getMusicGenres(): Promise<
  MusicGenre[]
> {
  const response =
    await apiRequest<MusicGenreListResponse>(
      '/api/v1/music/genres/',
    );

  return response.results;
}