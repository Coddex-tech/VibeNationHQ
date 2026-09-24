'use client';

import Link from 'next/link';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
  CheckCircleIcon,
  ShieldCheckIcon,
} from '@/components/Icons';

export default function VerifyEmailSuccessPage() {
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
                    <CheckCircleIcon className="h-4 w-4" />
                    Email verified
                  </div>

                  <h1 className="mt-6 text-4xl font-bold tracking-tight text-light-text dark:text-dark-text xl:text-5xl">
                    You&apos;re all set.
                    <span className="text-brand-teal"> Welcome to the Vibe.</span>
                  </h1>

                  <p className="mt-5 max-w-lg text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Your email has been successfully verified. Your
                    VibeNationHQ account is now ready for the stories,
                    music, entertainment, and culture waiting for you.
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
                      Your account is protected
                    </p>

                    <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                      A verified email gives you a trusted way to
                      receive important account messages and recover
                      access when needed.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Success side */}
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
                {/* Success icon */}
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-brand-teal/10 text-brand-teal">
                  <CheckCircleIcon className="h-10 w-10" />
                </div>

                <div className="mt-7">
                  <h2 className="text-3xl font-bold tracking-tight text-light-text dark:text-dark-text">
                    Email verified
                  </h2>

                  <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    Your email address has been successfully verified.
                    Your VibeNationHQ account is ready to go.
                  </p>
                </div>

                {/* Verified status */}
                <div className="mt-8 rounded-2xl border border-brand-teal/20 bg-brand-teal/5 p-5 text-left dark:bg-brand-teal/10">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal">
                      <CheckCircleIcon className="h-5 w-5" />
                    </div>

                    <div>
                      <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                        Email address verified
                      </p>

                      <p className="mt-0.5 text-xs text-light-text-muted dark:text-dark-text-muted">
                        Your account email is now trusted.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Continue */}
                <div className="mt-7">
                  <Link
                    href="/"
                    className="flex w-full items-center justify-center rounded-xl bg-brand-teal px-4 py-3.5 text-sm font-semibold text-white shadow-sm shadow-brand-teal/20 transition hover:bg-brand-teal-dark focus:outline-none focus:ring-4 focus:ring-brand-teal/20 active:scale-[0.99]"
                  >
                    Continue to VibeNationHQ
                  </Link>
                </div>

                {/* Security note */}
                <div className="mt-6 flex items-start gap-2.5 text-left">
                  <ShieldCheckIcon className="mt-0.5 h-4 w-4 shrink-0 text-brand-teal" />

                  <p className="text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                    Keep your account details secure and never share
                    your password or verification links with anyone.
                  </p>
                </div>

                {/* Sign in */}
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