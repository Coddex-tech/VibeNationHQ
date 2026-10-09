'use client';

import Link from 'next/link';

import FadeIn from '@/components/FadeIn';
import {
  ArrowRightIcon,
  MusicIcon,
  NewsIcon,
  SearchIcon,
} from '@/components/Icons';
import { useAuth } from '@/components/auth/AuthProvider';

export default function HomeHero() {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  return (
    <section
      aria-labelledby="home-hero-heading"
      className="
        relative overflow-hidden
        border-b border-light-border
        bg-light-bg
        dark:border-dark-border
        dark:bg-dark-bg
      "
    >
      {/* Subtle background detail */}
      <div
        aria-hidden="true"
        className="
          pointer-events-none absolute
          -right-32 -top-32
          h-80 w-80
          rounded-full
          bg-brand-teal/[0.07]
          blur-3xl
          dark:bg-brand-teal/[0.08]
        "
      />

      <div
        aria-hidden="true"
        className="
          pointer-events-none absolute
          -bottom-40 -left-32
          h-80 w-80
          rounded-full
          bg-cyan-500/[0.04]
          blur-3xl
          dark:bg-cyan-400/[0.05]
        "
      />

      <div
        className="
          relative mx-auto w-full max-w-7xl
          px-5 py-14
          sm:px-6 sm:py-20
          lg:px-8 lg:py-24
        "
      >
        <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:gap-16">
          {/* Main introduction */}
          <FadeIn>
            <div className="max-w-3xl">
              {/* Eyebrow */}
              <div
                className="
                  mb-6 inline-flex items-center gap-2
                  rounded-full
                  border border-brand-teal/20
                  bg-brand-teal/10
                  px-3.5 py-2
                  text-xs font-bold
                  text-brand-teal-dark
                  dark:border-brand-teal/30
                  dark:bg-brand-teal/10
                  dark:text-brand-teal-light
                "
              >
                <span
                  aria-hidden="true"
                  className="
                    h-1.5 w-1.5
                    rounded-full
                    bg-brand-teal
                  "
                />

                Entertainment. Music. Media.
              </div>

              <h1
                id="home-hero-heading"
                className="
                  max-w-3xl
                  text-4xl font-black leading-[1.05]
                  tracking-[-0.03em]
                  text-light-text
                  dark:text-dark-text
                  sm:text-5xl
                  lg:text-6xl
                  xl:text-7xl
                "
              >
                Discover what&apos;s
                <span className="text-brand-teal">
                  {' '}
                  happening.
                </span>
              </h1>

              <p
                className="
                  mt-6 max-w-2xl
                  text-base leading-7
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-lg sm:leading-8
                "
              >
                Discover music, follow artists, join conversations, and stay
                connected to the stories and culture shaping the vibe.
              </p>

              {/* Primary actions */}
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  href="/music"
                  className="
                    inline-flex h-12 items-center justify-center gap-2
                    rounded-xl
                    bg-brand-teal
                    px-5
                    text-sm font-bold text-white
                    shadow-sm shadow-brand-teal/20
                    transition-all duration-200
                    hover:bg-brand-teal-dark
                    active:scale-[0.99]
                    focus:outline-none
                    focus:ring-4
                    focus:ring-brand-teal/20
                  "
                >
                  <MusicIcon className="h-5 w-5" />
                  Explore music
                  <ArrowRightIcon className="h-4 w-4" />
                </Link>

                <Link
                  href="/news"
                  className="
                    inline-flex h-12 items-center justify-center gap-2
                    rounded-xl
                    border border-light-border
                    bg-light-surface
                    px-5
                    text-sm font-bold
                    text-light-text
                    transition-all duration-200
                    hover:bg-light-surface-soft
                    active:scale-[0.99]
                    focus:outline-none
                    focus:ring-4
                    focus:ring-brand-teal/10
                    dark:border-dark-border
                    dark:bg-dark-surface
                    dark:text-dark-text
                    dark:hover:bg-dark-surface-soft
                    dark:focus:ring-brand-teal/15
                  "
                >
                  <NewsIcon className="h-5 w-5" />
                  Explore news
                </Link>
              </div>

              {/* Search entry */}
              <Link
                href="/music/search"
                className="
                  mt-6 inline-flex items-center gap-2
                  text-sm font-semibold
                  text-light-text-muted
                  transition-colors
                  hover:text-brand-teal-dark
                  dark:text-dark-text-muted
                  dark:hover:text-brand-teal-light
                "
              >
                <SearchIcon className="h-4 w-4" />
                Looking for a song, artist or album?
                <ArrowRightIcon className="h-3.5 w-3.5" />
              </Link>

              {/* Auth-aware CTA */}
              {!isLoading && (
                <FadeIn>
                  {isAuthenticated === false && (
                    <p
                      className="
                        mt-5 flex flex-wrap items-center gap-x-2 gap-y-1
                        text-sm
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    >
                      <span>
                        New to VibeNationHQ?
                      </span>

                      <Link
                        href="/signup"
                        className="
                          inline-flex items-center gap-1
                          font-bold
                          text-brand-teal-dark
                          transition-colors
                          hover:text-brand-teal
                          dark:text-brand-teal-light
                          dark:hover:text-brand-teal
                        "
                      >
                        Create an account
                        <ArrowRightIcon className="h-3.5 w-3.5" />
                      </Link>
                    </p>
                  )}

                  {isAuthenticated === true && (
                    <p
                      className="
                        mt-5 flex flex-wrap items-center gap-x-2 gap-y-1
                        text-sm
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    >
                      <span>
                        Welcome back.
                      </span>

                      <Link
                        href="/account"
                        className="
                          inline-flex items-center gap-1
                          font-bold
                          text-brand-teal-dark
                          transition-colors
                          hover:text-brand-teal
                          dark:text-brand-teal-light
                          dark:hover:text-brand-teal
                        "
                      >
                        Go to your account
                        <ArrowRightIcon className="h-3.5 w-3.5" />
                      </Link>
                    </p>
                  )}
                </FadeIn>
              )}
            </div>
          </FadeIn>

          {/* Visual discovery panel */}
          <FadeIn delay={0.12}>
            <div
              className="
                relative mx-auto w-full max-w-lg
                lg:ml-auto
              "
            >
              <div
                className="
                  overflow-hidden rounded-2xl
                  border border-light-border
                  bg-light-surface
                  shadow-xl shadow-black/[0.05]
                  dark:border-dark-border
                  dark:bg-dark-surface
                  dark:shadow-black/20
                "
              >
                {/* Panel header */}
                <div
                  className="
                    flex items-center justify-between
                    border-b border-light-border
                    px-5 py-4
                    dark:border-dark-border
                  "
                >
                  <div>
                    <p
                      className="
                        text-xs font-bold uppercase tracking-wider
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    >
                      Your Vibe
                    </p>

                    <p
                      className="
                        mt-1 text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Discover something new
                    </p>
                  </div>

                  <div
                    className="
                      flex h-9 w-9 items-center justify-center
                      rounded-lg
                      bg-brand-teal/10
                      text-brand-teal
                    "
                  >
                    <MusicIcon className="h-4.5 w-4.5" />
                  </div>
                </div>

                {/* Discovery cards */}
                <div className="space-y-3 p-4">
                  {/* Music */}
                  <Link
                    href="/music"
                    className="
                      group flex items-center gap-4
                      rounded-xl
                      border border-light-border-soft
                      bg-light-surface-soft
                      p-4
                      transition-all duration-200
                      hover:border-brand-teal/30
                      hover:bg-light-surface
                      focus:outline-none
                      focus:ring-4
                      focus:ring-brand-teal/10
                      dark:border-dark-border-soft
                      dark:bg-dark-surface-soft
                      dark:hover:border-brand-teal/30
                      dark:hover:bg-dark-surface
                      dark:focus:ring-brand-teal/15
                    "
                  >
                    <div
                      className="
                        flex h-11 w-11 shrink-0 items-center justify-center
                        rounded-lg
                        bg-brand-teal/10
                        text-brand-teal
                      "
                    >
                      <MusicIcon className="h-5 w-5" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p
                        className="
                          text-sm font-bold
                          text-light-text
                          dark:text-dark-text
                        "
                      >
                        Discover music
                      </p>

                      <p
                        className="
                          mt-1 text-xs leading-5
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        Find songs, albums, artists and more.
                      </p>
                    </div>

                    <ArrowRightIcon
                      className="
                        h-4 w-4 shrink-0
                        text-light-text-soft
                        transition-transform
                        group-hover:translate-x-0.5
                        dark:text-dark-text-soft
                      "
                    />
                  </Link>

                  {/* News */}
                  <Link
                    href="/news"
                    className="
                      group flex items-center gap-4
                      rounded-xl
                      border border-light-border-soft
                      bg-light-surface-soft
                      p-4
                      transition-all duration-200
                      hover:border-brand-teal/30
                      hover:bg-light-surface
                      focus:outline-none
                      focus:ring-4
                      focus:ring-brand-teal/10
                      dark:border-dark-border-soft
                      dark:bg-dark-surface-soft
                      dark:hover:border-brand-teal/30
                      dark:hover:bg-dark-surface
                      dark:focus:ring-brand-teal/15
                    "
                  >
                    <div
                      className="
                        flex h-11 w-11 shrink-0 items-center justify-center
                        rounded-lg
                        bg-cyan-500/10
                        text-cyan-600
                        dark:text-cyan-400
                      "
                    >
                      <NewsIcon className="h-5 w-5" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p
                        className="
                          text-sm font-bold
                          text-light-text
                          dark:text-dark-text
                        "
                      >
                        Stay in the know
                      </p>

                      <p
                        className="
                          mt-1 text-xs leading-5
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        Catch the latest stories, culture and entertainment.
                      </p>
                    </div>

                    <ArrowRightIcon
                      className="
                        h-4 w-4 shrink-0
                        text-light-text-soft
                        transition-transform
                        group-hover:translate-x-0.5
                        dark:text-dark-text-soft
                      "
                    />
                  </Link>

                  {/* Brand message */}
                  <div
                    className="
                      rounded-xl
                      border border-brand-teal/15
                      bg-brand-teal/[0.06]
                      p-4
                      dark:border-brand-teal/20
                      dark:bg-brand-teal/[0.07]
                    "
                  >
                    <p
                      className="
                        text-xs font-bold uppercase tracking-wider
                        text-brand-teal-dark
                        dark:text-brand-teal-light
                      "
                    >
                      Stay in the Vibe
                    </p>

                    <p
                      className="
                        mt-2 text-sm leading-6
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Music, conversations and stories — all in one place.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  );
}