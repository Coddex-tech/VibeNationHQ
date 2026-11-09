'use client';

import { useRef, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  ArrowUpRight,
  Bookmark,
  ChartNoAxesColumn,
  Clock3,
  Heart,
  MessageCircle,
} from 'lucide-react';

import {
  favoriteEditorialArticle,
  likeEditorialArticle,
  unfavoriteEditorialArticle,
  unlikeEditorialArticle,
} from '@/lib/music/EditorialArticles';

import type {
  MusicFeedEditorialArticle,
} from '@/lib/music/MusicFeed';

type MusicEditorialPostProps = {
  article: MusicFeedEditorialArticle;
  onUnfavorited?: () => void;
};

export default function MusicEditorialPost({
  article,
  onUnfavorited,
}: MusicEditorialPostProps) {
  const publishedLabel =
    formatRelativeTime(article.published_at);

  const artwork =
    article.song?.artwork ??
    article.album?.artwork ??
    article.artist?.profile_image ??
    null;

  const musicContext = getMusicContext(article);

  const [liked, setLiked] = useState(article.liked);
  const [likesCount, setLikesCount] = useState(
    article.likes_count,
  );

  const [favorited, setFavorited] = useState(
    article.favorited,
  );
  const [favoritesCount, setFavoritesCount] =
    useState(article.favorites_count);

  const [likePending, setLikePending] = useState(false);
  const [favoritePending, setFavoritePending] =
    useState(false);

  const [interactionError, setInteractionError] =
    useState<string | null>(null);

  const likeLock = useRef(false);
  const favoriteLock = useRef(false);

  async function handleLike() {
    if (likeLock.current) {
      return;
    }

    likeLock.current = true;
    setLikePending(true);
    setInteractionError(null);

    const previousLiked = liked;
    const previousCount = likesCount;
    const nextLiked = !previousLiked;

    setLiked(nextLiked);
    setLikesCount(
      Math.max(
        0,
        previousCount + (nextLiked ? 1 : -1),
      ),
    );

    try {
      const response = nextLiked
        ? await likeEditorialArticle(article.id)
        : await unlikeEditorialArticle(article.id);

      setLiked(response.liked);
      setLikesCount(response.likes_count);
    } catch {
      setLiked(previousLiked);
      setLikesCount(previousCount);
      setInteractionError(
        'Could not update your like. Please try again.',
      );
    } finally {
      likeLock.current = false;
      setLikePending(false);
    }
  }

  async function handleFavorite() {
    if (favoriteLock.current) {
      return;
    }

    favoriteLock.current = true;
    setFavoritePending(true);
    setInteractionError(null);

    const previousFavorited = favorited;
    const previousCount = favoritesCount;
    const nextFavorited = !previousFavorited;

    setFavorited(nextFavorited);
    setFavoritesCount(
      Math.max(
        0,
        previousCount + (nextFavorited ? 1 : -1),
      ),
    );

    try {
      const response = nextFavorited
        ? await favoriteEditorialArticle(article.id)
        : await unfavoriteEditorialArticle(article.id);

      setFavorited(response.favorited);
      setFavoritesCount(response.favorites_count);

      if (!response.favorited) {
        onUnfavorited?.();
      }
    } catch {
      setFavorited(previousFavorited);
      setFavoritesCount(previousCount);
      setInteractionError(
        'Could not update your favorite. Please try again.',
      );
    } finally {
      favoriteLock.current = false;
      setFavoritePending(false);
    }
  }

  const articleUrl =
    `/music/editorial/${article.slug}`;

  const commentsUrl = `${articleUrl}#comments`;

  return (
    <article
      className="
        px-4 py-7
        sm:px-5 sm:py-8
      "
    >
      {/* Editorial identity */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <div
            className="
              flex h-10 w-10 shrink-0
              items-center justify-center
              rounded-xl
              bg-brand-teal/10
              text-xs font-black
              text-brand-teal-dark
              dark:bg-brand-teal/15
              dark:text-brand-teal-light
            "
          >
            VN
          </div>

          <div className="min-w-0">
            <p
              className="
                truncate text-sm font-bold
                text-light-text
                dark:text-dark-text
              "
            >
              VibeNationHQ Editorial
            </p>

            <div
              className="
                mt-0.5 flex items-center gap-2
                text-xs
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              <span>Music News</span>

              <span
                className="
                  h-1 w-1 rounded-full
                  bg-light-text-soft
                  dark:bg-dark-text-soft
                "
                aria-hidden="true"
              />

              <span>{publishedLabel}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Article content */}
      <div className="mt-5">
        <Link
          href={articleUrl}
          className="
            group block
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
            focus-visible:rounded-xl
          "
        >
          <h2
            className="
              text-xl font-black
              leading-tight tracking-tight
              text-light-text
              transition-colors duration-200
              group-hover:text-brand-teal-dark
              dark:text-dark-text
              dark:group-hover:text-brand-teal-light
              sm:text-2xl
            "
          >
            {article.title}
          </h2>

          {article.excerpt && (
            <p
              className="
                mt-3
                text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
                sm:text-[15px]
                sm:leading-7
              "
            >
              {article.excerpt}
            </p>
          )}
        </Link>
      </div>

      {/* Music context */}
      {musicContext && (
        <div className="mt-5">
          <MusicContext
            artwork={artwork}
            title={musicContext.title}
            subtitle={musicContext.subtitle}
            href={musicContext.href}
          />
        </div>
      )}

      {/* Article engagement and navigation */}
      <div
        className="
          mt-5 flex flex-wrap
          items-center justify-between
          gap-3
        "
      >
        <div
          className="
            flex flex-wrap items-center
            gap-x-4 gap-y-3
            text-xs
            text-light-text-soft
            dark:text-dark-text-soft
          "
        >
          {/* Like */}
          <button
            type="button"
            onClick={handleLike}
            disabled={likePending}
            aria-pressed={liked}
            aria-label={
              liked ? 'Unlike article' : 'Like article'
            }
            className={`
              inline-flex items-center gap-1.5
              rounded-full
              transition-colors
              disabled:cursor-not-allowed
              disabled:opacity-60
              ${
                liked
                  ? 'text-rose-600 dark:text-rose-400'
                  : 'hover:text-rose-600 dark:hover:text-rose-400'
              }
            `}
          >
            <Heart
              className="h-4 w-4"
              fill={liked ? 'currentColor' : 'none'}
              strokeWidth={1.8}
            />
            <span>{formatCount(likesCount)}</span>
          </button>

          {/* Comment: opens the article at its comments section */}
          <Link
            href={commentsUrl}
            aria-label={`View ${formatCount(article.comments_count)} comments`}
            className="
              inline-flex items-center gap-1.5
              rounded-full
              transition-colors
              hover:text-brand-teal-dark
              focus:outline-none
              focus-visible:ring-2
              focus-visible:ring-brand-teal/40
              dark:hover:text-brand-teal-light
            "
          >
            <MessageCircle
              className="h-4 w-4"
              strokeWidth={1.8}
            />
            <span>
              {formatCount(article.comments_count)}
            </span>
          </Link>

          {/* Favorite */}
          <button
            type="button"
            onClick={handleFavorite}
            disabled={favoritePending}
            aria-pressed={favorited}
            aria-label={
              favorited
                ? 'Remove article from favorites'
                : 'Add article to favorites'
            }
            className={`
              inline-flex items-center gap-1.5
              rounded-full
              transition-colors
              disabled:cursor-not-allowed
              disabled:opacity-60
              ${
                favorited
                  ? 'text-brand-teal-dark dark:text-brand-teal-light'
                  : 'hover:text-brand-teal-dark dark:hover:text-brand-teal-light'
              }
            `}
          >
            <Bookmark
              className="h-4 w-4"
              fill={favorited ? 'currentColor' : 'none'}
              strokeWidth={1.8}
            />
            <span>{formatCount(favoritesCount)}</span>
          </button>

          {/* Views */}
          <span
            className="inline-flex items-center gap-1.5"
            aria-label={`${formatCount(article.views_count)} views`}
          >
            <ChartNoAxesColumn
              className="h-[15px] w-[15px]"
              strokeWidth={1.8}
            />
            <span>{formatCount(article.views_count)}</span>
          </span>
        </div>

        <Link
          href={articleUrl}
          className="
            inline-flex items-center gap-1.5
            rounded-full
            bg-brand-teal/10
            px-3 py-1.5
            text-xs font-bold
            text-brand-teal-dark
            transition-all duration-200
            hover:bg-brand-teal
            hover:text-white
            dark:bg-brand-teal/15
            dark:text-brand-teal-light
            dark:hover:bg-brand-teal
            dark:hover:text-white
          "
        >
          Read article
          <ArrowUpRight
            className="h-3.5 w-3.5"
            strokeWidth={2}
          />
        </Link>
      </div>

      {interactionError && (
        <p
          role="alert"
          className="
            mt-3 text-sm
            text-red-600
            dark:text-red-400
          "
        >
          {interactionError}
        </p>
      )}
    </article>
  );
}

function MusicContext({
  artwork,
  title,
  subtitle,
  href,
}: {
  artwork: string | null;
  title: string;
  subtitle: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="
      group flex items-center gap-3
      overflow-hidden
      rounded-2xl
      bg-light-surface-soft
      p-3
      transition-colors duration-200
      hover:bg-light-surface
      dark:bg-dark-surface-soft
      dark:hover:bg-dark-surface
    "
    >
      <div
        className="
          relative h-14 w-14
          shrink-0 overflow-hidden
          rounded-xl
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      >
        {artwork ? (
          <Image
            src={artwork}
            alt={`${title} artwork`}
            fill
            sizes="56px"
            className="object-cover"
          />
        ) : (
          <div
            className="
              flex h-full w-full
              items-center justify-center
              text-light-text-soft
              dark:text-dark-text-soft
            "
          >
            <Clock3
              className="h-5 w-5"
              strokeWidth={1.7}
            />
          </div>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <p
          className="
            truncate text-sm font-bold
            text-light-text
            transition-colors
            group-hover:text-brand-teal-dark
            dark:text-dark-text
            dark:group-hover:text-brand-teal-light
          "
        >
          {title}
        </p>

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

      <ArrowUpRight
        className="
          h-4 w-4 shrink-0
          text-light-text-soft
          transition-transform duration-200
          group-hover:-translate-y-0.5
          group-hover:translate-x-0.5
          dark:text-dark-text-soft
        "
        strokeWidth={1.8}
      />
    </Link>
  );
}

function getMusicContext(
  article: MusicFeedEditorialArticle,
): {
  title: string;
  subtitle: string;
  href: string;
} | null {
  if (article.song) {
    const artists = article.song.artists
      .map((artist) => artist.name)
      .join(', ');

    return {
      title: article.song.title,
      subtitle: artists || 'Featured song',
      href: `/music/songs/${article.song.slug}`,
    };
  }

  if (article.album) {
    const artists = article.album.artists
      .map((artist) => artist.name)
      .join(', ');

    return {
      title: article.album.title,
      subtitle: artists || 'Featured album',
      href: `/music/albums/${article.album.slug}`,
    };
  }

  if (article.artist) {
    return {
      title: article.artist.name,
      subtitle: 'Featured artist',
      href: `/music/artists/${article.artist.slug}`,
    };
  }

  return null;
}

function formatRelativeTime(
  value: string | null,
): string {
  if (!value) {
    return 'Recently';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return 'Recently';
  }

  const difference = Date.now() - date.getTime();

  if (difference < 0) {
    return 'Just now';
  }

  const seconds = Math.floor(difference / 1000);

  if (seconds < 60) {
    return 'Just now';
  }

  const minutes = Math.floor(seconds / 60);

  if (minutes < 60) {
    return `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours}h`;
  }

  const days = Math.floor(hours / 24);

  if (days < 30) {
    return `${days}d`;
  }

  const months = Math.floor(days / 30);

  if (months < 12) {
    return `${months}mo`;
  }

  return `${Math.floor(months / 12)}y`;
}

function formatCount(
  count: number,
): string {
  if (count < 1000) {
    return String(count);
  }

  if (count < 1_000_000) {
    return `${formatCompactNumber(
      count / 1000,
    )}K`;
  }

  if (count < 1_000_000_000) {
    return `${formatCompactNumber(
      count / 1_000_000,
    )}M`;
  }

  return `${formatCompactNumber(
    count / 1_000_000_000,
  )}B`;
}

function formatCompactNumber(
  value: number,
): string {
  if (value >= 100) {
    return Math.round(value).toString();
  }

  return value
    .toFixed(1)
    .replace('.0', '');
}