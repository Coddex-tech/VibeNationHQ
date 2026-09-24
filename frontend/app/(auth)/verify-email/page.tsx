'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
  MailIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import { apiRequest, ApiError } from '@/lib/api';

type VerifyEmailResponse = {
  message: string;
};

export default function VerifyEmailPage() {
  const [email, setEmail] = useState('');
  const [isResending, setIsResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const verificationStarted = useRef(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    const emailParam = params.get('email');
    const token = params.get('token');

    if (emailParam) {
      setEmail(emailParam);
    }

    if (!token || verificationStarted.current) {
      return;
    }

    verificationStarted.current = true;

    const verifyEmail = async () => {
      try {
        await apiRequest<VerifyEmailResponse>(
          '/api/accounts/verify-email/',
          {
            method: 'POST',
            body: JSON.stringify({
              token,
            }),
          },
        );

        window.location.href = '/verify-email/success';
      } catch (error) {
        console.error('Email verification failed:', error);

        window.location.href = '/verify-email/error';
      }
    };

    verifyEmail();
  }, []);

  useEffect(() => {
    if (resendCooldown <= 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setResendCooldown((current) => {
        if (current <= 1) {
          window.clearInterval(timer);
          return 0;
        }

        return current - 1;
      });
    }, 1000);

    return () => {
      window.clearInterval(timer);
    };
  }, [resendCooldown]);

  const handleResend = async () => {
    if (!email || isResending || resendCooldown > 0) {
      return;
    }

    setIsResending(true);

    try {
      await apiRequest<VerifyEmailResponse>(
        '/api/accounts/resend-verification/',
        {
          method: 'POST',
          body: JSON.stringify({
            email,
          }),
        },
      );

      setResendCooldown(60);
    } catch (error) {
      if (error instanceof ApiError) {
        console.error(
          'Unable to resend verification email:',
          error.data ?? error.message,
        );
      } else {
        console.error(
          'Unable to resend verification email:',
          error,
        );
      }
    } finally {
      setIsResending(false);
    }
  };

  const resendLabel = isResending
    ? 'Sending...'
    : resendCooldown > 0
      ? `Resend available in ${resendCooldown}s`
      : 'Resend verification email';

  return (
    <main className="min-h-screen bg-light-bg text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text">
      <div className="flex min-h-screen items-start justify-center p-4 sm:p-6 lg:items-center">
        <FadeIn className="w-full max-w-6xl">
          <div className="relative grid overflow-hidden rounded-3xl border border-light-border bg-[#f7f8f8] shadow-xl shadow-black/5 dark:border-dark-border dark:bg-dark-surface dark:shadow-black/20 lg:grid-cols-[1.05fr_0.95fr]">

            {/* Editorial side */}
            <div className="hidden min-h-[680px] flex-col justify-between bg-light-surface p-10 dark:bg-[#282d2d] lg:flex xl:p-14">
              <div>
                <Link
                  href="/"
                  className="inline-flex items-center text-xl font-bold tracking-tight text-light-text dark:text-dark-text"
                >
                  <span className="text-brand-teal">Vibe</span>NationHQ
                </Link>

                <div className="mt-20 max-w-lg">
                  <div className="inline-flex items-center gap-2 rounded-full border border-brand-teal/20 bg-brand-teal/10 px-3 py-1.5 text-sm font-medium text-brand-teal">
                    <MailIcon className="h-4 w-4" />
                    Verify your email
                  </div>

                  <h1 className="mt-6 text-4xl font-bold tracking-tight text-light-text dark:text-dark-text xl:text-5xl">
                    One quick step,
                    <span className="text-brand-teal">
                      {' '}
                      then you&apos;re in.
                    </span>
                  </h1>

                  <p className="mt-5 max-w-lg text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Confirm your email address to help keep your
                    VibeNationHQ account secure and make sure we can
                    reach you when it matters.
                  </p>
                </div>
              </div>

              <div className="rounded-2xl border border-light-border-soft bg-light-surface-soft p-5 dark:border-dark-border-soft dark:bg-dark-surface-soft">
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal">
                    <ShieldCheckIcon className="h-5 w-5" />
                  </div>

                  <div>
                    <p className="font-semibold text-light-text dark:text-dark-text">
                      Why verify your email?
                    </p>

                    <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                      A verified email helps protect your account and
                      gives you a reliable way to recover access if you
                      ever forget your password.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Form side */}
            <div className="relative flex min-h-[680px] flex-col justify-center p-6 sm:p-8 lg:p-10 xl:p-14">
              {/* Theme toggle */}
              <div className="absolute right-4 top-4 z-50 sm:right-5 sm:top-5">
                <ThemeToggle />
              </div>

              {/* Mobile brand */}
              <div className="mb-10 lg:hidden">
                <Link
                  href="/"
                  className="text-xl font-bold tracking-tight text-light-text dark:text-dark-text"
                >
                  <span className="text-brand-teal">Vibe</span>NationHQ
                </Link>
              </div>

              <div className="mx-auto w-full max-w-md text-center">
                {/* Icon */}
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal">
                  <MailIcon className="h-7 w-7" />
                </div>

                <div className="mt-7">
                  <h2 className="text-3xl font-bold tracking-tight text-light-text dark:text-dark-text">
                    Check your inbox
                  </h2>

                  <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    We&apos;ve sent a verification link to
                  </p>

                  <p className="mt-1 break-all text-sm font-semibold text-light-text dark:text-dark-text">
                    {email || 'your email address'}
                  </p>
                </div>

                {/* Instructions */}
                <div className="mt-8 rounded-2xl border border-light-border-soft bg-light-surface-soft p-5 text-left dark:border-dark-border-soft dark:bg-dark-surface-soft">
                  <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                    What to do next
                  </p>

                  <ol className="mt-3 space-y-3 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    <li className="flex gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-teal/10 text-xs font-semibold text-brand-teal">
                        1
                      </span>

                      <span>
                        Open the verification email we just sent you.
                      </span>
                    </li>

                    <li className="flex gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-teal/10 text-xs font-semibold text-brand-teal">
                        2
                      </span>

                      <span>
                        Click the verification link in the email.
                      </span>
                    </li>

                    <li className="flex gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-teal/10 text-xs font-semibold text-brand-teal">
                        3
                      </span>

                      <span>
                        Return to VibeNationHQ and continue using your
                        account.
                      </span>
                    </li>
                  </ol>
                </div>

                {/* Resend */}
                <div className="mt-7">
                  <p className="text-sm text-light-text-muted dark:text-dark-text-muted">
                    Didn&apos;t receive the email?
                  </p>

                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={
                      !email ||
                      isResending ||
                      resendCooldown > 0
                    }
                    className="mt-2 text-sm font-semibold text-brand-teal transition hover:text-brand-teal-dark disabled:cursor-not-allowed disabled:opacity-60 dark:hover:text-brand-teal-light"
                  >
                    {resendLabel}
                  </button>
                </div>

                {/* Help */}
                <p className="mx-auto mt-6 max-w-sm text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                  Check your spam or junk folder if you don&apos;t see
                  the email. Make sure the address above is the one you
                  used when creating your account.
                </p>

                {/* Back */}
                <div className="mt-7">
                  <Link
                    href="/login"
                    className="text-sm font-semibold text-light-text-muted transition hover:text-light-text dark:text-dark-text-muted dark:hover:text-dark-text"
                  >
                    Back to sign in
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}