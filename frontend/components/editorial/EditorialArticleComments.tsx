'use client';

import {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import { usePathname } from 'next/navigation';
import {
    LoaderCircle,
    MessageCircle,
    X,
} from 'lucide-react';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/components/auth/AuthProvider';
import ConfirmationModal from '@/components/ui/ConfirmationModal';
import ReportContentModal from '@/components/ui/ReportContentModal';

import CommentComposer from '@/components/comments/CommentComposer';
import CommentThread, {
    type CommentThreadState,
} from '@/components/comments/CommentThread';
import type {
    SharedComment,
    SharedCommentLikeResponse,
} from '@/components/comments/CommentItem';

import {
    createEditorialComment,
    deleteEditorialComment,
    getEditorialComments,
    getEditorialCommentThread,
    likeEditorialComment,
    unlikeEditorialComment,
    updateEditorialComment,
} from '@/lib/music/EditorialArticles';

import type {
    EditorialComment,
    EditorialCommentLikeResponse,
    EditorialCommentsResponse,
} from '@/lib/music/EditorialArticles';

type EditorialArticleCommentsProps = {
    articleId: number;
    initialCommentsCount?: number;
};

type ThreadState = {
    comments: EditorialComment[];
    page: number;
    failedPage: number | null;
    hasMore: boolean;
    loading: boolean;
    error: string | null;
    loaded: boolean;
};

const ROOT_PAGE_SIZE = 20;
const COMMENT_MAX_LENGTH = 3000;
const EDIT_WINDOW_MS = 15 * 60 * 1000;
const HIGHLIGHT_DURATION_MS = 2000;

function getErrorMessage(error: unknown): string {
    if (error instanceof ApiError) {
        return error.message || 'Something went wrong. Please try again.';
    }

    if (error instanceof Error) {
        return error.message || 'Something went wrong. Please try again.';
    }

    return 'Something went wrong. Please try again.';
}

function normalizeId(
    value: string | number | null | undefined,
): string {
    return value == null ? '' : String(value);
}

function canEditComment(comment: EditorialComment): boolean {
    const createdAt = new Date(comment.created_at).getTime();

    return (
        Number.isFinite(createdAt) &&
        Date.now() <= createdAt + EDIT_WINDOW_MS
    );
}

function isUnavailableComment(comment: EditorialComment): boolean {
    return comment.status === 'hidden' || comment.status === 'removed';
}

function updateCommentInList(
    comments: EditorialComment[],
    commentId: number,
    updater: (comment: EditorialComment) => EditorialComment,
): EditorialComment[] {
    return comments.map((comment) =>
        comment.id === commentId ? updater(comment) : comment,
    );
}

function collectSubtreeIds(
    comments: EditorialComment[],
    commentId: number,
): Set<number> {
    const removedIds = new Set<number>([commentId]);
    let changed = true;

    while (changed) {
        changed = false;

        for (const comment of comments) {
            if (
                comment.parent != null &&
                removedIds.has(comment.parent) &&
                !removedIds.has(comment.id)
            ) {
                removedIds.add(comment.id);
                changed = true;
            }
        }
    }

    return removedIds;
}

function removeCommentSubtree(
    comments: EditorialComment[],
    commentId: number,
): EditorialComment[] {
    const removedIds = collectSubtreeIds(comments, commentId);

    return comments.filter((comment) => !removedIds.has(comment.id));
}

function mergeComments(
    existing: EditorialComment[],
    incoming: EditorialComment[],
): EditorialComment[] {
    const unique = new Map<number, EditorialComment>();

    for (const comment of existing) {
        unique.set(comment.id, comment);
    }

    for (const comment of incoming) {
        const previous = unique.get(comment.id);

        unique.set(
            comment.id,
            previous ? { ...previous, ...comment } : comment,
        );
    }

    return [...unique.values()].sort((a, b) => {
        const difference =
            new Date(a.created_at).getTime() -
            new Date(b.created_at).getTime();

        return difference || a.id - b.id;
    });
}

/**
 * Adapt the editorial API's snake_case response to the shared
 * comment component's camelCase representation.
 *
 * The API models remain unchanged; this is a frontend-only adapter.
 */
function toSharedComment(comment: EditorialComment): SharedComment {
    return {
        id: comment.id,
        user: {
            id: comment.user.id,
            username: comment.user.username,
            display_name: comment.user.display_name,
            profile_image: comment.user.profile_image,
            is_verified: comment.user.is_verified,
            is_identity_verified: comment.user.is_identity_verified,
        },
        parent: comment.parent,
        content: comment.content,
        mentionedUsernames: comment.mentioned_usernames ?? [],
        createdAt: comment.created_at,
        likesCount: comment.likes_count,
        isLiked: comment.liked,
        repliesCount: comment.replies_count,
        isEdited: comment.is_edited,
        status: comment.status,
    };
}

export default function EditorialArticleComments({
    articleId,
    initialCommentsCount = 0,
}: EditorialArticleCommentsProps) {
    const {
        user,
        isAuthenticated,
        isLoading: isAuthLoading,
    } = useAuth();

    const pathname = usePathname();

    const [comments, setComments] = useState<EditorialComment[]>([]);
    const [commentsCount, setCommentsCount] = useState(initialCommentsCount);

    const [rootPage, setRootPage] = useState(1);
    const [hasMoreRoots, setHasMoreRoots] = useState(false);
    const [loadingRoots, setLoadingRoots] = useState(true);
    const [loadingMoreRoots, setLoadingMoreRoots] = useState(false);
    const [rootError, setRootError] = useState<string | null>(null);

    const [threads, setThreads] = useState<Record<number, ThreadState>>({});

    const [draft, setDraft] = useState('');
    const [replyTo, setReplyTo] = useState<EditorialComment | null>(null);
    const [editingComment, setEditingComment] =
        useState<EditorialComment | null>(null);

    const [submitting, setSubmitting] = useState(false);
    const [actionError, setActionError] = useState<string | null>(null);

    /**
     * Increment this key to tell CommentComposer to focus its textarea.
     * It changes whenever the user starts replying to or editing a comment.
     */
    const [focusRequestKey, setFocusRequestKey] = useState(0);

    const [commentToDelete, setCommentToDelete] =
        useState<EditorialComment | null>(null);
    const [deleting, setDeleting] = useState(false);

    const [commentToReport, setCommentToReport] =
        useState<EditorialComment | null>(null);

    const [highlightedCommentId, setHighlightedCommentId] =
        useState<number | null>(null);
    const [menuMessage, setMenuMessage] = useState<string | null>(null);

    const requestGenerationRef = useRef(0);
    const loadingRootsRef = useRef(false);
    const loadingMoreRootsRef = useRef(false);
    const loadingThreadsRef = useRef(new Set<number>());
    const highlightTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
        null,
    );

    const currentUserId = normalizeId(user?.id);
    const authenticated = isAuthenticated === true;

    const rootComments = useMemo(
        () => comments.filter((comment) => comment.parent == null),
        [comments],
    );

    const sharedComments = useMemo(
        () => comments.map(toSharedComment),
        [comments],
    );

    const sharedRootComments = useMemo(
        () => rootComments.map(toSharedComment),
        [rootComments],
    );

    /**
     * Group loaded comments by their direct parent.
     *
     * Each key is a parent comment ID, and its value contains that
     * comment's loaded replies. Replies to replies remain associated
     * with their immediate parent.
     */
    const repliesByComment = useMemo(() => {
        const grouped: Record<string, SharedComment[]> = {};

        for (const comment of sharedComments) {
            if (comment.parent == null) {
                continue;
            }

            const parentId = String(comment.parent);

            if (!grouped[parentId]) {
                grouped[parentId] = [];
            }

            grouped[parentId].push(comment);
        }

        return grouped;
    }, [sharedComments]);

    const commentsById = useMemo(
        () => new Map(comments.map((comment) => [comment.id, comment])),
        [comments],
    );

    const getRootId = useCallback(
        (comment: EditorialComment): number => {
            if (comment.parent == null) return comment.id;

            if (comment.root_comment != null) {
                return comment.root_comment;
            }

            let current: EditorialComment | undefined = comment;
            const visited = new Set<number>();

            while (current?.parent != null && !visited.has(current.id)) {
                visited.add(current.id);
                current = commentsById.get(current.parent);
            }

            return current?.id ?? comment.id;
        },
        [commentsById],
    );

    const threadStates = useMemo<Record<string, CommentThreadState>>(() => {
        const result: Record<string, CommentThreadState> = {};

        for (const root of rootComments) {
            const thread = threads[root.id];

            result[String(root.id)] = {
                loadedCount: thread?.comments.length ?? 0,
                count: root.thread_replies_count,
                hasMore: thread?.hasMore ?? root.thread_replies_count > 0,
                isLoading: thread?.loading ?? false,
                error: thread?.error ?? null,
            };
        }

        return result;
    }, [rootComments, threads]);

    const fetchRoots = useCallback(
        async (page: number, append: boolean) => {
            if (loadingRootsRef.current || loadingMoreRootsRef.current) return;

            if (append) {
                loadingMoreRootsRef.current = true;
                setLoadingMoreRoots(true);
            } else {
                loadingRootsRef.current = true;
                setLoadingRoots(true);
            }

            setRootError(null);

            const generation = requestGenerationRef.current;

            try {
                const response: EditorialCommentsResponse =
                    await getEditorialComments(articleId, {
                        page,
                        pageSize: ROOT_PAGE_SIZE,
                    });

                if (generation !== requestGenerationRef.current) return;

                setComments((previous) =>
                    append
                        ? mergeComments(previous, response.results)
                        : mergeComments([], response.results),
                );

                setRootPage(page);
                setHasMoreRoots(Boolean(response.next));
            } catch (error) {
                if (generation === requestGenerationRef.current) {
                    setRootError(getErrorMessage(error));
                }
            } finally {
                if (generation === requestGenerationRef.current) {
                    if (append) {
                        loadingMoreRootsRef.current = false;
                        setLoadingMoreRoots(false);
                    } else {
                        loadingRootsRef.current = false;
                        setLoadingRoots(false);
                    }
                }
            }
        },
        [articleId],
    );

    useEffect(() => {
        requestGenerationRef.current += 1;

        loadingRootsRef.current = false;
        loadingMoreRootsRef.current = false;
        loadingThreadsRef.current.clear();

        setComments([]);
        setThreads({});
        setRootPage(1);
        setHasMoreRoots(false);
        setCommentsCount(initialCommentsCount);
        setRootError(null);
        setLoadingRoots(true);
        setLoadingMoreRoots(false);
        setReplyTo(null);
        setEditingComment(null);
        setDraft('');
        setActionError(null);
        setCommentToDelete(null);
        setCommentToReport(null);
        setHighlightedCommentId(null);
        setMenuMessage(null);
        setFocusRequestKey(0);

        void fetchRoots(1, false);

        return () => {
            requestGenerationRef.current += 1;

            if (highlightTimeoutRef.current) {
                clearTimeout(highlightTimeoutRef.current);
            }
        };
    }, [articleId, initialCommentsCount, fetchRoots]);

    const loadNextRoots = useCallback(() => {
        if (
            !hasMoreRoots ||
            loadingRoots ||
            loadingMoreRoots ||
            rootError
        ) {
            return;
        }

        void fetchRoots(rootPage + 1, true);
    }, [
        fetchRoots,
        hasMoreRoots,
        loadingMoreRoots,
        loadingRoots,
        rootError,
        rootPage,
    ]);

    const loadThread = useCallback(
        async (rootId: number, retry = false) => {
            const current = threads[rootId];

            if (loadingThreadsRef.current.has(rootId)) return;
            if (current?.loaded && !current.hasMore && !retry) return;

            const page = retry
                ? current?.failedPage ?? (current ? current.page + 1 : 1)
                : current?.loaded
                    ? current.page + 1
                    : 1;

            loadingThreadsRef.current.add(rootId);

            const generation = requestGenerationRef.current;

            setThreads((previous) => ({
                ...previous,
                [rootId]: {
                    comments: previous[rootId]?.comments ?? [],
                    page: previous[rootId]?.page ?? 0,
                    failedPage: null,
                    hasMore: previous[rootId]?.hasMore ?? true,
                    loading: true,
                    error: null,
                    loaded: previous[rootId]?.loaded ?? false,
                },
            }));

            try {
                const response = await getEditorialCommentThread(
                    articleId,
                    rootId,
                    page,
                );

                if (generation !== requestGenerationRef.current) return;

                setComments((previous) => mergeComments(previous, response.results));

                setThreads((previous) => ({
                    ...previous,
                    [rootId]: {
                        comments: mergeComments(
                            previous[rootId]?.comments ?? [],
                            response.results,
                        ),
                        page,
                        failedPage: null,
                        hasMore: Boolean(response.next),
                        loading: false,
                        error: null,
                        loaded: true,
                    },
                }));
            } catch (error) {
                if (generation !== requestGenerationRef.current) return;

                setThreads((previous) => ({
                    ...previous,
                    [rootId]: {
                        comments: previous[rootId]?.comments ?? [],
                        page: previous[rootId]?.page ?? 0,
                        failedPage: page,
                        hasMore: true,
                        loading: false,
                        error: getErrorMessage(error),
                        loaded: previous[rootId]?.loaded ?? false,
                    },
                }));
            } finally {
                loadingThreadsRef.current.delete(rootId);
            }
        },
        [articleId, threads],
    );

    const handleJumpToComment = useCallback((commentId: number) => {
        const target = document.getElementById(
            `editorial-comment-${commentId}`,
        );

        if (!target) {
            setMenuMessage(
                'That comment is not loaded yet. Load more replies and try again.',
            );
            return;
        }

        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setHighlightedCommentId(commentId);

        if (highlightTimeoutRef.current) {
            clearTimeout(highlightTimeoutRef.current);
        }

        highlightTimeoutRef.current = setTimeout(() => {
            setHighlightedCommentId(null);
        }, HIGHLIGHT_DURATION_MS);
    }, []);

    const handleRequireAuth = useCallback(() => {
        setActionError('Sign in to interact with comments.');
    }, []);

    /**
     * Select a comment to reply to and request focus in the composer.
     * Clicking Reply on the already-selected comment cancels that reply.
     */
    const handleReply = useCallback(
        (sharedComment: SharedComment) => {
            const comment = commentsById.get(sharedComment.id);

            if (!comment) return;

            if (!authenticated) {
                setActionError('Sign in to reply to comments.');
                return;
            }

            if (isUnavailableComment(comment)) return;

            setActionError(null);
            setEditingComment(null);
            setDraft('');

            if (replyTo?.id === comment.id) {
                setReplyTo(null);
                return;
            }

            setReplyTo(comment);

            // Ask CommentComposer to focus the textarea.
            setFocusRequestKey((current) => current + 1);
        },
        [authenticated, commentsById, replyTo],
    );

    /**
     * Start editing and focus the shared composer so the user can
     * immediately edit their comment.
     */
    const handleEdit = useCallback(
        (sharedComment: SharedComment) => {
            const comment = commentsById.get(sharedComment.id);

            if (!comment) return;

            if (!canEditComment(comment)) {
                setActionError(
                    'Comments can only be edited within 15 minutes of posting.',
                );
                return;
            }

            setActionError(null);
            setReplyTo(null);
            setEditingComment(comment);
            setDraft(comment.content);

            // Ask CommentComposer to focus the textarea.
            setFocusRequestKey((current) => current + 1);
        },
        [commentsById],
    );

    const handleCancelComposer = useCallback(() => {
        setReplyTo(null);
        setEditingComment(null);
        setDraft('');
        setActionError(null);
    }, []);

    const handleSubmit = useCallback(async () => {
        const content = draft.trim();

        if (!authenticated) {
            setActionError('Sign in to join the conversation.');
            return;
        }

        if (submitting) return;

        if (!content) {
            setActionError('Write a comment before submitting.');
            return;
        }

        if (content.length > COMMENT_MAX_LENGTH) {
            setActionError(
                `Comments cannot exceed ${COMMENT_MAX_LENGTH} characters.`,
            );
            return;
        }

        if (editingComment && !canEditComment(editingComment)) {
            setActionError(
                'Comments can only be edited within 15 minutes of posting.',
            );
            return;
        }

        if (replyTo && isUnavailableComment(replyTo)) {
            setActionError('You cannot reply to a comment that is unavailable.');
            return;
        }

        setSubmitting(true);
        setActionError(null);

        try {
            if (editingComment) {
                const updated = await updateEditorialComment(editingComment.id, {
                    content,
                });

                const applyUpdate = (comment: EditorialComment) => ({
                    ...comment,
                    ...updated,
                    content: updated.content,
                    is_edited: updated.is_edited,
                });

                setComments((previous) =>
                    updateCommentInList(previous, editingComment.id, applyUpdate),
                );

                setThreads((previous) => {
                    const next = { ...previous };

                    for (const [key, thread] of Object.entries(previous)) {
                        next[Number(key)] = {
                            ...thread,
                            comments: updateCommentInList(
                                thread.comments,
                                editingComment.id,
                                applyUpdate,
                            ),
                        };
                    }

                    return next;
                });
            } else {
                const parent = replyTo;

                const created = await createEditorialComment(articleId, {
                    content,
                    parent: parent?.id ?? null,
                });

                setComments((previous) => mergeComments(previous, [created]));
                setCommentsCount((count) => count + 1);

                if (parent) {
                    const rootId = getRootId(parent);

                    setComments((previous) =>
                        previous.map((comment) => {
                            if (comment.id === parent.id) {
                                return {
                                    ...comment,
                                    replies_count: comment.replies_count + 1,
                                };
                            }

                            if (comment.id === rootId) {
                                return {
                                    ...comment,
                                    thread_replies_count:
                                        comment.thread_replies_count + 1,
                                };
                            }

                            return comment;
                        }),
                    );

                    setThreads((previous) => {
                        const thread = previous[rootId];

                        if (!thread) return previous;

                        return {
                            ...previous,
                            [rootId]: {
                                ...thread,
                                comments: mergeComments(thread.comments, [created]),
                            },
                        };
                    });
                } else {
                    setHasMoreRoots(
                        (current) => current || rootComments.length >= ROOT_PAGE_SIZE,
                    );
                }
            }

            setDraft('');
            setReplyTo(null);
            setEditingComment(null);
        } catch (error) {
            setActionError(getErrorMessage(error));
        } finally {
            setSubmitting(false);
        }
    }, [
        articleId,
        authenticated,
        draft,
        editingComment,
        getRootId,
        replyTo,
        rootComments.length,
        submitting,
    ]);

    const handleToggleLike = useCallback(
        async (
            sharedComment: SharedComment,
        ): Promise<SharedCommentLikeResponse> => {
            const comment = commentsById.get(sharedComment.id);

            if (!comment || !authenticated || isUnavailableComment(comment)) {
                return {
                    liked: sharedComment.isLiked,
                    likes_count: sharedComment.likesCount,
                };
            }

            const previousLiked = comment.liked;
            const previousCount = comment.likes_count;
            const nextLiked = !previousLiked;
            const nextCount = Math.max(
                0,
                previousCount + (previousLiked ? -1 : 1),
            );

            const updateEverywhere = (
                updater: (item: EditorialComment) => EditorialComment,
            ) => {
                setComments((previous) =>
                    updateCommentInList(previous, comment.id, updater),
                );

                setThreads((previous) => {
                    const next = { ...previous };

                    for (const [key, thread] of Object.entries(previous)) {
                        next[Number(key)] = {
                            ...thread,
                            comments: updateCommentInList(
                                thread.comments,
                                comment.id,
                                updater,
                            ),
                        };
                    }

                    return next;
                });
            };

            updateEverywhere((item) => ({
                ...item,
                liked: nextLiked,
                likes_count: nextCount,
            }));

            try {
                const response: EditorialCommentLikeResponse = previousLiked
                    ? await unlikeEditorialComment(comment.id)
                    : await likeEditorialComment(comment.id);

                updateEverywhere((item) => ({
                    ...item,
                    liked: response.liked,
                    likes_count: response.likes_count,
                }));

                return {
                    liked: response.liked,
                    likes_count: response.likes_count,
                };
            } catch (error) {
                updateEverywhere((item) => ({
                    ...item,
                    liked: previousLiked,
                    likes_count: previousCount,
                }));

                setActionError(getErrorMessage(error));

                return {
                    liked: previousLiked,
                    likes_count: previousCount,
                };
            }
        },
        [authenticated, commentsById],
    );

    const handleDelete = useCallback(async () => {
        if (!commentToDelete || deleting) return;

        setDeleting(true);
        setActionError(null);

        const target = commentToDelete;
        const rootId = getRootId(target);
        const removedIds = collectSubtreeIds(comments, target.id);
        const loadedRemovedCount = removedIds.size;

        try {
            await deleteEditorialComment(target.id);

            setComments((previous) =>
                removeCommentSubtree(previous, target.id),
            );

            setThreads((previous) => {
                const next: Record<number, ThreadState> = {};

                for (const [key, thread] of Object.entries(previous)) {
                    const id = Number(key);

                    if (target.parent == null && id === target.id) continue;

                    next[id] = {
                        ...thread,
                        comments: removeCommentSubtree(thread.comments, target.id),
                    };
                }

                return next;
            });

            if (target.parent == null) {
                const totalRemoved = 1 + Math.max(0, target.thread_replies_count);

                setCommentsCount((count) => Math.max(0, count - totalRemoved));
            } else {
                const estimatedRemoved = Math.max(
                    loadedRemovedCount,
                    1 + Math.max(0, target.replies_count),
                );

                setCommentsCount((count) =>
                    Math.max(0, count - estimatedRemoved),
                );

                const updateCounts = (comment: EditorialComment) => {
                    if (comment.id === target.parent) {
                        return {
                            ...comment,
                            replies_count: Math.max(0, comment.replies_count - 1),
                        };
                    }

                    if (comment.id === rootId) {
                        return {
                            ...comment,
                            thread_replies_count: Math.max(
                                0,
                                comment.thread_replies_count - estimatedRemoved,
                            ),
                        };
                    }

                    return comment;
                };

                setComments((previous) => previous.map(updateCounts));

                setThreads((previous) => {
                    const thread = previous[rootId];

                    if (!thread) return previous;

                    return {
                        ...previous,
                        [rootId]: {
                            ...thread,
                            comments: thread.comments.map(updateCounts),
                        },
                    };
                });
            }

            if (replyTo && removedIds.has(replyTo.id)) {
                setReplyTo(null);
                setDraft('');
            }

            if (editingComment && removedIds.has(editingComment.id)) {
                setEditingComment(null);
                setDraft('');
            }

            setCommentToDelete(null);
        } catch (error) {
            setActionError(getErrorMessage(error));
        } finally {
            setDeleting(false);
        }
    }, [
        commentToDelete,
        comments,
        deleting,
        editingComment,
        getRootId,
        replyTo,
    ]);

    const loginHref = `/login?next=${encodeURIComponent(
        pathname || '/',
    )}`;

    return (
        <section
            id="editorial-comments"
            className="mt-10 scroll-mt-24"
            aria-labelledby="editorial-comments-heading"
        >
            <div className="mb-5 flex items-center gap-3">
                <MessageCircle size={23} className="text-teal-600" />

                <h2 id="editorial-comments-heading" className="text-xl font-bold">
                    Comments
                </h2>

                <span className="rounded-full bg-base-200 px-2.5 py-1 text-xs font-semibold text-base-content/70">
                    {commentsCount.toLocaleString()}
                </span>
            </div>

            {menuMessage && (
                <div className="mb-4 flex items-start justify-between gap-3 rounded-xl bg-base-200 p-3 text-sm">
                    <p>{menuMessage}</p>

                    <button
                        type="button"
                        onClick={() => setMenuMessage(null)}
                        aria-label="Dismiss message"
                        className="shrink-0 rounded-full p-1 hover:bg-base-300"
                    >
                        <X size={16} />
                    </button>
                </div>
            )}

            {actionError && (
                <div
                    role="alert"
                    className="mb-4 flex items-start justify-between gap-3 rounded-xl bg-error/5 px-3 py-2 text-sm text-error"
                >
                    <p className="min-w-0">{actionError}</p>

                    <button
                        type="button"
                        onClick={() => setActionError(null)}
                        aria-label="Dismiss error"
                        className="shrink-0 rounded-full p-0.5 hover:bg-error/10"
                    >
                        <X size={15} />
                    </button>
                </div>
            )}

            {loadingRoots && comments.length === 0 ? (
                <div
                    className="space-y-4 pb-64"
                    aria-label="Loading comments"
                >
                    {Array.from({ length: 3 }).map((_, index) => (
                        <div key={index} className="flex gap-3 py-3">
                            <div className="h-9 w-9 shrink-0 animate-pulse rounded-full bg-base-200" />

                            <div className="flex-1 space-y-2">
                                <div className="h-3 w-36 animate-pulse rounded bg-base-200" />
                                <div className="h-3 w-full animate-pulse rounded bg-base-200" />
                                <div className="h-3 w-3/4 animate-pulse rounded bg-base-200" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : rootError && comments.length === 0 ? (
                <div className="mb-64 rounded-xl bg-base-200/60 p-5 text-center">
                    <p role="alert" className="text-sm text-error">
                        {rootError}
                    </p>

                    <button
                        type="button"
                        onClick={() => void fetchRoots(1, false)}
                        className="mt-3 rounded-full bg-base-200 px-4 py-2 text-sm font-semibold hover:bg-base-300"
                    >
                        Try again
                    </button>
                </div>
            ) : rootComments.length === 0 ? (
                <div className="rounded-2xl bg-light-surface-soft px-5 py-10 text-center dark:bg-dark-surface-soft sm:px-8 sm:py-12">
                    <MessageCircle
                        size={30}
                        className="mx-auto text-base-content/35"
                    />

                    <p className="mt-3 font-semibold">No comments yet</p>

                    <p className="mt-1 text-sm text-base-content/55">
                        Be the first to share your thoughts on this article.
                    </p>
                </div>
            ) : (
                <div className="pb-64">
                    <CommentThread
                        comments={sharedRootComments}
                        repliesByComment={repliesByComment}
                        threadStates={threadStates}
                        currentUserId={currentUserId}
                        isAuthenticated={authenticated}
                        onReply={handleReply}
                        onEdit={handleEdit}
                        onDelete={(comment) => {
                            const editorialComment = commentsById.get(comment.id);

                            if (editorialComment) {
                                setCommentToDelete(editorialComment);
                            }
                        }}
                        onReport={(comment) => {
                            const editorialComment = commentsById.get(comment.id);

                            if (editorialComment) {
                                setCommentToReport(editorialComment);
                            }
                        }}
                        onLike={handleToggleLike}
                        onRequireAuth={handleRequireAuth}
                        onNavigateToComment={handleJumpToComment}
                        onLoadReplies={(rootId) => void loadThread(rootId)}
                        highlightedCommentId={highlightedCommentId}
                        commentIdPrefix="editorial-comment"
                        emptyMessage="No comments yet. Be the first to share your thoughts."
                    />
                </div>
            )}

            {loadingMoreRoots && (
                <div className="flex justify-center py-5">
                    <LoaderCircle size={22} className="animate-spin text-teal-600" />
                </div>
            )}

            {rootError && comments.length > 0 && (
                <div className="py-4 text-center">
                    <p role="alert" className="text-sm text-error">
                        {rootError}
                    </p>

                    <button
                        type="button"
                        onClick={() => void fetchRoots(rootPage + 1, true)}
                        className="mt-2 text-sm font-semibold text-teal-600 hover:underline"
                    >
                        Retry loading comments
                    </button>
                </div>
            )}

            {!rootError && hasMoreRoots && rootComments.length > 0 && (
                <div className="py-5 text-center">
                    <button
                        type="button"
                        onClick={loadNextRoots}
                        disabled={loadingMoreRoots || loadingRoots}
                        className="inline-flex min-h-9 items-center justify-center gap-2 rounded-full border border-base-300 px-4 py-2 text-sm font-semibold transition-colors hover:bg-base-200 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {loadingMoreRoots ? (
                            <LoaderCircle size={16} className="animate-spin" />
                        ) : null}

                        {loadingMoreRoots ? 'Loading comments…' : 'Load more comments'}
                    </button>
                </div>
            )}

            {!hasMoreRoots && !rootError && rootComments.length > 0 && (
                <p className="py-5 text-center text-xs text-base-content/45">
                    You've reached the end of the comments.
                </p>
            )}

            {isAuthLoading ? (
                <div className="fixed inset-x-0 bottom-0 z-40 border-t border-base-300 bg-base-100/95 p-4 shadow-lg backdrop-blur-md">
                    <div className="mx-auto flex min-h-12 w-full max-w-4xl items-center gap-3">
                        <LoaderCircle
                            size={18}
                            className="animate-spin text-teal-600"
                        />
                        <span className="text-sm text-base-content/60">
                            Preparing your comment box…
                        </span>
                    </div>
                </div>
            ) : (
                <CommentComposer
                    value={draft}
                    onChange={(value) => {
                        setDraft(value);

                        if (actionError) {
                            setActionError(null);
                        }
                    }}
                    onSubmit={handleSubmit}
                    isAuthenticated={authenticated}
                    isSubmitting={submitting}
                    replyingTo={replyTo ? toSharedComment(replyTo) : null}
                    editingComment={
                        editingComment ? toSharedComment(editingComment) : null
                    }
                    focusRequestKey={focusRequestKey}
                    onCancelContext={handleCancelComposer}
                    maxLength={COMMENT_MAX_LENGTH}
                    placeholder="Write a comment…"
                    loginHref={loginHref}
                />
            )}

            <ConfirmationModal
                open={Boolean(commentToDelete)}
                title="Delete comment?"
                description="This comment and its replies will be removed. This action cannot be undone."
                confirmLabel="Delete comment"
                destructive
                isLoading={deleting}
                onConfirm={handleDelete}
                onCancel={() => {
                    if (!deleting) setCommentToDelete(null);
                }}
            />

            <ReportContentModal
                isOpen={Boolean(commentToReport)}
                onClose={() => setCommentToReport(null)}
                endpoint={
                    commentToReport
                        ? `/api/v1/music/editorial/comments/${commentToReport.id}/report/`
                        : ''
                }
                contentLabel={
                    commentToReport?.parent != null ? 'reply' : 'comment'
                }
            />
        </section>
    );
}