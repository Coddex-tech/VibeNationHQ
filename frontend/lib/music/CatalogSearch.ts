import { apiRequest } from '@/lib/api';

export type MusicCatalogEntityType =
  | 'song'
  | 'album'
  | 'artist';

export type MusicCatalogArtist = {
  id: number;
  name: string;
  slug: string;
};

export type MusicCatalogAlbum = {
  id: number;
  title: string;
  slug: string;
};

export type MusicCatalogSearchResult = {
  entity_type: MusicCatalogEntityType;
  id: number;
  title: string;
  slug: string;
  artist: MusicCatalogArtist | null;
  artists: MusicCatalogArtist[];
  album: MusicCatalogAlbum | null;
  artwork: string | null;
};

type MusicCatalogSearchResponse = {
  results: MusicCatalogSearchResult[];
};

export type MusicCatalogSearchParams = {
  query: string;
  entityType?: MusicCatalogEntityType;
  limit?: number;
};

export async function searchMusicCatalog({
  query,
  entityType,
  limit = 10,
}: MusicCatalogSearchParams): Promise<
  MusicCatalogSearchResult[]
> {
  const params = new URLSearchParams();

  params.set('q', query);

  if (entityType) {
    params.set('type', entityType);
  }

  params.set('limit', String(limit));

  const response =
    await apiRequest<MusicCatalogSearchResponse>(
      `/api/v1/music/catalog/search/?${params.toString()}`,
    );

  return response.results;
}
