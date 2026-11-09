'use client';

import Image from 'next/image';
import Link from 'next/link';
import {
  useCallback,
  useEffect,
  useState,
} from 'react';
import type { ReactNode } from 'react';
import {
  AlertCircle,
  ArrowRight,
  Disc3,
  Flame,
  Music2,
  RefreshCw,
  Sparkles,
  Star,
  Users,
} from 'lucide-react';

import { getMediaUrl } from '@/lib/api';
import {
  getMusicDiscovery,
  type MusicDiscoveryAlbum,
  type MusicDiscoveryArtist,
  type MusicDiscoveryResponse,
  type MusicDiscoverySong,
} from '@/lib/music/MusicDiscovery';

function formatCount(value: number): string {
  return new Intl.NumberFormat('en', {
    notation: value >= 10000 ? 'compact' : 'standard',
    maximumFractionDigits: 1,
  }).format(value);
}

function getArtistNames(
  artists: MusicDiscoveryArtist[],
): string {
  if (artists.length === 0) {
    return 'Unknown artist';
  }

  return artists.map((artist) => artist.name).join(', ');
}

function SidebarArtwork({
  src,
  alt,
}: {
  src: string | null;
  alt: string;
}) {
  const imageSrc = getMediaUrl(src);

  return (
    <div
      className="
        relative flex h-12 w-12 shrink-0
        items-center justify-center
        overflow-hidden rounded-xl
        bg-light-surface-soft
        text-light-text-muted
        dark:bg-dark-surface-soft
        dark:text-dark-text-muted
      "
    >
      {imageSrc ? (
        <Image
          src={imageSrc}
          alt={alt}
          fill
          sizes="48px"
          className="object-cover"
        />
      ) : (
        <Music2
          className="h-5 w-5"
          aria-hidden="true"
        />
      )}
    </div>
  );
}

function SidebarSection({
  title,
  icon,
  href,
  children,
}: {
  title: string;
  icon: ReactNode;
  href?: string;
  children: ReactNode;
}) {
  return (
    <section
      className="
        min-w-0 rounded-2xl
        bg-light-surface p-4
        transition-colors duration-200
        dark:bg-dark-surface
      "
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2
          className="
            flex min-w-0 items-center gap-2.5
            text-sm font-bold tracking-tight
            text-light-text
            dark:text-dark-text
          "
        >
          <span
            className="
              flex h-9 w-9 shrink-0
              items-center justify-center
              rounded-xl
              bg-brand-teal/10
              text-brand-teal
              dark:bg-brand-teal/15
              dark:text-brand-teal-light
            "
            aria-hidden="true"
          >
            {icon}
          </span>

          <span className="min-w-0 break-words">
            {title}
          </span>
        </h2>

        {href && (
          <Link
            href={href}
            aria-label={`Explore ${title}`}
            className="
              group flex h-9 w-9 shrink-0
              items-center justify-center
              rounded-full
              text-light-text-muted
              transition-colors duration-200
              hover:bg-light-surface-hover
              hover:text-brand-teal
              focus:outline-none
              focus-visible:ring-2
              focus-visible:ring-brand-teal
              dark:text-dark-text-muted
              dark:hover:bg-dark-surface-hover
              dark:hover:text-brand-teal-light
            "
          >
            <ArrowRight
              className="
                h-4 w-4
                transition-transform duration-200
                group-hover:translate-x-0.5
              "
              aria-hidden="true"
            />
          </Link>
        )}
      </div>

      <div className="space-y-1">
        {children}
      </div>
    </section>
  );
}

function SongRow({
  song,
}: {
  song: MusicDiscoverySong;
}) {
  return (
    <Link
      href={`/music/songs/${encodeURIComponent(song.slug)}`}
      className="
        group flex min-w-0 items-center gap-3
        rounded-xl p-2
        transition-colors duration-200
        hover:bg-light-surface-soft
        focus:outline-none
        focus-visible:ring-2
        focus-visible:ring-brand-teal
        dark:hover:bg-dark-surface-soft
      "
    >
      <SidebarArtwork
        src={song.artwork}
        alt={`${song.title} artwork`}
      />

      <span className="min-w-0 flex-1">
        <span
          className="
            block truncate text-sm font-semibold
            text-light-text
            transition-colors duration-200
            group-hover:text-brand-teal
            dark:text-dark-text
            dark:group-hover:text-brand-teal-light
          "
        >
          {song.title}
        </span>

        <span
          className="
            mt-1 block truncate text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {getArtistNames(song.artists)}
        </span>
      </span>

      {song.average_rating !== null && (
        <span
          className="
            flex shrink-0 items-center gap-1
            text-xs font-medium
            text-light-text-muted
            dark:text-dark-text-muted
          "
          title="Average rating"
        >
          <Star
            className="
              h-3.5 w-3.5
              fill-amber-400 text-amber-400
            "
            aria-hidden="true"
          />
          {song.average_rating.toFixed(1)}
        </span>
      )}
    </Link>
  );
}

function AlbumRow({
  album,
}: {
  album: MusicDiscoveryAlbum;
}) {
  return (
    <Link
      href={`/music/albums/${encodeURIComponent(album.slug)}`}
      className="
        group flex min-w-0 items-center gap-3
        rounded-xl p-2
        transition-colors duration-200
        hover:bg-light-surface-soft
        focus:outline-none
        focus-visible:ring-2
        focus-visible:ring-brand-teal
        dark:hover:bg-dark-surface-soft
      "
    >
      <SidebarArtwork
        src={album.artwork}
        alt={`${album.title} artwork`}
      />

      <span className="min-w-0 flex-1">
        <span
          className="
            block truncate text-sm font-semibold
            text-light-text
            transition-colors duration-200
            group-hover:text-brand-teal
            dark:text-dark-text
            dark:group-hover:text-brand-teal-light
          "
        >
          {album.title}
        </span>

        <span
          className="
            mt-1 block truncate text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {getArtistNames(album.artists)}
        </span>
      </span>

      {album.average_rating !== null && (
        <span
          className="
            flex shrink-0 items-center gap-1
            text-xs font-medium
            text-light-text-muted
            dark:text-dark-text-muted
          "
          title="Average rating"
        >
          <Star
            className="
              h-3.5 w-3.5
              fill-amber-400 text-amber-400
            "
            aria-hidden="true"
          />
          {album.average_rating.toFixed(1)}
        </span>
      )}
    </Link>
  );
}

function ArtistRow({
  artist,
}: {
  artist: MusicDiscoveryArtist;
}) {
  const imageSrc = getMediaUrl(artist.profile_image);

  return (
    <div
      className="
        flex min-w-0 items-center gap-3
        rounded-xl p-2
      "
    >
      <div
        className="
          relative flex h-11 w-11 shrink-0
          items-center justify-center
          overflow-hidden rounded-full
          bg-light-surface-soft
          text-light-text-muted
          dark:bg-dark-surface-soft
          dark:text-dark-text-muted
        "
      >
        {imageSrc ? (
          <Image
            src={imageSrc}
            alt={artist.name}
            fill
            sizes="44px"
            className="object-cover"
          />
        ) : (
          <Users
            className="h-5 w-5"
            aria-hidden="true"
          />
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex min-w-0 items-center gap-1.5">
          <span
            className="
              truncate text-sm font-semibold
              text-light-text
              dark:text-dark-text
            "
          >
            {artist.name}
          </span>

          {artist.is_verified && (
            <span
              className="
                inline-flex h-4 w-4 shrink-0
                items-center justify-center
                rounded-full bg-brand-teal
                text-[10px] font-bold text-white
              "
              title="Verified artist"
              aria-label="Verified artist"
            >
              ✓
            </span>
          )}
        </div>

        <p
          className="
            mt-1 text-xs
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {formatCount(artist.followers_count)} followers
        </p>
      </div>
    </div>
  );
}

function SidebarLoading() {
  return (
    <div
      className="space-y-4"
      aria-label="Loading music recommendations"
      role="status"
    >
      <span className="sr-only">
        Loading music recommendations...
      </span>

      {[1, 2, 3].map((section) => (
        <div
          key={section}
          aria-hidden="true"
          className="
            animate-pulse rounded-2xl
            bg-light-surface p-4
            dark:bg-dark-surface
          "
        >
          <div className="mb-4 flex items-center gap-3">
            <div
              className="
                h-9 w-9 rounded-xl
                bg-light-surface-soft
                dark:bg-dark-surface-soft
              "
            />
            <div
              className="
                h-4 w-32 rounded
                bg-light-surface-soft
                dark:bg-dark-surface-soft
              "
            />
          </div>

          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="mb-3 flex items-center gap-3 last:mb-0"
            >
              <div
                className="
                  h-12 w-12 shrink-0 rounded-xl
                  bg-light-surface-soft
                  dark:bg-dark-surface-soft
                "
              />

              <div className="flex-1 space-y-2">
                <div
                  className="
                    h-3 w-3/4 rounded
                    bg-light-surface-soft
                    dark:bg-dark-surface-soft
                  "
                />
                <div
                  className="
                    h-3 w-1/2 rounded
                    bg-light-surface-soft
                    dark:bg-dark-surface-soft
                  "
                />
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function SidebarEmptyState({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <p
      className="
        rounded-xl px-2 py-3 text-sm
        text-light-text-muted
        dark:text-dark-text-muted
      "
    >
      {children}
    </p>
  );
}

function ExploreLink({
  href,
  icon,
  children,
}: {
  href: string;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <Link
      href={href}
      className="
        group flex items-center gap-3
        rounded-xl px-3 py-2.5
        text-sm font-medium
        text-light-text
        transition-colors duration-200
        hover:bg-light-surface-soft
        hover:text-brand-teal
        focus:outline-none
        focus-visible:ring-2
        focus-visible:ring-brand-teal
        dark:text-dark-text
        dark:hover:bg-dark-surface-soft
        dark:hover:text-brand-teal-light
      "
    >
      <span
        className="
          shrink-0 text-light-text-muted
          transition-colors duration-200
          group-hover:text-brand-teal
          dark:text-dark-text-muted
          dark:group-hover:text-brand-teal-light
        "
        aria-hidden="true"
      >
        {icon}
      </span>

      <span>{children}</span>
    </Link>
  );
}

export default function MusicRightSidebar() {
  const [discovery, setDiscovery] =
    useState<MusicDiscoveryResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  const [loadError, setLoadError] =
    useState<string | null>(null);

  const loadDiscovery = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);

    try {
      const response = await getMusicDiscovery();
      setDiscovery(response);
    } catch {
      setLoadError(
        'We couldn’t load music recommendations.',
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDiscovery();
  }, [loadDiscovery]);

  return (
    <aside
      className="
        hidden w-full max-w-[320px]
        shrink-0 self-start lg:block
      "
      aria-label="Music recommendations"
    >
      <div className="space-y-4">
        {isLoading && <SidebarLoading />}

        {!isLoading && loadError && (
          <section
            className="
              rounded-2xl bg-light-surface p-5
              dark:bg-dark-surface
            "
            role="alert"
          >
            <div
              className="
                flex h-10 w-10 items-center justify-center
                rounded-full
                bg-light-surface-soft
                text-light-text-muted
                dark:bg-dark-surface-soft
                dark:text-dark-text-muted
              "
            >
              <AlertCircle
                className="h-5 w-5"
                aria-hidden="true"
              />
            </div>

            <p
              className="
                mt-3 text-sm font-semibold
                text-light-text
                dark:text-dark-text
              "
            >
              Recommendations unavailable
            </p>

            <p
              className="
                mt-1 text-sm leading-6
                text-light-text-muted
                dark:text-dark-text-muted
              "
            >
              {loadError}
            </p>

            <button
              type="button"
              onClick={() => {
                void loadDiscovery();
              }}
              className="
                mt-4 inline-flex items-center gap-2
                rounded-xl bg-brand-teal px-3 py-2
                text-sm font-semibold text-white
                transition-opacity duration-200
                hover:opacity-90
                focus:outline-none
                focus-visible:ring-2
                focus-visible:ring-brand-teal
                focus-visible:ring-offset-2
                focus-visible:ring-offset-light-surface
                dark:focus-visible:ring-offset-dark-surface
              "
            >
              <RefreshCw
                className="h-4 w-4"
                aria-hidden="true"
              />
              Try again
            </button>
          </section>
        )}

        {!isLoading && !loadError && discovery && (
          <>
            <SidebarSection
              title="Trending songs"
              icon={<Flame className="h-4 w-4" />}
              href="/music/discover/trending"
            >
              {discovery.trending_songs
                .slice(0, 4)
                .map((song) => (
                  <SongRow key={song.id} song={song} />
                ))}

              {discovery.trending_songs.length === 0 && (
                <SidebarEmptyState>
                  No trending songs yet.
                </SidebarEmptyState>
              )}
            </SidebarSection>

            <SidebarSection
              title="Featured artists"
              icon={<Sparkles className="h-4 w-4" />}
              href="/music/discover/featured"
            >
              {discovery.featured_artists
                .slice(0, 4)
                .map((artist) => (
                  <ArtistRow
                    key={artist.id}
                    artist={artist}
                  />
                ))}

              {discovery.featured_artists.length === 0 && (
                <SidebarEmptyState>
                  No featured artists yet.
                </SidebarEmptyState>
              )}
            </SidebarSection>

            <SidebarSection
              title="Featured releases"
              icon={<Disc3 className="h-4 w-4" />}
              href="/music/discover/featured"
            >
              {discovery.featured_songs
                .slice(0, 2)
                .map((song) => (
                  <SongRow
                    key={`song-${song.id}`}
                    song={song}
                  />
                ))}

              {discovery.featured_albums
                .slice(0, 2)
                .map((album) => (
                  <AlbumRow
                    key={`album-${album.id}`}
                    album={album}
                  />
                ))}

              {discovery.featured_songs.length === 0 &&
                discovery.featured_albums.length === 0 && (
                  <SidebarEmptyState>
                    No featured releases yet.
                  </SidebarEmptyState>
                )}
            </SidebarSection>

            <SidebarSection
              title="Explore music"
              icon={<Sparkles className="h-4 w-4" />}
              href="/music/discover"
            >
              <ExploreLink
                href="/music/discover/most-discussed"
                icon={<Users className="h-4 w-4" />}
              >
                Most discussed
              </ExploreLink>

              <ExploreLink
                href="/music/discover/most-favorited"
                icon={<Star className="h-4 w-4" />}
              >
                Most favorited
              </ExploreLink>

              <ExploreLink
                href="/music/discover/top-rated"
                icon={<Star className="h-4 w-4" />}
              >
                Top rated
              </ExploreLink>

              <ExploreLink
                href="/music/discover/recently-released"
                icon={<Disc3 className="h-4 w-4" />}
              >
                Recently released
              </ExploreLink>

              <Link
                href="/music/discover"
                className="
                  mt-3 flex w-full items-center
                  justify-center gap-2
                  rounded-xl bg-brand-teal/5
                  px-3 py-3 text-sm font-semibold
                  text-brand-teal
                  transition-colors duration-200
                  hover:bg-brand-teal/10
                  focus:outline-none
                  focus-visible:ring-2
                  focus-visible:ring-brand-teal
                  dark:bg-brand-teal/10
                  dark:text-brand-teal-light
                  dark:hover:bg-brand-teal/15
                "
              >
                Explore all music
                <ArrowRight
                  className="h-4 w-4"
                  aria-hidden="true"
                />
              </Link>
            </SidebarSection>
          </>
        )}
      </div>
    </aside>
  );
}