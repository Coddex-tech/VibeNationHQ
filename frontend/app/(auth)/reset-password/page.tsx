// app/(auth)/reset-password/page.tsx

'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
  EyeIcon,
  EyeOffIcon,
  LockIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import { apiRequest, ApiError } from '@/lib/api';

type ResetPasswordResponse = {
  message: string;
};

export default function ResetPasswordPage() {
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] =
    useState('');

  const [isTokenMissing, setIsTokenMissing] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tokenParam = params.get('token');

    if (!tokenParam) {
      setIsTokenMissing(true);
      return;
    }

    setToken(tokenParam);
  }, []);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    setError('');
    setPasswordError('');
    setConfirmPasswordError('');

    if (!token) {
      setIsTokenMissing(true);
      setError(
        'This password reset link is missing or invalid.',
      );
      return;
    }

    if (!password || !confirmPassword) {
      setError('Please fill in both password fields.');
      return;
    }

    if (password !== confirmPassword) {
      setConfirmPasswordError(
        'Passwords do not match.',
      );
      return;
    }

    setIsSubmitting(true);

    try {
      await apiRequest<ResetPasswordResponse>(
        '/api/accounts/password/reset/',
        {
          method: 'POST',
          body: JSON.stringify({
            token,
            new_password: password,
            new_password_confirm: confirmPassword,
          }),
        },
      );

      window.location.href = '/login?reset=success';
    } catch (error) {
      if (error instanceof ApiError) {
        const data = error.data;

        if (data) {
          const tokenError = data.token;
          const newPasswordError = data.new_password;
          const confirmPasswordError =
            data.new_password_confirm;

          if (Array.isArray(newPasswordError)) {
            setPasswordError(
              newPasswordError.join(' '),
            );
          } else if (
            typeof newPasswordError === 'string'
          ) {
            setPasswordError(newPasswordError);
          }

          if (
            Array.isArray(confirmPasswordError)
          ) {
            setConfirmPasswordError(
              confirmPasswordError.join(' '),
            );
          } else if (
            typeof confirmPasswordError === 'string'
          ) {
            setConfirmPasswordError(
              confirmPasswordError,
            );
          }

          if (Array.isArray(tokenError)) {
            setError(tokenError.join(' '));
          } else if (
            typeof tokenError === 'string'
          ) {
            setError(tokenError);
          } else if (
            !newPasswordError &&
            !confirmPasswordError
          ) {
            setError(
              error.message ||
                'Unable to reset your password. Please try again.',
            );
          }
        } else {
          setError(
            error.message ||
              'Unable to reset your password. Please try again.',
          );
        }
      } else {
        setError(
          'Something went wrong. Please try again.',
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-light-bg text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text">
      <div className="flex min-h-screen items-start justify-center p-4 sm:p-6 lg:items-center">
        <FadeIn className="w-full max-w-6xl">
          <div className="relative grid overflow-hidden rounded-3xl border border-light-border bg-[#f7f8f8] shadow-xl shadow-black/5 dark:border-dark-border dark:bg-dark-surface dark:shadow-black/20 lg:grid-cols-[1.05fr_0.95fr]">
            
            {/* Editorial side */}
            <div className="hidden min-h-[720px] flex-col justify-between bg-light-surface p-10 dark:bg-[#282d2d] lg:flex xl:p-14">
              <div>
                <Link
                  href="/"
                  className="inline-flex items-center gap-2 text-xl font-bold tracking-tight text-light-text dark:text-dark-text"
                >
                  <span className="text-brand-teal">Vibe</span>
                  NationHQ
                </Link>

                <div className="mt-20 max-w-lg">
                  <div className="inline-flex items-center gap-2 rounded-full border border-brand-teal/20 bg-brand-teal/10 px-3 py-1.5 text-sm font-medium text-brand-teal">
                    <LockIcon className="h-4 w-4" />
                    Secure account recovery
                  </div>

                  <h1 className="mt-6 text-4xl font-bold tracking-tight text-light-text dark:text-dark-text xl:text-5xl">
                    A fresh password,
                    <span className="text-brand-teal">
                      {' '}
                      fresh Vibe.
                    </span>
                  </h1>

                  <p className="mt-5 max-w-lg text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Choose a new password to get back into your
                    VibeNationHQ account and continue exploring the
                    stories, music, entertainment, and culture you care
                    about.
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
                      Keep your account protected
                    </p>

                    <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                      Use a password that is unique to your
                      VibeNationHQ account and difficult for others to
                      guess.
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
                  <span className="text-brand-teal">Vibe</span>
                  NationHQ
                </Link>
              </div>

              <div className="mx-auto w-full max-w-md">
                <div className="mb-8">
                  <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal">
                    <LockIcon className="h-5 w-5" />
                  </div>

                  <h2 className="text-3xl font-bold tracking-tight text-light-text dark:text-dark-text">
                    Reset your password
                  </h2>

                  <p className="mt-3 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    Choose a new password for your VibeNationHQ account.
                  </p>
                </div>

                {isTokenMissing && (
                  <div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm leading-6 text-red-600 dark:text-red-400">
                    This password reset link is missing its
                    verification token. Please request a new reset
                    link.
                  </div>
                )}

                {error && !isTokenMissing && (
                  <div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm leading-6 text-red-600 dark:text-red-400">
                    {error}
                  </div>
                )}

                <form
                  className="space-y-5"
                  onSubmit={handleSubmit}
                >
                  {/* New password */}
                  <div>
                    <label
                      htmlFor="password"
                      className="mb-2 block text-sm font-medium text-light-text dark:text-dark-text"
                    >
                      New password
                    </label>

                    <div className="relative">
                      <input
                        id="password"
                        name="password"
                        type={
                          showPassword
                            ? 'text'
                            : 'password'
                        }
                        value={password}
                        onChange={(event) => {
                          setPassword(event.target.value);
                          setPasswordError('');
                          setError('');
                        }}
                        autoComplete="new-password"
                        placeholder="Enter your new password"
                        disabled={isSubmitting}
                        aria-invalid={Boolean(passwordError)}
                        aria-describedby={
                          passwordError
                            ? 'password-error'
                            : undefined
                        }
                        className={`w-full rounded-xl border bg-light-surface px-4 py-3.5 pr-12 text-sm text-light-text outline-none transition placeholder:text-light-text-soft focus:ring-4 focus:ring-brand-teal/10 dark:bg-dark-surface-soft dark:text-dark-text dark:placeholder:text-dark-text-soft dark:focus:ring-brand-teal/10 ${
                          passwordError
                            ? 'border-red-500 focus:border-red-500 dark:border-red-500'
                            : 'border-light-border focus:border-brand-teal dark:border-dark-border dark:focus:border-brand-teal'
                        }`}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            (value) => !value,
                          )
                        }
                        aria-label={
                          showPassword
                            ? 'Hide new password'
                            : 'Show new password'
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-light-text-soft transition hover:bg-light-surface-muted hover:text-light-text dark:text-dark-text-soft dark:hover:bg-dark-surface-muted dark:hover:text-dark-text"
                      >
                        {showPassword ? (
                          <EyeOffIcon className="h-5 w-5" />
                        ) : (
                          <EyeIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>

                    {passwordError ? (
                      <p
                        id="password-error"
                        className="mt-2 text-xs leading-5 text-red-600 dark:text-red-400"
                      >
                        {passwordError}
                      </p>
                    ) : (
                      <p className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                        Use at least 8 characters with a mix of letters
                        and numbers.
                      </p>
                    )}
                  </div>

                  {/* Confirm password */}
                  <div>
                    <label
                      htmlFor="confirmPassword"
                      className="mb-2 block text-sm font-medium text-light-text dark:text-dark-text"
                    >
                      Confirm new password
                    </label>

                    <div className="relative">
                      <input
                        id="confirmPassword"
                        name="confirmPassword"
                        type={
                          showConfirmPassword
                            ? 'text'
                            : 'password'
                        }
                        value={confirmPassword}
                        onChange={(event) => {
                          setConfirmPassword(
                            event.target.value,
                          );
                          setConfirmPasswordError('');
                          setError('');
                        }}
                        autoComplete="new-password"
                        placeholder="Re-enter your new password"
                        disabled={isSubmitting}
                        aria-invalid={Boolean(
                          confirmPasswordError,
                        )}
                        aria-describedby={
                          confirmPasswordError
                            ? 'confirm-password-error'
                            : undefined
                        }
                        className={`w-full rounded-xl border bg-light-surface px-4 py-3.5 pr-12 text-sm text-light-text outline-none transition placeholder:text-light-text-soft focus:ring-4 focus:ring-brand-teal/10 dark:bg-dark-surface-soft dark:text-dark-text dark:placeholder:text-dark-text-soft dark:focus:ring-brand-teal/10 ${
                          confirmPasswordError
                            ? 'border-red-500 focus:border-red-500 dark:border-red-500'
                            : 'border-light-border focus:border-brand-teal dark:border-dark-border dark:focus:border-brand-teal'
                        }`}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowConfirmPassword(
                            (value) => !value,
                          )
                        }
                        aria-label={
                          showConfirmPassword
                            ? 'Hide confirmed password'
                            : 'Show confirmed password'
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-light-text-soft transition hover:bg-light-surface-muted hover:text-light-text dark:text-dark-text-soft dark:hover:bg-dark-surface-muted dark:hover:text-dark-text"
                      >
                        {showConfirmPassword ? (
                          <EyeOffIcon className="h-5 w-5" />
                        ) : (
                          <EyeIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>

                    {confirmPasswordError && (
                      <p
                        id="confirm-password-error"
                        className="mt-2 text-xs leading-5 text-red-600 dark:text-red-400"
                      >
                        {confirmPasswordError}
                      </p>
                    )}
                  </div>

                  {/* Reset button */}
                  <button
                    type="submit"
                    disabled={
                      isSubmitting ||
                      isTokenMissing
                    }
                    className="w-full rounded-xl bg-brand-teal px-4 py-3.5 text-sm font-semibold text-white shadow-sm shadow-brand-teal/20 transition hover:bg-brand-teal-dark focus:outline-none focus:ring-4 focus:ring-brand-teal/20 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isSubmitting
                      ? 'Resetting password...'
                      : 'Reset password'}
                  </button>
                </form>

                {/* Security message */}
                <div className="mt-6 rounded-xl border border-light-border-soft bg-light-surface-soft p-4 dark:border-dark-border-soft dark:bg-dark-surface-soft">
                  <div className="flex items-start gap-3">
                    <ShieldCheckIcon className="mt-0.5 h-5 w-5 shrink-0 text-brand-teal" />

                    <p className="text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                      For your security, resetting your password may
                      sign you out of active sessions on other devices.
                    </p>
                  </div>
                </div>

                {/* Back to sign in */}
                <div className="mt-7 text-center">
                  <Link
                    href="/login"
                    className="text-sm font-semibold text-brand-teal transition hover:text-brand-teal-dark dark:hover:text-brand-teal-light"
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