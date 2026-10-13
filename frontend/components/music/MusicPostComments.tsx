'use client';

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from 'react';
import Link from 'next/link';
import {
  ArrowDown,
  CornerUpLeft,
  MessageCircle,
  Send,
  X,
} from 'lucide-react';

import { useAuth } from '@/components/auth/AuthProvider';
import ConfirmationModal from '@/components/ui/ConfirmationModal';
import ReportContentModal from '@/components/ui/ReportContentModal';
import MusicPostCommentItem from '@/components/music/MusicPostCommentItem';

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
  // Pagination belongs to the root conversation, not each nested reply.
  next: string | null;
  // For a root, this is the total number of descendants in its thread.
  count: number;
  // Number of unique descendants loaded for the root conversation.
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
const MAX_COMPOSER_LINES = 3;
const INITIAL_COMPOSER_HEIGHT = 140;
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

  const composerRef = useRef<HTMLFormElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const composerContainerRef = useRef<HTMLDivElement>(null);

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

  // Replies are stored under their exact parent comment ID.
  // Only a root comment owns thread pagination and exposes thread controls.
  const [repliesByComment, setRepliesByComment] = useState<
    Record<number, ReplyState>
  >({});

  const [highlightedCommentId, setHighlightedCommentId] =
    useState<number | null>(null);

  // Kept pending until React has rendered the target element into the DOM.
  const [pendingNavigationId, setPendingNavigationId] =
    useState<number | null>(null);

  const [draft, setDraft] = useState('');
  const [composerMode, setComposerMode] = useState<ComposerMode>({
    type: 'comment',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [commentToDelete, setCommentToDelete] =
    useState<CommunityComment | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const [commentToReport, setCommentToReport] =
    useState<CommunityComment | null>(null);

  const [keyboardOffset, setKeyboardOffset] = useState(0);
  const [composerHeight, setComposerHeight] = useState(
    INITIAL_COMPOSER_HEIGHT,
  );

  const authenticated = isAuthenticated === true;

  const resizeComposer = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = 'auto';

    const styles = window.getComputedStyle(textarea);
    const computedLineHeight = Number.parseFloat(styles.lineHeight);

    const lineHeight = Number.isFinite(computedLineHeight)
      ? computedLineHeight
      : 20;

    const paddingTop = Number.parseFloat(styles.paddingTop) || 0;
    const paddingBottom = Number.parseFloat(styles.paddingBottom) || 0;
    const borderTop = Number.parseFloat(styles.borderTopWidth) || 0;
    const borderBottom = Number.parseFloat(styles.borderBottomWidth) || 0;

    const maximumHeight =
      lineHeight * MAX_COMPOSER_LINES +
      paddingTop +
      paddingBottom +
      borderTop +
      borderBottom;

    const nextHeight = Math.min(textarea.scrollHeight, maximumHeight);

    textarea.style.height = `${nextHeight}px`;
    textarea.style.overflowY =
      textarea.scrollHeight > maximumHeight ? 'auto' : 'hidden';
  }, []);

  useEffect(() => {
    resizeComposer();
  }, [draft, composerMode.type, resizeComposer]);

  useEffect(() => {
    const container = composerContainerRef.current;
    if (!container) return;

    const updateHeight = () => {
      const height = container.getBoundingClientRect().height;

      if (height > 0) {
        setComposerHeight((current) =>
          Math.abs(current - height) > 1 ? height : current,
        );
      }
    };

    updateHeight();

    let observer: ResizeObserver | null = null;

    if (typeof ResizeObserver !== 'undefined') {
      observer = new ResizeObserver(updateHeight);
      observer.observe(container);
    }

    window.addEventListener('resize', updateHeight);

    return () => {
      observer?.disconnect();
      window.removeEventListener('resize', updateHeight);
    };
  }, [
    authenticated,
    composerMode.type,
    isAuthLoading,
    isAuthenticated,
    submitError,
    keyboardOffset,
  ]);

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

  const focusComposer = useCallback(() => {
    window.setTimeout(() => {
      textareaRef.current?.focus({ preventScroll: true });
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

  // Follow actual parent IDs until the top-level comment is reached.
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
                comment.thread_replies_count + difference,
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
   * Load exactly one page from the root conversation's thread endpoint.
   *
   * The API returns descendants at every nesting level. Each result is
   * inserted into the bucket identified by its real parent ID, so replies
   * to replies retain their correct visual nesting.
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

            // A thread endpoint should only return descendants.
            // Skip malformed entries without a parent instead of rendering
            // a root comment as a reply.
            if (comment.parent === null) {
              continue;
            }

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
   *
   * The pending ID is resolved by an effect after React has rendered any
   * newly loaded reply thread. This avoids querying the DOM too early.
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

      // If the target is known but its root thread is not rendered yet,
      // load the first thread page. The pending-navigation effect will
      // scroll once the target is present in the DOM.
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
    (comment: CommunityComment) => {
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
      focusComposer();
    },
    [
      authenticated,
      focusComposer,
      isAuthLoading,
      isAuthenticated,
      requireAuth,
    ],
  );

  const startEdit = useCallback(
    (comment: CommunityComment) => {
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
      focusComposer();
    },
    [
      authenticated,
      focusComposer,
      isAuthLoading,
      isAuthenticated,
      requireAuth,
    ],
  );

  const submitComment = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

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

      // Keep the selected comment as the direct parent, even for nested replies.
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
      comment: CommunityComment,
    ): Promise<CommunityCommentLikeResponse> => {
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
        const response = comment.is_liked
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
    [authenticated, isAuthLoading, isAuthenticated, requireAuth],
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

  // Render a reply and its loaded descendants. Thread pagination controls
  // are rendered only by the root comment, after the complete reply tree.
  const renderReply = (reply: CommunityComment): ReactNode => {
    const replyState = repliesByComment[reply.id];

    const replyTo =
      reply.parent === null ? null : findLoadedComment(reply.parent);

    return (
      <div key={reply.id} className="min-w-0">
        <MusicPostCommentItem
          comment={reply}
          replyTo={replyTo}
          currentUserId={
            user?.id && Number.isFinite(Number(user.id))
              ? Number(user.id)
              : null
          }
          isAuthenticated={authenticated}
          onReply={startReply}
          onEdit={startEdit}
          onDelete={setCommentToDelete}
          onReport={setCommentToReport}
          onLike={handleLike}
          onRequireAuth={requireAuth}
          onNavigateToComment={navigateToComment}
          isHighlighted={highlightedCommentId === reply.id}
          depth={1}
        />

        {replyState?.error && (
          <p
            role="alert"
            className="ml-3 mt-1 text-xs text-red-600 dark:text-red-300"
          >
            We could not load some replies in this thread. Try loading the
            conversation again from the original comment.
          </p>
        )}

        {replyState?.comments.length ? (
          <div className="mt-4 space-y-4">
            {replyState.comments.map((childReply) =>
              renderReply(childReply),
            )}
          </div>
        ) : null}
      </div>
    );
  };

  const renderRootComment = (comment: CommunityComment): ReactNode => {
    const replyState = repliesByComment[comment.id];

    const totalThreadReplies = Math.max(
      comment.thread_replies_count ?? 0,
      replyState?.count ?? 0,
    );

    const nextThreadPage = getNextPage(replyState?.next ?? null);

    return (
      <div key={comment.id} className="min-w-0">
        <MusicPostCommentItem
          comment={comment}
          currentUserId={
            user?.id && Number.isFinite(Number(user.id))
              ? Number(user.id)
              : null
          }
          isAuthenticated={authenticated}
          onReply={startReply}
          onEdit={startEdit}
          onDelete={setCommentToDelete}
          onReport={setCommentToReport}
          onLike={handleLike}
          onRequireAuth={requireAuth}
          onNavigateToComment={navigateToComment}
          isHighlighted={highlightedCommentId === comment.id}
          depth={0}
        />

        {totalThreadReplies > 0 && (
          <div className="mt-3 pl-2">
            {/*
              Render the entire loaded tree first. Since renderReply is
              recursive, this includes every currently loaded nested reply.
              The root's pagination and retry controls are placed afterward.
            */}
            {replyState?.loaded && replyState.comments.length > 0 && (
              <div className="space-y-5 border-l border-light-border pl-3 dark:border-dark-border sm:pl-4">
                {replyState.comments.map((reply) => renderReply(reply))}
              </div>
            )}

            {!replyState?.loaded && !replyState?.error && (
              <button
                type="button"
                onClick={() =>
                  void loadReplyThreadPage(comment.id, 1)
                }
                disabled={replyState?.loading}
                className="mt-1 inline-flex min-h-9 items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm font-semibold text-brand-teal transition-colors hover:bg-brand-teal/10 disabled:opacity-60"
              >
                {replyState?.loading ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-teal/30 border-t-brand-teal" />
                ) : (
                  <ArrowDown size={15} />
                )}

                {replyState?.loading
                  ? 'Loading replies…'
                  : `View ${totalThreadReplies} ${
                      totalThreadReplies === 1 ? 'reply' : 'replies'
                    }`}
              </button>
            )}

            {replyState?.loaded &&
              replyState.next &&
              !replyState.error && (
                <div className="mt-3">
                  <button
                    type="button"
                    onClick={() =>
                      void loadReplyThreadPage(
                        comment.id,
                        nextThreadPage,
                      )
                    }
                    disabled={replyState.loading}
                    className="inline-flex min-h-9 items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm font-semibold text-brand-teal transition-colors hover:bg-brand-teal/10 disabled:opacity-60"
                  >
                    {replyState.loading ? (
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-teal/30 border-t-brand-teal" />
                    ) : (
                      <ArrowDown size={15} />
                    )}

                    {replyState.loading
                      ? 'Loading replies…'
                      : 'Load more replies'}
                  </button>
                </div>
              )}

            {replyState?.error && (
              <div className="mt-3">
                <p
                  role="alert"
                  className="text-sm text-red-600 dark:text-red-300"
                >
                  {replyState.error}
                </p>

                <button
                  type="button"
                  onClick={() =>
                    void loadReplyThreadPage(
                      comment.id,
                      replyState.loaded
                        ? nextThreadPage
                        : 1,
                    )
                  }
                  disabled={replyState.loading}
                  className="mt-1 inline-flex min-h-9 items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm font-semibold text-brand-teal transition-colors hover:bg-brand-teal/10 disabled:opacity-60"
                >
                  {replyState.loading ? (
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-teal/30 border-t-brand-teal" />
                  ) : (
                    <ArrowDown size={15} />
                  )}

                  {replyState.loading
                    ? 'Retrying…'
                    : replyState.loaded
                      ? 'Retry loading more replies'
                      : 'Try again'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <section
      aria-labelledby={`${sectionId}-heading`}
      className="relative"
      style={{
        paddingBottom: `calc(${composerHeight}px + ${keyboardOffset}px + env(safe-area-inset-bottom, 0px) + 1rem)`,
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
          className="mb-5 rounded-xl border border-red-500/25 bg-red-500/5 p-4"
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

      {isLoadingComments ? (
        <div className="space-y-6" aria-label="Loading comments">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="flex animate-pulse gap-3 sm:gap-4">
              <div className="h-10 w-10 shrink-0 rounded-full bg-light-surface-muted dark:bg-dark-surface-muted" />

              <div className="flex-1 space-y-3">
                <div className="h-16 max-w-md rounded-2xl bg-light-surface-muted dark:bg-dark-surface-muted" />
                <div className="h-3 w-24 rounded bg-light-surface-soft dark:bg-dark-surface-soft" />
              </div>
            </div>
          ))}
        </div>
      ) : comments.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-light-border px-5 py-10 text-center dark:border-dark-border sm:px-8 sm:py-12">
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
          {comments.map((comment) => renderRootComment(comment))}

          {nextPage && (
            <div className="pt-3 text-center">
              <button
                type="button"
                onClick={() => void loadMoreComments()}
                disabled={isLoadingMore}
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-light-border px-5 py-2.5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-soft disabled:opacity-60 dark:border-dark-border dark:text-dark-text dark:hover:bg-dark-surface-soft"
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

      <div
        className="pointer-events-none fixed inset-x-0 z-40"
        style={{
          bottom: `calc(${keyboardOffset}px + env(safe-area-inset-bottom, 0px))`,
        }}
      >
        <div
          ref={composerContainerRef}
          className="pointer-events-auto mx-auto w-full max-w-3xl px-3 py-3 sm:px-6 sm:py-4"
        >
          {isAuthLoading || isAuthenticated === null ? (
            <div className="flex min-h-11 items-center gap-3">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-teal/30 border-t-brand-teal" />

              <p className="text-sm text-light-text-muted dark:text-dark-text-muted">
                Checking your sign-in status…
              </p>
            </div>
          ) : !authenticated ? (
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                  Join the conversation
                </p>

                <p className="mt-0.5 text-xs text-light-text-muted dark:text-dark-text-muted">
                  Sign in to comment, reply, and like.
                </p>
              </div>

              <Link
                href={loginUrl}
                className="inline-flex min-h-10 shrink-0 items-center justify-center rounded-xl bg-brand-teal px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2"
              >
                Log in
              </Link>
            </div>
          ) : (
            <>
              {composerMode.type !== 'comment' && (
                <div className="mb-2 flex items-center justify-between gap-3 rounded-xl border border-brand-teal/15 bg-light-surface px-3 py-2.5 dark:bg-dark-surface">
                  <div className="flex min-w-0 items-center gap-2 text-sm text-light-text dark:text-dark-text">
                    <CornerUpLeft
                      size={16}
                      className="shrink-0 text-brand-teal"
                    />

                    <span className="truncate">
                      {composerMode.type === 'reply'
                        ? `Replying to @${composerMode.comment.user.username}`
                        : 'Editing your comment'}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={cancelComposerMode}
                    disabled={isSubmitting}
                    aria-label="Cancel reply or editing"
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-light-text-muted transition-colors hover:bg-brand-teal/10 hover:text-light-text disabled:opacity-50 dark:text-dark-text-muted dark:hover:text-dark-text"
                  >
                    <X size={16} />
                  </button>
                </div>
              )}

              <form
                ref={composerRef}
                onSubmit={submitComment}
                className="flex items-end gap-2.5"
              >
                <label
                  className="sr-only"
                  htmlFor={`${sectionId}-composer`}
                >
                  {composerMode.type === 'edit'
                    ? 'Edit comment'
                    : composerMode.type === 'reply'
                      ? 'Write a reply'
                      : 'Write a comment'}
                </label>

                <textarea
                  ref={textareaRef}
                  id={`${sectionId}-composer`}
                  value={draft}
                  onChange={(event) => {
                    setDraft(
                      event.target.value.slice(0, MAX_COMMENT_LENGTH),
                    );
                    setSubmitError(null);
                  }}
                  onKeyDown={(event) => {
                    if (
                      event.key === 'Enter' &&
                      !event.shiftKey &&
                      !event.nativeEvent.isComposing
                    ) {
                      event.preventDefault();
                      composerRef.current?.requestSubmit();
                    }
                  }}
                  rows={1}
                  maxLength={MAX_COMMENT_LENGTH}
                  placeholder={
                    composerMode.type === 'edit'
                      ? 'Edit your comment…'
                      : composerMode.type === 'reply'
                        ? 'Write a reply…'
                        : 'Write a comment…'
                  }
                  disabled={isSubmitting}
                  className="min-h-11 min-w-0 flex-1 resize-none overflow-y-hidden rounded-2xl border border-light-border bg-light-bg px-4 py-3 text-base leading-5 text-light-text outline-none transition-colors placeholder:text-light-text-soft focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-bg dark:text-dark-text dark:placeholder:text-dark-text-soft sm:text-sm"
                />

                <button
                  type="submit"
                  disabled={isSubmitting || !draft.trim()}
                  aria-label={
                    composerMode.type === 'edit'
                      ? 'Save edited comment'
                      : composerMode.type === 'reply'
                        ? 'Send reply'
                        : 'Send comment'
                  }
                  className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-teal text-white transition-colors hover:bg-brand-teal-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </form>

              {submitError && (
                <p
                  role="alert"
                  className="mt-2 text-xs text-red-600 dark:text-red-300"
                >
                  {submitError}
                </p>
              )}
            </>
          )}
        </div>
      </div>

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