'use client';

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
} from 'react';
import {
  MessageCircle,
} from 'lucide-react';

import { useAuth } from '@/components/auth/AuthProvider';
import ConfirmationModal from '@/components/ui/ConfirmationModal';
import ReportContentModal from '@/components/ui/ReportContentModal';

import CommentComposer from '@/components/comments/CommentComposer';
import CommentThread from '@/components/comments/CommentThread';

import type {
  SharedComment,
  SharedCommentLikeResponse,
} from '@/components/comments/CommentItem';

import type {
  CommentThreadState,
} from '@/components/comments/CommentThread';

import {
  createCommunityComment,
  deleteCommunityComment,
  getCommunityComments,
  getCommunityCommentThread,
  likeCommunityComment,
  unlikeCommunityComment,
  updateCommunityComment,
} from '@/lib/music/CommunityPosts';

import type {
  CommunityComment,
  CommunityCommentLikeResponse,
  CommunityCommentsResponse,
} from '@/lib/music/CommunityPosts';

type MusicPostCommentsProps = {
  postId: number;
  initialCommentsCount?: number;
};

type ReplyState = {
  // Only direct children of this parent are stored here.
  comments: CommunityComment[];

  // Pagination belongs to the root conversation.
  next: string | null;

  // Total descendants in the root conversation.
  count: number;

  // Unique descendants loaded for this root conversation.
  loadedCount: number;

  loading: boolean;
  loaded: boolean;
  error: string | null;
};

type ComposerMode =
  | { type: 'comment' }
  | { type: 'reply'; comment: CommunityComment }
  | { type: 'edit'; comment: CommunityComment };

const PAGE_SIZE = 20;
const REPLY_PAGE_SIZE = 5;
const MAX_COMMENT_LENGTH = 10000;
const COMMENT_HIGHLIGHT_DURATION_MS = 2000;

const EMPTY_REPLY_STATE: ReplyState = {
  comments: [],
  next: null,
  count: 0,
  loadedCount: 0,
  loading: false,
  loaded: false,
  error: null,
};

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return fallback;
}

function getNextPage(nextUrl: string | null): number {
  if (!nextUrl) return 1;

  try {
    const url = new URL(
      nextUrl,
      typeof window !== 'undefined'
        ? window.location.origin
        : 'http://localhost',
    );

    const page = Number(url.searchParams.get('page'));

    return Number.isFinite(page) && page > 0 ? page : 1;
  } catch {
    return 1;
  }
}

function makeNextPageUrl(page: number): string {
  return `?page=${page}`;
}

function mergeComments(
  existing: CommunityComment[],
  incoming: CommunityComment[],
): CommunityComment[] {
  const merged = new Map<number, CommunityComment>();

  for (const comment of existing) {
    merged.set(comment.id, comment);
  }

  for (const comment of incoming) {
    merged.set(comment.id, comment);
  }

  return Array.from(merged.values());
}

/**
 * Adapt the community API's snake_case fields to the shared
 * presentation component's camelCase contract.
 *
 * The actual comment IDs and parent IDs are never changed.
 */
function toSharedComment(comment: CommunityComment): SharedComment {
  return {
    id: comment.id,
    user: {
      id: comment.user.id,
      username: comment.user.username,
    },
    parent: comment.parent,
    content: comment.content,
    createdAt: comment.created_at,
    likesCount: comment.likes_count,
    isLiked: Boolean(comment.is_liked),
    repliesCount: comment.replies_count,
    isEdited: Boolean(comment.is_edited),
    status: comment.status,
  };
}

function collectLoadedSubtreeIds(
  targetId: number,
  comments: CommunityComment[],
  repliesByComment: Record<number, ReplyState>,
): Set<number> {
  const allComments = new Map<number, CommunityComment>();

  for (const comment of comments) {
    allComments.set(comment.id, comment);
  }

  for (const state of Object.values(repliesByComment)) {
    for (const comment of state.comments) {
      allComments.set(comment.id, comment);
    }
  }

  const removedIds = new Set<number>([targetId]);
  let foundDescendant = true;

  while (foundDescendant) {
    foundDescendant = false;

    for (const comment of allComments.values()) {
      if (
        comment.parent !== null &&
        removedIds.has(comment.parent) &&
        !removedIds.has(comment.id)
      ) {
        removedIds.add(comment.id);
        foundDescendant = true;
      }
    }
  }

  return removedIds;
}

export default function MusicPostComments({
  postId,
  initialCommentsCount = 0,
}: MusicPostCommentsProps) {
  const { user, isAuthenticated, isLoading: isAuthLoading } = useAuth();

  const sectionId = useId();

  const sectionRef = useRef<HTMLElement>(null);
  const requestVersionRef = useRef(0);
  const postGenerationRef = useRef(0);
  const replyRequestVersionsRef = useRef<Record<number, number>>({});
  const likeRequestsRef = useRef<Set<number>>(new Set());
  const highlightTimeoutRef = useRef<number | null>(null);

  const [comments, setComments] = useState<CommunityComment[]>([]);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [commentsCount, setCommentsCount] = useState(initialCommentsCount);
  const [isLoadingComments, setIsLoadingComments] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [commentsError, setCommentsError] = useState<string | null>(null);

  // Every bucket contains only direct children of its key.
  // The shared CommentThread flattens the display without changing parents.
  const [repliesByComment, setRepliesByComment] = useState<
    Record<number, ReplyState>
  >({});

  const [highlightedCommentId, setHighlightedCommentId] =
    useState<number | null>(null);

  const [pendingNavigationId, setPendingNavigationId] =
    useState<number | null>(null);

  const [draft, setDraft] = useState('');
  const [composerMode, setComposerMode] = useState<ComposerMode>({
    type: 'comment',
  });

  // Increment this whenever Reply or Edit should focus the composer.
  const [focusRequestKey, setFocusRequestKey] = useState(0);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [commentToDelete, setCommentToDelete] =
    useState<CommunityComment | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const [commentToReport, setCommentToReport] =
    useState<CommunityComment | null>(null);

  const [keyboardOffset, setKeyboardOffset] = useState(0);

  const authenticated = isAuthenticated === true;

  const getCurrentUrl = useCallback(() => {
    if (typeof window === 'undefined') {
      return `/music/community/posts/${postId}/`;
    }

    return (
      window.location.pathname +
      window.location.search +
      window.location.hash
    );
  }, [postId]);

  const loginUrl = `/login?next=${encodeURIComponent(getCurrentUrl())}`;

  const requireAuth = useCallback(() => {
    if (typeof window === 'undefined') return;

    const currentUrl =
      window.location.pathname +
      window.location.search +
      window.location.hash;

    window.location.assign(
      `/login?next=${encodeURIComponent(currentUrl)}`,
    );
  }, []);

  // Retained for validation errors that should return focus to the composer.
  const focusComposer = useCallback(() => {
    window.setTimeout(() => {
      sectionRef.current
        ?.querySelector<HTMLTextAreaElement>('textarea')
        ?.focus({ preventScroll: true });
    }, 50);
  }, []);

  const cancelComposerMode = useCallback(() => {
    setComposerMode({ type: 'comment' });
    setDraft('');
    setSubmitError(null);
  }, []);

  const loadComments = useCallback(async () => {
    const version = ++requestVersionRef.current;
    const requestedPostId = postId;

    setIsLoadingComments(true);
    setCommentsError(null);

    try {
      const response: CommunityCommentsResponse =
        await getCommunityComments(requestedPostId, {
          page: 1,
          pageSize: PAGE_SIZE,
        });

      if (
        version !== requestVersionRef.current ||
        requestedPostId !== postId
      ) {
        return;
      }

      // Preserve comments submitted while this request was in flight.
      setComments((current) =>
        mergeComments(response.results, current),
      );

      setNextPage(response.next);
      setCommentsCount(response.count);
    } catch (error) {
      if (
        version !== requestVersionRef.current ||
        requestedPostId !== postId
      ) {
        return;
      }

      setCommentsError(
        getErrorMessage(error, 'We could not load the comments.'),
      );
    } finally {
      if (version === requestVersionRef.current) {
        setIsLoadingComments(false);
      }
    }
  }, [postId]);

  useEffect(() => {
    postGenerationRef.current += 1;
    requestVersionRef.current += 1;

    if (highlightTimeoutRef.current !== null) {
      window.clearTimeout(highlightTimeoutRef.current);
      highlightTimeoutRef.current = null;
    }

    setComments([]);
    setNextPage(null);
    setCommentsCount(initialCommentsCount);
    setRepliesByComment({});
    setComposerMode({ type: 'comment' });
    setDraft('');
    setSubmitError(null);
    setCommentsError(null);
    setIsLoadingMore(false);
    setIsSubmitting(false);
    setIsDeleting(false);
    setCommentToDelete(null);
    setCommentToReport(null);
    setHighlightedCommentId(null);
    setPendingNavigationId(null);
    setFocusRequestKey(0);

    replyRequestVersionsRef.current = {};
    likeRequestsRef.current.clear();

    void loadComments();

    return () => {
      requestVersionRef.current += 1;
      postGenerationRef.current += 1;

      if (highlightTimeoutRef.current !== null) {
        window.clearTimeout(highlightTimeoutRef.current);
        highlightTimeoutRef.current = null;
      }
    };
  }, [initialCommentsCount, loadComments]);

  useEffect(() => {
    const viewport = window.visualViewport;
    if (!viewport) return;

    const updateKeyboardOffset = () => {
      setKeyboardOffset(
        Math.max(
          0,
          window.innerHeight - viewport.height - viewport.offsetTop,
        ),
      );
    };

    updateKeyboardOffset();

    viewport.addEventListener('resize', updateKeyboardOffset);
    viewport.addEventListener('scroll', updateKeyboardOffset);

    return () => {
      viewport.removeEventListener('resize', updateKeyboardOffset);
      viewport.removeEventListener('scroll', updateKeyboardOffset);
    };
  }, []);

  // Find a comment anywhere in the currently loaded conversation.
  const findLoadedComment = useCallback(
    (commentId: number): CommunityComment | null => {
      const root = comments.find((comment) => comment.id === commentId);

      if (root) return root;

      for (const state of Object.values(repliesByComment)) {
        const found = state.comments.find(
          (comment) => comment.id === commentId,
        );

        if (found) return found;
      }

      return null;
    },
    [comments, repliesByComment],
  );

  // Follow real parent IDs until the top-level comment is reached.
  const findRootCommentId = useCallback(
    (commentId: number): number => {
      let current = findLoadedComment(commentId);
      const visited = new Set<number>();

      while (
        current &&
        current.parent !== null &&
        !visited.has(current.id)
      ) {
        visited.add(current.id);

        const parent = findLoadedComment(current.parent);

        if (!parent) {
          return current.parent;
        }

        current = parent;
      }

      return current?.id ?? commentId;
    },
    [findLoadedComment],
  );

  const updateCommentInState = useCallback(
    (updated: CommunityComment) => {
      setComments((current) =>
        current.map((comment) =>
          comment.id === updated.id ? updated : comment,
        ),
      );

      setRepliesByComment((current) => {
        const next = { ...current };

        for (const [parentId, state] of Object.entries(next)) {
          next[Number(parentId)] = {
            ...state,
            comments: state.comments.map((comment) =>
              comment.id === updated.id ? updated : comment,
            ),
          };
        }

        return next;
      });

      setComposerMode((current) => {
        if (
          current.type !== 'comment' &&
          current.comment.id === updated.id
        ) {
          return { ...current, comment: updated };
        }

        return current;
      });
    },
    [],
  );

  // Update direct-child counts when a reply is created or deleted.
  const updateRepliesCount = useCallback(
    (parentId: number, difference: number) => {
      const adjust = (comment: CommunityComment) =>
        comment.id === parentId
          ? {
              ...comment,
              replies_count: Math.max(
                0,
                comment.replies_count + difference,
              ),
            }
          : comment;

      setComments((current) => current.map(adjust));

      setRepliesByComment((current) => {
        const next = { ...current };

        for (const [id, state] of Object.entries(next)) {
          next[Number(id)] = {
            ...state,
            comments: state.comments.map(adjust),
          };
        }

        return next;
      });
    },
    [],
  );

  // Keep the root's total descendant count separate from direct replies_count.
  const updateThreadRepliesCount = useCallback(
    (rootId: number, difference: number) => {
      const adjust = (comment: CommunityComment) =>
        comment.id === rootId
          ? {
              ...comment,
              thread_replies_count: Math.max(
                0,
                (comment.thread_replies_count ?? 0) + difference,
              ),
            }
          : comment;

      setComments((current) => current.map(adjust));

      setRepliesByComment((current) => {
        const next = { ...current };

        for (const [id, state] of Object.entries(next)) {
          const parentId = Number(id);

          next[parentId] = {
            ...state,
            comments: state.comments.map(adjust),
            count:
              parentId === rootId
                ? Math.max(0, state.count + difference)
                : state.count,
            loadedCount:
              parentId === rootId && state.loaded
                ? Math.max(0, state.loadedCount + difference)
                : state.loadedCount,
          };
        }

        return next;
      });
    },
    [],
  );

  /**
   * Load one page of descendants from the root conversation's thread endpoint.
   * Each descendant is stored under its actual parent ID.
   */
  const loadReplyThreadPage = useCallback(
    async (rootCommentId: number, page = 1) => {
      const generation = postGenerationRef.current;

      const version =
        (replyRequestVersionsRef.current[rootCommentId] ?? 0) + 1;

      replyRequestVersionsRef.current[rootCommentId] = version;

      setRepliesByComment((current) => {
        const previous = current[rootCommentId] ?? EMPTY_REPLY_STATE;

        return {
          ...current,
          [rootCommentId]: {
            ...previous,
            loading: true,
            error: null,
          },
        };
      });

      try {
        const response = await getCommunityCommentThread(
          postId,
          rootCommentId,
          { page },
        );

        if (
          postGenerationRef.current !== generation ||
          replyRequestVersionsRef.current[rootCommentId] !== version
        ) {
          return;
        }

        setRepliesByComment((current) => {
          const next = { ...current };
          const existingIds = new Set<number>();

          for (const state of Object.values(current)) {
            for (const comment of state.comments) {
              existingIds.add(comment.id);
            }
          }

          let newUniqueCount = 0;

          for (const comment of response.results) {
            if (!existingIds.has(comment.id)) {
              existingIds.add(comment.id);
              newUniqueCount += 1;
            }

            // A thread endpoint should return descendants, not root comments.
            if (comment.parent === null) continue;

            const parentId = comment.parent;
            const previousParentState =
              next[parentId] ?? EMPTY_REPLY_STATE;

            next[parentId] = {
              ...previousParentState,
              comments: mergeComments(
                previousParentState.comments,
                [comment],
              ),
              loading: false,
              loaded: true,
              error: null,
            };
          }

          const previousRootState =
            next[rootCommentId] ?? EMPTY_REPLY_STATE;

          next[rootCommentId] = {
            ...previousRootState,
            next: response.next,
            count: response.count,
            loadedCount: Math.min(
              response.count,
              previousRootState.loadedCount + newUniqueCount,
            ),
            loading: false,
            loaded: true,
            error: null,
          };

          return next;
        });
      } catch (error) {
        if (
          postGenerationRef.current !== generation ||
          replyRequestVersionsRef.current[rootCommentId] !== version
        ) {
          return;
        }

        setRepliesByComment((current) => {
          const previous = current[rootCommentId] ?? EMPTY_REPLY_STATE;

          return {
            ...current,
            [rootCommentId]: {
              ...previous,
              loading: false,
              error: getErrorMessage(
                error,
                'We could not load these replies.',
              ),
            },
          };
        });
      }
    },
    [postId],
  );

  /**
   * Navigate to a comment or reply and briefly highlight it.
   * The pending ID is resolved after React renders the target.
   */
  const navigateToComment = useCallback(
    (commentId: number) => {
      setPendingNavigationId(commentId);

      const target = findLoadedComment(commentId);

      if (!target || target.parent === null) {
        return;
      }

      const rootId = findRootCommentId(commentId);
      const rootState = repliesByComment[rootId];

      if (!rootState?.loaded && !rootState?.loading) {
        void loadReplyThreadPage(rootId, 1);
      }
    },
    [
      findLoadedComment,
      findRootCommentId,
      loadReplyThreadPage,
      repliesByComment,
    ],
  );

  useEffect(() => {
    if (pendingNavigationId === null) return;

    const targetId = pendingNavigationId;
    const targetElement = document.getElementById(
      `community-comment-${targetId}`,
    );

    if (!targetElement) return;

    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    });

    setHighlightedCommentId(targetId);
    setPendingNavigationId(null);

    if (highlightTimeoutRef.current !== null) {
      window.clearTimeout(highlightTimeoutRef.current);
    }

    highlightTimeoutRef.current = window.setTimeout(() => {
      setHighlightedCommentId((current) =>
        current === targetId ? null : current,
      );

      highlightTimeoutRef.current = null;
    }, COMMENT_HIGHLIGHT_DURATION_MS);
  }, [pendingNavigationId, comments, repliesByComment]);

  useEffect(() => {
    return () => {
      if (highlightTimeoutRef.current !== null) {
        window.clearTimeout(highlightTimeoutRef.current);
      }
    };
  }, []);

  const startReply = useCallback(
    (sharedComment: SharedComment) => {
      const comment = findLoadedComment(sharedComment.id);
      if (!comment) return;

      if (isAuthLoading || isAuthenticated === null) {
        setSubmitError('Please wait while we check your sign-in status.');
        return;
      }

      if (!authenticated) {
        requireAuth();
        return;
      }

      setComposerMode({ type: 'reply', comment });
      setDraft('');
      setSubmitError(null);

      // Ask CommentComposer to focus its textarea after the mode updates.
      setFocusRequestKey((current) => current + 1);
    },
    [
      authenticated,
      findLoadedComment,
      isAuthLoading,
      isAuthenticated,
      requireAuth,
    ],
  );

  const startEdit = useCallback(
    (sharedComment: SharedComment) => {
      const comment = findLoadedComment(sharedComment.id);
      if (!comment) return;

      if (isAuthLoading || isAuthenticated === null) {
        setSubmitError('Please wait while we check your sign-in status.');
        return;
      }

      if (!authenticated) {
        requireAuth();
        return;
      }

      setComposerMode({ type: 'edit', comment });
      setDraft(comment.content);
      setSubmitError(null);

      // Ask CommentComposer to focus its textarea after the mode updates.
      setFocusRequestKey((current) => current + 1);
    },
    [
      authenticated,
      findLoadedComment,
      isAuthLoading,
      isAuthenticated,
      requireAuth,
    ],
  );

  const submitComment = async () => {
    if (isSubmitting) return;

    if (isAuthLoading || isAuthenticated === null) {
      setSubmitError('Please wait while we check your sign-in status.');
      return;
    }

    if (!authenticated) {
      requireAuth();
      return;
    }

    const content = draft.trim();

    if (!content) {
      setSubmitError('Write something before submitting.');
      focusComposer();
      return;
    }

    if (content.length > MAX_COMMENT_LENGTH) {
      setSubmitError(
        `Comments can contain at most ${MAX_COMMENT_LENGTH} characters.`,
      );
      return;
    }

    const generation = postGenerationRef.current;
    const requestedPostId = postId;
    const submittedMode = composerMode;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      if (submittedMode.type === 'edit') {
        const updated = await updateCommunityComment(
          submittedMode.comment.id,
          { content },
        );

        if (
          postGenerationRef.current !== generation ||
          requestedPostId !== postId
        ) {
          return;
        }

        updateCommentInState(updated);
        cancelComposerMode();
        return;
      }

      // Nested replies keep their selected comment as the actual parent.
      const parentId =
        submittedMode.type === 'reply'
          ? submittedMode.comment.id
          : null;

      const created = await createCommunityComment({
        post: requestedPostId,
        parent: parentId,
        content,
      });

      if (
        postGenerationRef.current !== generation ||
        requestedPostId !== postId
      ) {
        return;
      }

      if (parentId === null) {
        setComments((current) => mergeComments([created], current));
        setCommentsCount((current) => current + 1);
      } else {
        setRepliesByComment((current) => {
          const previous = current[parentId] ?? EMPTY_REPLY_STATE;

          const mergedComments = mergeComments(
            previous.comments,
            [created],
          );

          const newCount = Math.max(
            previous.count + 1,
            mergedComments.length,
          );

          const next =
            previous.next ??
            (newCount > mergedComments.length
              ? makeNextPageUrl(
                  Math.floor(
                    mergedComments.length / REPLY_PAGE_SIZE,
                  ) + 1,
                )
              : null);

          return {
            ...current,
            [parentId]: {
              ...previous,
              comments: mergedComments,
              next,
              count: newCount,
              loading: false,
              loaded: true,
              error: null,
            },
          };
        });

        setCommentsCount((current) => current + 1);
        updateRepliesCount(parentId, 1);

        const rootId = findRootCommentId(parentId);
        updateThreadRepliesCount(rootId, 1);
      }

      cancelComposerMode();
    } catch (error) {
      if (postGenerationRef.current === generation) {
        setSubmitError(
          getErrorMessage(
            error,
            'Your comment could not be submitted. Please try again.',
          ),
        );
      }
    } finally {
      if (postGenerationRef.current === generation) {
        setIsSubmitting(false);
      }
    }
  };

  const handleLike = useCallback(
    async (
      sharedComment: SharedComment,
    ): Promise<SharedCommentLikeResponse> => {
      const comment = findLoadedComment(sharedComment.id);

      if (!comment) {
        throw new Error('This comment is no longer available.');
      }

      if (isAuthLoading || isAuthenticated === null) {
        throw new Error('Please wait while we check your sign-in status.');
      }

      if (!authenticated) {
        requireAuth();

        return {
          liked: Boolean(comment.is_liked),
          likes_count: comment.likes_count,
        };
      }

      if (likeRequestsRef.current.has(comment.id)) {
        return {
          liked: Boolean(comment.is_liked),
          likes_count: comment.likes_count,
        };
      }

      const generation = postGenerationRef.current;
      likeRequestsRef.current.add(comment.id);

      try {
        const response: CommunityCommentLikeResponse = comment.is_liked
          ? await unlikeCommunityComment(comment.id)
          : await likeCommunityComment(comment.id);

        if (postGenerationRef.current !== generation) {
          return response;
        }

        const updateLike = (item: CommunityComment) =>
          item.id === comment.id
            ? {
                ...item,
                is_liked: response.liked,
                likes_count: response.likes_count,
              }
            : item;

        setComments((current) => current.map(updateLike));

        setRepliesByComment((current) => {
          const next = { ...current };

          for (const [parentId, state] of Object.entries(next)) {
            next[Number(parentId)] = {
              ...state,
              comments: state.comments.map(updateLike),
            };
          }

          return next;
        });

        return response;
      } catch (error) {
        if (postGenerationRef.current === generation) {
          setSubmitError(
            getErrorMessage(
              error,
              'We could not update that like. Please try again.',
            ),
          );
        }

        throw error;
      } finally {
        likeRequestsRef.current.delete(comment.id);
      }
    },
    [
      authenticated,
      findLoadedComment,
      isAuthLoading,
      isAuthenticated,
      requireAuth,
    ],
  );

  const confirmDelete = async () => {
    if (!commentToDelete || isDeleting) return;

    const deletedComment = commentToDelete;
    const deletedId = deletedComment.id;
    const requestedPostId = postId;
    const generation = postGenerationRef.current;

    const rootId =
      deletedComment.parent === null
        ? deletedId
        : findRootCommentId(deletedId);

    setIsDeleting(true);
    setCommentsError(null);

    try {
      await deleteCommunityComment(deletedId);

      if (
        postGenerationRef.current !== generation ||
        requestedPostId !== postId
      ) {
        return;
      }

      const directParentId = deletedComment.parent;

      const removedIds = collectLoadedSubtreeIds(
        deletedId,
        comments,
        repliesByComment,
      );

      // Invalidate pending requests for the deleted subtree.
      for (const removedId of removedIds) {
        replyRequestVersionsRef.current[removedId] =
          (replyRequestVersionsRef.current[removedId] ?? 0) + 1;
      }

      if (directParentId !== null) {
        replyRequestVersionsRef.current[directParentId] =
          (replyRequestVersionsRef.current[directParentId] ?? 0) + 1;
      }

      setComments((current) =>
        current
          .filter((comment) => !removedIds.has(comment.id))
          .map((comment) =>
            comment.id === directParentId
              ? {
                  ...comment,
                  replies_count: Math.max(
                    0,
                    comment.replies_count - 1,
                  ),
                }
              : comment,
          ),
      );

      setRepliesByComment((current) => {
        const next: Record<number, ReplyState> = {};

        for (const [id, state] of Object.entries(current)) {
          const parentId = Number(id);

          if (removedIds.has(parentId)) continue;

          next[parentId] = {
            ...state,
            comments: state.comments
              .filter((comment) => !removedIds.has(comment.id))
              .map((comment) =>
                comment.id === directParentId
                  ? {
                      ...comment,
                      replies_count: Math.max(
                        0,
                        comment.replies_count - 1,
                      ),
                    }
                  : comment,
              ),
            count:
              parentId === directParentId
                ? Math.max(0, state.count - 1)
                : state.count,
          };
        }

        return next;
      });

      setCommentsCount((current) =>
        Math.max(0, current - removedIds.size),
      );

      if (directParentId !== null) {
        updateThreadRepliesCount(rootId, -removedIds.size);
      }

      setComposerMode((current) => {
        if (
          current.type !== 'comment' &&
          removedIds.has(current.comment.id)
        ) {
          return { type: 'comment' };
        }

        return current;
      });

      if (
        composerMode.type !== 'comment' &&
        removedIds.has(composerMode.comment.id)
      ) {
        setDraft('');
        setSubmitError(null);
      }

      if (
        highlightedCommentId !== null &&
        removedIds.has(highlightedCommentId)
      ) {
        setHighlightedCommentId(null);
        setPendingNavigationId(null);

        if (highlightTimeoutRef.current !== null) {
          window.clearTimeout(highlightTimeoutRef.current);
          highlightTimeoutRef.current = null;
        }
      }

      setCommentToDelete(null);

      try {
        const response = await getCommunityComments(requestedPostId, {
          page: 1,
          pageSize: PAGE_SIZE,
        });

        if (
          postGenerationRef.current !== generation ||
          requestedPostId !== postId
        ) {
          return;
        }

        setComments((current) =>
          mergeComments(
            response.results,
            current.filter((comment) => !removedIds.has(comment.id)),
          ),
        );

        setNextPage(response.next);
        setCommentsCount(response.count);
        setIsLoadingMore(false);

        const visibleRootIds = new Set(
          response.results.map((comment) => comment.id),
        );

        setRepliesByComment((current) => {
          const next: Record<number, ReplyState> = {};

          for (const [id, state] of Object.entries(current)) {
            const parentId = Number(id);

            if (
              !visibleRootIds.has(parentId) ||
              removedIds.has(parentId)
            ) {
              continue;
            }

            next[parentId] = state;
          }

          return next;
        });
      } catch {
        if (
          postGenerationRef.current === generation &&
          requestedPostId === postId
        ) {
          setCommentsError(
            'The comment was deleted, but we could not refresh the comment list. Please try again.',
          );
        }
      }
    } catch (error) {
      if (postGenerationRef.current === generation) {
        setCommentsError(
          getErrorMessage(
            error,
            'We could not delete that comment. Please try again.',
          ),
        );
      }
    } finally {
      if (postGenerationRef.current === generation) {
        setIsDeleting(false);
      }
    }
  };

  const loadMoreComments = async () => {
    if (!nextPage || isLoadingMore) return;

    const requestedNextPage = nextPage;
    const requestedPostId = postId;
    const generation = postGenerationRef.current;
    const requestVersion = requestVersionRef.current;

    setIsLoadingMore(true);
    setCommentsError(null);

    try {
      const response = await getCommunityComments(requestedPostId, {
        page: getNextPage(requestedNextPage),
        pageSize: PAGE_SIZE,
      });

      if (
        postGenerationRef.current !== generation ||
        requestedPostId !== postId ||
        requestVersion !== requestVersionRef.current
      ) {
        return;
      }

      setComments((current) =>
        mergeComments(current, response.results),
      );

      setNextPage(response.next);
      setCommentsCount(response.count);
    } catch (error) {
      if (
        postGenerationRef.current === generation &&
        requestedPostId === postId &&
        requestVersion === requestVersionRef.current
      ) {
        setCommentsError(
          getErrorMessage(error, 'We could not load more comments.'),
        );
      }
    } finally {
      if (
        postGenerationRef.current === generation &&
        requestedPostId === postId
      ) {
        setIsLoadingMore(false);
      }
    }
  };

  // Normalize root comments for the shared thread component.
  const sharedComments = comments.map(toSharedComment);

  // Normalize each direct-parent bucket while retaining real parent IDs.
  const sharedRepliesByComment: Record<string, SharedComment[]> = {};

  for (const [parentId, state] of Object.entries(repliesByComment)) {
    sharedRepliesByComment[parentId] = state.comments.map(toSharedComment);
  }

  // Thread pagination/loading state is owned by each root conversation.
  const threadStates: Record<string, CommentThreadState> = {};

  for (const [rootId, state] of Object.entries(repliesByComment)) {
    threadStates[rootId] = {
      loadedCount: state.loadedCount,
      count: state.count,
      hasMore: Boolean(state.next),
      isLoading: state.loading,
      error: state.error,
    };
  }

  const handleSharedDelete = (comment: SharedComment) => {
    const original = findLoadedComment(comment.id);
    if (original) setCommentToDelete(original);
  };

  const handleSharedReport = (comment: SharedComment) => {
    const original = findLoadedComment(comment.id);
    if (original) setCommentToReport(original);
  };

  const handleLoadReplies = (rootCommentId: number) => {
    const state = repliesByComment[rootCommentId];

    if (state?.loading) return;

    const page = state?.loaded ? getNextPage(state.next) : 1;

    void loadReplyThreadPage(rootCommentId, page);
  };

  const handleCreatorComment = (comment: SharedComment): boolean => {
    const original = findLoadedComment(comment.id);

    if (!original || original.post_creator_id == null) {
      return false;
    }

    return String(original.post_creator_id) === String(original.user.id);
  };

  const currentUserId =
    user?.id != null && Number.isFinite(Number(user.id))
      ? Number(user.id)
      : null;

  const replyingTo =
    composerMode.type === 'reply'
      ? toSharedComment(composerMode.comment)
      : null;

  const editingComment =
    composerMode.type === 'edit'
      ? toSharedComment(composerMode.comment)
      : null;

  return (
    <section
      ref={sectionRef}
      aria-labelledby={`${sectionId}-heading`}
      className="relative"
      style={{
        // Reserve room for the fixed shared composer and mobile safe area.
        paddingBottom: `calc(240px + ${keyboardOffset}px + env(safe-area-inset-bottom, 0px))`,
      }}
    >
      <div className="mb-6 flex items-center justify-between gap-3">
        <h2
          id={`${sectionId}-heading`}
          className="flex items-center gap-2 text-lg font-bold text-light-text dark:text-dark-text sm:text-xl"
        >
          <MessageCircle size={21} />

          Comments

          <span className="text-sm font-medium text-light-text-muted dark:text-dark-text-muted">
            {commentsCount}
          </span>
        </h2>
      </div>

      {commentsError && (
        <div
          role="alert"
          className="mb-5 rounded-xl bg-red-500/5 p-4"
        >
          <p className="text-sm leading-6 text-light-text dark:text-dark-text">
            {commentsError}
          </p>

          <button
            type="button"
            onClick={() => void loadComments()}
            className="mt-2 text-sm font-semibold text-brand-teal hover:underline"
          >
            Try again
          </button>
        </div>
      )}

      {submitError && (
        <p
          role="alert"
          className="mb-4 rounded-lg bg-red-500/5 px-3 py-2 text-sm text-red-600 dark:text-red-300"
        >
          {submitError}
        </p>
      )}

      {isLoadingComments ? (
        <div className="space-y-6" aria-label="Loading comments">
          {Array.from({ length: 3 }).map((_, index) => (
            <div
              key={index}
              className="flex animate-pulse gap-3 sm:gap-4"
            >
              <div className="h-10 w-10 shrink-0 rounded-full bg-light-surface-muted dark:bg-dark-surface-muted" />

              <div className="flex-1 space-y-3">
                <div className="h-16 max-w-md rounded-2xl bg-light-surface-muted dark:bg-dark-surface-muted" />
                <div className="h-3 w-24 rounded bg-light-surface-soft dark:bg-dark-surface-soft" />
              </div>
            </div>
          ))}
        </div>
      ) : comments.length === 0 ? (
        <div className="rounded-2xl bg-light-surface-soft px-5 py-10 text-center dark:bg-dark-surface-soft sm:px-8 sm:py-12">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal">
            <MessageCircle size={23} />
          </div>

          <h3 className="mt-4 font-semibold text-light-text dark:text-dark-text">
            Start the conversation
          </h3>

          <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
            Share your thoughts and keep the conversation going.
          </p>
        </div>
      ) : (
        <div className="space-y-6 sm:space-y-7">
          <CommentThread
            comments={sharedComments}
            repliesByComment={sharedRepliesByComment}
            threadStates={threadStates}
            currentUserId={currentUserId}
            isAuthenticated={authenticated}
            onReply={startReply}
            onEdit={startEdit}
            onDelete={handleSharedDelete}
            onReport={handleSharedReport}
            onLike={handleLike}
            onRequireAuth={requireAuth}
            onNavigateToComment={navigateToComment}
            onLoadReplies={handleLoadReplies}
            highlightedCommentId={highlightedCommentId ?? undefined}
            isCreatorComment={handleCreatorComment}
            commentIdPrefix="community-comment"
            emptyMessage="No comments yet. Start the conversation."
          />

          {nextPage && (
            <div className="pt-3 text-center">
              <button
                type="button"
                onClick={() => void loadMoreComments()}
                disabled={isLoadingMore}
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-light-surface-soft px-5 py-2.5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-muted disabled:cursor-not-allowed disabled:opacity-60 dark:bg-dark-surface-soft dark:text-dark-text dark:hover:bg-dark-surface-muted"
              >
                {isLoadingMore && (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-teal/30 border-t-brand-teal" />
                )}

                {isLoadingMore ? 'Loading…' : 'Load more comments'}
              </button>
            </div>
          )}
        </div>
      )}

      {isAuthLoading || isAuthenticated === null ? (
        <div
          className="fixed inset-x-0 z-40"
          style={{
            bottom: `calc(${keyboardOffset}px + env(safe-area-inset-bottom, 0px))`,
          }}
        >
          <div className="mx-auto flex min-h-20 w-full max-w-3xl items-center gap-3 px-3 py-3 sm:px-6 sm:py-4">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-teal/30 border-t-brand-teal" />

            <p className="text-sm text-light-text-muted dark:text-dark-text-muted">
              Checking your sign-in status…
            </p>
          </div>
        </div>
      ) : (
        <CommentComposer
          value={draft}
          onChange={(value) => {
            setDraft(value.slice(0, MAX_COMMENT_LENGTH));
            setSubmitError(null);
          }}
          onSubmit={submitComment}
          isAuthenticated={authenticated}
          isSubmitting={isSubmitting}
          replyingTo={replyingTo}
          editingComment={editingComment}
          onCancelContext={cancelComposerMode}
          maxLength={MAX_COMMENT_LENGTH}
          placeholder={
            composerMode.type === 'edit'
              ? 'Edit your comment…'
              : composerMode.type === 'reply'
                ? 'Write a reply…'
                : 'Write a comment…'
          }
          loginHref={loginUrl}
          focusRequestKey={focusRequestKey}
          className="z-40"
        />
      )}

      <ConfirmationModal
        open={commentToDelete !== null}
        title="Delete this comment?"
        description="This comment and its replies will be removed from the conversation."
        confirmLabel="Delete comment"
        destructive
        isLoading={isDeleting}
        onCancel={() => {
          if (!isDeleting) setCommentToDelete(null);
        }}
        onConfirm={confirmDelete}
      />

      <ReportContentModal
        isOpen={commentToReport !== null}
        onClose={() => setCommentToReport(null)}
        endpoint={
          commentToReport
            ? `/api/v1/music/community/comments/${commentToReport.id}/report/`
            : '/api/v1/music/community/comments/0/report/'
        }
        contentLabel={
          commentToReport?.parent === null ? 'comment' : 'reply'
        }
      />
    </section>
  );
}