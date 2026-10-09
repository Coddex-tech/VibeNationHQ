'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  ArrowRightIcon,
  MusicIcon,
} from '@/components/Icons';
import {
  getCommunityPosts,
  type CommunityPost,
} from '@/lib/music/CommunityPosts';

function formatPostDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return '';
  }

  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

function getTargetTitle(
  post: CommunityPost,
) {
  const target = post.target;

  if (!target) {
    return null;
  }

  if (target.song) {
    return target.song.title;
  }

  if (target.album) {
    return target.album.title;
  }

  if (target.artist) {
    return target.artist.name;
  }

  return target.title;
}

function getTargetSubtitle(
  post: CommunityPost,
) {
  const target = post.target;

  if (!target) {
    return null;
  }

  if (target.song) {
    const artists = [
      ...target.song.artists,
      ...target.song.featured_artists,
    ];

    if (artists.length === 0) {
      return null;
    }

    return artists
      .map((artist) => artist.name)
      .join(', ');
  }

  if (target.album) {
    if (target.album.artists.length === 0) {
      return null;
    }

    return target.album.artists
      .map((artist) => artist.name)
      .join(', ');
  }

  if (target.artist) {
    return 'Artist';
  }

  return target.artist_name;
}

function getTargetArtwork(
  post: CommunityPost,
) {
  const target = post.target;

  if (!target) {
    return null;
  }

  if (target.song) {
    return target.song.artwork;
  }

  if (target.album) {
    return target.album.artwork;
  }

  if (target.artist) {
    return target.artist.profile_image;
  }

  return target.artwork_url;
}

function CommunityPostCard({
  post,
}: {
  post: CommunityPost;
}) {
  const targetTitle =
    getTargetTitle(post);

  const targetSubtitle =
    getTargetSubtitle(post);

  const targetArtwork =
    getTargetArtwork(post);

  const username =
    post.user.username || 'vibenation';

  return (
    <article
      className="
        rounded-2xl
        border border-light-border
        bg-light-surface
        p-5
        shadow-sm shadow-black/[0.03]
        dark:border-dark-border
        dark:bg-dark-surface
        dark:shadow-black/10
      "
    >
      <div className="flex items-start gap-3">
        {/* User avatar */}
        <div
          className="
            flex h-10 w-10 shrink-0
            items-center justify-center
            rounded-full
            bg-brand-teal/10
            text-sm font-black
            text-brand-teal-dark
            dark:bg-brand-teal/15
            dark:text-brand-teal-light
          "
          aria-hidden="true"
        >
          {username
            .charAt(0)
            .toUpperCase()}
        </div>

        <div className="min-w-0 flex-1">
          {/* User + date */}
          <div
            className="
              flex flex-wrap
              items-center gap-x-2 gap-y-1
            "
          >
            <p
              className="
                break-words
                text-sm font-bold
                text-light-text
                dark:text-dark-text
              "
            >
              @{username}
            </p>

            <span
              aria-hidden="true"
              className="
                text-xs
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              ·
            </span>

            <time
              dateTime={post.created_at}
              className="
                text-xs
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {formatPostDate(
                post.created_at,
              )}
            </time>
          </div>

          {/* Post content */}
          <p
            className="
              mt-3
              whitespace-pre-line
              break-words
              text-sm leading-6
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            {post.content}
          </p>

          {/* Music target */}
          {targetTitle && (
            <div
              className="
                mt-4 flex items-center gap-3
                rounded-xl
                border border-light-border-soft
                bg-light-surface-soft
                p-3
                dark:border-dark-border-soft
                dark:bg-dark-surface-soft
              "
            >
              <div
                className="
                  relative flex h-11 w-11
                  shrink-0 items-center
                  justify-center
                  overflow-hidden rounded-lg
                  bg-light-surface-muted
                  text-light-text-soft
                  dark:bg-dark-surface-muted
                  dark:text-dark-text-soft
                "
              >
                {targetArtwork ? (
                  <Image
                    src={targetArtwork}
                    alt=""
                    fill
                    sizes="44px"
                    className="object-cover"
                  />
                ) : (
                  <MusicIcon className="h-5 w-5" />
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p
                  className="
                    truncate
                    text-sm font-bold
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  {targetTitle}
                </p>

                {targetSubtitle && (
                  <p
                    className="
                      mt-0.5 truncate
                      text-xs
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    {targetSubtitle}
                  </p>
                )}
              </div>

              {post.rating !== null && (
                <div
                  className="
                    shrink-0
                    rounded-full
                    bg-brand-teal/10
                    px-2.5 py-1
                    text-xs font-bold
                    text-brand-teal-dark
                    dark:bg-brand-teal/15
                    dark:text-brand-teal-light
                  "
                >
                  {Number(post.rating).toFixed(1)}
                </div>
              )}
            </div>
          )}

          {/* Engagement */}
          <div
            className="
              mt-4 flex flex-wrap
              items-center gap-x-4 gap-y-2
              text-xs font-medium
              text-light-text-soft
              dark:text-dark-text-soft
            "
          >
            <span>
              {post.likes_count}{' '}
              {post.likes_count === 1
                ? 'like'
                : 'likes'}
            </span>

            <span>
              {post.comments_count}{' '}
              {post.comments_count === 1
                ? 'comment'
                : 'comments'}
            </span>

            {post.is_edited && (
              <span>Edited</span>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

function CommunitySkeletonCard() {
  return (
    <div
      className="
        animate-pulse
        rounded-2xl
        border border-light-border
        bg-light-surface
        p-5
        dark:border-dark-border
        dark:bg-dark-surface
      "
    >
      <div className="flex items-start gap-3">
        <div
          className="
            h-10 w-10 shrink-0
            rounded-full
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div className="min-w-0 flex-1">
          <div
            className="
              h-4 w-32 max-w-full rounded
              bg-light-surface-muted
              dark:bg-dark-surface-muted
            "
          />

          <div
            className="
              mt-4 h-4 w-full rounded
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />

          <div
            className="
              mt-2 h-4 w-4/5 rounded
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />

          <div
            className="
              mt-4 h-14 w-full rounded-xl
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />
        </div>
      </div>
    </div>
  );
}

export default function HomeCommunitySection() {
  const [posts, setPosts] =
    useState<CommunityPost[]>([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadCommunityPosts() {
      setIsLoading(true);
      setError(null);

      try {
        const response =
          await getCommunityPosts({
            pageSize: 3,
          });

        if (!isMounted) {
          return;
        }

        setPosts(response.results);
      } catch {
        if (!isMounted) {
          return;
        }

        setError(
          'Unable to load community conversations right now.',
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadCommunityPosts();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section
      aria-labelledby="home-community-heading"
      className="
        border-b border-light-border
        bg-light-bg
        dark:border-dark-border
        dark:bg-dark-bg
      "
    >
      <div
        className="
          mx-auto w-full max-w-7xl
          px-5 py-14
          sm:px-6 sm:py-16
          lg:px-8 lg:py-20
        "
      >
        <div
          className="
            grid items-start gap-10
            lg:grid-cols-[0.85fr_1.15fr]
            lg:gap-16
          "
        >
          {/* Section introduction */}
          <FadeIn>
            <div className="max-w-xl">
              <div
                className="
                  mb-3 inline-flex
                  items-center gap-2
                  text-xs font-bold
                  uppercase tracking-wider
                  text-brand-teal-dark
                  dark:text-brand-teal-light
                "
              >
                <span
                  aria-hidden="true"
                  className="
                    h-1.5 w-1.5
                    rounded-full
                    bg-brand-teal
                  "
                />

                Community
              </div>

              <h2
                id="home-community-heading"
                className="
                  text-2xl font-black
                  tracking-tight
                  text-light-text
                  dark:text-dark-text
                  sm:text-3xl
                "
              >
                Music is better when
                there&apos;s a conversation.
              </h2>

              <p
                className="
                  mt-4 text-sm leading-7
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-base
                "
              >
                Find a song, share what it
                means to you, rate it, and see
                what other people are saying.
                VibeNationHQ brings music
                discovery and genuine
                conversation together.
              </p>

              <Link
                href="/music"
                className="
                  mt-6 inline-flex
                  items-center gap-2
                  rounded-xl
                  bg-brand-teal
                  px-4 py-2.5
                  text-sm font-bold
                  text-white
                  shadow-sm
                  shadow-brand-teal/20
                  transition-all duration-200
                  hover:bg-brand-teal-dark
                  active:scale-[0.99]
                "
              >
                Explore the community
                <ArrowRightIcon className="h-4 w-4" />
              </Link>
            </div>
          </FadeIn>

          {/* Community feed */}
          <FadeIn delay={0.1}>
            {isLoading ? (
              <div className="space-y-4">
                <CommunitySkeletonCard />
                <CommunitySkeletonCard />
              </div>
            ) : error ? (
              <div
                role="alert"
                className="
                  rounded-2xl
                  border border-red-200
                  bg-red-50
                  px-5 py-6
                  dark:border-red-500/20
                  dark:bg-red-500/10
                "
              >
                <p
                  className="
                    text-sm font-bold
                    text-red-700
                    dark:text-red-300
                  "
                >
                  Community unavailable
                </p>

                <p
                  className="
                    mt-1 text-sm leading-6
                    text-red-600
                    dark:text-red-300/80
                  "
                >
                  We couldn&apos;t load the
                  latest conversations. Please
                  try again later.
                </p>
              </div>
            ) : posts.length === 0 ? (
              <div
                className="
                  rounded-2xl
                  border border-light-border
                  bg-light-surface
                  px-6 py-10
                  text-center
                  shadow-sm shadow-black/[0.03]
                  dark:border-dark-border
                  dark:bg-dark-surface
                  dark:shadow-black/10
                "
              >
                <div
                  className="
                    mx-auto flex h-12 w-12
                    items-center justify-center
                    rounded-xl
                    bg-brand-teal/10
                    text-brand-teal
                    dark:bg-brand-teal/15
                  "
                >
                  <MusicIcon className="h-6 w-6" />
                </div>

                <h3
                  className="
                    mt-4 text-base font-bold
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  The conversation starts here.
                </h3>

                <p
                  className="
                    mx-auto mt-2 max-w-md
                    text-sm leading-6
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Community conversations will
                  appear here once people start
                  sharing their thoughts on music.
                </p>

                <Link
                  href="/music"
                  className="
                    mt-5 inline-flex
                    items-center gap-2
                    text-sm font-bold
                    text-brand-teal-dark
                    hover:text-brand-teal
                    dark:text-brand-teal-light
                  "
                >
                  Explore music
                  <ArrowRightIcon className="h-4 w-4" />
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <CommunityPostCard
                    key={post.id}
                    post={post}
                  />
                ))}

                <div className="pt-1">
                  <Link
                    href="/music"
                    className="
                      inline-flex
                      items-center gap-2
                      text-sm font-bold
                      text-brand-teal-dark
                      hover:text-brand-teal
                      dark:text-brand-teal-light
                    "
                  >
                    See more community
                    <ArrowRightIcon className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            )}
          </FadeIn>
        </div>
      </div>
    </section>
  );
}