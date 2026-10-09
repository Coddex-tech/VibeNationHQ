import { apiRequest } from '@/lib/api';

import type {
  CommunityAlbum,
  CommunityArtist,
  CommunityPost,
  CommunitySong,
} from './CommunityPosts';

export type MusicFeedContentType =
  | 'community_post'
  | 'editorial'
  | 'song'
  | 'album'
  | 'artist';

export type MusicFeedSource =
  | 'mutual'
  | 'following'
  | 'followed_artist'
  | 'history'
  | 'featured'
  | 'editorial'
  | 'discovery'
  | 'recent';

export type MusicFeedEditorialArticle = {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  author: {
    id: number;
    name: string;
  };
  song: CommunitySong | null;
  artist: CommunityArtist | null;
  album: CommunityAlbum | null;
  status: string;
  published_at: string | null;
  is_featured: boolean;
  views_count: number;
  likes_count: number;
  comments_count: number;
};

export type MusicFeedContent =
  | {
      content_type: 'community_post';
      content: CommunityPost;
    }
  | {
      content_type: 'editorial';
      content: MusicFeedEditorialArticle;
    }
  | {
      content_type: 'song';
      content: CommunitySong;
    }
  | {
      content_type: 'album';
      content: CommunityAlbum;
    }
  | {
      content_type: 'artist';
      content: CommunityArtist;
    };

export type MusicFeedItem =
  MusicFeedContent & {
    source: MusicFeedSource;
  };

export type MusicFeedResponse = {
  results: MusicFeedItem[];
  has_more: boolean;
  next_cursor: string | null;
};

export type GetMusicFeedParams = {
  limit?: number;
  cursor?: string | null;
};

/**
 * Fetch the personalized VibeNationHQ music feed.
 *
 * The backend owns candidate generation, personalization,
 * ranking, diversity, and cursor-based pagination.
 */
export async function getMusicFeed({
  limit,
  cursor,
}: GetMusicFeedParams = {}): Promise<MusicFeedResponse> {
  const params = new URLSearchParams();

  if (limit !== undefined) {
    params.set(
      'limit',
      String(limit),
    );
  }

  if (cursor) {
    params.set(
      'cursor',
      cursor,
    );
  }

  const queryString = params.toString();

  const endpoint =
    queryString.length > 0
      ? `/api/v1/music/feed/?${queryString}`
      : '/api/v1/music/feed/';

  return apiRequest<MusicFeedResponse>(
    endpoint,
  );
}