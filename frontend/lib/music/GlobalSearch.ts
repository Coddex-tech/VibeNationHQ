
import { apiRequest } from '@/lib/api';

import type {
  CommunityPost,
  CommunitySong,
  CommunityAlbum,
  CommunityArtist,
  CommunityUser,
} from '@/lib/music/CommunityPosts';

import type {
  MusicFeedEditorialArticle,
} from '@/lib/music/MusicFeed';

// ========================================================
// Search categories
// ========================================================

export type GlobalSearchCategory =
  | 'songs'
  | 'albums'
  | 'artists'
  | 'community_posts'
  | 'editorial_articles'
  | 'users';

export type GlobalSearchType =
  | 'all'
  | GlobalSearchCategory;

// ========================================================
// Paginated category response
// ========================================================

export type GlobalSearchCategoryPage<T> = {
  count: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  next: string | null;
  previous: string | null;
  results: T[];
};

// ========================================================
// Search response
// ========================================================

export type GlobalSearchResults = {
  songs: GlobalSearchCategoryPage<CommunitySong>;
  albums: GlobalSearchCategoryPage<CommunityAlbum>;
  artists: GlobalSearchCategoryPage<CommunityArtist>;
  community_posts: GlobalSearchCategoryPage<CommunityPost>;
  editorial_articles: GlobalSearchCategoryPage<MusicFeedEditorialArticle>;
  users: GlobalSearchCategoryPage<CommunityUser>;
};

export type GlobalSearchResponse = {
  query: string;
  type: GlobalSearchType;
  results: GlobalSearchResults;
};

// ========================================================
// Search parameters
// ========================================================

export type GlobalSearchPages = {
  songs?: number;
  albums?: number;
  artists?: number;
  community_posts?: number;
  editorial_articles?: number;
  users?: number;
};

export type GetGlobalSearchParams = {
  query: string;
  type?: GlobalSearchType;
  pageSize?: number;
  pages?: GlobalSearchPages;
  signal?: AbortSignal;
};

// ========================================================
// API
// ========================================================

/**
 * Performs a global search across VibeNationHQ.
 *
 * Each category has its own independent pagination parameter.
 * Passing an AbortSignal allows callers to cancel outdated
 * requests when the search query changes.
 */
export async function getGlobalSearch({
  query,
  type = 'all',
  pageSize,
  pages,
  signal,
}: GetGlobalSearchParams): Promise<GlobalSearchResponse> {
  const trimmedQuery = query.trim();

  if (!trimmedQuery) {
    throw new Error('Enter a search term.');
  }

  const params = new URLSearchParams();

  params.set('q', trimmedQuery);

  if (type !== 'all') {
    params.set('type', type);
  }

  if (pageSize !== undefined) {
    params.set('page_size', String(pageSize));
  }

  if (pages?.songs !== undefined) {
    params.set('songs_page', String(pages.songs));
  }

  if (pages?.albums !== undefined) {
    params.set('albums_page', String(pages.albums));
  }

  if (pages?.artists !== undefined) {
    params.set('artists_page', String(pages.artists));
  }

  if (pages?.community_posts !== undefined) {
    params.set(
      'community_posts_page',
      String(pages.community_posts),
    );
  }

  if (pages?.editorial_articles !== undefined) {
    params.set(
      'editorial_articles_page',
      String(pages.editorial_articles),
    );
  }

  if (pages?.users !== undefined) {
    params.set('users_page', String(pages.users));
  }

  return apiRequest<GlobalSearchResponse>(
    `/api/v1/music/global-search/?${params.toString()}`,
    {
      method: 'GET',
      signal,
    },
  );
}
