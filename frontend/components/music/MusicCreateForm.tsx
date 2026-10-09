'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  useEffect,
  useRef,
  useState,
} from 'react';
import type {
  FormEvent,
  MouseEvent,
} from 'react';

import { useRouter } from 'next/navigation';

import {
  Album as AlbumIcon,
  ArrowLeft,
  ChevronRight,
  Loader2,
  Music2,
  Plus,
  Search,
  Star,
  UserRound,
  X,
} from 'lucide-react';

import { apiRequest } from '@/lib/api';

type EntityType =
  | 'song'
  | 'album'
  | 'artist';

type CatalogArtist = {
  id: number;
  name: string;
  slug: string;
};

type CatalogAlbum = {
  id: number;
  title: string;
  slug: string;
};

type CatalogSearchResult = {
  entity_type: EntityType;
  id: number;
  title: string;
  slug: string;
  artist: CatalogArtist | null;
  artists: CatalogArtist[];
  album: CatalogAlbum | null;
  artwork: string | null;
};

type CatalogSearchResponse = {
  results: CatalogSearchResult[];
};

type ProviderSearchResult = {
  provider: string;
  provider_id: string;
  entity_type: EntityType;
  title: string;

  artist_name: string | null;
  album_name: string | null;

  artwork_url: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  preview_url: string | null;

  spotify_url: string | null;
  apple_music_url: string | null;
  youtube_url: string | null;
  audiomack_url: string | null;
  boomplay_url: string | null;

  country: string | null;
  isrc: string | null;

  metadata: Record<string, unknown>;
};

type ProviderSearchResponse = {
  results: ProviderSearchResult[];
};

type ImportResponse = {
  entity_type: EntityType;
  created: boolean;
  identity_id: number;
  object_id: number;
  object_type: string;
  title: string;
  artist: CatalogArtist | null;
  album: CatalogAlbum | null;
  song: {
    id: number;
    title: string;
    slug: string;
  } | null;
};

type SelectedTarget = {
  target_type: EntityType;
  id: number;
  title: string;
  slug: string;
  artist: CatalogArtist | null;
  artists: CatalogArtist[];
  album: CatalogAlbum | null;
  artwork: string | null;
};

type CreatePostResponse = {
  id: number;
  content: string;
  rating: number | null;
  target: unknown;
};

type SearchStatus =
  | 'idle'
  | 'loading'
  | 'success'
  | 'error';

type SearchState = {
  query: string;
  localResults: CatalogSearchResult[];
  providerResults: ProviderSearchResult[];
  status: SearchStatus;
  error: string;
  source: 'local' | 'provider' | null;
};

const entityFilters: {
  value: EntityType;
  label: string;
  icon: typeof Music2;
}[] = [
  {
    value: 'song',
    label: 'Songs',
    icon: Music2,
  },
  {
    value: 'album',
    label: 'Albums',
    icon: AlbumIcon,
  },
  {
    value: 'artist',
    label: 'Artists',
    icon: UserRound,
  },
];

const MIN_SEARCH_LENGTH = 2;
const MAX_CONTENT_LENGTH = 5000;

const RATING_MIN = 0.5;
const RATING_MAX = 5;
const RATING_STEP = 0.5;

function getArtistNames(
  result: CatalogSearchResult | SelectedTarget,
): string {
  if (result.artists.length > 0) {
    return result.artists
      .map((artist) => artist.name)
      .join(', ');
  }

  if (result.artist) {
    return result.artist.name;
  }

  return '';
}

function getEntityLabel(
  entityType: EntityType,
): string {
  if (entityType === 'song') {
    return 'Song';
  }

  if (entityType === 'album') {
    return 'Album';
  }

  return 'Artist';
}

function getEntityIcon(
  entityType: EntityType,
) {
  if (entityType === 'song') {
    return Music2;
  }

  if (entityType === 'album') {
    return AlbumIcon;
  }

  return UserRound;
}

function getEntityAccent(
  entityType: EntityType,
): string {
  if (entityType === 'song') {
    return 'text-brand-teal-dark dark:text-brand-teal-light';
  }

  if (entityType === 'album') {
    return 'text-violet-600 dark:text-violet-400';
  }

  return 'text-orange-600 dark:text-orange-400';
}

function createEmptySearchState(): SearchState {
  return {
    query: '',
    localResults: [],
    providerResults: [],
    status: 'idle',
    error: '',
    source: null,
  };
}

function getProviderLabel(
  provider: string,
): string {
  const normalized =
    provider.trim().toLowerCase();

  if (
    normalized === 'itunes' ||
    normalized === 'apple' ||
    normalized === 'apple_music'
  ) {
    return 'Apple Music / iTunes';
  }

  return provider;
}

function getProviderKey(
  result: ProviderSearchResult,
): string {
  return `${result.provider}:${result.provider_id}`;
}

function clampRating(
  value: number,
): number {
  return Math.min(
    RATING_MAX,
    Math.max(RATING_MIN, value),
  );
}

function getRatingFromPointer(
  event: MouseEvent<HTMLDivElement>,
): number {
  const container =
    event.currentTarget.getBoundingClientRect();

  if (container.width <= 0) {
    return RATING_MIN;
  }

  const relativeX =
    Math.min(
      container.width,
      Math.max(
        0,
        event.clientX - container.left,
      ),
    );

  const starWidth =
    container.width / 5;

  const starIndex = Math.min(
    4,
    Math.floor(
      relativeX / starWidth,
    ),
  );

  const positionWithinStar =
    relativeX -
    starIndex * starWidth;

  const isLeftHalf =
    positionWithinStar <
    starWidth / 2;

  const rawRating =
    starIndex +
    (isLeftHalf ? 0.5 : 1);

  return clampRating(rawRating);
}

export default function MusicCreateForm() {
  const router = useRouter();

  const [content, setContent] =
    useState('');

  const [rating, setRating] =
    useState<number | null>(null);

  const [hoverRating, setHoverRating] =
    useState<number | null>(null);

  const [
    isMusicPickerOpen,
    setIsMusicPickerOpen,
  ] = useState(false);

  const [searchType, setSearchType] =
    useState<EntityType>('song');

  const [searchStates, setSearchStates] =
    useState<Record<EntityType, SearchState>>({
      song: createEmptySearchState(),
      album: createEmptySearchState(),
      artist: createEmptySearchState(),
    });

  const [selectedTarget, setSelectedTarget] =
    useState<SelectedTarget | null>(null);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [
    importingProviderKey,
    setImportingProviderKey,
  ] = useState<string | null>(null);

  const [submitError, setSubmitError] =
    useState('');

  const [
    playingProviderKey,
    setPlayingProviderKey,
  ] = useState<string | null>(null);

  const [
    previewProgress,
    setPreviewProgress,
  ] = useState(0);

  const audioRef =
    useRef<HTMLAudioElement | null>(null);

  const searchRequestId =
    useRef(0);

  const searchAbortController =
    useRef<AbortController | null>(null);

  const activeSearchState =
    searchStates[searchType];

  const searchQuery =
    activeSearchState.query;

  const searchResults =
    activeSearchState.localResults;

  const providerResults =
    activeSearchState.providerResults;

  const searchStatus =
    activeSearchState.status;

  const searchError =
    activeSearchState.error;

  const searchSource =
    activeSearchState.source;

  const canRate =
    selectedTarget?.target_type === 'song' ||
    selectedTarget?.target_type === 'album';

  const displayedRating =
    hoverRating ?? rating;

  const updateSearchState = (
    type: EntityType,
    updates: Partial<SearchState>,
  ) => {
    setSearchStates((current) => ({
      ...current,
      [type]: {
        ...current[type],
        ...updates,
      },
    }));
  };

  useEffect(() => {
    const query =
      searchStates[searchType].query.trim();

    if (
      query.length <
      MIN_SEARCH_LENGTH
    ) {
      searchRequestId.current += 1;

      searchAbortController.current?.abort();

      updateSearchState(
        searchType,
        {
          localResults: [],
          providerResults: [],
          status: 'idle',
          error: '',
          source: null,
        },
      );

      return;
    }

    const requestId =
      searchRequestId.current + 1;

    searchRequestId.current =
      requestId;

    searchAbortController.current?.abort();

    const controller =
      new AbortController();

    searchAbortController.current =
      controller;

    const timeout =
      window.setTimeout(
        async () => {
          updateSearchState(
            searchType,
            {
              status: 'loading',
              error: '',
              source: null,
            },
          );

          try {
            const params =
              new URLSearchParams();

            params.set(
              'q',
              query,
            );

            params.set(
              'type',
              searchType,
            );

            params.set(
              'limit',
              '10',
            );

            const localResponse =
              await apiRequest<CatalogSearchResponse>(
                `/api/v1/music/catalog/search/?${params.toString()}`,
                {
                  signal:
                    controller.signal,
                },
              );

            if (
              controller.signal.aborted ||
              requestId !==
                searchRequestId.current
            ) {
              return;
            }

            if (
              localResponse.results.length >
              0
            ) {
              updateSearchState(
                searchType,
                {
                  localResults:
                    localResponse.results,
                  providerResults: [],
                  status: 'success',
                  error: '',
                  source: 'local',
                },
              );

              return;
            }

            const providerResponse =
              await apiRequest<ProviderSearchResponse>(
                `/api/v1/music/search/providers/?${params.toString()}&country=NG`,
                {
                  signal:
                    controller.signal,
                },
              );

            if (
              controller.signal.aborted ||
              requestId !==
                searchRequestId.current
            ) {
              return;
            }

            updateSearchState(
              searchType,
              {
                localResults: [],
                providerResults:
                  providerResponse.results,
                status: 'success',
                error: '',
                source:
                  providerResponse.results.length >
                  0
                    ? 'provider'
                    : null,
              },
            );
          } catch (error) {
            if (
              controller.signal.aborted
            ) {
              return;
            }

            updateSearchState(
              searchType,
              {
                localResults: [],
                providerResults: [],
                status: 'error',
                source: null,
                error:
                  error instanceof Error
                    ? error.message ||
                      'Unable to search the music catalog.'
                    : 'Unable to search the music catalog.',
              },
            );
          }
        },
        300,
      );

    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [
    searchStates[searchType].query,
    searchType,
  ]);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, []);

  const clearSearch = () => {
    updateSearchState(
      searchType,
      {
        query: '',
        localResults: [],
        providerResults: [],
        status: 'idle',
        error: '',
        source: null,
      },
    );
  };

  const handleOpenMusicPicker = () => {
    setIsMusicPickerOpen(true);
    setSubmitError('');
  };

  const handleCloseMusicPicker = () => {
    setIsMusicPickerOpen(false);
  };

  const handleSearchChange = (
    value: string,
  ) => {
    updateSearchState(
      searchType,
      {
        query: value,
      },
    );
  };

  const handleSearchTypeChange = (
    type: EntityType,
  ) => {
    setSearchType(type);
    setSubmitError('');
    setHoverRating(null);
  };

  const handleSelectLocalResult = (
    result: CatalogSearchResult,
  ) => {
    setSelectedTarget({
      target_type:
        result.entity_type,
      id: result.id,
      title: result.title,
      slug: result.slug,
      artist: result.artist,
      artists: result.artists,
      album: result.album,
      artwork: result.artwork,
    });

    setRating(null);
    setHoverRating(null);
    setSubmitError('');
    setIsMusicPickerOpen(false);
  };

  const handleToggleProviderPreview = async (
    event: MouseEvent<HTMLButtonElement>,
    result: ProviderSearchResult,
  ) => {
    event.stopPropagation();

    if (!result.preview_url) {
      setSubmitError(
        'This music provider did not provide a playable preview for this result.',
      );
      return;
    }

    const providerKey =
      getProviderKey(result);

    if (
      playingProviderKey ===
      providerKey
    ) {
      audioRef.current?.pause();
      setPlayingProviderKey(null);
      setPreviewProgress(0);
      return;
    }

    audioRef.current?.pause();

    const audio =
      new Audio(result.preview_url);

    audio.preload = 'metadata';

    audioRef.current = audio;

    setPlayingProviderKey(
      providerKey,
    );
    setPreviewProgress(0);

    audio.addEventListener(
      'timeupdate',
      () => {
        if (
          !audio.duration ||
          !Number.isFinite(
            audio.duration,
          )
        ) {
          return;
        }

        setPreviewProgress(
          Math.min(
            1,
            Math.max(
              0,
              audio.currentTime /
                audio.duration,
            ),
          ),
        );
      },
    );

    audio.addEventListener(
      'ended',
      () => {
        if (
          audioRef.current === audio
        ) {
          setPlayingProviderKey(null);
          setPreviewProgress(0);
          audioRef.current = null;
        }
      },
    );

    audio.addEventListener(
      'error',
      () => {
        if (
          audioRef.current === audio
        ) {
          setPlayingProviderKey(null);
          setPreviewProgress(0);
          audioRef.current = null;

          setSubmitError(
            'This preview could not be played.',
          );
        }
      },
    );

    try {
      await audio.play();
    } catch {
      if (
        audioRef.current === audio
      ) {
        setPlayingProviderKey(null);
        setPreviewProgress(0);
        audioRef.current = null;
      }

      setSubmitError(
        'Unable to play this preview.',
      );
    }
  };

  const handleSelectProviderResult =
    async (
      result: ProviderSearchResult,
    ) => {
      setSubmitError('');

      const providerKey =
        getProviderKey(result);

      if (
        importingProviderKey !== null
      ) {
        return;
      }

      setImportingProviderKey(
        providerKey,
      );

      audioRef.current?.pause();
      audioRef.current = null;
      setPlayingProviderKey(null);
      setPreviewProgress(0);

      try {
        const imported =
          await apiRequest<ImportResponse>(
            '/api/v1/music/import/',
            {
              method: 'POST',
              body: JSON.stringify({
                provider:
                  result.provider,
                provider_id:
                  result.provider_id,
                entity_type:
                  result.entity_type,
                title:
                  result.title,
                artist_name:
                  result.artist_name,
                album_name:
                  result.album_name,
                artwork_url:
                  result.artwork_url,
                release_date:
                  result.release_date,
                duration_seconds:
                  result.duration_seconds,
                preview_url:
                  result.preview_url,
                spotify_url:
                  result.spotify_url,
                apple_music_url:
                  result.apple_music_url,
                youtube_url:
                  result.youtube_url,
                audiomack_url:
                  result.audiomack_url,
                boomplay_url:
                  result.boomplay_url,
                country:
                  result.country,
                isrc:
                  result.isrc,
                metadata:
                  result.metadata ?? {},
              }),
            },
          );

        /*
         * Build the selected target from the
         * canonical object returned by VibeNationHQ.
         *
         * Artwork and provider metadata are not
         * included in ImportResponse, so artwork
         * comes from the original provider result.
         */
        if (
          imported.entity_type ===
          'song' &&
          imported.song
        ) {
          setSelectedTarget({
            target_type: 'song',
            id: imported.song.id,
            title:
              imported.song.title ||
              imported.title ||
              result.title,
            slug:
              imported.song.slug,
            artist:
              imported.artist,
            artists:
              imported.artist
                ? [imported.artist]
                : [],
            album:
              imported.album,
            artwork:
              result.artwork_url,
          });
        } else if (
          imported.entity_type ===
          'album' &&
          imported.album
        ) {
          setSelectedTarget({
            target_type: 'album',
            id: imported.album.id,
            title:
              imported.album.title ||
              imported.title ||
              result.title,
            slug:
              imported.album.slug,
            artist:
              imported.artist,
            artists:
              imported.artist
                ? [imported.artist]
                : [],
            album:
              imported.album,
            artwork:
              result.artwork_url,
          });
        } else if (
          imported.entity_type ===
          'artist' &&
          imported.artist
        ) {
          setSelectedTarget({
            target_type: 'artist',
            id: imported.artist.id,
            title:
              imported.artist.name ||
              imported.title ||
              result.title,
            slug:
              imported.artist.slug,
            artist:
              imported.artist,
            artists: [
              imported.artist,
            ],
            album: null,
            artwork:
              result.artwork_url,
          });
        } else {
          throw new Error(
            'The music was imported, but VibeNationHQ did not return a usable catalog object.',
          );
        }

        setRating(null);
        setHoverRating(null);
        setIsMusicPickerOpen(false);
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setSubmitError(
            error.message ||
              'Unable to add this music to VibeNationHQ.',
          );
        } else {
          setSubmitError(
            'Unable to add this music to VibeNationHQ.',
          );
        }
      } finally {
        setImportingProviderKey(
          null,
        );
      }
    };

  const handleRemoveTarget = () => {
    setSelectedTarget(null);
    setRating(null);
    setHoverRating(null);
    setSubmitError('');
  };

  const handleRatingHover = (
    event: MouseEvent<HTMLDivElement>,
  ) => {
    setHoverRating(
      getRatingFromPointer(event),
    );
  };

  const handleRatingClick = (
    event: MouseEvent<HTMLDivElement>,
  ) => {
    setRating(
      getRatingFromPointer(event),
    );
  };

  const renderRatingStar = (
    star: number,
  ) => {
    const value =
      displayedRating ?? 0;

    const isFull =
      value >= star;

    const isHalf =
      !isFull &&
      value >= star - 0.5;

    const starSize = 28;

    return (
      <div
        key={star}
        aria-hidden="true"
        className="
          relative flex h-9 w-9
          shrink-0
          items-center justify-center
        "
      >
        <Star
          className="
            absolute
            text-light-border
            dark:text-dark-border
          "
          size={starSize}
          strokeWidth={1.7}
        />

        {(isFull || isHalf) && (
          <div
            className="
              pointer-events-none
              absolute inset-0
              flex items-center
              justify-center
              overflow-hidden
            "
          >
            <div
              className="
                relative h-7 w-7
              "
            >
              <Star
                className="
                  absolute inset-0
                  fill-brand-teal
                  text-brand-teal
                "
                size={starSize}
                strokeWidth={1.7}
              />

              {isHalf && (
                <div
                  className="
                    absolute right-0 top-0
                    h-full w-1/2
                    overflow-hidden
                    bg-light-surface
                    dark:bg-dark-surface
                  "
                >
                  <Star
                    className="
                      absolute right-0 top-0
                      fill-transparent
                      text-light-border
                      dark:text-dark-border
                    "
                    size={starSize}
                    strokeWidth={1.7}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setSubmitError('');

    const trimmedContent =
      content.trim();

    if (!trimmedContent) {
      setSubmitError(
        'Write something before publishing your post.',
      );
      return;
    }

    if (!canRate) {
      setRating(null);
    }

    setIsSubmitting(true);

    try {
      let target:
        | Record<
            string,
            string | number
          >
        | null = null;

      if (selectedTarget) {
        target = {
          target_type:
            selectedTarget.target_type,
        };

        if (
          selectedTarget.target_type ===
          'song'
        ) {
          target.song =
            selectedTarget.id;
        }

        if (
          selectedTarget.target_type ===
          'album'
        ) {
          target.album =
            selectedTarget.id;
        }

        if (
          selectedTarget.target_type ===
          'artist'
        ) {
          target.artist =
            selectedTarget.id;
        }
      }

      await apiRequest<CreatePostResponse>(
        '/api/v1/music/community/posts/',
        {
          method: 'POST',
          body: JSON.stringify({
            content:
              trimmedContent,
            rating: canRate
              ? rating
              : null,
            target,
          }),
        },
      );

      router.push('/music');
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setSubmitError(
          error.message ||
            'Unable to publish your post.',
        );
      } else {
        setSubmitError(
          'Unable to publish your post.',
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-3xl"
    >
      {/* Header */}
      <header className="mb-7">
        <Link
          href="/music"
          className="
            inline-flex items-center gap-2
            text-sm font-semibold
            text-light-text-muted
            transition-colors
            hover:text-brand-teal-dark
            dark:text-dark-text-muted
            dark:hover:text-brand-teal-light
          "
        >
          <ArrowLeft className="h-4 w-4" />
          Back to music
        </Link>

        <div className="mt-7">
          <p
            className="
              text-xs font-bold uppercase
              tracking-[0.16em]
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            Community
          </p>

          <h1
            className="
              mt-2 text-3xl font-black
              tracking-tight
              text-light-text
              dark:text-dark-text
              sm:text-4xl
            "
          >
            Share your vibe
          </h1>

          <p
            className="
              mt-2 max-w-xl
              text-sm leading-6
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            Say what you think, start a
            conversation, or share something
            you discovered.
          </p>
        </div>
      </header>

      {submitError && (
        <div
          role="alert"
          className="
            mb-5 flex items-start gap-3
            rounded-2xl
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
          <div className="min-w-0 flex-1">
            {submitError}
          </div>

          <button
            type="button"
            onClick={() =>
              setSubmitError('')
            }
            aria-label="Dismiss error"
            className="
              shrink-0 rounded-lg p-1
              text-red-500
              transition-colors
              hover:bg-red-100
              dark:text-red-300
              dark:hover:bg-red-500/10
            "
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Composer */}
      <section
        className="
          overflow-hidden
          rounded-3xl
          border border-light-border
          bg-light-surface
          shadow-sm shadow-black/[0.04]
          dark:border-dark-border
          dark:bg-dark-surface
          dark:shadow-black/20
        "
      >
        {/* Text composer */}
        <div className="p-5 sm:p-7">
          <div className="flex items-center gap-3">
            <div
              className="
                flex h-9 w-9 shrink-0
                items-center justify-center
                rounded-full
                bg-brand-teal/10
                text-brand-teal
                dark:bg-brand-teal/15
              "
            >
              <Music2 className="h-4 w-4" />
            </div>

            <div>
              <p
                className="
                  text-sm font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                What's on your mind?
              </p>

              <p
                className="
                  text-xs
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                Your thoughts, your vibe.
              </p>
            </div>
          </div>

          <textarea
            value={content}
            onChange={(event) =>
              setContent(
                event.target.value,
              )
            }
            placeholder="Share your thoughts about music..."
            maxLength={
              MAX_CONTENT_LENGTH
            }
            rows={6}
            className="
              mt-4 w-full
              resize-none
              rounded-2xl
              border
              border-light-border
              bg-light-bg
              px-4
              py-4
              text-sm
              text-light-text
              outline-none
              transition
              placeholder:text-light-muted
              focus:border-primary
              dark:border-dark-border
              dark:bg-dark-bg
              dark:text-dark-text
              dark:placeholder:text-dark-muted
            "
          />

          <div
            className="
              mt-4 flex items-center
              justify-between gap-4
              border-t border-light-border-soft
              pt-4
              dark:border-dark-border-soft
            "
          >
            <p
              className="
                text-xs
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {content.trim().length ===
              0
                ? 'Write something to get started.'
                : 'You can add music below.'}
            </p>

            <span
              className="
                shrink-0 text-xs font-medium
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {content.length.toLocaleString()}
              /
              {MAX_CONTENT_LENGTH.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Music attachment */}
        <div
          className="
            border-t border-light-border-soft
            dark:border-dark-border-soft
          "
        >
          {!selectedTarget &&
            !isMusicPickerOpen && (
              <button
                type="button"
                onClick={
                  handleOpenMusicPicker
                }
                disabled={isSubmitting}
                className="
                  flex w-full items-center
                  gap-4 px-5 py-5
                  text-left
                  transition-colors
                  hover:bg-light-surface-soft
                  disabled:cursor-not-allowed
                  disabled:opacity-60
                  dark:hover:bg-dark-surface-soft
                  sm:px-7
                "
              >
                <div
                  className="
                    flex h-10 w-10
                    shrink-0
                    items-center justify-center
                    rounded-xl
                    border border-light-border
                    bg-light-surface-soft
                    text-brand-teal
                    dark:border-dark-border
                    dark:bg-dark-surface-soft
                  "
                >
                  <Plus className="h-5 w-5" />
                </div>

                <div className="min-w-0 flex-1">
                  <p
                    className="
                      text-sm font-bold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Add music
                  </p>

                  <p
                    className="
                      mt-0.5 text-xs
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Attach a song, album, or
                    artist
                  </p>
                </div>

                <ChevronRight
                  className="
                    h-5 w-5 shrink-0
                    text-light-text-soft
                    dark:text-dark-text-soft
                  "
                />
              </button>
            )}

          {/* Search picker */}
          {isMusicPickerOpen && (
            <div className="p-5 sm:p-7">
              <div
                className="
                  flex items-start
                  justify-between gap-4
                "
              >
                <div>
                  <p
                    className="
                      text-sm font-bold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Add music
                  </p>

                  <p
                    className="
                      mt-1 text-xs leading-5
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Find something from the
                    VibeNationHQ catalog or
                    search our music providers.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={
                    handleCloseMusicPicker
                  }
                  className="
                    flex h-9 w-9 shrink-0
                    items-center justify-center
                    rounded-xl
                    text-light-text-soft
                    transition-colors
                    hover:bg-light-surface-soft
                    hover:text-light-text
                    dark:text-dark-text-soft
                    dark:hover:bg-dark-surface-soft
                    dark:hover:text-dark-text
                  "
                  aria-label="Close music search"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Entity tabs */}
              <div
                className="
                  mt-5 flex
                  overflow-x-auto
                  rounded-xl
                  border border-light-border
                  bg-light-surface-soft
                  p-1
                  dark:border-dark-border
                  dark:bg-dark-surface-soft
                "
              >
                {entityFilters.map(
                  (filter) => {
                    const Icon =
                      filter.icon;

                    const active =
                      searchType ===
                      filter.value;

                    return (
                      <button
                        key={
                          filter.value
                        }
                        type="button"
                        onClick={() =>
                          handleSearchTypeChange(
                            filter.value,
                          )
                        }
                        disabled={
                          isSubmitting ||
                          importingProviderKey !==
                            null
                        }
                        className={`
                          inline-flex
                          min-h-10
                          flex-1
                          items-center
                          justify-center
                          gap-1.5
                          rounded-lg
                          px-4
                          text-xs font-bold
                          whitespace-nowrap
                          transition-all
                          disabled:cursor-not-allowed
                          disabled:opacity-60

                          ${
                            active
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
                        <Icon className="h-4 w-4" />
                        {filter.label}
                      </button>
                    );
                  },
                )}
              </div>

              {/* Search */}
              <div className="relative mt-4">
                <Search
                  className="
                    pointer-events-none
                    absolute left-3.5 top-1/2
                    h-5 w-5
                    -translate-y-1/2
                    text-light-text-soft
                    dark:text-dark-text-soft
                  "
                />

                <input
                  type="search"
                  value={searchQuery}
                  onChange={(event) =>
                    handleSearchChange(
                      event.target.value,
                    )
                  }
                  placeholder={`Search ${getEntityLabel(
                    searchType,
                  ).toLowerCase()}s...`}
                  disabled={
                    isSubmitting ||
                    importingProviderKey !==
                      null
                  }
                  autoComplete="off"
                  autoFocus
                  className="
                    h-12 w-full
                    rounded-xl
                    border border-light-border
                    bg-light-surface
                    pl-11 pr-11
                    text-sm
                    text-light-text
                    outline-none
                    transition-all
                    placeholder:text-light-text-soft
                    focus:border-brand-teal
                    focus:ring-4
                    focus:ring-brand-teal/10
                    disabled:cursor-not-allowed
                    disabled:opacity-60
                    dark:border-dark-border
                    dark:bg-dark-surface
                    dark:text-dark-text
                    dark:placeholder:text-dark-text-soft
                    dark:focus:border-brand-teal
                    dark:focus:ring-brand-teal/15
                  "
                />

                {searchStatus ===
                  'loading' && (
                  <Loader2
                    className="
                      absolute right-3.5 top-1/2
                      h-5 w-5
                      -translate-y-1/2
                      animate-spin
                      text-brand-teal
                    "
                  />
                )}

                {searchQuery.length >
                  0 &&
                  searchStatus !==
                    'loading' && (
                    <button
                      type="button"
                      onClick={
                        clearSearch
                      }
                      aria-label="Clear search"
                      className="
                        absolute right-2 top-1/2
                        flex h-9 w-9
                        -translate-y-1/2
                        items-center justify-center
                        rounded-lg
                        text-light-text-soft
                        hover:bg-light-surface-soft
                        hover:text-light-text
                        dark:text-dark-text-soft
                        dark:hover:bg-dark-surface-soft
                        dark:hover:text-dark-text
                      "
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
              </div>

              {/* Searching state */}
              {searchStatus ===
                'loading' && (
                <div
                  className="
                    mt-4 overflow-hidden
                    rounded-2xl
                    border border-light-border
                    dark:border-dark-border
                  "
                >
                  <div
                    className="
                      flex items-center gap-3
                      px-4 py-5
                      sm:px-5
                    "
                  >
                    <div
                      className="
                        flex h-10 w-10
                        shrink-0
                        items-center justify-center
                        rounded-xl
                        bg-brand-teal/10
                        text-brand-teal
                        dark:bg-brand-teal/15
                      "
                    >
                      <Loader2
                        className="
                          h-5 w-5
                          animate-spin
                        "
                      />
                    </div>

                    <div className="min-w-0">
                      <p
                        className="
                          text-sm font-semibold
                          text-light-text
                          dark:text-dark-text
                        "
                      >
                        Searching...
                      </p>

                      <p
                        className="
                          mt-0.5 text-xs
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        Looking through the
                        {` `}
                        {getEntityLabel(
                          searchType,
                        ).toLowerCase()}
                        {` `}
                        catalog and music providers.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Search hint */}
              {searchQuery.trim()
                .length > 0 &&
                searchQuery.trim()
                  .length <
                  MIN_SEARCH_LENGTH && (
                  <p
                    className="
                      mt-3 text-xs
                      text-light-text-soft
                      dark:text-dark-text-soft
                    "
                  >
                    Type at least{' '}
                    {MIN_SEARCH_LENGTH}{' '}
                    characters to search.
                  </p>
                )}

              {/* Search error */}
              {searchStatus ===
                'error' && (
                <div
                  role="alert"
                  className="
                    mt-4 rounded-xl
                    border border-red-200
                    bg-red-50
                    px-4 py-3
                    text-xs leading-5
                    text-red-700
                    dark:border-red-500/20
                    dark:bg-red-500/10
                    dark:text-red-300
                  "
                >
                  {searchError}
                </div>
              )}

              {/* Local results */}
              {searchSource ===
                'local' &&
                searchResults.length >
                  0 && (
                  <div
                    className="
                      mt-4 overflow-hidden
                      rounded-2xl
                      border border-light-border
                      dark:border-dark-border
                    "
                  >
                    <div
                      className="
                        divide-y
                        divide-light-border-soft
                        dark:divide-dark-border-soft
                      "
                    >
                      {searchResults.map(
                        (result) => {
                          const Icon =
                            getEntityIcon(
                              result.entity_type,
                            );

                          const artistNames =
                            getArtistNames(
                              result,
                            );

                          return (
                            <button
                              key={`${result.entity_type}-${result.id}`}
                              type="button"
                              onClick={() =>
                                handleSelectLocalResult(
                                  result,
                                )
                              }
                              disabled={
                                isSubmitting ||
                                importingProviderKey !==
                                  null
                              }
                              className="
                                group flex w-full
                                items-center gap-3
                                px-4 py-3.5
                                text-left
                                transition-colors
                                hover:bg-light-surface-soft
                                disabled:cursor-not-allowed
                                disabled:opacity-60
                                dark:hover:bg-dark-surface-soft
                                sm:px-5
                              "
                            >
                              <div
                                className="
                                  relative h-14 w-14
                                  shrink-0
                                  overflow-hidden
                                  rounded-xl
                                  bg-light-surface-muted
                                  ring-1
                                  ring-black/[0.04]
                                  dark:bg-dark-surface-muted
                                  dark:ring-white/[0.04]
                                "
                              >
                                {result.artwork ? (
                                  <Image
                                    src={
                                      result.artwork
                                    }
                                    alt={`${result.title} artwork`}
                                    fill
                                    sizes="56px"
                                    className="
                                      object-cover
                                      transition-transform
                                      duration-300
                                      group-hover:scale-105
                                    "
                                  />
                                ) : (
                                  <div
                                    className="
                                      flex h-full w-full
                                      items-center
                                      justify-center
                                      text-light-text-soft
                                      dark:text-dark-text-soft
                                    "
                                  >
                                    <Icon className="h-5 w-5" />
                                  </div>
                                )}
                              </div>

                              <div className="min-w-0 flex-1">
                                <div
                                  className="
                                    flex items-center
                                    gap-2
                                  "
                                >
                                  <p
                                    className="
                                      min-w-0 truncate
                                      text-sm font-bold
                                      text-light-text
                                      dark:text-dark-text
                                    "
                                  >
                                    {result.title}
                                  </p>

                                  <span
                                    className={`
                                      hidden shrink-0
                                      rounded-full
                                      bg-light-surface-soft
                                      px-2 py-0.5
                                      text-[10px]
                                      font-bold
                                      uppercase
                                      tracking-wide
                                      dark:bg-dark-surface-soft
                                      sm:inline-flex
                                      ${getEntityAccent(
                                        result.entity_type,
                                      )}
                                    `}
                                  >
                                    {getEntityLabel(
                                      result.entity_type,
                                    )}
                                  </span>
                                </div>

                                <p
                                  className="
                                    mt-1 truncate
                                    text-xs
                                    text-light-text-muted
                                    dark:text-dark-text-muted
                                  "
                                >
                                  {result.entity_type ===
                                  'artist'
                                    ? 'Artist'
                                    : artistNames ||
                                      result
                                        .album
                                        ?.title ||
                                      'VibeNationHQ catalog'}
                                </p>

                                {result.entity_type ===
                                  'song' &&
                                  result.album && (
                                    <p
                                      className="
                                        mt-0.5 truncate
                                        text-[11px]
                                        text-light-text-soft
                                        dark:text-dark-text-soft
                                      "
                                    >
                                      {result.album.title}
                                    </p>
                                  )}
                              </div>

                              <ChevronRight
                                className="
                                  h-4 w-4
                                  shrink-0
                                  text-light-text-soft
                                  transition-transform
                                  group-hover:translate-x-0.5
                                  dark:text-dark-text-soft
                                "
                              />
                            </button>
                          );
                        },
                      )}
                    </div>
                  </div>
                )}

              {/* Provider results */}
              {searchSource ===
                'provider' &&
                providerResults.length >
                  0 && (
                  <div className="mt-4">
                    <div className="mb-3">
                      <p
                        className="
                          text-xs font-bold
                          uppercase
                          tracking-[0.12em]
                          text-brand-teal-dark
                          dark:text-brand-teal-light
                        "
                      >
                        From music providers
                      </p>

                      <p
                        className="
                          mt-1 text-xs
                          leading-5
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        These results come from
                        external music catalogs.
                        Select a result to add its
                        metadata to VibeNationHQ.
                      </p>
                    </div>

                    <div
                      className="
                        overflow-hidden
                        rounded-2xl
                        border border-light-border
                        dark:border-dark-border
                      "
                    >
                      <div
                        className="
                          divide-y
                          divide-light-border-soft
                          dark:divide-dark-border-soft
                        "
                      >
                        {providerResults.map(
                          (result) => {
                            const Icon =
                              getEntityIcon(
                                result.entity_type,
                              );

                            const providerKey =
                              getProviderKey(
                                result,
                              );

                            const isPlaying =
                              playingProviderKey ===
                              providerKey;

                            const isImporting =
                              importingProviderKey ===
                              providerKey;

                            const hasPreview =
                              Boolean(
                                result.preview_url,
                              );

                            const radius = 24;

                            const circumference =
                              2 *
                              Math.PI *
                              radius;

                            const dashOffset =
                              circumference *
                              (1 -
                                (isPlaying
                                  ? previewProgress
                                  : 0));

                            return (
                              <div
                                key={
                                  providerKey
                                }
                                role="button"
                                tabIndex={
                                  isImporting
                                    ? -1
                                    : 0
                                }
                                onClick={() =>
                                  handleSelectProviderResult(
                                    result,
                                  )
                                }
                                onKeyDown={(
                                  event,
                                ) => {
                                  if (
                                    event.key ===
                                      'Enter' ||
                                    event.key ===
                                      ' '
                                  ) {
                                    event.preventDefault();

                                    handleSelectProviderResult(
                                      result,
                                    );
                                  }
                                }}
                                aria-disabled={
                                  isImporting
                                }
                                className="
                                  group flex w-full
                                  cursor-pointer
                                  items-center gap-3
                                  px-4 py-3.5
                                  text-left
                                  transition-colors
                                  hover:bg-light-surface-soft
                                  focus:outline-none
                                  focus-visible:bg-light-surface-soft
                                  dark:hover:bg-dark-surface-soft
                                  dark:focus-visible:bg-dark-surface-soft
                                  sm:px-5
                                "
                              >
                                <div
                                  className="
                                    relative h-14 w-14
                                    shrink-0
                                  "
                                >
                                  <div
                                    className="
                                      absolute inset-0
                                      overflow-hidden
                                      rounded-xl
                                      bg-light-surface-muted
                                      ring-1
                                      ring-black/[0.04]
                                      dark:bg-dark-surface-muted
                                      dark:ring-white/[0.04]
                                    "
                                  >
                                    {result.artwork_url ? (
                                      <Image
                                        src={
                                          result.artwork_url
                                        }
                                        alt={`${result.title} artwork`}
                                        fill
                                        sizes="56px"
                                        className={`
                                          object-cover
                                          transition-transform
                                          duration-300
                                          ${
                                            isPlaying
                                              ? 'scale-105'
                                              : 'group-hover:scale-105'
                                          }
                                        `}
                                      />
                                    ) : (
                                      <div
                                        className="
                                          flex h-full w-full
                                          items-center
                                          justify-center
                                          text-light-text-soft
                                          dark:text-dark-text-soft
                                        "
                                      >
                                        <Icon className="h-5 w-5" />
                                      </div>
                                    )}
                                  </div>

                                  {isPlaying && (
                                    <svg
                                      className="
                                        pointer-events-none
                                        absolute -inset-1
                                        h-16 w-16
                                        -rotate-90
                                      "
                                      viewBox="0 0 56 56"
                                      aria-hidden="true"
                                    >
                                      <circle
                                        cx="28"
                                        cy="28"
                                        r={radius}
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2.5"
                                        className="
                                          text-brand-teal/20
                                        "
                                      />

                                      <circle
                                        cx="28"
                                        cy="28"
                                        r={radius}
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2.5"
                                        strokeLinecap="round"
                                        className="
                                          text-brand-teal
                                          transition-[stroke-dashoffset]
                                          duration-100
                                        "
                                        strokeDasharray={
                                          circumference
                                        }
                                        strokeDashoffset={
                                          dashOffset
                                        }
                                      />
                                    </svg>
                                  )}

                                  {hasPreview && (
                                    <button
                                      type="button"
                                      onClick={(
                                        event,
                                      ) =>
                                        handleToggleProviderPreview(
                                          event,
                                          result,
                                        )
                                      }
                                      aria-label={
                                        isPlaying
                                          ? `Pause preview of ${result.title}`
                                          : `Play preview of ${result.title}`
                                      }
                                      className="
                                        absolute inset-0
                                        z-10 m-auto
                                        flex h-9 w-9
                                        items-center
                                        justify-center
                                        rounded-full
                                        bg-black/65
                                        text-white
                                        shadow-lg
                                        backdrop-blur-sm
                                        transition-all
                                        hover:scale-105
                                        hover:bg-brand-teal
                                        focus:outline-none
                                        focus-visible:ring-2
                                        focus-visible:ring-white
                                      "
                                    >
                                      {isPlaying ? (
                                        <span className="flex items-center gap-0.5">
                                          <span className="h-3.5 w-0.5 rounded-full bg-white" />
                                          <span className="h-3.5 w-0.5 rounded-full bg-white" />
                                        </span>
                                      ) : (
                                        <span
                                          className="
                                            ml-0.5
                                            h-0 w-0
                                            border-y-[6px]
                                            border-l-[8px]
                                            border-y-transparent
                                            border-l-white
                                          "
                                        />
                                      )}
                                    </button>
                                  )}
                                </div>

                                <div className="min-w-0 flex-1">
                                  <div
                                    className="
                                      flex items-center
                                      gap-2
                                    "
                                  >
                                    <p
                                      className="
                                        min-w-0 truncate
                                        text-sm font-bold
                                        text-light-text
                                        dark:text-dark-text
                                      "
                                    >
                                      {result.title}
                                    </p>

                                    <span
                                      className={`
                                        hidden shrink-0
                                        rounded-full
                                        bg-light-surface-soft
                                        px-2 py-0.5
                                        text-[10px]
                                        font-bold
                                        uppercase
                                        tracking-wide
                                        dark:bg-dark-surface-soft
                                        sm:inline-flex
                                        ${getEntityAccent(
                                          result.entity_type,
                                        )}
                                      `}
                                    >
                                      {getEntityLabel(
                                        result.entity_type,
                                      )}
                                    </span>
                                  </div>

                                  <p
                                    className="
                                      mt-1 truncate
                                      text-xs
                                      text-light-text-muted
                                      dark:text-dark-text-muted
                                    "
                                  >
                                    {result.artist_name ||
                                      result.album_name ||
                                      result.provider}
                                  </p>

                                  <div
                                    className="
                                      mt-1.5 flex
                                      min-w-0
                                      items-center gap-2
                                    "
                                  >
                                    <span
                                      className="
                                        truncate
                                        text-[10px]
                                        font-medium
                                        text-light-text-soft
                                        dark:text-dark-text-soft
                                      "
                                    >
                                      {getProviderLabel(
                                        result.provider,
                                      )}
                                    </span>

                                    {result.preview_url && (
                                      <>
                                        <span
                                          className="
                                            h-1 w-1
                                            shrink-0
                                            rounded-full
                                            bg-light-text-soft
                                            dark:bg-dark-text-soft
                                          "
                                        />

                                        <span
                                          className="
                                            shrink-0
                                            text-[10px]
                                            font-medium
                                            text-brand-teal-dark
                                            dark:text-brand-teal-light
                                          "
                                        >
                                          Preview
                                        </span>
                                      </>
                                    )}
                                  </div>
                                </div>

                                {isImporting ? (
                                  <Loader2
                                    className="
                                      h-5 w-5
                                      shrink-0
                                      animate-spin
                                      text-brand-teal
                                    "
                                  />
                                ) : (
                                  <ChevronRight
                                    className="
                                      h-4 w-4
                                      shrink-0
                                      text-light-text-soft
                                      transition-transform
                                      group-hover:translate-x-0.5
                                      dark:text-dark-text-soft
                                    "
                                  />
                                )}
                              </div>
                            );
                          },
                        )}
                      </div>
                    </div>

                    <p
                      className="
                        mt-3 text-[10px]
                        leading-4
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    >
                      Music previews and catalog
                      metadata are supplied by the
                      external provider shown above.
                      VibeNationHQ does not host the
                      full audio track.
                    </p>
                  </div>
                )}

              {/* Nothing found */}
              {searchStatus ===
                'success' &&
                searchSource === null && (
                  <div
                    className="
                      mt-4 rounded-2xl
                      border border-dashed
                      border-light-border
                      px-5 py-8
                      text-center
                      dark:border-dark-border
                    "
                  >
                    <Search
                      className="
                        mx-auto h-6 w-6
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    />

                    <p
                      className="
                        mt-3 text-sm font-semibold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Nothing found
                    </p>

                    <p
                      className="
                        mt-1 text-xs
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      Try a different search
                      term.
                    </p>
                  </div>
                )}
            </div>
          )}

          {/* Selected target */}
          {selectedTarget && (
            <div className="p-5 sm:p-7">
              <div
                className="
                  rounded-2xl
                  border border-brand-teal/20
                  bg-brand-teal/[0.045]
                  dark:border-brand-teal/20
                  dark:bg-brand-teal/[0.08]
                "
              >
                <div
                  className="
                    flex items-center
                    justify-between gap-4
                    border-b
                    border-brand-teal/10
                    px-4 py-3
                    dark:border-brand-teal/15
                  "
                >
                  <div>
                    <p
                      className="
                        text-[10px] font-bold
                        uppercase
                        tracking-[0.14em]
                        text-brand-teal-dark
                        dark:text-brand-teal-light
                      "
                    >
                      Music attached
                    </p>

                    <p
                      className="
                        mt-0.5 text-xs
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      {getEntityLabel(
                        selectedTarget.target_type,
                      )}{' '}
                      added to your post
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={
                      handleRemoveTarget
                    }
                    disabled={
                      isSubmitting
                    }
                    className="
                      flex h-8 w-8
                      items-center justify-center
                      rounded-lg
                      text-light-text-soft
                      transition-colors
                      hover:bg-brand-teal/10
                      hover:text-light-text
                      dark:text-dark-text-soft
                      dark:hover:bg-brand-teal/15
                      dark:hover:text-dark-text
                    "
                    aria-label="Remove attached music"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>

                <div
                  className="
                    flex items-center gap-4
                    px-4 py-4
                  "
                >
                  <div
                    className="
                      relative h-14 w-14
                      shrink-0
                      overflow-hidden
                      rounded-xl
                      bg-light-surface-muted
                      dark:bg-dark-surface-muted
                    "
                  >
                    {selectedTarget.artwork ? (
                      <Image
                        src={
                          selectedTarget.artwork
                        }
                        alt={`${selectedTarget.title} artwork`}
                        fill
                        sizes="56px"
                        className="object-cover"
                      />
                    ) : (
                      <div
                        className="
                          flex h-full w-full
                          items-center justify-center
                          text-light-text-soft
                          dark:text-dark-text-soft
                        "
                      >
                        {(() => {
                          const Icon =
                            getEntityIcon(
                              selectedTarget.target_type,
                            );

                          return (
                            <Icon className="h-6 w-6" />
                          );
                        })()}
                      </div>
                    )}
                  </div>

                  <div className="min-w-0 flex-1">
                    <p
                      className="
                        truncate text-sm font-bold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      {selectedTarget.title}
                    </p>

                    <p
                      className="
                        mt-1 truncate text-xs
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      {selectedTarget.target_type ===
                      'artist'
                        ? 'Artist'
                        : getArtistNames(
                            selectedTarget,
                          ) ||
                          selectedTarget
                            .album
                            ?.title ||
                          getEntityLabel(
                            selectedTarget.target_type,
                          )}
                    </p>

                    {selectedTarget.target_type !==
                      'artist' &&
                      selectedTarget.album && (
                        <p
                          className="
                            mt-0.5 truncate text-[11px]
                            text-light-text-soft
                            dark:text-dark-text-soft
                          "
                        >
                          {
                            selectedTarget
                              .album.title
                          }
                        </p>
                      )}
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={
                  handleOpenMusicPicker
                }
                disabled={
                  isSubmitting
                }
                className="
                  mt-3 inline-flex
                  items-center gap-1.5
                  text-xs font-semibold
                  text-brand-teal-dark
                  transition-colors
                  hover:text-brand-teal
                  dark:text-brand-teal-light
                "
              >
                <Plus className="h-3.5 w-3.5" />
                Change music
              </button>
            </div>
          )}
        </div>

        {/* Rating */}
        {selectedTarget &&
          canRate && (
            <div
              className="
                border-t
                border-light-border-soft
                px-5 py-5
                dark:border-dark-border-soft
                sm:px-7
              "
            >
              <div
                className="
                  flex flex-col gap-3
                  sm:flex-row
                  sm:items-center
                  sm:justify-between
                "
              >
                <div>
                  <p
                    className="
                      text-sm font-bold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Add a rating
                  </p>

                  <p
                    className="
                      mt-0.5 text-xs
                      text-light-text-muted
                      dark:text-dark-text-muted
                    "
                  >
                    Optional. Rate it from
                    0.5 to 5 stars.
                  </p>
                </div>

                <div
                  className="
                    flex min-h-9
                    items-center
                  "
                >
                  <div
                    role="radiogroup"
                    aria-label="Music rating"
                    onMouseMove={
                      handleRatingHover
                    }
                    onMouseLeave={() =>
                      setHoverRating(null)
                    }
                    onClick={
                      handleRatingClick
                    }
                    className="
                      flex
                      h-9
                      w-[180px]
                      shrink-0
                      cursor-pointer
                      items-center
                      gap-0
                      rounded-lg
                      outline-none
                    "
                  >
                    {[1, 2, 3, 4, 5].map(
                      (star) =>
                        renderRatingStar(
                          star,
                        ),
                    )}
                  </div>

                  <span
                    className="
                      ml-2
                      inline-flex
                      w-9
                      justify-center
                      text-sm font-bold
                      tabular-nums
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    {displayedRating !==
                    null
                      ? displayedRating.toFixed(
                          1,
                        )
                      : '—'}
                  </span>

                  {rating !== null && (
                    <button
                      type="button"
                      onClick={() => {
                        setRating(
                          null,
                        );
                        setHoverRating(
                          null,
                        );
                      }}
                      disabled={
                        isSubmitting
                      }
                      className="
                        ml-1 rounded-lg
                        px-2 py-1.5
                        text-xs font-semibold
                        text-light-text-soft
                        transition-colors
                        hover:bg-light-surface-soft
                        hover:text-light-text
                        dark:text-dark-text-soft
                        dark:hover:bg-dark-surface-soft
                        dark:hover:text-dark-text
                      "
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

        {/* Footer */}
        <div
          className="
            flex flex-col-reverse gap-3
            border-t
            border-light-border-soft
            bg-light-surface-soft/50
            px-5 py-4
            dark:border-dark-border-soft
            dark:bg-dark-surface-soft/30
            sm:flex-row
            sm:items-center
            sm:justify-between
            sm:px-7
          "
        >
          <Link
            href="/music"
            className="
              inline-flex min-h-11
              items-center justify-center
              rounded-xl
              px-4
              text-sm font-semibold
              text-light-text-muted
              transition-colors
              hover:bg-light-surface
              hover:text-light-text
              dark:text-dark-text-muted
              dark:hover:bg-dark-surface
              dark:hover:text-dark-text
            "
          >
            Cancel
          </Link>

          <button
            type="submit"
            disabled={
              isSubmitting ||
              !content.trim() ||
              importingProviderKey !== null
            }
            className="
              inline-flex min-h-11
              w-full
              items-center justify-center
              gap-2
              rounded-xl
              bg-brand-teal
              px-6
              text-sm font-bold
              text-white
              shadow-sm
              shadow-brand-teal/20
              transition-all duration-200
              hover:bg-brand-teal-dark
              active:scale-[0.99]
              focus:outline-none
              focus-visible:ring-4
              focus-visible:ring-brand-teal/20
              disabled:cursor-not-allowed
              disabled:opacity-50
              sm:w-auto
            "
          >
            {isSubmitting ? (
              <>
                <Loader2
                  className="
                    h-4 w-4
                    animate-spin
                  "
                />
                Posting...
              </>
            ) : (
              'Post'
            )}
          </button>
        </div>
      </section>
    </form>
  );
}