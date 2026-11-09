
'use client';

import { useCallback, useState } from 'react';
import {
  Bookmark,
  Music2,
  Newspaper,
  Layers3,
  RefreshCw,
} from 'lucide-react';

import MusicPost from '@/components/music/CommunityPost';
import MusicEditorialPost from '@/components/music/MusicEditorialPost';

import type {
  CommunityPost,
  EditorialArticle,
  FavoriteContentType,
  FavoriteItem,
  FavoritesResponse
} from './page';

import type {
  MusicFeedEditorialArticle,
} from '@/lib/music/MusicFeed';

type FavoritesTab =
  | 'all'
  | 'community_post'
  | 'editorial';

type FavoritesClientProps = {
  initialFavorites: FavoritesResponse;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';

const PAGE_SIZE = 20;

const TABS: {
  value: FavoritesTab;
  label: string;
  description: string;
  icon: typeof Layers3;
}[] = [
  {
    value: 'all',
    label: 'All',
    description: 'Everything you saved',
    icon: Layers3,
  },
  {
    value: 'community_post',
    label: 'Community',
    description: 'Posts from the community',
    icon: Music2,
  },
  {
    value: 'editorial',
    label: 'Editorial',
    description: 'Articles worth keeping',
    icon: Newspaper,
  },
];

function getTabType(
  tab: FavoritesTab,
): FavoriteContentType | null {
  return tab === 'all' ? null : tab;
}

function isCommunityPost(
  item: FavoriteItem,
): item is FavoriteItem & {
  content: CommunityPost;
} {
  return item.content_type === 'community_post';
}

function isEditorialArticle(
  item: FavoriteItem,
): item is FavoriteItem & {
  content: EditorialArticle;
} {
  return item.content_type === 'editorial';
}

export default function FavoritesClient({
  initialFavorites,
}: FavoritesClientProps) {
  const [activeTab, setActiveTab] =
    useState<FavoritesTab>('all');

  const [favorites, setFavorites] =
    useState<FavoriteItem[]>(
      initialFavorites.results,
    );

  const [count, setCount] =
    useState(initialFavorites.count);

  const [nextUrl, setNextUrl] =
    useState<string | null>(
      initialFavorites.next,
    );

  const [loading, setLoading] =
    useState(false);

  const [loadingMore, setLoadingMore] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [loadedTab, setLoadedTab] =
    useState<FavoritesTab>('all');

  const getFavorites = useCallback(
    async (
      tab: FavoritesTab,
      url?: string,
    ): Promise<FavoritesResponse> => {
      const type = getTabType(tab);

      const endpoint =
        url ??
        `${API_URL}/api/v1/music/favorites/?page_size=${PAGE_SIZE}${
          type
            ? `&type=${encodeURIComponent(type)}`
            : ''
        }`;

      const response = await fetch(endpoint, {
        method: 'GET',
        credentials: 'include',
        headers: {
          Accept: 'application/json',
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        if (
          response.status === 401 ||
          response.status === 403
        ) {
          throw new Error(
            'Please sign in to view your favorites.',
          );
        }

        throw new Error(
          `Unable to load favorites (${response.status}).`,
        );
      }

      return response.json() as Promise<FavoritesResponse>;
    },
    [],
  );

  const changeTab = useCallback(
    async (tab: FavoritesTab) => {
      if (tab === activeTab && tab === loadedTab) {
        return;
      }

      setActiveTab(tab);
      setLoading(true);
      setError(null);

      try {
        const response = await getFavorites(tab);

        setFavorites(response.results);
        setCount(response.count);
        setNextUrl(response.next);
        setLoadedTab(tab);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : 'Something went wrong while loading favorites.',
        );

        setFavorites([]);
        setCount(0);
        setNextUrl(null);
      } finally {
        setLoading(false);
      }
    },
    [activeTab, loadedTab, getFavorites],
  );

  const loadNextPage = useCallback(async () => {
    if (!nextUrl || loadingMore) {
      return;
    }

    setLoadingMore(true);
    setError(null);

    try {
      const response = await getFavorites(
        activeTab,
        nextUrl,
      );

      setFavorites((current) => {
        const existingKeys = new Set(
          current.map(
            (item) =>
              `${item.content_type}:${item.content.id}`,
          ),
        );

        const newItems = response.results.filter(
          (item) =>
            !existingKeys.has(
              `${item.content_type}:${item.content.id}`,
            ),
        );

        return [...current, ...newItems];
      });

      setCount(response.count);
      setNextUrl(response.next);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : 'Unable to load more favorites.',
      );
    } finally {
      setLoadingMore(false);
    }
  }, [
    activeTab,
    nextUrl,
    loadingMore,
    getFavorites,
  ]);

  const removeFavoriteFromList = useCallback(
    (
      contentType: FavoriteContentType,
      id: number,
    ) => {
      setFavorites((current) => {
        const exists = current.some(
          (item) =>
            item.content_type === contentType &&
            item.content.id === id,
        );

        if (!exists) {
          return current;
        }

        setCount((currentCount) =>
          Math.max(0, currentCount - 1),
        );

        return current.filter(
          (item) =>
            !(
              item.content_type === contentType &&
              item.content.id === id
            ),
        );
      });
    },
    [],
  );

  const renderFavorite = (item: FavoriteItem) => {
    if (isCommunityPost(item)) {
      return (
        <div
          key={`community-${item.content.id}`}
          className="
            border-b border-light-border
            transition-colors
            dark:border-dark-border
          "
        >
          <MusicPost
            post={item.content as never}
          />
        </div>
      );
    }

    if (isEditorialArticle(item)) {
      return (
        <div
          key={`editorial-${item.content.id}`}
          className="
            border-b border-light-border
            transition-colors
            dark:border-dark-border
          "
        >
          <MusicEditorialPost
            article={
              item.content as unknown as MusicFeedEditorialArticle
            }
            onUnfavorited={() =>
              removeFavoriteFromList(
                'editorial',
                item.content.id,
              )
            }
          />
        </div>
      );
    }

    return null;
  };

  const activeTabInfo = TABS.find(
    (tab) => tab.value === activeTab,
  )!;

  return (
    <section
      aria-label="Your saved favorites"
      className="pb-8"
    >
      {/* Tab navigation */}
      <div
        className="
          sticky top-0 z-20
          border-y border-light-border
          bg-light-bg/95
          backdrop-blur-xl
          dark:border-dark-border
          dark:bg-dark-bg/95
        "
      >
        <div
          className="
            grid grid-cols-3
            px-3 sm:px-5
          "
          role="tablist"
          aria-label="Favorite categories"
        >
          {TABS.map((tab) => {
            const selected =
              activeTab === tab.value;

            const Icon = tab.icon;

            return (
              <button
                key={tab.value}
                type="button"
                role="tab"
                id={`favorites-tab-${tab.value}`}
                aria-selected={selected}
                aria-controls="favorites-tab-panel"
                onClick={() => changeTab(tab.value)}
                className={`
                  group relative
                  flex min-w-0
                  items-center justify-center
                  gap-2
                  px-1 py-4
                  text-sm font-semibold
                  transition-colors duration-200
                  focus:outline-none
                  focus-visible:ring-2
                  focus-visible:ring-inset
                  focus-visible:ring-brand-teal/50
                  sm:gap-2.5
                  sm:py-5
                  ${
                    selected
                      ? `
                        text-brand-teal-dark
                        dark:text-brand-teal-light
                      `
                      : `
                        text-light-text-soft
                        hover:text-light-text
                        dark:text-dark-text-soft
                        dark:hover:text-dark-text
                      `
                  }
                `}
              >
                <Icon
                  className={`
                    h-[17px] w-[17px] shrink-0
                    transition-transform duration-200
                    ${
                      selected
                        ? 'scale-105'
                        : 'group-hover:scale-105'
                    }
                  `}
                  strokeWidth={selected ? 2.3 : 1.8}
                  aria-hidden="true"
                />

                <span className="truncate">
                  {tab.label}
                </span>

                {/* Persistent active indicator */}
                <span
                  aria-hidden="true"
                  className={`
                    absolute inset-x-2 bottom-0
                    h-[3px] rounded-t-full
                    bg-brand-teal
                    transition-all duration-200
                    ${
                      selected
                        ? 'scale-x-100 opacity-100'
                        : 'scale-x-50 opacity-0'
                    }
                  `}
                />
              </button>
            );
          })}
        </div>
      </div>

      {/* Feed heading */}
      <div
        className="
          flex items-center justify-between
          gap-3
          px-4 pb-3 pt-5
          sm:px-5 sm:pt-6
        "
      >
        <div className="min-w-0">
          <h2
            className="
              text-base font-bold
              tracking-tight
              text-light-text
              dark:text-dark-text
            "
          >
            {activeTabInfo.description}
          </h2>

          <p
            className="
              mt-1 text-xs
              text-light-text-soft
              dark:text-dark-text-soft
            "
          >
            {loading
              ? 'Updating your collection…'
              : `${count.toLocaleString()} ${
                  count === 1 ? 'saved item' : 'saved items'
                }`}
          </p>
        </div>

        <div
          className="
            flex h-10 w-10 shrink-0
            items-center justify-center
            rounded-xl
            bg-brand-teal/10
            text-brand-teal-dark
            dark:bg-brand-teal/15
            dark:text-brand-teal-light
          "
          aria-hidden="true"
        >
          <Bookmark
            className="h-5 w-5"
            strokeWidth={1.8}
          />
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div
          role="alert"
          className="
            mx-4 mb-4 rounded-xl
            border border-red-200
            bg-red-50 p-4
            dark:border-red-900/70
            dark:bg-red-950/40
            sm:mx-5
          "
        >
          <p
            className="
              text-sm font-medium
              text-red-700
              dark:text-red-300
            "
          >
            {error}
          </p>

          <button
            type="button"
            onClick={() => {
              setLoadedTab(
                (current) =>
                  current === activeTab
                    ? 'all'
                    : current,
              );
              void changeTab(activeTab);
            }}
            className="
              mt-2 inline-flex items-center gap-1.5
              text-sm font-semibold
              text-red-700 underline
              underline-offset-4
              dark:text-red-300
            "
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </button>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div
          className="space-y-4 px-4 py-4 sm:px-5"
          role="status"
          aria-live="polite"
        >
          <span className="sr-only">
            Loading favorites
          </span>

          {[1, 2].map((item) => (
            <div
              key={item}
              className="
                animate-pulse
                rounded-2xl
                border border-light-border
                p-4
                dark:border-dark-border
              "
            >
              <div className="flex items-center gap-3">
                <div
                  className="
                    h-10 w-10 rounded-xl
                    bg-light-border
                    dark:bg-dark-border
                  "
                />

                <div className="flex-1 space-y-2">
                  <div
                    className="
                      h-3 w-32 rounded-full
                      bg-light-border
                      dark:bg-dark-border
                    "
                  />

                  <div
                    className="
                      h-2.5 w-20 rounded-full
                      bg-light-border
                      dark:bg-dark-border
                    "
                  />
                </div>
              </div>

              <div
                className="
                  mt-5 h-4 w-4/5 rounded-full
                  bg-light-border
                  dark:bg-dark-border
                "
              />

              <div
                className="
                  mt-3 h-3 w-full rounded-full
                  bg-light-border
                  dark:bg-dark-border
                "
              />

              <div
                className="
                  mt-2 h-3 w-3/5 rounded-full
                  bg-light-border
                  dark:bg-dark-border
                "
              />
            </div>
          ))}
        </div>
      ) : favorites.length > 0 ? (
        <div
          id="favorites-tab-panel"
          role="tabpanel"
          aria-labelledby={`favorites-tab-${activeTab}`}
          aria-busy={loadingMore}
        >
          <div>
            {favorites.map(renderFavorite)}
          </div>

          {nextUrl && (
            <div
              className="
                flex justify-center
                px-4 py-7
                sm:px-5
              "
            >
              <button
                type="button"
                onClick={loadNextPage}
                disabled={loadingMore}
                className="
                  inline-flex min-w-40
                  items-center justify-center
                  gap-2 rounded-xl
                  border border-light-border
                  bg-light-card
                  px-5 py-3
                  text-sm font-semibold
                  text-light-text
                  transition-all duration-200
                  hover:border-brand-teal/40
                  hover:bg-brand-teal/5
                  disabled:cursor-not-allowed
                  disabled:opacity-60
                  dark:border-dark-border
                  dark:bg-dark-card
                  dark:text-dark-text
                  dark:hover:border-brand-teal/40
                  dark:hover:bg-brand-teal/10
                "
              >
                {loadingMore ? (
                  <>
                    <RefreshCw
                      className="h-4 w-4 animate-spin"
                    />
                    Loading more
                  </>
                ) : (
                  'Load more'
                )}
              </button>
            </div>
          )}
        </div>
      ) : (
        !error && (
          <div
            id="favorites-tab-panel"
            role="tabpanel"
            aria-labelledby={`favorites-tab-${activeTab}`}
            className="
              mx-4 my-4
              rounded-2xl
              border border-dashed
              border-light-border
              px-5 py-14
              text-center
              dark:border-dark-border
              sm:mx-5 sm:py-16
            "
          >
            <div
              className="
                mx-auto flex h-14 w-14
                items-center justify-center
                rounded-2xl
                bg-brand-teal/10
                text-brand-teal-dark
                dark:bg-brand-teal/15
                dark:text-brand-teal-light
              "
            >
              <Bookmark
                className="h-7 w-7"
                strokeWidth={1.5}
              />
            </div>

            <h3
              className="
                mt-5 text-lg font-bold
                tracking-tight
                text-light-text
                dark:text-dark-text
              "
            >
              {activeTab === 'community_post'
                ? 'No community favorites yet'
                : activeTab === 'editorial'
                  ? 'No editorial favorites yet'
                  : 'Your collection starts here'}
            </h3>

            <p
              className="
                mx-auto mt-2 max-w-xs
                text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
              "
            >
              {activeTab === 'community_post'
                ? 'Save posts from the music community and they will be waiting for you here.'
                : activeTab === 'editorial'
                  ? 'Bookmark music editorial articles to keep the stories you love close.'
                  : 'When you favorite a community post or editorial article, you will find it here.'}
            </p>
          </div>
        )
      )}
    </section>
  );
}
