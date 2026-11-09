'use client';

import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  useRouter,
  useSearchParams,
} from 'next/navigation';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  Loader2,
  ShieldCheck,
  UserRound,
  AtSign,
} from 'lucide-react';

import ThemeToggle from '@/components/ThemeToggle';
import { useAuth } from '@/components/auth/AuthProvider';
import { ApiError, apiRequest } from '@/lib/api';

type SetupStep = 'display-name' | 'username';

type UsernameAvailabilityResponse = {
  username: string;
  available: boolean;
  message?: string;
};

type FormErrors = {
  display_name?: string;
  username?: string;
  general?: string;
};

function getSafeNextPath(value: string | null): string {
  if (
    !value ||
    !value.startsWith('/') ||
    value.startsWith('//') ||
    value.includes('\\')
  ) {
    return '/music';
  }

  const pathname = value.split('?')[0].split('#')[0];

  const blockedPaths = [
    '/account/setup',
    '/login',
    '/signup',
    '/verify-email',
  ];

  if (
    blockedPaths.some(
      (path) =>
        pathname === path ||
        pathname.startsWith(`${path}/`),
    )
  ) {
    return '/';
  }

  return value;
}

function getApiErrorMessage(
  error: unknown,
  field: string,
): string | undefined {
  if (!(error instanceof ApiError)) {
    return undefined;
  }

  const data = error.data as
    | Record<string, unknown>
    | undefined;

  const fieldError = data?.[field];

  if (Array.isArray(fieldError) && fieldError.length > 0) {
    return String(fieldError[0]);
  }

  if (typeof fieldError === 'string') {
    return fieldError;
  }

  return undefined;
}

function getGeneralError(error: unknown): string {
  if (error instanceof ApiError) {
    const data = error.data as
      | Record<string, unknown>
      | undefined;

    if (typeof data?.detail === 'string') {
      return data.detail;
    }

    return 'Something went wrong. Please check your details and try again.';
  }

  return 'Unable to complete this step right now. Please check your connection and try again.';
}

function AccountSetupContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const {
    user,
    isAuthenticated,
    isLoading,
    refreshAuth,
  } = useAuth();

  const nextPath = getSafeNextPath(
    searchParams.get('next'),
  );

  const [step, setStep] = useState<SetupStep>(
    'display-name',
  );

  const [displayName, setDisplayName] = useState('');
  const [username, setUsername] = useState('');

  const [errors, setErrors] = useState<FormErrors>({});

  const [isSavingDisplayName, setIsSavingDisplayName] =
    useState(false);

  const [isSavingUsername, setIsSavingUsername] =
    useState(false);

  const [isRedirecting, setIsRedirecting] =
    useState(false);

  const [
    usernameAvailability,
    setUsernameAvailability,
  ] = useState<
    'idle' | 'checking' | 'available' | 'unavailable' | 'error'
  >('idle');

  const [availabilityMessage, setAvailabilityMessage] =
    useState('');

  const trimmedUsername = username.trim();

  const isUsernameFormatValid =
    /^[A-Za-z0-9_]{3,30}$/.test(trimmedUsername);

  const setupUrl = searchParams.get('next')
    ? `/account/setup?next=${encodeURIComponent(
        searchParams.get('next')!,
      )}`
    : '/account/setup';

  // Populate the display name from the authenticated user.
  useEffect(() => {
    if (!user) {
      return;
    }

    if (user.display_name?.trim()) {
      setDisplayName(user.display_name);
      setStep('username');
    }
  }, [user]);

  // Handle authentication and completed accounts.
  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (!isAuthenticated || !user) {
      router.replace(
        `/login?next=${encodeURIComponent(setupUrl)}`,
      );

      return;
    }

    if (user.onboarding_completed) {
      setIsRedirecting(true);
      router.replace(nextPath);
    }
  }, [
    isLoading,
    isAuthenticated,
    user,
    router,
    setupUrl,
    nextPath,
  ]);

  // Check username availability after the user pauses typing.
  useEffect(() => {
    if (step !== 'username') {
      return;
    }

    if (!trimmedUsername) {
      setUsernameAvailability('idle');
      setAvailabilityMessage('');
      return;
    }

    if (!isUsernameFormatValid) {
      setUsernameAvailability('idle');
      setAvailabilityMessage(
        'Use 3–30 characters: letters, numbers, and underscores only.',
      );
      return;
    }

    let isCurrentRequest = true;

    setUsernameAvailability('checking');
    setAvailabilityMessage('Checking username availability...');

    const timeout = setTimeout(async () => {
      try {
        const response =
          await apiRequest<UsernameAvailabilityResponse>(
            `/api/accounts/onboarding/username/availability/?username=${encodeURIComponent(
              trimmedUsername,
            )}`,
          );

        if (!isCurrentRequest) {
          return;
        }

        if (response.available) {
          setUsernameAvailability('available');
          setAvailabilityMessage(
            response.message || 'This username is available.',
          );
        } else {
          setUsernameAvailability('unavailable');
          setAvailabilityMessage(
            response.message || 'This username is already taken.',
          );
        }
      } catch {
        if (!isCurrentRequest) {
          return;
        }

        setUsernameAvailability('error');
        setAvailabilityMessage(
          'Unable to check availability. Please try again.',
        );
      }
    }, 450);

    return () => {
      isCurrentRequest = false;
      clearTimeout(timeout);
    };
  }, [
    trimmedUsername,
    isUsernameFormatValid,
    step,
  ]);

  const handleDisplayNameSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    const cleanedName = displayName.trim();

    setErrors({});

    if (!cleanedName) {
      setErrors({
        display_name: 'Please enter your display name.',
      });
      return;
    }

    if (cleanedName.length > 100) {
      setErrors({
        display_name:
          'Your display name cannot exceed 100 characters.',
      });
      return;
    }

    setIsSavingDisplayName(true);

    try {
      await apiRequest(
        '/api/accounts/onboarding/display-name/',
        {
          method: 'POST',
          body: JSON.stringify({
            display_name: cleanedName,
          }),
        },
      );

      await refreshAuth();

      setDisplayName(cleanedName);
      setStep('username');
      setErrors({});
    } catch (error) {
      setErrors({
        display_name: getApiErrorMessage(
          error,
          'display_name',
        ),
        general: getGeneralError(error),
      });
    } finally {
      setIsSavingDisplayName(false);
    }
  };

  const handleUsernameSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setErrors({});

    if (!isUsernameFormatValid) {
      setErrors({
        username:
          'Use 3–30 characters: letters, numbers, and underscores only.',
      });
      return;
    }

    if (usernameAvailability !== 'available') {
      setErrors({
        username:
          'Please enter an available username before continuing.',
      });
      return;
    }

    setIsSavingUsername(true);

    try {
      await apiRequest(
        '/api/accounts/onboarding/username/',
        {
          method: 'POST',
          body: JSON.stringify({
            username: trimmedUsername,
          }),
        },
      );

      await refreshAuth();

      setIsRedirecting(true);
      router.replace(nextPath);
    } catch (error) {
      const usernameError = getApiErrorMessage(
        error,
        'username',
      );

      setErrors({
        username: usernameError,
        general: usernameError
          ? undefined
          : getGeneralError(error),
      });

      if (usernameError) {
        setUsernameAvailability('unavailable');
        setAvailabilityMessage(usernameError);
      }
    } finally {
      setIsSavingUsername(false);
    }
  };

  const isBusy =
    isSavingDisplayName ||
    isSavingUsername ||
    isRedirecting;

  if (
    isLoading ||
    !isAuthenticated ||
    !user ||
    user.onboarding_completed ||
    isRedirecting
  ) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-light-bg px-4 dark:bg-dark-bg">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-7 w-7 animate-spin text-brand-teal" />

          <p className="text-sm text-light-text-muted dark:text-dark-text-muted">
            Preparing your account...
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-light-bg px-4 py-8 text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text sm:px-6 sm:py-12">
      <div className="mx-auto w-full max-w-2xl">
        {/* Header */}
        <div className="mb-10 flex items-center justify-between">
          <Link
            href="/"
            aria-label="VibeNationHQ home"
            className="inline-flex items-center"
          >
            <span className="text-xl font-black tracking-tight sm:text-2xl">
              VibeNation
              <span className="text-brand-teal">HQ</span>
            </span>
          </Link>

          <ThemeToggle />
        </div>

        {/* Main card */}
        <section
          className="
            overflow-hidden rounded-2xl
            border border-light-border
            bg-light-surface
            shadow-lg shadow-black/[0.03]
            dark:border-dark-border
            dark:bg-dark-surface
            dark:shadow-black/20
          "
        >
          <div className="p-5 sm:p-8 md:p-10">
            {/* Intro */}
            <div className="mb-8">
              <div
                className="
                  mb-5 flex h-12 w-12 items-center justify-center
                  rounded-xl
                  border border-brand-teal/20
                  bg-brand-teal/10
                  text-brand-teal
                  dark:border-brand-teal/30
                "
              >
                <ShieldCheck className="h-6 w-6" />
              </div>

              <p className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-brand-teal">
                Welcome to VibeNationHQ
              </p>

              <h1 className="text-2xl font-black tracking-tight sm:text-3xl">
                Let's set up your account.
              </h1>

              <p className="mt-3 max-w-lg text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                Just a couple of things before you get
                started. Set up your public identity so
                people can recognise you across VibeNationHQ.
              </p>
            </div>

            {/* Progress */}
            <div className="mb-9">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-semibold text-light-text-muted dark:text-dark-text-muted">
                  Account setup
                </span>

                <span className="text-xs font-bold text-brand-teal">
                  {step === 'display-name' ? 'Step 1 of 2' : 'Step 2 of 2'}
                </span>
              </div>

              <div className="flex gap-2">
                <div
                  className={`h-1.5 flex-1 rounded-full ${
                    step === 'display-name' ||
                    step === 'username'
                      ? 'bg-brand-teal'
                      : 'bg-light-border dark:bg-dark-border'
                  }`}
                />

                <div
                  className={`h-1.5 flex-1 rounded-full ${
                    step === 'username'
                      ? 'bg-brand-teal'
                      : 'bg-light-border dark:bg-dark-border'
                  }`}
                />
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2">
                  <div
                    className={`
                      flex h-7 w-7 shrink-0 items-center justify-center
                      rounded-full
                      ${
                        step === 'username'
                          ? 'bg-brand-teal text-white'
                          : 'bg-brand-teal/10 text-brand-teal'
                      }
                    `}
                  >
                    {step === 'username' ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <span className="text-xs font-bold">1</span>
                    )}
                  </div>

                  <span className="text-xs font-semibold">
                    Display name
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <div
                    className={`
                      flex h-7 w-7 shrink-0 items-center justify-center
                      rounded-full
                      ${
                        step === 'username'
                          ? 'bg-brand-teal text-white'
                          : 'bg-light-surface-muted text-light-text-soft dark:bg-dark-surface-muted dark:text-dark-text-soft'
                      }
                    `}
                  >
                    <span className="text-xs font-bold">2</span>
                  </div>

                  <span
                    className={`text-xs font-semibold ${
                      step === 'username'
                        ? 'text-light-text dark:text-dark-text'
                        : 'text-light-text-soft dark:text-dark-text-soft'
                    }`}
                  >
                    Username
                  </span>
                </div>
              </div>
            </div>

            {/* General error */}
            {errors.general && (
              <div
                role="alert"
                className="
                  mb-6 rounded-xl
                  border border-red-200
                  bg-red-50
                  px-4 py-3
                  text-sm leading-5 text-red-700
                  dark:border-red-500/20
                  dark:bg-red-500/10
                  dark:text-red-300
                "
              >
                {errors.general}
              </div>
            )}

            {/* Step 1: Display name */}
            {step === 'display-name' && (
              <form
                className="space-y-6"
                onSubmit={handleDisplayNameSubmit}
                noValidate
              >
                <div>
                  <label
                    htmlFor="display-name"
                    className="mb-2 block text-sm font-semibold"
                  >
                    What should we call you?
                  </label>

                  <div className="relative">
                    <UserRound
                      className="
                        pointer-events-none absolute left-3.5 top-1/2
                        h-5 w-5 -translate-y-1/2
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    />

                    <input
                      id="display-name"
                      name="display_name"
                      type="text"
                      autoComplete="name"
                      autoFocus
                      maxLength={100}
                      placeholder="Enter your display name"
                      value={displayName}
                      onChange={(event) => {
                        setDisplayName(event.target.value);

                        if (errors.display_name || errors.general) {
                          setErrors({});
                        }
                      }}
                      aria-invalid={Boolean(errors.display_name)}
                      aria-describedby={
                        errors.display_name
                          ? 'display-name-error'
                          : 'display-name-help'
                      }
                      className={`
                        h-12 w-full rounded-xl
                        border bg-light-surface-soft
                        pl-11 pr-4
                        text-sm text-light-text
                        placeholder:text-light-text-soft
                        outline-none transition-all
                        focus:border-brand-teal
                        focus:ring-4 focus:ring-brand-teal/10
                        dark:bg-dark-surface-soft
                        dark:text-dark-text
                        dark:placeholder:text-dark-text-soft
                        ${
                          errors.display_name
                            ? 'border-red-400 dark:border-red-500'
                            : 'border-light-border dark:border-dark-border'
                        }
                      `}
                    />
                  </div>

                  {errors.display_name ? (
                    <p
                      id="display-name-error"
                      className="mt-2 text-xs text-red-600 dark:text-red-400"
                    >
                      {errors.display_name}
                    </p>
                  ) : (
                    <p
                      id="display-name-help"
                      className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft"
                    >
                      This is the name other people will see
                      when you post, comment, or interact.
                    </p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isBusy || !displayName.trim()}
                  className="
                    flex h-12 w-full items-center justify-center gap-2
                    rounded-xl bg-brand-teal px-4
                    text-sm font-bold text-white
                    shadow-sm shadow-brand-teal/20
                    transition-all hover:bg-brand-teal-dark
                    active:scale-[0.99]
                    focus:outline-none focus:ring-4 focus:ring-brand-teal/20
                    disabled:cursor-not-allowed disabled:opacity-60
                  "
                >
                  {isSavingDisplayName ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </form>
            )}

            {/* Step 2: Username */}
            {step === 'username' && (
              <form
                className="space-y-6"
                onSubmit={handleUsernameSubmit}
                noValidate
              >
                <div>
                  <label
                    htmlFor="username"
                    className="mb-2 block text-sm font-semibold"
                  >
                    Choose your username
                  </label>

                  <div className="relative">
                    <AtSign
                      className="
                        pointer-events-none absolute left-3.5 top-1/2
                        h-5 w-5 -translate-y-1/2
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    />

                    <input
                      id="username"
                      name="username"
                      type="text"
                      autoComplete="username"
                      autoFocus
                      maxLength={30}
                      spellCheck={false}
                      autoCapitalize="none"
                      placeholder="yourusername"
                      value={username}
                      onChange={(event) => {
                        setUsername(event.target.value);

                        if (errors.username || errors.general) {
                          setErrors({});
                        }
                      }}
                      aria-invalid={Boolean(errors.username)}
                      aria-describedby="username-help"
                      className={`
                        h-12 w-full rounded-xl
                        border bg-light-surface-soft
                        pl-11 pr-4
                        text-sm text-light-text
                        placeholder:text-light-text-soft
                        outline-none transition-all
                        focus:border-brand-teal
                        focus:ring-4 focus:ring-brand-teal/10
                        dark:bg-dark-surface-soft
                        dark:text-dark-text
                        dark:placeholder:text-dark-text-soft
                        ${
                          errors.username
                            ? 'border-red-400 dark:border-red-500'
                            : 'border-light-border dark:border-dark-border'
                        }
                      `}
                    />
                  </div>

                  <p
                    id="username-help"
                    className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft"
                  >
                    Your username must be 3–30 characters.
                    Only letters, numbers, and underscores
                    are allowed.
                  </p>

                  {username.length > 0 && (
                    <div
                      className="mt-3 flex items-start gap-2 text-xs"
                      aria-live="polite"
                    >
                      {usernameAvailability === 'checking' && (
                        <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-light-text-soft dark:text-dark-text-soft" />
                      )}

                      {usernameAvailability === 'available' && (
                        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-600 dark:text-green-400" />
                      )}

                      {usernameAvailability === 'unavailable' && (
                        <AtSign className="mt-0.5 h-4 w-4 shrink-0 text-red-600 dark:text-red-400" />
                      )}

                      {usernameAvailability === 'error' && (
                        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400" />
                      )}

                      {usernameAvailability === 'idle' &&
                        !isUsernameFormatValid && (
                          <AtSign className="mt-0.5 h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />
                        )}

                      <span
                        className={
                          usernameAvailability === 'available'
                            ? 'text-green-700 dark:text-green-400'
                            : usernameAvailability === 'unavailable'
                              ? 'text-red-600 dark:text-red-400'
                              : usernameAvailability === 'error'
                                ? 'text-amber-700 dark:text-amber-400'
                                : 'text-light-text-muted dark:text-dark-text-muted'
                        }
                      >
                        {availabilityMessage}
                      </span>
                    </div>
                  )}

                  {errors.username && (
                    <p className="mt-2 text-xs text-red-600 dark:text-red-400">
                      {errors.username}
                    </p>
                  )}
                </div>

                {/* Username preview */}
                <div
                  className="
                    rounded-xl border border-light-border-soft
                    bg-light-surface-soft p-4
                    dark:border-dark-border-soft
                    dark:bg-dark-surface-soft
                  "
                >
                  <p className="mb-2 text-xs font-semibold text-light-text-muted dark:text-dark-text-muted">
                    Your public identity
                  </p>

                  <p className="text-sm font-bold">
                    {displayName.trim() || 'Your display name'}
                  </p>

                  <p className="mt-1 text-xs text-light-text-soft dark:text-dark-text-soft">
                    @{trimmedUsername || 'yourusername'}
                  </p>
                </div>

                <div className="flex flex-col-reverse gap-3 sm:flex-row">
                  <button
                    type="button"
                    disabled={isBusy}
                    onClick={() => {
                      setErrors({});
                      setStep('display-name');
                    }}
                    className="
                      flex h-12 items-center justify-center gap-2
                      rounded-xl border border-light-border
                      bg-light-surface px-5
                      text-sm font-semibold
                      transition-colors hover:bg-light-surface-soft
                      dark:border-dark-border
                      dark:bg-dark-surface-soft
                      dark:hover:bg-dark-surface-muted
                      disabled:opacity-60
                      sm:w-auto
                    "
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Back
                  </button>

                  <button
                    type="submit"
                    disabled={
                      isBusy ||
                      !isUsernameFormatValid ||
                      usernameAvailability !== 'available'
                    }
                    className="
                      flex h-12 flex-1 items-center justify-center gap-2
                      rounded-xl bg-brand-teal px-4
                      text-sm font-bold text-white
                      shadow-sm shadow-brand-teal/20
                      transition-all hover:bg-brand-teal-dark
                      active:scale-[0.99]
                      focus:outline-none focus:ring-4 focus:ring-brand-teal/20
                      disabled:cursor-not-allowed disabled:opacity-60
                    "
                  >
                    {isSavingUsername ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Finishing setup...
                      </>
                    ) : (
                      <>
                        Complete setup
                        <Check className="h-4 w-4" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}

            {/* Footer */}
            <div className="mt-8 border-t border-light-border-soft pt-5 dark:border-dark-border-soft">
              <p className="text-center text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                Your account details help people recognise
                you across VibeNationHQ. You can update
                your profile information later.
              </p>
            </div>
          </div>
        </section>

        <p className="mt-6 text-center text-xs text-light-text-soft dark:text-dark-text-soft">
          Need help?{' '}
          <Link
            href="/contact"
            className="font-semibold text-brand-teal hover:underline"
          >
            Contact us
          </Link>
        </p>
      </div>
    </main>
  );
}

export default function AccountSetupPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-light-bg dark:bg-dark-bg">
          <Loader2 className="h-7 w-7 animate-spin text-brand-teal" />
        </main>
      }
    >
      <AccountSetupContent />
    </Suspense>
  );
}