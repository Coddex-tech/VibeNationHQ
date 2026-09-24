'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  AlertTriangleIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import ConfirmationModal from '@/components/ui/ConfirmationModal';
import HomeNav from '@/components/special/HomeNav';
import { ApiError, apiRequest } from '@/lib/api';

type UserSession = {
  id: string;
  device_name: string;
  user_agent: string;
  ip_address: string | null;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
  is_current: boolean;
};

type SessionListResponse = {
  sessions: UserSession[];
};

type RevokeAllSessionsResponse = {
  message: string;
  revoked_count: number;
};

type ConfirmationAction =
  | {
      type: 'single';
      session: UserSession;
    }
  | {
      type: 'all';
    }
  | null;

export default function ActiveSessionsPage() {
  const [sessions, setSessions] = useState<UserSession[]>(
    [],
  );

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] = useState('');

  const [revokingSessionId, setRevokingSessionId] =
    useState<string | null>(null);

  const [isRevokingOthers, setIsRevokingOthers] =
    useState(false);

  const [successMessage, setSuccessMessage] =
    useState('');

  const [confirmationAction, setConfirmationAction] =
    useState<ConfirmationAction>(null);

  const formatDate = (value: string) => {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return 'Unknown';
    }

    return new Intl.DateTimeFormat('en', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(date);
  };

  const formatLastActive = (value: string) => {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return 'Unknown';
    }

    const now = Date.now();

    const difference = Math.max(
      0,
      now - date.getTime(),
    );

    const seconds = Math.floor(
      difference / 1000,
    );

    if (seconds < 60) {
      return 'Just now';
    }

    const minutes = Math.floor(
      seconds / 60,
    );

    if (minutes < 60) {
      return `${minutes} minute${
        minutes === 1 ? '' : 's'
      } ago`;
    }

    const hours = Math.floor(
      minutes / 60,
    );

    if (hours < 24) {
      return `${hours} hour${
        hours === 1 ? '' : 's'
      } ago`;
    }

    const days = Math.floor(
      hours / 24,
    );

    if (days < 30) {
      return `${days} day${
        days === 1 ? '' : 's'
      } ago`;
    }

    return formatDate(value);
  };

  const loadSessions = async () => {
    setError('');
    setSuccessMessage('');

    try {
      const data =
        await apiRequest<SessionListResponse>(
          '/api/accounts/sessions/',
        );

      setSessions(data.sessions);
    } catch (error) {
      if (error instanceof ApiError) {
        setError(
          error.data?.detail ??
            'Unable to load your active sessions.',
        );
      } else {
        setError(
          'Unable to load your active sessions.',
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleRevoke = async (
    session: UserSession,
  ) => {
    setError('');
    setSuccessMessage('');
    setRevokingSessionId(session.id);

    try {
      await apiRequest<{
        message: string;
      }>(
        `/api/accounts/sessions/${session.id}/`,
        {
          method: 'DELETE',
        },
      );

      setSessions((currentSessions) =>
        currentSessions.filter(
          (item) => item.id !== session.id,
        ),
      );

      setSuccessMessage(
        'The session was signed out successfully.',
      );
    } catch (error) {
      if (error instanceof ApiError) {
        setError(
          error.data?.detail ??
            'Unable to revoke this session.',
        );
      } else {
        setError(
          'Unable to revoke this session.',
        );
      }
    } finally {
      setRevokingSessionId(null);
    }
  };

  const handleRevokeOthers = async () => {
    const otherSessions = sessions.filter(
      (session) => !session.is_current,
    );

    if (otherSessions.length === 0) {
      return;
    }

    setError('');
    setSuccessMessage('');
    setIsRevokingOthers(true);

    try {
      const data =
        await apiRequest<RevokeAllSessionsResponse>(
          '/api/accounts/sessions/revoke-others/',
          {
            method: 'POST',
          },
        );

      setSessions((currentSessions) =>
        currentSessions.filter(
          (session) => session.is_current,
        ),
      );

      setSuccessMessage(
        data.revoked_count === 1
          ? '1 other session was signed out successfully.'
          : `${data.revoked_count} other sessions were signed out successfully.`,
      );
    } catch (error) {
      if (error instanceof ApiError) {
        setError(
          error.data?.detail ??
            'Unable to sign out the other sessions.',
        );
      } else {
        setError(
          'Unable to sign out the other sessions.',
        );
      }
    } finally {
      setIsRevokingOthers(false);
    }
  };

  const openSingleRevokeConfirmation = (
    session: UserSession,
  ) => {
    setError('');
    setSuccessMessage('');

    setConfirmationAction({
      type: 'single',
      session,
    });
  };

  const openRevokeOthersConfirmation = () => {
    const hasOtherSessions = sessions.some(
      (session) => !session.is_current,
    );

    if (!hasOtherSessions) {
      return;
    }

    setError('');
    setSuccessMessage('');

    setConfirmationAction({
      type: 'all',
    });
  };

  const closeConfirmation = () => {
    if (
      revokingSessionId !== null ||
      isRevokingOthers
    ) {
      return;
    }

    setConfirmationAction(null);
  };

  const handleConfirmAction = async () => {
    if (!confirmationAction) {
      return;
    }

    const action = confirmationAction;

    setConfirmationAction(null);

    if (action.type === 'single') {
      await handleRevoke(action.session);
      return;
    }

    await handleRevokeOthers();
  };

  const hasOtherSessions = sessions.some(
    (session) => !session.is_current,
  );

  const isConfirmationBusy =
    revokingSessionId !== null ||
    isRevokingOthers;

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
          <div className="max-w-3xl">
            <Link
              href="/settings/security"
              className="
                inline-flex items-center gap-2
                text-sm font-semibold
                text-brand-teal-dark
                transition-colors
                hover:text-brand-teal
                dark:text-brand-teal-light
              "
            >
              <ArrowLeftIcon className="h-4 w-4" />
              Security
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
              Active sessions
            </h1>

            <p
              className="
                mt-3 text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
                sm:text-base
              "
            >
              Review the devices and browsers
              currently signed in to your
              VibeNationHQ account.
            </p>
          </div>
        </FadeIn>

        {error && (
          <FadeIn className="mt-8">
            <div
              role="alert"
              className="
                flex items-start gap-3
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
              <AlertTriangleIcon
                className="
                  mt-0.5 h-5 w-5 shrink-0
                "
              />

              <p>{error}</p>
            </div>
          </FadeIn>
        )}

        {successMessage && (
          <FadeIn className="mt-8">
            <div
              role="status"
              className="
                flex items-start gap-3
                rounded-xl
                border border-brand-teal/20
                bg-brand-teal/5
                px-4 py-3.5
                text-sm leading-6
                text-brand-teal-dark
                dark:border-brand-teal/20
                dark:bg-brand-teal/10
                dark:text-brand-teal-light
              "
            >
              <CheckCircleIcon
                className="
                  mt-0.5 h-5 w-5 shrink-0
                "
              />

              <p>{successMessage}</p>
            </div>
          </FadeIn>
        )}

        {isLoading ? (
          <FadeIn className="mt-8">
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
                <div className="animate-pulse">
                  <div
                    className="
                      h-5 w-32 rounded
                      bg-light-surface-muted
                      dark:bg-dark-surface-muted
                    "
                  />

                  <div
                    className="
                      mt-2 h-4 w-64 max-w-full
                      rounded
                      bg-light-surface-soft
                      dark:bg-dark-surface-soft
                    "
                  />
                </div>
              </div>

              <div className="divide-y divide-light-border-soft dark:divide-dark-border-soft">
                {[1, 2].map((item) => (
                  <div
                    key={item}
                    className="
                      animate-pulse
                      px-5 py-6
                      sm:px-6
                    "
                  >
                    <div className="flex items-start gap-4">
                      <div
                        className="
                          h-11 w-11 shrink-0
                          rounded-xl
                          bg-light-surface-muted
                          dark:bg-dark-surface-muted
                        "
                      />

                      <div className="min-w-0 flex-1">
                        <div
                          className="
                            h-4 w-40 max-w-full rounded
                            bg-light-surface-muted
                            dark:bg-dark-surface-muted
                          "
                        />

                        <div
                          className="
                            mt-2 h-3 w-56 max-w-full rounded
                            bg-light-surface-soft
                            dark:bg-dark-surface-soft
                          "
                        />

                        <div
                          className="
                            mt-4 h-3 w-48 max-w-full rounded
                            bg-light-surface-soft
                            dark:bg-dark-surface-soft
                          "
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </FadeIn>
        ) : (
          <FadeIn className="mt-8">
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
                <div
                  className="
                    flex flex-col gap-4
                    sm:flex-row
                    sm:items-center
                    sm:justify-between
                  "
                >
                  <div className="min-w-0">
                    <h2
                      className="
                        text-base font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Signed-in devices
                    </h2>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      {sessions.length === 1
                        ? '1 active session'
                        : `${sessions.length} active sessions`}
                    </p>
                  </div>

                  <div
                    className="
                      flex w-full flex-col
                      items-stretch gap-2
                      sm:w-auto sm:flex-row
                      sm:items-center
                    "
                  >
                    {hasOtherSessions && (
                      <button
                        type="button"
                        onClick={
                          openRevokeOthersConfirmation
                        }
                        disabled={
                          isRevokingOthers ||
                          revokingSessionId !== null
                        }
                        className="
                          inline-flex min-h-10
                          w-full
                          items-center justify-center
                          rounded-lg
                          border border-red-200
                          bg-red-50
                          px-3.5 py-2
                          text-xs font-bold
                          text-red-700
                          transition-all duration-200
                          hover:border-red-300
                          hover:bg-red-100
                          disabled:cursor-not-allowed
                          disabled:opacity-60
                          sm:w-auto
                          dark:border-red-500/20
                          dark:bg-red-500/10
                          dark:text-red-300
                          dark:hover:bg-red-500/15
                        "
                      >
                        {isRevokingOthers
                          ? 'Signing out...'
                          : 'Sign out all other sessions'}
                      </button>
                    )}

                    <div
                      className="
                        inline-flex w-fit
                        items-center gap-2
                        self-start
                        rounded-full
                        bg-brand-teal/10
                        px-3 py-1.5
                        text-xs font-bold
                        text-brand-teal-dark
                        dark:bg-brand-teal/15
                        dark:text-brand-teal-light
                        sm:self-auto
                      "
                    >
                      <ShieldCheckIcon className="h-3.5 w-3.5" />
                      Account protected
                    </div>
                  </div>
                </div>
              </div>

              {sessions.length === 0 ? (
                <div
                  className="
                    px-5 py-12 text-center
                    sm:px-6 sm:py-14
                  "
                >
                  <div
                    className="
                      mx-auto flex h-12 w-12
                      items-center justify-center
                      rounded-xl
                      bg-light-surface-soft
                      text-light-text-muted
                      dark:bg-dark-surface-soft
                      dark:text-dark-text-muted
                    "
                  >
                    <ShieldCheckIcon className="h-6 w-6" />
                  </div>

                  <h3
                    className="
                      mt-4 text-base font-bold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    No active sessions
                  </h3>

                  <p
                    className="
                      mx-auto mt-2 max-w-md
                      text-sm leading-6
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    There are currently no active
                    sessions connected to your
                    account.
                  </p>
                </div>
              ) : (
                <div
                  className="
                    divide-y
                    divide-light-border-soft
                    dark:divide-dark-border-soft
                  "
                >
                  {sessions.map((session) => (
                    <article
                      key={session.id}
                      className="px-5 py-6 sm:px-6"
                    >
                      <div
                        className="
                          flex flex-col gap-5
                          sm:flex-row
                          sm:items-start
                        "
                      >
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
                          <ShieldCheckIcon className="h-5 w-5" />
                        </div>

                        <div className="min-w-0 flex-1">
                          <div
                            className="
                              flex flex-wrap
                              items-center gap-2
                            "
                          >
                            <h3
                              className="
                                min-w-0 break-words
                                text-sm font-bold
                                text-light-text
                                dark:text-dark-text
                              "
                            >
                              {session.device_name ||
                                'Unknown device'}
                            </h3>

                            {session.is_current && (
                              <span
                                className="
                                  inline-flex shrink-0
                                  items-center gap-1
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
                                Current session
                              </span>
                            )}
                          </div>

                          <p
                            className="
                              mt-1 break-words
                              text-xs leading-5
                              text-light-text-soft
                              dark:text-dark-text-soft
                            "
                          >
                            {session.user_agent ||
                              'Browser information unavailable'}
                          </p>

                          <div
                            className="
                              mt-5 grid gap-4
                              text-sm
                              sm:grid-cols-2
                            "
                          >
                            <div className="min-w-0">
                              <p
                                className="
                                  text-[11px]
                                  font-semibold uppercase
                                  tracking-wide
                                  text-light-text-soft
                                  dark:text-dark-text-soft
                                "
                              >
                                Last active
                              </p>

                              <p
                                className="
                                  mt-1 break-words font-medium
                                  text-light-text
                                  dark:text-dark-text
                                "
                              >
                                {formatLastActive(
                                  session.last_seen_at,
                                )}
                              </p>
                            </div>

                            <div className="min-w-0">
                              <p
                                className="
                                  text-[11px]
                                  font-semibold uppercase
                                  tracking-wide
                                  text-light-text-soft
                                  dark:text-dark-text-soft
                                "
                              >
                                Signed in
                              </p>

                              <p
                                className="
                                  mt-1 break-words font-medium
                                  text-light-text
                                  dark:text-dark-text
                                "
                              >
                                {formatDate(
                                  session.created_at,
                                )}
                              </p>
                            </div>

                            {session.ip_address && (
                              <div className="min-w-0">
                                <p
                                  className="
                                    text-[11px]
                                    font-semibold uppercase
                                    tracking-wide
                                    text-light-text-soft
                                    dark:text-dark-text-soft
                                  "
                                >
                                  IP address
                                </p>

                                <p
                                  className="
                                    mt-1 break-all font-medium
                                    text-light-text
                                    dark:text-dark-text
                                  "
                                >
                                  {session.ip_address}
                                </p>
                              </div>
                            )}

                            <div className="min-w-0">
                              <p
                                className="
                                  text-[11px]
                                  font-semibold uppercase
                                  tracking-wide
                                  text-light-text-soft
                                  dark:text-dark-text-soft
                                "
                              >
                                Expires
                              </p>

                              <p
                                className="
                                  mt-1 break-words font-medium
                                  text-light-text
                                  dark:text-dark-text
                                "
                              >
                                {formatDate(
                                  session.expires_at,
                                )}
                              </p>
                            </div>
                          </div>

                          {!session.is_current && (
                            <div className="mt-5">
                              <button
                                type="button"
                                onClick={() =>
                                  openSingleRevokeConfirmation(
                                    session,
                                  )
                                }
                                disabled={
                                  revokingSessionId ===
                                    session.id ||
                                  isRevokingOthers
                                }
                                className="
                                  inline-flex min-h-10
                                  w-full
                                  items-center justify-center
                                  rounded-lg
                                  border border-red-200
                                  bg-red-50
                                  px-4 py-2
                                  text-xs font-bold
                                  text-red-700
                                  transition-all duration-200
                                  hover:border-red-300
                                  hover:bg-red-100
                                  disabled:cursor-not-allowed
                                  disabled:opacity-60
                                  sm:w-auto
                                  dark:border-red-500/20
                                  dark:bg-red-500/10
                                  dark:text-red-300
                                  dark:hover:bg-red-500/15
                                "
                              >
                                {revokingSessionId ===
                                session.id
                                  ? 'Signing out...'
                                  : 'Sign out'}
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </FadeIn>
        )}

        <FadeIn className="mt-6">
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

              <div className="min-w-0">
                <p
                  className="
                    text-sm font-bold
                    text-light-text
                    dark:text-dark-text
                  "
                >
                  Don't recognize a session?
                </p>

                <p
                  className="
                    mt-1 text-sm leading-5
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Sign it out immediately. If you
                  believe someone else has access to
                  your account, change your password
                  afterward.
                </p>
              </div>
            </div>
          </div>
        </FadeIn>
      </main>

      <ConfirmationModal
        open={confirmationAction !== null}
        title={
          confirmationAction?.type === 'all'
            ? 'Sign out other sessions?'
            : 'Sign out this session?'
        }
        description={
          confirmationAction?.type === 'all'
            ? 'This will sign out your account from all other devices and browsers. Your current session will remain active.'
            : `This will sign out ${
                confirmationAction?.session.device_name ||
                'this device'
              } from your VibeNationHQ account.`
        }
        confirmLabel={
          confirmationAction?.type === 'all'
            ? 'Sign out all'
            : 'Sign out'
        }
        destructive
        isLoading={isConfirmationBusy}
        onConfirm={handleConfirmAction}
        onCancel={closeConfirmation}
      >
        {confirmationAction?.type === 'single' && (
          <div
            className="
              rounded-xl
              border border-light-border-soft
              bg-light-surface-soft
              px-4 py-3
              dark:border-dark-border-soft
              dark:bg-dark-surface-soft
            "
          >
            <p
              className="
                text-xs font-semibold
                text-light-text-muted
                dark:text-dark-text-muted
              "
            >
              Device
            </p>

            <p
              className="
                mt-1 break-words
                text-sm font-semibold
                text-light-text
                dark:text-dark-text
              "
            >
              {confirmationAction.session
                .device_name || 'Unknown device'}
            </p>
          </div>
        )}
      </ConfirmationModal>
    </div>
  );
}