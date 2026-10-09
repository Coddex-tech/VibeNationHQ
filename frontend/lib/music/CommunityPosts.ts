
import { apiRequest } from '@/lib/api';

export type CommunityTargetType =
  | 'song'
  | 'album'
  | 'artist'
  | 'external';

export type CommunityUser = {
  id: number;
  username: string;
  is_following: boolean;
};

export type CommunityArtist = {
  id: number;
  name: string;
  slug: string;
  profile_image: string | null;
  is_verified: boolean;
  followers_count: number;
};

export type CommunityAlbum = {
  id: number;
  title: string;
  slug: string;
  artists: CommunityArtist[];
  release_type: string;
  artwork: string | null;
  release_date: string | null;
  favorites_count: number;
  ratings_count: number;
};

export type CommunitySong = {
  id: number;
  title: string;
  slug: string;
  artists: CommunityArtist[];
  featured_artists: CommunityArtist[];
  artwork: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  duration_display: string | null;
  favorites_count: number;
  ratings_count: number;
};

export type CommunityPostTarget = {
  id: number;
  target_type: CommunityTargetType;

  song: CommunitySong | null;
  album: CommunityAlbum | null;
  artist: CommunityArtist | null;

  external_provider: string | null;
  external_content_type: string | null;
  external_id: string | null;

  title: string | null;
  artist_name: string | null;
  album_name: string | null;
  artwork_url: string | null;
  preview_url: string | null;
  spotify_url: string | null;
  apple_music_url: string | null;
};

export type CommunityPost = {
  id: number;
  user: CommunityUser;
  content: string;
  rating: number | null;
  target: CommunityPostTarget | null;
  views_count: number;
  likes_count: number;
  comments_count: number;
  favorites_count: number;
  is_liked: boolean;
  is_favorited: boolean;
  status: string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
};

export type CommunityPostsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: CommunityPost[];
};

export type UserFollowResponse = {
  following: boolean;
  follow?: {
    id: number;
  };
};

export type GetCommunityPostsParams = {
  page?: number;
  pageSize?: number;
};

export async function getCommunityPosts({
  page,
  pageSize,
}: GetCommunityPostsParams = {}): Promise<
  CommunityPostsResponse
> {
  const params = new URLSearchParams();

  if (page !== undefined) {
    params.set('page', String(page));
  }

  if (pageSize !== undefined) {
    params.set('page_size', String(pageSize));
  }

  const queryString = params.toString();

  const endpoint =
    queryString.length > 0
      ? `/api/v1/music/community/posts/?${queryString}`
      : '/api/v1/music/community/posts/';

  return apiRequest<CommunityPostsResponse>(
      endpoint,
    );
}

export type GetCommunityFavoritesParams = {
  page?: number;
  pageSize?: number;
};

export async function getCommunityFavorites({
  page,
  pageSize,
}: GetCommunityFavoritesParams = {}): Promise<
  CommunityPostsResponse
> {
  const params = new URLSearchParams();

  if (page !== undefined) {
    params.set('page', String(page));
  }

  if (pageSize !== undefined) {
    params.set('page_size', String(pageSize));
  }

  const queryString = params.toString();

  const endpoint =
    queryString.length > 0
      ? `/api/v1/music/community/favorites/?${queryString}`
      : '/api/v1/music/community/favorites/';

  return apiRequest<CommunityPostsResponse>(
    endpoint,
  );
}

export async function followCommunityUser(
  userId: number,
): Promise<UserFollowResponse> {
  return apiRequest<UserFollowResponse>(
    `/api/v1/music/users/${userId}/follow/`,
    {
      method: 'POST',
    },
  );
}

export async function unfollowCommunityUser(
  userId: number,
): Promise<UserFollowResponse> {
  return apiRequest<UserFollowResponse>(
    `/api/v1/music/users/${userId}/follow/`,
    {
      method: 'DELETE',
    },
  );
}