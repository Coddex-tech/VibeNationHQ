'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';
import type { TouchEvent } from 'react';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  Check,
  CheckCircle2,
  Disc3,
  LoaderCircle,
  Music2,
  Users,
  X,
} from 'lucide-react';

import { ApiError, apiRequest, getMediaUrl } from '@/lib/api';

import type {
  CommunityAlbum,
  CommunityArtist,
  CommunityPost,
  CommunitySong,
} from '@/lib/music/CommunityPosts';

import {
  followCommunityUser,
  unfollowCommunityUser,
} from '@/lib/music/CommunityPosts';

import MusicPost from '@/components/music/CommunityPost';
import { useAuth } from '@/components/auth/AuthProvider';
import HomeNav from '@/components/special/HomeNav';
import MusicNavigation from '@/components/music/MusicNavigation';
import VerificationBadge from '@/components/Icons';

// ============================================================
// Types
// ============================================================

type PublicProfile = {
  id: number;
  username: string;
  display_name: string | null;
  bio: string | null;
  profile_image: string | null;
  is_verified: boolean;
  is_identity_verified: boolean;
  followers_count: number;
  following_count: number;
  artists_count: number;
  is_following: boolean;
  is_following_you: boolean;
  is_own_profile: boolean;
  date_joined: string;
};

type ProfileMusicItem = {
  target_type: 'song' | 'album' | 'artist';
  post_count: number;
  latest_post_at: string;
  entity: CommunitySong | CommunityAlbum | CommunityArtist;
};

type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

type ProfileTab = 'posts' | 'music';

// ============================================================
// Constants
// ============================================================

const PAGE_SIZE = 12;

// ============================================================
// Helpers
// ============================================================

function formatCount(value: number): string {
  if (value < 1000) {
    return value.toLocaleString();
  }

  if (value < 1_000_000) {
    return `${(value / 1000).toFixed(value >= 10_000 ? 0 : 1)}K`;
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
        <VerificationBadge type="verified" size={16} />
      )}

      {isIdentityVerified && (
        <VerificationBadge type="identity" size={16} />
      )}
    </span>
  );
}

// ============================================================
// Profile avatar
// ============================================================

function ProfileAvatar({
  image,
  name,
  onClick,
  size = 'large',
}: {
  image: string | null;
  name: string;
  onClick?: () => void;
  size?: 'large' | 'small';
}) {
  const dimensions =
    size === 'large'
      ? 'h-24 w-24 sm:h-32 sm:w-32'
      : 'h-12 w-12';

  const imageUrl = getMediaUrl(image);

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!imageUrl || !onClick}
      aria-label={
        imageUrl ? `View ${name}'s profile picture` : undefined
      }
      className={`${dimensions} relative shrink-0 overflow-hidden rounded-full border-2 border-light-border bg-light-surface-alt text-xl font-semibold text-light-text dark:border-dark-border dark:bg-dark-surface-alt dark:text-dark-text ${
        imageUrl && onClick
          ? 'cursor-pointer transition-colors hover:border-brand-teal'
          : 'cursor-default'
      }`}
    >
      {imageUrl ? (
        <Image
          src={imageUrl}
          alt={`${name}'s profile picture`}
          fill
          sizes={
            size === 'large'
              ? '(max-width: 640px) 96px, 128px'
              : '48px'
          }
          className="object-cover"
        />
      ) : (
        <span>{getInitials(name || '?')}</span>
      )}
    </button>
  );
}

// ============================================================
// Music activity card
// ============================================================

function MusicProfileCard({
  item,
}: {
  item: ProfileMusicItem;
}) {
  const entity = item.entity;

  let title = '';
  let subtitle = '';
  let image: string | null = null;
  let href = '';
  let typeLabel = '';

  if (item.target_type === 'song') {
    const song = entity as CommunitySong;

    title = song.title;

    subtitle = [
      ...song.artists.map((artist) => artist.name),
      ...song.featured_artists.map((artist) => artist.name),
    ].join(', ');

    image = song.artwork;
    href = `/music/songs/${song.slug}`;
    typeLabel = 'Song';
  } else if (item.target_type === 'album') {
    const album = entity as CommunityAlbum;

    title = album.title;
    subtitle = album.artists.map((artist) => artist.name).join(', ');
    image = album.artwork;
    href = `/music/albums/${album.slug}`;
    typeLabel = 'Album';
  } else {
    const artist = entity as CommunityArtist;

    title = artist.name;
    subtitle = `${formatCount(artist.followers_count)} followers`;
    image = artist.profile_image;
    href = `/music/artists/${artist.slug}`;
    typeLabel = 'Artist';
  }

  const imageUrl = getMediaUrl(image);

  return (
    <Link
      href={href}
      className="group flex min-w-0 items-center gap-3 rounded-xl border border-light-border bg-light-surface p-3 transition-colors hover:border-brand-teal/50 dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/50 sm:gap-4 sm:p-4"
    >
      <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-light-surface-alt dark:bg-dark-surface-alt sm:h-16 sm:w-16">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={title}
            fill
            sizes="64px"
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-light-muted dark:text-dark-muted">
            {item.target_type === 'artist' ? (
              <Users className="h-6 w-6" />
            ) : item.target_type === 'album' ? (
              <Disc3 className="h-6 w-6" />
            ) : (
              <Music2 className="h-6 w-6" />
            )}
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex min-w-0 items-center gap-2">
          <h3 className="truncate text-sm font-semibold text-light-text transition-colors group-hover:text-brand-teal dark:text-dark-text sm:text-base">
            {title}
          </h3>

          {item.target_type === 'artist' &&
            (entity as CommunityArtist).is_verified && (
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0 fill-blue-500 text-white" />
            )}
        </div>

        <p className="mt-0.5 truncate text-xs text-light-muted dark:text-dark-muted sm:text-sm">
          {subtitle || typeLabel}
        </p>

        <p className="mt-1 text-[11px] font-medium text-brand-teal sm:text-xs">
          {item.post_count.toLocaleString()}{' '}
          {item.post_count === 1 ? 'post' : 'posts'}
        </p>
      </div>

      <span className="shrink-0 rounded-full bg-light-surface-alt px-2.5 py-1 text-[10px] font-medium text-light-muted dark:bg-dark-surface-alt dark:text-dark-muted sm:text-xs">
        {typeLabel}
      </span>
    </Link>
  );
}

// ============================================================
// Full-screen profile photo viewer
// ============================================================

function ProfilePhotoViewer({
  image,
  name,
  onClose,
}: {
  image: string;
  name: string;
  onClose: () => void;
}) {
  const touchStart = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose]);

  const handleTouchStart = (event: TouchEvent<HTMLDivElement>) => {
    const touch = event.touches[0];

    touchStart.current = {
      x: touch.clientX,
      y: touch.clientY,
    };
  };

  const handleTouchEnd = (event: TouchEvent<HTMLDivElement>) => {
    if (!touchStart.current) {
      return;
    }

    const touch = event.changedTouches[0];

    const deltaX = touch.clientX - touchStart.current.x;
    const deltaY = touch.clientY - touchStart.current.y;

    if (Math.abs(deltaX) > 45 || Math.abs(deltaY) > 45) {
      onClose();
    }

    touchStart.current = null;
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`${name}'s profile picture`}
      onClick={onClose}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-5 backdrop-blur-xl"
    >
      <button
        type="button"
        onClick={onClose}
        aria-label="Close profile picture"
        className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-white/15 text-white transition-colors hover:bg-white/25"
      >
        <X className="h-5 w-5" />
      </button>

      <div
        onClick={(event) => event.stopPropagation()}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        className="relative flex max-h-[85vh] max-w-[90vw] touch-none items-center justify-center"
      >
        <Image
          src={image}
          alt={`${name}'s profile picture`}
          width={900}
          height={900}
          priority
          draggable={false}
          className="max-h-[85vh] max-w-[90vw] rounded-xl object-contain shadow-2xl"
        />
      </div>

      <p className="pointer-events-none absolute bottom-6 left-0 right-0 text-center text-xs text-white/70">
        Tap outside or swipe in any direction to close
      </p>
    </div>
  );
}

// ============================================================
// Main public profile page
// ============================================================

export default function PublicProfilePage() {
  const params = useParams<{ username: string }>();
  const username = decodeURIComponent(params.username);

  const { isAuthenticated } = useAuth();

  // --------------------------------------------------------
  // Profile state
  // --------------------------------------------------------

  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState('');

  // --------------------------------------------------------
  // Tab state
  // --------------------------------------------------------

  const [activeTab, setActiveTab] = useState<ProfileTab>('posts');

  // --------------------------------------------------------
  // Posts state
  // --------------------------------------------------------

  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [postsNextPage, setPostsNextPage] = useState(1);
  const [postsHasMore, setPostsHasMore] = useState(true);
  const [postsLoading, setPostsLoading] = useState(false);
  const [postsLoaded, setPostsLoaded] = useState(false);
  const [postsError, setPostsError] = useState('');

  // --------------------------------------------------------
  // Music state
  // --------------------------------------------------------

  const [musicItems, setMusicItems] = useState<ProfileMusicItem[]>([]);
  const [musicNextPage, setMusicNextPage] = useState(1);
  const [musicHasMore, setMusicHasMore] = useState(true);
  const [musicLoading, setMusicLoading] = useState(false);
  const [musicLoaded, setMusicLoaded] = useState(false);
  const [musicError, setMusicError] = useState('');

  // --------------------------------------------------------
  // Follow state
  // --------------------------------------------------------

  const [isFollowing, setIsFollowing] = useState(false);
  const [followersCount, setFollowersCount] = useState(0);
  const [followLoading, setFollowLoading] = useState(false);
  const [followError, setFollowError] = useState('');

  // --------------------------------------------------------
  // Photo viewer state
  // --------------------------------------------------------

  const [photoOpen, setPhotoOpen] = useState(false);

  // --------------------------------------------------------
  // Infinite scroll refs
  // --------------------------------------------------------

  const postsSentinelRef = useRef<HTMLDivElement | null>(null);
  const musicSentinelRef = useRef<HTMLDivElement | null>(null);

  const postsLoadingRef = useRef(false);
  const musicLoadingRef = useRef(false);

  // ========================================================
  // Fetch profile
  // ========================================================

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      setProfileLoading(true);
      setProfileError('');

      try {
        const response = await apiRequest<PublicProfile>(
          `/api/accounts/users/${encodeURIComponent(username)}/`,
        );

        if (cancelled) {
          return;
        }

        setProfile(response);
        setIsFollowing(response.is_following);
        setFollowersCount(response.followers_count);
      } catch (error) {
        if (cancelled) {
          return;
        }

        setProfileError(
          error instanceof ApiError
            ? error.message
            : 'Unable to load this profile. Please try again.',
        );
      } finally {
        if (!cancelled) {
          setProfileLoading(false);
        }
      }
    }

    loadProfile();

    return () => {
      cancelled = true;
    };
  }, [username]);

  // ========================================================
  // Reset profile content when username changes
  // ========================================================

  useEffect(() => {
    setPosts([]);
    setMusicItems([]);

    setPostsNextPage(1);
    setMusicNextPage(1);

    setPostsHasMore(true);
    setMusicHasMore(true);

    setPostsLoaded(false);
    setMusicLoaded(false);

    setPostsError('');
    setMusicError('');
    setFollowError('');

    postsLoadingRef.current = false;
    musicLoadingRef.current = false;
  }, [username]);

  // ========================================================
  // Load published community posts
  // ========================================================

  const loadPosts = useCallback(
    async (page: number) => {
      if (postsLoadingRef.current || !postsHasMore) {
        return;
      }

      postsLoadingRef.current = true;
      setPostsLoading(true);
      setPostsError('');

      try {
        const response = await apiRequest<
          PaginatedResponse<CommunityPost>
        >(
          `/api/accounts/users/${encodeURIComponent(
            username,
          )}/posts/?page=${page}&page_size=${PAGE_SIZE}`,
        );

        setPosts((current) => {
          if (page === 1) {
            return response.results;
          }

          const existingIds = new Set(
            current.map((post) => post.id),
          );

          const newPosts = response.results.filter(
            (post) => !existingIds.has(post.id),
          );

          return [...current, ...newPosts];
        });

        setPostsHasMore(Boolean(response.next));
        setPostsNextPage(page + 1);
        setPostsLoaded(true);
      } catch (error) {
        setPostsError(
          error instanceof ApiError
            ? error.message
            : 'Unable to load posts. Please try again.',
        );
      } finally {
        postsLoadingRef.current = false;
        setPostsLoading(false);
      }
    },
    [username, postsHasMore],
  );

  // ========================================================
  // Load aggregated music activity
  // ========================================================

  const loadMusic = useCallback(
    async (page: number) => {
      if (musicLoadingRef.current || !musicHasMore) {
        return;
      }

      musicLoadingRef.current = true;
      setMusicLoading(true);
      setMusicError('');

      try {
        const response = await apiRequest<
          PaginatedResponse<ProfileMusicItem>
        >(
          `/api/accounts/users/${encodeURIComponent(
            username,
          )}/music/?page=${page}&page_size=${PAGE_SIZE}`,
        );

        setMusicItems((current) => {
          if (page === 1) {
            return response.results;
          }

          const existingKeys = new Set(
            current.map(
              (item) => `${item.target_type}-${item.entity.id}`,
            ),
          );

          const newItems = response.results.filter(
            (item) =>
              !existingKeys.has(
                `${item.target_type}-${item.entity.id}`,
              ),
          );

          return [...current, ...newItems];
        });

        setMusicHasMore(Boolean(response.next));
        setMusicNextPage(page + 1);
        setMusicLoaded(true);
      } catch (error) {
        setMusicError(
          error instanceof ApiError
            ? error.message
            : 'Unable to load music activity. Please try again.',
        );
      } finally {
        musicLoadingRef.current = false;
        setMusicLoading(false);
      }
    },
    [username, musicHasMore],
  );

  // ========================================================
  // Load Posts when the profile is ready
  // ========================================================

  useEffect(() => {
    if (
      !profile ||
      postsLoaded ||
      postsLoadingRef.current
    ) {
      return;
    }

    loadPosts(1);
  }, [profile, postsLoaded, loadPosts]);

  // ========================================================
  // Load Music when the Music tab is opened
  // ========================================================

  useEffect(() => {
    if (
      activeTab !== 'music' ||
      !profile ||
      musicLoaded ||
      musicLoadingRef.current
    ) {
      return;
    }

    loadMusic(1);
  }, [activeTab, profile, musicLoaded, loadMusic]);

  // ========================================================
  // Infinite scroll: Posts
  // ========================================================

  useEffect(() => {
    if (
      activeTab !== 'posts' ||
      !postsHasMore ||
      postsLoading ||
      !postsLoaded ||
      postsError
    ) {
      return;
    }

    const sentinel = postsSentinelRef.current;

    if (!sentinel) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          loadPosts(postsNextPage);
        }
      },
      {
        rootMargin: '500px 0px',
      },
    );

    observer.observe(sentinel);

    return () => observer.disconnect();
  }, [
    activeTab,
    postsHasMore,
    postsLoading,
    postsLoaded,
    postsError,
    postsNextPage,
    loadPosts,
  ]);

  // ========================================================
  // Infinite scroll: Music
  // ========================================================

  useEffect(() => {
    if (
      activeTab !== 'music' ||
      !musicHasMore ||
      musicLoading ||
      !musicLoaded ||
      musicError
    ) {
      return;
    }

    const sentinel = musicSentinelRef.current;

    if (!sentinel) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          loadMusic(musicNextPage);
        }
      },
      {
        rootMargin: '500px 0px',
      },
    );

    observer.observe(sentinel);

    return () => observer.disconnect();
  }, [
    activeTab,
    musicHasMore,
    musicLoading,
    musicLoaded,
    musicError,
    musicNextPage,
    loadMusic,
  ]);

  // ========================================================
  // Follow / unfollow
  // ========================================================

  const handleFollow = async () => {
    if (!profile || followLoading) {
      return;
    }

    if (!isAuthenticated) {
      setFollowError('Sign in to follow this account.');
      return;
    }

    setFollowLoading(true);
    setFollowError('');

    const previousFollowing = isFollowing;
    const previousCount = followersCount;

    // Optimistic update
    setIsFollowing(!previousFollowing);

    setFollowersCount((count) =>
      Math.max(
        0,
        count + (previousFollowing ? -1 : 1),
      ),
    );

    try {
      if (previousFollowing) {
        await unfollowCommunityUser(profile.id);
      } else {
        await followCommunityUser(profile.id);
      }
    } catch (error) {
      // Roll back if the request fails.
      setIsFollowing(previousFollowing);
      setFollowersCount(previousCount);

      setFollowError(
        error instanceof ApiError
          ? error.message
          : 'Unable to update your follow status. Please try again.',
      );
    } finally {
      setFollowLoading(false);
    }
  };

  // ========================================================
  // Photo viewer
  // ========================================================

  const closePhoto = useCallback(() => {
    setPhotoOpen(false);
  }, []);

  // ========================================================
  // Derived values
  // ========================================================

  const displayName =
    profile?.display_name || profile?.username || '';

  const profileImage = getMediaUrl(
    profile?.profile_image,
  );

  // ========================================================
  // Loading state
  // ========================================================

  if (profileLoading) {
    return (
      <>
        <div className="sticky top-0 z-50">
          <HomeNav />
        </div>

        <main className="min-h-screen bg-light-bg px-4 py-8 dark:bg-dark-bg">
          <div className="mx-auto max-w-4xl animate-pulse">
            <div className="mb-8 h-5 w-24 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />

            <div className="flex items-center gap-4">
              <div className="h-24 w-24 rounded-full bg-light-surface-alt dark:bg-dark-surface-alt sm:h-32 sm:w-32" />

              <div className="flex-1 space-y-3">
                <div className="h-5 w-40 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />
                <div className="h-4 w-28 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />
                <div className="h-4 w-48 rounded bg-light-surface-alt dark:bg-dark-surface-alt" />
              </div>
            </div>

            <div className="mt-8 h-20 rounded-xl bg-light-surface-alt dark:bg-dark-surface-alt" />

            <div className="mt-6 h-12 rounded-lg bg-light-surface-alt dark:bg-dark-surface-alt" />

            <div className="mt-5 space-y-4">
              <div className="h-48 rounded-xl bg-light-surface-alt dark:bg-dark-surface-alt" />
              <div className="h-48 rounded-xl bg-light-surface-alt dark:bg-dark-surface-alt" />
            </div>
          </div>
        </main>
      </>
    );
  }

  // ========================================================
  // Profile error / unavailable state
  // ========================================================

  if (profileError || !profile) {
    return (
      <>
        <div className="sticky top-0 z-50">
          <HomeNav />
        </div>

        <main className="flex min-h-screen items-center justify-center bg-light-bg px-4 dark:bg-dark-bg">
          <div className="w-full max-w-md rounded-2xl border border-light-border bg-light-surface p-6 text-center dark:border-dark-border dark:bg-dark-surface">
            <Users className="mx-auto h-10 w-10 text-light-muted dark:text-dark-muted" />

            <h1 className="mt-4 text-lg font-semibold text-light-text dark:text-dark-text">
              Profile unavailable
            </h1>

            <p className="mt-2 text-sm text-light-muted dark:text-dark-muted">
              {profileError || 'This profile could not be found.'}
            </p>

            <Link
              href="/"
              className="mt-5 inline-flex items-center gap-2 rounded-full bg-brand-teal px-5 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90"
            >
              <ArrowLeft className="h-4 w-4" />
              Go home
            </Link>
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
      {/* Sticky navigation */}
      <div className="sticky top-0 z-50">
        <HomeNav />
      </div>
      <MusicNavigation />

      <main className="min-h-screen bg-light-bg pb-12 text-light-text dark:bg-dark-bg dark:text-dark-text">
        <div className="mx-auto max-w-4xl px-3 sm:px-5 lg:px-6">
          {/* Back navigation */}
          <div className="py-3 sm:py-5">
            <button
              type="button"
              onClick={() => window.history.back()}
              className="inline-flex items-center gap-2 rounded-lg py-2 pr-3 text-xs font-medium text-light-muted transition-colors hover:text-brand-teal dark:text-dark-muted dark:hover:text-brand-teal sm:text-sm"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </button>
          </div>

          {/* =================================================
              Profile header
          ================================================= */}

          <section className="rounded-2xl border border-light-border bg-light-surface p-3.5 dark:border-dark-border dark:bg-dark-surface sm:p-6">
            <div className="flex items-start gap-3.5 sm:gap-6">
              <ProfileAvatar
                image={profile.profile_image}
                name={displayName}
                onClick={
                  profileImage
                    ? () => setPhotoOpen(true)
                    : undefined
                }
              />

              <div className="min-w-0 flex-1 pt-1">
                <div className="flex flex-wrap items-center gap-1.5">
                  <h1 className="break-words text-base font-bold leading-tight text-light-text dark:text-dark-text sm:text-2xl">
                    {displayName}
                  </h1>

                  <VerificationBadges
                    isVerified={profile.is_verified}
                    isIdentityVerified={
                      profile.is_identity_verified
                    }
                  />
                </div>

                <p className="mt-1 break-all text-[11px] text-light-muted dark:text-dark-muted sm:text-sm">
                  @{profile.username}
                </p>

                {profile.bio && (
                  <p className="mt-2.5 whitespace-pre-wrap break-words text-xs leading-relaxed text-light-text dark:text-dark-text sm:mt-3 sm:text-sm">
                    {profile.bio}
                  </p>
                )}

                <div className="mt-3.5 flex flex-wrap items-center gap-2 sm:mt-4">
                  {profile.is_own_profile ? (
                    <Link
                      href="/settings/profile"
                      className="inline-flex items-center justify-center rounded-full border border-light-border px-4 py-2 text-[11px] font-semibold text-light-text transition-colors hover:border-brand-teal hover:text-brand-teal dark:border-dark-border dark:text-dark-text dark:hover:border-brand-teal dark:hover:text-brand-teal sm:px-5 sm:text-sm"
                    >
                      Edit profile
                    </Link>
                  ) : (
                    <button
                      type="button"
                      onClick={handleFollow}
                      disabled={followLoading}
                      className={`inline-flex min-w-24 items-center justify-center gap-2 rounded-full px-4 py-2 text-[11px] font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 sm:px-5 sm:text-sm ${
                        isFollowing
                          ? 'border border-light-border bg-transparent text-light-text hover:border-red-400 hover:text-red-500 dark:border-dark-border dark:text-dark-text'
                          : 'bg-brand-teal text-white hover:opacity-90'
                      }`}
                    >
                      {followLoading ? (
                        <LoaderCircle className="h-4 w-4 animate-spin" />
                      ) : isFollowing ? (
                        <>
                          <Check className="h-3.5 w-3.5" />
                          Following
                        </>
                      ) : profile.is_following_you ? (
                        'Follow Back'
                      ) : (
                        'Follow'
                      )}
                    </button>
                  )}
                </div>

                {followError && (
                  <div className="mt-2 text-[11px] text-red-500 sm:text-xs">
                    {followError}{' '}

                    {!isAuthenticated && (
                      <Link
                        href="/login"
                        className="font-semibold underline"
                      >
                        Sign in
                      </Link>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Profile statistics */}
            <div className="mt-5 grid grid-cols-3 divide-x divide-light-border border-t border-light-border pt-3.5 dark:divide-dark-border dark:border-dark-border sm:mt-6 sm:pt-4">
              <Link
                href={`/account/${encodeURIComponent(
                  profile.username,
                )}/connections?tab=followers`}
                className="group px-1 text-center"
              >
                <p className="text-sm font-bold text-light-text group-hover:text-brand-teal dark:text-dark-text sm:text-lg">
                  {formatCount(followersCount)}
                </p>

                <p className="mt-0.5 text-[10px] text-light-muted group-hover:text-brand-teal dark:text-dark-muted sm:text-xs">
                  Followers
                </p>
              </Link>

              <Link
                href={`/account/${encodeURIComponent(
                  profile.username,
                )}/connections?tab=following`}
                className="group px-1 text-center"
              >
                <p className="text-sm font-bold text-light-text group-hover:text-brand-teal dark:text-dark-text sm:text-lg">
                  {formatCount(profile.following_count)}
                </p>

                <p className="mt-0.5 text-[10px] text-light-muted group-hover:text-brand-teal dark:text-dark-muted sm:text-xs">
                  Following
                </p>
              </Link>

              <Link
                href={`/account/${encodeURIComponent(
                  profile.username,
                )}/connections?tab=artists`}
                className="group px-1 text-center"
              >
                <p className="text-sm font-bold text-light-text group-hover:text-brand-teal dark:text-dark-text sm:text-lg">
                  {formatCount(profile.artists_count)}
                </p>

                <p className="mt-0.5 text-[10px] text-light-muted group-hover:text-brand-teal dark:text-dark-muted sm:text-xs">
                  Artists
                </p>
              </Link>
            </div>
          </section>

          {/* =================================================
              Profile tabs
          ================================================= */}

          <div className="mt-5 border-b border-light-border dark:border-dark-border sm:mt-6">
            <div className="flex items-center gap-7">
              <button
                type="button"
                onClick={() => setActiveTab('posts')}
                aria-pressed={activeTab === 'posts'}
                className={`relative py-3 text-xs font-semibold transition-colors sm:text-sm ${
                  activeTab === 'posts'
                    ? 'text-brand-teal'
                    : 'text-light-muted hover:text-light-text dark:text-dark-muted dark:hover:text-dark-text'
                }`}
              >
                Posts

                {activeTab === 'posts' && (
                  <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-brand-teal" />
                )}
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('music')}
                aria-pressed={activeTab === 'music'}
                className={`relative py-3 text-xs font-semibold transition-colors sm:text-sm ${
                  activeTab === 'music'
                    ? 'text-brand-teal'
                    : 'text-light-muted hover:text-light-text dark:text-dark-muted dark:hover:text-dark-text'
                }`}
              >
                Music

                {activeTab === 'music' && (
                  <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-brand-teal" />
                )}
              </button>
            </div>
          </div>

          {/* =================================================
              Posts tab
          ================================================= */}

          {activeTab === 'posts' && (
            <section className="mt-4 space-y-4">
              {/* Empty state */}
              {posts.length === 0 &&
                !postsLoading &&
                !postsError && (
                  <div className="rounded-2xl border border-light-border bg-light-surface px-5 py-12 text-center dark:border-dark-border dark:bg-dark-surface">
                    <Music2 className="mx-auto h-9 w-9 text-light-muted dark:text-dark-muted" />

                    <h2 className="mt-3 text-sm font-semibold text-light-text dark:text-dark-text">
                      No posts yet
                    </h2>

                    <p className="mt-1 text-xs text-light-muted dark:text-dark-muted">
                      Published community posts will appear here.
                    </p>
                  </div>
                )}

              {/* Posts */}
              {posts.map((post) => (
                <MusicPost
                  key={post.id}
                  post={post}
                  showFollowButton={false}
                />
              ))}

              {/* Error state */}
              {postsError && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-center text-xs text-red-600 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-400">
                  <p>{postsError}</p>

                  <button
                    type="button"
                    onClick={() => loadPosts(postsNextPage)}
                    className="mt-2 font-semibold underline"
                  >
                    Try again
                  </button>
                </div>
              )}

              {/* Loading indicator */}
              {postsLoading && (
                <div className="flex items-center justify-center gap-2 py-6 text-xs text-light-muted dark:text-dark-muted">
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                  Loading posts...
                </div>
              )}

              {/* End of list */}
              {!postsHasMore &&
                posts.length > 0 &&
                !postsLoading && (
                  <p className="py-5 text-center text-[11px] text-light-muted dark:text-dark-muted">
                    You&apos;ve reached the end.
                  </p>
                )}

              {/* Infinite scroll sentinel */}
              <div
                ref={postsSentinelRef}
                className="h-1"
                aria-hidden="true"
              />
            </section>
          )}

          {/* =================================================
              Music tab
          ================================================= */}

          {activeTab === 'music' && (
            <section className="mt-4 space-y-3">
              {/* Empty state */}
              {musicItems.length === 0 &&
                !musicLoading &&
                !musicError && (
                  <div className="rounded-2xl border border-light-border bg-light-surface px-5 py-12 text-center dark:border-dark-border dark:bg-dark-surface">
                    <Disc3 className="mx-auto h-9 w-9 text-light-muted dark:text-dark-muted" />

                    <h2 className="mt-3 text-sm font-semibold text-light-text dark:text-dark-text">
                      No music activity yet
                    </h2>

                    <p className="mt-1 text-xs text-light-muted dark:text-dark-muted">
                      Songs, albums and artists this user posts about will appear here.
                    </p>
                  </div>
                )}

              {/* Music activity */}
              {musicItems.map((item) => (
                <MusicProfileCard
                  key={`${item.target_type}-${item.entity.id}`}
                  item={item}
                />
              ))}

              {/* Error state */}
              {musicError && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-center text-xs text-red-600 dark:border-red-900/40 dark:bg-red-950/20 dark:text-red-400">
                  <p>{musicError}</p>

                  <button
                    type="button"
                    onClick={() => loadMusic(musicNextPage)}
                    className="mt-2 font-semibold underline"
                  >
                    Try again
                  </button>
                </div>
              )}

              {/* Loading indicator */}
              {musicLoading && (
                <div className="flex items-center justify-center gap-2 py-6 text-xs text-light-muted dark:text-dark-muted">
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                  Loading music...
                </div>
              )}

              {/* End of list */}
              {!musicHasMore &&
                musicItems.length > 0 &&
                !musicLoading && (
                  <p className="py-5 text-center text-[11px] text-light-muted dark:text-dark-muted">
                    You&apos;ve reached the end.
                  </p>
                )}

              {/* Infinite scroll sentinel */}
              <div
                ref={musicSentinelRef}
                className="h-1"
                aria-hidden="true"
              />
            </section>
          )}
        </div>

        {/* ===================================================
            Full-screen profile photo
        =================================================== */}

        {photoOpen && profileImage && (
          <ProfilePhotoViewer
            image={profileImage}
            name={displayName}
            onClose={closePhoto}
          />
        )}
      </main>
    </>
  );
}