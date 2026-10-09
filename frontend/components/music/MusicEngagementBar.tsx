'use client';

import {
  Bookmark,
  Heart,
  MessageCircle,
  Share2,
  ChartNoAxesColumn,
} from 'lucide-react';
import { useState } from 'react';

import { apiRequest } from '@/lib/api';

type MusicEngagementBarProps = {
  postId: number;
  likesCount: number;
  isLiked: boolean;
  isFavorited: boolean;
  favoritesCount: number;
  commentsCount: number;
  viewsCount: number;
};

type CommunityPostLikeResponse = {
  liked: boolean;
  likes_count: number;
};

type CommunityPostFavoriteResponse = {
  favorited: boolean;
  favorites_count: number;
};

export default function MusicEngagementBar({
  postId,
  likesCount,
  isLiked: initialIsLiked,
  isFavorited: initialIsFavorited,
  favoritesCount,
  commentsCount,
  viewsCount,
}: MusicEngagementBarProps) {
  const [isLiked, setIsLiked] =
    useState(initialIsLiked);

  const [isLikeUpdating, setIsLikeUpdating] =
    useState(false);

  const [isSaved, setIsSaved] =
    useState(initialIsFavorited);

  const [isSaveUpdating, setIsSaveUpdating] =
    useState(false);

  const [likeCount, setLikeCount] =
    useState(likesCount);

  const [favoriteCount, setFavoriteCount] =
    useState(favoritesCount);

  const handleLike = async () => {
    if (isLikeUpdating) {
      return;
    }

    setIsLikeUpdating(true);

    try {
      const response =
        await apiRequest<CommunityPostLikeResponse>(
          `/api/v1/music/community/posts/${postId}/like/`,
          {
            method: isLiked
              ? 'DELETE'
              : 'POST',
          },
        );

      setIsLiked(response.liked);
      setLikeCount(response.likes_count);
    } catch {
      // Keep the current UI state unchanged.
    } finally {
      setIsLikeUpdating(false);
    }
  };

  const handleSave = async () => {
    if (isSaveUpdating) {
      return;
    }

    setIsSaveUpdating(true);

    try {
      const response =
        await apiRequest<CommunityPostFavoriteResponse>(
          `/api/v1/music/community/posts/${postId}/favorite/`,
          {
            method: isSaved
              ? 'DELETE'
              : 'POST',
          },
        );

      setIsSaved(response.favorited);
      setFavoriteCount(response.favorites_count);
    } catch {
      // Keep the current UI state unchanged.
    } finally {
      setIsSaveUpdating(false);
    }
  };

  const handleShare = async () => {
    const shareUrl =
      typeof window !== 'undefined'
        ? `${window.location.origin}/music/posts/${postId}`
        : '';

    if (
      typeof navigator !== 'undefined' &&
      navigator.share
    ) {
      try {
        await navigator.share({
          title: 'VibeNationHQ',
          url: shareUrl,
        });
      } catch {
        // User cancelled the native share sheet.
      }

      return;
    }

    if (
      typeof navigator !== 'undefined' &&
      navigator.clipboard &&
      shareUrl
    ) {
      try {
        await navigator.clipboard.writeText(
          shareUrl,
        );
      } catch {
        // Clipboard access may be unavailable.
      }
    }
  };

  return (
    <div
      className="
        flex items-center justify-between gap-4
        text-light-text-soft
        dark:text-dark-text-soft
      "
    >
      <div
        className="
          flex min-w-0
          items-center gap-1
          sm:gap-2
        "
      >
        {/* Like */}
        <button
          type="button"
          onClick={handleLike}
          disabled={isLikeUpdating}
          aria-label={
            isLiked
              ? 'Unlike post'
              : 'Like post'
          }
          aria-pressed={isLiked}
          className={`
            inline-flex
            min-h-9 min-w-9
            items-center justify-center
            gap-1.5
            rounded-full
            px-2.5
            text-xs font-medium
            transition-all duration-200
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
            disabled:cursor-wait
            disabled:opacity-60
            ${
              isLiked
                ? `
                  bg-red-500/10
                  text-red-500
                  dark:bg-red-500/10
                  dark:text-red-400
                `
                : `
                  hover:bg-light-surface-soft
                  hover:text-light-text
                  dark:hover:bg-dark-surface-soft
                  dark:hover:text-dark-text
                `
            }
          `}
        >
          <Heart
            className="h-[17px] w-[17px]"
            fill={
              isLiked
                ? 'currentColor'
                : 'none'
            }
            strokeWidth={1.9}
          />

          {likeCount > 0 && (
            <span>
              {formatCount(likeCount)}
            </span>
          )}
        </button>

        {/* Comments */}
        <button
          type="button"
          aria-label={
            commentsCount === 1
              ? 'View 1 comment'
              : `View ${commentsCount} comments`
          }
          className="
            inline-flex
            min-h-9 min-w-9
            items-center justify-center
            gap-1.5
            rounded-full
            px-2.5
            text-xs font-medium
            transition-colors duration-200
            hover:bg-light-surface-soft
            hover:text-light-text
            dark:hover:bg-dark-surface-soft
            dark:hover:text-dark-text
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
          "
        >
          <MessageCircle
            className="h-[17px] w-[17px]"
            strokeWidth={1.9}
          />

          {commentsCount > 0 && (
            <span>
              {formatCount(commentsCount)}
            </span>
          )}
        </button>

        {/* Save */}
        <button
          type="button"
          onClick={handleSave}
          disabled={isSaveUpdating}
          aria-label={
            isSaved
              ? 'Remove post from saved'
              : 'Save post'
          }
          aria-pressed={isSaved}
          className={`
            inline-flex
            min-h-9 min-w-9
            items-center justify-center
            gap-1.5
            rounded-full
            px-2.5
            text-xs font-medium
            transition-all duration-200
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
            disabled:cursor-wait
            disabled:opacity-60
            ${
              isSaved
                ? `
                  bg-brand-teal/10
                  text-brand-teal-dark
                  dark:bg-brand-teal/15
                  dark:text-brand-teal-light
                `
                : `
                  hover:bg-light-surface-soft
                  hover:text-light-text
                  dark:hover:bg-dark-surface-soft
                  dark:hover:text-dark-text
                `
            }
          `}
        >
          <Bookmark
            className="h-[17px] w-[17px]"
            fill={
              isSaved
                ? 'currentColor'
                : 'none'
            }
            strokeWidth={1.9}
          />

          {favoriteCount > 0 && (
            <span>
              {formatCount(favoriteCount)}
            </span>
          )}
        </button>

        {/* Share */}
        <button
          type="button"
          onClick={handleShare}
          aria-label="Share post"
          className="
            inline-flex
            min-h-9 min-w-9
            items-center justify-center
            rounded-full
            px-2.5
            transition-colors duration-200
            hover:bg-light-surface-soft
            hover:text-light-text
            dark:hover:bg-dark-surface-soft
            dark:hover:text-dark-text
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
          "
        >
          <Share2
            className="h-[17px] w-[17px]"
            strokeWidth={1.9}
          />
        </button>
      </div>

      {/* Views + future actions */}
      <div className="flex shrink-0 items-center gap-1">
        <div
          className="
            inline-flex items-center gap-1.5
            px-2
            text-[11px]
            font-medium
            text-light-text-soft
            dark:text-dark-text-soft
          "
          aria-label={`${viewsCount} views`}
        >
          <ChartNoAxesColumn
            className="h-[15px] w-[15px]"
            strokeWidth={1.8}
          />

          <span>
            {formatCount(viewsCount)}
          </span>
        </div>
      </div>
    </div>
  );
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

  if (value >= 10) {
    return value.toFixed(1).replace('.0', '');
  }

  return value.toFixed(1).replace('.0', '');
}