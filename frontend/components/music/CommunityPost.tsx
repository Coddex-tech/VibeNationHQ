'use client';

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import type { MouseEvent, KeyboardEvent } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  Copy,
  Flag,
  LoaderCircle,
  MoreHorizontal,
  Pencil,
  Star,
  Trash2,
  UserMinus,
  UserPlus,
  X,
} from 'lucide-react';

import {
  apiRequest,
  ApiError,
  getMediaUrl,
} from '@/lib/api';
import {
  followCommunityUser,
  unfollowCommunityUser,
} from '@/lib/music/CommunityPosts';
import type { CommunityPost } from '@/lib/music/CommunityPosts';
import { useAuth } from '@/components/auth/AuthProvider';

import ReportContentModal from '@/components/ui/ReportContentModal';

import MusicAttachment from './MusicAttachment';
import MusicEngagementBar from './MusicEngagementBar';
import MusicPostComments from './MusicPostComments';
import VerificationBadge from '../Icons';

type MusicPostProps = {
  post: CommunityPost;
  showFollowButton?: boolean;
  variant?: 'feed' | 'detail';
  hideMusicAttachment?: boolean;
  likeCommentOnly?: boolean;
};

type PostDialog = 'edit' | 'delete' | null;

type FollowStateChangedEvent = CustomEvent<{
  userId: number;
  following: boolean;
  followingYou?: boolean;
}>;

const FOLLOW_STATE_CHANGED_EVENT =
  'vibenation:user-follow-state-changed';

const POST_PREVIEW_LENGTH = 300;
const RATING_MIN = 0.5;
const RATING_MAX = 5;
const STAR_VALUES = [1, 2, 3, 4, 5];

export default function MusicPost({
  post,
  showFollowButton = true,
  variant = 'feed',
  hideMusicAttachment = false,
  likeCommentOnly = false,
}: MusicPostProps) {
  const { user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const isDetail = variant === 'detail';

  /*
   * Compact presentation is reserved for related posts on music
   * detail pages. TargetCommunityPosts passes both flags for this
   * purpose; the regular community feed does not.
   */
  const isCompactRelatedPost =
    !isDetail && hideMusicAttachment && likeCommentOnly;

  const [displayPost, setDisplayPost] = useState(post);
  const [isContentExpanded, setIsContentExpanded] = useState(false);
  const [isDeleted, setIsDeleted] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [activeDialog, setActiveDialog] = useState<PostDialog>(null);

  const [editContent, setEditContent] = useState(post.content);
  const [editRating, setEditRating] = useState<number | null>(
    getPostRating(post.rating),
  );
  const [hoverRating, setHoverRating] = useState<number | null>(null);

  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [editError, setEditError] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [toastMessage, setToastMessage] = useState('');

  const [currentTime, setCurrentTime] = useState(() => Date.now());

  const [isFollowing, setIsFollowing] = useState(
    Boolean(post.user.is_following),
  );
  const [isFollowingYou, setIsFollowingYou] = useState(
    Boolean(post.user.is_following_you),
  );

  const [isFollowLoading, setIsFollowLoading] = useState(false);
  const [followError, setFollowError] = useState('');

  // Used when a supplied profile image cannot be loaded.
  const [hasProfileImageError, setHasProfileImageError] = useState(false);

  const menuRef = useRef<HTMLDivElement>(null);
  const followRequestInProgress = useRef(false);
  const commentsSectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    setDisplayPost(post);
  }, [post]);

  useEffect(() => {
    setIsContentExpanded(false);
  }, [displayPost.id]);

  useEffect(() => {
    setIsFollowing(Boolean(post.user.is_following));
  }, [post.user.id, post.user.is_following]);

  useEffect(() => {
    setIsFollowingYou(Boolean(post.user.is_following_you));
  }, [post.user.id, post.user.is_following_you]);

  useEffect(() => {
    function handleFollowStateChanged(event: Event) {
      const followEvent = event as FollowStateChangedEvent;

      if (followEvent.detail.userId === Number(displayPost.user.id)) {
        setIsFollowing(followEvent.detail.following);

        if (typeof followEvent.detail.followingYou === 'boolean') {
          setIsFollowingYou(followEvent.detail.followingYou);
        }

        setFollowError('');
      }
    }

    window.addEventListener(
      FOLLOW_STATE_CHANGED_EVENT,
      handleFollowStateChanged,
    );

    return () => {
      window.removeEventListener(
        FOLLOW_STATE_CHANGED_EVENT,
        handleFollowStateChanged,
      );
    };
  }, [displayPost.user.id]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setCurrentTime(Date.now());
    }, 15_000);

    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    if (!toastMessage) return;

    const timeoutId = window.setTimeout(() => {
      setToastMessage('');
    }, 5000);

    return () => window.clearTimeout(timeoutId);
  }, [toastMessage]);

  const username =
    displayPost.user.username?.trim() || 'VibeNation user';

  const cleanUsername = username.replace(/^@/, '');

  const displayName =
    displayPost.user.display_name?.trim() || cleanUsername || 'VibeNation user';

  const profileImageUrl = displayPost.user.profile_image
    ? getMediaUrl(displayPost.user.profile_image)
    : null;

  // Reset the image error when the author or their image changes.
  useEffect(() => {
    setHasProfileImageError(false);
  }, [profileImageUrl]);

  const hasUsableProfileImage =
    Boolean(profileImageUrl) && !hasProfileImageError;

  const isIdentityVerified = Boolean(
    displayPost.user.is_identity_verified,
  );

  const isVerified = Boolean(displayPost.user.is_verified);

  /*
   * Identity verification takes priority.
   * Only one verification badge is ever rendered.
   */
  const verificationType = isIdentityVerified
    ? 'identity'
    : isVerified
      ? 'verified'
      : null;

  const initials =
    cleanUsername
      .split(/[\s_.-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('') || 'VN';

  const avatarColor = getAvatarColor(cleanUsername.toLowerCase());
  const postContent = displayPost.content;

  const isContentTruncated =
    !isDetail && postContent.length > POST_PREVIEW_LENGTH;

  const displayedContent =
    isContentTruncated && !isContentExpanded
      ? `${postContent.slice(0, POST_PREVIEW_LENGTH).trimEnd()}…`
      : postContent;

  // The individual author's rating is separate from the song's overall rating.
  const rating = getPostRating(displayPost.rating);
  const hasRating = rating !== null && rating > 0;

  const isOwner =
    user !== null &&
    user !== undefined &&
    String(user.id) === String(displayPost.user.id);

  const editDeadline =
    new Date(displayPost.created_at).getTime() +
    30 * 60 * 1000;

  const canEditPost =
    isOwner &&
    Number.isFinite(editDeadline) &&
    currentTime < editDeadline;

  const canRateTarget =
    displayPost.target?.target_type === 'song' ||
    displayPost.target?.target_type === 'album';

  const isDialogOpen = activeDialog !== null;
  const displayedEditRating = hoverRating ?? editRating;

  const closeReportDialog = useCallback(() => {
    setIsReportOpen(false);
  }, []);

  const closeActionDialog = useCallback(() => {
    if (isSaving || isDeleting) return;

    setActiveDialog(null);
    setEditError('');
    setDeleteError('');
    setHoverRating(null);
  }, [isSaving, isDeleting]);

  function openReportDialog() {
    setIsMenuOpen(false);
    setIsReportOpen(true);
  }

  function openEditDialog() {
    setEditContent(displayPost.content);
    setEditRating(getPostRating(displayPost.rating));
    setHoverRating(null);
    setEditError('');
    setIsMenuOpen(false);
    setActiveDialog('edit');
  }

  function openDeleteDialog() {
    setDeleteError('');
    setIsMenuOpen(false);
    setActiveDialog('delete');
  }

  async function handleFollowToggle() {
    if (
      followRequestInProgress.current ||
      isFollowLoading ||
      isOwner
    ) {
      return;
    }

    if (!user) {
      const returnTo = pathname || '/community';

      setIsMenuOpen(false);

      router.push(`/login?next=${encodeURIComponent(returnTo)}`);
      return;
    }

    const targetUserId = Number(displayPost.user.id);
    const previousFollowing = isFollowing;
    const nextFollowing = !previousFollowing;

    // Update the UI immediately.
    setIsFollowing(nextFollowing);
    setFollowError('');

    followRequestInProgress.current = true;
    setIsFollowLoading(true);

    // Synchronize other post cards immediately.
    window.dispatchEvent(
      new CustomEvent(FOLLOW_STATE_CHANGED_EVENT, {
        detail: {
          userId: targetUserId,
          following: nextFollowing,
        },
      }),
    );

    try {
      const response = nextFollowing
        ? await followCommunityUser(targetUserId)
        : await unfollowCommunityUser(targetUserId);

      const confirmedFollowing = Boolean(response.following);

      // Reconcile with the server response.
      setIsFollowing(confirmedFollowing);

      window.dispatchEvent(
        new CustomEvent(FOLLOW_STATE_CHANGED_EVENT, {
          detail: {
            userId: targetUserId,
            following: confirmedFollowing,
          },
        }),
      );
    } catch (error) {
      // Roll back if the API request fails.
      setIsFollowing(previousFollowing);

      window.dispatchEvent(
        new CustomEvent(FOLLOW_STATE_CHANGED_EVENT, {
          detail: {
            userId: targetUserId,
            following: previousFollowing,
          },
        }),
      );

      setFollowError(getErrorMessage(error));
    } finally {
      followRequestInProgress.current = false;
      setIsFollowLoading(false);
    }
  }

  function handleFollowMenuAction() {
    setIsMenuOpen(false);
    void handleFollowToggle();
  }

  useEffect(() => {
    if (!isMenuOpen) return;

    function handlePointerDown(event: PointerEvent) {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    }

    document.addEventListener('pointerdown', handlePointerDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
    };
  }, [isMenuOpen]);

  useEffect(() => {
    if (!isMenuOpen) return;

    function handleKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === 'Escape') setIsMenuOpen(false);
    }

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isMenuOpen]);

  useEffect(() => {
    if (!isDialogOpen || isSaving || isDeleting) return;

    function handleKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === 'Escape') closeActionDialog();
    }

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [
    isDialogOpen,
    isSaving,
    isDeleting,
    closeActionDialog,
  ]);

  function handleRatingHover(event: MouseEvent<HTMLDivElement>) {
    if (isSaving) return;
    setHoverRating(getRatingFromPointer(event));
  }

  function handleRatingClick(event: MouseEvent<HTMLDivElement>) {
    if (isSaving) return;

    setEditRating(getRatingFromPointer(event));
    setHoverRating(null);
    setEditError('');
  }

  function handleRatingKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (isSaving) return;

    const currentRating = displayedEditRating ?? RATING_MIN;
    let nextRating: number | null = null;

    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowUp':
        nextRating = clampRating(currentRating + RATING_MIN);
        break;

      case 'ArrowLeft':
      case 'ArrowDown':
        nextRating = clampRating(currentRating - RATING_MIN);
        break;

      case 'Home':
        nextRating = RATING_MIN;
        break;

      case 'End':
        nextRating = RATING_MAX;
        break;

      case 'Delete':
      case 'Backspace':
        event.preventDefault();
        setEditRating(null);
        setHoverRating(null);
        setEditError('');
        return;

      default:
        return;
    }

    event.preventDefault();
    setEditRating(nextRating);
    setHoverRating(null);
    setEditError('');
  }

  function renderEditRatingStar(star: number) {
    const value = displayedEditRating ?? 0;
    const isFull = value >= star;
    const isHalf = !isFull && value >= star - 0.5;

    return (
      <div
        key={star}
        aria-hidden="true"
        className="relative flex h-9 w-9 shrink-0 items-center justify-center"
      >
        <Star
          className="absolute text-light-border dark:text-dark-border"
          size={28}
          strokeWidth={1.7}
        />

        {(isFull || isHalf) && (
          <Star
            className="absolute fill-brand-teal text-brand-teal"
            size={28}
            strokeWidth={1.7}
            style={{
              clipPath: isHalf ? 'inset(0 50% 0 0)' : undefined,
            }}
          />
        )}
      </div>
    );
  }

  async function handleSaveEdit() {
    const trimmedContent = editContent.trim();

    if (!trimmedContent) {
      setEditError('Post content cannot be empty.');
      return;
    }

    if (trimmedContent.length > 5000) {
      setEditError('Post content cannot exceed 5,000 characters.');
      return;
    }

    if (Date.now() >= editDeadline) {
      setEditError(
        'The 30-minute editing window has expired. This post can no longer be edited.',
      );
      return;
    }

    if (isSaving) return;

    setIsSaving(true);
    setEditError('');

    try {
      const updatedPost = await apiRequest<CommunityPost>(
        `/api/v1/music/community/posts/${displayPost.id}/`,
        {
          method: 'PATCH',
          body: JSON.stringify({
            content: trimmedContent,
            ...(canRateTarget ? { rating: editRating } : {}),
          }),
        },
      );

      setDisplayPost(updatedPost);
      setEditContent(updatedPost.content);
      setEditRating(getPostRating(updatedPost.rating));
      setHoverRating(null);
      setActiveDialog(null);
      setEditError('');
      setToastMessage('Post edited successfully.');
    } catch (error) {
      setEditError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeletePost() {
    if (isDeleting) return;

    setIsDeleting(true);
    setDeleteError('');

    try {
      await apiRequest<void>(
        `/api/v1/music/community/posts/${displayPost.id}/`,
        { method: 'DELETE' },
      );

      setIsDeleted(true);
      setActiveDialog(null);
    } catch (error) {
      setDeleteError(getErrorMessage(error));
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleCopyPostLink() {
    setIsMenuOpen(false);

    const postUrl =
      `${window.location.origin}` +
      `/music/community/posts/${displayPost.id}/` +
      encodeURIComponent(displayPost.slug);

    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error('Clipboard access is unavailable.');
      }

      await navigator.clipboard.writeText(postUrl);
      setToastMessage('Post link copied!');
    } catch {
      setToastMessage('Could not copy the link. Please try again.');
    }
  }

  function handleCommentsClick() {
    if (!isDetail) {
      const postUrl =
        `/music/community/posts/${displayPost.id}/` +
        `${encodeURIComponent(displayPost.slug)}#community-comments`;

      router.push(postUrl);
      return;
    }

    commentsSectionRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }

  if (isDeleted) return null;

  return (
    <>
      <article
        className={`
          relative mx-auto min-w-0 w-full
          transition-colors duration-200
          ${
            isDetail
              ? `
                max-w-3xl rounded-xl
                border border-light-border/80
                bg-light-surface
                px-4 py-5
                sm:px-5 sm:py-6
                dark:border-dark-border
                dark:bg-dark-surface
              `
              : isCompactRelatedPost
                ? `
                  rounded-lg
                  border-b border-light-border/60
                  px-1.5 py-2
                  dark:border-dark-border
                `
                : `
                  border-b border-light-border/70
                  px-3 py-3
                  hover:bg-light-surface/60
                  sm:px-4 sm:py-4
                  dark:border-dark-border
                  dark:hover:bg-dark-surface/40
                `
          }
        `}
      >
        {/* Author, individual rating and post actions */}
        <div
          className={`flex items-start justify-between ${
            isCompactRelatedPost ? 'gap-1.5' : 'gap-3'
          }`}
        >
          <div
            className={`flex min-w-0 flex-1 items-start ${
              isCompactRelatedPost ? 'gap-1.5' : 'gap-2.5 sm:gap-3'
            }`}
          >
            <Link
              href={`/account/${encodeURIComponent(username)}`}
              aria-label={`View ${displayName}'s profile`}
              className={`
                relative flex shrink-0 items-center justify-center
                overflow-hidden rounded-full
                text-sm font-extrabold tracking-wide
                ring-1 ring-black/5 transition-transform
                hover:scale-105
                focus-visible:outline-none
                focus-visible:ring-2 focus-visible:ring-brand-teal
                focus-visible:ring-offset-2
                dark:focus-visible:ring-offset-dark-surface
                ${
                  isCompactRelatedPost
                    ? 'h-8 w-8 text-xs'
                    : isDetail
                      ? 'h-10 w-10 sm:h-11 sm:w-11'
                      : 'h-9 w-9 text-sm sm:h-10 sm:w-10'
                }
              `}
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
                  unoptimized
                  sizes="(max-width: 640px) 40px, 44px"
                  className="rounded-full object-cover"
                  onError={() => setHasProfileImageError(true)}
                />
              ) : (
                initials
              )}
            </Link>

            <div className="min-w-0 flex-1">
              <div className="flex min-w-0 flex-wrap items-center gap-x-1.5 gap-y-0.5">
                <Link
                  href={`/account/${encodeURIComponent(username)}`}
                  className="
                    max-w-full truncate text-sm font-bold
                    text-light-text transition-colors
                    hover:text-brand-teal-dark
                    dark:text-dark-text
                    dark:hover:text-brand-teal-light
                  "
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

                {/*
                  Show the author's individual rating beside their name only
                  in compact related-post cards on song, album and artist
                  detail pages.
                */}
                {isCompactRelatedPost && hasRating && rating !== null && (
                  <span
                    className="inline-flex shrink-0 items-center gap-1"
                    aria-label={`Rated ${rating.toFixed(1)} out of 5 stars`}
                    title={`Rated ${rating.toFixed(1)} out of 5`}
                  >
                    <span
                      className="inline-flex items-center gap-px"
                      aria-hidden="true"
                    >
                      {STAR_VALUES.map((star) => {
                        const fillPercent = Math.max(
                          0,
                          Math.min(100, (rating - star + 1) * 100),
                        );

                        return (
                          <span
                            key={star}
                            className="relative inline-flex h-3 w-3 shrink-0"
                          >
                            <Star
                              className="absolute inset-0 h-3 w-3 text-light-border dark:text-dark-border"
                              strokeWidth={1.8}
                            />

                            {fillPercent > 0 && (
                              <Star
                                className="absolute inset-0 h-3 w-3 fill-brand-teal text-brand-teal"
                                strokeWidth={1.8}
                                style={{
                                  clipPath: `inset(0 ${100 - fillPercent}% 0 0)`,
                                }}
                              />
                            )}
                          </span>
                        );
                      })}
                    </span>

                    <span className="text-[11px] font-semibold tabular-nums text-light-text-soft dark:text-dark-text-soft">
                      {rating.toFixed(1)}
                    </span>
                  </span>
                )}
              </div>

              <div
                className={`flex min-w-0 items-center gap-1.5 text-xs text-light-text-soft dark:text-dark-text-soft ${
                  isCompactRelatedPost ? 'mt-0' : 'mt-0.5'
                }`}
              >
                <span className="truncate">@{cleanUsername}</span>

                {!isDetail && (
                  <>
                    <span aria-hidden="true">·</span>
                    <time
                      dateTime={displayPost.created_at}
                      title={formatFullDate(displayPost.created_at)}
                      className="shrink-0"
                    >
                      {formatRelativeTime(displayPost.created_at)}
                    </time>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-1">
            {!isOwner && showFollowButton && (
              <button
                type="button"
                onClick={() => void handleFollowToggle()}
                disabled={isFollowLoading}
                aria-label={
                  isFollowing
                    ? `Following @${cleanUsername}`
                    : isFollowingYou
                      ? `Follow back @${cleanUsername}`
                      : `Follow @${cleanUsername}`
                }
                className="
                  inline-flex min-h-8 items-center justify-center gap-1
                  rounded-full border border-brand-teal
                  bg-brand-teal px-2.5 py-1
                  text-xs font-semibold text-white
                  transition-colors hover:bg-brand-teal-dark
                  focus-visible:outline-none
                  focus-visible:ring-2 focus-visible:ring-brand-teal
                  focus-visible:ring-offset-2
                  disabled:cursor-not-allowed disabled:opacity-60
                  dark:focus-visible:ring-offset-dark-surface
                  sm:gap-1.5 sm:px-3
                "
              >
                {isFollowLoading ? (
                  <LoaderCircle
                    className="h-3.5 w-3.5 animate-spin"
                    aria-hidden="true"
                  />
                ) : isFollowing ? (
                  <UserMinus
                    className="h-3.5 w-3.5"
                    aria-hidden="true"
                  />
                ) : (
                  <UserPlus
                    className="h-3.5 w-3.5"
                    aria-hidden="true"
                  />
                )}

                <span>
                  {isFollowLoading
                    ? isFollowing
                      ? 'Following…'
                      : 'Unfollowing…'
                    : isFollowing
                      ? 'Following'
                      : isFollowingYou
                        ? 'Follow back'
                        : 'Follow'}
                </span>
              </button>
            )}
            <div ref={menuRef} className="relative shrink-0">
              <button
                type="button"
                aria-label="More post options"
                aria-haspopup="menu"
                aria-expanded={isMenuOpen}
                onClick={() => setIsMenuOpen((open) => !open)}
                className="
                  flex h-8 w-8 items-center justify-center rounded-full
                  text-light-text-soft transition-colors
                  hover:bg-light-surface-soft hover:text-light-text
                  focus-visible:outline-none
                  focus-visible:ring-2 focus-visible:ring-brand-teal
                  dark:text-dark-text-soft
                  dark:hover:bg-dark-surface-soft dark:hover:text-dark-text
                "
              >
                <MoreHorizontal className="h-5 w-5" aria-hidden="true" />
              </button>

              {isMenuOpen && (
                <div
                  role="menu"
                  aria-label="Post options"
                  className="
                    absolute right-0 top-full z-30 mt-2
                    w-56 overflow-hidden rounded-xl
                    border border-light-border
                    bg-light-surface p-1.5 shadow-xl
                    dark:border-dark-border dark:bg-dark-surface
                  "
                >
                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => void handleCopyPostLink()}
                    className={menuItemClass}
                  >
                    <Copy className="h-4 w-4 shrink-0" />
                    Copy post link
                  </button>

                  {isOwner ? (
                    <>
                      {canEditPost && (
                        <button
                          type="button"
                          role="menuitem"
                          onClick={openEditDialog}
                          className={menuItemClass}
                        >
                          <Pencil className="h-4 w-4 shrink-0" />
                          Edit post
                        </button>
                      )}

                      <button
                        type="button"
                        role="menuitem"
                        onClick={openDeleteDialog}
                        className={dangerMenuItemClass}
                      >
                        <Trash2 className="h-4 w-4 shrink-0" />
                        Delete post
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        role="menuitem"
                        disabled={isFollowLoading}
                        onClick={handleFollowMenuAction}
                        className={`
                          ${menuItemClass}
                          ${
                            isFollowing
                              ? 'text-red-600 hover:bg-red-500/10 dark:text-red-400'
                              : ''
                          }
                          disabled:cursor-not-allowed disabled:opacity-60
                        `}
                      >
                        {isFollowLoading ? (
                          <LoaderCircle className="h-4 w-4 shrink-0 animate-spin" />
                        ) : isFollowing ? (
                          <UserMinus className="h-4 w-4 shrink-0" />
                        ) : (
                          <UserPlus className="h-4 w-4 shrink-0" />
                        )}
                        {isFollowing
                          ? `Unfollow @${cleanUsername}`
                          : `Follow @${cleanUsername}`}
                      </button>

                      <button
                        type="button"
                        role="menuitem"
                        onClick={openReportDialog}
                        className={menuItemClass}
                      >
                        <Flag className="h-4 w-4 shrink-0" />
                        Report post
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {followError && (
          <p
            role="alert"
            className="mt-2 text-right text-xs text-red-600 dark:text-red-400"
          >
            {followError}
          </p>
        )}

        {/* Post content */}
        <div
          className={
            isCompactRelatedPost
              ? 'mt-1.5'
              : isDetail
                ? 'mt-5 sm:mt-6'
                : 'mt-3'
          }
        >
          <p
            className={`
              whitespace-pre-wrap break-words
              text-sm leading-relaxed
              text-light-text dark:text-dark-text
              ${
                isDetail
                  ? 'text-[15px] leading-7 sm:text-base sm:leading-7'
                  : isCompactRelatedPost
                    ? 'text-[13px] leading-[1.5]'
                    : ''
              }
            `}
          >
            <Link
              href={`/music/community/posts/${displayPost.id}/${encodeURIComponent(
                displayPost.slug,
              )}`}
              aria-label={`Read full community post by @${cleanUsername}`}
              className="
                rounded-sm
                focus-visible:outline-none
                focus-visible:ring-2 focus-visible:ring-brand-teal
              "
            >
              {displayedContent}
            </Link>

            {isContentTruncated && (
              <>
                {' '}
                <button
                  type="button"
                  onClick={() =>
                    setIsContentExpanded((expanded) => !expanded)
                  }
                  aria-expanded={isContentExpanded}
                  className="
                    inline font-semibold text-brand-teal
                    transition-colors hover:underline
                    focus-visible:outline-none focus-visible:underline
                    dark:text-brand-teal-light
                  "
                >
                  {isContentExpanded ? 'See less' : 'See more'}
                </button>
              </>
            )}
          </p>
        </div>

        {/* Music attachment */}
        {!hideMusicAttachment && displayPost.target && (
          <div
            className={
              isCompactRelatedPost
                ? 'mt-1.5'
                : isDetail
                  ? 'mt-5 sm:mt-6'
                  : 'mt-3'
            }
          >
            <MusicAttachment target={displayPost.target} />
          </div>
        )}

        {/* Detail-page publication and edit timestamps */}
        {isDetail && (
          <div className="mt-4 flex flex-wrap items-center gap-x-2 gap-y-2 text-xs text-light-text-soft dark:text-dark-text-soft">
            <time dateTime={displayPost.created_at}>
              {formatFullDate(displayPost.created_at)}
            </time>

            {displayPost.is_edited && (
              <>
                <span aria-hidden="true">·</span>

                <span className="inline-flex items-center gap-1">
                  <Pencil
                    className="h-3 w-3 shrink-0"
                    aria-hidden="true"
                  />
                  <span>Edited</span>

                  <time dateTime={displayPost.updated_at}>
                    {formatFullDate(displayPost.updated_at)}
                  </time>
                </span>
              </>
            )}
          </div>
        )}

        {/* Preserve existing engagement behavior. */}
        <div
          className={
            isCompactRelatedPost
              ? 'mt-1'
              : isDetail
                ? 'mt-5 border-t border-light-border/70 pt-4 dark:border-dark-border sm:mt-6 sm:pt-5'
                : 'mt-3 border-t border-light-border/60 pt-3 dark:border-dark-border'
          }
        >
          <MusicEngagementBar
            postId={displayPost.id}
            likesCount={displayPost.likes_count}
            isLiked={displayPost.is_liked}
            isFavorited={displayPost.is_favorited}
            favoritesCount={displayPost.favorites_count}
            commentsCount={displayPost.comments_count}
            viewsCount={displayPost.views_count}
            variant={variant}
            onCommentsClick={handleCommentsClick}
            likeCommentOnly={likeCommentOnly}
          />
        </div>
      </article>

      {isDetail && (
        <section
          ref={commentsSectionRef}
          id="community-comments"
          tabIndex={-1}
          aria-label="Community comments"
          className="
            mx-auto mt-8 w-full max-w-3xl
            scroll-mt-28 rounded-2xl
            border border-light-border/70
            px-4 py-5 shadow-sm outline-none
            focus-visible:ring-2 focus-visible:ring-brand-teal
            sm:mt-10 sm:px-6 sm:py-7
            lg:px-7 lg:py-7
            dark:border-dark-border
          "
        >
          <MusicPostComments
            postId={displayPost.id}
            initialCommentsCount={displayPost.comments_count}
          />
        </section>
      )}

      {/* Edit post dialog */}
      {activeDialog === 'edit' && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/60 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeActionDialog();
            }
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-community-post-title"
            className="
              my-auto w-full max-w-lg rounded-2xl
              border border-light-border bg-light-surface p-5 shadow-xl
              sm:p-6
              dark:border-dark-border dark:bg-dark-surface
            "
          >
            <div className="flex items-center justify-between gap-4">
              <h2
                id="edit-community-post-title"
                className="text-lg font-bold text-light-text dark:text-dark-text"
              >
                Edit post
              </h2>

              <button
                type="button"
                aria-label="Close edit dialog"
                disabled={isSaving}
                onClick={closeActionDialog}
                className={iconButtonClass}
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="mt-2 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
              Update your post without changing its music attachment.
            </p>

            <form
              className="mt-6 space-y-6"
              onSubmit={(event) => {
                event.preventDefault();
                void handleSaveEdit();
              }}
            >
              <div>
                <label
                  htmlFor={`edit-post-content-${displayPost.id}`}
                  className={labelClass}
                >
                  Post content
                </label>

                <textarea
                  id={`edit-post-content-${displayPost.id}`}
                  value={editContent}
                  onChange={(event) => setEditContent(event.target.value)}
                  maxLength={5000}
                  rows={6}
                  required
                  disabled={isSaving}
                  className={`${fieldClass} resize-y`}
                />

                <p className="mt-2 text-right text-xs text-light-text-soft dark:text-dark-text-soft">
                  {editContent.length}/5000
                </p>
              </div>

              {canRateTarget && (
                <div>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p
                        id={`edit-post-rating-label-${displayPost.id}`}
                        className={labelClass}
                      >
                        Rating
                      </p>

                      <p className="-mt-1 text-xs text-light-text-muted dark:text-dark-text-muted">
                        Optional. Rate it from 0.5 to 5 stars.
                      </p>
                    </div>

                    <div className="flex min-h-9 items-center">
                      <div
                        role="group"
                        aria-labelledby={`edit-post-rating-label-${displayPost.id}`}
                        aria-describedby={`edit-post-rating-help-${displayPost.id}`}
                        tabIndex={isSaving ? -1 : 0}
                        onMouseMove={handleRatingHover}
                        onMouseLeave={() => setHoverRating(null)}
                        onClick={handleRatingClick}
                        onKeyDown={handleRatingKeyDown}
                        className="
                          flex h-9 w-[180px] shrink-0
                          cursor-pointer items-center gap-0 rounded-lg
                          outline-none focus-visible:ring-2
                          focus-visible:ring-brand-teal focus-visible:ring-offset-2
                          dark:focus-visible:ring-offset-dark-surface
                        "
                      >
                        {STAR_VALUES.map(renderEditRatingStar)}
                      </div>

                      <span
                        aria-live="polite"
                        aria-atomic="true"
                        className="ml-2 inline-flex w-9 justify-center text-sm font-bold tabular-nums text-light-text dark:text-dark-text"
                      >
                        {displayedEditRating !== null
                          ? displayedEditRating.toFixed(1)
                          : '—'}
                      </span>

                      {editRating !== null && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditRating(null);
                            setHoverRating(null);
                            setEditError('');
                          }}
                          disabled={isSaving}
                          className="
                            ml-1 rounded-lg px-2 py-1.5 text-xs font-semibold
                            text-light-text-muted transition-colors
                            hover:bg-light-surface-soft hover:text-light-text
                            focus-visible:outline-none focus-visible:ring-2
                            focus-visible:ring-brand-teal
                            disabled:cursor-not-allowed disabled:opacity-50
                            dark:text-dark-text-muted
                            dark:hover:bg-dark-surface-soft dark:hover:text-dark-text
                          "
                        >
                          Clear
                        </button>
                      )}
                    </div>
                  </div>

                  <p
                    id={`edit-post-rating-help-${displayPost.id}`}
                    className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft"
                  >
                    Select a star for a full rating or its left half for a
                    half-star. Use arrow keys to adjust, Home or End for the
                    minimum or maximum, and Delete to clear the rating.
                  </p>
                </div>
              )}

              {editError && (
                <p
                  role="alert"
                  className="text-sm text-red-600 dark:text-red-400"
                >
                  {editError}
                </p>
              )}

              <div className="flex justify-end gap-3 pt-1">
                <button
                  type="button"
                  disabled={isSaving}
                  onClick={closeActionDialog}
                  className={secondaryButtonClass}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={isSaving || !editContent.trim()}
                  className={primaryButtonClass}
                >
                  {isSaving ? (
                    <>
                      <LoaderCircle className="h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save changes'
                  )}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}

      {/* Delete confirmation dialog */}
      {activeDialog === 'delete' && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/60 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeActionDialog();
            }
          }}
        >
          <section
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="delete-community-post-title"
            aria-describedby="delete-community-post-description"
            className="
              my-auto w-full max-w-md rounded-2xl
              border border-light-border bg-light-surface p-6 shadow-xl
              sm:p-7
              dark:border-dark-border dark:bg-dark-surface
            "
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2
                  id="delete-community-post-title"
                  className="text-lg font-bold text-light-text dark:text-dark-text"
                >
                  Delete this post?
                </h2>

                <p
                  id="delete-community-post-description"
                  className="mt-3 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted"
                >
                  Your post will be removed from the community. This action
                  cannot be undone from this dialog.
                </p>
              </div>

              <button
                type="button"
                aria-label="Close delete dialog"
                disabled={isDeleting}
                onClick={closeActionDialog}
                className={iconButtonClass}
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {deleteError && (
              <p
                role="alert"
                className="mt-4 text-sm text-red-600 dark:text-red-400"
              >
                {deleteError}
              </p>
            )}

            <div className="mt-7 flex justify-end gap-3">
              <button
                type="button"
                disabled={isDeleting}
                onClick={closeActionDialog}
                className={secondaryButtonClass}
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={isDeleting}
                onClick={() => void handleDeletePost()}
                className="
                  inline-flex items-center justify-center gap-2
                  rounded-lg bg-red-600 px-4 py-2.5
                  text-sm font-semibold text-white transition-colors
                  hover:bg-red-700 focus-visible:outline-none
                  focus-visible:ring-2 focus-visible:ring-red-500
                  focus-visible:ring-offset-2
                  disabled:cursor-not-allowed disabled:opacity-60
                "
              >
                {isDeleting ? (
                  <>
                    <LoaderCircle className="h-4 w-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  'Delete post'
                )}
              </button>
            </div>
          </section>
        </div>
      )}

      <ReportContentModal
        isOpen={isReportOpen}
        onClose={closeReportDialog}
        endpoint={`/api/v1/music/community/posts/${displayPost.id}/report/`}
        contentLabel="post"
      />

      {toastMessage && (
        <div
          role="status"
          aria-live="polite"
          className="
            fixed bottom-5 left-1/2 z-[100]
            w-max max-w-[calc(100%-2rem)] -translate-x-1/2
            rounded-xl border border-light-border
            bg-light-surface px-5 py-3.5
            text-sm font-medium text-light-text shadow-xl
            dark:border-dark-border dark:bg-dark-surface dark:text-dark-text
          "
        >
          {toastMessage}
        </div>
      )}
    </>
  );
}

const menuItemClass = `
  flex w-full items-center gap-3
  rounded-lg px-3 py-2.5
  text-left text-sm font-medium
  text-light-text transition-colors
  hover:bg-light-surface-soft
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal
  dark:text-dark-text dark:hover:bg-dark-surface-soft
`;

const dangerMenuItemClass = `
  flex w-full items-center gap-3
  rounded-lg px-3 py-2.5
  text-left text-sm font-medium text-red-600
  transition-colors hover:bg-red-500/10
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500
  dark:text-red-400
`;

const labelClass = `
  mb-2.5 block text-sm font-semibold
  text-light-text dark:text-dark-text
`;

const fieldClass = `
  w-full rounded-xl
  border border-light-border bg-light-surface
  px-4 py-3 text-sm leading-6 text-light-text outline-none
  transition-colors focus:border-brand-teal
  focus:ring-2 focus:ring-brand-teal/20
  disabled:cursor-not-allowed disabled:opacity-60
  dark:border-dark-border dark:bg-dark-surface dark:text-dark-text
`;

const primaryButtonClass = `
  inline-flex items-center justify-center gap-2
  rounded-lg bg-brand-teal px-4 py-2.5
  text-sm font-semibold text-white transition-colors
  hover:bg-brand-teal-dark
  focus-visible:outline-none focus-visible:ring-2
  focus-visible:ring-brand-teal focus-visible:ring-offset-2
  disabled:cursor-not-allowed disabled:opacity-60
`;

const secondaryButtonClass = `
  inline-flex items-center justify-center
  rounded-lg border border-light-border px-4 py-2.5
  text-sm font-semibold text-light-text transition-colors
  hover:bg-light-surface-soft
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal
  disabled:cursor-not-allowed disabled:opacity-60
  dark:border-dark-border dark:text-dark-text
  dark:hover:bg-dark-surface-soft
`;

const iconButtonClass = `
  flex h-9 w-9 shrink-0 items-center justify-center
  rounded-full text-light-text-muted transition-colors
  hover:bg-light-surface-soft hover:text-light-text
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal
  disabled:cursor-not-allowed disabled:opacity-50
  dark:text-dark-text-muted dark:hover:bg-dark-surface-soft
  dark:hover:text-dark-text
`;

function getAvatarColor(username: string): {
  background: string;
  foreground: string;
} {
  const colors = [
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

  let hash = 0;

  for (let index = 0; index < username.length; index += 1) {
    hash = (hash * 31 + username.charCodeAt(index)) >>> 0;
  }

  return colors[hash % colors.length];
}

/**
 * Accept numeric ratings and numeric strings from API responses.
 * Community ratings use half-star increments from 0.5 to 5.
 */
function getPostRating(value: unknown): number | null {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return null;
  }

  const numericValue =
    typeof value === 'number'
      ? value
      : typeof value === 'string'
        ? Number(value.trim())
        : Number.NaN;

  if (!Number.isFinite(numericValue) || numericValue <= 0) {
    return null;
  }

  return clampRating(numericValue);
}

function clampRating(value: number): number {
  return Math.min(
    RATING_MAX,
    Math.max(RATING_MIN, Math.round(value * 2) / 2),
  );
}

function getRatingFromPointer(
  event: MouseEvent<HTMLDivElement>,
): number {
  const container = event.currentTarget.getBoundingClientRect();

  if (container.width <= 0) return RATING_MIN;

  const relativeX = Math.min(
    container.width,
    Math.max(0, event.clientX - container.left),
  );

  const starWidth = container.width / STAR_VALUES.length;

  const starIndex = Math.min(
    STAR_VALUES.length - 1,
    Math.floor(relativeX / starWidth),
  );

  const positionWithinStar = relativeX - starIndex * starWidth;
  const isLeftHalf = positionWithinStar < starWidth / 2;

  const rawRating = starIndex + (isLeftHalf ? 0.5 : 1);

  return clampRating(rawRating);
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message || 'The request could not be completed.';
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return 'Something went wrong. Please try again.';
}

function formatFullDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return 'Date unavailable';
  }

  return new Intl.DateTimeFormat('en-NG', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

function formatRelativeTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return 'Recently';

  const difference = Date.now() - date.getTime();

  if (difference < 0) return 'Just now';

  const seconds = Math.floor(difference / 1000);

  if (seconds < 60) return 'Just now';

  const minutes = Math.floor(seconds / 60);

  if (minutes < 60) return `${minutes}m`;

  const hours = Math.floor(minutes / 60);

  if (hours < 24) return `${hours}h`;

  const days = Math.floor(hours / 24);

  if (days < 30) return `${days}d`;

  const months = Math.floor(days / 30);

  if (months < 12) return `${months}mo`;

  const years = Math.floor(months / 12);

  return `${years}y`;
}