'use client';

import { useEffect } from 'react';

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
  useEffect(() => {
    if (!open || isLoading) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onCancel();
      }
    };

    document.addEventListener(
      'keydown',
      handleKeyDown,
    );

    return () => {
      document.removeEventListener(
        'keydown',
        handleKeyDown,
      );
    };
  }, [open, isLoading, onCancel]);

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
        bg-black/50
        p-0
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
          onCancel();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirmation-modal-title"
        aria-describedby="confirmation-modal-description"
        className="
          w-full
          max-h-[90vh]
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
            >
              {icon ?? defaultIcon}
            </div>

            <div className="min-w-0 flex-1">
              <h2
                id="confirmation-modal-title"
                className="
                  text-base font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                {title}
              </h2>

              <p
                id="confirmation-modal-description"
                className="
                  mt-2 text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                {description}
              </p>
            </div>
          </div>

          {children && (
            <div className="mt-5">
              {children}
            </div>
          )}

          <div
            className="
              mt-6 flex flex-col-reverse gap-2
              sm:flex-row sm:justify-end
            "
          >
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="
                inline-flex min-h-11
                w-full items-center justify-center
                rounded-xl
                border border-light-border
                bg-light-surface
                px-4 py-2
                text-sm font-semibold
                text-light-text
                transition-colors
                hover:bg-light-surface-soft
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
                w-full items-center justify-center
                rounded-xl
                border
                px-4 py-2
                text-sm font-bold
                text-white
                transition-all duration-200
                disabled:cursor-not-allowed
                disabled:opacity-60
                sm:w-auto
                ${
                  destructive
                    ? `
                      border-red-600
                      bg-red-600
                      hover:bg-red-700
                      dark:border-red-500
                      dark:bg-red-500
                      dark:hover:bg-red-600
                    `
                    : `
                      border-brand-teal
                      bg-brand-teal
                      hover:bg-brand-teal-dark
                      dark:border-brand-teal
                      dark:bg-brand-teal
                      dark:hover:bg-brand-teal-dark
                    `
                }
              `}
            >
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