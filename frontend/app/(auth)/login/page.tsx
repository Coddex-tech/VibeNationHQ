// app/(auth)/login/page.tsx

'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
  CheckCircleIcon,
  EyeIcon,
  EyeOffIcon,
  GoogleIcon,
  LockIcon,
  MailIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';

type LoginResponse = {
  message: string;
  user: {
    id: string;
    email: string;
    username: string;
  };
};

type FormErrors = {
  email?: string;
  password?: string;
  general?: string;
};

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const resetSuccessful =
    searchParams.get('reset') === 'success';

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setErrors({});
    setIsSubmitting(true);

    try {
      await apiRequest<LoginResponse>(
        '/api/accounts/login/',
        {
          method: 'POST',
          body: JSON.stringify({
            email,
            password,
          }),
        },
      );

      router.push('/account');
    } catch (error) {
      if (error instanceof ApiError) {
        const data = error.data;

        setErrors({
          email: Array.isArray(data?.email)
            ? String(data.email[0])
            : undefined,

          password: Array.isArray(data?.password)
            ? String(data.password[0])
            : undefined,

          general:
            typeof data?.detail === 'string'
              ? data.detail
              : 'Unable to sign in. Please check your details and try again.',
        });
      } else {
        setErrors({
          general:
            'Unable to sign in right now. Please check your connection and try again.',
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-light-bg text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl items-start px-4 py-5 sm:items-center sm:px-6 sm:py-8 lg:px-8 lg:py-10">
        <div
          className="
            relative grid w-full overflow-hidden rounded-2xl
            border border-light-border
            bg-[#f7f8f8]
            shadow-lg shadow-black/[0.04]
            dark:border-dark-border
            dark:bg-dark-surface
            dark:shadow-black/20
            lg:min-h-[660px]
            lg:grid-cols-[0.9fr_1.1fr]
          "
        >
          {/* Theme toggle */}
          <div className="absolute right-4 top-4 z-50 sm:right-5 sm:top-5">
            <ThemeToggle />
          </div>

          {/* Brand / editorial side */}
          <section
            className="
              relative hidden overflow-hidden
              border-r border-light-border
              bg-light-surface-soft
              p-8
              dark:border-dark-border
              dark:bg-dark-surface-soft
              lg:flex lg:flex-col lg:justify-between
              lg:p-10
              xl:p-12
            "
          >
            <div className="relative z-10">
              <Link
                href="/"
                className="inline-flex items-center"
                aria-label="VibeNationHQ home"
              >
                <span className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text">
                  VibeNation
                  <span className="text-brand-teal">HQ</span>
                </span>
              </Link>

              <div className="mt-20 max-w-md xl:mt-24">
                <FadeIn>
                  <div
                    className="
                      mb-5 inline-flex items-center gap-2
                      rounded-full
                      border border-brand-teal/20
                      bg-brand-teal/10
                      px-3 py-1.5
                      text-xs font-semibold
                      text-brand-teal-dark
                      dark:border-brand-teal/30
                      dark:bg-brand-teal/10
                      dark:text-brand-teal-light
                    "
                  >
                    <ShieldCheckIcon className="h-4 w-4" />
                    Your VibeNation account
                  </div>

                  <h1 className="text-4xl font-black leading-tight tracking-tight text-light-text dark:text-dark-text xl:text-5xl">
                    Welcome back to your
                    <span className="text-brand-teal"> Vibe.</span>
                  </h1>

                  <p className="mt-5 max-w-lg text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Sign in to stay connected to the stories, music,
                    entertainment, and culture shaping the world around you.
                  </p>
                </FadeIn>
              </div>
            </div>

            <div className="relative z-10">
              <div className="grid grid-cols-2 gap-3">
                <div
                  className="
                    rounded-xl
                    border border-light-border-soft
                    bg-light-surface
                    p-4
                    dark:border-dark-border-soft
                    dark:bg-dark-surface
                  "
                >
                  <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                    Music
                  </p>

                  <p className="mt-1 text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                    Discover songs, artists and conversations.
                  </p>
                </div>

                <div
                  className="
                    rounded-xl
                    border border-light-border-soft
                    bg-light-surface
                    p-4
                    dark:border-dark-border-soft
                    dark:bg-dark-surface
                  "
                >
                  <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                    News
                  </p>

                  <p className="mt-1 text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                    Keep up with stories that matter.
                  </p>
                </div>
              </div>
            </div>

            <div
              className="
                pointer-events-none absolute
                -bottom-28 -right-28
                h-72 w-72
                rounded-full
                bg-brand-teal/[0.07]
                blur-3xl
              "
            />
          </section>

          {/* Login form */}
          <section
            className="
              flex items-center justify-center
              px-5 pb-7 pt-20
              sm:px-8 sm:pb-10 sm:pt-20
              lg:p-10
              xl:p-14
            "
          >
            <FadeIn className="w-full max-w-md">
              {/* Mobile brand */}
              <div className="lg:hidden">
                <Link
                  href="/"
                  className="inline-flex items-center"
                  aria-label="VibeNationHQ home"
                >
                  <span className="text-xl font-black tracking-tight text-light-text dark:text-dark-text">
                    VibeNation
                    <span className="text-brand-teal">HQ</span>
                  </span>
                </Link>
              </div>

              <div className="mt-8 lg:mt-0">
                {/* Password reset success */}
                {resetSuccessful && (
                  <div
                    role="status"
                    className="
                      mb-6 flex items-start gap-3
                      rounded-xl
                      border border-brand-teal/20
                      bg-brand-teal/10
                      px-4 py-3.5
                      text-sm leading-6
                      text-light-text
                      dark:border-brand-teal/30
                      dark:bg-brand-teal/10
                      dark:text-dark-text
                    "
                  >
                    <CheckCircleIcon className="mt-0.5 h-5 w-5 shrink-0 text-brand-teal" />

                    <div>
                      <p className="font-semibold">
                        Password reset successful
                      </p>

                      <p className="mt-0.5 text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                        Your password has been updated. You can now
                        sign in with your new password.
                      </p>
                    </div>
                  </div>
                )}

                <div className="mb-8">
                  <div
                    className="
                      mb-4 flex h-11 w-11 items-center justify-center
                      rounded-xl
                      border border-brand-teal/20
                      bg-brand-teal/10
                      text-brand-teal
                      dark:border-brand-teal/30
                      dark:bg-brand-teal/10
                    "
                  >
                    <LockIcon className="h-5 w-5" />
                  </div>

                  <h2 className="text-2xl font-bold tracking-tight text-light-text dark:text-dark-text sm:text-3xl">
                    Sign in
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    Welcome back. Enter your account details to continue.
                  </p>
                </div>

                {/* General error */}
                {errors.general && (
                  <div
                    role="alert"
                    className="
                      mb-5 rounded-xl
                      border border-red-200
                      bg-red-50
                      px-4 py-3
                      text-sm leading-6 text-red-700
                      dark:border-red-500/20
                      dark:bg-red-500/10
                      dark:text-red-300
                    "
                  >
                    {errors.general}
                  </div>
                )}

                <form
                  className="space-y-5"
                  onSubmit={handleSubmit}
                >
                  {/* Email */}
                  <div>
                    <label
                      htmlFor="email"
                      className="mb-2 block text-sm font-semibold text-light-text dark:text-dark-text"
                    >
                      Email address
                    </label>

                    <div className="relative">
                      <MailIcon
                        className="
                          pointer-events-none absolute left-3.5 top-1/2
                          h-5 w-5 -translate-y-1/2
                          text-light-text-soft
                          dark:text-dark-text-soft
                        "
                      />

                      <input
                        id="email"
                        name="email"
                        type="email"
                        value={email}
                        onChange={(event) =>
                          setEmail(event.target.value)
                        }
                        autoComplete="email"
                        placeholder="you@example.com"
                        aria-invalid={Boolean(errors.email)}
                        className={`
                          h-12 w-full rounded-xl
                          border
                          bg-light-surface
                          pl-11 pr-4
                          text-sm text-light-text
                          placeholder:text-light-text-soft
                          outline-none
                          transition-all duration-200
                          focus:border-brand-teal
                          focus:ring-4
                          focus:ring-brand-teal/10
                          dark:bg-dark-surface-soft
                          dark:text-dark-text
                          dark:placeholder:text-dark-text-soft
                          dark:focus:border-brand-teal
                          dark:focus:ring-brand-teal/15
                          ${
                            errors.email
                              ? 'border-red-400 dark:border-red-400'
                              : 'border-light-border dark:border-dark-border'
                          }
                        `}
                      />
                    </div>

                    {errors.email && (
                      <p className="mt-2 text-xs font-medium text-red-600 dark:text-red-400">
                        {errors.email}
                      </p>
                    )}
                  </div>

                  {/* Password */}
                  <div>
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <label
                        htmlFor="password"
                        className="block text-sm font-semibold text-light-text dark:text-dark-text"
                      >
                        Password
                      </label>

                      <Link
                        href="/forgot-password"
                        className="
                          text-xs font-semibold
                          text-brand-teal-dark
                          transition-colors
                          hover:text-brand-teal
                          dark:text-brand-teal-light
                          dark:hover:text-brand-teal
                        "
                      >
                        Forgot password?
                      </Link>
                    </div>

                    <div className="relative">
                      <LockIcon
                        className="
                          pointer-events-none absolute left-3.5 top-1/2
                          h-5 w-5 -translate-y-1/2
                          text-light-text-soft
                          dark:text-dark-text-soft
                        "
                      />

                      <input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(event) =>
                          setPassword(event.target.value)
                        }
                        autoComplete="current-password"
                        placeholder="Enter your password"
                        aria-invalid={Boolean(errors.password)}
                        className={`
                          h-12 w-full rounded-xl
                          border
                          bg-light-surface
                          pl-11 pr-12
                          text-sm text-light-text
                          placeholder:text-light-text-soft
                          outline-none
                          transition-all duration-200
                          focus:border-brand-teal
                          focus:ring-4
                          focus:ring-brand-teal/10
                          dark:bg-dark-surface-soft
                          dark:text-dark-text
                          dark:placeholder:text-dark-text-soft
                          dark:focus:border-brand-teal
                          dark:focus:ring-brand-teal/15
                          ${
                            errors.password
                              ? 'border-red-400 dark:border-red-400'
                              : 'border-light-border dark:border-dark-border'
                          }
                        `}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword((value) => !value)
                        }
                        aria-label={
                          showPassword
                            ? 'Hide password'
                            : 'Show password'
                        }
                        className="
                          absolute right-2 top-1/2
                          flex h-9 w-9 -translate-y-1/2
                          items-center justify-center
                          rounded-lg
                          text-light-text-soft
                          transition-colors
                          hover:bg-light-surface-muted
                          hover:text-light-text
                          dark:text-dark-text-soft
                          dark:hover:bg-dark-surface-muted
                          dark:hover:text-dark-text
                        "
                      >
                        {showPassword ? (
                          <EyeOffIcon className="h-5 w-5" />
                        ) : (
                          <EyeIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>

                    {errors.password && (
                      <p className="mt-2 text-xs font-medium text-red-600 dark:text-red-400">
                        {errors.password}
                      </p>
                    )}
                  </div>

                  {/* Submit */}
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="
                      flex h-12 w-full items-center justify-center gap-2
                      rounded-xl
                      bg-brand-teal
                      px-4
                      text-sm font-bold text-white
                      shadow-sm shadow-brand-teal/20
                      transition-all duration-200
                      hover:bg-brand-teal-dark
                      active:scale-[0.99]
                      focus:outline-none
                      focus:ring-4
                      focus:ring-brand-teal/20
                      disabled:cursor-not-allowed
                      disabled:opacity-70
                    "
                  >
                    {isSubmitting && (
                      <span
                        className="
                          h-4 w-4
                          animate-spin
                          rounded-full
                          border-2
                          border-white/30
                          border-t-white
                        "
                        aria-hidden="true"
                      />
                    )}

                    {isSubmitting ? 'Signing in...' : 'Sign in'}
                  </button>
                </form>

                {/* Divider */}
                <div className="my-7 flex items-center gap-4">
                  <div className="h-px flex-1 bg-light-border dark:bg-dark-border" />

                  <span className="text-[11px] font-semibold tracking-wide text-light-text-soft dark:text-dark-text-soft">
                    OR
                  </span>

                  <div className="h-px flex-1 bg-light-border dark:bg-dark-border" />
                </div>

                {/* Google */}
                <button
                  type="button"
                  className="
                    flex h-12 w-full items-center justify-center gap-3
                    rounded-xl
                    border border-light-border
                    bg-light-surface
                    px-4
                    text-sm font-semibold text-light-text
                    transition-all duration-200
                    hover:bg-light-surface-soft
                    hover:text-light-text
                    active:scale-[0.99]
                    focus:outline-none
                    focus:ring-4
                    focus:ring-brand-teal/10

                    dark:border-dark-border
                    dark:bg-dark-surface-soft
                    dark:text-dark-text

                    dark:hover:bg-[#3b4141]
                    dark:hover:text-[#f1f4f3]

                    dark:active:bg-[#353a3a]
                    dark:focus:ring-brand-teal/15
                  "
                >
                  <GoogleIcon className="h-5 w-5 shrink-0" />

                  <span>Continue with Google</span>
                </button>

                {/* Signup */}
                <p className="mt-8 text-center text-sm text-light-text-muted dark:text-dark-text-muted">
                  Don't have an account?{' '}
                  <Link
                    href="/signup"
                    className="
                      font-bold
                      text-brand-teal-dark
                      hover:text-brand-teal
                      dark:text-brand-teal-light
                      dark:hover:text-brand-teal
                    "
                  >
                    Create an account
                  </Link>
                </p>

                {/* Legal */}
                <div className="mt-8 border-t border-light-border-soft pt-5 text-center dark:border-dark-border-soft">
                  <p className="text-[11px] leading-5 text-light-text-soft dark:text-dark-text-soft">
                    By continuing, you agree to VibeNationHQ&apos;s{' '}
                    <Link
                      href="/terms"
                      className="underline underline-offset-2 hover:text-light-text dark:hover:text-dark-text"
                    >
                      Terms
                    </Link>{' '}
                    and{' '}
                    <Link
                      href="/privacy"
                      className="underline underline-offset-2 hover:text-light-text dark:hover:text-dark-text"
                    >
                      Privacy Policy
                    </Link>
                    .
                  </p>
                </div>
              </div>
            </FadeIn>
          </section>
        </div>
      </div>
    </div>
  );
}