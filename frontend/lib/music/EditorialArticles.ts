
import { apiRequest } from '@/lib/api';

export type EditorialAuthor = {
  id: number;
  name: string;
};

export type EditorialArtist = {
  id: number;
  name: string;
  slug: string;
  profile_image: string | null;
  is_verified: boolean;
  followers_count: number;
};

export type EditorialAlbum = {
  id: number;
  title: string;
  slug: string;
  artists: EditorialArtist[];
  release_type: string;
  artwork: string | null;
  release_date: string | null;
  favorites_count: number;
  ratings_count: number;
};

export type EditorialSong = {
  id: number;
  title: string;
  slug: string;
  artists: EditorialArtist[];
  featured_artists: EditorialArtist[];
  artwork: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  duration_display: string | null;
  favorites_count: number;
  ratings_count: number;
};

export type EditorialGenre = {
  id: number;
  name: string;
  slug: string;
  description: string;
};

export type EditorialArticleCard = {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  author: EditorialAuthor;
  song: EditorialSong | null;
  artist: EditorialArtist | null;
  album: EditorialAlbum | null;
  status: string;
  published_at: string | null;
  is_featured: boolean;
  views_count: number;
  likes_count: number;
  liked: boolean;
  favorites_count: number;
  favorited: boolean;
  comments_count: number;
};

export type EditorialArticle = EditorialArticleCard & {
  content: string;
  genres: EditorialGenre[];
  created_at: string;
  updated_at: string;
};

export type EditorialArticlesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: EditorialArticleCard[];
};

export type GetEditorialArticlesParams = {
  page?: number;
  pageSize?: number;
};

export type EditorialLikeResponse = {
  liked: boolean;
  likes_count: number;
};

export type EditorialFavoriteResponse = {
  favorited: boolean;
  favorites_count: number;
};

export type EditorialArticleViewResponse = {
  views_count: number;
};

// ============================================================
// EDITORIAL COMMENTS: TYPES
// ============================================================

export type EditorialCommentUser = {
  id: number;
  username: string;
  display_name: string;
  profile_image: string | null;
  is_verified: boolean;
  is_identity_verified: boolean;
};

export type EditorialComment = {
  id: number;
  user: EditorialCommentUser;
  article: number;
  parent: number | null;
  root_comment: number | null;
  content: string;
  mentioned_usernames: string[];
  views_count: number;
  likes_count: number;
  liked: boolean;
  replies_count: number;
  thread_replies_count: number;
  status: 'published' | 'hidden' | 'removed' | string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
};

export type EditorialCommentsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: EditorialComment[];
};

export type EditorialCommentLikeResponse = {
  liked: boolean;
  likes_count: number;
};

export type GetEditorialCommentsParams = {
  page?: number;
  pageSize?: number;
};

export type CreateEditorialCommentPayload = {
  content: string;
  parent?: number | null;
};

export type UpdateEditorialCommentPayload = {
  content: string;
};

export type EditorialCommentReportReason =
  | 'spam'
  | 'harassment'
  | 'hate'
  | 'sexual'
  | 'misinformation'
  | 'copyright'
  | 'other';

export type CreateEditorialCommentReportPayload = {
  reason: EditorialCommentReportReason;
  details?: string;
};

// ============================================================
// EDITORIAL ARTICLES
// ============================================================

export async function getEditorialArticles({
  page,
  pageSize,
}: GetEditorialArticlesParams = {}): Promise<EditorialArticlesResponse> {
  const params = new URLSearchParams();

  if (page !== undefined) {
    params.set('page', String(page));
  }

  if (pageSize !== undefined) {
    params.set('page_size', String(pageSize));
  }

  const queryString = params.toString();

  const endpoint = queryString
    ? `/api/v1/music/editorial/?${queryString}`
    : '/api/v1/music/editorial/';

  return apiRequest<EditorialArticlesResponse>(endpoint);
}

export async function getEditorialArticle(
  slug: string,
): Promise<EditorialArticle> {
  return apiRequest<EditorialArticle>(
    `/api/v1/music/editorial/${encodeURIComponent(slug)}/`,
  );
}

export async function likeEditorialArticle(
  articleId: number,
): Promise<EditorialLikeResponse> {
  return apiRequest<EditorialLikeResponse>(
    `/api/v1/music/editorial/${articleId}/like/`,
    { method: 'POST' },
  );
}

export async function unlikeEditorialArticle(
  articleId: number,
): Promise<EditorialLikeResponse> {
  return apiRequest<EditorialLikeResponse>(
    `/api/v1/music/editorial/${articleId}/like/`,
    { method: 'DELETE' },
  );
}

export async function favoriteEditorialArticle(
  articleId: number,
): Promise<EditorialFavoriteResponse> {
  return apiRequest<EditorialFavoriteResponse>(
    `/api/v1/music/editorial/${articleId}/favorite/`,
    { method: 'POST' },
  );
}

export async function unfavoriteEditorialArticle(
  articleId: number,
): Promise<EditorialFavoriteResponse> {
  return apiRequest<EditorialFavoriteResponse>(
    `/api/v1/music/editorial/${articleId}/favorite/`,
    { method: 'DELETE' },
  );
}

export async function recordEditorialArticleView(
  articleId: number,
): Promise<EditorialArticleViewResponse> {
  return apiRequest<EditorialArticleViewResponse>(
    `/api/v1/music/editorial/${articleId}/view/`,
    { method: 'POST' },
  );
}

// ============================================================
// EDITORIAL COMMENTS: API HELPERS
// ============================================================

export async function getEditorialComments(
  articleId: number,
  {
    page,
    pageSize,
  }: GetEditorialCommentsParams = {},
): Promise<EditorialCommentsResponse> {
  const params = new URLSearchParams();

  if (page !== undefined) {
    params.set('page', String(page));
  }

  if (pageSize !== undefined) {
    params.set('page_size', String(pageSize));
  }

  const queryString = params.toString();

  const endpoint =
    `/api/v1/music/editorial/${articleId}/comments/` +
    (queryString ? `?${queryString}` : '');

  return apiRequest<EditorialCommentsResponse>(endpoint);
}

export async function getEditorialCommentThread(
  articleId: number,
  rootCommentId: number,
  page = 1,
): Promise<EditorialCommentsResponse> {
  const params = new URLSearchParams({
    page: String(page),
  });

  return apiRequest<EditorialCommentsResponse>(
    `/api/v1/music/editorial/${articleId}/comments/` +
      `${rootCommentId}/thread/?${params.toString()}`,
  );
}

export async function createEditorialComment(
  articleId: number,
  payload: CreateEditorialCommentPayload,
): Promise<EditorialComment> {
  return apiRequest<EditorialComment>(
    `/api/v1/music/editorial/${articleId}/comments/`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  );
}

export async function updateEditorialComment(
  commentId: number,
  payload: UpdateEditorialCommentPayload,
): Promise<EditorialComment> {
  return apiRequest<EditorialComment>(
    `/api/v1/music/editorial/comments/${commentId}/`,
    {
      method: 'PATCH',
      body: JSON.stringify(payload),
    },
  );
}

export async function deleteEditorialComment(
  commentId: number,
): Promise<void> {
  return apiRequest<void>(
    `/api/v1/music/editorial/comments/${commentId}/`,
    { method: 'DELETE' },
  );
}

export async function likeEditorialComment(
  commentId: number,
): Promise<EditorialCommentLikeResponse> {
  return apiRequest<EditorialCommentLikeResponse>(
    `/api/v1/music/editorial/comments/${commentId}/like/`,
    { method: 'POST' },
  );
}

export async function unlikeEditorialComment(
  commentId: number,
): Promise<EditorialCommentLikeResponse> {
  return apiRequest<EditorialCommentLikeResponse>(
    `/api/v1/music/editorial/comments/${commentId}/like/`,
    { method: 'DELETE' },
  );
}

export async function reportEditorialComment(
  commentId: number,
  payload: CreateEditorialCommentReportPayload,
): Promise<unknown> {
  return apiRequest<unknown>(
    `/api/v1/music/editorial/comments/${commentId}/report/`,
    {
      method: 'POST',
      body: JSON.stringify({
        reason: payload.reason,
        details: payload.details?.trim() ?? '',
      }),
    },
  );
}
