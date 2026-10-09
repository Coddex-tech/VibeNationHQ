import {
  searchMusicCatalog,
  type MusicCatalogEntityType,
  type MusicCatalogSearchResult,
} from './CatalogSearch';

import {
    searchMusicProviders,
    type MusicEntityType,
    type MusicProviderSearchResult
} from './ProviderSearch';

export type MusicSearchSource =
  | 'catalog'
  | 'providers';

export type MusicSearchResult =
  | {
      source: 'catalog';
      result: MusicCatalogSearchResult;
    }
  | {
      source: 'providers';
      result: MusicProviderSearchResult;
    };

export type MusicSearchParams = {
  query: string;
  entityType?: MusicCatalogEntityType;
  limit?: number;
};

export type MusicSearchResponse = {
  source: MusicSearchSource;
  results: MusicSearchResult[];
};

export async function searchMusic({
  query,
  entityType,
  limit = 10,
}: MusicSearchParams): Promise<MusicSearchResponse> {
  const normalizedQuery = query.trim();

  if (!normalizedQuery) {
    return {
      source: 'catalog',
      results: [],
    };
  }

  const catalogResults =
    await searchMusicCatalog({
      query: normalizedQuery,
      entityType,
      limit,
    });

  if (catalogResults.length > 0) {
    return {
      source: 'catalog',
      results: catalogResults.map((result) => ({
        source: 'catalog',
        result,
      })),
    };
  }

  const providerEntityType:
    | MusicEntityType
    | undefined = entityType;

  const providerResults =
    await searchMusicProviders({
      query: normalizedQuery,
      entityType: providerEntityType,
      limit,
    });

  return {
    source: 'providers',
    results: providerResults.map((result) => ({
      source: 'providers',
      result,
    })),
  };
}