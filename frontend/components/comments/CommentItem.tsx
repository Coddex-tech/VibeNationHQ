'use client';

import Image from 'next/image';
import { getMediaUrl } from '@/lib/api';
import VerificationBadge from '../Icons';

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

import {
    canEditComment,
    formatCommentDate,
    formatCount,
    getAvatarColor,
    getAvatarLetter,
    getProfileUsername,
    normalizeUserId
} from './commentUtils';
import MentionText from '../MentionText';

/**
 * Common comment shape used by the shared comment UI.
 *
 * Community and editorial comments should be converted into this shape
 * by their respective feature adapters. Their API response types do not
 * need to change.
 */
export type SharedComment = {
  id: number;
  user: {
    id: string | number;
    username: string;
    display_name: string | null;
    profile_image: string | null;
    is_verified: boolean;
    is_identity_verified: boolean;
  };
  parent: number | null;
  content: string;
  mentionedUsernames: string[];
  createdAt: string;
  likesCount: number;
  isLiked: boolean;
  repliesCount: number;
  isEdited: boolean;
  status: string;
};

export type SharedCommentLikeResponse = {
  liked: boolean;
  likes_count: number;
};

type CommentItemProps = {
  comment: SharedComment;
  replyTo?: SharedComment | null;

  currentUserId: string | number | null;
  isAuthenticated: boolean;

  /**
   * Set this only when the feature knows the commenter is the
   * relevant creator, such as the community post's creator.
   */
  showCreatorBadge?: boolean;

  onReply: (comment: SharedComment) => void;
  onEdit: (comment: SharedComment) => void;
  onDelete: (comment: SharedComment) => void;
  onReport: (comment: SharedComment) => void;

  onLike: (
    comment: SharedComment,
  ) => Promise<SharedCommentLikeResponse>;

  onRequireAuth: () => void;
  onNavigateToComment?: (commentId: number) => void;

  isHighlighted?: boolean;

  /**
   * Allows each feature to preserve its existing comment element IDs.
   */
  commentIdPrefix?: string;
};

const COMMENT_EDIT_WINDOW_MS = 15 * 60 * 1000;
const COMMENT_COLLAPSED_LINES = 4;

export default function CommentItem({
  comment,
  replyTo = null,
  currentUserId,
  isAuthenticated,
  showCreatorBadge = false,
  onReply,
  onEdit,
  onDelete,
  onReport,
  onLike,
  onRequireAuth,
  onNavigateToComment,
  isHighlighted = false,
  commentIdPrefix = 'comment',
}: CommentItemProps) {
  const [hasProfileImageError, setHasProfileImageError] = useState(false);
  const [isLiked, setIsLiked] = useState(comment.isLiked);
  const [likesCount, setLikesCount] = useState(comment.likesCount);
  const [isLiking, setIsLiking] = useState(false);
  const [likeError, setLikeError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(() => Date.now());

  const commentContentRef = useRef<HTMLParagraphElement>(null);

  const [isContentExpanded, setIsContentExpanded] = useState(false);
  const [canExpandContent, setCanExpandContent] = useState(false);

  useEffect(() => {
    setIsLiked(comment.isLiked);
    setLikesCount(comment.likesCount);
  }, [comment.isLiked, comment.likesCount]);

  useEffect(() => {
    setIsContentExpanded(false);
    setCanExpandContent(false);
  }, [comment.id, comment.content]);

  const isRemoved = comment.status === 'removed';
  const isHidden = comment.status === 'hidden';
  const unavailable = isRemoved || isHidden;

  const normalizedCurrentUserId = normalizeUserId(currentUserId);
  const normalizedCommentUserId = normalizeUserId(comment.user.id);

  const isOwner =
    normalizedCurrentUserId !== null &&
    normalizedCurrentUserId === normalizedCommentUserId;

  const canEdit =
    isOwner &&
    !unavailable &&
    canEditComment(
      comment.createdAt,
      currentTime,
      COMMENT_EDIT_WINDOW_MS,
    );

  const createdAt = new Date(comment.createdAt).getTime();

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
    if (unavailable) {
      setMenuOpen(false);
    }
  }, [unavailable]);

  useEffect(() => {
    const element = commentContentRef.current;

    if (!element || unavailable || isContentExpanded) {
      setCanExpandContent(false);
      return;
    }

    let animationFrame = 0;

    const measureOverflow = () => {
      window.cancelAnimationFrame(animationFrame);

      animationFrame = window.requestAnimationFrame(() => {
        const currentElement = commentContentRef.current;

        if (!currentElement) return;

        setCanExpandContent(
          currentElement.scrollHeight >
            currentElement.clientHeight + 1,
        );
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
  const cleanUsername = getProfileUsername(username);
  const avatarLetter = getAvatarLetter(cleanUsername);
  const avatarColor = getAvatarColor(cleanUsername);

  const displayName =
    comment.user.display_name?.trim() || cleanUsername || 'VibeNation user';

  const profileImageUrl = comment.user.profile_image
    ? getMediaUrl(comment.user.profile_image)
    : null;

  useEffect(() => {
    setHasProfileImageError(false);
  }, [profileImageUrl]);

  const hasUsableProfileImage =
    Boolean(profileImageUrl) && !hasProfileImageError;

  const verificationType = comment.user.is_identity_verified
    ? 'identity'
    : comment.user.is_verified
      ? 'verified'
      : null;

  const replyTargetUsername = replyTo
    ? getProfileUsername(replyTo.user.username)
    : '';

  const canNavigateToReplyTarget =
    Boolean(replyTo) &&
    !unavailable &&
    typeof onNavigateToComment === 'function';

  function handleNavigateToReplyTarget() {
    if (!replyTo || !onNavigateToComment) return;

    onNavigateToComment(replyTo.id);
  }

  return (
    <article
      id={`${commentIdPrefix}-${comment.id}`}
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
          aria-label={`View ${displayName}'s profile`}
          title={`View ${displayName}'s profile`}
          className="relative flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full text-sm font-bold ring-1 ring-black/5 transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 dark:focus-visible:ring-offset-dark-bg sm:h-9 sm:w-9"
          style={
            hasUsableProfileImage
              ? undefined
              : {
                  backgroundColor: avatarColor.background,
                  color: avatarColor.foreground,
                }
          }
        >
          {hasUsableProfileImage && profileImageUrl ? (
            <Image
              src={profileImageUrl}
              alt=""
              fill
              sizes="36px"
              className="rounded-full object-cover"
              onError={() => setHasProfileImageError(true)}
            />
          ) : (
            avatarLetter
          )}
        </Link>

        <div className="min-w-0 flex-1">
          <div className="inline-block max-w-full min-w-0 rounded-2xl rounded-tl-md border border-light-border/70 bg-light-surface-soft px-3 py-2 dark:border-dark-border/70 dark:bg-dark-surface-soft sm:px-3.5 sm:py-2.5">
            <div className="flex min-w-0 flex-col gap-0.5">
              {/* Name and badges */}
              <div className="flex min-w-0 flex-wrap items-center gap-x-1.5 gap-y-0.5">
                <Link
                  href={`/account/${encodeURIComponent(cleanUsername)}`}
                  className="min-w-0 max-w-full break-words text-[13px] font-semibold leading-5 text-light-text transition-colors hover:text-brand-teal focus-visible:outline-none focus-visible:underline dark:text-dark-text sm:text-sm"
                >
                  {displayName}
                </Link>

                {verificationType === 'identity' && (
                  <span
                    role="img"
                    aria-label="Identity verified"
                    title="Identity verified"
                    className="inline-flex shrink-0 items-center text-brand-teal"
                  >
                    <VerificationBadge type="identity" size={16} />
                  </span>
                )}

                {verificationType === 'verified' && (
                  <span
                    role="img"
                    aria-label="Verified account"
                    title="Verified account"
                    className="inline-flex shrink-0 items-center text-blue-500"
                  >
                    <VerificationBadge type="verified" size={16} />
                  </span>
                )}

                {showCreatorBadge && (
                  <span className="inline-flex shrink-0 items-center rounded-full bg-brand-teal/10 px-1.5 py-0.5 text-[9px] font-semibold leading-none text-brand-teal sm:text-[10px]">
                    Creator
                  </span>
                )}
              </div>

              {/* Username and date */}
              <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-0.5">
                <Link
                  href={`/account/${encodeURIComponent(cleanUsername)}`}
                  className="min-w-0 max-w-full break-words text-[10px] leading-4 text-light-text-muted transition-colors hover:text-brand-teal focus-visible:outline-none focus-visible:underline dark:text-dark-text-muted sm:text-xs"
                >
                  @{cleanUsername}
                </Link>

                <span
                  className="shrink-0 text-[10px] leading-4 text-light-text-muted dark:text-dark-text-muted sm:text-xs"
                  title={new Date(comment.createdAt).toLocaleString()}
                >
                  {formatCommentDate(comment.createdAt)}
                </span>

                {comment.isEdited && !unavailable && (
                  <span
                    className="shrink-0 text-[10px] leading-4 text-light-text-muted dark:text-dark-text-muted sm:text-xs"
                    title="This comment has been edited."
                  >
                    · edited
                  </span>
                )}
              </div>
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
                            event.target !== event.currentTarget
                          ) {
                            return;
                          }

                          if (event.key === 'Enter' || event.key === ' ') {
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
                  <MentionText
                    content={comment.content}
                    mentionedUsernames={comment.mentionedUsernames}
                    onMentionClick={() => {
                      // A mention link must never trigger reply navigation.
                    }}
                  />
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

          {comment.repliesCount > 0 && (
            <p className="mt-1 pl-1 text-xs text-light-text-muted dark:text-dark-text-muted sm:pl-2">
              {comment.repliesCount}{' '}
              {comment.repliesCount === 1 ? 'reply' : 'replies'}
            </p>
          )}
        </div>
      </div>
    </article>
  );
}
