'use client';

import {
  Bookmark,
  ChartNoAxesColumn,
  Eye,
  Heart,
  MessageCircle,
  Share2,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { apiRequest, ApiError } from '@/lib/api';

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
  likeCommentOnly?: boolean;
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
  likeCommentOnly = false,
}: MusicEngagementBarProps) {
  const [isLiked, setIsLiked] = useState(initialIsLiked);
  const [isLikeUpdating, setIsLikeUpdating] = useState(false);

  const [isSaved, setIsSaved] = useState(initialIsFavorited);
  const [isSaveUpdating, setIsSaveUpdating] = useState(false);

  const [likeCount, setLikeCount] = useState(likesCount);
  const [favoriteCount, setFavoriteCount] = useState(favoritesCount);
  const [currentViewsCount, setCurrentViewsCount] = useState(viewsCount);
  const [likeError, setLikeError] = useState('');

  const likeLock = useRef(false);
  const saveLock = useRef(false);
  const activePostId = useRef(postId);

  // Reset state when this component starts representing a different post.
  // Do not repeatedly overwrite optimistic state with props for the same post.
  useEffect(() => {
    if (activePostId.current === postId) return;

    activePostId.current = postId;
    likeLock.current = false;
    saveLock.current = false;

    setIsLiked(initialIsLiked);
    setIsLikeUpdating(false);
    setLikeCount(likesCount);
    setLikeError('');

    setIsSaved(initialIsFavorited);
    setIsSaveUpdating(false);
    setFavoriteCount(favoritesCount);

    setCurrentViewsCount(viewsCount);
  }, [
    postId,
    initialIsLiked,
    likesCount,
    initialIsFavorited,
    favoritesCount,
    viewsCount,
  ]);

  // Reconcile server-provided counts when they change, without replacing
  // the user's in-flight optimistic like state.
  useEffect(() => {
    if (likeLock.current) return;
    setLikeCount(likesCount);
  }, [likesCount, postId]);

  useEffect(() => {
    if (likeLock.current) return;
    setIsLiked(initialIsLiked);
  }, [initialIsLiked, postId]);

  useEffect(() => {
    if (saveLock.current) return;
    setIsSaved(initialIsFavorited);
    setFavoriteCount(favoritesCount);
  }, [initialIsFavorited, favoritesCount, postId]);

  useEffect(() => {
    setCurrentViewsCount(viewsCount);
  }, [viewsCount, postId]);

  useEffect(() => {
    function handleViewUpdate(event: Event) {
      const customEvent = event as CommunityPostViewUpdatedEvent;

      if (customEvent.detail?.postId !== postId) return;

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
    if (likeLock.current) return;

    likeLock.current = true;
    setIsLikeUpdating(true);
    setLikeError('');

    const requestedPostId = postId;
    const previousLiked = isLiked;
    const previousCount = likeCount;
    const nextLiked = !previousLiked;

    setIsLiked(nextLiked);
    setLikeCount(
      Math.max(0, previousCount + (nextLiked ? 1 : -1)),
    );

    try {
      const response = await apiRequest<CommunityPostLikeResponse>(
        `/api/v1/music/community/posts/${requestedPostId}/like/`,
        {
          method: nextLiked ? 'POST' : 'DELETE',
        },
      );

      if (activePostId.current !== requestedPostId) return;

      setIsLiked(response.liked);
      setLikeCount(response.likes_count);
    } catch (error) {
      if (activePostId.current !== requestedPostId) return;

      const message = getRequestErrorMessage(error);
      const normalizedMessage = message.toLowerCase();

      // The server already has this like. Treat the duplicate POST as
      // reconciliation, not as a reason to revert the UI to "not liked".
      if (
        nextLiked &&
        (normalizedMessage.includes('already liked') ||
          normalizedMessage.includes('already like'))
      ) {
        setIsLiked(true);
        setLikeCount(previousCount);
        setLikeError('');
      } else if (
        !nextLiked &&
        (normalizedMessage.includes('not liked') ||
          normalizedMessage.includes('already unliked') ||
          normalizedMessage.includes('no like'))
      ) {
        setIsLiked(false);
        setLikeCount(Math.max(0, previousCount - 1));
        setLikeError('');
      } else {
        setIsLiked(previousLiked);
        setLikeCount(previousCount);
        setLikeError(message);
        console.error('Failed to update community post like:', error);
      }
    } finally {
      if (activePostId.current === requestedPostId) {
        likeLock.current = false;
        setIsLikeUpdating(false);
      }
    }
  };

  const handleSave = async () => {
    if (saveLock.current) return;

    saveLock.current = true;
    setIsSaveUpdating(true);

    const requestedPostId = postId;
    const previousSaved = isSaved;
    const previousCount = favoriteCount;
    const nextSaved = !previousSaved;

    setIsSaved(nextSaved);
    setFavoriteCount(
      Math.max(0, previousCount + (nextSaved ? 1 : -1)),
    );

    try {
      const response = await apiRequest<CommunityPostFavoriteResponse>(
        `/api/v1/music/community/posts/${requestedPostId}/favorite/`,
        {
          method: nextSaved ? 'POST' : 'DELETE',
        },
      );

      if (activePostId.current !== requestedPostId) return;

      setIsSaved(response.favorited);
      setFavoriteCount(response.favorites_count);
    } catch (error) {
      if (activePostId.current !== requestedPostId) return;

      setIsSaved(previousSaved);
      setFavoriteCount(previousCount);
      console.error(
        'Failed to update community post favorite:',
        error,
      );
    } finally {
      if (activePostId.current === requestedPostId) {
        saveLock.current = false;
        setIsSaveUpdating(false);
      }
    }
  };

  const handleShare = async () => {
    const shareUrl =
      typeof window !== 'undefined' ? window.location.href : '';

    if (typeof navigator !== 'undefined' && navigator.share) {
      try {
        await navigator.share({
          title: 'VibeNationHQ',
          url: shareUrl,
        });
      } catch {
        // Sharing may be cancelled by the user.
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
        console.error('Unable to copy the share link.');
      }
    }
  };

  return (
    <div
      className={`
        text-light-text-soft dark:text-dark-text-soft
        ${variant === 'detail' ? 'space-y-2' : ''}
      `}
    >
      {variant === 'detail' && !likeCommentOnly && (
        <div
          className="
            flex items-center gap-2
            border-b border-light-border pb-3
            text-sm font-medium
            dark:border-dark-border
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
        <div className="flex min-w-0 flex-wrap items-center gap-1 sm:gap-2">
          <button
            type="button"
            onClick={() => void handleLike()}
            disabled={isLikeUpdating}
            aria-label={isLiked ? 'Unlike post' : 'Like post'}
            aria-pressed={isLiked}
            className={`
              inline-flex min-h-9 min-w-9
              items-center justify-center gap-1.5
              rounded-full px-2.5 text-xs font-medium
              transition-colors duration-200
              focus:outline-none focus-visible:ring-4
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
              aria-hidden="true"
            />

            {likeCount > 0 && (
              <span aria-live="polite">
                {formatCount(likeCount)}
              </span>
            )}
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
              inline-flex min-h-9 min-w-9 items-center
              justify-center gap-1.5 rounded-full px-2.5
              text-xs font-medium transition-colors duration-200
              hover:bg-light-surface-soft hover:text-light-text
              dark:hover:bg-dark-surface-soft dark:hover:text-dark-text
              focus:outline-none focus-visible:ring-4
              focus-visible:ring-brand-teal/15
            "
          >
            <MessageCircle
              className="h-[17px] w-[17px]"
              strokeWidth={1.9}
              aria-hidden="true"
            />

            {commentsCount > 0 && (
              <span>{formatCount(commentsCount)}</span>
            )}
          </button>

          {!likeCommentOnly && (
            <>
              <button
                type="button"
                onClick={() => void handleSave()}
                disabled={isSaveUpdating}
                aria-label={
                  isSaved ? 'Remove post from saved' : 'Save post'
                }
                aria-pressed={isSaved}
                className={`
                  inline-flex min-h-9 min-w-9
                  items-center justify-center gap-1.5
                  rounded-full px-2.5 text-xs font-medium
                  transition-colors duration-200
                  focus:outline-none focus-visible:ring-4
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
                  aria-hidden="true"
                />

                {favoriteCount > 0 && (
                  <span>{formatCount(favoriteCount)}</span>
                )}
              </button>

              <button
                type="button"
                onClick={() => void handleShare()}
                aria-label="Share post"
                className="
                  inline-flex min-h-9 min-w-9 items-center
                  justify-center rounded-full px-2.5
                  transition-colors duration-200
                  hover:bg-light-surface-soft hover:text-light-text
                  dark:hover:bg-dark-surface-soft dark:hover:text-dark-text
                  focus:outline-none focus-visible:ring-4
                  focus-visible:ring-brand-teal/15
                "
              >
                <Share2
                  className="h-[17px] w-[17px]"
                  strokeWidth={1.9}
                  aria-hidden="true"
                />
              </button>
            </>
          )}

          {variant === 'feed' && !likeCommentOnly && (
            <div
              className="
                inline-flex min-h-9 items-center gap-1.5
                rounded-full px-2.5 text-xs font-medium
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

      {likeError && (
        <p
          role="status"
          className="pt-1 text-xs text-red-600 dark:text-red-400"
        >
          {likeError}
        </p>
      )}
    </div>
  );
}

function getRequestErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message || 'The like could not be updated.';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'The like could not be updated. Please try again.';
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