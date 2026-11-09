'use client';

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from 'react';

import Image from 'next/image';
import Link from 'next/link';

import {
  Search,
  X,
  Users,
  Newspaper,
  Music2,
  Disc3,
  Mic2,
  ArrowUpRight,
  LoaderCircle,
  CheckCircle2,
  Clock3,
} from 'lucide-react';

import MusicNavigation from '@/components/music/MusicNavigation';
import MusicPost from '@/components/music/CommunityPost';
import MusicEditorialPost from '@/components/music/MusicEditorialPost';

import {
  getGlobalSearch,
  type GlobalSearchCategory,
  type GlobalSearchCategoryPage,
  type GlobalSearchResults,
} from '@/lib/music/GlobalSearch';

import type {
  CommunitySong,
  CommunityAlbum,
  CommunityArtist,
  CommunityUser,
} from '@/lib/music/CommunityPosts';

import type {
  MusicFeedEditorialArticle,
} from '@/lib/music/MusicFeed';

import { getMediaUrl } from '@/lib/api';
import VerificationBadge from '@/components/Icons';

// ========================================================
// Types
// ========================================================

type SearchTab =
  | 'all'
  | Exclude<GlobalSearchCategory, 'community_posts'>;

type SearchResultState = {
  query: string;
  results: GlobalSearchResults;
};

type CategoryConfig = {
  id: SearchTab;
  label: string;
  icon: typeof Search;
};

type UserSuggestionState = {
  query: string;
  users: CommunityUser[];
};

type SearchHistoryItem = {
  query: string;
  searchedAt: number;
};

type InfiniteLoadTriggerProps = {
  page: GlobalSearchCategoryPage<unknown>;
  loading: boolean;
  error?: string;
  onLoadMore: () => void;
};

// ========================================================
// Constants
// ========================================================

const PAGE_SIZE = 20;
const USER_SUGGESTION_LIMIT = 6;
const MAX_SEARCH_HISTORY = 10;
const MATCHING_HISTORY_LIMIT = 5;

const SEARCH_HISTORY_STORAGE_KEY =
  'vibenationhq_recent_searches';

const TOP_FEED_ORDER: GlobalSearchCategory[] = [
  'community_posts',
  'users',
  'editorial_articles',
  'songs',
  'albums',
  'artists',
];

const SEARCH_TABS: CategoryConfig[] = [
  {
    id: 'all',
    label: 'Top',
    icon: Search,
  },
  {
    id: 'users',
    label: 'Users',
    icon: Users,
  },
  {
    id: 'editorial_articles',
    label: 'Articles',
    icon: Newspaper,
  },
  {
    id: 'songs',
    label: 'Songs',
    icon: Music2,
  },
  {
    id: 'albums',
    label: 'Albums',
    icon: Disc3,
  },
  {
    id: 'artists',
    label: 'Artists',
    icon: Mic2,
  },
];

const EMPTY_PAGE: GlobalSearchCategoryPage<never> = {
  count: 0,
  page: 1,
  page_size: PAGE_SIZE,
  has_next: false,
  has_previous: false,
  next: null,
  previous: null,
  results: [],
};

const EMPTY_RESULTS: GlobalSearchResults = {
  users: { ...EMPTY_PAGE },
  community_posts: { ...EMPTY_PAGE },
  editorial_articles: { ...EMPTY_PAGE },
  songs: { ...EMPTY_PAGE },
  albums: { ...EMPTY_PAGE },
  artists: { ...EMPTY_PAGE },
};

// ========================================================
// Page
// ========================================================

export default function MusicSearchPage() {
  const [query, setQuery] = useState('');

  const [activeTab, setActiveTab] =
    useState<SearchTab>('all');

  const [searchState, setSearchState] =
    useState<SearchResultState | null>(null);

  const [loading, setLoading] = useState(false);

  const [searchError, setSearchError] =
    useState<string | null>(null);

  const [loadingMore, setLoadingMore] =
    useState<Partial<Record<GlobalSearchCategory, boolean>>>(
      {},
    );

  const [loadMoreErrors, setLoadMoreErrors] =
    useState<Partial<Record<GlobalSearchCategory, string>>>(
      {},
    );

  const [initialized, setInitialized] = useState(false);

  // Search history
  const [searchHistory, setSearchHistory] =
    useState<SearchHistoryItem[]>([]);

  // Live user suggestions
  const [userSuggestions, setUserSuggestions] =
    useState<UserSuggestionState | null>(null);

  const [loadingSuggestions, setLoadingSuggestions] =
    useState(false);

  // Dropdown visibility
  const [isSearchFocused, setIsSearchFocused] =
    useState(false);

  const abortControllerRef =
    useRef<AbortController | null>(null);

  const suggestionAbortControllerRef =
    useRef<AbortController | null>(null);

  const requestVersionRef = useRef(0);

  const initialSearchHandledRef = useRef(false);

  // Prevent duplicate pagination requests.
  const paginationRequestsRef = useRef<Set<string>>(
    new Set(),
  );

  const trimmedQuery = query.trim();

  const results = searchState?.results ?? EMPTY_RESULTS;

  // Only display full results for the exact submitted query.
  const hasCurrentSearch =
    Boolean(searchState) &&
    searchState?.query === trimmedQuery;

  // ------------------------------------------------------
  // Search history storage
  // ------------------------------------------------------

  const persistSearchHistory = useCallback(
    (history: SearchHistoryItem[]) => {
      try {
        window.localStorage.setItem(
          SEARCH_HISTORY_STORAGE_KEY,
          JSON.stringify(history),
        );
      } catch {
        // Search history is optional.
      }
    },
    [],
  );

  const saveSearchHistory = useCallback(
    (searchQuery: string) => {
      const normalizedQuery = searchQuery.trim();

      if (!normalizedQuery) {
        return;
      }

      setSearchHistory((previous) => {
        const normalized = normalizedQuery.toLowerCase();

        const updated: SearchHistoryItem[] = [
          {
            query: normalizedQuery,
            searchedAt: Date.now(),
          },
          ...previous.filter(
            (item) =>
              item.query.toLowerCase() !== normalized,
          ),
        ].slice(0, MAX_SEARCH_HISTORY);

        persistSearchHistory(updated);

        return updated;
      });
    },
    [persistSearchHistory],
  );

  const removeSearchHistoryItem = useCallback(
    (historyQuery: string) => {
      setSearchHistory((previous) => {
        const normalized = historyQuery.toLowerCase();

        const updated = previous.filter(
          (item) =>
            item.query.toLowerCase() !== normalized,
        );

        persistSearchHistory(updated);

        return updated;
      });
    },
    [persistSearchHistory],
  );

  const clearSearchHistory = useCallback(() => {
    setSearchHistory([]);

    try {
      window.localStorage.removeItem(
        SEARCH_HISTORY_STORAGE_KEY,
      );
    } catch {
      // The visible history is still cleared.
    }
  }, []);

  const filteredRecentSearches = useMemo(() => {
    if (!trimmedQuery) {
      return searchHistory.slice(0, MAX_SEARCH_HISTORY);
    }

    const normalizedQuery = trimmedQuery.toLowerCase();

    return searchHistory
      .filter((item) =>
        item.query.toLowerCase().includes(normalizedQuery),
      )
      .slice(0, MATCHING_HISTORY_LIMIT);
  }, [searchHistory, trimmedQuery]);

  // ------------------------------------------------------
  // Read initial URL and local search history
  // ------------------------------------------------------

  useEffect(() => {
    const params = new URLSearchParams(
      window.location.search,
    );

    const initialQuery = params.get('q') ?? '';

    if (initialQuery) {
      setQuery(initialQuery);
    }

    try {
      const storedHistory = window.localStorage.getItem(
        SEARCH_HISTORY_STORAGE_KEY,
      );

      if (storedHistory) {
        const parsed = JSON.parse(storedHistory);

        if (Array.isArray(parsed)) {
          const validHistory = parsed
            .filter(
              (item): item is SearchHistoryItem =>
                typeof item?.query === 'string' &&
                typeof item?.searchedAt === 'number',
            )
            .slice(0, MAX_SEARCH_HISTORY);

          setSearchHistory(validHistory);
        }
      }
    } catch {
      setSearchHistory([]);
    }

    setInitialized(true);
  }, []);

  // ------------------------------------------------------
  // URL synchronization
  // ------------------------------------------------------

  const updateSearchUrl = useCallback(
    (value: string) => {
      const params = new URLSearchParams(
        window.location.search,
      );

      if (value.trim()) {
        params.set('q', value.trim());
      } else {
        params.delete('q');
      }

      const queryString = params.toString();

      const nextUrl = queryString
        ? `${window.location.pathname}?${queryString}`
        : window.location.pathname;

      window.history.replaceState(
        window.history.state,
        '',
        nextUrl,
      );
    },
    [],
  );

  // ------------------------------------------------------
  // Full search request
  // ------------------------------------------------------

  const performSearch = useCallback(
    async (
      searchQuery: string,
      signal?: AbortSignal,
    ) => {
      const normalizedQuery = searchQuery.trim();

      if (!normalizedQuery) {
        return;
      }

      const requestVersion =
        ++requestVersionRef.current;

      setLoading(true);
      setSearchError(null);
      setSearchState(null);
      setLoadMoreErrors({});
      setLoadingMore({});

      try {
        const response = await getGlobalSearch({
          query: normalizedQuery,
          type: 'all',
          pageSize: PAGE_SIZE,
          signal,
        });

        if (
          signal?.aborted ||
          requestVersion !== requestVersionRef.current
        ) {
          return;
        }

        setSearchState({
          query: normalizedQuery,
          results: response.results,
        });
      } catch (error) {
        if (
          signal?.aborted ||
          requestVersion !== requestVersionRef.current
        ) {
          return;
        }

        setSearchState(null);

        setSearchError(
          error instanceof Error
            ? error.message
            : 'Something went wrong. Please try again.',
        );
      } finally {
        if (
          !signal?.aborted &&
          requestVersion === requestVersionRef.current
        ) {
          setLoading(false);
        }
      }
    },
    [],
  );

  // ------------------------------------------------------
  // Run initial search from URL
  // ------------------------------------------------------

  useEffect(() => {
    if (
      !initialized ||
      initialSearchHandledRef.current
    ) {
      return;
    }

    initialSearchHandledRef.current = true;

    const params = new URLSearchParams(
      window.location.search,
    );

    const initialQuery = params.get('q')?.trim();

    if (initialQuery) {
      void performSearch(initialQuery);
    }
  }, [initialized, performSearch]);

  // ------------------------------------------------------
  // Live user suggestions while typing
  // ------------------------------------------------------

  useEffect(() => {
    if (!initialized) {
      return;
    }

    suggestionAbortControllerRef.current?.abort();

    setUserSuggestions(null);
    setLoadingSuggestions(false);

    if (trimmedQuery.length < 2) {
      return;
    }

    const controller = new AbortController();

    suggestionAbortControllerRef.current = controller;

    const timeout = window.setTimeout(async () => {
      setLoadingSuggestions(true);

      try {
        const response = await getGlobalSearch({
          query: trimmedQuery,
          type: 'users',
          pageSize: USER_SUGGESTION_LIMIT,
          signal: controller.signal,
        });

        if (controller.signal.aborted) {
          return;
        }

        setUserSuggestions({
          query: trimmedQuery,
          users: response.results.users.results.slice(
            0,
            USER_SUGGESTION_LIMIT,
          ),
        });
      } catch {
        if (!controller.signal.aborted) {
          setUserSuggestions({
            query: trimmedQuery,
            users: [],
          });
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoadingSuggestions(false);
        }
      }
    }, 250);

    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [trimmedQuery, initialized]);

  // ------------------------------------------------------
  // Search form
  // ------------------------------------------------------

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!trimmedQuery) {
      return;
    }

    suggestionAbortControllerRef.current?.abort();
    abortControllerRef.current?.abort();

    const controller = new AbortController();

    abortControllerRef.current = controller;

    setIsSearchFocused(false);

    saveSearchHistory(trimmedQuery);
    updateSearchUrl(trimmedQuery);

    void performSearch(trimmedQuery, controller.signal);
  }

  // ------------------------------------------------------
  // Select a previous search
  // ------------------------------------------------------

  function handleHistorySearch(
    historyQuery: string,
  ) {
    suggestionAbortControllerRef.current?.abort();
    abortControllerRef.current?.abort();

    const controller = new AbortController();

    abortControllerRef.current = controller;

    setQuery(historyQuery);
    setIsSearchFocused(false);

    saveSearchHistory(historyQuery);
    updateSearchUrl(historyQuery);

    void performSearch(historyQuery, controller.signal);
  }

  // ------------------------------------------------------
  // Clear search
  // ------------------------------------------------------

  function handleClearSearch() {
    abortControllerRef.current?.abort();
    suggestionAbortControllerRef.current?.abort();

    requestVersionRef.current += 1;

    setQuery('');
    setSearchState(null);
    setSearchError(null);
    setLoading(false);
    setLoadingSuggestions(false);
    setUserSuggestions(null);
    setLoadingMore({});
    setLoadMoreErrors({});
    setActiveTab('all');
    setIsSearchFocused(true);

    updateSearchUrl('');
  }

  // ------------------------------------------------------
  // Input changes
  // ------------------------------------------------------

  function handleQueryChange(value: string) {
    setQuery(value);

    // Hide old full results while the user is editing.
    setSearchError(null);
  }

  // ------------------------------------------------------
  // Independent category pagination
  // ------------------------------------------------------

  const loadMore = useCallback(
    async (category: GlobalSearchCategory) => {
      if (!searchState) {
        return;
      }

      const requestedVersion = requestVersionRef.current;
      const requestedQuery = searchState.query;

      const currentPage =
        searchState.results[category];

      if (!currentPage.has_next) {
        return;
      }

      const requestKey =
        `${requestedVersion}:${category}`;

      if (paginationRequestsRef.current.has(requestKey)) {
        return;
      }

      const nextPage = currentPage.page + 1;

      paginationRequestsRef.current.add(requestKey);

      setLoadingMore((previous) => ({
        ...previous,
        [category]: true,
      }));

      setLoadMoreErrors((previous) => ({
        ...previous,
        [category]: undefined,
      }));

      try {
        const response = await getGlobalSearch({
          query: requestedQuery,
          type: category,
          pageSize: PAGE_SIZE,
          pages: {
            [category]: nextPage,
          },
        });

        // Ignore pagination responses from an older search.
        if (
          requestedVersion !== requestVersionRef.current
        ) {
          return;
        }

        const nextCategoryPage =
          response.results[category];

        setSearchState((previous) => {
          if (
            !previous ||
            previous.query !== requestedQuery ||
            requestedVersion !== requestVersionRef.current
          ) {
            return previous;
          }

          const existingPage =
            previous.results[category];

          // Prevent an older page from replacing newer data.
          if (
            existingPage.page >= nextCategoryPage.page
          ) {
            return previous;
          }

          const existingIds = new Set(
            existingPage.results.map((item) => item.id),
          );

          const newResults =
            nextCategoryPage.results.filter(
              (item) => !existingIds.has(item.id),
            );

          return {
            ...previous,
            results: {
              ...previous.results,
              [category]: {
                ...nextCategoryPage,
                results: [
                  ...existingPage.results,
                  ...newResults,
                ],
              },
            },
          };
        });
      } catch (error) {
        if (
          requestedVersion !== requestVersionRef.current
        ) {
          return;
        }

        setLoadMoreErrors((previous) => ({
          ...previous,
          [category]:
            error instanceof Error
              ? error.message
              : 'Could not load more results.',
        }));
      } finally {
        paginationRequestsRef.current.delete(requestKey);

        if (
          requestedVersion === requestVersionRef.current
        ) {
          setLoadingMore((previous) => ({
            ...previous,
            [category]: false,
          }));
        }
      }
    },
    [searchState],
  );

  // ------------------------------------------------------
  // Derived state
  // ------------------------------------------------------

  const activeResultCount =
    activeTab === 'all'
      ? TOP_FEED_ORDER.reduce(
          (total, category) =>
            total + results[category].count,
          0,
        )
      : results[activeTab].count;

  const isSearching =
    loading && !hasCurrentSearch;

  const showNoResults =
    hasCurrentSearch &&
    !loading &&
    activeResultCount === 0;

  const showSuggestions =
    isSearchFocused &&
    (
      Boolean(trimmedQuery) ||
      searchHistory.length > 0
    );

  const currentUserSuggestions =
    userSuggestions?.query === trimmedQuery
      ? userSuggestions.users
      : [];

  // ------------------------------------------------------
  // Render
  // ------------------------------------------------------

  return (
    <main
      className="
        min-h-screen
        bg-light-bg
        text-light-text
        dark:bg-dark-bg
        dark:text-dark-text
      "
    >
      <MusicNavigation />

      <div
        className="
          mx-auto
          w-full max-w-5xl
          px-3 py-5
          sm:px-5 sm:py-8
          lg:px-8
        "
      >
        {/* Search field and suggestion panel */}
        <form
          onSubmit={handleSubmit}
          className="relative z-30 mb-5 sm:mb-6"
          role="search"
        >
          <div
            className="
              flex items-center gap-3
              rounded-2xl
              border border-light-border
              bg-light-surface
              px-4
              shadow-sm
              transition-colors
              focus-within:border-brand-teal
              dark:border-dark-border
              dark:bg-dark-surface
              dark:focus-within:border-brand-teal
            "
          >
            <Search
              className="
                h-5 w-5 shrink-0
                text-light-text-soft
                dark:text-dark-text-soft
              "
            />

            <input
                type="search"
                value={query}
                onChange={(event) =>
                    handleQueryChange(event.target.value)
                }
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => {
                    window.setTimeout(() => {
                    setIsSearchFocused(false);
                    }, 150);
                }}
                placeholder="Search people, songs, artists, posts..."
                aria-label="Search VibeNationHQ"
                autoComplete="off"
                aria-autocomplete="list"
                className="
                    h-12 min-w-0 flex-1
                    appearance-none
                    border-0
                    bg-transparent
                    text-sm font-medium
                    text-light-text
                    outline-none
                    ring-0
                    shadow-none
                    placeholder:font-normal
                    placeholder:text-light-text-soft
                    focus:border-0
                    focus:outline-none
                    focus:ring-0
                    focus:shadow-none
                    dark:text-dark-text
                    dark:placeholder:text-dark-text-soft
                    sm:text-base
                "
                />

            {query && (
              <button
                type="button"
                onClick={handleClearSearch}
                aria-label="Clear search"
                className="
                  flex h-8 w-8 shrink-0
                  items-center justify-center
                  rounded-full
                  text-light-text-soft
                  transition-colors
                  hover:bg-light-surface-soft
                  hover:text-light-text
                  dark:text-dark-text-soft
                  dark:hover:bg-dark-surface-soft
                  dark:hover:text-dark-text
                "
              >
                <X className="h-4 w-4" />
              </button>
            )}

            <button
              type="submit"
              disabled={!trimmedQuery}
              className="
                hidden shrink-0
                rounded-xl
                bg-brand-teal
                px-5 py-2
                text-sm font-bold text-white
                transition-opacity
                hover:opacity-90
                disabled:cursor-not-allowed
                disabled:opacity-50
                sm:block
              "
            >
              Search
            </button>
          </div>

          {/* Suggestions dropdown */}
          {showSuggestions && (
            <div
              className="
                absolute left-0 right-0 top-[calc(100%+8px)]
                z-50
                overflow-hidden
                rounded-2xl
                border border-light-border
                bg-light-surface
                shadow-xl
                dark:border-dark-border
                dark:bg-dark-surface
              "
              onMouseDown={(event) =>
                event.preventDefault()
              }
            >
              {/* Recent searches */}
              {filteredRecentSearches.length > 0 && (
                <div className="p-3">
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <h3
                      className="
                        text-[11px] font-bold uppercase tracking-wider
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Recent searches
                    </h3>

                    <button
                      type="button"
                      onClick={clearSearchHistory}
                      className="
                        rounded-md px-2 py-1
                        text-[11px] font-semibold
                        text-light-text-soft
                        transition-colors
                        hover:bg-light-surface-soft
                        hover:text-red-500
                        dark:text-dark-text-soft
                        dark:hover:bg-dark-surface-soft
                        dark:hover:text-red-400
                      "
                    >
                      Clear all
                    </button>
                  </div>

                  <div className="space-y-1">
                    {filteredRecentSearches.map((item) => (
                      <div
                        key={`${item.query}-${item.searchedAt}`}
                        className="
                          flex min-w-0 items-center gap-2
                          rounded-xl
                          transition-colors
                          hover:bg-light-surface-soft
                          dark:hover:bg-dark-surface-soft
                        "
                      >
                        <button
                          type="button"
                          onClick={() =>
                            handleHistorySearch(item.query)
                          }
                          className="
                            flex min-w-0 flex-1 items-center gap-3
                            px-3 py-2.5
                            text-left
                          "
                        >
                          <Clock3
                            className="
                              h-4 w-4 shrink-0
                              text-light-text-soft
                              dark:text-dark-text-soft
                            "
                          />

                          <span className="min-w-0 flex-1 truncate text-sm font-medium">
                            {item.query}
                          </span>

                          <ArrowUpRight
                            className="
                              h-3.5 w-3.5 shrink-0
                              text-light-text-soft
                              dark:text-dark-text-soft
                            "
                          />
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            removeSearchHistoryItem(item.query)
                          }
                          aria-label={`Remove ${item.query} from recent searches`}
                          title="Remove from history"
                          className="
                            mr-2 flex h-7 w-7 shrink-0
                            items-center justify-center
                            rounded-full
                            text-light-text-soft
                            transition-colors
                            hover:bg-light-border
                            hover:text-red-500
                            dark:text-dark-text-soft
                            dark:hover:bg-dark-border
                            dark:hover:text-red-400
                          "
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(filteredRecentSearches.length > 0 ||
                currentUserSuggestions.length > 0 ||
                loadingSuggestions) && (
                <div className="border-t border-light-border dark:border-dark-border" />
              )}

              {/* Matching users */}
              <div className="p-3">
                {loadingSuggestions && (
                  <div className="mb-2 flex justify-end">
                    <LoaderCircle className="h-3.5 w-3.5 animate-spin text-brand-teal" />
                  </div>
                )}

                {currentUserSuggestions.length > 0 ? (
                  <div className="space-y-1">
                    {currentUserSuggestions.map((user) => (
                      <UserSuggestionRow
                        key={user.id}
                        user={user}
                      />
                    ))}
                  </div>
                ) : loadingSuggestions ? (
                  <p className="px-3 py-3 text-xs text-light-text-muted dark:text-dark-text-muted">
                    Finding matching people...
                  </p>
                ) : trimmedQuery.length >= 2 ? (
                  <p className="px-3 py-3 text-xs text-light-text-muted dark:text-dark-text-muted">
                    No matching people found.
                  </p>
                ) : trimmedQuery.length > 0 ? (
                  <p className="px-3 py-3 text-xs text-light-text-muted dark:text-dark-text-muted">
                    Type at least 2 characters to find people.
                  </p>
                ) : null}
              </div>

              {/* Search hint */}
              {trimmedQuery && (
                <button
                  type="submit"
                  className="
                    flex w-full items-center gap-3
                    border-t border-light-border
                    bg-light-surface-soft
                    px-4 py-3
                    text-left
                    transition-colors
                    hover:bg-brand-teal/5
                    dark:border-dark-border
                    dark:bg-dark-surface-soft
                    dark:hover:bg-brand-teal/10
                  "
                >
                  <Search className="h-4 w-4 shrink-0 text-brand-teal" />

                  <span className="min-w-0 flex-1 truncate text-xs font-semibold">
                    Search for &quot;{trimmedQuery}&quot;
                  </span>

                  <span className="text-[10px] text-light-text-soft dark:text-dark-text-soft">
                    Enter
                  </span>
                </button>
              )}
            </div>
          )}
        </form>

        {/* Category tabs */}
        <nav
          aria-label="Search categories"
          className="
            relative z-10
            mb-5
            rounded-2xl
            border border-light-border
            bg-light-surface
            p-1.5
            dark:border-dark-border
            dark:bg-dark-surface
            sm:mb-6
            sm:p-2
          "
        >
          <div className="grid grid-cols-6 gap-1">
            {SEARCH_TABS.map((tab) => {
              const Icon = tab.icon;
              const selected = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  aria-pressed={selected}
                  className={`
                    flex min-w-0
                    flex-col items-center
                    justify-center
                    gap-1
                    rounded-xl
                    px-0.5 py-2.5
                    text-[9px] font-bold
                    leading-tight
                    transition-colors
                    min-[380px]:text-[10px]
                    sm:flex-row sm:gap-2
                    sm:px-2 sm:py-3
                    sm:text-xs
                    ${
                      selected
                        ? 'bg-brand-teal text-white shadow-sm'
                        : 'text-light-text-muted hover:bg-light-surface-soft hover:text-light-text dark:text-dark-text-muted dark:hover:bg-dark-surface-soft dark:hover:text-dark-text'
                    }
                  `}
                >
                  <Icon className="hidden h-4 w-4 shrink-0 sm:block" />

                  <span className="whitespace-nowrap">
                    {tab.label}
                  </span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Search status */}
        {hasCurrentSearch && trimmedQuery && loading && (
          <div className="mb-5 flex items-center justify-between gap-3">
            <span
              className="
                inline-flex items-center gap-2
                text-xs font-medium
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Searching
            </span>
          </div>
        )}

        {/* Initial state */}
        {!trimmedQuery && <SearchWelcome />}

        {/* Loading state */}
        {isSearching && <SearchLoading />}

        {/* Error state */}
        {searchError && !loading && (
          <SearchError
            message={searchError}
            onRetry={() => {
              const controller = new AbortController();

              abortControllerRef.current = controller;

              void performSearch(
                trimmedQuery,
                controller.signal,
              );
            }}
          />
        )}

        {/* Empty state */}
        {showNoResults && !searchError && (
          <SearchEmpty
            query={searchState?.query ?? query}
            activeTab={activeTab}
          />
        )}

        {/* Top combined results */}
        {hasCurrentSearch &&
          activeTab === 'all' &&
          !searchError &&
          activeResultCount > 0 && (
            <TopSearchResults
              results={results}
              loadingMore={loadingMore}
              loadMoreErrors={loadMoreErrors}
              onLoadMore={loadMore}
            />
          )}

        {/* Individual category results */}
        {hasCurrentSearch &&
          activeTab !== 'all' &&
          !searchError && (
            <CategoryResults
              category={activeTab}
              results={results}
              loadingMore={loadingMore}
              loadMoreErrors={loadMoreErrors}
              onLoadMore={loadMore}
            />
          )}
      </div>
    </main>
  );
}

// ========================================================
// Top combined search feed
// ========================================================

function TopSearchResults({
  results,
  loadingMore,
  loadMoreErrors,
  onLoadMore,
}: {
  results: GlobalSearchResults;
  loadingMore: Partial<Record<GlobalSearchCategory, boolean>>;
  loadMoreErrors: Partial<Record<GlobalSearchCategory, string>>;
  onLoadMore: (category: GlobalSearchCategory) => void;
}) {
  const visibleCategories = TOP_FEED_ORDER.filter(
    (category) => results[category].count > 0,
  );

  return (
    <div>
      {visibleCategories.map((category, index) => {
        const page = results[category];

        return (
          <section
            key={category}
            className={`
              min-w-0
              ${index > 0
                ? 'mt-6 border-t border-light-border pt-6 dark:border-dark-border'
                : ''
              }
            `}
          >
            <TopCategoryContent
              category={category}
              results={results}
            />

            <InfiniteLoadTrigger
              page={page}
              loading={Boolean(loadingMore[category])}
              error={loadMoreErrors[category]}
              onLoadMore={() => onLoadMore(category)}
            />
          </section>
        );
      })}
    </div>
  );
}

// ========================================================
// Top category content
// ========================================================

function TopCategoryContent({
  category,
  results,
}: {
  category: GlobalSearchCategory;
  results: GlobalSearchResults;
}) {
  switch (category) {
    case 'community_posts':
      return (
        <div
          className="
            divide-y divide-light-border
            overflow-hidden rounded-2xl
            border border-light-border
            bg-light-surface
            dark:divide-dark-border
            dark:border-dark-border
            dark:bg-dark-surface
          "
        >
          {results.community_posts.results.map((post) => (
            <MusicPost
              key={post.id}
              post={post}
              variant="feed"
            />
          ))}
        </div>
      );

    case 'users':
      return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {results.users.results.map((user) => (
            <UserResultCard
              key={user.id}
              user={user}
            />
          ))}
        </div>
      );

    case 'editorial_articles':
      return (
        <div
          className="
            divide-y divide-light-border
            overflow-hidden rounded-2xl
            border border-light-border
            bg-light-surface
            dark:divide-dark-border
            dark:border-dark-border
            dark:bg-dark-surface
          "
        >
          {results.editorial_articles.results.map(
            (article) => (
              <MusicEditorialPost
                key={article.id}
                article={article}
              />
            ),
          )}
        </div>
      );

    case 'songs':
      return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {results.songs.results.map((song) => (
            <SongResultCard
              key={song.id}
              song={song}
            />
          ))}
        </div>
      );

    case 'albums':
      return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {results.albums.results.map((album) => (
            <AlbumResultCard
              key={album.id}
              album={album}
            />
          ))}
        </div>
      );

    case 'artists':
      return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {results.artists.results.map((artist) => (
            <ArtistResultCard
              key={artist.id}
              artist={artist}
            />
          ))}
        </div>
      );

    default:
      return null;
  }
}

// ========================================================
// User suggestion row
// ========================================================

function UserSuggestionRow({
  user,
}: {
  user: CommunityUser;
}) {
  const profileUrl = getUserProfileUrl(user.username);
  const imageUrl = getMediaUrl(user.profile_image);

  return (
    <Link
      href={profileUrl}
      className="
        group flex min-w-0 items-center gap-3
        rounded-xl
        px-3 py-2.5
        transition-colors
        hover:bg-light-surface-soft
        dark:hover:bg-dark-surface-soft
      "
    >
      <div
        className="
          relative h-9 w-9 shrink-0
          overflow-hidden rounded-full
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      >
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt=""
            fill
            sizes="36px"
            className="object-cover"
          />
        ) : (
          <div
            className="
              flex h-full w-full
              items-center justify-center
              text-xs font-black
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            {getInitials(
              user.display_name || user.username,
            )}
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex min-w-0 items-center gap-1.5">
          <p className="truncate text-xs font-bold text-light-text group-hover:text-brand-teal-dark dark:text-dark-text dark:group-hover:text-brand-teal-light">
            {user.display_name || user.username}
          </p>

          <VerificationBadges user={user} />
        </div>

        <p className="mt-0.5 truncate text-[11px] text-light-text-muted dark:text-dark-text-muted">
          @{user.username}
        </p>
      </div>

      <ArrowUpRight className="h-3.5 w-3.5 shrink-0 text-light-text-soft dark:text-dark-text-soft" />
    </Link>
  );
}

// ========================================================
// Welcome state
// ========================================================

function SearchWelcome() {
  return (
    <div
      className="
        flex flex-col items-center
        rounded-3xl
        border border-dashed
        border-light-border
        bg-light-surface
        px-5 py-14
        text-center
        dark:border-dark-border
        dark:bg-dark-surface
        sm:py-20
      "
    >
      <div
        className="
          flex h-16 w-16
          items-center justify-center
          rounded-3xl
          bg-brand-teal/10
          text-brand-teal-dark
          dark:bg-brand-teal/15
          dark:text-brand-teal-light
        "
      >
        <Search className="h-7 w-7" />
      </div>

      <h2 className="mt-5 text-lg font-black">
        Find your next vibe
      </h2>

      <p
        className="
          mt-2 max-w-sm
          text-sm leading-6
          text-light-text-muted
          dark:text-dark-text-muted
        "
      >
        Search for people, artists, songs, albums,
        community conversations and music stories.
      </p>
    </div>
  );
}

// ========================================================
// Loading state
// ========================================================

function SearchLoading() {
  return (
    <div
      className="space-y-3"
      aria-label="Loading search results"
    >
      {Array.from({ length: 5 }).map((_, index) => (
        <div
          key={index}
          className="
            flex animate-pulse items-center gap-4
            rounded-2xl
            border border-light-border
            bg-light-surface
            p-4
            dark:border-dark-border
            dark:bg-dark-surface
          "
        >
          <div
            className="
              h-12 w-12 shrink-0
              rounded-2xl
              bg-light-surface-muted
              dark:bg-dark-surface-muted
            "
          />

          <div className="min-w-0 flex-1 space-y-2">
            <div
              className="
                h-3 w-2/5 rounded-full
                bg-light-surface-muted
                dark:bg-dark-surface-muted
              "
            />

            <div
              className="
                h-3 w-3/5 rounded-full
                bg-light-surface-muted
                dark:bg-dark-surface-muted
              "
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// ========================================================
// Error state
// ========================================================

function SearchError({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div
      className="
        rounded-2xl
        border border-red-200
        bg-red-50
        px-5 py-8
        text-center
        dark:border-red-900/50
        dark:bg-red-950/20
      "
    >
      <p className="text-sm font-semibold text-red-700 dark:text-red-400">
        {message}
      </p>

      <button
        type="button"
        onClick={onRetry}
        className="
          mt-4 rounded-xl
          bg-brand-teal
          px-4 py-2
          text-xs font-bold text-white
          hover:opacity-90
        "
      >
        Try again
      </button>
    </div>
  );
}

// ========================================================
// Empty state
// ========================================================

function SearchEmpty({
  query,
  activeTab,
}: {
  query: string;
  activeTab: SearchTab;
}) {
  const message =
    activeTab === 'all'
      ? 'We couldn’t find matching people, posts, articles, songs, albums or artists. Try another name or phrase.'
      : `We couldn't find any ${getCategoryTitle(activeTab).toLowerCase()} matching your search. Try another name or search term.`;

  return (
    <div
      className="
        rounded-3xl
        border border-light-border
        bg-light-surface
        px-5 py-14
        text-center
        dark:border-dark-border
        dark:bg-dark-surface
      "
    >
      <div
        className="
          mx-auto flex h-14 w-14
          items-center justify-center
          rounded-2xl
          bg-light-surface-soft
          text-light-text-soft
          dark:bg-dark-surface-soft
          dark:text-dark-text-soft
        "
      >
        <Search className="h-6 w-6" />
      </div>

      <h2 className="mt-4 text-base font-black">
        No results found
      </h2>

      <p
        className="
          mx-auto mt-2 max-w-sm
          text-sm leading-6
          text-light-text-muted
          dark:text-dark-text-muted
        "
      >
        {message}
      </p>

      <p className="mt-3 text-xs text-light-text-soft dark:text-dark-text-soft">
        Search: <span className="font-bold">“{query}”</span>
      </p>
    </div>
  );
}

// ========================================================
// User result
// ========================================================

function UserResultCard({
  user,
}: {
  user: CommunityUser;
}) {
  const profileUrl = getUserProfileUrl(user.username);
  const imageUrl = getMediaUrl(user.profile_image);

  return (
    <Link
      href={profileUrl}
      className="
        group flex min-w-0 items-center gap-3
        rounded-2xl
        border border-light-border
        bg-light-surface
        p-3
        transition-colors
        hover:border-brand-teal/40
        hover:bg-light-surface-soft
        dark:border-dark-border
        dark:bg-dark-surface
        dark:hover:border-brand-teal/40
        dark:hover:bg-dark-surface-soft
      "
    >
      <div
        className="
          relative h-12 w-12 shrink-0
          overflow-hidden rounded-full
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      >
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt=""
            fill
            unoptimized
            sizes="48px"
            className="object-cover"
          />
        ) : (
          <div
            className="
              flex h-full w-full
              items-center justify-center
              text-base font-black
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            {getInitials(
              user.display_name || user.username,
            )}
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex min-w-0 items-center gap-1.5">
          <p
            className="
              truncate text-sm font-bold
              text-light-text
              group-hover:text-brand-teal-dark
              dark:text-dark-text
              dark:group-hover:text-brand-teal-light
            "
          >
            {user.display_name || user.username}
          </p>

          <VerificationBadges user={user} />
        </div>

        <p
          className="
            mt-0.5 truncate text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          @{user.username}
        </p>
      </div>

      <ArrowUpRight
        className="
          h-4 w-4 shrink-0
          text-light-text-soft
          transition-transform
          group-hover:-translate-y-0.5
          group-hover:translate-x-0.5
          dark:text-dark-text-soft
        "
      />
    </Link>
  );
}

// ========================================================
// Verification badges
// ========================================================

function VerificationBadges({
  user,
}: {
  user: Pick<
    CommunityUser,
    'is_verified' | 'is_identity_verified'
  >;
}) {
  return (
    <span className="inline-flex shrink-0 items-center gap-0.5">
      {user.is_verified && (
        <VerificationBadge type="verified" size={16} />
      )}

      {user.is_identity_verified && (
        <VerificationBadge type="identity" size={16} />
      )}
    </span>
  );
}

// ========================================================
// Individual category results
// ========================================================

function CategoryResults({
  category,
  results,
  loadingMore,
  loadMoreErrors,
  onLoadMore,
}: {
  category: Exclude<
    GlobalSearchCategory,
    'community_posts'
  >;
  results: GlobalSearchResults;
  loadingMore: Partial<Record<GlobalSearchCategory, boolean>>;
  loadMoreErrors: Partial<Record<GlobalSearchCategory, string>>;
  onLoadMore: (category: GlobalSearchCategory) => void;
}) {
  const page = results[category];

  if (page.count === 0) {
    return (
      <SearchEmpty
        query="your search"
        activeTab={category}
      />
    );
  }

  return (
    <section>
      {/* Users */}
      {category === 'users' && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {(page.results as CommunityUser[]).map((user) => (
            <UserResultCard
              key={user.id}
              user={user}
            />
          ))}
        </div>
      )}

      {/* Editorial articles */}
      {category === 'editorial_articles' && (
        <div
          className="
            divide-y divide-light-border
            overflow-hidden rounded-2xl
            border border-light-border
            bg-light-surface
            dark:divide-dark-border
            dark:border-dark-border
            dark:bg-dark-surface
          "
        >
          {(page.results as MusicFeedEditorialArticle[]).map(
            (article) => (
              <MusicEditorialPost
                key={article.id}
                article={article}
              />
            ),
          )}
        </div>
      )}

      {/* Songs */}
      {category === 'songs' && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {(page.results as CommunitySong[]).map((song) => (
            <SongResultCard
              key={song.id}
              song={song}
            />
          ))}
        </div>
      )}

      {/* Albums */}
      {category === 'albums' && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {(page.results as CommunityAlbum[]).map((album) => (
            <AlbumResultCard
              key={album.id}
              album={album}
            />
          ))}
        </div>
      )}

      {/* Artists */}
      {category === 'artists' && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {(page.results as CommunityArtist[]).map((artist) => (
            <ArtistResultCard
              key={artist.id}
              artist={artist}
            />
          ))}
        </div>
      )}

      <InfiniteLoadTrigger
        page={page}
        loading={Boolean(loadingMore[category])}
        error={loadMoreErrors[category]}
        onLoadMore={() => onLoadMore(category)}
      />
    </section>
  );
}

// ========================================================
// Infinite loading trigger
// ========================================================

function InfiniteLoadTrigger({
  page,
  loading,
  error,
  onLoadMore,
}: InfiniteLoadTriggerProps) {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  // Remember which page has already triggered a request.
  const lastTriggeredPageRef = useRef<number | null>(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;

    if (
      !sentinel ||
      !page.has_next ||
      loading ||
      error
    ) {
      return;
    }

    if (
      lastTriggeredPageRef.current === page.page
    ) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];

        if (
          !entry?.isIntersecting ||
          lastTriggeredPageRef.current === page.page
        ) {
          return;
        }

        lastTriggeredPageRef.current = page.page;

        onLoadMore();
      },
      {
        root: null,
        rootMargin: '500px 0px',
        threshold: 0,
      },
    );

    observer.observe(sentinel);

    return () => {
      observer.disconnect();
    };
  }, [
    page.page,
    page.has_next,
    loading,
    error,
    onLoadMore,
  ]);

  if (!page.has_next && !loading && !error) {
    return null;
  }

  return (
    <div
      ref={sentinelRef}
      className="
        flex min-h-16
        flex-col items-center justify-center
        gap-2 py-4
      "
    >
      {loading && (
        <div
          className="
            inline-flex items-center gap-2
            text-xs font-medium
            text-brand-teal-dark
            dark:text-brand-teal-light
          "
        >
          <LoaderCircle className="h-4 w-4 animate-spin" />
          Loading more results...
        </div>
      )}

      {error && (
        <>
          <p
            role="alert"
            className="text-center text-xs text-red-600 dark:text-red-400"
          >
            {error}
          </p>

          <button
            type="button"
            onClick={onLoadMore}
            className="
              rounded-xl
              border border-light-border
              bg-light-surface
              px-4 py-2
              text-xs font-bold
              text-light-text
              transition-colors
              hover:border-brand-teal/40
              hover:bg-brand-teal/5
              dark:border-dark-border
              dark:bg-dark-surface
              dark:text-dark-text
              dark:hover:bg-brand-teal/10
            "
          >
            Try again
          </button>
        </>
      )}

      {!loading && !error && page.has_next && (
        <span className="text-[11px] text-light-text-soft dark:text-dark-text-soft">
          Scroll to load more
        </span>
      )}
    </div>
  );
}

// ========================================================
// Song result
// ========================================================

function SongResultCard({
  song,
}: {
  song: CommunitySong;
}) {
  const artwork = getMediaUrl(song.artwork);

  const artistNames = [
    ...song.artists.map((artist) => artist.name),
    ...song.featured_artists.map((artist) => artist.name),
  ].join(', ');

  return (
    <Link
      href={`/music/songs/${song.slug}`}
      className="
        group flex min-w-0 items-center gap-3
        rounded-2xl
        border border-light-border
        bg-light-surface p-3
        transition-colors
        hover:border-brand-teal/40
        hover:bg-light-surface-soft
        dark:border-dark-border
        dark:bg-dark-surface
        dark:hover:border-brand-teal/40
        dark:hover:bg-dark-surface-soft
      "
    >
      <ResultArtwork
        src={artwork}
        alt={song.title}
        icon={<Music2 className="h-5 w-5" />}
      />

      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-bold group-hover:text-brand-teal-dark dark:group-hover:text-brand-teal-light">
          {song.title}
        </p>

        <p className="mt-1 truncate text-xs text-light-text-muted dark:text-dark-text-muted">
          {artistNames || 'Unknown artist'}
        </p>

        <p className="mt-1 text-[11px] text-light-text-soft dark:text-dark-text-soft">
          {song.duration_display || 'Song'}
        </p>
      </div>

      <ArrowUpRight className="h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />
    </Link>
  );
}

// ========================================================
// Album result
// ========================================================

function AlbumResultCard({
  album,
}: {
  album: CommunityAlbum;
}) {
  const artwork = getMediaUrl(album.artwork);

  const artistNames = album.artists
    .map((artist) => artist.name)
    .join(', ');

  return (
    <Link
      href={`/music/albums/${album.slug}`}
      className="
        group flex min-w-0 items-center gap-3
        rounded-2xl
        border border-light-border
        bg-light-surface p-3
        transition-colors
        hover:border-brand-teal/40
        hover:bg-light-surface-soft
        dark:border-dark-border
        dark:bg-dark-surface
        dark:hover:border-brand-teal/40
        dark:hover:bg-dark-surface-soft
      "
    >
      <ResultArtwork
        src={artwork}
        alt={album.title}
        icon={<Disc3 className="h-5 w-5" />}
      />

      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-bold group-hover:text-brand-teal-dark dark:group-hover:text-brand-teal-light">
          {album.title}
        </p>

        <p className="mt-1 truncate text-xs text-light-text-muted dark:text-dark-text-muted">
          {artistNames || 'Unknown artist'}
        </p>

        <p className="mt-1 text-[11px] text-light-text-soft dark:text-dark-text-soft">
          {album.release_type || 'Album'}
        </p>
      </div>

      <ArrowUpRight className="h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />
    </Link>
  );
}

// ========================================================
// Artist result
// ========================================================

function ArtistResultCard({
  artist,
}: {
  artist: CommunityArtist;
}) {
  const imageUrl = getMediaUrl(artist.profile_image);

  return (
    <Link
      href={`/music/artists/${artist.slug}`}
      className="
        group flex min-w-0 items-center gap-3
        rounded-2xl
        border border-light-border
        bg-light-surface p-3
        transition-colors
        hover:border-brand-teal/40
        hover:bg-light-surface-soft
        dark:border-dark-border
        dark:bg-dark-surface
        dark:hover:border-brand-teal/40
        dark:hover:bg-dark-surface-soft
      "
    >
      <div
        className="
          relative h-12 w-12 shrink-0
          overflow-hidden rounded-full
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      >
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt=""
            fill
            unoptimized
            sizes="48px"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-brand-teal-dark dark:text-brand-teal-light">
            <Mic2 className="h-5 w-5" />
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex min-w-0 items-center gap-1.5">
          <p className="truncate text-sm font-bold group-hover:text-brand-teal-dark dark:group-hover:text-brand-teal-light">
            {artist.name}
          </p>

          {artist.is_verified && (
            <CheckCircle2
              className="h-4 w-4 shrink-0 text-blue-500"
              strokeWidth={2.4}
              aria-label="Verified artist"
            />
          )}
        </div>

        <p className="mt-1 text-xs text-light-text-muted dark:text-dark-text-muted">
          {formatCount(artist.followers_count)} followers
        </p>
      </div>

      <ArrowUpRight className="h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />
    </Link>
  );
}

// ========================================================
// Shared artwork
// ========================================================

function ResultArtwork({
  src,
  alt,
  icon,
}: {
  src: string | null;
  alt: string;
  icon: ReactNode;
}) {
  return (
    <div
      className="
        relative h-14 w-14 shrink-0
        overflow-hidden rounded-xl
        bg-light-surface-muted
        dark:bg-dark-surface-muted
      "
    >
      {src ? (
        <Image
          src={src}
          alt={`${alt} artwork`}
          fill
          unoptimized
          sizes="56px"
          className="object-cover"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-light-text-soft dark:text-dark-text-soft">
          {icon}
        </div>
      )}
    </div>
  );
}

// ========================================================
// Helpers
// ========================================================

function getCategoryTitle(
  category: SearchTab,
): string {
  const titles: Record<SearchTab, string> = {
    all: 'Top',
    users: 'People',
    editorial_articles: 'Articles',
    songs: 'Songs',
    albums: 'Albums',
    artists: 'Artists',
  };

  return titles[category];
}

function getUserProfileUrl(username: string): string {
  return `/account/${encodeURIComponent(username)}`;
}

function getInitials(value: string): string {
  const words = value.trim().split(/\s+/).filter(Boolean);

  if (words.length === 0) {
    return 'U';
  }

  return words
    .slice(0, 2)
    .map((word) => word.charAt(0))
    .join('')
    .toUpperCase();
}

function formatCount(count: number): string {
  if (count < 1000) {
    return String(count);
  }

  if (count < 1_000_000) {
    return `${formatCompactNumber(count / 1000)}K`;
  }

  if (count < 1_000_000_000) {
    return `${formatCompactNumber(count / 1_000_000)}M`;
  }

  return `${formatCompactNumber(count / 1_000_000_000)}B`;
}

function formatCompactNumber(value: number): string {
  if (value >= 100) {
    return Math.round(value).toString();
  }

  return value
    .toFixed(1)
    .replace('.0', '');
}