import { apiRequest } from '@/lib/api';

export type MusicProvider =
  | 'itunes'
  | 'musicbrainz'
  | 'spotify'
  | 'other';

export type MusicEntityType =
  | 'song'
  | 'album'
  | 'artist';

export type MusicProviderSearchResult = {
  provider: MusicProvider;
  provider_id: string;
  entity_type: MusicEntityType;
  title: string;
  artist_name: string | null;
  album_name: string | null;
  artwork_url: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  preview_url: string | null;
  spotify_url: string | null;
  apple_music_url: string | null;
  youtube_url: string | null;
  audiomack_url: string | null;
  boomplay_url: string | null;
  country: string | null;
  isrc: string | null;
  musicbrainz_id: string | null;
  artist_musicbrainz_id: string | null;
  album_musicbrainz_id: string | null;
  metadata: Record<string, unknown>;
};

type MusicProviderSearchResponse = {
  results: MusicProviderSearchResult[];
};

export type MusicProviderSearchParams = {
  query: string;
  entityType?: MusicEntityType;
  country?: string;
  limit?: number;
};

export async function searchMusicProviders({
  query,
  entityType,
  country = 'NG',
  limit = 10,
}: MusicProviderSearchParams): Promise<
  MusicProviderSearchResult[]
> {
  const params = new URLSearchParams();

  params.set('q', query);

  if (entityType) {
    params.set('type', entityType);
  }

  params.set(
    'country',
    country.toUpperCase(),
  );

  params.set(
    'limit',
    String(limit),
  );

  const response =
    await apiRequest<MusicProviderSearchResponse>(
      `/api/v1/music/search/providers/?${params.toString()}`,
    );

  return response.results;
}