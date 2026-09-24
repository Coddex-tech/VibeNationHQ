'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
  CheckCircleIcon,
  HomeIcon,
  MailIcon,
  ShieldIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';

type VerifyEmailChangeResponse = {
  message: string;
  user: {
    id: string;
    email: string;
    username: string;
  };
};

export default function VerifyEmailChangePage() {
  const searchParams = useSearchParams();

  const token = searchParams.get('token');

  const [status, setStatus] = useState<
    'loading' | 'success' | 'error'
  >('loading');

  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage(
        'This email verification link is missing its verification token.',
      );
      return;
    }

    let cancelled = false;

    async function verifyEmailChange() {
      try {
        const data =
          await apiRequest<VerifyEmailChangeResponse>(
            '/api/accounts/email/change/verify/',
            {
              method: 'POST',
              body: JSON.stringify({
                token,
              }),
            },
          );

        if (cancelled) {
          return;
        }

        setEmail(data.user.email);
        setMessage(
          data.message ||
            'Email address changed successfully.',
        );
        setStatus('success');
      } catch (err) {
        if (cancelled) {
          return;
        }

        if (err instanceof ApiError) {
          setMessage(err.message);
        } else {
          setMessage(
            'Something went wrong while verifying your email address.',
          );
        }

        setStatus('error');
      }
    }

    verifyEmailChange();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const isLoading = status === 'loading';
  const isSuccess = status === 'success';

  return (
    <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <header className="border-b border-light-border-soft bg-light-surface/95 backdrop-blur-sm dark:border-dark-border-soft dark:bg-dark-surface/95">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link
            href="/"
            className="text-xl font-bold tracking-tight text-brand-teal"
          >
            VibeNationHQ
          </Link>

          <div className="flex items-center gap-2">
            <Link
              href="/"
              aria-label="Go to homepage"
              className="rounded-xl p-2.5 text-light-text-muted transition-colors hover:bg-light-surface-soft hover:text-light-text dark:text-dark-text-muted dark:hover:bg-dark-surface-soft dark:hover:text-dark-text"
            >
              <HomeIcon className="h-5 w-5" />
            </Link>

            <ThemeToggle />
          </div>
        </div>
      </header>

      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-xl items-center px-4 py-12 sm:px-6">
        <FadeIn className="w-full">
          <section className="overflow-hidden rounded-2xl border border-light-border bg-light-surface shadow-sm dark:border-dark-border dark:bg-dark-surface">
            <div className="px-5 py-8 text-center sm:px-8 sm:py-10">
              {isLoading && (
                <>
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-teal/10 dark:bg-brand-teal/15">
                    <MailIcon className="h-7 w-7 animate-pulse text-brand-teal dark:text-brand-teal-light" />
                  </div>

                  <h1 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
                    Verifying your email
                  </h1>

                  <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    We&apos;re confirming your new email address.
                    This should only take a moment.
                  </p>

                  <div className="mx-auto mt-7 h-1.5 w-32 overflow-hidden rounded-full bg-light-surface-muted dark:bg-dark-surface-muted">
                    <div className="h-full w-1/2 animate-pulse rounded-full bg-brand-teal" />
                  </div>
                </>
              )}

              {isSuccess && (
                <>
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-brand-teal/10 dark:bg-brand-teal/15">
                    <CheckCircleIcon className="h-8 w-8 text-brand-teal dark:text-brand-teal-light" />
                  </div>

                  <h1 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
                    Email address changed
                  </h1>

                  <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    {message}
                  </p>

                  {email && (
                    <div className="mx-auto mt-6 max-w-md rounded-xl border border-brand-teal/20 bg-brand-teal/5 px-4 py-4 text-left dark:border-brand-teal/25 dark:bg-brand-teal/10">
                      <div className="flex items-start gap-3">
                        <MailIcon className="mt-0.5 h-5 w-5 shrink-0 text-brand-teal dark:text-brand-teal-light" />

                        <div className="min-w-0">
                          <p className="text-xs font-medium text-light-text-muted dark:text-dark-text-muted">
                            Your new email
                          </p>

                          <p className="mt-1 break-all text-sm font-semibold text-light-text dark:text-dark-text">
                            {email}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mx-auto mt-6 flex max-w-md items-start gap-3 rounded-xl border border-light-border-soft bg-light-surface-soft px-4 py-3.5 text-left dark:border-dark-border-soft dark:bg-dark-surface-soft">
                    <ShieldIcon className="mt-0.5 h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />

                    <p className="text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                      Your account email has been updated. Keep
                      your email address secure because it can be
                      used for account recovery and important
                      security notifications.
                    </p>
                  </div>

                  <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
                    <Link
                      href="/settings/security"
                      className="inline-flex min-h-11 items-center justify-center rounded-xl bg-brand-teal px-5 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark"
                    >
                      Back to Security
                    </Link>

                    <Link
                      href="/account"
                      className="inline-flex min-h-11 items-center justify-center rounded-xl border border-light-border px-5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-soft dark:border-dark-border dark:text-dark-text dark:hover:bg-dark-surface-soft"
                    >
                      Go to Account
                    </Link>
                  </div>
                </>
              )}

              {!isLoading && !isSuccess && (
                <>
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-50 dark:bg-red-950/30">
                    <MailIcon className="h-8 w-8 text-red-600 dark:text-red-400" />
                  </div>

                  <h1 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
                    Verification failed
                  </h1>

                  <p
                    role="alert"
                    className="mx-auto mt-3 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted"
                  >
                    {message}
                  </p>

                  <div className="mx-auto mt-6 max-w-md rounded-xl border border-light-border-soft bg-light-surface-soft px-4 py-4 text-left dark:border-dark-border-soft dark:bg-dark-surface-soft">
                    <p className="text-sm font-semibold">
                      What you can do
                    </p>

                    <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                      If this link has expired or has already been
                      used, return to Security and start the email
                      change process again.
                    </p>
                  </div>

                  <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
                    <Link
                      href="/settings/security/email"
                      className="inline-flex min-h-11 items-center justify-center rounded-xl bg-brand-teal px-5 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark"
                    >
                      Change email again
                    </Link>

                    <Link
                      href="/"
                      className="inline-flex min-h-11 items-center justify-center rounded-xl border border-light-border px-5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-soft dark:border-dark-border dark:text-dark-text dark:hover:bg-dark-surface-soft"
                    >
                      Go to Homepage
                    </Link>
                  </div>
                </>
              )}
            </div>
          </section>
        </FadeIn>
      </div>
    </main>
  );
}