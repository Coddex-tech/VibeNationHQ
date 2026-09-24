'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';

import FadeIn from '@/components/FadeIn';
import HomeNav from '@/components/special/HomeNav';
import {
  LockIcon,
  MailIcon,
  ShieldCheckIcon,
} from '@/components/Icons';

type ThemePreference =
  | 'system'
  | 'light'
  | 'dark';

export default function SettingsPage() {
  const {
    theme,
    resolvedTheme,
    setTheme,
  } = useTheme();

  const [mounted, setMounted] =
    useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const currentTheme: ThemePreference =
    theme === 'light' ||
    theme === 'dark' ||
    theme === 'system'
      ? theme
      : 'system';

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
            <p
              className="
                text-sm font-semibold
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              Account preferences
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
              Settings
            </h1>

            <p
              className="
                mt-3 text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
                sm:text-base
              "
            >
              Manage your VibeNationHQ preferences,
              account options, and experience.
            </p>
          </div>
        </FadeIn>

        <div className="mt-8 space-y-5">
          {/* Appearance */}
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
                  Appearance
                </h2>

                <p
                  className="
                    mt-1 text-sm leading-5
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Choose how VibeNationHQ should
                  appear across your devices.
                </p>
              </div>

              <div className="px-5 py-5 sm:px-6">
                <div
                  className="
                    flex flex-col gap-5
                    lg:flex-row
                    lg:items-center
                    lg:justify-between
                  "
                >
                  <div>
                    <p
                      className="
                        text-sm font-semibold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Theme
                    </p>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Use your system preference or
                      choose light or dark mode.
                    </p>

                    {mounted && (
                      <p
                        className="
                          mt-2 text-xs
                          text-light-text-soft
                          dark:text-dark-text-soft
                        "
                      >
                        Currently using{' '}
                        <span className="font-semibold">
                          {resolvedTheme === 'dark'
                            ? 'dark'
                            : 'light'}
                        </span>{' '}
                        mode.
                      </p>
                    )}
                  </div>

                  <div
                    className="
                      grid w-full grid-cols-3
                      rounded-xl
                      border border-light-border
                      bg-light-surface-soft
                      p-1
                      dark:border-dark-border
                      dark:bg-dark-surface-soft
                      lg:w-auto
                    "
                  >
                    <button
                      type="button"
                      onClick={() =>
                        setTheme('system')
                      }
                      aria-pressed={
                        currentTheme === 'system'
                      }
                      className={`
                        rounded-lg
                        px-3 py-2.5
                        text-sm font-semibold
                        transition-all duration-200
                        ${
                          currentTheme === 'system'
                            ? `
                              bg-light-surface
                              text-light-text
                              shadow-sm
                              dark:bg-dark-surface
                              dark:text-dark-text
                            `
                            : `
                              text-light-text-muted
                              hover:text-light-text
                              dark:text-dark-text-muted
                              dark:hover:text-dark-text
                            `
                        }
                      `}
                    >
                      System
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        setTheme('light')
                      }
                      aria-pressed={
                        currentTheme === 'light'
                      }
                      className={`
                        rounded-lg
                        px-3 py-2.5
                        text-sm font-semibold
                        transition-all duration-200
                        ${
                          currentTheme === 'light'
                            ? `
                              bg-light-surface
                              text-light-text
                              shadow-sm
                              dark:bg-dark-surface
                              dark:text-dark-text
                            `
                            : `
                              text-light-text-muted
                              hover:text-light-text
                              dark:text-dark-text-muted
                              dark:hover:text-dark-text
                            `
                        }
                      `}
                    >
                      Light
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        setTheme('dark')
                      }
                      aria-pressed={
                        currentTheme === 'dark'
                      }
                      className={`
                        rounded-lg
                        px-3 py-2.5
                        text-sm font-semibold
                        transition-all duration-200
                        ${
                          currentTheme === 'dark'
                            ? `
                              bg-light-surface
                              text-light-text
                              shadow-sm
                              dark:bg-dark-surface
                              dark:text-dark-text
                            `
                            : `
                              text-light-text-muted
                              hover:text-light-text
                              dark:text-dark-text-muted
                              dark:hover:text-dark-text
                            `
                        }
                      `}
                    >
                      Dark
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </FadeIn>

          {/* Account */}
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
                  Account
                </h2>

                <p
                  className="
                    mt-1 text-sm leading-5
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Manage your account information
                  and security.
                </p>
              </div>

              <div
                className="
                  divide-y
                  divide-light-border-soft
                  dark:divide-dark-border-soft
                "
              >
                <Link
                  href="/account"
                  className="
                    group flex items-center gap-4
                    px-5 py-5
                    transition-colors duration-200
                    hover:bg-light-surface-soft
                    dark:hover:bg-dark-surface-soft
                    sm:px-6
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
                    <MailIcon className="h-5 w-5" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <h3
                      className="
                        text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Account information
                    </h3>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      View your username, email,
                      account status, and membership
                      information.
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
                    Open
                  </span>
                </Link>

                <Link
                  href="/settings/security"
                  className="
                    group flex items-center gap-4
                    px-5 py-5
                    transition-colors duration-200
                    hover:bg-light-surface-soft
                    dark:hover:bg-dark-surface-soft
                    sm:px-6
                  "
                >
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

                  <div className="min-w-0 flex-1">
                    <h3
                      className="
                        text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Security
                    </h3>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Manage your password, email,
                      phone, Google connection, and
                      active sessions.
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
                    Open
                  </span>
                </Link>
              </div>
            </section>
          </FadeIn>

          {/* Notifications */}
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
                  Notifications
                </h2>

                <p
                  className="
                    mt-1 text-sm leading-5
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Control how VibeNationHQ keeps you
                  updated.
                </p>
              </div>

              <div className="px-5 py-5 sm:px-6">
                <div
                  className="
                    rounded-xl
                    border border-dashed
                    border-light-border
                    bg-light-surface-soft
                    px-4 py-4
                    dark:border-dark-border
                    dark:bg-dark-surface-soft
                  "
                >
                  <p
                    className="
                      text-sm font-semibold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Notification preferences
                  </p>

                  <p
                    className="
                      mt-1 text-sm leading-5
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Email and activity notification
                    controls will appear here when the
                    notification system is connected.
                  </p>
                </div>
              </div>
            </section>
          </FadeIn>

          {/* Support & legal */}
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
                  Support & legal
                </h2>

                <p
                  className="
                    mt-1 text-sm leading-5
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Help, privacy, and information about
                  using VibeNationHQ.
                </p>
              </div>

              <div
                className="
                  divide-y
                  divide-light-border-soft
                  dark:divide-dark-border-soft
                "
              >
                <Link
                  href="/contact"
                  className="
                    group flex items-center gap-4
                    px-5 py-5
                    transition-colors duration-200
                    hover:bg-light-surface-soft
                    dark:hover:bg-dark-surface-soft
                    sm:px-6
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
                    <MailIcon className="h-5 w-5" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <h3
                      className="
                        text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Help & support
                    </h3>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Contact the VibeNationHQ team
                      when you need assistance.
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
                    Open
                  </span>
                </Link>

                <Link
                  href="/privacy"
                  className="
                    group flex items-center gap-4
                    px-5 py-5
                    transition-colors duration-200
                    hover:bg-light-surface-soft
                    dark:hover:bg-dark-surface-soft
                    sm:px-6
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
                    <LockIcon className="h-5 w-5" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <h3
                      className="
                        text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Privacy
                    </h3>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Read how VibeNationHQ handles
                      your information.
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
                    Read
                  </span>
                </Link>

                <Link
                  href="/terms"
                  className="
                    group flex items-center gap-4
                    px-5 py-5
                    transition-colors duration-200
                    hover:bg-light-surface-soft
                    dark:hover:bg-dark-surface-soft
                    sm:px-6
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
                    <LockIcon className="h-5 w-5" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <h3
                      className="
                        text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Terms of service
                    </h3>

                    <p
                      className="
                        mt-1 text-sm leading-5
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Review the terms governing use
                      of VibeNationHQ.
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
                    Read
                  </span>
                </Link>
              </div>
            </section>
          </FadeIn>
        </div>
      </main>
    </div>
  );
}