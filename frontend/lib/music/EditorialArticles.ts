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
  comments_count: number;
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

export async function getEditorialArticles({
  page,
  pageSize,
}: GetEditorialArticlesParams = {}): Promise<
  EditorialArticlesResponse
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
      ? `/api/v1/music/editorial/?${queryString}`
      : '/api/v1/music/editorial/';

  return apiRequest<EditorialArticlesResponse>(
    endpoint,
  );
}