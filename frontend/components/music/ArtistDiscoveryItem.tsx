'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import {
  Check,
  UserPlus,
  UserRoundCheck,
} from 'lucide-react';

import type { CommunityArtist } from '@/lib/music/CommunityPosts';

type ArtistDiscoveryItemProps = {
  artist: CommunityArtist;
};

export default function ArtistDiscoveryItem({
  artist,
}: ArtistDiscoveryItemProps) {
  const [isFollowing, setIsFollowing] =
    useState(false);

  const [isUpdating, setIsUpdating] =
    useState(false);

  const artistHref =
    `/music/artists/${artist.slug}`;

  const handleFollow = async () => {
    if (isUpdating) {
      return;
    }

    setIsUpdating(true);

    try {
      /*
       * Follow API will be connected here once the
       * artist-follow endpoint is finalized.
       *
       * For now this provides the correct interaction
       * and optimistic UI behavior.
       */
      setIsFollowing(
        (currentValue) => !currentValue,
      );
    } finally {
      setIsUpdating(false);
    }
  };

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
      <div
        className="
          flex items-center gap-3
        "
      >
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
              {artist.name
                .charAt(0)
                .toUpperCase()}
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
                <Check className="h-3 w-3" strokeWidth={2.5} />
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
            {formatFollowerCount(
              artist.followers_count,
            )}{' '}
            followers
          </p>
        </div>

        {/* Follow */}
        <button
          type="button"
          onClick={handleFollow}
          disabled={isUpdating}
          aria-pressed={isFollowing}
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
          {isFollowing ? (
            <>
              <UserRoundCheck className="h-3.5 w-3.5" />
              Following
            </>
          ) : (
            <>
              <UserPlus className="h-3.5 w-3.5" />
              Follow
            </>
          )}
        </button>
      </div>
    </article>
  );
}

function formatFollowerCount(
  value: number,
): string {
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