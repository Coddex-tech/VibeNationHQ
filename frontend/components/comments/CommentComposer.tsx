'use client';

import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
} from 'react';
import Link from 'next/link';
import { LoaderCircle, Send, X } from 'lucide-react';

import type { SharedComment } from './CommentItem';

type CommentComposerProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void | Promise<void>;

  isAuthenticated: boolean;
  isSubmitting?: boolean;

  replyingTo?: SharedComment | null;
  editingComment?: SharedComment | null;

  /**
   * Increment this value whenever the parent wants to focus the composer.
   * For example, increment it when the user clicks Reply on a comment.
   */
  focusRequestKey?: number;

  onCancelContext?: () => void;

  maxLength?: number;
  placeholder?: string;
  loginHref?: string;
  className?: string;
};

const MAX_VISIBLE_LINES = 3;
const INITIAL_TEXTAREA_HEIGHT = 44;

export default function CommentComposer({
  value,
  onChange,
  onSubmit,
  isAuthenticated,
  isSubmitting = false,
  replyingTo = null,
  editingComment = null,
  focusRequestKey = 0,
  onCancelContext,
  maxLength = 10_000,
  placeholder = 'Write a comment...',
  loginHref = '/login',
  className = '',
}: CommentComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isComposingRef = useRef(false);

  const [viewportBottomOffset, setViewportBottomOffset] = useState(0);

  const contextComment = editingComment ?? replyingTo;
  const isEditing = Boolean(editingComment);

  const contextUsername = contextComment
    ? contextComment.user.username.trim().replace(/^@/, '')
    : '';

  const isOverLimit = value.length > maxLength;

  /**
   * Automatically focus the textarea when the parent requests it.
   * The cursor is placed at the end of any existing text.
   */
  useEffect(() => {
    if (focusRequestKey <= 0 || !isAuthenticated || isSubmitting) {
      return;
    }

    const textarea = textareaRef.current;

    if (!textarea || textarea.disabled) {
      return;
    }

    textarea.focus({ preventScroll: true });

    const cursorPosition = textarea.value.length;

    textarea.setSelectionRange(cursorPosition, cursorPosition);
  }, [focusRequestKey, isAuthenticated, isSubmitting]);

  /**
   * Automatically resize the textarea while respecting the
   * maximum number of visible lines.
   */
  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = 'auto';

    const computedStyle = window.getComputedStyle(textarea);
    const lineHeight = Number.parseFloat(computedStyle.lineHeight) || 24;
    const verticalPadding =
      (Number.parseFloat(computedStyle.paddingTop) || 0) +
      (Number.parseFloat(computedStyle.paddingBottom) || 0);

    const maxHeight =
      lineHeight * MAX_VISIBLE_LINES + verticalPadding;

    const nextHeight = Math.min(
      Math.max(textarea.scrollHeight, INITIAL_TEXTAREA_HEIGHT),
      maxHeight,
    );

    textarea.style.height = `${nextHeight}px`;
    textarea.style.overflowY =
      textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
  }, [value]);

  /**
   * Keep the composer above the on-screen keyboard on mobile browsers.
   * The parent component remains responsible for submitting comments.
   */
  useEffect(() => {
    const updateViewportOffset = () => {
      const viewport = window.visualViewport;

      if (!viewport) {
        setViewportBottomOffset(0);
        return;
      }

      const offset = Math.max(
        0,
        window.innerHeight - viewport.height - viewport.offsetTop,
      );

      setViewportBottomOffset(offset);
    };

    updateViewportOffset();

    const viewport = window.visualViewport;

    viewport?.addEventListener('resize', updateViewportOffset);
    viewport?.addEventListener('scroll', updateViewportOffset);
    window.addEventListener('resize', updateViewportOffset);

    return () => {
      viewport?.removeEventListener('resize', updateViewportOffset);
      viewport?.removeEventListener('scroll', updateViewportOffset);
      window.removeEventListener('resize', updateViewportOffset);
    };
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (
      !isAuthenticated ||
      isSubmitting ||
      isOverLimit ||
      !value.trim()
    ) {
      return;
    }

    void onSubmit();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (
      event.key !== 'Enter' ||
      event.shiftKey ||
      event.nativeEvent.isComposing ||
      isComposingRef.current
    ) {
      return;
    }

    event.preventDefault();

    if (
      !isAuthenticated ||
      isSubmitting ||
      isOverLimit ||
      !value.trim()
    ) {
      return;
    }

    void onSubmit();
  }

  return (
    <div
      className={['fixed inset-x-0 z-40', className]
        .filter(Boolean)
        .join(' ')}
      style={{
        bottom: `${viewportBottomOffset}px`,
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      <div className="mx-auto w-full max-w-4xl px-3 py-2 sm:px-5 sm:py-2">
        {contextComment && (
          <div className="mb-2 flex min-w-0 items-center gap-2 rounded-xl bg-light-surface-soft px-3 py-2 dark:bg-dark-surface-soft">
            <div className="min-w-0 flex-1 text-xs text-light-text-muted dark:text-dark-text-muted">
              {isEditing ? (
                <p>Editing your comment</p>
              ) : (
                <p className="truncate">
                  Replying to{' '}
                  <span className="font-semibold text-brand-teal">
                    @{contextUsername}
                  </span>
                </p>
              )}
            </div>

            {onCancelContext && (
              <button
                type="button"
                onClick={onCancelContext}
                aria-label={
                  isEditing ? 'Cancel editing' : 'Cancel reply'
                }
                className="shrink-0 rounded-full p-1.5 text-light-text-muted transition-colors hover:bg-light-border/60 hover:text-light-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:text-dark-text-muted dark:hover:bg-dark-border/60 dark:hover:text-dark-text"
              >
                <X size={15} />
              </button>
            )}
          </div>
        )}

        {!isAuthenticated ? (
          <div className="flex flex-col gap-3 rounded-xl bg-light-surface-soft px-4 py-3 dark:bg-dark-surface-soft sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-light-text-muted dark:text-dark-text-muted">
              Sign in to join the conversation.
            </p>

            <Link
              href={loginHref}
              className="inline-flex min-h-9 shrink-0 items-center justify-center rounded-full bg-brand-teal px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 dark:focus-visible:ring-offset-dark-surface"
            >
              Sign in to comment
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="min-w-0">
            <div className="flex min-w-0 items-end gap-2">
              <div className="min-w-0 flex-1 overflow-hidden rounded-2xl border border-light-border bg-light-bg transition-colors focus-within:border-brand-teal dark:border-dark-border dark:bg-dark-bg">
                <textarea
                  ref={textareaRef}
                  value={value}
                  onChange={(event) => onChange(event.target.value)}
                  onKeyDown={handleKeyDown}
                  onCompositionStart={() => {
                    isComposingRef.current = true;
                  }}
                  onCompositionEnd={() => {
                    isComposingRef.current = false;
                  }}
                  disabled={isSubmitting}
                  maxLength={maxLength}
                  rows={1}
                  placeholder={
                    isEditing
                      ? 'Edit your comment...'
                      : replyingTo
                        ? `Reply to @${contextUsername}...`
                        : placeholder
                  }
                  aria-label={
                    isEditing
                      ? 'Edit comment'
                      : replyingTo
                        ? `Reply to ${contextUsername}`
                        : 'Write a comment'
                  }
                  aria-invalid={isOverLimit}
                  className="block max-h-32 min-h-11 w-full resize-none bg-transparent px-3.5 py-3 text-sm leading-6 text-light-text outline-none placeholder:text-light-text-muted disabled:cursor-not-allowed disabled:opacity-60 dark:text-dark-text dark:placeholder:text-dark-text-muted"
                />
              </div>

              <button
                type="submit"
                disabled={
                  isSubmitting ||
                  !value.trim() ||
                  isOverLimit
                }
                aria-label={
                  isEditing ? 'Save edited comment' : 'Send comment'
                }
                title={
                  isEditing ? 'Save comment' : 'Send comment'
                }
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-teal text-white transition-colors hover:bg-brand-teal/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:focus-visible:ring-offset-dark-surface"
              >
                {isSubmitting ? (
                  <LoaderCircle size={19} className="animate-spin" />
                ) : (
                  <Send size={18} />
                )}
              </button>
            </div>

            {isOverLimit && (
              <p
                role="alert"
                className="mt-1 text-xs text-red-600 dark:text-red-300"
              >
                Your comment exceeds the{' '}
                {maxLength.toLocaleString()} character limit.
              </p>
            )}
          </form>
        )}
      </div>
    </div>
  );
}