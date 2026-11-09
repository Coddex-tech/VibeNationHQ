'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  CheckCircleIcon,
  LockIcon,
  MailIcon,
  PhoneIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import { ApiError, apiRequest, getMediaUrl } from '@/lib/api';
import HomeNav from '@/components/special/HomeNav';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import ConfirmationModal from '@/components/ui/ConfirmationModal';

type CurrentUserResponse = {
  user: {
    id: string;
    email: string;
    username: string;
    display_name: string;
    bio: string;
    profile_image: string | null;
    is_active?: boolean;
    date_joined?: string;
    created_at?: string;
    phone?: {
      phone_number: string;
      is_verified: boolean;
      verified_at?: string | null;
    } | null;
  };
};

function getUserInitials(
  displayName: string,
  username: string,
): string {
  const name = displayName.trim();

  if (name) {
    const parts = name.split(/\s+/);

    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }

    return name.slice(0, 2).toUpperCase();
  }

  return username.slice(0, 2).toUpperCase();
}

export default function AccountPage() {
  const router = useRouter();

  const [user, setUser] =
    useState<CurrentUserResponse['user'] | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [isLogoutModalOpen, setIsLogoutModalOpen] =
    useState(false);

  const [isLoggingOut, setIsLoggingOut] =
    useState(false);

  const [logoutError, setLogoutError] =
    useState('');

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
              'Unable to load your account right now.',
          );
        } else {
          setError(
            'Unable to load your account right now.',
          );
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadAccount();
  }, []);

  const formatDate = (value?: string) => {
    if (!value) {
      return 'Not available';
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return 'Not available';
    }

    return new Intl.DateTimeFormat('en', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(date);
  };

  const formatPhoneNumber = (value: string) => {
    if (!value) {
      return '';
    }

    if (value.length <= 7) {
      return value;
    }

    return `${value.slice(0, 4)}••••${value.slice(-3)}`;
  };

  const openLogoutModal = () => {
    setLogoutError('');
    setIsLogoutModalOpen(true);
  };

  const closeLogoutModal = () => {
    if (isLoggingOut) {
      return;
    }

    setIsLogoutModalOpen(false);
    setLogoutError('');
  };

  const handleLogout = async () => {
    if (isLoggingOut) {
      return;
    }

    setLogoutError('');
    setIsLoggingOut(true);

    try {
      await apiRequest(
        '/api/accounts/logout/',
        {
          method: 'POST',
        },
      );

      setIsLogoutModalOpen(false);

      router.push('/login');
    } catch (error) {
      if (error instanceof ApiError) {
        setLogoutError(
          error.data?.detail ??
            'Unable to sign out right now. Please try again.',
        );
      } else {
        setLogoutError(
          'Unable to sign out right now. Please try again.',
        );
      }
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <ProtectedRoute>
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
            mx-auto w-full max-w-6xl
            px-4 py-8
            sm:px-6 sm:py-10
            lg:px-8 lg:py-12
          "
        >
          <FadeIn>
            <div className="max-w-2xl">
              <p
                className="
                  text-sm font-semibold
                  text-brand-teal-dark
                  dark:text-brand-teal-light
                "
              >
                Your account
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
                Account
              </h1>

              <p
                className="
                  mt-3 text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-base
                "
              >
                Manage your VibeNationHQ account,
                security, and personal information.
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
                <div className="animate-pulse">
                  <div
                    className="
                      h-6 w-40 rounded-lg
                      bg-light-surface-muted
                      dark:bg-dark-surface-muted
                    "
                  />

                  <div
                    className="
                      mt-4 h-4 w-64 rounded
                      bg-light-surface-muted
                      dark:bg-dark-surface-muted
                    "
                  />

                  <div
                    className="
                      mt-8 h-20 rounded-xl
                      bg-light-surface-soft
                      dark:bg-dark-surface-soft
                    "
                  />
                </div>
              </div>
            </FadeIn>
          ) : user ? (
            <div className="mt-8 grid gap-5 lg:grid-cols-[1.35fr_0.65fr]">
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
                      bg-light-surface-soft
                      px-5 py-5
                      dark:border-dark-border-soft
                      dark:bg-dark-surface-soft
                      sm:px-6
                    "
                  >
                    <div className="flex items-center gap-4">
                      {/* Profile picture */}
                      <div
                        className="
                          relative
                          h-16 w-16 shrink-0
                          overflow-hidden
                          rounded-full
                          border-2
                          border-light-border
                          bg-brand-teal/10
                          dark:border-dark-border
                          dark:bg-brand-teal/15
                        "
                      >
                        {user.profile_image ? (
                          <Image
                            src={getMediaUrl(user.profile_image)}
                            alt={`${user.display_name || user.username}'s profile picture`}
                            fill
                            sizes="64px"
                            className="object-cover"
                          />
                        ) : (
                          <div
                            className="
                              flex h-full w-full
                              items-center justify-center
                              text-xl font-black
                              text-brand-teal-dark
                              dark:text-brand-teal-light
                            "
                          >
                            {getUserInitials(
                              user.display_name,
                              user.username,
                            )}
                          </div>
                        )}
                      </div>

                      {/* Account identity */}
                      <div className="min-w-0">
                        <h2
                          className="
                            truncate text-lg font-bold
                            text-light-text
                            dark:text-dark-text
                          "
                        >
                          {user.display_name || user.username}
                        </h2>

                        <p
                          className="
                            mt-0.5 truncate text-sm
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          @{user.username}
                        </p>

                        <p
                          className="
                            mt-1 truncate text-sm
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          {user.email}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="divide-y divide-light-border-soft dark:divide-dark-border-soft">
                    {/* Email */}
                    <div className="flex items-start gap-4 px-5 py-5 sm:px-6">
                      <div
                        className="
                          flex h-10 w-10 shrink-0
                          items-center justify-center
                          rounded-xl
                          bg-light-surface-soft
                          text-light-text-muted
                          dark:bg-dark-surface-soft
                          dark:text-dark-text-muted
                        "
                      >
                        <MailIcon className="h-5 w-5" />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <p
                            className="
                              text-sm font-semibold
                              text-light-text
                              dark:text-dark-text
                            "
                          >
                            Email address
                          </p>

                          <span
                            className="
                              inline-flex items-center gap-1
                              rounded-full
                              bg-brand-teal/10
                              px-2 py-0.5
                              text-[11px] font-bold
                              text-brand-teal-dark
                              dark:bg-brand-teal/15
                              dark:text-brand-teal-light
                            "
                          >
                            <CheckCircleIcon className="h-3.5 w-3.5" />
                            Verified
                          </span>
                        </div>

                        <p
                          className="
                            mt-1 break-all text-sm
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          {user.email}
                        </p>
                      </div>
                    </div>

                    {/* Phone */}
                    <div className="flex items-start gap-4 px-5 py-5 sm:px-6">
                      <div
                        className="
                          flex h-10 w-10 shrink-0
                          items-center justify-center
                          rounded-xl
                          bg-light-surface-soft
                          text-light-text-muted
                          dark:bg-dark-surface-soft
                          dark:text-dark-text-muted
                        "
                      >
                        <PhoneIcon className="h-5 w-5" />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <p
                            className="
                              text-sm font-semibold
                              text-light-text
                              dark:text-dark-text
                            "
                          >
                            Phone number
                          </p>

                          {user.phone?.is_verified && (
                            <span
                              className="
                                inline-flex items-center gap-1
                                rounded-full
                                bg-brand-teal/10
                                px-2 py-0.5
                                text-[11px] font-bold
                                text-brand-teal-dark
                                dark:bg-brand-teal/15
                                dark:text-brand-teal-light
                              "
                            >
                              <CheckCircleIcon className="h-3.5 w-3.5" />
                              Verified
                            </span>
                          )}
                        </div>

                        <p
                          className="
                            mt-1 text-sm
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          {user.phone
                            ? formatPhoneNumber(
                                user.phone.phone_number,
                              )
                            : 'Not added'}
                        </p>
                      </div>
                    </div>

                    {/* Account status */}
                    <div className="flex items-start gap-4 px-5 py-5 sm:px-6">
                      <div
                        className="
                          flex h-10 w-10 shrink-0
                          items-center justify-center
                          rounded-xl
                          bg-light-surface-soft
                          text-light-text-muted
                          dark:bg-dark-surface-soft
                          dark:text-dark-text-muted
                        "
                      >
                        <ShieldCheckIcon className="h-5 w-5" />
                      </div>

                      <div className="min-w-0 flex-1">
                        <p
                          className="
                            text-sm font-semibold
                            text-light-text
                            dark:text-dark-text
                          "
                        >
                          Account status
                        </p>

                        <p
                          className="
                            mt-1 text-sm
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          {user.is_active === false
                            ? 'Inactive'
                            : 'Active'}
                        </p>
                      </div>
                    </div>

                    {/* Member since */}
                    <div className="flex items-start gap-4 px-5 py-5 sm:px-6">
                      <div
                        className="
                          flex h-10 w-10 shrink-0
                          items-center justify-center
                          rounded-xl
                          bg-light-surface-soft
                          text-light-text-muted
                          dark:bg-dark-surface-soft
                          dark:text-dark-text-muted
                        "
                      >
                        <LockIcon className="h-5 w-5" />
                      </div>

                      <div className="min-w-0 flex-1">
                        <p
                          className="
                            text-sm font-semibold
                            text-light-text
                            dark:text-dark-text
                          "
                        >
                          Member since
                        </p>

                        <p
                          className="
                            mt-1 text-sm
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          {formatDate(
                            user.date_joined ??
                              user.created_at,
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                </section>
              </FadeIn>

              <div className="space-y-5">
                <FadeIn>
                  <Link
                    href="/settings/security"
                    className="
                      group block
                      rounded-2xl
                      border border-light-border
                      bg-light-surface
                      p-5
                      shadow-sm shadow-black/[0.03]
                      transition-all duration-200
                      hover:-translate-y-0.5
                      hover:border-brand-teal/30
                      hover:shadow-md
                      dark:border-dark-border
                      dark:bg-dark-surface
                      dark:shadow-black/10
                      dark:hover:border-brand-teal/30
                      sm:p-6
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

                      <div className="min-w-0">
                        <h2
                          className="
                            text-base font-bold
                            text-light-text
                            dark:text-dark-text
                          "
                        >
                          Security
                        </h2>

                        <p
                          className="
                            mt-1 text-sm leading-5
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          Manage your password,
                          phone, email, Google connection,
                          and active sessions.
                        </p>

                        <span
                          className="
                            mt-4 inline-flex
                            text-xs font-bold
                            text-brand-teal-dark
                            transition-colors
                            group-hover:text-brand-teal
                            dark:text-brand-teal-light
                          "
                        >
                          Manage security
                        </span>
                      </div>
                    </div>
                  </Link>
                </FadeIn>

                <FadeIn>
                  <Link
                    href="/settings"
                    className="
                      group block
                      rounded-2xl
                      border border-light-border
                      bg-light-surface
                      p-5
                      shadow-sm shadow-black/[0.03]
                      transition-all duration-200
                      hover:-translate-y-0.5
                      hover:border-brand-teal/30
                      hover:shadow-md
                      dark:border-dark-border
                      dark:bg-dark-surface
                      dark:shadow-black/10
                      sm:p-6
                    "
                  >
                    <div className="flex items-start gap-4">
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
                        <LockIcon className="h-5 w-5" />
                      </div>

                      <div className="min-w-0">
                        <h2
                          className="
                            text-base font-bold
                            text-light-text
                            dark:text-dark-text
                          "
                        >
                          Settings
                        </h2>

                        <p
                          className="
                            mt-1 text-sm leading-5
                            text-light-text-muted
                            dark:text-dark-text-muted
                          "
                        >
                          Manage your account preferences
                          and VibeNationHQ experience.
                        </p>

                        <span
                          className="
                            mt-4 inline-flex
                            text-xs font-bold
                            text-brand-teal-dark
                            transition-colors
                            group-hover:text-brand-teal
                            dark:text-brand-teal-light
                          "
                        >
                          Open settings
                        </span>
                      </div>
                    </div>
                  </Link>
                </FadeIn>

                <FadeIn>
                  <button
                    type="button"
                    onClick={openLogoutModal}
                    className="
                      flex w-full items-center justify-center
                      rounded-xl
                      border border-light-border
                      bg-transparent
                      px-4 py-3
                      text-sm font-bold
                      text-light-text-muted
                      transition-all duration-200
                      hover:border-red-300
                      hover:bg-red-50
                      hover:text-red-600
                      focus:outline-none
                      focus:ring-4
                      focus:ring-red-500/10
                      dark:border-dark-border
                      dark:text-dark-text-muted
                      dark:hover:border-red-500/30
                      dark:hover:bg-red-500/10
                      dark:hover:text-red-400
                    "
                  >
                    Sign out
                  </button>
                </FadeIn>
              </div>
            </div>
          ) : null}
        </main>

        {/* Logout confirmation */}
        <ConfirmationModal
          open={isLogoutModalOpen}
          title="Log out of VibeNationHQ?"
          description={
            logoutError ||
            'You will be signed out of this browser. Your other active sessions will remain signed in.'
          }
          confirmLabel="Log out"
          cancelLabel="Cancel"
          destructive
          isLoading={isLoggingOut}
          onConfirm={handleLogout}
          onCancel={closeLogoutModal}
        />
      </div>
    </ProtectedRoute>
  );
}