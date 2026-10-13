
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
  is_following?: boolean;
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
  slug: string;
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

export type ArtistFollowResponse = {
  following: boolean;
  followers_count: number;
  follow?: {
    id: number;
  };
};

// ============================================================
// COMMUNITY COMMENT TYPES
// ============================================================

export type CommunityCommentStatus =
  | 'published'
  | 'hidden'
  | 'removed';

export type CommunityCommentReportReason =
  | 'spam'
  | 'harassment'
  | 'hate'
  | 'sexual'
  | 'misinformation'
  | 'other';

export type CommunityComment = {
  id: number;
  user: CommunityUser;
  post: number;
  post_creator_id: number;
  parent: number | null;
  content: string;
  views_count: number;
  likes_count: number;
  replies_count: number;
  thread_replies_count: number;
  status: CommunityCommentStatus;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
  is_liked?: boolean;
};

export type CommunityCommentsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: CommunityComment[];
};

export type CommunityCommentCreatePayload = {
  post: number;
  parent: number | null;
  content: string;
};

export type CommunityCommentUpdatePayload = {
  content: string;
};

export type CommunityCommentLikeResponse = {
  liked: boolean;
  likes_count: number;
};

export type CommunityCommentReportPayload = {
  reason: CommunityCommentReportReason;
  details?: string;
};

// ============================================================
// COMMUNITY POSTS API
// ============================================================

export type GetCommunityPostsParams = {
  page?: number;
  pageSize?: number;
};

export async function getCommunityPosts({
  page,
  pageSize,
}: GetCommunityPostsParams = {}): Promise<CommunityPostsResponse> {
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

  return apiRequest<CommunityPostsResponse>(endpoint);
}

export async function getCommunityPost(
  postId: number,
): Promise<CommunityPost> {
  return apiRequest<CommunityPost>(
    `/api/v1/music/community/posts/${postId}/`,
  );
}

// ============================================================
// COMMUNITY FAVORITES API
// ============================================================

export type GetCommunityFavoritesParams = {
  page?: number;
  pageSize?: number;
};

export async function getCommunityFavorites({
  page,
  pageSize,
}: GetCommunityFavoritesParams = {}): Promise<CommunityPostsResponse> {
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

  return apiRequest<CommunityPostsResponse>(endpoint);
}

// ============================================================
// COMMUNITY COMMENTS API
// ============================================================

export type GetCommunityCommentsParams = {
  page?: number;
  pageSize?: number;
  parentId?: number;
};

/**
 * Load top-level comments when parentId is omitted.
 * Load direct replies to a comment when parentId is supplied.
 *
 * The backend returns a paginated response.
 */
export async function getCommunityComments(
  postId: number,
  {
    page,
    pageSize,
    parentId,
  }: GetCommunityCommentsParams = {},
): Promise<CommunityCommentsResponse> {
  const params = new URLSearchParams();

  if (page !== undefined) {
    params.set('page', String(page));
  }

  if (pageSize !== undefined) {
    params.set('page_size', String(pageSize));
  }

  if (parentId !== undefined) {
    params.set('parent', String(parentId));
  }

  const queryString = params.toString();

  const endpoint =
    `/api/v1/music/community/posts/${postId}/comments/` +
    (queryString ? `?${queryString}` : '');

  return apiRequest<CommunityCommentsResponse>(endpoint);
}


/**
 * Load one page of replies belonging to a root comment's entire thread.
 *
 * The backend returns descendants at every nesting level, preserving
 * each comment's actual parent ID.
 *
 * The backend controls the page size (five comments per request).
 */
export async function getCommunityCommentThread(
  postId: number,
  rootCommentId: number,
  {
    page,
  }: {
    page?: number;
  } = {},
): Promise<CommunityCommentsResponse> {
  const params = new URLSearchParams();

  if (page !== undefined) {
    params.set('page', String(page));
  }

  const queryString = params.toString();

  const endpoint =
    `/api/v1/music/community/posts/${postId}/comments/` +
    `${rootCommentId}/thread/` +
    (queryString ? `?${queryString}` : '');

  return apiRequest<CommunityCommentsResponse>(endpoint);
}


/**
 * Create a top-level comment or a reply.
 *
 * Set parent to null for a top-level comment.
 * Set parent to the target comment ID for a reply.
 */
export async function createCommunityComment(
  payload: CommunityCommentCreatePayload,
): Promise<CommunityComment> {
  return apiRequest<CommunityComment>(
    `/api/v1/music/community/posts/${payload.post}/comments/`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  );
}

/**
 * Edit an existing comment.
 */
export async function updateCommunityComment(
  commentId: number,
  payload: CommunityCommentUpdatePayload,
): Promise<CommunityComment> {
  return apiRequest<CommunityComment>(
    `/api/v1/music/community/comments/${commentId}/`,
    {
      method: 'PATCH',
      body: JSON.stringify(payload),
    },
  );
}

/**
 * Delete a comment.
 *
 * The backend performs a soft delete.
 * A successful response may have no response body (HTTP 204).
 */
export async function deleteCommunityComment(
  commentId: number,
): Promise<void> {
  await apiRequest<void>(
    `/api/v1/music/community/comments/${commentId}/`,
    {
      method: 'DELETE',
    },
  );
}

/**
 * Like a comment or reply.
 */
export async function likeCommunityComment(
  commentId: number,
): Promise<CommunityCommentLikeResponse> {
  return apiRequest<CommunityCommentLikeResponse>(
    `/api/v1/music/community/comments/${commentId}/like/`,
    {
      method: 'POST',
    },
  );
}

/**
 * Unlike a comment or reply.
 */
export async function unlikeCommunityComment(
  commentId: number,
): Promise<CommunityCommentLikeResponse> {
  return apiRequest<CommunityCommentLikeResponse>(
    `/api/v1/music/community/comments/${commentId}/like/`,
    {
      method: 'DELETE',
    },
  );
}

/**
 * Report a comment or reply.
 */
export async function reportCommunityComment(
  commentId: number,
  payload: CommunityCommentReportPayload,
): Promise<unknown> {
  return apiRequest<unknown>(
    `/api/v1/music/community/comments/${commentId}/report/`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  );
}

// ============================================================
// USER FOLLOW API
// ============================================================

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

// ============================================================
// ARTIST FOLLOW API
// ============================================================

export async function followArtist(
  artistId: number,
): Promise<ArtistFollowResponse> {
  return apiRequest<ArtistFollowResponse>(
    `/api/v1/music/artists/${artistId}/follow/`,
    {
      method: 'POST',
    },
  );
}

export async function unfollowArtist(
  artistId: number,
): Promise<ArtistFollowResponse> {
  return apiRequest<ArtistFollowResponse>(
    `/api/v1/music/artists/${artistId}/follow/`,
    {
      method: 'DELETE',
    },
  );
}
