'use client';

import {
  Bookmark,
  Eye,
  Heart,
  MessageCircle,
  Share2,
  ChartNoAxesColumn,
} from 'lucide-react';
import { useEffect, useState } from 'react';

import { apiRequest } from '@/lib/api';

type MusicEngagementBarProps = {
  postId: number;
  likesCount: number;
  isLiked: boolean;
  isFavorited: boolean;
  favoritesCount: number;
  commentsCount: number;
  viewsCount: number;
  variant?: 'feed' | 'detail';
  onCommentsClick?: () => void;
};

type CommunityPostLikeResponse = {
  liked: boolean;
  likes_count: number;
};

type CommunityPostFavoriteResponse = {
  favorited: boolean;
  favorites_count: number;
};

type CommunityPostViewUpdatedEvent = CustomEvent<{
  postId: number;
  viewsCount: number;
}>;

export default function MusicEngagementBar({
  postId,
  likesCount,
  isLiked: initialIsLiked,
  isFavorited: initialIsFavorited,
  favoritesCount,
  commentsCount,
  viewsCount,
  variant = 'feed',
  onCommentsClick,
}: MusicEngagementBarProps) {
  const [isLiked, setIsLiked] = useState(initialIsLiked);
  const [isLikeUpdating, setIsLikeUpdating] = useState(false);

  const [isSaved, setIsSaved] = useState(initialIsFavorited);
  const [isSaveUpdating, setIsSaveUpdating] = useState(false);

  const [likeCount, setLikeCount] = useState(likesCount);
  const [favoriteCount, setFavoriteCount] = useState(favoritesCount);
  const [currentViewsCount, setCurrentViewsCount] = useState(viewsCount);

  useEffect(() => {
    setIsLiked(initialIsLiked);
    setLikeCount(likesCount);
  }, [initialIsLiked, likesCount]);

  useEffect(() => {
    setIsSaved(initialIsFavorited);
    setFavoriteCount(favoritesCount);
  }, [initialIsFavorited, favoritesCount]);

  useEffect(() => {
    setCurrentViewsCount(viewsCount);
  }, [viewsCount]);

  useEffect(() => {
    function handleViewUpdate(event: Event) {
      const customEvent = event as CommunityPostViewUpdatedEvent;

      if (customEvent.detail?.postId !== postId) {
        return;
      }

      setCurrentViewsCount(customEvent.detail.viewsCount);
    }

    window.addEventListener(
      'community-post-view-updated',
      handleViewUpdate,
    );

    return () => {
      window.removeEventListener(
        'community-post-view-updated',
        handleViewUpdate,
      );
    };
  }, [postId]);

  const handleLike = async () => {
    if (isLikeUpdating) {
      return;
    }

    setIsLikeUpdating(true);

    try {
      const response = await apiRequest<CommunityPostLikeResponse>(
        `/api/v1/music/community/posts/${postId}/like/`,
        {
          method: isLiked ? 'DELETE' : 'POST',
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
            method: isSaved ? 'DELETE' : 'POST',
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
      typeof window !== 'undefined' ? window.location.href : '';

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
        // The user cancelled the native share sheet, or sharing failed.
      }

      return;
    }

    if (
      typeof navigator !== 'undefined' &&
      navigator.clipboard &&
      shareUrl
    ) {
      try {
        await navigator.clipboard.writeText(shareUrl);
      } catch {
        // Clipboard access may be unavailable.
      }
    }
  };

  return (
    <div
      className={`
        text-light-text-soft
        dark:text-dark-text-soft
        ${variant === 'detail' ? 'space-y-3' : ''}
      `}
    >
      {variant === 'detail' && (
        <div
          className="
            flex items-center gap-2
            border-b border-light-border
            pb-3 text-sm font-medium
            text-light-text-soft
            dark:border-dark-border
            dark:text-dark-text-soft
          "
          aria-label={`${formatCount(currentViewsCount)} views`}
        >
          <Eye
            className="h-[18px] w-[18px]"
            strokeWidth={1.9}
            aria-hidden="true"
          />

          <span>{formatCount(currentViewsCount)} views</span>
        </div>
      )}

      <div
        className={`
          flex flex-wrap items-center
          ${variant === 'detail' ? 'gap-2' : ''}
        `}
      >
        <div
          className="
            flex min-w-0 flex-wrap
            items-center gap-1 sm:gap-2
          "
        >
          <button
            type="button"
            onClick={handleLike}
            disabled={isLikeUpdating}
            aria-label={isLiked ? 'Unlike post' : 'Like post'}
            aria-pressed={isLiked}
            className={`
              inline-flex min-h-9 min-w-9
              items-center justify-center gap-1.5
              rounded-full px-2.5
              text-xs font-medium
              transition-all duration-200
              focus:outline-none
              focus-visible:ring-4
              focus-visible:ring-brand-teal/15
              disabled:cursor-wait disabled:opacity-60
              ${
                isLiked
                  ? 'bg-red-500/10 text-red-500 dark:text-red-400'
                  : 'hover:bg-light-surface-soft hover:text-light-text dark:hover:bg-dark-surface-soft dark:hover:text-dark-text'
              }
            `}
          >
            <Heart
              className="h-[17px] w-[17px]"
              fill={isLiked ? 'currentColor' : 'none'}
              strokeWidth={1.9}
            />

            {likeCount > 0 && <span>{formatCount(likeCount)}</span>}
          </button>

          <button
            type="button"
            onClick={onCommentsClick}
            aria-label={
              commentsCount === 1
                ? 'View 1 comment'
                : `View ${commentsCount} comments`
            }
            className="
              inline-flex min-h-9 min-w-9
              items-center justify-center gap-1.5
              rounded-full px-2.5
              text-xs font-medium
              transition-colors duration-200
              hover:bg-light-surface-soft hover:text-light-text
              dark:hover:bg-dark-surface-soft dark:hover:text-dark-text
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
              <span>{formatCount(commentsCount)}</span>
            )}
          </button>

          <button
            type="button"
            onClick={handleSave}
            disabled={isSaveUpdating}
            aria-label={isSaved ? 'Remove post from saved' : 'Save post'}
            aria-pressed={isSaved}
            className={`
              inline-flex min-h-9 min-w-9
              items-center justify-center gap-1.5
              rounded-full px-2.5
              text-xs font-medium
              transition-all duration-200
              focus:outline-none
              focus-visible:ring-4
              focus-visible:ring-brand-teal/15
              disabled:cursor-wait disabled:opacity-60
              ${
                isSaved
                  ? 'bg-brand-teal/10 text-brand-teal-dark dark:bg-brand-teal/15 dark:text-brand-teal-light'
                  : 'hover:bg-light-surface-soft hover:text-light-text dark:hover:bg-dark-surface-soft dark:hover:text-dark-text'
              }
            `}
          >
            <Bookmark
              className="h-[17px] w-[17px]"
              fill={isSaved ? 'currentColor' : 'none'}
              strokeWidth={1.9}
            />

            {favoriteCount > 0 && (
              <span>{formatCount(favoriteCount)}</span>
            )}
          </button>

          <button
            type="button"
            onClick={handleShare}
            aria-label="Share post"
            className="
              inline-flex min-h-9 min-w-9
              items-center justify-center
              rounded-full px-2.5
              transition-colors duration-200
              hover:bg-light-surface-soft hover:text-light-text
              dark:hover:bg-dark-surface-soft dark:hover:text-dark-text
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

          {variant === 'feed' && (
            <div
              className="
                inline-flex min-h-9
                items-center gap-1.5
                rounded-full px-2.5
                text-xs font-medium
                text-light-text-soft dark:text-dark-text-soft
              "
              aria-label={`${formatCount(currentViewsCount)} views`}
            >
              <ChartNoAxesColumn
                className="h-[17px] w-[17px]"
                strokeWidth={1.9}
                aria-hidden="true"
              />

              <span>{formatCount(currentViewsCount)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function formatCount(count: number): string {
  if (count < 1_000) {
    return String(count);
  }

  if (count < 1_000_000) {
    return `${formatCompactNumber(count / 1_000)}K`;
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

  return value.toFixed(1).replace('.0', '');
}