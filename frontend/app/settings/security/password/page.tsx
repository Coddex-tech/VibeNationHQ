'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  CheckCircleIcon,
  EyeIcon,
  EyeOffIcon,
  LockIcon,
  ShieldIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';
import HomeNav from '@/components/special/HomeNav';

type ChangePasswordResponse = {
  message: string;
};

export default function ChangePasswordPage() {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newPasswordConfirm, setNewPasswordConfirm] =
    useState('');

  const [showCurrentPassword, setShowCurrentPassword] =
    useState(false);
  const [showNewPassword, setShowNewPassword] =
    useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError('');
    setSuccessMessage('');

    if (!currentPassword) {
      setError('Please enter your current password.');
      return;
    }

    if (!newPassword) {
      setError('Please enter a new password.');
      return;
    }

    if (newPassword.length < 8) {
      setError(
        'Your new password must be at least 8 characters long.',
      );
      return;
    }

    if (!newPasswordConfirm) {
      setError(
        'Please confirm your new password.',
      );
      return;
    }

    if (newPassword !== newPasswordConfirm) {
      setError('Passwords do not match.');
      return;
    }

    if (currentPassword === newPassword) {
      setError(
        'Your new password must be different from your current password.',
      );
      return;
    }

    setSubmitting(true);

    try {
      const data =
        await apiRequest<ChangePasswordResponse>(
          '/api/accounts/password/change/',
          {
            method: 'POST',
            body: JSON.stringify({
              current_password: currentPassword,
              new_password: newPassword,
              new_password_confirm: newPasswordConfirm,
            }),
          },
        );

      setSuccessMessage(
        data.message ||
          'Password changed successfully.',
      );

      setCurrentPassword('');
      setNewPassword('');
      setNewPasswordConfirm('');
    } catch (err) {
      if (err instanceof ApiError) {
        const data = err.data;

        const currentPasswordError =
          data?.current_password;

        const newPasswordError =
          data?.new_password;

        const confirmPasswordError =
          data?.new_password_confirm;

        if (typeof currentPasswordError === 'string') {
          setError(currentPasswordError);
        } else if (Array.isArray(newPasswordError)) {
          setError(newPasswordError.join(' '));
        } else if (
          typeof newPasswordError === 'string'
        ) {
          setError(newPasswordError);
        } else if (
          typeof confirmPasswordError === 'string'
        ) {
          setError(confirmPasswordError);
        } else if (
          Array.isArray(confirmPasswordError)
        ) {
          setError(confirmPasswordError.join(' '));
        } else {
          setError(err.message);
        }
      } else {
        setError(
          'Something went wrong. Please try again.',
        );
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <HomeNav />

      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-12">
        <FadeIn>
          <div className="mb-8">
            <Link
              href="/settings/security"
              className="mb-5 inline-flex items-center gap-2 text-sm font-medium text-light-text-muted transition-colors hover:text-brand-teal dark:text-dark-text-muted dark:hover:text-brand-teal-light"
            >
              <span aria-hidden="true">←</span>
              Back to Security
            </Link>

            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light">
                <LockIcon className="h-6 w-6" />
              </div>

              <div>
                <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                  Change password
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-light-text-muted dark:text-dark-text-muted sm:text-base">
                  Choose a new password for your VibeNationHQ
                  account. Your other active sessions will be
                  signed out after the change.
                </p>
              </div>
            </div>
          </div>
        </FadeIn>

        <FadeIn delay={0.05}>
          <section className="overflow-hidden rounded-2xl border border-light-border bg-light-surface shadow-sm dark:border-dark-border dark:bg-dark-surface">
            <form
              onSubmit={handleSubmit}
              className="px-5 py-6 sm:px-6 sm:py-7"
            >
              <div className="mb-6">
                <h2 className="text-lg font-semibold">
                  Update your password
                </h2>

                <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                  Enter your current password, then choose and
                  confirm your new password.
                </p>
              </div>

              {error && (
                <div
                  role="alert"
                  className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-300"
                >
                  {error}
                </div>
              )}

              {successMessage && (
                <div
                  role="status"
                  className="mb-5 rounded-xl border border-brand-teal/25 bg-brand-teal/10 px-4 py-4 dark:border-brand-teal/30 dark:bg-brand-teal/10"
                >
                  <div className="flex items-start gap-3">
                    <CheckCircleIcon className="mt-0.5 h-5 w-5 shrink-0 text-brand-teal dark:text-brand-teal-light" />

                    <div>
                      <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                        Password changed successfully
                      </p>

                      <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                        Your password has been updated. Other
                        active sessions have been signed out for
                        your security.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-5">
                <PasswordField
                  id="current-password"
                  label="Current password"
                  value={currentPassword}
                  onChange={setCurrentPassword}
                  visible={showCurrentPassword}
                  onToggleVisibility={() =>
                    setShowCurrentPassword(
                      (visible) => !visible,
                    )
                  }
                  autoComplete="current-password"
                  disabled={submitting}
                />

                <div className="border-t border-light-border-soft pt-5 dark:border-dark-border-soft">
                  <PasswordField
                    id="new-password"
                    label="New password"
                    value={newPassword}
                    onChange={setNewPassword}
                    visible={showNewPassword}
                    onToggleVisibility={() =>
                      setShowNewPassword(
                        (visible) => !visible,
                      )
                    }
                    autoComplete="new-password"
                    disabled={submitting}
                  />

                  <p className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                    Your password must be at least 8 characters
                    and satisfy VibeNationHQ&apos;s password
                    requirements.
                  </p>
                </div>

                <PasswordField
                  id="new-password-confirm"
                  label="Confirm new password"
                  value={newPasswordConfirm}
                  onChange={setNewPasswordConfirm}
                  visible={showConfirmPassword}
                  onToggleVisibility={() =>
                    setShowConfirmPassword(
                      (visible) => !visible,
                    )
                  }
                  autoComplete="new-password"
                  disabled={submitting}
                />
              </div>

              <div className="mt-6 flex items-start gap-3 rounded-xl border border-light-border-soft bg-light-surface-soft px-4 py-3.5 dark:border-dark-border-soft dark:bg-dark-surface-soft">
                <ShieldIcon className="mt-0.5 h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />

                <p className="text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                  After changing your password, VibeNationHQ
                  will revoke your other active sessions. The
                  session you are currently using will remain
                  active.
                </p>
              </div>

              <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <Link
                  href="/settings/security"
                  className="inline-flex min-h-11 items-center justify-center rounded-xl border border-light-border px-5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-soft dark:border-dark-border dark:text-dark-text dark:hover:bg-dark-surface-soft"
                >
                  Cancel
                </Link>

                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex min-h-11 items-center justify-center rounded-xl bg-brand-teal px-5 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting
                    ? 'Changing password...'
                    : 'Change password'}
                </button>
              </div>
            </form>
          </section>
        </FadeIn>
      </div>
    </main>
  );
}

function PasswordField({
  id,
  label,
  value,
  onChange,
  visible,
  onToggleVisibility,
  autoComplete,
  disabled,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  visible: boolean;
  onToggleVisibility: () => void;
  autoComplete: string;
  disabled: boolean;
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-2 block text-sm font-medium"
      >
        {label}
      </label>

      <div className="relative">
        <LockIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-light-text-soft dark:text-dark-text-soft" />

        <input
          id={id}
          name={id}
          type={visible ? 'text' : 'password'}
          autoComplete={autoComplete}
          value={value}
          onChange={(event) =>
            onChange(event.target.value)
          }
          disabled={disabled}
          className="w-full rounded-xl border border-light-border bg-light-surface py-3 pl-11 pr-12 text-sm text-light-text outline-none transition focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:focus:border-brand-teal-light"
        />

        <button
          type="button"
          onClick={onToggleVisibility}
          disabled={disabled}
          aria-label={
            visible
              ? `Hide ${label.toLowerCase()}`
              : `Show ${label.toLowerCase()}`
          }
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-2 text-light-text-soft transition-colors hover:bg-light-surface-soft hover:text-light-text disabled:cursor-not-allowed disabled:opacity-50 dark:text-dark-text-soft dark:hover:bg-dark-surface-muted dark:hover:text-dark-text"
        >
          {visible ? (
            <EyeOffIcon className="h-5 w-5" />
          ) : (
            <EyeIcon className="h-5 w-5" />
          )}
        </button>
      </div>
    </div>
  );
}