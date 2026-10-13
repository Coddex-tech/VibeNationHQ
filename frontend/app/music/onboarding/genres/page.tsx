'use client';

import { useEffect, useMemo, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  ChevronRightIcon,
  MusicIcon,
} from '@/components/Icons';
import HomeNav from '@/components/special/HomeNav';
import {
  getGenrePreferences,
  setGenrePreferences,
} from '@/lib/music/GenrePreferences';
import {
  getMusicGenres,
  type MusicGenre,
} from '@/lib/music/Genres';

export default function GenreOnboardingPage() {
  const [genres, setGenres] = useState<MusicGenre[]>(
    [],
  );

  const [selectedGenreIds, setSelectedGenreIds] =
    useState<number[]>([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isSaving, setIsSaving] =
    useState(false);

  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadPreferences = async () => {
      setIsLoading(true);
      setError('');

      try {
        const [availableGenres, preferences] =
          await Promise.all([
            getMusicGenres(),
            getGenrePreferences(),
          ]);

        if (!isMounted) {
          return;
        }

        setGenres(availableGenres);

        setSelectedGenreIds(
          preferences.map(
            (preference) => preference.genre_id,
          ),
        );
      } catch {
        if (!isMounted) {
          return;
        }

        setError(
          'We could not load your music preferences. Please try again.',
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadPreferences();

    return () => {
      isMounted = false;
    };
  }, []);

  const selectedGenreSet = useMemo(
    () => new Set(selectedGenreIds),
    [selectedGenreIds],
  );

  const toggleGenre = (genreId: number) => {
    setSelectedGenreIds((current) => {
      if (current.includes(genreId)) {
        return current.filter(
          (id) => id !== genreId,
        );
      }

      return [...current, genreId];
    });
  };

  const handleSave = async () => {
    setError('');
    setIsSaving(true);

    try {
      await setGenrePreferences({
        genreIds: selectedGenreIds,
      });

      window.location.href = '/music';
    } catch {
      setError(
        'We could not save your preferences. Please try again.',
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleSkip = () => {
    window.location.href = '/music';
  };

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
      <main
        className="
          mx-auto flex min-h-[calc(100vh-4rem)]
          w-full max-w-4xl
          flex-col
          px-4 py-8
          sm:px-6 sm:py-10
          lg:px-8 lg:py-12
        "
      >
        {/* Progress */}
        <div className="mx-auto w-full max-w-2xl">
          <div className="flex items-center justify-between">
            <p
              className="
                text-xs font-bold
                uppercase tracking-[0.14em]
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              Music setup
            </p>

            <p
              className="
                text-xs font-semibold
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              Step 1 of 1
            </p>
          </div>

          <div
            className="
              mt-3 h-1.5 overflow-hidden
              rounded-full
              bg-light-surface-muted
              dark:bg-dark-surface-muted
            "
          >
            <div
              className="
                h-full w-full
                rounded-full
                bg-brand-teal
              "
            />
          </div>
        </div>

        <section
          className="
            mx-auto w-full max-w-2xl
            flex-1
            py-10
            sm:py-14
          "
        >
          <FadeIn>
            <div className="text-center">
              <div
                className="
                  mx-auto flex h-14 w-14
                  items-center justify-center
                  rounded-2xl
                  bg-brand-teal/10
                  text-brand-teal
                  dark:bg-brand-teal/15
                "
              >
                <MusicIcon className="h-7 w-7" />
              </div>

              <h1
                className="
                  mt-6
                  text-3xl font-black tracking-tight
                  text-light-text
                  dark:text-dark-text
                  sm:text-4xl
                "
              >
                Tune Your Vibe
              </h1>

              <p
                className="
                  mx-auto mt-3 max-w-lg
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-base
                "
              >
                Pick the genres you enjoy. We'll use
                your choices to personalize your music
                discovery.
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

                <p className="min-w-0">
                  {error}
                </p>
              </div>
            </FadeIn>
          )}

          {isLoading ? (
            <div
              className="
                mt-10 grid grid-cols-2 gap-3
                sm:grid-cols-3
              "
            >
              {Array.from({
                length: 24,
              }).map((_, index) => (
                <div
                  key={index}
                  className="
                    h-14 animate-pulse
                    rounded-xl
                    bg-light-surface-muted
                    dark:bg-dark-surface-muted
                  "
                />
              ))}
            </div>
          ) : (
            <FadeIn
              className="
                mt-10
                grid grid-cols-2 gap-3
                sm:grid-cols-3
              "
            >
              {genres.map((genre) => {
                const isSelected =
                  selectedGenreSet.has(
                    genre.id,
                  );

                return (
                  <button
                    key={genre.id}
                    type="button"
                    onClick={() =>
                      toggleGenre(genre.id)
                    }
                    disabled={isSaving}
                    aria-pressed={isSelected}
                    className={`
                      group relative
                      flex min-h-14
                      items-center
                      justify-between gap-2
                      rounded-xl
                      border
                      px-4 py-3
                      text-left
                      text-sm font-semibold
                      transition-all duration-200
                      disabled:cursor-not-allowed
                      disabled:opacity-60
                      ${
                        isSelected
                          ? `
                            border-brand-teal
                            bg-brand-teal/10
                            text-brand-teal-dark
                            shadow-sm
                            dark:bg-brand-teal/15
                            dark:text-brand-teal-light
                          `
                          : `
                            border-light-border
                            bg-light-surface
                            text-light-text
                            hover:border-brand-teal/40
                            hover:bg-light-surface-soft
                            dark:border-dark-border
                            dark:bg-dark-surface
                            dark:text-dark-text
                            dark:hover:border-brand-teal/40
                            dark:hover:bg-dark-surface-soft
                          `
                      }
                    `}
                  >
                    <span className="min-w-0 truncate">
                      {genre.name}
                    </span>

                    {isSelected && (
                      <CheckCircleIcon
                        className="
                          h-5 w-5 shrink-0
                          text-brand-teal
                        "
                      />
                    )}
                  </button>
                );
              })}
            </FadeIn>
          )}

          {!isLoading &&
            genres.length === 0 &&
            !error && (
              <FadeIn className="mt-10">
                <div
                  className="
                    rounded-2xl
                    border border-light-border
                    bg-light-surface
                    px-5 py-10 text-center
                    dark:border-dark-border
                    dark:bg-dark-surface
                  "
                >
                  <p
                    className="
                      text-sm font-semibold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    No music genres are available
                    yet.
                  </p>

                  <p
                    className="
                      mt-2 text-sm leading-6
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    You can continue and personalize
                    your music discovery later.
                  </p>
                </div>
              </FadeIn>
            )}

          {!isLoading && (
            <FadeIn className="mt-8">
              <div
                className="
                  flex flex-col-reverse gap-3
                  sm:flex-row sm:items-center
                  sm:justify-between
                "
              >
                <button
                  type="button"
                  onClick={handleSkip}
                  disabled={isSaving}
                  className="
                    inline-flex min-h-12
                    items-center justify-center
                    rounded-xl
                    px-5 py-3
                    text-sm font-semibold
                    text-light-text-muted
                    transition-colors
                    hover:bg-light-surface-soft
                    hover:text-light-text
                    disabled:cursor-not-allowed
                    disabled:opacity-60
                    dark:text-dark-text-muted
                    dark:hover:bg-dark-surface-soft
                    dark:hover:text-dark-text
                  "
                >
                  Skip for now
                </button>

                <button
                  type="button"
                  onClick={handleSave}
                  disabled={isSaving}
                  className="
                    inline-flex min-h-12
                    w-full items-center justify-center
                    gap-2
                    rounded-xl
                    bg-brand-teal
                    px-5 py-3
                    text-sm font-bold
                    text-white
                    shadow-sm
                    shadow-brand-teal/20
                    transition-all duration-200
                    hover:bg-brand-teal-dark
                    active:scale-[0.99]
                    disabled:cursor-not-allowed
                    disabled:opacity-60
                    focus:outline-none
                    focus:ring-4
                    focus:ring-brand-teal/20
                    sm:w-auto
                  "
                >
                  {isSaving
                    ? 'Saving...'
                    : selectedGenreIds.length > 0
                      ? `Continue with ${selectedGenreIds.length} ${
                          selectedGenreIds.length === 1
                            ? 'genre'
                            : 'genres'
                        }`
                      : 'Continue'}

                  {!isSaving && (
                    <ChevronRightIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
            </FadeIn>
          )}
        </section>

        <footer
          className="
            border-t
            border-light-border-soft
            pt-5
            text-center
            dark:border-dark-border-soft
          "
        >
          <p
            className="
              text-xs leading-5
              text-light-text-soft
              dark:text-dark-text-soft
            "
          >
            You can change your music preferences
            anytime from Settings.
          </p>
        </footer>
      </main>
    </div>
  );
}