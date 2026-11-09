'use client';

import { useMemo } from 'react';
import {
  ChevronDown,
  LoaderCircle,
  MessageCircle,
  RotateCw,
} from 'lucide-react';

import CommentItem, {
  type SharedComment,
  type SharedCommentLikeResponse,
} from './CommentItem';

export type CommentThreadState = {
  loadedCount: number;
  count: number;
  hasMore: boolean;
  isLoading: boolean;
  error?: string | null;
};

type CommentThreadProps = {
  comments: SharedComment[];
  repliesByComment: Record<string, SharedComment[]>;
  threadStates?: Record<string, CommentThreadState>;
  currentUserId: string | number | null;
  isAuthenticated: boolean;

  onReply: (comment: SharedComment) => void;
  onEdit: (comment: SharedComment) => void;
  onDelete: (comment: SharedComment) => void;
  onReport: (comment: SharedComment) => void;

  onLike: (
    comment: SharedComment,
  ) => Promise<SharedCommentLikeResponse>;

  onRequireAuth: () => void;
  onNavigateToComment?: (commentId: number) => void;
  onLoadReplies?: (rootCommentId: number) => void;
  highlightedCommentId?: number | null;
  isCreatorComment?: (comment: SharedComment) => boolean;
  commentIdPrefix?: string;
  emptyMessage?: string;
};

function getTimestamp(comment: SharedComment): number {
  const timestamp = new Date(comment.createdAt).getTime();

  return Number.isFinite(timestamp) ? timestamp : 0;
}

/**
 * Collect all loaded descendants of a root comment.
 *
 * Replies retain their actual parent IDs for display and reply references.
 * The flattened thread is ordered oldest first.
 */
function getThreadReplies(
  rootComment: SharedComment,
  repliesByComment: Record<string, SharedComment[]>,
): SharedComment[] {
  const visited = new Set<string>([String(rootComment.id)]);
  const descendants: SharedComment[] = [];

  function collect(parentId: number) {
    const children = repliesByComment[String(parentId)] ?? [];

    for (const child of children) {
      const childId = String(child.id);

      if (visited.has(childId)) {
        continue;
      }

      visited.add(childId);
      descendants.push(child);

      collect(child.id);
    }
  }

  collect(rootComment.id);

  descendants.sort((first, second) => {
    const timestampDifference =
      getTimestamp(first) - getTimestamp(second);

    if (timestampDifference !== 0) {
      return timestampDifference;
    }

    return first.id - second.id;
  });

  return descendants;
}

export default function CommentThread({
  comments,
  repliesByComment,
  threadStates = {},
  currentUserId,
  isAuthenticated,
  onReply,
  onEdit,
  onDelete,
  onReport,
  onLike,
  onRequireAuth,
  onNavigateToComment,
  onLoadReplies,
  highlightedCommentId = null,
  isCreatorComment,
  commentIdPrefix = 'comment',
  emptyMessage = 'No comments yet. Be the first to comment.',
}: CommentThreadProps) {
  const parentLookup = useMemo(() => {
    const lookup = new Map<number, SharedComment>();

    for (const root of comments) {
      lookup.set(root.id, root);
    }

    for (const replies of Object.values(repliesByComment)) {
      for (const reply of replies) {
        lookup.set(reply.id, reply);
      }
    }

    return lookup;
  }, [comments, repliesByComment]);

  if (comments.length === 0) {
    return (
      <div
        className="
          rounded-2xl
          bg-light-surface-soft
          px-4 py-8 text-center
          dark:bg-dark-surface-soft
          sm:py-10
        "
      >
        <MessageCircle
          size={26}
          aria-hidden="true"
          className="
            mx-auto mb-3
            text-light-text-muted
            dark:text-dark-text-muted
          "
        />

        <p
          className="
            text-sm
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {emptyMessage}
        </p>
      </div>
    );
  }

  return (
    <div className="min-w-0 space-y-5">
      {comments.map((rootComment) => {
        const rootId = String(rootComment.id);
        const state = threadStates[rootId];

        const threadReplies = getThreadReplies(
          rootComment,
          repliesByComment,
        );

        const hasLoadedReplies = threadReplies.length > 0;

        const knownReplyCount = Math.max(
          rootComment.repliesCount,
          state?.count ?? 0,
          threadReplies.length,
        );

        const hasUnloadedReplies =
          state?.hasMore ??
          (knownReplyCount > threadReplies.length);

        const isLoading = state?.isLoading ?? false;
        const error = state?.error ?? null;

        const shouldShowReplyControl =
          rootComment.repliesCount > 0 ||
          knownReplyCount > 0 ||
          hasLoadedReplies;

        return (
          <section
            key={rootComment.id}
            aria-label={`Comment thread by ${rootComment.user.username}`}
            className="min-w-0"
          >
            <CommentItem
              comment={rootComment}
              currentUserId={currentUserId}
              isAuthenticated={isAuthenticated}
              showCreatorBadge={
                isCreatorComment?.(rootComment) ?? false
              }
              onReply={onReply}
              onEdit={onEdit}
              onDelete={onDelete}
              onReport={onReport}
              onLike={onLike}
              onRequireAuth={onRequireAuth}
              onNavigateToComment={onNavigateToComment}
              isHighlighted={
                highlightedCommentId === rootComment.id
              }
              commentIdPrefix={commentIdPrefix}
            />

            {shouldShowReplyControl && (
              <div className="ml-10 mt-1 min-w-0 sm:ml-12">
                {threadReplies.length > 0 && (
                  <div className="min-w-0 space-y-3 pl-3 sm:pl-4">
                    {threadReplies.map((reply) => {
                      const actualParent =
                        reply.parent === null
                          ? null
                          : parentLookup.get(reply.parent) ?? null;

                      return (
                        <CommentItem
                          key={reply.id}
                          comment={reply}
                          replyTo={actualParent}
                          currentUserId={currentUserId}
                          isAuthenticated={isAuthenticated}
                          showCreatorBadge={
                            isCreatorComment?.(reply) ?? false
                          }
                          onReply={onReply}
                          onEdit={onEdit}
                          onDelete={onDelete}
                          onReport={onReport}
                          onLike={onLike}
                          onRequireAuth={onRequireAuth}
                          onNavigateToComment={onNavigateToComment}
                          isHighlighted={
                            highlightedCommentId === reply.id
                          }
                          commentIdPrefix={commentIdPrefix}
                        />
                      );
                    })}
                  </div>
                )}

                {error && (
                  <div
                    role="alert"
                    className="
                      mt-2 flex flex-wrap items-center gap-2
                      text-xs text-red-600
                      dark:text-red-300
                    "
                  >
                    <span>{error}</span>

                    {onLoadReplies && (
                      <button
                        type="button"
                        onClick={() => onLoadReplies(rootComment.id)}
                        disabled={isLoading}
                        className="
                          inline-flex items-center gap-1
                          font-semibold underline underline-offset-2
                          disabled:opacity-50
                        "
                      >
                        <RotateCw size={12} aria-hidden="true" />
                        Try again
                      </button>
                    )}
                  </div>
                )}

                {onLoadReplies &&
                  (hasUnloadedReplies ||
                    (!hasLoadedReplies && !isLoading && !error)) && (
                    <button
                      type="button"
                      onClick={() => onLoadReplies(rootComment.id)}
                      disabled={isLoading}
                      className="
                        mt-2 inline-flex min-h-8
                        items-center gap-1.5
                        rounded-full px-2 py-1
                        text-xs font-semibold
                        text-brand-teal
                        transition-colors duration-200
                        hover:bg-brand-teal/10
                        focus-visible:outline-none
                        focus-visible:ring-2
                        focus-visible:ring-brand-teal
                        disabled:cursor-not-allowed
                        disabled:opacity-60
                      "
                    >
                      {isLoading ? (
                        <>
                          <LoaderCircle
                            size={14}
                            className="animate-spin"
                            aria-hidden="true"
                          />
                          Loading replies…
                        </>
                      ) : hasLoadedReplies ? (
                        <>
                          <ChevronDown
                            size={14}
                            aria-hidden="true"
                          />
                          Load more replies
                        </>
                      ) : (
                        <>
                          <ChevronDown
                            size={14}
                            aria-hidden="true"
                          />
                          Load replies
                          {knownReplyCount > 0
                            ? ` (${knownReplyCount})`
                            : ''}
                        </>
                      )}
                    </button>
                  )}

                {isLoading && hasLoadedReplies && (
                  <p
                    className="
                      mt-1 text-xs
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Loading more replies…
                  </p>
                )}

                {state &&
                  !hasUnloadedReplies &&
                  hasLoadedReplies &&
                  !isLoading && (
                    <p
                      className="
                        mt-2 text-xs
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      All replies loaded
                    </p>
                  )}
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}