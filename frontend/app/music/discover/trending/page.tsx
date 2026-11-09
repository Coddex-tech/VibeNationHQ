
import type { Metadata } from 'next';
import Link from 'next/link';
import {
  ArrowLeft,
  ArrowRight,
  Flame,
  Music2,
  TrendingUp,
  Users,
} from 'lucide-react';

import MusicNavigation from '@/components/music/MusicNavigation';
import DiscoveryAlbumCard from '@/components/music/discovery/DiscoveryAlbumCard';
import DiscoveryArtistCard from '@/components/music/discovery/DiscoveryArtistCard';
import DiscoveryPageHeader from '@/components/music/discovery/DiscoveryPageHeader';
import DiscoverySection from '@/components/music/discovery/DiscoverySection';
import DiscoverySongCard from '@/components/music/discovery/DiscoverySongCard';

import {
  getMusicDiscovery,
  type MusicDiscoveryAlbum,
  type MusicDiscoveryArtist,
  type MusicDiscoverySong,
} from '@/lib/music/MusicDiscovery';

export const metadata: Metadata = {
  title: 'Trending Music | VibeNationHQ',
  description:
    'Explore trending songs, albums, and artists on VibeNationHQ.',
};

const otherDiscoveryCategories = [
  {
    label: 'Most discussed',
    href: '/music/discover/most-discussed',
  },
  {
    label: 'Most favorited',
    href: '/music/discover/most-favorited',
  },
  {
    label: 'Top rated',
    href: '/music/discover/top-rated',
  },
  {
    label: 'Featured',
    href: '/music/discover/featured',
  },
  {
    label: 'Recent',
    href: '/music/discover/recent',
  },
];

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex min-h-32 flex-col items-center justify-center rounded-2xl bg-light-surface px-5 py-8 text-center dark:bg-dark-surface">
      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light">
        <Music2 className="h-5 w-5" aria-hidden="true" />
      </div>

      <p className="max-w-md text-sm leading-relaxed text-light-text-muted dark:text-dark-text-muted">
        {message}
      </p>
    </div>
  );
}

function SongGrid({ songs }: { songs: MusicDiscoverySong[] }) {
  if (songs.length === 0) {
    return (
      <EmptyState message="There are no trending songs to display right now. Check back as more music gains attention." />
    );
  }

  return (
    <div className="grid grid-cols-2 gap-x-3 gap-y-5 sm:grid-cols-3 sm:gap-x-4 sm:gap-y-6 lg:grid-cols-4 xl:grid-cols-5">
      {songs.map((song, index) => (
        <DiscoverySongCard
          key={song.id}
          song={song}
          rank={index + 1}
        />
      ))}
    </div>
  );
}

function AlbumGrid({ albums }: { albums: MusicDiscoveryAlbum[] }) {
  if (albums.length === 0) {
    return (
      <EmptyState message="There are no trending albums to display right now." />
    );
  }

  return (
    <div className="grid grid-cols-2 gap-x-3 gap-y-5 sm:grid-cols-3 sm:gap-x-4 sm:gap-y-6 lg:grid-cols-4 xl:grid-cols-5">
      {albums.map((album, index) => (
        <DiscoveryAlbumCard
          key={album.id}
          album={album}
          rank={index + 1}
        />
      ))}
    </div>
  );
}

function ArtistGrid({ artists }: { artists: MusicDiscoveryArtist[] }) {
  if (artists.length === 0) {
    return (
      <EmptyState message="There are no trending artists to display right now." />
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
      {artists.map((artist, index) => (
        <DiscoveryArtistCard
          key={artist.id}
          artist={artist}
          rank={index + 1}
        />
      ))}
    </div>
  );
}

function TrendingErrorState() {
  return (
    <div className="mx-auto flex min-h-[50vh] w-full max-w-xl items-center justify-center">
      <div className="w-full rounded-3xl bg-light-surface px-6 py-10 text-center dark:bg-dark-surface sm:px-10">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light">
          <Music2 className="h-8 w-8" aria-hidden="true" />
        </div>

        <h1 className="mt-5 text-xl font-extrabold tracking-tight sm:text-2xl">
          Trending music is temporarily unavailable
        </h1>

        <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-light-text-muted dark:text-dark-text-muted">
          We couldn&apos;t retrieve trending music right now. Please try again
          in a moment.
        </p>

        <Link
          href="/music/discover/trending"
          className="mt-6 inline-flex items-center justify-center gap-2 rounded-full bg-brand-teal px-5 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 focus-visible:ring-offset-light-bg dark:focus-visible:ring-offset-dark-bg"
        >
          Reload page
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>

        <div>
          <Link
            href="/music/discover"
            className="mt-5 inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-light-text-muted transition-colors hover:bg-black/5 hover:text-brand-teal focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:text-dark-text-muted dark:hover:bg-white/5 dark:hover:text-brand-teal-light"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Back to Music Discovery
          </Link>
        </div>
      </div>
    </div>
  );
}

export default async function TrendingMusicPage() {
  let discovery;

  try {
    discovery = await getMusicDiscovery();
  } catch {
    return (
      <div className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
        <MusicNavigation />

        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
          <TrendingErrorState />
        </main>
      </div>
    );
  }

  const hasTrendingContent =
    discovery.trending_songs.length > 0 ||
    discovery.trending_albums.length > 0 ||
    discovery.trending_artists.length > 0;

  return (
    <div className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <MusicNavigation />

      <main className="mx-auto w-full max-w-7xl space-y-8 px-4 py-6 sm:space-y-10 sm:px-6 sm:py-8 lg:px-8">
        {/* Back navigation */}
        <Link
          href="/music/discover"
          className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-light-text-muted transition-colors hover:bg-black/5 hover:text-brand-teal focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:text-dark-text-muted dark:hover:bg-white/5 dark:hover:text-brand-teal-light"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to Music Discovery
        </Link>

        {/* Page introduction */}
        <DiscoveryPageHeader
          eyebrow="WHAT'S GETTING ATTENTION"
          title="Trending Music"
          description="See which songs, albums, and artists are attracting attention across VibeNationHQ."
          icon="flame"
        />

        {/* Other discovery categories */}
        <nav
          aria-label="Other music discovery categories"
          className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-2 sm:mx-0 sm:flex-wrap sm:px-0"
        >
          {otherDiscoveryCategories.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="inline-flex shrink-0 items-center rounded-full bg-light-surface px-4 py-2.5 text-sm font-medium text-light-text-muted transition-colors hover:bg-brand-teal/10 hover:text-brand-teal focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:bg-dark-surface dark:text-dark-text-muted dark:hover:bg-brand-teal/10 dark:hover:text-brand-teal-light"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Trending content */}
        {!hasTrendingContent ? (
          <EmptyState message="Trending content will appear here as music starts gaining attention. Explore the other discovery categories in the meantime." />
        ) : (
          <div className="space-y-8 sm:space-y-10">
            <DiscoverySection
              title="Trending Songs"
              description="Tracks currently catching listeners' attention."
              icon="flame"
              href="/music/discover/trending"
            >
              <SongGrid songs={discovery.trending_songs} />
            </DiscoverySection>

            <DiscoverySection
              title="Trending Albums"
              description="Albums that music fans are checking out."
              icon="trending"
              href="/music/discover/trending"
            >
              <AlbumGrid albums={discovery.trending_albums} />
            </DiscoverySection>

            <DiscoverySection
              title="Trending Artists"
              description="Artists currently drawing attention from listeners."
              icon="users"
              href="/music/discover/trending"
            >
              <ArtistGrid artists={discovery.trending_artists} />
            </DiscoverySection>
          </div>
        )}

        {/* Explore more */}
        <section className="rounded-3xl bg-light-surface p-5 dark:bg-dark-surface sm:p-7">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light">
                  <Music2 className="h-4 w-4" aria-hidden="true" />
                </div>

                <h2 className="text-lg font-extrabold tracking-tight">
                  Want to explore more?
                </h2>
              </div>

              <p className="mt-2 text-sm leading-relaxed text-light-text-muted dark:text-dark-text-muted">
                Discover community favorites, highly rated releases, and new
                music.
              </p>
            </div>

            <Link
              href="/music/discover"
              className="inline-flex w-fit shrink-0 items-center gap-2 rounded-full bg-brand-teal px-5 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 focus-visible:ring-offset-light-surface dark:focus-visible:ring-offset-dark-surface"
            >
              Explore all music
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
