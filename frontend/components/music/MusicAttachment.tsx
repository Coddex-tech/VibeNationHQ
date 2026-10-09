'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  Album,
  Disc3,
  ExternalLink,
  LoaderCircle,
  Music2,
  Pause,
  Play,
  UserRound,
} from 'lucide-react';
import {
  useEffect,
  useRef,
  useState,
} from 'react';

import { apiRequest } from '@/lib/api';

import type {
  CommunityAlbum,
  CommunityArtist,
  CommunityPostTarget,
  CommunitySong,
} from '@/lib/music/CommunityPosts';

/**
 * Only one music preview may be active at a time.
 *
 * The currently active audio element is stored here so
 * another PreviewButton can stop it before starting.
 */
let activePreviewAudio:
  HTMLAudioElement | null = null;

/**
 * Allows the currently active PreviewButton to immediately
 * clear its own loading/playing state when another preview
 * takes over.
 */
let stopActivePreview:
  (() => void) | null = null;

type MusicAttachmentProps = {
  target: CommunityPostTarget;
};

export default function MusicAttachment({
  target,
}: MusicAttachmentProps) {
  if (target.target_type === 'song' && target.song) {
    return (
      <SongAttachment
        song={target.song}
        previewUrl={target.preview_url}
      />
    );
  }

  if (target.target_type === 'album' && target.album) {
    return (
      <AlbumAttachment album={target.album} />
    );
  }

  if (
    target.target_type === 'artist' &&
    target.artist
  ) {
    return (
      <ArtistAttachment artist={target.artist} />
    );
  }

  if (target.target_type === 'external') {
    return <ExternalAttachment target={target} />;
  }

  return null;
}

function SongAttachment({
  song,
  previewUrl,
}: {
  song: CommunitySong;
  previewUrl: string | null;
}) {
  const primaryArtist =
    song.artists[0]?.name ?? 'Unknown artist';

  const artistNames =
    song.artists
      .map((artist) => artist.name)
      .join(', ') || primaryArtist;

  return (
    <div
      className="
        overflow-hidden
        rounded-2xl
        border border-light-border
        bg-light-surface-soft
        transition-colors duration-200
        dark:border-dark-border
        dark:bg-dark-surface-soft
      "
    >
      <div className="flex items-center gap-3.5 p-3.5 sm:gap-4 sm:p-4">
        <Link
          href={`/music/songs/${song.slug}`}
          aria-label={`View ${song.title}`}
          className="
            shrink-0
            rounded-xl
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/20
          "
        >
          <Artwork
            src={song.artwork}
            alt={`${song.title} artwork`}
            size="song"
          />
        </Link>

        <div className="min-w-0 flex-1">
          <div
            className="
              flex items-center gap-2
              text-[11px] font-semibold uppercase
              tracking-wide
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            <Music2
              className="h-3.5 w-3.5 shrink-0"
              strokeWidth={2}
            />
            Song
          </div>

          <Link
            href={`/music/songs/${song.slug}`}
            className="
              mt-1 block truncate
              text-sm font-bold
              text-light-text
              transition-colors
              hover:text-brand-teal-dark
              dark:text-dark-text
              dark:hover:text-brand-teal-light
              sm:text-[15px]
            "
          >
            {song.title}
          </Link>

          <p
            className="
              mt-1 truncate
              text-xs leading-5
              text-light-text-muted
              dark:text-dark-text-muted
            "
            title={artistNames}
          >
            {artistNames}
          </p>

          {song.duration_display && (
            <p
              className="
                mt-1 text-[11px]
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {song.duration_display}
            </p>
          )}
        </div>

        <PreviewButton
          label={`Play preview of ${song.title}`}
          previewUrl={previewUrl}
          songId={song.id}
        />
      </div>
    </div>
  );
}

function AlbumAttachment({
  album,
}: {
  album: CommunityAlbum;
}) {
  const artistNames =
    album.artists
      .map((artist) => artist.name)
      .join(', ') || 'Unknown artist';

  return (
    <div
      className="
        overflow-hidden
        rounded-2xl
        border border-light-border
        bg-light-surface-soft
        transition-colors duration-200
        dark:border-dark-border
        dark:bg-dark-surface-soft
      "
    >
      <div className="flex items-center gap-3.5 p-3.5 sm:gap-4 sm:p-4">
        <Link
          href={`/music/albums/${album.slug}`}
          aria-label={`View ${album.title}`}
          className="
            shrink-0
            rounded-xl
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/20
          "
        >
          <Artwork
            src={album.artwork}
            alt={`${album.title} artwork`}
            size="album"
          />
        </Link>

        <div className="min-w-0 flex-1">
          <div
            className="
              flex items-center gap-2
              text-[11px] font-semibold uppercase
              tracking-wide
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            <Album
              className="h-3.5 w-3.5 shrink-0"
              strokeWidth={2}
            />
            Album
          </div>

          <Link
            href={`/music/albums/${album.slug}`}
            className="
              mt-1 block truncate
              text-sm font-bold
              text-light-text
              transition-colors
              hover:text-brand-teal-dark
              dark:text-dark-text
              dark:hover:text-brand-teal-light
              sm:text-[15px]
            "
          >
            {album.title}
          </Link>

          <p
            className="
              mt-1 truncate
              text-xs leading-5
              text-light-text-muted
              dark:text-dark-text-muted
            "
            title={artistNames}
          >
            {artistNames}
          </p>

          <p
            className="
              mt-1 text-[11px]
              text-light-text-soft
              dark:text-dark-text-soft
            "
          >
            {formatReleaseType(album.release_type)}
          </p>
        </div>

        <Link
          href={`/music/albums/${album.slug}`}
          aria-label={`View ${album.title}`}
          className="
            flex h-10 w-10 shrink-0
            items-center justify-center
            rounded-full
            bg-light-surface
            text-light-text-muted
            transition-colors duration-200
            hover:bg-brand-teal
            hover:text-white
            dark:bg-dark-surface
            dark:text-dark-text-muted
            dark:hover:bg-brand-teal
            dark:hover:text-white
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/20
          "
        >
          <Disc3
            className="h-[18px] w-[18px]"
            strokeWidth={1.9}
          />
        </Link>
      </div>
    </div>
  );
}

function ArtistAttachment({
  artist,
}: {
  artist: CommunityArtist;
}) {
  return (
    <div
      className="
        overflow-hidden
        rounded-2xl
        border border-light-border
        bg-light-surface-soft
        transition-colors duration-200
        dark:border-dark-border
        dark:bg-dark-surface-soft
      "
    >
      <div className="flex items-center gap-3.5 p-3.5 sm:gap-4 sm:p-4">
        <Link
          href={`/music/artists/${artist.slug}`}
          aria-label={`View ${artist.name}`}
          className="
            shrink-0
            rounded-full
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/20
          "
        >
          <Artwork
            src={artist.profile_image}
            alt={`${artist.name} profile`}
            size="artist"
            rounded
          />
        </Link>

        <div className="min-w-0 flex-1">
          <div
            className="
              flex items-center gap-2
              text-[11px] font-semibold uppercase
              tracking-wide
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            <UserRound
              className="h-3.5 w-3.5 shrink-0"
              strokeWidth={2}
            />
            Artist
          </div>

          <Link
            href={`/music/artists/${artist.slug}`}
            className="
              mt-1 block truncate
              text-sm font-bold
              text-light-text
              transition-colors
              hover:text-brand-teal-dark
              dark:text-dark-text
              dark:hover:text-brand-teal-light
              sm:text-[15px]
            "
          >
            {artist.name}
          </Link>

          <div
            className="
              mt-1 flex min-w-0 items-center gap-2
              text-xs
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            <span className="truncate">
              {formatFollowerCount(
                artist.followers_count,
              )}{' '}
              followers
            </span>

            {artist.is_verified && (
              <span
                className="
                  inline-flex shrink-0 items-center
                  rounded-full
                  bg-brand-teal/10
                  px-1.5 py-0.5
                  text-[10px] font-bold
                  text-brand-teal-dark
                  dark:bg-brand-teal/15
                  dark:text-brand-teal-light
                "
              >
                Verified
              </span>
            )}
          </div>
        </div>

        <Link
          href={`/music/artists/${artist.slug}`}
          className="
            inline-flex min-h-10 shrink-0
            items-center justify-center
            rounded-xl
            bg-brand-teal
            px-3.5
            text-xs font-bold
            text-white
            transition-colors duration-200
            hover:bg-brand-teal-dark
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/20
          "
        >
          View
        </Link>
      </div>
    </div>
  );
}

function ExternalAttachment({
  target,
}: {
  target: CommunityPostTarget;
}) {
  const title =
    target.title?.trim() || 'Music';

  const artist =
    target.artist_name?.trim() ||
    'Unknown artist';

  return (
    <div
      className="
        overflow-hidden
        rounded-2xl
        border border-light-border
        bg-light-surface-soft
        transition-colors duration-200
        dark:border-dark-border
        dark:bg-dark-surface-soft
      "
    >
      <div className="flex items-center gap-3.5 p-3.5 sm:gap-4 sm:p-4">
        <Artwork
          src={target.artwork_url}
          alt={`${title} artwork`}
          size="song"
        />

        <div className="min-w-0 flex-1">
          <div
            className="
              flex items-center gap-2
              text-[11px] font-semibold uppercase
              tracking-wide
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            <Music2
              className="h-3.5 w-3.5 shrink-0"
              strokeWidth={2}
            />
            {target.external_provider ||
              'External music'}
          </div>

          <p
            className="
              mt-1 truncate
              text-sm font-bold
              text-light-text
              dark:text-dark-text
              sm:text-[15px]
            "
          >
            {title}
          </p>

          <p
            className="
              mt-1 truncate
              text-xs leading-5
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            {artist}
          </p>
        </div>

        {target.preview_url ? (
          <PreviewButton
            label={`Play preview of ${title}`}
            previewUrl={target.preview_url}
          />
        ) : (
          <ExternalLink
            className="
              h-5 w-5 shrink-0
              text-light-text-soft
              dark:text-dark-text-soft
            "
          />
        )}
      </div>
    </div>
  );
}

function Artwork({
  src,
  alt,
  size,
  rounded = false,
}: {
  src: string | null;
  alt: string;
  size: 'song' | 'album' | 'artist';
  rounded?: boolean;
}) {
  const sizeClasses = {
    song: 'h-16 w-16 sm:h-[72px] sm:w-[72px]',
    album: 'h-16 w-16 sm:h-[72px] sm:w-[72px]',
    artist: 'h-16 w-16 sm:h-[72px] sm:w-[72px]',
  };

  return (
    <div
      className={`
        relative shrink-0 overflow-hidden
        ${sizeClasses[size]}
        ${rounded ? 'rounded-full' : 'rounded-xl'}
        bg-light-surface-muted
        shadow-sm
        dark:bg-dark-surface-muted
      `}
    >
      {src ? (
        <Image
          src={src}
          alt={alt}
          fill
          sizes="72px"
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
          aria-hidden="true"
        >
          {size === 'artist' ? (
            <UserRound
              className="h-6 w-6"
              strokeWidth={1.7}
            />
          ) : (
            <Music2
              className="h-6 w-6"
              strokeWidth={1.7}
            />
          )}
        </div>
      )}
    </div>
  );
}

function PreviewButton({
  label,
  previewUrl,
  songId,
}: {
  label: string;
  previewUrl: string | null;
  songId?: number;
}) {
  const audioRef =
    useRef<HTMLAudioElement | null>(null);

  const loadingTimeoutRef =
    useRef<ReturnType<typeof setTimeout> | null>(
      null,
    );

  const playRequestRef =
    useRef(0);

  const [isPlaying, setIsPlaying] =
    useState(false);

  const [isLoading, setIsLoading] =
    useState(false);

  const [hasError, setHasError] =
    useState(false);

  const [progress, setProgress] =
    useState(0);

  const clearLoadingTimeout = () => {
    if (loadingTimeoutRef.current !== null) {
      clearTimeout(
        loadingTimeoutRef.current,
      );

      loadingTimeoutRef.current = null;
    }
  };

  const stopThisPreview = () => {
    playRequestRef.current += 1;

    clearLoadingTimeout();

    const audio = audioRef.current;

    if (audio) {
      audio.pause();
    }

    setIsPlaying(false);
    setIsLoading(false);
  };

  useEffect(() => {
    return () => {
      playRequestRef.current += 1;

      clearLoadingTimeout();

      const audio = audioRef.current;

      if (audio) {
        if (activePreviewAudio === audio) {
          activePreviewAudio = null;
          stopActivePreview = null;
        }

        audio.pause();
        audio.removeAttribute('src');
        audio.load();
      }
    };
  }, []);

  const recordPreviewPlay = () => {
    if (songId === undefined) {
      return;
    }

    void apiRequest(
      '/api/v1/music/feed/interactions/',
      {
        method: 'POST',
        body: JSON.stringify({
          interaction_type: 'play_preview',
          target_type: 'song',
          target_id: songId,
          idempotency_key:
            crypto.randomUUID(),
        }),
      },
    ).catch(() => {
      /*
       * Playback must never fail because
       * interaction tracking failed.
       */
    });
  };

  const handleTogglePlayback =
    async () => {
      const audio = audioRef.current;

      if (!audio) {
        return;
      }

      if (isLoading) {
        return;
      }

      setHasError(false);

      if (!previewUrl) {
        setHasError(true);
        return;
      }

      /*
       * Clicking the currently playing preview
       * pauses it without resetting progress.
       */
      if (!audio.paused) {
        audio.pause();
        return;
      }

      /*
       * If this preview finished previously,
       * start it again from the beginning.
       */
      if (audio.ended) {
        audio.currentTime = 0;
        setProgress(0);
      }

      /*
       * Stop the previous preview first.
       *
       * This also clears its loading state if it
       * was still waiting for the network.
       */
      if (
        activePreviewAudio &&
        activePreviewAudio !== audio
      ) {
        stopActivePreview?.();

        activePreviewAudio.pause();
      }

      /*
       * This preview is now the only active one.
       */
      activePreviewAudio = audio;
      stopActivePreview = stopThisPreview;

      /*
       * Invalidate any previous play attempt belonging
       * to this component.
       */
      const requestId =
        ++playRequestRef.current;

      setIsLoading(true);

      /*
       * If playback hasn't actually started after
       * 12 seconds, don't leave the user staring at
       * an infinite spinner.
       */
      clearLoadingTimeout();

      loadingTimeoutRef.current =
        setTimeout(() => {
          if (
            playRequestRef.current !==
            requestId
          ) {
            return;
          }

          audio.pause();

          setIsPlaying(false);
          setIsLoading(false);
          setHasError(true);

          if (
            activePreviewAudio === audio
          ) {
            activePreviewAudio = null;
            stopActivePreview = null;
          }
        }, 12_000);

      try {
        /*
         * Reset the source only when necessary.
         *
         * We intentionally don't call load() here because
         * doing so every time can introduce unnecessary
         * network/loading delays.
         */
        if (
          audio.src !== previewUrl
        ) {
          audio.src = previewUrl;
          audio.load();
        }

        await audio.play();

        /*
         * A different preview may have taken over
         * while this play() promise was resolving.
         */
        if (
          playRequestRef.current !==
          requestId
        ) {
          return;
        }
      } catch {
        if (
          playRequestRef.current !==
          requestId
        ) {
          return;
        }

        clearLoadingTimeout();

        setIsPlaying(false);
        setIsLoading(false);
        setHasError(true);

        if (
          activePreviewAudio === audio
        ) {
          activePreviewAudio = null;
          stopActivePreview = null;
        }
      }
    };

  const handlePlay = () => {
    const audio = audioRef.current;

    if (!audio) {
      return;
    }

    /*
     * Safety net: if the browser starts this audio
     * independently, stop whatever was previously active.
     */
    if (
      activePreviewAudio &&
      activePreviewAudio !== audio
    ) {
      stopActivePreview?.();
      activePreviewAudio.pause();
    }

    activePreviewAudio = audio;
    stopActivePreview = stopThisPreview;

    clearLoadingTimeout();

    setIsLoading(false);
    setIsPlaying(true);
    setHasError(false);

    recordPreviewPlay();
  };

  const handlePlaying = () => {
    clearLoadingTimeout();

    setIsLoading(false);
    setIsPlaying(true);
  };

  const handlePause = () => {
    clearLoadingTimeout();

    setIsPlaying(false);
    setIsLoading(false);

    const audio = audioRef.current;

    if (
      audio &&
      activePreviewAudio === audio
    ) {
      activePreviewAudio = null;
      stopActivePreview = null;
    }
  };

  const handleTimeUpdate = () => {
    const audio = audioRef.current;

    if (
      !audio ||
      !Number.isFinite(audio.duration) ||
      audio.duration <= 0
    ) {
      return;
    }

    setProgress(
      Math.min(
        Math.max(
          audio.currentTime /
            audio.duration,
          0,
        ),
        1,
      ),
    );
  };

  const handleEnded = () => {
    clearLoadingTimeout();

    setIsPlaying(false);
    setIsLoading(false);
    setProgress(0);

    const audio = audioRef.current;

    if (
      audio &&
      activePreviewAudio === audio
    ) {
      activePreviewAudio = null;
      stopActivePreview = null;
    }
  };

  const handleError = () => {
    clearLoadingTimeout();

    setIsPlaying(false);
    setIsLoading(false);
    setProgress(0);
    setHasError(true);

    const audio = audioRef.current;

    if (
      audio &&
      activePreviewAudio === audio
    ) {
      activePreviewAudio = null;
      stopActivePreview = null;
    }
  };

  const circumference =
    2 * Math.PI * 21;

  const progressOffset =
    circumference -
    progress * circumference;

  const cleanLabel = label
    .replace(/^Play preview of /, '')
    .replace(/^Pause preview of /, '');

  return (
    <>
      <audio
        ref={audioRef}
        src={previewUrl ?? undefined}
        preload="metadata"
        onPlay={handlePlay}
        onPlaying={handlePlaying}
        onPause={handlePause}
        onTimeUpdate={handleTimeUpdate}
        onEnded={handleEnded}
        onError={handleError}
      />

      <div
        className="
          relative
          h-11 w-11
          shrink-0
        "
      >
        <svg
          className="
            pointer-events-none
            absolute
            inset-0
            h-full
            w-full
            -rotate-90
          "
          viewBox="0 0 46 46"
          aria-hidden="true"
        >
          <circle
            cx="23"
            cy="23"
            r="21"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-brand-teal/20"
          />

          <circle
            cx="23"
            cy="23"
            r="21"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            className="
              text-brand-teal
              transition-[stroke-dashoffset]
              duration-100
              ease-linear
            "
            strokeDasharray={circumference}
            strokeDashoffset={progressOffset}
          />
        </svg>

        <button
          type="button"
          onClick={handleTogglePlayback}
          disabled={isLoading}
          aria-label={
            hasError
              ? `Preview unavailable for ${cleanLabel}`
              : isPlaying
                ? `Pause preview of ${cleanLabel}`
                : label
          }
          title={
            hasError
              ? 'Preview unavailable'
              : undefined
          }
          className="
            absolute
            left-1/2
            top-1/2
            flex
            h-10
            w-10
            -translate-x-1/2
            -translate-y-1/2
            items-center
            justify-center
            rounded-full
            bg-brand-teal
            text-white
            shadow-sm
            shadow-brand-teal/20
            transition-colors duration-200
            hover:bg-brand-teal-dark
            active:scale-[0.98]
            disabled:cursor-wait
            disabled:opacity-80
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/20
          "
        >
          {isLoading ? (
            <LoaderCircle
              className="
                h-[17px]
                w-[17px]
                animate-spin
              "
              strokeWidth={1.9}
            />
          ) : isPlaying ? (
            <Pause
              className="
                h-[17px]
                w-[17px]
              "
              fill="currentColor"
              strokeWidth={1.8}
            />
          ) : (
            <Play
              className="
                ml-0.5
                h-[17px]
                w-[17px]
              "
              fill="currentColor"
              strokeWidth={1.8}
            />
          )}
        </button>
      </div>
    </>
  );
}

function formatFollowerCount(
  count: number,
): string {
  if (count < 1000) {
    return String(count);
  }

  if (count < 1_000_000) {
    return `${(count / 1000).toFixed(
      count >= 10_000 ? 0 : 1,
    )}K`;
  }

  return `${(count / 1_000_000).toFixed(
    count >= 10_000_000 ? 0 : 1,
  )}M`;
}

function formatReleaseType(
  releaseType: string,
): string {
  if (!releaseType) {
    return 'Release';
  }

  return releaseType
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}