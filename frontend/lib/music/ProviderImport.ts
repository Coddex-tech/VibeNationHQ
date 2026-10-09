import { apiRequest } from '@/lib/api';

import type { MusicProviderSearchResult } from './providerSearch';

export type MusicProviderImportResponse = {
  entity_type: 'song' | 'album' | 'artist';
  created: boolean;
  identity_id: number;
  object_id: number;
  object_type: 'song' | 'album' | 'artist';
  title: string;
  artist: {
    id: number;
    name: string;
    slug: string;
  } | null;
  album: {
    id: number;
    title: string;
    slug: string;
  } | null;
  song: {
    id: number;
    title: string;
    slug: string;
  } | null;
};

export async function importMusicProviderResult(
  result: MusicProviderSearchResult,
): Promise<MusicProviderImportResponse> {
  const response =
    await apiRequest<MusicProviderImportResponse>(
      '/api/v1/music/import/',
      {
        method: 'POST',
        body: JSON.stringify({
          provider: result.provider,
          provider_id: result.provider_id,
          entity_type: result.entity_type,
          title: result.title,
          artist_name: result.artist_name,
          album_name: result.album_name,
          artwork_url: result.artwork_url,
          release_date: result.release_date,
          duration_seconds: result.duration_seconds,
          preview_url: result.preview_url,
          spotify_url: result.spotify_url,
          apple_music_url: result.apple_music_url,
          youtube_url: result.youtube_url,
          audiomack_url: result.audiomack_url,
          boomplay_url: result.boomplay_url,
          country: result.country,
          isrc: result.isrc,
          musicbrainz_id: result.musicbrainz_id,
          artist_musicbrainz_id:
            result.artist_musicbrainz_id,
          album_musicbrainz_id:
            result.album_musicbrainz_id,
          metadata: result.metadata,
        }),
      },
    );

  return response;
}