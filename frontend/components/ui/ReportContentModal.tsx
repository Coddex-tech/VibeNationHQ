'use client';

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type FormEvent,
} from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  CheckCircle2,
  Info,
  LogIn,
  ShieldAlert,
  X,
} from 'lucide-react';

import {
  apiRequest,
  ApiError,
} from '@/lib/api';

export type ReportReason =
  | 'spam'
  | 'harassment'
  | 'hate'
  | 'sexual'
  | 'misinformation'
  | 'copyright'
  | 'other';

type ReportContentModalProps = {
  isOpen: boolean;
  onClose: () => void;
  endpoint: string;
  contentLabel: 'post' | 'comment' | 'reply';
};

type ReportFeedback = {
  type: 'success' | 'error';
  message: string;
};

const REPORT_REASONS: {
  value: ReportReason;
  label: string;
}[] = [
  { value: 'spam', label: 'Spam' },
  { value: 'harassment', label: 'Harassment or bullying' },
  { value: 'hate', label: 'Hate speech' },
  { value: 'sexual', label: 'Sexual content' },
  { value: 'misinformation', label: 'Misinformation' },
  { value: 'copyright', label: 'Copyright infringement' },
  { value: 'other', label: 'Something else' },
];

export default function ReportContentModal({
  isOpen,
  onClose,
  endpoint,
  contentLabel,
}: ReportContentModalProps) {
  const [reason, setReason] = useState<ReportReason | ''>('');
  const [details, setDetails] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<ReportFeedback | null>(null);
  const [requiresLogin, setRequiresLogin] = useState(false);

  const dialogRef = useRef<HTMLDivElement>(null);
  const reasonSelectRef = useRef<HTMLSelectElement>(null);
  const loginButtonRef = useRef<HTMLAnchorElement>(null);
  const isSubmittingRef = useRef(false);

  const id = useId();
  const titleId = `${id}-report-title`;
  const descriptionId = `${id}-report-description`;
  const reasonId = `${id}-report-reason`;
  const detailsId = `${id}-report-details`;

  const handleClose = useCallback(() => {
    if (isSubmittingRef.current) {
      return;
    }

    onClose();
  }, [onClose]);

  // Reset the form whenever a new report dialog is opened.
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setReason('');
    setDetails('');
    setFeedback(null);
    setRequiresLogin(false);
  }, [isOpen, endpoint, contentLabel]);

  // Manage focus and keyboard interaction while the dialog is open.
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const previousFocus =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;

    const dialog = dialogRef.current;

    reasonSelectRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        if (!isSubmittingRef.current) {
          event.preventDefault();
          handleClose();
        }

        return;
      }

      if (event.key !== 'Tab' || !dialog) {
        return;
      }

      const focusableElements =
        dialog.querySelectorAll<HTMLElement>(
          [
            'button:not(:disabled)',
            'a[href]:not([aria-disabled="true"])',
            'select:not(:disabled)',
            'textarea:not(:disabled)',
            'input:not(:disabled)',
            '[tabindex]:not([tabindex="-1"])',
          ].join(','),
        );

      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const first = focusableElements[0];
      const last = focusableElements[focusableElements.length - 1];

      if (
        event.shiftKey &&
        document.activeElement === first
      ) {
        event.preventDefault();
        last.focus();
      } else if (
        !event.shiftKey &&
        document.activeElement === last
      ) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      previousFocus?.focus();
    };
  }, [isOpen, handleClose]);

  // Move focus to the login action when the authentication prompt appears.
  useEffect(() => {
    if (isOpen && requiresLogin) {
      loginButtonRef.current?.focus();
    }
  }, [isOpen, requiresLogin]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!reason || isSubmittingRef.current) {
      return;
    }

    isSubmittingRef.current = true;
    setIsSubmitting(true);
    setFeedback(null);
    setRequiresLogin(false);

    try {
      await apiRequest<unknown>(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          reason,
          details: details.trim(),
        }),
      });

      setFeedback({
        type: 'success',
        message:
          'Thank you. Your report has been submitted for review.',
      });
    } catch (error: unknown) {
      const needsLogin =
        error instanceof ApiError &&
        error.status === 401;

      setRequiresLogin(needsLogin);

      setFeedback({
        type: 'error',
        message: needsLogin
          ? `You need to log in before reporting this ${contentLabel}.`
          : getReportErrorMessage(error, contentLabel),
      });
    } finally {
      isSubmittingRef.current = false;
      setIsSubmitting(false);
    }
  }

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="
        fixed inset-0 z-[100]
        flex items-end justify-center
        overflow-y-auto overscroll-contain
        bg-black/55 p-0
        backdrop-blur-[3px]
        sm:items-center sm:p-4
      "
      onMouseDown={(event) => {
        if (
          event.target === event.currentTarget &&
          !isSubmitting
        ) {
          handleClose();
        }
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        className="
          my-auto
          max-h-[92dvh] w-full
          overflow-y-auto overscroll-contain
          rounded-t-2xl
          border border-light-border
          bg-light-surface
          shadow-2xl shadow-black/20
          sm:max-w-lg sm:rounded-2xl
          dark:border-dark-border
          dark:bg-dark-surface
          dark:shadow-black/50
      "
      >
        {/* Header */}
        <div
          className="
            sticky top-0 z-10
            flex items-start justify-between gap-3
            border-b border-light-border
            bg-light-surface/95
            px-4 py-4 backdrop-blur
            sm:px-6 sm:py-5
            dark:border-dark-border
            dark:bg-dark-surface/95
          "
        >
          <div className="flex min-w-0 items-start gap-3">
            <div
              className="
                flex h-10 w-10 shrink-0 items-center justify-center
                rounded-xl bg-brand-teal/10 text-brand-teal
              "
              aria-hidden="true"
            >
              <ShieldAlert className="h-5 w-5" />
            </div>

            <div className="min-w-0 pt-0.5">
              <h2
                id={titleId}
                className="
                  text-lg font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                Report {contentLabel}
              </h2>

              <p
                id={descriptionId}
                className="
                  mt-1 text-sm leading-5
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                Help us keep VibeNationHQ safe and respectful.
              </p>
            </div>
          </div>

          <button
            type="button"
            aria-label={`Close report ${contentLabel} dialog`}
            onClick={handleClose}
            disabled={isSubmitting}
            className="
              flex h-10 w-10 shrink-0 items-center justify-center
              rounded-full text-light-text-muted
              transition-colors hover:bg-light-surface-soft
              focus-visible:outline-none
              focus-visible:ring-2 focus-visible:ring-brand-teal
              disabled:cursor-not-allowed disabled:opacity-50
              dark:text-dark-text-muted
              dark:hover:bg-dark-surface-soft
            "
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-4 py-5 sm:px-6 sm:py-6">
          {/* Successful report */}
          {feedback?.type === 'success' ? (
            <div>
              <div
                role="status"
                className="
                  flex items-start gap-3 rounded-xl
                  border border-brand-teal/25
                  bg-brand-teal/10 p-4
                "
              >
                <CheckCircle2
                  className="mt-0.5 h-5 w-5 shrink-0 text-brand-teal"
                  aria-hidden="true"
                />

                <p
                  className="
                    text-sm leading-6
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  {feedback.message}
                </p>
              </div>

              <button
                type="button"
                onClick={handleClose}
                className="
                  mt-5 min-h-11 w-full rounded-xl
                  bg-brand-teal px-4 py-3
                  text-sm font-semibold text-white
                  transition-colors hover:bg-brand-teal-dark
                  focus-visible:outline-none
                  focus-visible:ring-2 focus-visible:ring-brand-teal
                  focus-visible:ring-offset-2
                "
              >
                Done
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Report reason */}
              <div>
                <label
                  htmlFor={reasonId}
                  className="
                    mb-2 block text-sm font-semibold
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  Why are you reporting this {contentLabel}?
                </label>

                <div className="relative">
                    <select
                    ref={reasonSelectRef}
                    id={reasonId}
                    name="reason"
                    value={reason}
                    onChange={(event) => {
                        setReason(
                        event.target.value as ReportReason | '',
                        );
                        setFeedback(null);
                        setRequiresLogin(false);
                    }}
                    required
                    disabled={isSubmitting}
                    className="
                        min-h-11 w-full min-w-0 appearance-none
                        rounded-xl border border-light-border
                        bg-light-surface
                        px-3.5 py-2.5 pr-10
                        text-sm font-medium text-light-text
                        outline-none transition-all duration-200
                        hover:border-brand-teal/50
                        focus:border-brand-teal
                        focus:ring-2 focus:ring-brand-teal/20
                        disabled:cursor-not-allowed disabled:opacity-60
                        dark:border-dark-border
                        dark:bg-dark-surface
                        dark:text-dark-text
                    "
                    >
                    <option
                        value=""
                        disabled
                        className="text-sm text-gray-400"
                    >
                        Select a reason
                    </option>

                    {REPORT_REASONS.map((item) => (
                        <option
                        key={item.value}
                        value={item.value}
                        className="
                            bg-white py-2 text-sm text-gray-800
                            dark:bg-gray-900 dark:text-gray-100
                        "
                        >
                        {item.label}
                        </option>
                    ))}
                    </select>

                  <span
                    className="
                      pointer-events-none absolute inset-y-0 right-3
                      flex items-center text-light-text-muted
                      dark:text-dark-text-muted
                    "
                    aria-hidden="true"
                  >
                    <svg
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      className="h-4 w-4"
                    >
                      <path
                        fillRule="evenodd"
                        d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.168l3.71-3.938a.75.75 0 1 1 1.09 1.03l-4.25 4.5a.75.75 0 0 1-1.09 0l-4.25-4.5a.75.75 0 0 1 .02-1.05Z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                </div>

                <p
                  className="
                    mt-1.5 text-xs leading-5
                    text-light-text-soft
                    dark:text-dark-text-soft
                  "
                >
                  Choose the reason that best describes the issue.
                </p>
              </div>

              {/* Additional details */}
              <div>
                <label
                  htmlFor={detailsId}
                  className="
                    mb-2 flex flex-wrap items-center gap-2
                    text-sm font-semibold
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  Additional details

                  <span
                    className="
                      rounded-md bg-light-surface-soft
                      px-2 py-0.5 text-xs font-normal
                      text-light-text-muted
                      dark:bg-dark-surface-soft
                      dark:text-dark-text-muted
                    "
                  >
                    Optional
                  </span>
                </label>

                <textarea
                  id={detailsId}
                  name="details"
                  value={details}
                  onChange={(event) => {
                    setDetails(event.target.value.slice(0, 2000));
                    setFeedback(null);
                    setRequiresLogin(false);
                  }}
                  maxLength={2000}
                  rows={4}
                  disabled={isSubmitting}
                  placeholder="Give us more context if needed..."
                  className="
                    min-h-28 w-full resize-y rounded-xl
                    border border-light-border
                    bg-light-surface px-3.5 py-3
                    text-base leading-6 text-light-text
                    outline-none placeholder:text-light-text-soft
                    focus:border-brand-teal
                    focus:ring-2 focus:ring-brand-teal/20
                    disabled:opacity-60 sm:text-sm
                    dark:border-dark-border
                    dark:bg-dark-surface
                    dark:text-dark-text
                    dark:placeholder:text-dark-text-soft
                  "
                />

                <div
                  className="
                    mt-1.5 flex items-center justify-between gap-3
                    text-xs text-light-text-soft
                    dark:text-dark-text-soft
                  "
                >
                  <span>Do not include sensitive personal information.</span>
                  <span className="shrink-0 tabular-nums">
                    {details.length}/2000
                  </span>
                </div>
              </div>

              {/* Authentication prompt or other errors */}
              {feedback?.type === 'error' && (
                <div
                  role="alert"
                  className="
                    rounded-xl border border-red-500/25
                    bg-red-500/5 p-3.5 sm:p-4
                  "
                >
                  <div className="flex items-start gap-2.5">
                    {requiresLogin ? (
                      <Info
                        className="mt-0.5 h-5 w-5 shrink-0 text-brand-teal"
                        aria-hidden="true"
                      />
                    ) : (
                      <AlertCircle
                        className="mt-0.5 h-5 w-5 shrink-0 text-red-600 dark:text-red-300"
                        aria-hidden="true"
                      />
                    )}

                    <p
                      className="
                        min-w-0 text-sm leading-6
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      {feedback.message}
                    </p>
                  </div>

                  {requiresLogin && (
                    <div
                      className="
                        mt-3 border-t border-light-border
                        pt-3 dark:border-dark-border
                      "
                    >
                      <Link
                        ref={loginButtonRef}
                        href={`/login?next=${encodeURIComponent(
                          typeof window !== 'undefined'
                            ? window.location.pathname +
                                window.location.search +
                                window.location.hash
                            : '/',
                        )}`}
                        className="
                          inline-flex min-h-11 w-full
                          items-center justify-center gap-2
                          rounded-xl bg-brand-teal
                          px-4 py-3 text-sm font-semibold text-white
                          transition-colors hover:bg-brand-teal-dark
                          focus-visible:outline-none
                          focus-visible:ring-2
                          focus-visible:ring-brand-teal
                          focus-visible:ring-offset-2
                          sm:w-auto sm:min-w-40
                        "
                      >
                        <LogIn className="h-4 w-4" />
                        Log in to continue
                      </Link>

                      <p
                        className="
                          mt-2 text-xs leading-5
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        After logging in, return here to submit your report.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div
                className="
                  flex flex-col-reverse gap-2.5
                  border-t border-light-border pt-4
                  sm:flex-row sm:justify-end sm:gap-3
                  dark:border-dark-border
                "
              >
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={isSubmitting}
                  className="
                    min-h-11 w-full rounded-xl
                    px-4 py-3 text-sm font-semibold
                    text-light-text-muted transition-colors
                    hover:bg-light-surface-soft
                    focus-visible:outline-none
                    focus-visible:ring-2 focus-visible:ring-brand-teal
                    disabled:cursor-not-allowed disabled:opacity-50
                    sm:w-auto
                    dark:text-dark-text-muted
                    dark:hover:bg-dark-surface-soft
                  "
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={!reason || isSubmitting}
                  className="
                    inline-flex min-h-11 w-full
                    items-center justify-center gap-2
                    rounded-xl bg-brand-teal
                    px-5 py-3 text-sm font-semibold text-white
                    transition-colors hover:bg-brand-teal-dark
                    focus-visible:outline-none
                    focus-visible:ring-2 focus-visible:ring-brand-teal
                    focus-visible:ring-offset-2
                    disabled:cursor-not-allowed disabled:opacity-60
                    sm:w-auto
                  "
                >
                  {isSubmitting && (
                    <span
                      aria-hidden="true"
                      className="
                        h-4 w-4 animate-spin rounded-full
                        border-2 border-white/40 border-t-white
                      "
                    />
                  )}

                  {isSubmitting ? 'Submitting...' : 'Submit report'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

function getReportErrorMessage(
  error: unknown,
  contentLabel: 'post' | 'comment' | 'reply',
): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return `You need to log in before reporting this ${contentLabel}.`;
    }

    if (error.status === 403) {
      return `You are not permitted to report this ${contentLabel}.`;
    }

    const data = error.data;

    if (data) {
      if (
        typeof data.detail === 'string' &&
        data.detail.trim()
      ) {
        return data.detail;
      }

      for (const [key, value] of Object.entries(data)) {
        if (key === 'detail') {
          continue;
        }

        if (Array.isArray(value) && value.length > 0) {
          const message = value.find(
            (item): item is string =>
              typeof item === 'string' &&
              item.trim().length > 0,
          );

          if (message) {
            return message;
          }
        }

        if (typeof value === 'string' && value.trim()) {
          return value;
        }
      }
    }

    if (error.status === 400) {
      return (
        error.message ||
        `Your ${contentLabel} report could not be submitted. Please check your selection and try again.`
      );
    }

    return error.message;
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return `We could not submit your ${contentLabel} report. Please try again.`;
}