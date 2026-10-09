import type { Metadata } from 'next';
import { cookies } from 'next/headers';

import MusicPost from '@/components/music/MusicPost';
import MusicNavigation from '@/components/music/MusicNavigation';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ??
  'http://localhost:3000';

const favoritesTitle =
  'Your Favorites';

const favoritesDescription =
  'View the music community posts you have saved on VibeNationHQ.';

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

type CommunityPost = {
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

type CommunityPostsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: CommunityPost[];
};

async function getInitialCommunityFavorites(): Promise<
  CommunityPostsResponse
> {
  const cookieStore = await cookies();

  const cookieHeader =
    cookieStore
      .getAll()
      .map(
        ({ name, value }) =>
          `${name}=${value}`,
      )
      .join('; ');

  const response = await fetch(
    `${API_URL}/api/v1/music/community/favorites/?page_size=20`,
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
    throw new Error(
      `Community favorites request failed with status ${response.status}.`,
    );
  }

  return response.json() as Promise<
    CommunityPostsResponse
  >;
}

export default async function FavoritesPage() {
  const favorites =
    await getInitialCommunityFavorites();

  const favoritesUrl =
    `${siteUrl}/favorites`;

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

      <main
        className="
          mx-auto w-full max-w-3xl
        "
      >
        <header
          className="
            px-4 pb-3 pt-6
            sm:px-5 sm:pt-8
          "
        >
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
            Posts you have saved from the music community.
          </p>
        </header>

        {favorites.results.length > 0 ? (
          <section
            aria-label="Favorite music community posts"
          >
            {favorites.results.map((post) => (
              <MusicPost
                key={post.id}
                post={post as never}
              />
            ))}
          </section>
        ) : (
          <section
            className="
              px-4 py-16 text-center
              sm:px-5
            "
          >
            <h2
              className="
                text-lg font-semibold
                text-light-text
                dark:text-dark-text
              "
            >
              No favorites yet
            </h2>

            <p
              className="
                mx-auto mt-2 max-w-sm
                text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
              "
            >
              Posts you save from the music community
              will appear here.
            </p>
          </section>
        )}
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            structuredData,
          ),
        }}
      />
    </div>
  );
}