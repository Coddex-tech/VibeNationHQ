
'use client';

import { useEffect, useState } from 'react';
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
  depth?: number;
};

const COMMENT_EDIT_WINDOW_MS = 15 * 60 * 1000;

const AVATAR_COLORS = [
  'bg-teal-100 text-teal-800 dark:bg-teal-900/50 dark:text-teal-200',
  'bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-200',
  'bg-violet-100 text-violet-800 dark:bg-violet-900/50 dark:text-violet-200',
  'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200',
  'bg-rose-100 text-rose-800 dark:bg-rose-900/50 dark:text-rose-200',
  'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200',
  'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/50 dark:text-indigo-200',
  'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-200',
];

function normalizeUserId(
  value: string | number | null | undefined,
): string | null {
  if (value === null || value === undefined) return null;
  return String(value);
}

function getAvatarColor(username: string): string {
  let hash = 0;

  for (let index = 0; index < username.length; index += 1) {
    hash = (hash * 31 + username.charCodeAt(index)) | 0;
  }

  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
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
}: MusicPostCommentItemProps) {
  const [isLiked, setIsLiked] = useState(comment.is_liked ?? false);
  const [likesCount, setLikesCount] = useState(comment.likes_count);
  const [isLiking, setIsLiking] = useState(false);
  const [likeError, setLikeError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(() => Date.now());

  useEffect(() => {
    setIsLiked(comment.is_liked ?? false);
    setLikesCount(comment.likes_count);
  }, [comment.is_liked, comment.likes_count]);

  const normalizedCurrentUserId = normalizeUserId(currentUserId);
  const normalizedCommentUserId = normalizeUserId(comment.user.id);

  const isOwner =
    normalizedCurrentUserId !== null &&
    normalizedCurrentUserId === normalizedCommentUserId;

  const normalizedCreatorId = normalizeUserId(
    comment.post_creator_id,
  );

  const isPostCreator =
    normalizedCreatorId !== null &&
    normalizedCreatorId === normalizedCommentUserId;

  const isRemoved = comment.status === 'removed';
  const isHidden = comment.status === 'hidden';
  const unavailable = isRemoved || isHidden;

  const createdAt = new Date(comment.created_at).getTime();

  const canEdit =
    isOwner &&
    !unavailable &&
    Number.isFinite(createdAt) &&
    currentTime < createdAt + COMMENT_EDIT_WINDOW_MS;

  const buttonClass =
    'inline-flex min-h-8 items-center gap-1.5 rounded-full px-2.5 py-1.5 ' +
    'text-xs font-medium transition-colors disabled:cursor-not-allowed ' +
    'disabled:opacity-50';

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
  const avatarLetter = username.charAt(0).toUpperCase() || '?';
  const replyTargetUsername = replyTo?.user.username.trim();

  return (
    <article
      className="min-w-0"
      aria-label={`Comment by ${comment.user.username}`}
    >
      <div className="flex items-start gap-3">
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold ${getAvatarColor(username)}`}
          aria-hidden="true"
        >
          {avatarLetter}
        </div>

        <div className="min-w-0 flex-1">
          <div className="inline-block max-w-full rounded-2xl rounded-tl-md border border-light-border/70 bg-light-surface-soft px-3.5 py-2.5 dark:border-dark-border/70 dark:bg-dark-surface-soft">
            <div className="mb-1.5 flex flex-wrap items-center gap-x-2 gap-y-1">
              <span className="break-all text-sm font-semibold text-light-text dark:text-dark-text">
                @{comment.user.username}
              </span>

              {isPostCreator && (
                <span className="inline-flex items-center rounded-full border border-brand-teal/20 bg-brand-teal/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-brand-teal">
                  Creator
                </span>
              )}

              <span
                className="text-xs text-light-text-muted dark:text-dark-text-muted"
                title={new Date(comment.created_at).toLocaleString()}
              >
                {formatCommentDate(comment.created_at)}
              </span>

              {comment.is_edited && !unavailable && (
                <span
                  className="text-xs text-light-text-muted dark:text-dark-text-muted"
                  title="This comment has been edited."
                >
                  · edited
                </span>
              )}
            </div>

            {replyTargetUsername && !unavailable && (
              <p className="mb-2 flex flex-wrap items-center gap-1 text-xs text-light-text-muted dark:text-dark-text-muted">
                <MessageCircle
                  size={12}
                  className="shrink-0 text-brand-teal"
                  aria-hidden="true"
                />

                <span>Replying to</span>

                <span className="break-all font-semibold text-brand-teal">
                  @{replyTargetUsername}
                </span>
              </p>
            )}

            {isRemoved ? (
              <p className="text-sm italic text-light-text-muted dark:text-dark-text-muted">
                This comment has been removed.
              </p>
            ) : isHidden ? (
              <p className="text-sm italic text-light-text-muted dark:text-dark-text-muted">
                This comment is unavailable.
              </p>
            ) : (
              <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-light-text dark:text-dark-text">
                {comment.content}
              </p>
            )}
          </div>

          {!unavailable && (
            <div className="mt-1 flex flex-wrap items-center gap-1">
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

                  // Pass the exact comment clicked, not its root.
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

              <div className="relative ml-auto">
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

                    <div className="absolute right-0 top-full z-20 mt-1 w-44 rounded-xl border border-light-border bg-light-surface p-1 shadow-lg dark:border-dark-border dark:bg-dark-surface">
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
              className="mt-1 text-xs text-red-600 dark:text-red-300"
            >
              {likeError}
            </p>
          )}

          {comment.replies_count > 0 && (
            <p className="mt-1 pl-2 text-xs text-light-text-muted dark:text-dark-text-muted">
              {comment.replies_count}{' '}
              {comment.replies_count === 1 ? 'reply' : 'replies'}
            </p>
          )}
        </div>
      </div>
    </article>
  );
}
