'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  CheckCircleIcon,
  LockIcon,
  MailIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';
import HomeNav from '@/components/special/HomeNav';

type CurrentUserResponse = {
  user: {
    id: string;
    email: string;
    username: string;
    is_active?: boolean;
  };
};

type ChangeEmailResponse = {
  message: string;
};

export default function ChangeEmailPage() {
  const [currentEmail, setCurrentEmail] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');

  const [loadingUser, setLoadingUser] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    async function loadUser() {
      try {
        const data =
          await apiRequest<CurrentUserResponse>(
            '/api/accounts/me/',
          );

        setCurrentEmail(data.user.email);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError(
            'Unable to load your account information.',
          );
        }
      } finally {
        setLoadingUser(false);
      }
    }

    loadUser();
  }, []);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError('');
    setSuccessMessage('');

    const trimmedEmail = newEmail.trim().toLowerCase();

    if (!trimmedEmail) {
      setError('Please enter your new email address.');
      return;
    }

    if (!currentPassword) {
      setError('Please enter your current password.');
      return;
    }

    if (
      currentEmail &&
      trimmedEmail === currentEmail.toLowerCase()
    ) {
      setError(
        'Your new email must be different from your current email.',
      );
      return;
    }

    setSubmitting(true);

    try {
      const data =
        await apiRequest<ChangeEmailResponse>(
          '/api/accounts/email/change/',
          {
            method: 'POST',
            body: JSON.stringify({
              current_password: currentPassword,
              new_email: trimmedEmail,
            }),
          },
        );

      setSuccessMessage(
        data.message ||
          'A verification link has been sent to your new email address.',
      );

      setCurrentPassword('');
      setNewEmail('');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(
          'Something went wrong. Please try again.',
        );
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (loadingUser) {
    return (
      <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
        <HomeNav />

        <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl items-center justify-center px-4 py-12 sm:px-6">
          <div className="text-sm text-light-text-muted dark:text-dark-text-muted">
            Loading security settings...
          </div>
        </div>
      </main>
    );
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
                <MailIcon className="h-6 w-6" />
              </div>

              <div>
                <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                  Change email
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-light-text-muted dark:text-dark-text-muted sm:text-base">
                  Update the email address connected to your
                  VibeNationHQ account. You&apos;ll need to verify
                  the new address before the change takes effect.
                </p>
              </div>
            </div>
          </div>
        </FadeIn>

        <FadeIn delay={0.05}>
          <section className="overflow-hidden rounded-2xl border border-light-border bg-light-surface shadow-sm dark:border-dark-border dark:bg-dark-surface">
            <div className="border-b border-light-border-soft px-5 py-5 dark:border-dark-border-soft sm:px-6">
              <div className="flex items-center gap-3">
                <MailIcon className="h-5 w-5 text-brand-teal" />

                <div>
                  <h2 className="font-semibold">
                    Current email
                  </h2>

                  <p className="mt-1 text-sm text-light-text-muted dark:text-dark-text-muted">
                    Your currently verified account email.
                  </p>
                </div>
              </div>

              <div className="mt-4 flex flex-col gap-3 rounded-xl border border-light-border-soft bg-light-surface-soft p-4 dark:border-dark-border-soft dark:bg-dark-surface-soft sm:flex-row sm:items-center sm:justify-between">
                <span className="break-all text-sm font-medium">
                  {currentEmail}
                </span>

                <span className="inline-flex w-fit items-center gap-1.5 rounded-full bg-brand-teal/10 px-2.5 py-1 text-xs font-semibold text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light">
                  <CheckCircleIcon className="h-3.5 w-3.5" />
                  Verified
                </span>
              </div>
            </div>

            <form
              onSubmit={handleSubmit}
              className="px-5 py-6 sm:px-6 sm:py-7"
            >
              <div className="mb-6">
                <h2 className="text-lg font-semibold">
                  Enter your new email
                </h2>

                <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                  For your security, we&apos;ll first confirm
                  your current password.
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
                        Verification email sent
                      </p>

                      <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                        {successMessage}
                      </p>

                      <p className="mt-2 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                        Open the verification link in your new
                        email address. Your current email will
                        remain active until verification is
                        completed.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-5">
                <div>
                  <label
                    htmlFor="new-email"
                    className="mb-2 block text-sm font-medium"
                  >
                    New email address
                  </label>

                  <div className="relative">
                    <MailIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-light-text-soft dark:text-dark-text-soft" />

                    <input
                      id="new-email"
                      name="new-email"
                      type="email"
                      autoComplete="email"
                      value={newEmail}
                      onChange={(event) =>
                        setNewEmail(event.target.value)
                      }
                      placeholder="you@example.com"
                      disabled={submitting}
                      className="w-full rounded-xl border border-light-border bg-light-surface py-3 pl-11 pr-4 text-sm text-light-text outline-none transition focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:focus:border-brand-teal-light"
                    />
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="current-password"
                    className="mb-2 block text-sm font-medium"
                  >
                    Current password
                  </label>

                  <div className="relative">
                    <LockIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-light-text-soft dark:text-dark-text-soft" />

                    <input
                      id="current-password"
                      name="current-password"
                      type="password"
                      autoComplete="current-password"
                      value={currentPassword}
                      onChange={(event) =>
                        setCurrentPassword(event.target.value)
                      }
                      placeholder="Enter your current password"
                      disabled={submitting}
                      className="w-full rounded-xl border border-light-border bg-light-surface py-3 pl-11 pr-4 text-sm text-light-text outline-none transition focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:focus:border-brand-teal-light"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex items-start gap-3 rounded-xl border border-light-border-soft bg-light-surface-soft px-4 py-3.5 dark:border-dark-border-soft dark:bg-dark-surface-soft">
                <LockIcon className="mt-0.5 h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />

                <p className="text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                  Changing your email is a sensitive account
                  action. Your current password is required, and
                  the new email must be verified before it becomes
                  your account email.
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
                    ? 'Sending verification...'
                    : 'Continue'}
                </button>
              </div>
            </form>
          </section>
        </FadeIn>
      </div>
    </main>
  );
}