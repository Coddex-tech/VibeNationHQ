'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  AlertTriangleIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  MusicIcon,
  SearchIcon,
} from '@/components/Icons';
import {
  getMusicDiscovery,
  type MusicDiscoveryAlbum,
  type MusicDiscoveryArtist,
  type MusicDiscoveryResponse,
  type MusicDiscoverySong,
} from '@/lib/music/MusicDiscovery';

function MusicArtwork({
  src,
  alt,
  size = 'md',
}: {
  src: string | null;
  alt: string;
  size?: 'sm' | 'md' | 'lg';
}) {
  const sizeClass =
    size === 'sm'
      ? 'h-12 w-12 rounded-lg'
      : size === 'lg'
        ? 'h-32 w-32 rounded-xl sm:h-40 sm:w-40 sm:rounded-2xl'
        : 'h-16 w-16 rounded-xl';

  if (!src) {
    return (
      <div
        className={`
          ${sizeClass}
          flex shrink-0 items-center justify-center
          bg-brand-teal/10
          text-brand-teal
        `}
        aria-label={`${alt} artwork unavailable`}
      >
        <MusicIcon
          className={
            size === 'lg'
              ? 'h-8 w-8 sm:h-10 sm:w-10'
              : 'h-5 w-5'
          }
        />
      </div>
    );
  }

  return (
    <div
      className={`
        ${sizeClass}
        relative shrink-0 overflow-hidden
        bg-light-surface-soft
        dark:bg-dark-surface-soft
      `}
    >
      <Image
        src={src}
        alt={alt}
        fill
        sizes={
          size === 'lg'
            ? '(max-width: 640px) 128px, 160px'
            : size === 'sm'
              ? '48px'
              : '64px'
        }
        className="object-cover"
      />
    </div>
  );
}

function formatRating(
  rating: number | null,
) {
  if (
    rating === null ||
    Number.isNaN(rating)
  ) {
    return null;
  }

  return rating.toFixed(1);
}

function SongCard({
  song,
}: {
  song: MusicDiscoverySong;
}) {
  const artistNames = song.artists
    .map((artist) => artist.name)
    .join(', ');

  const rating = formatRating(
    song.average_rating,
  );

  return (
    <Link
      href={`/music/songs/${song.slug}`}
      className="
        group
        flex min-w-0 gap-3
        rounded-xl
        border border-light-border-soft
        bg-light-surface-soft
        p-3
        transition-all duration-200
        hover:-translate-y-0.5
        hover:border-brand-teal/30
        hover:bg-light-surface
        hover:shadow-md hover:shadow-black/[0.04]
        focus:outline-none
        focus:ring-4
        focus:ring-brand-teal/10
        dark:border-dark-border-soft
        dark:bg-dark-surface-soft
        dark:hover:border-brand-teal/30
        dark:hover:bg-dark-surface
        dark:hover:shadow-black/20
        dark:focus:ring-brand-teal/15
      "
    >
      <MusicArtwork
        src={song.artwork}
        alt={`${song.title} artwork`}
      />

      <div className="min-w-0 flex-1 py-0.5">
        <div className="flex items-start gap-2">
          <h3
            className="
              min-w-0 flex-1
              truncate
              text-sm font-bold
              text-light-text
              dark:text-dark-text
            "
          >
            {song.title}
          </h3>

          <ArrowRightIcon
            className="
              mt-0.5 h-4 w-4 shrink-0
              text-light-text-soft
              transition-transform
              group-hover:translate-x-0.5
              dark:text-dark-text-soft
            "
          />
        </div>

        <p
          className="
            mt-1 truncate
            text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {artistNames || 'Unknown artist'}
        </p>

        <div
          className="
            mt-2 flex flex-wrap
            items-center gap-x-3 gap-y-1
          "
        >
          {song.duration_display && (
            <span
              className="
                text-[11px] font-medium
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {song.duration_display}
            </span>
          )}

          {rating && (
            <span
              className="
                inline-flex items-center gap-1
                text-[11px] font-semibold
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              <CheckCircleIcon className="h-3.5 w-3.5" />
              {rating}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

function AlbumCard({
  album,
}: {
  album: MusicDiscoveryAlbum;
}) {
  const artistNames = album.artists
    .map((artist) => artist.name)
    .join(', ');

  const rating = formatRating(
    album.average_rating,
  );

  return (
    <Link
      href={`/music/albums/${album.slug}`}
      className="
        group
        flex min-w-0 gap-3
        rounded-xl
        border border-light-border-soft
        bg-light-surface-soft
        p-3
        transition-all duration-200
        hover:-translate-y-0.5
        hover:border-brand-teal/30
        hover:bg-light-surface
        hover:shadow-md hover:shadow-black/[0.04]
        focus:outline-none
        focus:ring-4
        focus:ring-brand-teal/10
        dark:border-dark-border-soft
        dark:bg-dark-surface-soft
        dark:hover:border-brand-teal/30
        dark:hover:bg-dark-surface
        dark:hover:shadow-black/20
        dark:focus:ring-brand-teal/15
      "
    >
      <MusicArtwork
        src={album.artwork}
        alt={`${album.title} artwork`}
      />

      <div className="min-w-0 flex-1 py-0.5">
        <div className="flex items-start gap-2">
          <h3
            className="
              min-w-0 flex-1
              truncate
              text-sm font-bold
              text-light-text
              dark:text-dark-text
            "
          >
            {album.title}
          </h3>

          <ArrowRightIcon
            className="
              mt-0.5 h-4 w-4 shrink-0
              text-light-text-soft
              transition-transform
              group-hover:translate-x-0.5
              dark:text-dark-text-soft
            "
          />
        </div>

        <p
          className="
            mt-1 truncate
            text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {artistNames || 'Unknown artist'}
        </p>

        {rating && (
          <div
            className="
              mt-2 inline-flex
              items-center gap-1
              text-[11px] font-semibold
              text-brand-teal-dark
              dark:text-brand-teal-light
            "
          >
            <CheckCircleIcon className="h-3.5 w-3.5" />
            {rating}
          </div>
        )}
      </div>
    </Link>
  );
}

function ArtistCard({
  artist,
}: {
  artist: MusicDiscoveryArtist;
}) {
  return (
    <Link
      href={`/music/artists/${artist.slug}`}
      className="
        group
        flex min-w-0 items-center gap-3
        rounded-xl
        border border-light-border-soft
        bg-light-surface-soft
        p-3
        transition-all duration-200
        hover:-translate-y-0.5
        hover:border-brand-teal/30
        hover:bg-light-surface
        hover:shadow-md hover:shadow-black/[0.04]
        focus:outline-none
        focus:ring-4
        focus:ring-brand-teal/10
        dark:border-dark-border-soft
        dark:bg-dark-surface-soft
        dark:hover:border-brand-teal/30
        dark:hover:bg-dark-surface
        dark:hover:shadow-black/20
        dark:focus:ring-brand-teal/15
      "
    >
      {artist.profile_image ? (
        <div
          className="
            relative h-12 w-12
            shrink-0 overflow-hidden
            rounded-full
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        >
          <Image
            src={artist.profile_image}
            alt={artist.name}
            fill
            sizes="48px"
            className="object-cover"
          />
        </div>
      ) : (
        <div
          className="
            flex h-12 w-12 shrink-0
            items-center justify-center
            rounded-full
            bg-brand-teal/10
            text-brand-teal
          "
        >
          <MusicIcon className="h-5 w-5" />
        </div>
      )}

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h3
            className="
              min-w-0 truncate
              text-sm font-bold
              text-light-text
              dark:text-dark-text
            "
          >
            {artist.name}
          </h3>

          {artist.is_verified && (
            <CheckCircleIcon
              className="
                h-4 w-4 shrink-0
                text-brand-teal
              "
              aria-label="Verified artist"
            />
          )}
        </div>

        <p
          className="
            mt-1 text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {artist.followers_count.toLocaleString()}
          {' '}
          {artist.followers_count === 1
            ? 'follower'
            : 'followers'}
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
  );
}

function SectionHeading({
  eyebrow,
  title,
  href,
}: {
  eyebrow: string;
  title: string;
  href?: string;
}) {
  return (
    <div
      className="
        flex flex-col gap-3
        sm:flex-row sm:items-end
        sm:justify-between
      "
    >
      <div>
        <div
          className="
            mb-2 inline-flex items-center gap-2
            text-xs font-bold uppercase tracking-wider
            text-brand-teal-dark
            dark:text-brand-teal-light
          "
        >
          <MusicIcon className="h-4 w-4" />
          {eyebrow}
        </div>

        <h2
          className="
            text-xl font-black tracking-tight
            text-light-text
            dark:text-dark-text
            sm:text-2xl
          "
        >
          {title}
        </h2>
      </div>

      {href && (
        <Link
          href={href}
          className="
            inline-flex shrink-0
            items-center gap-2
            text-sm font-bold
            text-brand-teal-dark
            transition-colors
            hover:text-brand-teal
            dark:text-brand-teal-light
            dark:hover:text-brand-teal
          "
        >
          View all
          <ArrowRightIcon className="h-4 w-4" />
        </Link>
      )}
    </div>
  );
}

function SongSkeleton() {
  return (
    <div
      className="
        animate-pulse
        flex gap-3
        rounded-xl
        border border-light-border-soft
        bg-light-surface-soft
        p-3
        dark:border-dark-border-soft
        dark:bg-dark-surface-soft
      "
    >
      <div
        className="
          h-16 w-16 shrink-0
          rounded-xl
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      />

      <div className="min-w-0 flex-1 py-1">
        <div
          className="
            h-4 w-3/4 max-w-48 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-2 h-3 w-1/2 max-w-32 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-3 h-3 w-20 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />
      </div>
    </div>
  );
}

function ArtistSkeleton() {
  return (
    <div
      className="
        animate-pulse
        flex items-center gap-3
        rounded-xl
        border border-light-border-soft
        bg-light-surface-soft
        p-3
        dark:border-dark-border-soft
        dark:bg-dark-surface-soft
      "
    >
      <div
        className="
          h-12 w-12 shrink-0 rounded-full
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      />

      <div className="min-w-0 flex-1">
        <div
          className="
            h-4 w-3/4 max-w-40 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-2 h-3 w-24 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />
      </div>
    </div>
  );
}

function AlbumSkeleton() {
  return (
    <div
      className="
        animate-pulse
        flex gap-3
        rounded-xl
        border border-light-border-soft
        bg-light-surface-soft
        p-3
        dark:border-dark-border-soft
        dark:bg-dark-surface-soft
      "
    >
      <div
        className="
          h-16 w-16 shrink-0 rounded-xl
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      />

      <div className="min-w-0 flex-1 py-1">
        <div
          className="
            h-4 w-3/4 max-w-44 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-2 h-3 w-1/2 max-w-28 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-3 h-3 w-16 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />
      </div>
    </div>
  );
}

function DiscoverySkeleton() {
  return (
    <div className="mt-8 space-y-10">
      <section>
        <div
          className="
            animate-pulse
            h-6 w-40 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-4 grid gap-3
            sm:grid-cols-2
            lg:grid-cols-3
          "
        >
          {Array.from({ length: 6 }).map(
            (_, index) => (
              <SongSkeleton
                key={`song-${index}`}
              />
            ),
          )}
        </div>
      </section>

      <section>
        <div
          className="
            animate-pulse
            h-6 w-44 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-4 grid gap-3
            sm:grid-cols-2
            lg:grid-cols-3
          "
        >
          {Array.from({ length: 6 }).map(
            (_, index) => (
              <ArtistSkeleton
                key={`artist-${index}`}
              />
            ),
          )}
        </div>
      </section>

      <section>
        <div
          className="
            animate-pulse
            h-6 w-48 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-4 grid gap-3
            sm:grid-cols-2
            lg:grid-cols-3
          "
        >
          {Array.from({ length: 6 }).map(
            (_, index) => (
              <AlbumSkeleton
                key={`album-${index}`}
              />
            ),
          )}
        </div>
      </section>
    </div>
  );
}

export default function HomeMusicSection() {
  const [discovery, setDiscovery] =
    useState<MusicDiscoveryResponse | null>(
      null,
    );

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState('');

  useEffect(() => {
    let isMounted = true;

    const loadDiscovery = async () => {
      setIsLoading(true);
      setError('');

      try {
        const data =
          await getMusicDiscovery();

        if (!isMounted) {
          return;
        }

        setDiscovery(data);
      } catch {
        if (!isMounted) {
          return;
        }

        setError(
          'Unable to load music discovery right now.',
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadDiscovery();

    return () => {
      isMounted = false;
    };
  }, []);

  const trendingSongs =
    discovery?.trending_songs.slice(0, 6) ?? [];

  const trendingArtists =
    discovery?.trending_artists.slice(0, 6) ?? [];

  const featuredSongs =
    discovery?.featured_songs.slice(0, 3) ?? [];

  const featuredAlbums =
    discovery?.featured_albums.slice(0, 3) ?? [];

  const recentlyReleasedSongs =
    discovery?.recently_released_songs.slice(
      0,
      6,
    ) ?? [];

  const recentlyReleasedAlbums =
    discovery?.recently_released_albums.slice(
      0,
      6,
    ) ?? [];

  const hasDiscoveryContent =
    trendingSongs.length > 0 ||
    trendingArtists.length > 0 ||
    featuredSongs.length > 0 ||
    featuredAlbums.length > 0 ||
    recentlyReleasedSongs.length > 0 ||
    recentlyReleasedAlbums.length > 0;

  return (
    <section
      aria-labelledby="home-music-heading"
      className="
        border-b border-light-border
        bg-light-surface
        dark:border-dark-border
        dark:bg-dark-surface
      "
    >
      <div
        className="
          mx-auto w-full max-w-7xl
          px-5 py-14
          sm:px-6 sm:py-16
          lg:px-8 lg:py-20
        "
      >
        {/* Section heading */}
        <FadeIn>
          <div
            className="
              flex flex-col gap-5
              sm:flex-row sm:items-end
              sm:justify-between
            "
          >
            <div className="max-w-2xl">
              <div
                className="
                  mb-3 inline-flex items-center gap-2
                  text-xs font-bold uppercase tracking-wider
                  text-brand-teal-dark
                  dark:text-brand-teal-light
                "
              >
                <MusicIcon className="h-4 w-4" />
                Music
              </div>

              <h2
                id="home-music-heading"
                className="
                  text-2xl font-black tracking-tight
                  text-light-text
                  dark:text-dark-text
                  sm:text-3xl
                "
              >
                Find your next favorite.
              </h2>

              <p
                className="
                  mt-2 max-w-xl
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-base
                "
              >
                Explore songs, artists and albums,
                then join the conversation around the
                music you love.
              </p>
            </div>

            <Link
              href="/music"
              className="
                inline-flex shrink-0 items-center gap-2
                text-sm font-bold
                text-brand-teal-dark
                transition-colors
                hover:text-brand-teal
                dark:text-brand-teal-light
                dark:hover:text-brand-teal
              "
            >
              Explore Music HQ
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
          </div>
        </FadeIn>

        {/* Search entry */}
        <FadeIn delay={0.05}>
          <Link
            href="/music/search"
            className="
              group mt-8
              flex items-center gap-3
              rounded-2xl
              border border-light-border
              bg-light-bg
              px-4 py-4
              transition-all duration-200
              hover:border-brand-teal/30
              hover:bg-light-surface-soft
              focus:outline-none
              focus:ring-4
              focus:ring-brand-teal/10
              dark:border-dark-border
              dark:bg-dark-bg
              dark:hover:border-brand-teal/30
              dark:hover:bg-dark-surface-soft
              dark:focus:ring-brand-teal/15
              sm:px-5
            "
          >
            <div
              className="
                flex h-10 w-10 shrink-0
                items-center justify-center
                rounded-xl
                bg-brand-teal/10
                text-brand-teal
              "
            >
              <SearchIcon className="h-5 w-5" />
            </div>

            <div className="min-w-0 flex-1">
              <p
                className="
                  text-sm font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                Search VibeNation Music
              </p>

              <p
                className="
                  mt-0.5 truncate
                  text-xs
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                Find a song, artist or album.
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

        {isLoading ? (
          <FadeIn delay={0.08}>
            <DiscoverySkeleton />
          </FadeIn>
        ) : !hasDiscoveryContent ? (
          <FadeIn delay={0.08}>
            <div
              className="
                mt-8 rounded-2xl
                border border-light-border
                bg-light-bg
                px-5 py-10
                text-center
                dark:border-dark-border
                dark:bg-dark-bg
              "
            >
              <div
                className="
                  mx-auto flex h-12 w-12
                  items-center justify-center
                  rounded-xl
                  bg-brand-teal/10
                  text-brand-teal
                "
              >
                <MusicIcon className="h-6 w-6" />
              </div>

              <h3
                className="
                  mt-4 text-base font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                Music discovery is getting ready.
              </h3>

              <p
                className="
                  mx-auto mt-2 max-w-md
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                Explore the music catalog or search
                for a song, artist or album while new
                discoveries are being added.
              </p>

              <Link
                href="/music"
                className="
                  mt-5 inline-flex
                  items-center gap-2
                  rounded-xl
                  bg-brand-teal
                  px-4 py-2.5
                  text-sm font-bold text-white
                  transition-colors
                  hover:bg-brand-teal-dark
                  focus:outline-none
                  focus:ring-4
                  focus:ring-brand-teal/20
                "
              >
                Explore music
                <ArrowRightIcon className="h-4 w-4" />
              </Link>
            </div>
          </FadeIn>
        ) : (
          <div className="mt-10 space-y-12">
            {/* Trending songs */}
            {trendingSongs.length > 0 && (
              <FadeIn>
                <section>
                  <SectionHeading
                    eyebrow="Trending"
                    title="Songs people are discovering"
                    href="/music/songs"
                  />

                  <div
                    className="
                      mt-5 grid gap-3
                      sm:grid-cols-2
                      lg:grid-cols-3
                    "
                  >
                    {trendingSongs.map((song) => (
                      <SongCard
                        key={song.id}
                        song={song}
                      />
                    ))}
                  </div>
                </section>
              </FadeIn>
            )}

            {/* Trending artists */}
            {trendingArtists.length > 0 && (
              <FadeIn delay={0.04}>
                <section>
                  <SectionHeading
                    eyebrow="Artists"
                    title="Artists on the rise"
                    href="/music/artists"
                  />

                  <div
                    className="
                      mt-5 grid gap-3
                      sm:grid-cols-2
                      lg:grid-cols-3
                    "
                  >
                    {trendingArtists.map(
                      (artist) => (
                        <ArtistCard
                          key={artist.id}
                          artist={artist}
                        />
                      ),
                    )}
                  </div>
                </section>
              </FadeIn>
            )}

            {/* Featured */}
            {(featuredSongs.length > 0 ||
              featuredAlbums.length > 0) && (
              <FadeIn delay={0.06}>
                <section>
                  <SectionHeading
                    eyebrow="Featured"
                    title="Picked for the VibeNation community"
                  />

                  <div
                    className="
                      mt-5 grid gap-3
                      lg:grid-cols-2
                    "
                  >
                    {featuredSongs.length > 0 && (
                      <div className="space-y-3">
                        {featuredSongs.map(
                          (song) => (
                            <SongCard
                              key={song.id}
                              song={song}
                            />
                          ),
                        )}
                      </div>
                    )}

                    {featuredAlbums.length > 0 && (
                      <div className="space-y-3">
                        {featuredAlbums.map(
                          (album) => (
                            <AlbumCard
                              key={album.id}
                              album={album}
                            />
                          ),
                        )}
                      </div>
                    )}
                  </div>
                </section>
              </FadeIn>
            )}

            {/* Recently released */}
            {(recentlyReleasedSongs.length > 0 ||
              recentlyReleasedAlbums.length > 0) && (
              <FadeIn delay={0.08}>
                <section>
                  <SectionHeading
                    eyebrow="Fresh releases"
                    title="Recently released"
                  />

                  <div
                    className="
                      mt-5 grid gap-3
                      lg:grid-cols-2
                    "
                  >
                    {recentlyReleasedSongs.length >
                      0 && (
                      <div className="space-y-3">
                        {recentlyReleasedSongs.map(
                          (song) => (
                            <SongCard
                              key={song.id}
                              song={song}
                            />
                          ),
                        )}
                      </div>
                    )}

                    {recentlyReleasedAlbums.length >
                      0 && (
                      <div className="space-y-3">
                        {recentlyReleasedAlbums.map(
                          (album) => (
                            <AlbumCard
                              key={album.id}
                              album={album}
                            />
                          ),
                        )}
                      </div>
                    )}
                  </div>
                </section>
              </FadeIn>
            )}
          </div>
        )}

        {/* Bottom discovery prompt */}
        <FadeIn delay={0.12}>
          <div
            className="
              mt-12
              rounded-2xl
              border border-brand-teal/20
              bg-brand-teal/[0.06]
              px-5 py-6
              dark:border-brand-teal/20
              dark:bg-brand-teal/[0.07]
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
                <p
                  className="
                    text-sm font-bold
                    text-brand-teal-dark
                    dark:text-brand-teal-light
                  "
                >
                  Your music community starts here.
                </p>

                <p
                  className="
                    mt-1 text-sm leading-6
                    text-light-text-muted
                    dark:text-dark-text-muted
                  "
                >
                  Search for music, discover something
                  new, and share what you think.
                </p>
              </div>

              <Link
                href="/music"
                className="
                  inline-flex shrink-0
                  items-center justify-center gap-2
                  rounded-xl
                  bg-brand-teal
                  px-4 py-2.5
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
                Explore Music HQ
                <ArrowRightIcon className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}