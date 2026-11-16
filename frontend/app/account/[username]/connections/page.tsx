
'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import {
  useParams,
  useRouter,
  useSearchParams,
} from 'next/navigation';
import {
  ArrowLeft,
  Check,
  CheckCircle2,
  Disc3,
  LoaderCircle,
  Music2,
  Search,
  Users,
  X,
} from 'lucide-react';

import { ApiError, apiRequest, getMediaUrl } from '@/lib/api';

import type {
  CommunityArtist,
} from '@/lib/music/CommunityPosts';

import {
  followCommunityUser,
  unfollowCommunityUser,
  followArtist,
  unfollowArtist,
} from '@/lib/music/CommunityPosts';

import { useAuth } from '@/components/auth/AuthProvider';
import HomeNav from '@/components/special/HomeNav';
import MusicNavigation from '@/components/music/MusicNavigation';

// ============================================================
// Types
// ============================================================

type ConnectionTab = 'followers' | 'following' | 'artists';

type PublicConnectionUser = {
  id: number;
  username: string;
  display_name: string | null;
  profile_image: string | null;
  is_verified: boolean;
  is_identity_verified: boolean;
  is_following: boolean;
};

type PublicConnectionArtist = CommunityArtist & {
  is_following: boolean;
};

type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

type ConnectionItem =
  | PublicConnectionUser
  | PublicConnectionArtist;

// ============================================================
// Constants
// ============================================================

const PAGE_SIZE = 12;
const SEARCH_DEBOUNCE_MS = 350;
const MAX_SEARCH_LENGTH = 100;

const CONNECTION_TABS: {
  id: ConnectionTab;
  label: string;
}[] = [
  {
    id: 'followers',
    label: 'Followers',
  },
  {
    id: 'following',
    label: 'Following',
  },
  {
    id: 'artists',
    label: 'Artists',
  },
];

// ============================================================
// Helpers
// ============================================================

function formatCount(value: number): string {
  if (value < 1000) {
    return value.toLocaleString();
  }

  if (value < 1_000_000) {
    return `${(value / 1000).toFixed(
      value >= 10_000 ? 0 : 1,
    )}K`;
  }

  return `${(value / 1_000_000).toFixed(
    value >= 10_000_000 ? 0 : 1,
  )}M`;
}

function getInitials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();
}

function isConnectionUser(
  item: ConnectionItem,
): item is PublicConnectionUser {
  return 'username' in item;
}

// ============================================================
// Verification badges
// ============================================================

function VerificationBadges({
  isVerified,
  isIdentityVerified,
}: {
  isVerified: boolean;
  isIdentityVerified: boolean;
}) {
  return (
    <span className="inline-flex shrink-0 items-center gap-1">
      {isVerified && (
        <CheckCircle2
          aria-label="Verified account"
          title="Verified account"
          className="h-4 w-4 shrink-0 fill-blue-500 text-white sm:h-[18px] sm:w-[18px]"
        />
      )}

      {isIdentityVerified && (
        <CheckCircle2
          aria-label="Identity verified"
          title="Identity verified"
          className="h-4 w-4 shrink-0 fill-brand-teal text-white sm:h-[18px] sm:w-[18px]"
        />
      )}
    </span>
  );
}

// ============================================================
// Connection avatar
// ============================================================

function ConnectionAvatar({
  image,
  name,
  type = 'user',
}: {
  image: string | null;
  name: string;
  type?: 'user' | 'artist';
}) {
  const imageUrl = getMediaUrl(image);

  return (
    <div className="relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full border border-light-border bg-light-surface-alt text-sm font-semibold text-light-muted dark:border-dark-border dark:bg-dark-surface-alt dark:text-dark-muted sm:h-14 sm:w-14">
      {imageUrl ? (
        <Image
          src={imageUrl}
          alt={name}
          fill
          sizes="56px"
          className="object-cover"
        />
      ) : (
        type === 'artist' ? (
          <Music2 className="h-6 w-6" />
        ) : (
          <span>{getInitials(name || '?')}</span>
        )
      )}
    </div>
  );
}

// ============================================================
// Follow button
// ============================================================

function FollowButton({
  isFollowing,
  loading,
  onClick,
}: {
  isFollowing: boolean;
  loading: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={loading}
      className={`inline-flex min-w-[100px] shrink-0 items-center justify-center gap-1.5 rounded-full px-3.5 py-2 text-[11px] font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 sm:min-w-[112px] sm:px-4 sm:text-xs ${
        isFollowing
          ? 'border border-light-border bg-transparent text-light-text hover:border-red-400 hover:text-red-500 dark:border-dark-border dark:text-dark-text'
          : 'bg-brand-teal text-white hover:opacity-90'
      }`}
    >
      {loading ? (
        <LoaderCircle className="h-3.5 w-3.5 animate-spin" />
      ) : isFollowing ? (
        <>
          <Check className="h-3.5 w-3.5" />
          Following
        </>
      ) : (
        'Follow'
      )}
    </button>
  );
}

// ============================================================
// View profile button
// ============================================================

function ViewProfileButton({
  username,
}: {
  username: string;
}) {
  return (
    <Link
      href={`/account/${encodeURIComponent(username)}`}
      className="inline-flex min-w-[100px] shrink-0 items-center justify-center rounded-full border border-light-border bg-transparent px-3.5 py-2 text-[11px] font-semibold text-light-text transition-colors hover:border-brand-teal hover:text-brand-teal dark:border-dark-border dark:text-dark-text sm:min-w-[112px] sm:px-4 sm:text-xs"
    >
      View profile
    </Link>
  );
}

// ============================================================
// User connection card
// ============================================================

function UserConnectionCard({
  user,
  isAuthenticated,
  isCurrentUser,
  onFollow,
  followLoading,
}: {
  user: PublicConnectionUser;
  isAuthenticated: boolean;
  isCurrentUser: boolean;
  onFollow: (user: PublicConnectionUser) => void;
  followLoading: boolean;
}) {
  const displayName = user.display_name || user.username;

  return (
    <div className="flex min-w-0 items-center gap-3 rounded-xl border border-light-border bg-light-surface p-3 transition-colors hover:border-brand-teal/40 dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40 sm:gap-4 sm:p-4">
      <Link
        href={`/account/${encodeURIComponent(user.username)}`}
        className="shrink-0"
        aria-label={`View ${displayName}'s profile`}
      >
        <ConnectionAvatar
          image={user.profile_image}
          name={displayName}
        />
      </Link>

      <div className="min-w-0 flex-1">
        <Link
          href={`/account/${encodeURIComponent(user.username)}`}
          className="group inline-flex max-w-full items-center gap-1.5"
        >
          <h3 className="truncate text-sm font-semibold text-light-text transition-colors group-hover:text-brand-teal dark:text-dark-text sm:text-base">
            {displayName}
          </h3>

          <VerificationBadges
            isVerified={user.is_verified}
            isIdentityVerified={user.is_identity_verified}
          />
        </Link>

        <Link
          href={`/account/${encodeURIComponent(user.username)}`}
          className="mt-0.5 block truncate text-xs text-light-muted transition-colors hover:text-brand-teal dark:text-dark-muted sm:text-sm"
        >
          @{user.username}
        </Link>
      </div>

      {isAuthenticated && (
        isCurrentUser ? (
          <ViewProfileButton username={user.username} />
        ) : (
          <FollowButton
            isFollowing={user.is_following}
            loading={followLoading}
            onClick={() => onFollow(user)}
          />
        )
      )}
    </div>
  );
}

// ============================================================
// Artist connection card
// ============================================================

function ArtistConnectionCard({
  artist,
  isAuthenticated,
  onFollow,
  followLoading,
}: {
  artist: PublicConnectionArtist;
  isAuthenticated: boolean;
  onFollow: (artist: PublicConnectionArtist) => void;
  followLoading: boolean;
}) {
  return (
    <div className="flex min-w-0 items-center gap-3 rounded-xl border border-light-border bg-light-surface p-3 transition-colors hover:border-brand-teal/40 dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40 sm:gap-4 sm:p-4">
      <Link
        href={`/music/artists/${artist.slug}`}
        className="shrink-0"
        aria-label={`View ${artist.name}'s artist page`}
      >
        <ConnectionAvatar
          image={artist.profile_image}
          name={artist.name}
          type="artist"
        />
      </Link>

      <div className="min-w-0 flex-1">
        <Link
          href={`/music/artists/${artist.slug}`}
          className="group inline-flex max-w-full items-center gap-1.5"
        >
          <h3 className="truncate text-sm font-semibold text-light-text transition-colors group-hover:text-brand-teal dark:text-dark-text sm:text-base">
            {artist.name}
          </h3>

          {artist.is_verified && (
            <CheckCircle2
              aria-label="Verified artist"
              title="Verified artist"
              className="h-4 w-4 shrink-0 fill-blue-500 text-white"
            />
          )}
        </Link>

        <p className="mt-0.5 truncate text-xs text-light-muted dark:text-dark-muted sm:text-sm">
          {formatCount(artist.followers_count)} followers
        </p>
      </div>

      {isAuthenticated && (
        <FollowButton
          isFollowing={artist.is_following}
          loading={followLoading}
          onClick={() => onFollow(artist)}
        />
      )}
    </div>
  );
}

// ============================================================
// Main connections page
// ============================================================

export default function PublicConnectionsPage() {
  const params = useParams<{ username: string }>();
  const username = decodeURIComponent(params.username);

  const router = useRouter();
  const searchParams = useSearchParams();

  const { user: currentUser, isAuthenticated } = useAuth();

  // --------------------------------------------------------
  // Active tab
  // --------------------------------------------------------

  const requestedTab = searchParams.get('tab');

  const activeTab: ConnectionTab =
    requestedTab === 'following' ||
    requestedTab === 'artists' ||
    requestedTab === 'followers'
      ? requestedTab
      : 'followers';

  // --------------------------------------------------------
  // Search state
  // --------------------------------------------------------

  const [searchTerm, setSearchTerm] = useState(
    () => searchParams.get('search') || '',
  );

  const [debouncedSearch, setDebouncedSearch] = useState(
    () => searchParams.get('search')?.trim() || '',
  );

  const normalizedSearch = debouncedSearch.trim();

  // --------------------------------------------------------
  // Connection list state
  // --------------------------------------------------------

  const [connections, setConnections] = useState<ConnectionItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);

  const [nextPage, setNextPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState('');

  // --------------------------------------------------------
  // Follow action state
  // --------------------------------------------------------

  const [followLoadingIds, setFollowLoadingIds] = useState<
    Set<number>
  >(() => new Set());

  const [followError, setFollowError] = useState('');

  // --------------------------------------------------------
  // Infinite scroll refs
  // --------------------------------------------------------

  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const loadingRef = useRef(false);
  const requestIdRef = useRef(0);

  // ========================================================
  // Debounce search
  // ========================================================

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedSearch(searchTerm.trim());
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeout);
  }, [searchTerm]);

  // ========================================================
  // Keep search in the URL
  // ========================================================

  useEffect(() => {
    const query = new URLSearchParams();

    query.set('tab', activeTab);

    if (normalizedSearch) {
      query.set('search', normalizedSearch);
    }

    const nextUrl =
      `/account/${encodeURIComponent(username)}/connections?${query.toString()}`;

    router.replace(nextUrl, {
      scroll: false,
    });
  }, [
    username,
    activeTab,
    normalizedSearch,
    router,
  ]);

  // ========================================================
  // Change active tab
  // ========================================================

  const handleTabChange = (tab: ConnectionTab) => {
    if (tab === activeTab) {
      return;
    }

    const query = new URLSearchParams();

    query.set('tab', tab);

    const currentSearch = searchTerm.trim();

    if (currentSearch) {
      query.set('search', currentSearch);
    }

    router.push(
      `/account/${encodeURIComponent(username)}/connections?${query.toString()}`,
      {
        scroll: false,
      },
    );
  };

  // ========================================================
  // Handle search input
  // ========================================================

  const handleSearchChange = (
    value: string,
  ) => {
    setSearchTerm(
      value.slice(0, MAX_SEARCH_LENGTH),
    );
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setDebouncedSearch('');
  };

  // ========================================================
  // Reset list when profile, tab, or search changes
  // ========================================================

  useEffect(() => {
    requestIdRef.current += 1;

    setConnections([]);
    setTotalCount(0);

    setNextPage(1);
    setHasMore(true);

    setLoading(false);
    setLoaded(false);
    setError('');
    setFollowError('');

    loadingRef.current = false;
  }, [
    username,
    activeTab,
    normalizedSearch,
  ]);

  // ========================================================
  // Load connections
  // ========================================================

  const loadConnections = useCallback(
    async (page: number) => {
      if (
        loadingRef.current ||
        (page !== 1 && !hasMore)
      ) {
        return;
      }

      loadingRef.current = true;

      const requestId = ++requestIdRef.current;

      setLoading(true);
      setError('');

      try {
        const query = new URLSearchParams({
          tab: activeTab,
          page: String(page),
          page_size: String(PAGE_SIZE),
        });

        if (normalizedSearch) {
          query.set('search', normalizedSearch);
        }

        const response = await apiRequest<
          PaginatedResponse<ConnectionItem>
        >(
          `/api/accounts/users/${encodeURIComponent(
            username,
          )}/connections/?${query.toString()}`,
        );

        if (requestId !== requestIdRef.current) {
          return;
        }

        setConnections((current) => {
          if (page === 1) {
            return response.results;
          }

          const existingIds = new Set(
            current.map((item) => item.id),
          );

          const newItems = response.results.filter(
            (item) => !existingIds.has(item.id),
          );

          return [...current, ...newItems];
        });

        setTotalCount(response.count);
        setHasMore(Boolean(response.next));
        setNextPage(page + 1);
        setLoaded(true);
      } catch (error) {
        if (requestId !== requestIdRef.current) {
          return;
        }

        setError(
          error instanceof ApiError
            ? error.message
            : 'Unable to load connections. Please try again.',
        );
      } finally {
        if (requestId === requestIdRef.current) {
          loadingRef.current = false;
          setLoading(false);
        }
      }
    },
    [
      username,
      activeTab,
      normalizedSearch,
      hasMore,
    ],
  );

  // ========================================================
  // Initial load / reload after search or tab change
  // ========================================================

  useEffect(() => {
    if (loaded || loadingRef.current) {
      return;
    }

    loadConnections(1);
  }, [
    loaded,
    loadConnections,
  ]);

  // ========================================================
  // Infinite scrolling
  // ========================================================

  useEffect(() => {
    if (
      !loaded ||
      !hasMore ||
      loading ||
      error
    ) {
      return;
    }

    const sentinel = sentinelRef.current;

    if (!sentinel) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          loadConnections(nextPage);
        }
      },
      {
        rootMargin: '500px 0px',
      },
    );

    observer.observe(sentinel);

    return () => observer.disconnect();
  }, [
    loaded,
    hasMore,
    loading,
    error,
    nextPage,
    loadConnections,
  ]);

  // ========================================================
  // Follow / unfollow user
  // ========================================================

  const handleUserFollow = async (
    user: PublicConnectionUser,
  ) => {
    if (
      !isAuthenticated ||
      String(currentUser?.id) === String(user.id) ||
      followLoadingIds.has(user.id)
    ) {
      return;
    }

    setFollowError('');

    const previousFollowing = user.is_following;

    setFollowLoadingIds((current) => {
      const updated = new Set(current);
      updated.add(user.id);
      return updated;
    });

    // Optimistic update.
    setConnections((current) =>
      current.map((item) =>
        isConnectionUser(item) && item.id === user.id
          ? {
              ...item,
              is_following: !previousFollowing,
            }
          : item,
      ),
    );

    try {
      if (previousFollowing) {
        await unfollowCommunityUser(user.id);
      } else {
        await followCommunityUser(user.id);
      }
    } catch (error) {
      // Roll back if the request fails.
      setConnections((current) =>
        current.map((item) =>
          isConnectionUser(item) && item.id === user.id
            ? {
                ...item,
                is_following: previousFollowing,
              }
            : item,
        ),
      );

      setFollowError(
        error instanceof ApiError
          ? error.message
          : 'Unable to update your follow status. Please try again.',
      );
    } finally {
      setFollowLoadingIds((current) => {
        const updated = new Set(current);
        updated.delete(user.id);
        return updated;
      });
    }
  };

  // ========================================================
  // Follow / unfollow artist
  // ========================================================

  const handleArtistFollow = async (
    artist: PublicConnectionArtist,
  ) => {
    if (
      !isAuthenticated ||
      followLoadingIds.has(artist.id)
    ) {
      return;
    }

    setFollowError('');

    const previousFollowing = artist.is_following;
    const previousFollowersCount = artist.followers_count;

    setFollowLoadingIds((current) => {
      const updated = new Set(current);
      updated.add(artist.id);
      return updated;
    });

    // Optimistic update.
    setConnections((current) =>
      current.map((item) =>
        !isConnectionUser(item) && item.id === artist.id
          ? {
              ...item,
              is_following: !previousFollowing,
              followers_count: Math.max(
                0,
                previousFollowersCount +
                  (previousFollowing ? -1 : 1),
              ),
            }
          : item,
      ),
    );

    try {
      if (previousFollowing) {
        await unfollowArtist(artist.id);
      } else {
        await followArtist(artist.id);
      }
    } catch (error) {
      // Roll back if the request fails.
      setConnections((current) =>
        current.map((item) =>
          !isConnectionUser(item) && item.id === artist.id
            ? {
                ...item,
                is_following: previousFollowing,
                followers_count: previousFollowersCount,
              }
            : item,
        ),
      );

      setFollowError(
        error instanceof ApiError
          ? error.message
          : 'Unable to update your follow status. Please try again.',
      );
    } finally {
      setFollowLoadingIds((current) => {
        const updated = new Set(current);
        updated.delete(artist.id);
        return updated;
      });
    }
  };

  // ========================================================
  // Derived values
  // ========================================================

  const heading =
    activeTab === 'followers'
      ? 'Followers'
      : activeTab === 'following'
        ? 'Following'
        : 'Artists';

  const emptyTitle = normalizedSearch
    ? 'No matching results'
    : activeTab === 'followers'
      ? 'No followers yet'
      : activeTab === 'following'
        ? 'Not following anyone yet'
        : 'No followed artists yet';

  const emptyDescription = normalizedSearch
    ? `We couldn't find any ${activeTab === 'artists' ? 'artists' : 'accounts'} matching "${normalizedSearch}". Try another search.`
    : activeTab === 'followers'
      ? 'People who follow this account will appear here.'
      : activeTab === 'following'
        ? 'Accounts this user follows will appear here.'
        : 'Artists this user follows will appear here.';

  // ========================================================
  // Loading state
  // ========================================================

  if (!loaded && loading) {
    return (
      <>
        <div className="sticky top-0 z-50">
          <HomeNav />
        </div>

        <MusicNavigation />

        <main className="min-h-screen bg-light-bg px-3 py-8 dark:bg-dark-bg sm:px-5">
          <div className="mx-auto max-w-4xl animate-pulse">
            <div className="mb-6 h-5 w-24 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />

            <div className="h-7 w-40 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />

            <div className="mt-5 h-12 rounded-lg bg-light-surface-alt dark:bg-dark-surface-alt" />

            <div className="mt-5 space-y-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 rounded-xl border border-light-border bg-light-surface p-3 dark:border-dark-border dark:bg-dark-surface sm:p-4"
                >
                  <div className="h-12 w-12 rounded-full bg-light-surface-alt dark:bg-dark-surface-alt" />

                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-32 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />
                    <div className="h-3 w-24 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />
                  </div>

                  <div className="h-8 w-24 rounded-full bg-light-surface-alt dark:bg-dark-surface-alt" />
                </div>
              ))}
            </div>
          </div>
        </main>
      </>
    );
  }

  // ========================================================
  // Main page
  // ========================================================

  return (
    <>
      <div className="sticky top-0 z-50">
        <HomeNav />
      </div>

      <MusicNavigation />

      <main className="min-h-screen bg-light-bg pb-12 text-light-text dark:bg-dark-bg dark:text-dark-text">
        <div className="mx-auto max-w-4xl px-3 sm:px-5 lg:px-6">
          {/* Back navigation */}

          <div className="py-3 sm:py-5">
            <Link
              href={`/account/${encodeURIComponent(username)}`}
              className="inline-flex items-center gap-2 rounded-lg py-2 pr-3 text-xs font-medium text-light-muted transition-colors hover:text-brand-teal dark:text-dark-muted dark:hover:text-brand-teal sm:text-sm"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to profile
            </Link>
          </div>

          {/* Page heading */}

          <section className="rounded-2xl border border-light-border bg-light-surface p-4 dark:border-dark-border dark:bg-dark-surface sm:p-6">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-light-surface-alt text-light-muted dark:bg-dark-surface-alt dark:text-dark-muted">
                <Users className="h-5 w-5" />
              </div>

              <div className="min-w-0">
                <h1 className="text-lg font-bold text-light-text dark:text-dark-text sm:text-xl">
                  Connections
                </h1>

                <p className="mt-0.5 truncate text-xs text-light-muted dark:text-dark-muted sm:text-sm">
                  @{username}
                </p>
              </div>
            </div>

            {/* Search */}

            <div className="relative mt-5">
              <Search
                aria-hidden="true"
                className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-light-muted dark:text-dark-muted"
              />

              <input
                type="search"
                value={searchTerm}
                onChange={(event) =>
                  handleSearchChange(event.target.value)
                }
                maxLength={MAX_SEARCH_LENGTH}
                placeholder="Search connections..."
                aria-label="Search connections"
                className="h-11 w-full rounded-xl border border-light-border bg-light-bg py-2 pl-10 pr-11 text-sm text-light-text outline-none transition-colors placeholder:text-light-muted focus:border-brand-teal focus:ring-1 focus:ring-brand-teal dark:border-dark-border dark:bg-dark-bg dark:text-dark-text dark:placeholder:text-dark-muted"
              />

              {searchTerm && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  aria-label="Clear search"
                  className="absolute right-3 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full text-light-muted transition-colors hover:bg-light-surface-alt hover:text-light-text dark:text-dark-muted dark:hover:bg-dark-surface-alt dark:hover:text-dark-text"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Connection tabs */}

            <div className="mt-5 grid grid-cols-3 border-b border-light-border dark:border-dark-border">
              {CONNECTION_TABS.map((tab) => {
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => handleTabChange(tab.id)}
                    aria-pressed={isActive}
                    className={`relative py-3 text-xs font-semibold transition-colors sm:text-sm ${
                      isActive
                        ? 'text-brand-teal'
                        : 'text-light-muted hover:text-light-text dark:text-dark-muted dark:hover:text-dark-text'
                    }`}
                  >
                    {tab.label}

                    {isActive && (
                      <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-brand-teal" />
                    )}
                  </button>
                );
              })}
            </div>
          </section>

          {/* Connection list heading */}

          <div className="mt-5 flex items-center justify-between gap-3 sm:mt-6">
            <div className="min-w-0">
              <h2 className="text-sm font-bold text-light-text dark:text-dark-text sm:text-base">
                {heading}
              </h2>

              {normalizedSearch && (
                <p className="mt-1 truncate text-[11px] text-light-muted dark:text-dark-muted">
                  Results for &quot;{normalizedSearch}&quot;
                </p>
              )}
            </div>

            {loaded && (
              <span className="shrink-0 text-xs text-light-muted dark:text-dark-muted">
                {formatCount(totalCount)}{' '}
                {totalCount === 1 ? 'connection' : 'connections'}
              </span>
            )}
          </div>

          {/* Follow action error */}

          {followError && (
            <div
              role="alert"
              className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-600 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-400"
            >
              {followError}
            </div>
          )}

          {/* Connection list */}

          <section className="mt-4 space-y-3">
            {/* Empty state */}

            {loaded &&
              connections.length === 0 &&
              !error && (
                <div className="rounded-2xl border border-light-border bg-light-surface px-5 py-12 text-center dark:border-dark-border dark:bg-dark-surface">
                  {activeTab === 'artists' ? (
                    <Disc3 className="mx-auto h-9 w-9 text-light-muted dark:text-dark-muted" />
                  ) : (
                    <Users className="mx-auto h-9 w-9 text-light-muted dark:text-dark-muted" />
                  )}

                  <h3 className="mt-3 text-sm font-semibold text-light-text dark:text-dark-text">
                    {emptyTitle}
                  </h3>

                  <p className="mx-auto mt-1 max-w-sm text-xs leading-relaxed text-light-muted dark:text-dark-muted">
                    {emptyDescription}
                  </p>

                  {normalizedSearch && (
                    <button
                      type="button"
                      onClick={handleClearSearch}
                      className="mt-4 text-xs font-semibold text-brand-teal transition-opacity hover:opacity-80"
                    >
                      Clear search
                    </button>
                  )}
                </div>
              )}

            {/* User and artist connections */}

            {connections.map((item) => {
              if (isConnectionUser(item)) {
                const isCurrentUser =
                  isAuthenticated &&
                  String(currentUser?.id) === String(item.id);

                return (
                  <UserConnectionCard
                    key={`user-${item.id}`}
                    user={item}
                    isAuthenticated={Boolean(isAuthenticated)}
                    isCurrentUser={isCurrentUser}
                    onFollow={handleUserFollow}
                    followLoading={followLoadingIds.has(item.id)}
                  />
                );
              }

              return (
                <ArtistConnectionCard
                  key={`artist-${item.id}`}
                  artist={item}
                  isAuthenticated={Boolean(isAuthenticated)}
                  onFollow={handleArtistFollow}
                  followLoading={followLoadingIds.has(item.id)}
                />
              );
            })}

            {/* Error state */}

            {error && (
              <div
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 p-4 text-center text-xs text-red-600 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-400"
              >
                <p>{error}</p>

                <button
                  type="button"
                  onClick={() => loadConnections(nextPage)}
                  className="mt-2 font-semibold underline"
                >
                  Try again
                </button>
              </div>
            )}

            {/* Loading indicator */}

            {loading && (
              <div className="flex items-center justify-center gap-2 py-6 text-xs text-light-muted dark:text-dark-muted">
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Searching or loading {heading.toLowerCase()}...
              </div>
            )}

            {/* End of list */}

            {loaded &&
              !hasMore &&
              connections.length > 0 &&
              !loading && (
                <p className="py-5 text-center text-[11px] text-light-muted dark:text-dark-muted">
                  You&apos;ve reached the end.
                </p>
              )}

            {/* Infinite scroll sentinel */}

            <div
              ref={sentinelRef}
              className="h-1"
              aria-hidden="true"
            />
          </section>
        </div>
      </main>
    </>
  );
}
