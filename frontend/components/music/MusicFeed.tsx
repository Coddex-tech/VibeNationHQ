
'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useMemo, useState } from 'react';
import {
  Disc3,
  Music2,
  Plus,
  Sparkles,
} from 'lucide-react';

import type {
  MusicFeedItem,
  MusicFeedResponse,
} from '@/lib/music/MusicFeed';

import MusicEditorialPost from './MusicEditorialPost';
import MusicPost from './MusicPost';
import ArtistDiscoveryItem from './ArtistDiscoveryItem';
import MusicDiscoveryItem from './MusicDiscoveryItem';

type MusicFeedProps = {
  initialFeed: MusicFeedResponse;
};

export default function MusicFeed({
  initialFeed,
}: MusicFeedProps) {
  const [feed] =
    useState<MusicFeedResponse>(initialFeed);

  const [showCreateButton, setShowCreateButton] =
    useState(true);

  /*
   * Only the first community post from each author
   * receives a Follow button.
   *
   * Authors already being followed and the current
   * user's own posts do not receive one.
   *
   * This map is calculated from the initial feed and
   * remains stable while individual post components
   * synchronize follow changes.
   */
  const followButtonPostIds = useMemo(() => {
    const eligiblePostIds = new Set<number>();
    const seenAuthorIds = new Set<number>();

    for (const item of feed.results) {
      if (item.content_type !== 'community_post') {
        continue;
      }

      const post = item.content;
      const authorId = Number(post.user.id);

      if (
        !Number.isFinite(authorId) ||
        authorId <= 0 ||
        post.user.is_following ||
        seenAuthorIds.has(authorId)
      ) {
        continue;
      }

      seenAuthorIds.add(authorId);
      eligiblePostIds.add(Number(post.id));
    }

    return eligiblePostIds;
  }, [feed.results]);

  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDelta =
        currentScrollY - lastScrollY;

      /*
       * Only filter tiny touchpad/trackpad jitter.
       *
       * A real change of direction immediately
       * controls the button.
       */
      if (scrollDelta > 4) {
        setShowCreateButton(false);
      } else if (scrollDelta < -4) {
        setShowCreateButton(true);
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener(
      'scroll',
      handleScroll,
      { passive: true },
    );

    return () => {
      window.removeEventListener(
        'scroll',
        handleScroll,
      );
    };
  }, []);

  return (
    <>
      <section
        aria-label="Music feed"
        className="w-full"
      >
        {feed.results.length === 0 ? (
          <MusicFeedEmptyState />
        ) : (
          <div>
            {feed.results.map((item) => (
              <MusicFeedItemView
                key={`${item.content_type}-${item.content.id}`}
                item={item}
                showFollowButton={
                  item.content_type === 'community_post' &&
                  followButtonPostIds.has(
                    Number(item.content.id),
                  )
                }
              />
            ))}

            {feed.has_more && (
              <div
                className="
                  border-t border-light-border-soft
                  px-5 py-10
                  text-center
                  dark:border-dark-border-soft
                "
              >
                <div
                  className="
                    mx-auto flex h-10 w-10
                    items-center justify-center
                    rounded-full
                    bg-brand-teal/10
                    text-brand-teal
                    dark:bg-brand-teal/15
                  "
                >
                  <Sparkles className="h-5 w-5" />
                </div>

                <p
                  className="
                    mt-3 text-sm font-semibold
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  More music waiting for you
                </p>

                <p
                  className="
                    mt-1 text-xs leading-5
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Keep exploring to discover more
                  songs, artists, and conversations.
                </p>
              </div>
            )}
          </div>
        )}
      </section>

      <Link
        href="/music/create"
        aria-label="Create music post"
        className={`
          fixed
          right-5
          bottom-[calc(1.25rem+env(safe-area-inset-bottom))]
          z-50

          flex
          h-14
          w-14
          items-center
          justify-center

          rounded-full
          bg-brand-teal
          text-white

          shadow-lg
          shadow-brand-teal/20

          transition-all
          duration-250
          ease-out

          hover:scale-[1.04]
          hover:shadow-xl
          hover:shadow-brand-teal/25

          active:scale-95

          focus:outline-none
          focus-visible:ring-4
          focus-visible:ring-brand-teal/25
          focus-visible:ring-offset-2
          focus-visible:ring-offset-light-bg

          dark:focus-visible:ring-offset-dark-bg

          sm:right-7
          sm:bottom-[calc(1.75rem+env(safe-area-inset-bottom))]

          ${
            showCreateButton
              ? `
                translate-y-0
                scale-100
                opacity-100
                pointer-events-auto
              `
              : `
                translate-y-24
                scale-95
                opacity-0
                pointer-events-none
              `
          }
        `}
      >
        <Plus
          className="
            h-6 w-6
            transition-transform
            duration-200
          "
          strokeWidth={2.5}
        />
      </Link>
    </>
  );
}

type MusicFeedItemViewProps = {
  item: MusicFeedItem;
  showFollowButton: boolean;
};

function MusicFeedItemView({
  item,
  showFollowButton,
}: MusicFeedItemViewProps) {
  switch (item.content_type) {
    case 'community_post':
      return (
        <MusicPost
          post={item.content}
          showFollowButton={showFollowButton}
        />
      );

    case 'editorial':
      return (
        <MusicEditorialPost
          article={item.content}
        />
      );

    case 'song':
      return (
        <MusicDiscoveryItem
          type="song"
          item={item.content}
        />
      );

    case 'album':
      return (
        <MusicDiscoveryItem
          type="album"
          item={item.content}
        />
      );

    case 'artist':
      return (
        <ArtistDiscoveryItem
          artist={item.content}
        />
      );

    default:
      return null;
  }
}

type DiscoveryFeedItemProps = {
  type: 'Song' | 'Album' | 'Artist';
  title: string;
  subtitle: string;
  artwork: string | null;
  href: string;
};

function DiscoveryFeedItem({
  type,
  title,
  subtitle,
  artwork,
  href,
}: DiscoveryFeedItemProps) {
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
        <div
          className="
            relative h-14 w-14 shrink-0
            overflow-hidden rounded-xl
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        >
          {artwork ? (
            <Image
              src={artwork}
              alt=""
              fill
              sizes="56px"
              className="object-cover"
            />
          ) : (
            <div
              className="
                flex h-full w-full
                items-center justify-center
                text-xs font-bold
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              VN
            </div>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div
            className="
              flex items-center gap-2
            "
          >
            <span
              className="
                inline-flex items-center gap-1
                text-[11px] font-semibold
                uppercase tracking-wide
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              {type === 'Song' && (
                <Music2 className="h-3.5 w-3.5" />
              )}

              {type === 'Album' && (
                <Disc3 className="h-3.5 w-3.5" />
              )}

              {type === 'Artist' && (
                <Sparkles className="h-3.5 w-3.5" />
              )}

              {type}
            </span>
          </div>

          <h3
            className="
              mt-1 truncate
              text-sm font-bold
              text-light-text
              dark:text-dark-text
            "
          >
            {title}
          </h3>

          <p
            className="
              mt-0.5 truncate
              text-xs
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            {subtitle}
          </p>
        </div>

        <Link
          href={href}
          className="
            shrink-0
            rounded-lg
            border border-light-border
            px-3 py-2
            text-xs font-semibold
            text-light-text
            transition-colors
            hover:border-brand-teal/30
            hover:bg-brand-teal/5
            hover:text-brand-teal-dark
            dark:border-dark-border
            dark:text-dark-text
            dark:hover:border-brand-teal/30
            dark:hover:bg-brand-teal/10
            dark:hover:text-brand-teal-light
          "
        >
          View
        </Link>
      </div>
    </article>
  );
}

function MusicFeedEmptyState() {
  return (
    <div
      className="
        border-b border-light-border-soft
        px-5 py-16
        text-center
        dark:border-dark-border-soft
      "
    >
      <div
        className="
          mx-auto flex h-14 w-14
          items-center justify-center
          rounded-2xl
          bg-brand-teal/10
          text-brand-teal
          dark:bg-brand-teal/15
        "
      >
        <Music2 className="h-6 w-6" />
      </div>

      <h2
        className="
          mt-5 text-lg font-bold
          text-light-text
          dark:text-dark-text
        "
      >
        Your music feed is quiet
      </h2>

      <p
        className="
          mx-auto mt-2 max-w-md
          text-sm leading-6
          text-light-text-muted
          dark:text-dark-text-muted
        "
      >
        Follow artists, discover songs, and join
        conversations to start building your feed.
      </p>
    </div>
  );
}

function getArtistNames(
  artists: {
    name: string;
  }[],
): string {
  if (artists.length === 0) {
    return 'Unknown artist';
  }

  return artists
    .map((artist) => artist.name)
    .join(', ');
}

function formatCount(value: number): string {
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
