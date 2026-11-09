
import type { Metadata } from 'next';
import { cookies } from 'next/headers';

import MusicNavigation from '@/components/music/MusicNavigation';
import FavoritesClient from '@/components/favorites/FavoritesClient';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ??
  'http://localhost:3000';

const favoritesTitle = 'Your Favorites';

const favoritesDescription =
  'View the music community posts and editorial articles you have saved on VibeNationHQ.';

export const metadata: Metadata = {
  title: favoritesTitle,
  description: favoritesDescription,

  alternates: {
    canonical: '/favorites',
  },

  openGraph: {
    type: 'website',
    title: favoritesTitle,
    description: favoritesDescription,
    url: '/favorites',
  },

  twitter: {
    card: 'summary',
    title: favoritesTitle,
    description: favoritesDescription,
  },
};

export type FavoriteContentType =
  | 'community_post'
  | 'editorial';

export type CommunityPost = {
  id: number;
  user: {
    id: number;
    username: string;
  };
  content: string;
  rating: number | null;
  target: {
    id: number;
    target_type:
      | 'song'
      | 'album'
      | 'artist'
      | 'external';
    song: unknown | null;
    album: unknown | null;
    artist: unknown | null;
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
  } | null;
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

export type EditorialArticle = {
  id: number;
  title: string;
  slug: string;
  excerpt?: string | null;
  author?: unknown;
  song?: unknown | null;
  artist?: unknown | null;
  album?: unknown | null;
  status?: string;
  published_at?: string | null;
  is_featured?: boolean;
  views_count?: number;
  likes_count?: number;
  liked?: boolean;
  favorites_count?: number;
  favorited?: boolean;
  comments_count?: number;
};

export type FavoriteItem = {
  content_type: FavoriteContentType;
  favorited_at: string;
  content: CommunityPost | EditorialArticle;
};

export type FavoritesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: FavoriteItem[];
};

async function getInitialFavorites(): Promise<FavoritesResponse> {
  const cookieStore = await cookies();

  const cookieHeader = cookieStore
    .getAll()
    .map(({ name, value }) => `${name}=${value}`)
    .join('; ');

  const response = await fetch(
    `${API_URL}/api/v1/music/favorites/?page_size=20`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',

        ...(cookieHeader
          ? {
              Cookie: cookieHeader,
            }
          : {}),
      },
      cache: 'no-store',
    },
  );

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      return {
        count: 0,
        next: null,
        previous: null,
        results: [],
      };
    }

    throw new Error(
      `Favorites request failed with status ${response.status}.`,
    );
  }

  return response.json() as Promise<FavoritesResponse>;
}

export default async function FavoritesPage() {
  const favorites = await getInitialFavorites();

  const favoritesUrl = `${siteUrl}/favorites`;

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': `${favoritesUrl}#collectionpage`,
    name: favoritesTitle,
    description: favoritesDescription,
    url: favoritesUrl,

    isPartOf: {
      '@type': 'WebSite',
      '@id': `${siteUrl}#website`,
    },

    mainEntity: {
      '@type': 'ItemList',
      name: 'VibeNationHQ Favorites',
      url: favoritesUrl,
      numberOfItems: favorites.count,
    },
  };

  return (
    <div
      className="
        min-h-screen
        bg-light-bg
        text-light-text
        dark:bg-dark-bg
        dark:text-dark-text
      "
    >
      <MusicNavigation />

      <main className="mx-auto w-full max-w-3xl">
        <header className="px-4 pb-3 pt-6 sm:px-5 sm:pt-8">
          <h1
            className="
              text-2xl font-bold
              text-light-text
              dark:text-dark-text
            "
          >
            Your Favorites
          </h1>

          <p
            className="
              mt-1 text-sm
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            Your saved community posts and editorial articles, all in one place.
          </p>
        </header>

        <FavoritesClient initialFavorites={favorites} />
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData),
        }}
      />
    </div>
  );
}
