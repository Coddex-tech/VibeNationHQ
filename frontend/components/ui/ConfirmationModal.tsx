
'use client';

import {
  useCallback,
  useEffect,
  useRef,
} from 'react';

import { AlertTriangleIcon } from '@/components/Icons';

type ConfirmationModalProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  isLoading?: boolean;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
};

export default function ConfirmationModal({
  open,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  destructive = false,
  isLoading = false,
  icon,
  children,
  onConfirm,
  onCancel,
}: ConfirmationModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);
  const isLoadingRef = useRef(isLoading);
  const onCancelRef = useRef(onCancel);

  // Keep event handlers current without repeatedly
  // attaching keyboard listeners.
  useEffect(() => {
    isLoadingRef.current = isLoading;
  }, [isLoading]);

  useEffect(() => {
    onCancelRef.current = onCancel;
  }, [onCancel]);

  const handleCancel = useCallback(() => {
    if (isLoadingRef.current) {
      return;
    }

    onCancelRef.current();
  }, []);

  useEffect(() => {
    if (!open) {
      return;
    }

    const previousFocus =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;

    const dialog = dialogRef.current;

    cancelButtonRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        if (!isLoadingRef.current) {
          event.preventDefault();
          handleCancel();
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
            'input:not(:disabled)',
            'select:not(:disabled)',
            'textarea:not(:disabled)',
            'a[href]',
            '[tabindex]:not([tabindex="-1"])',
          ].join(','),
        );

      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const first = focusableElements[0];
      const last =
        focusableElements[focusableElements.length - 1];

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

    document.addEventListener(
      'keydown',
      handleKeyDown,
    );

    return () => {
      document.removeEventListener(
        'keydown',
        handleKeyDown,
      );

      previousFocus?.focus();
    };
  }, [open, handleCancel]);

  if (!open) {
    return null;
  }

  const defaultIcon = (
    <AlertTriangleIcon className="h-5 w-5" />
  );

  return (
    <div
      className="
        fixed inset-0 z-[100]
        flex items-end justify-center
        overflow-y-auto
        bg-black/50 p-0
        backdrop-blur-[2px]
        sm:items-center
        sm:p-4
      "
      role="presentation"
      onMouseDown={(event) => {
        if (
          event.target === event.currentTarget &&
          !isLoading
        ) {
          handleCancel();
        }
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirmation-modal-title"
        aria-describedby="confirmation-modal-description"
        className="
          my-auto
          w-full max-h-[90vh]
          overflow-y-auto
          rounded-t-2xl
          border border-light-border
          bg-light-surface
          shadow-2xl shadow-black/20
          dark:border-dark-border
          dark:bg-dark-surface
          dark:shadow-black/50
          sm:max-w-md
          sm:rounded-2xl
        "
      >
        <div className="p-5 sm:p-6">
          {/* Header */}
          <div className="flex items-start gap-4">
            <div
              className={`
                flex h-11 w-11 shrink-0
                items-center justify-center
                rounded-xl
                ${
                  destructive
                    ? `
                      bg-red-500/10
                      text-red-600
                      dark:text-red-300
                    `
                    : `
                      bg-brand-teal/10
                      text-brand-teal-dark
                      dark:text-brand-teal-light
                    `
                }
              `}
              aria-hidden="true"
            >
              {icon ?? defaultIcon}
            </div>

            <div className="min-w-0 flex-1 pt-0.5">
              <h2
                id="confirmation-modal-title"
                className="
                  text-lg font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                {title}
              </h2>

              <p
                id="confirmation-modal-description"
                className="
                  mt-1.5 text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                {description}
              </p>
            </div>
          </div>

          {/* Optional custom content */}
          {children && (
            <div className="mt-5">
              {children}
            </div>
          )}

          {/* Actions */}
          <div
            className="
              mt-6 flex flex-col-reverse gap-3
              sm:flex-row sm:justify-end
            "
          >
            <button
              ref={cancelButtonRef}
              type="button"
              onClick={handleCancel}
              disabled={isLoading}
              className="
                inline-flex min-h-11
                w-full items-center justify-center
                rounded-xl
                border border-light-border
                bg-light-surface
                px-4 py-3
                text-sm font-semibold
                text-light-text
                transition-colors duration-200
                hover:bg-light-surface-soft
                focus-visible:outline-none
                focus-visible:ring-2
                focus-visible:ring-brand-teal
                focus-visible:ring-offset-2
                disabled:cursor-not-allowed
                disabled:opacity-60
                sm:w-auto
                dark:border-dark-border
                dark:bg-dark-surface
                dark:text-dark-text
                dark:hover:bg-dark-surface-soft
              "
            >
              {cancelLabel}
            </button>

            <button
              type="button"
              onClick={onConfirm}
              disabled={isLoading}
              className={`
                inline-flex min-h-11
                w-full items-center justify-center gap-2
                rounded-xl
                border px-5 py-3
                text-sm font-semibold
                text-white
                transition-colors duration-200
                focus-visible:outline-none
                focus-visible:ring-2
                focus-visible:ring-offset-2
                disabled:cursor-not-allowed
                disabled:opacity-60
                sm:w-auto
                ${
                  destructive
                    ? `
                      border-red-600
                      bg-red-600
                      hover:bg-red-700
                      focus-visible:ring-red-500
                      dark:border-red-500
                      dark:bg-red-500
                      dark:hover:bg-red-600
                    `
                    : `
                      border-brand-teal
                      bg-brand-teal
                      hover:bg-brand-teal-dark
                      focus-visible:ring-brand-teal
                      dark:border-brand-teal
                      dark:bg-brand-teal
                      dark:hover:bg-brand-teal-dark
                    `
                }
              `}
            >
              {isLoading && (
                <span
                  aria-hidden="true"
                  className="
                    h-4 w-4 animate-spin
                    rounded-full
                    border-2 border-white/40
                    border-t-white
                  "
                />
              )}

              {isLoading
                ? 'Please wait...'
                : confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}