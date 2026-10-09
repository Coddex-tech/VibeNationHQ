import { apiRequest } from '@/lib/api';


// ============================================================
// SHARED PAGINATION
// ============================================================


export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};


// ============================================================
// CATALOG TYPES
// ============================================================


export type EditorialGenre = {
  id: number;
  name: string;
  slug: string;
  description: string;
};


export type EditorialArtistCard = {
  id: number;
  name: string;
  slug: string;
  profile_image: string | null;
  is_verified: boolean;
  followers_count: number;
};


export type EditorialAlbumCard = {
  id: number;
  title: string;
  slug: string;
  artists: EditorialArtistCard[];
  release_type: string;
  artwork: string | null;
  release_date: string | null;
  favorites_count: number;
  ratings_count: number;
};


export type EditorialSongCard = {
  id: number;
  title: string;
  slug: string;
  artists: EditorialArtistCard[];
  featured_artists: EditorialArtistCard[];
  artwork: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  duration_display: string;
  favorites_count: number;
  ratings_count: number;
};


// ============================================================
// EDITORIAL AUTHOR
// ============================================================


export type EditorialAuthor = {
  id: number;
  name: string;
};


// ============================================================
// EDITORIAL ARTICLE
// ============================================================


export type EditorialArticleCard = {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  author: EditorialAuthor;
  song: EditorialSongCard | null;
  artist: EditorialArtistCard | null;
  album: EditorialAlbumCard | null;
  status: string;
  published_at: string | null;
  is_featured: boolean;
  views_count: number;
  likes_count: number;
  liked: boolean;
  comments_count: number;
};


export type EditorialArticle = {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  author: EditorialAuthor;
  song: EditorialSongCard | null;
  artist: EditorialArtistCard | null;
  album: EditorialAlbumCard | null;
  genres: EditorialGenre[];
  status: string;
  published_at: string | null;
  is_featured: boolean;
  views_count: number;
  likes_count: number;
  liked: boolean;
  comments_count: number;
  created_at: string;
  updated_at: string;
};


// ============================================================
// EDITORIAL COMMENTS
// ============================================================


export type EditorialCommentUser = {
  id: number;
  name: string;
};


export type EditorialComment = {
  id: number;
  user: EditorialCommentUser;
  article: number;
  parent: number | null;
  content: string;
  views_count: number;
  likes_count: number;
  liked: boolean;
  replies_count: number;
  status: string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
};


// ============================================================
// REPORTS
// ============================================================


export type EditorialReportReason =
  | string;


export type EditorialArticleReport = {
  id: number;
  user: number;
  article: number;
  reason: EditorialReportReason;
  details: string;
  created_at: string;
  updated_at: string;
};


export type EditorialCommentReport = {
  id: number;
  user: number;
  comment: number;
  reason: EditorialReportReason;
  details: string;
  created_at: string;
  updated_at: string;
};


// ============================================================
// REQUEST TYPES
// ============================================================


export type CreateEditorialCommentInput = {
  content: string;
  parent?: number | null;
};


export type UpdateEditorialCommentInput = {
  content: string;
};


export type CreateEditorialArticleReportInput = {
  reason: string;
  details?: string;
};


export type CreateEditorialCommentReportInput = {
  reason: string;
  details?: string;
};


// ============================================================
// ARTICLE API
// ============================================================


export async function getEditorialArticles(
  page = 1,
  pageSize?: number,
): Promise<
  PaginatedResponse<EditorialArticleCard>
> {
  const params = new URLSearchParams();

  params.set(
    'page',
    String(page),
  );

  if (pageSize !== undefined) {
    params.set(
      'page_size',
      String(pageSize),
    );
  }

  return apiRequest<
    PaginatedResponse<EditorialArticleCard>
  >(
    `/api/editorial/articles/?${params.toString()}`,
  );
}


export async function getEditorialArticle(
  slug: string,
): Promise<EditorialArticle> {
  return apiRequest<EditorialArticle>(
    `/api/editorial/articles/${encodeURIComponent(slug)}/`,
  );
}


// ============================================================
// ARTICLE LIKES
// ============================================================


export type EditorialLikeResponse = {
  liked: boolean;
  likes_count: number;
};


export async function likeEditorialArticle(
  articleId: number,
): Promise<EditorialLikeResponse> {
  return apiRequest<EditorialLikeResponse>(
    `/api/editorial/articles/${articleId}/like/`,
    {
      method: 'POST',
    },
  );
}


export async function unlikeEditorialArticle(
  articleId: number,
): Promise<EditorialLikeResponse> {
  return apiRequest<EditorialLikeResponse>(
    `/api/editorial/articles/${articleId}/like/`,
    {
      method: 'DELETE',
    },
  );
}


// ============================================================
// EDITORIAL COMMENTS
// ============================================================


export async function getEditorialComments(
  articleId: number,
  page = 1,
  pageSize?: number,
  parent?: number | null,
): Promise<
  PaginatedResponse<EditorialComment>
> {
  const params = new URLSearchParams();

  params.set(
    'page',
    String(page),
  );

  if (pageSize !== undefined) {
    params.set(
      'page_size',
      String(pageSize),
    );
  }

  if (parent !== undefined && parent !== null) {
    params.set(
      'parent',
      String(parent),
    );
  }

  return apiRequest<
    PaginatedResponse<EditorialComment>
  >(
    `/api/editorial/articles/${articleId}/comments/?${params.toString()}`,
  );
}


export async function createEditorialComment(
  articleId: number,
  input: CreateEditorialCommentInput,
): Promise<EditorialComment> {
  return apiRequest<EditorialComment>(
    `/api/editorial/articles/${articleId}/comments/`,
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}


export async function updateEditorialComment(
  commentId: number,
  input: UpdateEditorialCommentInput,
): Promise<EditorialComment> {
  return apiRequest<EditorialComment>(
    `/api/editorial/comments/${commentId}/`,
    {
      method: 'PATCH',
      body: JSON.stringify(input),
    },
  );
}


export async function deleteEditorialComment(
  commentId: number,
): Promise<void> {
  await apiRequest<unknown>(
    `/api/editorial/comments/${commentId}/`,
    {
      method: 'DELETE',
    },
  );
}


// ============================================================
// COMMENT LIKES
// ============================================================


export async function likeEditorialComment(
  commentId: number,
): Promise<EditorialLikeResponse> {
  return apiRequest<EditorialLikeResponse>(
    `/api/editorial/comments/${commentId}/like/`,
    {
      method: 'POST',
    },
  );
}


export async function unlikeEditorialComment(
  commentId: number,
): Promise<EditorialLikeResponse> {
  return apiRequest<EditorialLikeResponse>(
    `/api/editorial/comments/${commentId}/like/`,
    {
      method: 'DELETE',
    },
  );
}


// ============================================================
// ARTICLE REPORTS
// ============================================================


export async function reportEditorialArticle(
  articleId: number,
  input: CreateEditorialArticleReportInput,
): Promise<EditorialArticleReport> {
  return apiRequest<EditorialArticleReport>(
    `/api/editorial/articles/${articleId}/report/`,
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}


// ============================================================
// COMMENT REPORTS
// ============================================================


export async function reportEditorialComment(
  commentId: number,
  input: CreateEditorialCommentReportInput,
): Promise<EditorialCommentReport> {
  return apiRequest<EditorialCommentReport>(
    `/api/editorial/comments/${commentId}/report/`,
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}