
import type { Metadata } from 'next';

import Image from 'next/image';
import Link from 'next/link';
import { cookies } from 'next/headers';
import {
  notFound,
  permanentRedirect,
} from 'next/navigation';

import MusicNavigation from '@/components/music/MusicNavigation';
import TargetCommunityPosts from '@/components/music/TargetCommunityPosts';
import ArtistFollowButton from '@/components/music/ArtistFollowButton';
import { getMediaUrl } from '@/lib/api';

type ArtistProfile = {
  id: number;
  name: string;
  slug: string;
  profile_image: string | null;
  country: string | null;
  is_verified: boolean;
  followers_count: number;
  is_following?: boolean;
};

type ArtistSong = {
  id: number;
  title: string;
  slug: string;
  artists: ArtistProfile[];
  featured_artists: ArtistProfile[];
  artwork: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  duration_display: string | null;
  favorites_count: number;
  ratings_count: number;
};

type ArtistAlbum = {
  id: number;
  title: string;
  slug: string;
  artists: ArtistProfile[];
  release_type: string;
  artwork: string | null;
  release_date: string | null;
  favorites_count: number;
  ratings_count: number;
};

type ArtistDetail = ArtistProfile & {
  is_following: boolean;
  songs: ArtistSong[];
  albums: ArtistAlbum[];
  related_posts: unknown[];
};

type ArtistPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000';

function formatCount(value: number): string {
  return new Intl.NumberFormat('en').format(value);
}

function formatReleaseDate(
  releaseDate: string | null,
): string | null {
  if (!releaseDate) return null;

  const date = new Date(releaseDate);

  if (Number.isNaN(date.getTime())) {
    return releaseDate;
  }

  return new Intl.DateTimeFormat('en', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(date);
}

function getArtistTitle(artist: ArtistDetail): string {
  return `${artist.name} | VibeNationHQ`;
}

function getArtistDescription(artist: ArtistDetail): string {
  const details = [
    artist.country ? `Artist from ${artist.country}.` : '',
    `${formatCount(artist.songs.length)} songs`,
    `${formatCount(artist.albums.length)} albums`,
  ].filter(Boolean);

  return `Explore ${artist.name} on VibeNationHQ. ${details.join(' · ')}. Discover music and join the community discussion.`;
}

async function getArtistBySlug(
  slug: string,
): Promise<ArtistDetail> {
  /*
   * Forward the current visitor's cookies to Django so the API
   * can determine whether this visitor follows the artist.
   *
   * This response contains user-specific data, so it must not
   * be cached and shared between different visitors.
   */
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  const response = await fetch(
    `${API_URL}/api/v1/music/artists/${encodeURIComponent(slug)}/`,
    {
      cache: 'no-store',
      headers: cookieHeader
        ? {
            Cookie: cookieHeader,
          }
        : undefined,
    },
  );

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error(
      `Unable to load artist details. The music API returned ${response.status}.`,
    );
  }

  return response.json() as Promise<ArtistDetail>;
}

export async function generateMetadata({
  params,
}: ArtistPageProps): Promise<Metadata> {
  const { slug } = await params;
  const artist = await getArtistBySlug(slug);

  const title = getArtistTitle(artist);
  const description = getArtistDescription(artist);
  const canonicalPath =
    `/music/artists/${encodeURIComponent(artist.slug)}`;
  const imageUrl = getMediaUrl(artist.profile_image);

  return {
    title,
    description,
    alternates: {
      canonical: canonicalPath,
    },
    openGraph: {
      type: 'profile',
      title,
      description,
      url: new URL(canonicalPath, SITE_URL).toString(),
      siteName: 'VibeNationHQ',
      images: imageUrl ? [imageUrl] : [],
    },
    twitter: {
      card: imageUrl ? 'summary_large_image' : 'summary',
      title,
      description,
      images: imageUrl ? [imageUrl] : [],
    },
  };
}

function getSongArtists(song: ArtistSong): ArtistProfile[] {
  const artists = [...song.artists, ...song.featured_artists];

  return artists.filter(
    (artist, index) =>
      artists.findIndex(
        (candidate) => candidate.id === artist.id,
      ) === index,
  );
}

function getReleaseTypeLabel(releaseType: string): string {
  return releaseType.replace(/[_-]+/g, ' ').trim();
}

function ArtistArtwork({
  imageUrl,
  name,
}: {
  imageUrl: string | null;
  name: string;
}) {
  return (
    <div className="relative aspect-square w-full overflow-hidden rounded-3xl bg-light-muted/10 shadow-lg shadow-black/10 ring-1 ring-black/5 dark:bg-dark-muted/10 dark:ring-white/10">
      {imageUrl ? (
        <Image
          src={imageUrl}
          alt={`${name} artist portrait`}
          fill
          priority
          sizes="(max-width: 767px) min(72vw, 320px), 280px"
          className="object-cover"
        />
      ) : (
        <div
          className="flex h-full items-center justify-center bg-gradient-to-br from-brand/20 via-brand/10 to-transparent text-7xl font-bold text-brand"
          role="img"
          aria-label={`Artist image unavailable for ${name}`}
        >
          {name.trim().charAt(0).toUpperCase() || '♪'}
        </div>
      )}
    </div>
  );
}

function VerifiedBadge({
  name,
}: {
  name: string;
}) {
  return (
    <span
      className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand text-xs font-bold text-white"
      role="img"
      aria-label={`${name} is a verified artist`}
      title="Verified artist"
    >
      ✓
    </span>
  );
}

function ArtistHero({
  artist,
  imageUrl,
  createPostUrl,
}: {
  artist: ArtistDetail;
  imageUrl: string | null;
  createPostUrl: string;
}) {
  return (
    <section
      aria-labelledby="artist-title"
      className="overflow-hidden rounded-3xl border border-light-border bg-light-surface dark:border-dark-border dark:bg-dark-surface"
    >
      <div className="grid gap-5 p-4 sm:gap-7 sm:p-6 md:grid-cols-[220px_minmax(0,1fr)] md:items-start lg:grid-cols-[260px_minmax(0,1fr)] lg:gap-8 lg:p-7">
        <div className="mx-auto w-full max-w-[280px] md:max-w-none">
          <ArtistArtwork
            imageUrl={imageUrl}
            name={artist.name}
          />
        </div>

        <div className="min-w-0">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-brand/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-brand">
              Artist
            </span>

            {artist.is_verified && (
              <VerifiedBadge name={artist.name} />
            )}
          </div>

          <h1
            id="artist-title"
            className="break-words text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl"
          >
            {artist.name}
          </h1>

          {artist.country && (
            <p className="mt-2 text-sm text-light-muted dark:text-dark-muted sm:text-base">
              {artist.country}
            </p>
          )}

          <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-3">
            <div>
              <p className="text-xl font-bold tabular-nums">
                {formatCount(artist.songs.length)}
              </p>
              <p className="mt-0.5 text-xs text-light-muted dark:text-dark-muted">
                Songs shown
              </p>
            </div>

            <span
              className="h-9 w-px bg-light-border dark:bg-dark-border"
              aria-hidden="true"
            />

            <div>
              <p className="text-xl font-bold tabular-nums">
                {formatCount(artist.albums.length)}
              </p>
              <p className="mt-0.5 text-xs text-light-muted dark:text-dark-muted">
                Albums shown
              </p>
            </div>
          </div>

          <p className="mt-4 max-w-2xl text-sm leading-6 text-light-muted dark:text-dark-muted">
            Explore {artist.name}&apos;s music, discover albums and
            songs, and join conversations with the VibeNationHQ
            community.
          </p>

          <div className="mt-5">
            <ArtistFollowButton
              artistId={artist.id}
              initialIsFollowing={artist.is_following}
              initialFollowersCount={artist.followers_count}
            />
          </div>

          <div className="mt-5 flex flex-wrap gap-2.5">
            <Link
              href="#artist-songs"
              className="inline-flex min-h-10 items-center justify-center rounded-full bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 dark:focus-visible:ring-offset-dark-surface"
            >
              Explore songs
            </Link>

            <Link
              href={createPostUrl}
              className="inline-flex min-h-10 items-center justify-center rounded-full border border-light-border px-4 py-2 text-sm font-semibold transition hover:border-brand hover:bg-brand/5 hover:text-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand dark:border-dark-border"
            >
              Start a discussion
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function ArtistSectionHeading({
  eyebrow,
  title,
  description,
  count,
}: {
  eyebrow: string;
  title: string;
  description: string;
  count: number;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3 sm:mb-5">
      <div>
        <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.18em] text-brand">
          {eyebrow}
        </p>

        <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">
          {title}
        </h2>

        <p className="mt-1.5 max-w-xl text-sm leading-6 text-light-muted dark:text-dark-muted">
          {description}
        </p>
      </div>

      <span className="shrink-0 rounded-full border border-light-border px-3 py-1.5 text-xs font-medium text-light-muted dark:border-dark-border dark:text-dark-muted">
        {formatCount(count)} {count === 1 ? 'item' : 'items'}
      </span>
    </div>
  );
}

function EmptyCollection({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-light-border bg-light-surface px-5 py-10 text-center dark:border-dark-border dark:bg-dark-surface">
      <div className="text-4xl text-brand" aria-hidden="true">
        ♫
      </div>

      <h3 className="mt-4 font-semibold">{title}</h3>

      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-light-muted dark:text-dark-muted">
        {description}
      </p>
    </div>
  );
}

function AlbumGrid({
  albums,
}: {
  albums: ArtistAlbum[];
}) {
  if (albums.length === 0) {
    return (
      <EmptyCollection
        title="No albums available yet"
        description="Albums associated with this artist will appear here when they are published."
      />
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
      {albums.map((album) => {
        const artworkUrl = getMediaUrl(album.artwork);

        return (
          <article
            key={album.id}
            className="min-w-0 overflow-hidden rounded-2xl border border-light-border bg-light-surface transition duration-200 hover:-translate-y-0.5 hover:border-brand/50 dark:border-dark-border dark:bg-dark-surface"
          >
            <Link
              href={`/music/albums/${encodeURIComponent(album.slug)}`}
              className="group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand"
              aria-label={`View album ${album.title}`}
            >
              <div className="relative aspect-square overflow-hidden bg-light-muted/10 dark:bg-dark-muted/10">
                {artworkUrl ? (
                  <Image
                    src={artworkUrl}
                    alt={`${album.title} album artwork`}
                    fill
                    sizes="(max-width: 639px) 45vw, (max-width: 1023px) 30vw, 220px"
                    className="object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                ) : (
                  <div
                    className="flex h-full items-center justify-center text-4xl text-brand"
                    aria-hidden="true"
                  >
                    ♫
                  </div>
                )}
              </div>

              <div className="p-3 sm:p-4">
                <p className="line-clamp-2 break-words text-sm font-semibold transition-colors group-hover:text-brand sm:text-base">
                  {album.title}
                </p>

                <p className="mt-1 text-xs capitalize text-light-muted dark:text-dark-muted">
                  {getReleaseTypeLabel(album.release_type)}
                </p>

                {album.release_date && (
                  <p className="mt-1 text-xs text-light-muted dark:text-dark-muted">
                    {formatReleaseDate(album.release_date)}
                  </p>
                )}
              </div>
            </Link>
          </article>
        );
      })}
    </div>
  );
}

function SongList({
  songs,
}: {
  songs: ArtistSong[];
}) {
  if (songs.length === 0) {
    return (
      <EmptyCollection
        title="No songs available yet"
        description="Published songs associated with this artist will appear here when available."
      />
    );
  }

  return (
    <ol className="overflow-hidden rounded-2xl border border-light-border bg-light-surface dark:border-dark-border dark:bg-dark-surface">
      {songs.map((song, index) => {
        const artworkUrl = getMediaUrl(song.artwork);
        const songArtists = getSongArtists(song);

        return (
          <li
            key={song.id}
            className="border-b border-light-border last:border-b-0 dark:border-dark-border"
          >
            <Link
              href={`/music/songs/${encodeURIComponent(song.slug)}`}
              aria-label={`View ${song.title} song details`}
              className="
                group relative flex min-w-0 items-center gap-3
                px-3 py-3 transition-colors duration-200
                hover:bg-[#008080]/[0.10]
                focus-visible:z-10 focus-visible:outline-none
                focus-visible:ring-2 focus-visible:ring-inset
                focus-visible:ring-[#008080]
                dark:hover:bg-[#008080]/[0.20]
                sm:gap-4 sm:px-4 sm:py-3.5
              "
            >
              <span className="hidden w-7 shrink-0 text-center text-sm tabular-nums text-light-muted dark:text-dark-muted sm:block">
                {index + 1}
              </span>

              <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-light-muted/10 ring-1 ring-black/5 dark:bg-dark-muted/10 dark:ring-white/10 sm:h-14 sm:w-14">
                {artworkUrl ? (
                  <Image
                    src={artworkUrl}
                    alt=""
                    fill
                    sizes="56px"
                    className="object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                ) : (
                  <div
                    className="flex h-full items-center justify-center text-xl text-brand"
                    aria-hidden="true"
                  >
                    ♫
                  </div>
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p className="flex items-start gap-1.5">
                  <span className="text-xs tabular-nums text-light-muted dark:text-dark-muted sm:hidden">
                    {index + 1}.
                  </span>

                  <span className="min-w-0 break-words text-sm font-semibold text-light-text transition-colors group-hover:text-brand dark:text-dark-text sm:text-base">
                    {song.title}
                  </span>
                </p>

                <p className="mt-1 break-words text-xs text-light-muted dark:text-dark-muted sm:text-sm">
                  {songArtists.map((artist) => artist.name).join(', ') ||
                    'Unknown artist'}
                </p>

                {song.duration_display && (
                  <p className="mt-1 text-[11px] text-light-muted dark:text-dark-muted sm:text-xs">
                    {song.duration_display}
                  </p>
                )}
              </div>

              <span
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-light-muted transition-all duration-200 group-hover:translate-x-0.5 group-hover:bg-[#008080]/10 group-hover:text-[#008080] dark:text-dark-muted dark:group-hover:bg-[#008080]/20 dark:group-hover:text-[#20B2AA]"
                aria-hidden="true"
              >
                <svg
                  viewBox="0 0 24 24"
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M7 17 17 7" />
                  <path d="M7 7h10v10" />
                </svg>
              </span>
            </Link>
          </li>
        );
      })}
    </ol>
  );
}

export default async function ArtistDetailPage({
  params,
}: ArtistPageProps) {
  const { slug } = await params;

  if (!slug.trim()) {
    notFound();
  }

  const artist = await getArtistBySlug(slug);

  const canonicalPath =
    `/music/artists/${encodeURIComponent(artist.slug)}`;

  if (slug !== artist.slug) {
    permanentRedirect(canonicalPath);
  }

  const imageUrl = getMediaUrl(artist.profile_image);

  const createPostParams = new URLSearchParams({
    target_type: 'artist',
    target_id: String(artist.id),
    target_title: artist.name,
    target_slug: artist.slug,
    target_artwork: artist.profile_image ?? '',
  });

  const createArtistPostUrl =
    `/music/create?${createPostParams.toString()}`;

  const canonicalUrl = new URL(canonicalPath, SITE_URL).toString();

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'MusicGroup',
    '@id': `${canonicalUrl}#artist`,
    url: canonicalUrl,
    name: artist.name,
    image: imageUrl ?? undefined,
    ...(artist.country ? { areaServed: artist.country } : {}),
    album: artist.albums.map((album) => ({
      '@type': 'MusicAlbum',
      name: album.title,
      url: new URL(
        `/music/albums/${encodeURIComponent(album.slug)}`,
        SITE_URL,
      ).toString(),
    })),
    track: artist.songs.map((song) => ({
      '@type': 'MusicRecording',
      name: song.title,
      url: new URL(
        `/music/songs/${encodeURIComponent(song.slug)}`,
        SITE_URL,
      ).toString(),
    })),
  };

  return (
    <div className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <MusicNavigation />

      <main className="mx-auto w-full max-w-6xl px-4 py-5 sm:px-6 sm:py-8 lg:px-8">
        <nav
          aria-label="Breadcrumb"
          className="mb-5 flex flex-wrap items-center gap-2 text-xs text-light-muted dark:text-dark-muted sm:mb-6 sm:text-sm"
        >
          <Link
            href="/music/discover"
            className="transition hover:text-brand"
          >
            Music discovery
          </Link>

          <span aria-hidden="true">/</span>

          <Link
            href="/music/artists"
            className="transition hover:text-brand"
          >
            Artists
          </Link>

          <span aria-hidden="true">/</span>

          <span
            aria-current="page"
            className="max-w-full truncate font-medium text-light-text dark:text-dark-text"
          >
            {artist.name}
          </span>
        </nav>

        <ArtistHero
          artist={artist}
          imageUrl={imageUrl}
          createPostUrl={createArtistPostUrl}
        />

        <section
          id="artist-albums"
          aria-labelledby="artist-albums-title"
          className="mt-9 scroll-mt-6 sm:mt-11"
        >
          <ArtistSectionHeading
            eyebrow="Discography"
            title="Albums"
            description={`Explore albums associated with ${artist.name}.`}
            count={artist.albums.length}
          />

          <AlbumGrid albums={artist.albums} />
        </section>

        <section
          id="artist-songs"
          aria-labelledby="artist-songs-title"
          className="mt-9 scroll-mt-6 sm:mt-11"
        >
          <ArtistSectionHeading
            eyebrow="Music catalogue"
            title="Songs"
            description={`Discover songs performed by ${artist.name}, including featured appearances.`}
            count={artist.songs.length}
          />

          <SongList songs={artist.songs} />
        </section>

        <section
          aria-labelledby="artist-discussion-title"
          className="mt-9 sm:mt-11"
        >
          <div className="mb-4">
            <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.18em] text-brand">
              Community
            </p>

            <h2
              id="artist-discussion-title"
              className="text-2xl font-bold tracking-tight sm:text-3xl"
            >
              Discussions about {artist.name}
            </h2>

            <p className="mt-1.5 text-sm leading-6 text-light-muted dark:text-dark-muted">
              Share your thoughts and join conversations about this artist.
            </p>
          </div>

          <TargetCommunityPosts
            targetType="artist"
            targetId={artist.id}
            createPostUrl={createArtistPostUrl}
          />
        </section>
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData).replace(
            /</g,
            '\\u003c',
          ),
        }}
      />
    </div>
  );
}
