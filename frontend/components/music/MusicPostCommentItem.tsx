'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import {
  Flag,
  Heart,
  MessageCircle,
  MoreHorizontal,
  Pencil,
  Trash2,
} from 'lucide-react';

import type {
  CommunityComment,
  CommunityCommentLikeResponse,
} from '@/lib/music/CommunityPosts';

type MusicPostCommentItemProps = {
  comment: CommunityComment;
  replyTo?: CommunityComment | null;
  currentUserId: string | number | null;
  isAuthenticated: boolean;
  onReply: (comment: CommunityComment) => void;
  onEdit: (comment: CommunityComment) => void;
  onDelete: (comment: CommunityComment) => void;
  onReport: (comment: CommunityComment) => void;
  onLike: (
    comment: CommunityComment,
  ) => Promise<CommunityCommentLikeResponse>;
  onRequireAuth: () => void;
  onNavigateToComment?: (commentId: number) => void;
  isHighlighted?: boolean;
  depth?: number;
};

const COMMENT_EDIT_WINDOW_MS = 15 * 60 * 1000;
const COMMENT_COLLAPSED_LINES = 4;

const AVATAR_COLORS = [
  { background: '#1E3A8A', foreground: '#FFFFFF' },
  { background: '#831843', foreground: '#FFFFFF' },
  { background: '#065F46', foreground: '#FFFFFF' },
  { background: '#92400E', foreground: '#FFFFFF' },
  { background: '#5B21B6', foreground: '#FFFFFF' },
  { background: '#9A3412', foreground: '#FFFFFF' },
  { background: '#155E75', foreground: '#FFFFFF' },
  { background: '#991B1B', foreground: '#FFFFFF' },
  { background: '#334155', foreground: '#FFFFFF' },
  { background: '#166534', foreground: '#FFFFFF' },
  { background: '#4338CA', foreground: '#FFFFFF' },
  { background: '#6D28D9', foreground: '#FFFFFF' },
];

function normalizeUserId(
  value: string | number | null | undefined,
): string | null {
  if (value === null || value === undefined) return null;
  return String(value);
}

/**
 * Keep this palette and hashing algorithm aligned with MusicPost.tsx.
 * Normalizing the username makes the colour consistent regardless of case
 * or whether the username is displayed with a leading @.
 */
function getAvatarColor(username: string): {
  background: string;
  foreground: string;
} {
  const normalizedUsername = username
    .trim()
    .replace(/^@/, '')
    .toLowerCase();

  let hash = 0;

  for (
    let index = 0;
    index < normalizedUsername.length;
    index += 1
  ) {
    hash =
      (hash * 31 + normalizedUsername.charCodeAt(index)) >>> 0;
  }

  return AVATAR_COLORS[hash % AVATAR_COLORS.length];
}

function formatCommentDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return '';

  const elapsed = Math.max(0, Date.now() - date.getTime());
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (elapsed < minute) return 'Just now';
  if (elapsed < hour) return `${Math.floor(elapsed / minute)}m ago`;
  if (elapsed < day) return `${Math.floor(elapsed / hour)}h ago`;

  if (elapsed < 7 * day) {
    return `${Math.floor(elapsed / day)}d ago`;
  }

  return new Intl.DateTimeFormat(undefined, {
    day: 'numeric',
    month: 'short',
    year:
      date.getFullYear() !== new Date().getFullYear()
        ? 'numeric'
        : undefined,
  }).format(date);
}

function formatCount(count: number): string {
  if (count >= 1_000_000) {
    return `${(count / 1_000_000)
      .toFixed(count >= 10_000_000 ? 0 : 1)
      .replace(/\.0$/, '')}M`;
  }

  if (count >= 1_000) {
    return `${(count / 1_000)
      .toFixed(count >= 10_000 ? 0 : 1)
      .replace(/\.0$/, '')}K`;
  }

  return String(count);
}

export default function MusicPostCommentItem({
  comment,
  replyTo = null,
  currentUserId,
  isAuthenticated,
  onReply,
  onEdit,
  onDelete,
  onReport,
  onLike,
  onRequireAuth,
  onNavigateToComment,
  isHighlighted = false,
}: MusicPostCommentItemProps) {
  const [isLiked, setIsLiked] = useState(comment.is_liked ?? false);
  const [likesCount, setLikesCount] = useState(comment.likes_count);
  const [isLiking, setIsLiking] = useState(false);
  const [likeError, setLikeError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(() => Date.now());

  const commentContentRef = useRef<HTMLParagraphElement>(null);

  const [isContentExpanded, setIsContentExpanded] = useState(false);
  const [canExpandContent, setCanExpandContent] = useState(false);

  useEffect(() => {
    setIsLiked(comment.is_liked ?? false);
    setLikesCount(comment.likes_count);
  }, [comment.is_liked, comment.likes_count]);

  useEffect(() => {
    setIsContentExpanded(false);
    setCanExpandContent(false);
  }, [comment.id, comment.content]);

  const isRemoved = comment.status === 'removed';
  const isHidden = comment.status === 'hidden';
  const unavailable = isRemoved || isHidden;

  useEffect(() => {
    const element = commentContentRef.current;

    if (!element || unavailable) {
      setCanExpandContent(false);
      return;
    }

    let animationFrame = 0;

    const measureOverflow = () => {
      window.cancelAnimationFrame(animationFrame);

      animationFrame = window.requestAnimationFrame(() => {
        const currentElement = commentContentRef.current;

        if (!currentElement) return;

        const previousStyles = {
          display: currentElement.style.display,
          webkitBoxOrient: currentElement.style.webkitBoxOrient,
          webkitLineClamp: currentElement.style.webkitLineClamp,
          overflow: currentElement.style.overflow,
        };

        currentElement.style.display = '-webkit-box';
        currentElement.style.webkitBoxOrient = 'vertical';
        currentElement.style.webkitLineClamp = String(
          COMMENT_COLLAPSED_LINES,
        );
        currentElement.style.overflow = 'hidden';

        const hasOverflow =
          currentElement.scrollHeight >
          currentElement.clientHeight + 1;

        currentElement.style.display = previousStyles.display;
        currentElement.style.webkitBoxOrient =
          previousStyles.webkitBoxOrient;
        currentElement.style.webkitLineClamp =
          previousStyles.webkitLineClamp;
        currentElement.style.overflow = previousStyles.overflow;

        setCanExpandContent(hasOverflow);
      });
    };

    measureOverflow();

    const resizeObserver =
      typeof ResizeObserver !== 'undefined'
        ? new ResizeObserver(measureOverflow)
        : null;

    resizeObserver?.observe(element);
    window.addEventListener('resize', measureOverflow);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      resizeObserver?.disconnect();
      window.removeEventListener('resize', measureOverflow);
    };
  }, [comment.content, unavailable, isContentExpanded]);

  const normalizedCurrentUserId = normalizeUserId(currentUserId);
  const normalizedCommentUserId = normalizeUserId(comment.user.id);

  const isOwner =
    normalizedCurrentUserId !== null &&
    normalizedCurrentUserId === normalizedCommentUserId;

  const normalizedCreatorId = normalizeUserId(comment.post_creator_id);

  const isPostCreator =
    normalizedCreatorId !== null &&
    normalizedCreatorId === normalizedCommentUserId;

  const createdAt = new Date(comment.created_at).getTime();

  const canEdit =
    isOwner &&
    !unavailable &&
    Number.isFinite(createdAt) &&
    currentTime < createdAt + COMMENT_EDIT_WINDOW_MS;

  const buttonClass =
    'inline-flex min-h-8 items-center justify-center gap-1 rounded-full ' +
    'px-2 py-1.5 text-xs font-medium transition-colors ' +
    'disabled:cursor-not-allowed disabled:opacity-50 ' +
    'sm:gap-1.5 sm:px-2.5';

  useEffect(() => {
    if (!isOwner || unavailable) return;

    const remainingTime =
      createdAt + COMMENT_EDIT_WINDOW_MS - Date.now();

    if (!Number.isFinite(createdAt) || remainingTime <= 0) return;

    const timeout = window.setTimeout(() => {
      setCurrentTime(Date.now());
    }, remainingTime + 50);

    return () => window.clearTimeout(timeout);
  }, [createdAt, isOwner, unavailable]);

  useEffect(() => {
    if (unavailable) setMenuOpen(false);
  }, [unavailable]);

  async function handleLike() {
    if (!isAuthenticated) {
      onRequireAuth();
      return;
    }

    if (isLiking || unavailable) return;

    setIsLiking(true);
    setLikeError(null);

    try {
      const response = await onLike(comment);

      setIsLiked(response.liked);
      setLikesCount(response.likes_count);
    } catch {
      setLikeError('Could not update your like. Please try again.');
    } finally {
      setIsLiking(false);
    }
  }

  const username = comment.user.username.trim();
  const cleanUsername = username.replace(/^@/, '');
  const avatarLetter = cleanUsername.charAt(0).toUpperCase() || '?';
  const avatarColor = getAvatarColor(cleanUsername);

  const replyTargetUsername = replyTo?.user.username
    .trim()
    .replace(/^@/, '');

  const canNavigateToReplyTarget =
    Boolean(replyTo) &&
    !unavailable &&
    typeof onNavigateToComment === 'function';

  const handleNavigateToReplyTarget = () => {
    if (!replyTo || !onNavigateToComment) return;

    onNavigateToComment(replyTo.id);
  };

  return (
    <article
      id={`community-comment-${comment.id}`}
      aria-label={`Comment by ${comment.user.username}`}
      className={[
        'w-full min-w-0 rounded-2xl transition-colors duration-300',
        isHighlighted
          ? 'bg-brand-teal/10 ring-2 ring-brand-teal/70 ring-offset-2 ring-offset-light-bg dark:ring-offset-dark-bg'
          : 'ring-2 ring-transparent',
      ].join(' ')}
      style={{ scrollMarginTop: '110px' }}
    >
      <div className="flex min-w-0 items-start gap-2 p-1 sm:gap-3">
        <Link
          href={`/account/${encodeURIComponent(cleanUsername)}`}
          aria-label={`View ${cleanUsername}'s profile`}
          title={`View ${cleanUsername}'s profile`}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 dark:focus-visible:ring-offset-dark-bg sm:h-9 sm:w-9"
          style={{
            backgroundColor: avatarColor.background,
            color: avatarColor.foreground,
          }}
        >
          {avatarLetter}
        </Link>

        <div className="min-w-0 flex-1">
          <div className="inline-block max-w-full min-w-0 rounded-2xl rounded-tl-md border border-light-border/70 bg-light-surface-soft px-3 py-2 dark:border-dark-border/70 dark:bg-dark-surface-soft sm:px-3.5 sm:py-2.5">
            <div className="flex min-w-0 flex-wrap items-center gap-x-1.5 gap-y-0.5 sm:gap-x-2">
              <Link
                href={`/account/${encodeURIComponent(cleanUsername)}`}
                className="min-w-0 max-w-full break-words [overflow-wrap:anywhere] text-[13px] font-semibold leading-5 text-light-text transition-colors hover:text-brand-teal focus-visible:outline-none focus-visible:underline dark:text-dark-text sm:text-sm"
              >
                {comment.user.username}
              </Link>

              {isPostCreator && (
                <span className="shrink-0 text-[9px] font-semibold leading-4 text-brand-teal sm:text-[10px]">
                  Creator
                </span>
              )}

              <span
                className="shrink-0 text-[10px] leading-4 text-light-text-muted dark:text-dark-text-muted sm:text-xs"
                title={new Date(comment.created_at).toLocaleString()}
              >
                {formatCommentDate(comment.created_at)}
              </span>

              {comment.is_edited && !unavailable && (
                <span
                  className="shrink-0 text-[10px] leading-4 text-light-text-muted dark:text-dark-text-muted sm:text-xs"
                  title="This comment has been edited."
                >
                  · edited
                </span>
              )}
            </div>

            {replyTargetUsername &&
              canNavigateToReplyTarget &&
              replyTo && (
                <p className="mb-1.5 mt-1 flex min-w-0 flex-wrap items-center gap-x-1 text-xs leading-relaxed text-light-text-muted dark:text-dark-text-muted sm:mb-2">
                  <span>Replying to</span>

                  <button
                    type="button"
                    onClick={handleNavigateToReplyTarget}
                    aria-label={`Jump to ${replyTargetUsername}'s comment`}
                    className="break-words font-semibold text-brand-teal [overflow-wrap:anywhere] hover:underline focus-visible:outline-none focus-visible:underline"
                  >
                    @{replyTargetUsername}
                  </button>
                </p>
              )}

            {isRemoved ? (
              <p className="break-words text-sm italic leading-relaxed text-light-text-muted dark:text-dark-text-muted">
                This comment has been removed.
              </p>
            ) : isHidden ? (
              <p className="break-words text-sm italic leading-relaxed text-light-text-muted dark:text-dark-text-muted">
                This comment is unavailable.
              </p>
            ) : (
              <>
                <p
                  ref={commentContentRef}
                  role={canNavigateToReplyTarget ? 'link' : undefined}
                  tabIndex={canNavigateToReplyTarget ? 0 : undefined}
                  aria-label={
                    canNavigateToReplyTarget && replyTargetUsername
                      ? `Jump to the comment by ${replyTargetUsername} that this reply responds to`
                      : undefined
                  }
                  onClick={
                    canNavigateToReplyTarget
                      ? handleNavigateToReplyTarget
                      : undefined
                  }
                  onKeyDown={
                    canNavigateToReplyTarget
                      ? (event) => {
                          if (
                            event.key === 'Enter' ||
                            event.key === ' '
                          ) {
                            event.preventDefault();
                            handleNavigateToReplyTarget();
                          }
                        }
                      : undefined
                  }
                  className={[
                    'whitespace-pre-wrap break-words text-sm leading-relaxed [overflow-wrap:anywhere] text-light-text dark:text-dark-text',
                    canNavigateToReplyTarget
                      ? 'cursor-pointer rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal'
                      : '',
                  ].join(' ')}
                  style={{
                    display: isContentExpanded ? 'block' : '-webkit-box',
                    WebkitBoxOrient: 'vertical',
                    WebkitLineClamp: isContentExpanded
                      ? 'unset'
                      : COMMENT_COLLAPSED_LINES,
                    overflow: isContentExpanded ? 'visible' : 'hidden',
                  }}
                >
                  {comment.content}
                </p>

                {(canExpandContent || isContentExpanded) && (
                  <button
                    type="button"
                    onClick={() => {
                      setIsContentExpanded((expanded) => !expanded);
                    }}
                    aria-expanded={isContentExpanded}
                    className="mt-1 text-xs font-semibold text-brand-teal transition-colors hover:text-brand-teal/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 dark:focus-visible:ring-offset-dark-surface"
                  >
                    {isContentExpanded ? 'See less' : 'See more'}
                  </button>
                )}
              </>
            )}
          </div>

          {!unavailable && (
            <div className="mt-1 flex min-w-0 flex-wrap items-center gap-x-0.5 gap-y-0.5 sm:gap-x-1">
              <button
                type="button"
                onClick={handleLike}
                disabled={isLiking}
                aria-pressed={isLiked}
                aria-label={isLiked ? 'Unlike comment' : 'Like comment'}
                className={`${buttonClass} ${
                  isLiked
                    ? 'text-brand-teal'
                    : 'text-light-text-muted hover:bg-light-surface-soft hover:text-light-text dark:text-dark-text-muted dark:hover:bg-dark-surface-soft dark:hover:text-dark-text'
                }`}
              >
                <Heart
                  size={15}
                  className={isLiked ? 'fill-current' : ''}
                />

                {likesCount > 0 && (
                  <span>{formatCount(likesCount)}</span>
                )}

                <span>{isLiked ? 'Liked' : 'Like'}</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  if (!isAuthenticated) {
                    onRequireAuth();
                    return;
                  }

                  onReply(comment);
                }}
                className={`${buttonClass} text-light-text-muted hover:bg-light-surface-soft hover:text-light-text dark:text-dark-text-muted dark:hover:bg-dark-surface-soft dark:hover:text-dark-text`}
              >
                <MessageCircle size={15} />
                Reply
              </button>

              {isOwner && canEdit && (
                <button
                  type="button"
                  onClick={() => onEdit(comment)}
                  title="Comments can be edited for 15 minutes after posting."
                  className={`${buttonClass} text-light-text-muted hover:bg-light-surface-soft hover:text-light-text dark:text-dark-text-muted dark:hover:bg-dark-surface-soft dark:hover:text-dark-text`}
                >
                  <Pencil size={14} />
                  Edit
                </button>
              )}

              <div className="relative ml-auto shrink-0">
                <button
                  type="button"
                  onClick={() => setMenuOpen((open) => !open)}
                  aria-label="Comment options"
                  aria-expanded={menuOpen}
                  className="rounded-full p-2 text-light-text-muted transition-colors hover:bg-light-surface-soft hover:text-light-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:text-dark-text-muted dark:hover:bg-dark-surface-soft dark:hover:text-dark-text"
                >
                  <MoreHorizontal size={17} />
                </button>

                {menuOpen && (
                  <>
                    <button
                      type="button"
                      aria-label="Close comment options"
                      className="fixed inset-0 z-10 cursor-default"
                      onClick={() => setMenuOpen(false)}
                    />

                    <div className="absolute right-0 top-full z-20 mt-1 w-44 max-w-[calc(100vw-2rem)] rounded-xl border border-light-border bg-light-surface p-1 shadow-lg dark:border-dark-border dark:bg-dark-surface">
                      {isOwner ? (
                        <>
                          {canEdit && (
                            <button
                              type="button"
                              onClick={() => {
                                setMenuOpen(false);
                                onEdit(comment);
                              }}
                              className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm text-light-text transition-colors hover:bg-light-surface-soft dark:text-dark-text dark:hover:bg-dark-surface-soft"
                            >
                              <Pencil size={15} />
                              Edit comment
                            </button>
                          )}

                          <button
                            type="button"
                            onClick={() => {
                              setMenuOpen(false);
                              onDelete(comment);
                            }}
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-950/30"
                          >
                            <Trash2 size={15} />
                            Delete comment
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          onClick={() => {
                            setMenuOpen(false);

                            if (!isAuthenticated) {
                              onRequireAuth();
                              return;
                            }

                            onReport(comment);
                          }}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm text-light-text transition-colors hover:bg-light-surface-soft dark:text-dark-text dark:hover:bg-dark-surface-soft"
                        >
                          <Flag size={15} />
                          Report comment
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {likeError && (
            <p
              role="alert"
              className="mt-1 break-words text-xs text-red-600 dark:text-red-300"
            >
              {likeError}
            </p>
          )}

          {comment.replies_count > 0 && (
            <p className="mt-1 pl-1 text-xs text-light-text-muted dark:text-dark-text-muted sm:pl-2">
              {comment.replies_count}{' '}
              {comment.replies_count === 1 ? 'reply' : 'replies'}
            </p>
          )}
        </div>
      </div>
    </article>
  );
}