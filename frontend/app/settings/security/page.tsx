'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  CheckCircleIcon,
  LockIcon,
  MailIcon,
  PhoneIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';
import HomeNav from '@/components/special/HomeNav';

type CurrentUserResponse = {
  user: {
    id: string;
    email: string;
    username: string;
    is_active?: boolean;
    phone?: {
      phone_number: string;
      is_verified: boolean;
      verified_at?: string | null;
    } | null;
  };
};

type SecurityRowProps = {
  icon: React.ReactNode;
  title: string;
  description: string;
  status?: string;
  statusTone?: 'success' | 'neutral';
  actionLabel?: string;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
};

function SecurityRow({
  icon,
  title,
  description,
  status,
  statusTone = 'neutral',
  actionLabel,
  href,
  onClick,
  disabled = false,
}: SecurityRowProps) {
  const content = (
    <>
      <div
        className="
          flex h-11 w-11 shrink-0
          items-center justify-center
          rounded-xl
          bg-light-surface-soft
          text-light-text-muted
          dark:bg-dark-surface-soft
          dark:text-dark-text-muted
        "
      >
        {icon}
      </div>

      <div className="min-w-0 flex-1">
        <div
          className="
            flex flex-wrap items-center gap-2
          "
        >
          <h3
            className="
              text-sm font-bold
              text-light-text
              dark:text-dark-text
            "
          >
            {title}
          </h3>

          {status && (
            <span
              className={`
                inline-flex items-center gap-1
                rounded-full
                px-2 py-0.5
                text-[11px] font-bold
                ${
                  statusTone === 'success'
                    ? `
                      bg-brand-teal/10
                      text-brand-teal-dark
                      dark:bg-brand-teal/15
                      dark:text-brand-teal-light
                    `
                    : `
                      bg-light-surface-muted
                      text-light-text-muted
                      dark:bg-dark-surface-muted
                      dark:text-dark-text-muted
                    `
                }
              `}
            >
              {statusTone === 'success' && (
                <CheckCircleIcon className="h-3.5 w-3.5" />
              )}

              {status}
            </span>
          )}
        </div>

        <p
          className="
            mt-1 text-sm leading-5
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {description}
        </p>
      </div>

      {actionLabel && (
        <span
          className="
            shrink-0
            text-xs font-bold
            text-brand-teal-dark
            dark:text-brand-teal-light
          "
        >
          {actionLabel}
        </span>
      )}
    </>
  );

  if (href && !disabled) {
    return (
      <Link
        href={href}
        className="
          group flex items-center gap-4
          px-5 py-5
          transition-colors duration-200
          hover:bg-light-surface-soft
          dark:hover:bg-dark-surface-soft
          sm:px-6
        "
      >
        {content}
      </Link>
    );
  }

  if (onClick && !disabled) {
    return (
      <button
        type="button"
        onClick={onClick}
        className="
          group flex w-full items-center gap-4
          px-5 py-5 text-left
          transition-colors duration-200
          hover:bg-light-surface-soft
          dark:hover:bg-dark-surface-soft
          sm:px-6
        "
      >
        {content}
      </button>
    );
  }

  return (
    <div
      className="
        flex items-center gap-4
        px-5 py-5
        sm:px-6
      "
    >
      {content}
    </div>
  );
}

export default function SecuritySettingsPage() {
  const [user, setUser] =
    useState<CurrentUserResponse['user'] | null>(
      null,
    );

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] = useState('');

  useEffect(() => {
    const loadAccount = async () => {
      try {
        const data =
          await apiRequest<CurrentUserResponse>(
            '/api/accounts/me/',
          );

        setUser(data.user);
      } catch (error) {
        if (error instanceof ApiError) {
          setError(
            error.data?.detail ??
              'Unable to load your security settings.',
          );
        } else {
          setError(
            'Unable to load your security settings.',
          );
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadAccount();
  }, []);

  const formatPhoneNumber = (value: string) => {
    if (!value) {
      return '';
    }

    if (value.length <= 7) {
      return value;
    }

    return `${value.slice(0, 4)}••••${value.slice(-3)}`;
  };

  const hasVerifiedPhone =
    user?.phone?.is_verified === true;

  return (
    <div
      className="
        min-h-screen
        bg-light-bg
        text-light-text
        transition-colors duration-300
        dark:bg-dark-bg
        dark:text-dark-text
      "
    >
      <HomeNav />

      <main
        className="
          mx-auto w-full max-w-5xl
          px-4 py-8
          sm:px-6 sm:py-10
          lg:px-8 lg:py-12
        "
      >
        <FadeIn>
          <div className="max-w-2xl">
            <Link
              href="/settings"
              className="
                inline-flex items-center
                text-sm font-semibold
                text-brand-teal-dark
                transition-colors
                hover:text-brand-teal
                dark:text-brand-teal-light
              "
            >
              ← Settings
            </Link>

            <p
              className="
                mt-5 text-sm font-semibold
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              Account security
            </p>

            <h1
              className="
                mt-2
                text-3xl font-black tracking-tight
                text-light-text
                dark:text-dark-text
                sm:text-4xl
              "
            >
              Security
            </h1>

            <p
              className="
                mt-3 text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
                sm:text-base
              "
            >
              Protect your VibeNationHQ account and
              manage the credentials and sessions
              connected to it.
            </p>
          </div>
        </FadeIn>

        {error && (
          <FadeIn className="mt-8">
            <div
              role="alert"
              className="
                rounded-xl
                border border-red-200
                bg-red-50
                px-4 py-3.5
                text-sm leading-6
                text-red-700
                dark:border-red-500/20
                dark:bg-red-500/10
                dark:text-red-300
              "
            >
              {error}
            </div>
          </FadeIn>
        )}

        {isLoading ? (
          <FadeIn className="mt-8">
            <div
              className="
                rounded-2xl
                border border-light-border
                bg-light-surface
                p-6
                dark:border-dark-border
                dark:bg-dark-surface
                sm:p-8
              "
            >
              <div className="animate-pulse space-y-5">
                <div
                  className="
                    h-5 w-36 rounded
                    bg-light-surface-muted
                    dark:bg-dark-surface-muted
                  "
                />

                <div
                  className="
                    h-14 rounded-xl
                    bg-light-surface-soft
                    dark:bg-dark-surface-soft
                  "
                />

                <div
                  className="
                    h-14 rounded-xl
                    bg-light-surface-soft
                    dark:bg-dark-surface-soft
                  "
                />

                <div
                  className="
                    h-14 rounded-xl
                    bg-light-surface-soft
                    dark:bg-dark-surface-soft
                  "
                />
              </div>
            </div>
          </FadeIn>
        ) : user ? (
          <div className="mt-8 space-y-5">
            {/* Login & credentials */}
            <FadeIn>
              <section
                className="
                  overflow-hidden
                  rounded-2xl
                  border border-light-border
                  bg-light-surface
                  shadow-sm shadow-black/[0.03]
                  dark:border-dark-border
                  dark:bg-dark-surface
                  dark:shadow-black/10
                "
              >
                <div
                  className="
                    border-b
                    border-light-border-soft
                    px-5 py-5
                    sm:px-6
                  "
                >
                  <div className="flex items-start gap-4">
                    <div
                      className="
                        flex h-11 w-11 shrink-0
                        items-center justify-center
                        rounded-xl
                        bg-brand-teal/10
                        text-brand-teal
                        dark:bg-brand-teal/15
                      "
                    >
                      <ShieldCheckIcon className="h-5 w-5" />
                    </div>

                    <div>
                      <h2
                        className="
                          text-base font-bold
                          text-light-text
                          dark:text-dark-text
                        "
                      >
                        Login & credentials
                      </h2>

                      <p
                        className="
                          mt-1 text-sm leading-5
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        Manage the credentials you use
                        to access your account.
                      </p>
                    </div>
                  </div>
                </div>

                <div
                  className="
                    divide-y
                    divide-light-border-soft
                    dark:divide-dark-border-soft
                  "
                >
                  <SecurityRow
                    icon={
                      <MailIcon className="h-5 w-5" />
                    }
                    title="Email address"
                    description={user.email}
                    status="Verified"
                    statusTone="success"
                    actionLabel="Change"
                    href="/settings/security/email"
                  />

                  <SecurityRow
                    icon={
                      <LockIcon className="h-5 w-5" />
                    }
                    title="Password"
                    description="Your password is used to securely sign in to VibeNationHQ."
                    actionLabel="Change"
                    href="/settings/security/password"
                  />
                </div>
              </section>
            </FadeIn>

            {/* Recovery */}
            <FadeIn>
              <section
                className="
                  overflow-hidden
                  rounded-2xl
                  border border-light-border
                  bg-light-surface
                  shadow-sm shadow-black/[0.03]
                  dark:border-dark-border
                  dark:bg-dark-surface
                  dark:shadow-black/10
                "
              >
                <div
                  className="
                    border-b
                    border-light-border-soft
                    px-5 py-5
                    sm:px-6
                  "
                >
                  <h2
                    className="
                      text-base font-bold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Recovery & verification
                  </h2>

                  <p
                    className="
                      mt-1 text-sm leading-5
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Add additional ways to verify
                    important account changes.
                  </p>
                </div>

                <div
                  className="
                    divide-y
                    divide-light-border-soft
                    dark:divide-dark-border-soft
                  "
                >
                  <SecurityRow
                    icon={
                      <MailIcon className="h-5 w-5" />
                    }
                    title="Email verification"
                    description="Your email address is verified and can be used for account recovery."
                    status="Verified"
                    statusTone="success"
                  />

                  {hasVerifiedPhone ? (
                    <SecurityRow
                      icon={
                        <PhoneIcon className="h-5 w-5" />
                      }
                      title="Phone number"
                      description={formatPhoneNumber(
                        user.phone!.phone_number,
                      )}
                      status="Verified"
                      statusTone="success"
                      actionLabel="Change"
                      href="/settings/security/phone/change"
                    />
                  ) : (
                    <SecurityRow
                      icon={
                        <PhoneIcon className="h-5 w-5" />
                      }
                      title="Phone number"
                      description="Add a verified phone number for additional account recovery and security."
                      status="Not added"
                      statusTone="neutral"
                      actionLabel="Add"
                      href="/settings/security/phone"
                    />
                  )}

                  <SecurityRow
                    icon={
                      <ShieldCheckIcon className="h-5 w-5" />
                    }
                    title="Google"
                    description="Connect your Google account for another sign-in method."
                    status="Not connected"
                    statusTone="neutral"
                    actionLabel="Connect"
                  />
                </div>
              </section>
            </FadeIn>

            {/* Sessions */}
            <FadeIn>
              <section
                className="
                  overflow-hidden
                  rounded-2xl
                  border border-light-border
                  bg-light-surface
                  shadow-sm shadow-black/[0.03]
                  dark:border-dark-border
                  dark:bg-dark-surface
                  dark:shadow-black/10
                "
              >
                <div
                  className="
                    border-b
                    border-light-border-soft
                    px-5 py-5
                    sm:px-6
                  "
                >
                  <h2
                    className="
                      text-base font-bold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Active sessions
                  </h2>

                  <p
                    className="
                      mt-1 text-sm leading-5
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Review where your account is
                    currently signed in and revoke
                    sessions you don't recognize.
                  </p>
                </div>

                <div className="px-5 py-5 sm:px-6">
                  <Link
                    href="/settings/security/sessions"
                    className="
                      group flex items-center gap-4
                      rounded-xl
                      border border-light-border
                      bg-light-surface-soft
                      px-4 py-4
                      transition-all duration-200
                      hover:border-brand-teal/30
                      hover:bg-light-surface
                      dark:border-dark-border
                      dark:bg-dark-surface-soft
                      dark:hover:border-brand-teal/30
                      dark:hover:bg-dark-surface
                    "
                  >
                    <div
                      className="
                        flex h-10 w-10 shrink-0
                        items-center justify-center
                        rounded-xl
                        bg-light-surface
                        text-light-text-muted
                        dark:bg-dark-surface
                        dark:text-dark-text-muted
                      "
                    >
                      <ShieldCheckIcon className="h-5 w-5" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p
                        className="
                          text-sm font-bold
                          text-light-text
                          dark:text-dark-text
                        "
                      >
                        Manage active sessions
                      </p>

                      <p
                        className="
                          mt-1 text-sm leading-5
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        View devices and sign out
                        sessions remotely.
                      </p>
                    </div>

                    <span
                      className="
                        hidden shrink-0
                        text-xs font-bold
                        text-brand-teal-dark
                        group-hover:text-brand-teal
                        dark:text-brand-teal-light
                        sm:block
                      "
                    >
                      Manage
                    </span>
                  </Link>
                </div>
              </section>
            </FadeIn>

            {/* Security note */}
            <FadeIn>
              <div
                className="
                  rounded-2xl
                  border border-brand-teal/20
                  bg-brand-teal/5
                  px-5 py-5
                  dark:border-brand-teal/20
                  dark:bg-brand-teal/10
                  sm:px-6
                "
              >
                <div className="flex items-start gap-3">
                  <ShieldCheckIcon
                    className="
                      mt-0.5 h-5 w-5 shrink-0
                      text-brand-teal
                    "
                  />

                  <div>
                    <p
                      className="
                        text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Keep your account secure
                    </p>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Never share your password or
                      verification codes with anyone.
                      VibeNationHQ support will never
                      ask you to send them your password.
                    </p>
                  </div>
                </div>
              </div>
            </FadeIn>
          </div>
        ) : null}
      </main>
    </div>
  );
}