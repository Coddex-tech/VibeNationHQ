
'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  useEffect,
  useRef,
  useState,
} from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  Check,
  LoaderCircle,
  UserPlus,
  UserRoundCheck,
} from 'lucide-react';

import { ApiError } from '@/lib/api';
import {
  followArtist,
  unfollowArtist,
} from '@/lib/music/CommunityPosts';
import type { CommunityArtist } from '@/lib/music/CommunityPosts';
import { useAuth } from '@/components/auth/AuthProvider';

type ArtistDiscoveryItemProps = {
  artist: CommunityArtist;
};

type ArtistFollowStateChangedEvent = CustomEvent<{
  artistId: number;
  following: boolean;
  followersCount: number;
}>;

const ARTIST_FOLLOW_STATE_CHANGED_EVENT =
  'vibenation:artist-follow-state-changed';

export default function ArtistDiscoveryItem({
  artist,
}: ArtistDiscoveryItemProps) {
  const { user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const [isFollowing, setIsFollowing] = useState(
    Boolean(artist.is_following),
  );

  const [followersCount, setFollowersCount] = useState(
    artist.followers_count,
  );

  const [isUpdating, setIsUpdating] = useState(false);
  const [followError, setFollowError] = useState('');

  const followRequestInProgress = useRef(false);

  const artistHref = `/music/artists/${artist.slug}`;

  // Synchronize the button and count when the parent supplies
  // updated artist data.
  useEffect(() => {
    setIsFollowing(Boolean(artist.is_following));
    setFollowersCount(artist.followers_count);
  }, [
    artist.id,
    artist.is_following,
    artist.followers_count,
  ]);

  // Keep other mounted cards for this artist synchronized.
  useEffect(() => {
    function handleArtistFollowStateChanged(event: Event) {
      const followEvent =
        event as ArtistFollowStateChangedEvent;

      if (followEvent.detail.artistId !== Number(artist.id)) {
        return;
      }

      setIsFollowing(followEvent.detail.following);
      setFollowersCount(followEvent.detail.followersCount);
      setFollowError('');
    }

    window.addEventListener(
      ARTIST_FOLLOW_STATE_CHANGED_EVENT,
      handleArtistFollowStateChanged,
    );

    return () => {
      window.removeEventListener(
        ARTIST_FOLLOW_STATE_CHANGED_EVENT,
        handleArtistFollowStateChanged,
      );
    };
  }, [artist.id]);

  async function handleFollowToggle() {
    if (followRequestInProgress.current || isUpdating) {
      return;
    }

    // Guests must sign in before following an artist.
    if (!user) {
      const returnTo = pathname || '/music';

      router.push(
        `/login?next=${encodeURIComponent(returnTo)}`,
      );

      return;
    }

    followRequestInProgress.current = true;
    setIsUpdating(true);
    setFollowError('');

    try {
      const response = isFollowing
        ? await unfollowArtist(Number(artist.id))
        : await followArtist(Number(artist.id));

      const following = Boolean(response.following);
      const nextFollowersCount = response.followers_count;

      setIsFollowing(following);
      setFollowersCount(nextFollowersCount);

      // Update other cards for this artist in the current page.
      window.dispatchEvent(
        new CustomEvent(ARTIST_FOLLOW_STATE_CHANGED_EVENT, {
          detail: {
            artistId: Number(artist.id),
            following,
            followersCount: nextFollowersCount,
          },
        }),
      );
    } catch (error) {
      setFollowError(getErrorMessage(error));
    } finally {
      followRequestInProgress.current = false;
      setIsUpdating(false);
    }
  }

  return (
    <article
      className="
        border-b
        border-light-border-soft
        px-4 py-5
        dark:border-dark-border-soft
        sm:px-6 sm:py-6
      "
    >
      <div className="flex items-center gap-3">
        {/* Artist identity */}
        <Link
          href={artistHref}
          aria-label={`View ${artist.name}'s profile`}
          className="
            relative h-12 w-12
            shrink-0
            overflow-hidden
            rounded-full
            bg-light-surface-soft
            transition-transform duration-200
            hover:scale-[1.02]
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
            dark:bg-dark-surface-soft
          "
        >
          {artist.profile_image ? (
            <Image
              src={artist.profile_image}
              alt=""
              fill
              sizes="48px"
              className="object-cover"
            />
          ) : (
            <div
              className="
                flex h-full w-full
                items-center justify-center
                text-sm font-bold
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {artist.name.charAt(0).toUpperCase()}
            </div>
          )}
        </Link>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <Link
              href={artistHref}
              className="
                min-w-0 truncate
                text-sm font-bold
                text-light-text
                transition-colors
                hover:text-brand-teal-dark
                focus:outline-none
                focus-visible:underline
                dark:text-dark-text
                dark:hover:text-brand-teal-light
              "
            >
              {artist.name}
            </Link>

            {artist.is_verified && (
              <span
                className="
                  inline-flex shrink-0
                  items-center justify-center
                  rounded-full
                  bg-brand-teal
                  text-white
                "
                aria-label="Verified artist"
                title="Verified artist"
              >
                <Check
                  className="h-3 w-3"
                  strokeWidth={2.5}
                />
              </span>
            )}
          </div>

          <p
            className="
              mt-1 text-xs
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            {formatFollowerCount(followersCount)} followers
          </p>
        </div>

        {/* Follow */}
        <button
          type="button"
          onClick={() => {
            void handleFollowToggle();
          }}
          disabled={isUpdating}
          aria-pressed={isFollowing}
          aria-label={
            isFollowing
              ? `Unfollow ${artist.name}`
              : `Follow ${artist.name}`
          }
          className={`
            inline-flex
            min-h-9
            shrink-0
            items-center
            justify-center
            gap-1.5
            rounded-lg
            border
            px-3.5
            py-2
            text-xs
            font-bold
            transition-all duration-200
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
            disabled:cursor-not-allowed
            disabled:opacity-60

            ${
              isFollowing
                ? `
                  border-brand-teal/20
                  bg-brand-teal/10
                  text-brand-teal-dark
                  hover:bg-brand-teal/15
                  dark:border-brand-teal/25
                  dark:bg-brand-teal/15
                  dark:text-brand-teal-light
                  dark:hover:bg-brand-teal/20
                `
                : `
                  border-brand-teal
                  bg-brand-teal
                  text-white
                  hover:bg-brand-teal-dark
                  dark:border-brand-teal
                  dark:bg-brand-teal
                  dark:hover:bg-brand-teal-dark
                `
            }
          `}
        >
          {isUpdating ? (
            <>
              <LoaderCircle
                className="h-3.5 w-3.5 animate-spin"
                aria-hidden="true"
              />
              Please wait
            </>
          ) : isFollowing ? (
            <>
              <UserRoundCheck
                className="h-3.5 w-3.5"
                aria-hidden="true"
              />
              Following
            </>
          ) : (
            <>
              <UserPlus
                className="h-3.5 w-3.5"
                aria-hidden="true"
              />
              Follow
            </>
          )}
        </button>
      </div>

      {followError && (
        <p
          role="alert"
          className="
            mt-3 text-right text-xs
            text-red-600
            dark:text-red-400
          "
        >
          {followError}
        </p>
      )}
    </article>
  );
}

function formatFollowerCount(value: number): string {
  if (value < 1_000) {
    return String(value);
  }

  if (value < 1_000_000) {
    return `${(value / 1_000).toFixed(
      value >= 10_000 ? 0 : 1,
    )}K`;
  }

  return `${(value / 1_000_000).toFixed(
    value >= 10_000_000 ? 0 : 1,
  )}M`;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message || 'The request could not be completed.';
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return 'Something went wrong. Please try again.';
}
