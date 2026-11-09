import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  ArrowRight,
  Clock3,
} from 'lucide-react';

import MusicNavigation from '@/components/music/MusicNavigation';
import { getMusicDiscovery } from '@/lib/music/MusicDiscovery';
import DiscoveryPageHeader from '@/components/music/discovery/DiscoveryPageHeader';
import DiscoverySection from '@/components/music/discovery/DiscoverySection';
import DiscoverySongCard from '@/components/music/discovery/DiscoverySongCard';
import DiscoveryAlbumCard from '@/components/music/discovery/DiscoveryAlbumCard';

export const metadata: Metadata = {
  title: 'Recently Released Music | VibeNationHQ',
  description:
    'Discover recently released songs and albums on VibeNationHQ.',
};

function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl bg-light-surface px-5 py-10 text-center dark:bg-dark-surface">
      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light">
        <Clock3 size={26} aria-hidden="true" />
      </div>

      <h3 className="font-semibold text-light-text dark:text-dark-text">
        {title}
      </h3>

      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
        {description}
      </p>
    </div>
  );
}

function CategoryLink({
  href,
  children,
}: {
  href: string;
  children: ReactNode;
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-2 rounded-full bg-light-surface px-4 py-2.5 text-sm font-medium text-light-text-muted transition-colors hover:bg-brand-teal/10 hover:text-brand-teal focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:bg-dark-surface dark:text-dark-text-muted dark:hover:text-brand-teal-light"
    >
      {children}
    </Link>
  );
}

export default async function RecentlyReleasedPage() {
  let discovery;

  try {
    discovery = await getMusicDiscovery();
  } catch {
    discovery = null;
  }

  const songs = discovery?.recently_released_songs ?? [];
  const albums = discovery?.recently_released_albums ?? [];

  return (
    <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <MusicNavigation />

      <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <div className="mb-7">
          <Link
            href="/music/discover"
            className="group inline-flex items-center gap-2 rounded-full py-1 text-sm font-medium text-light-text-muted transition-colors hover:text-brand-teal focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:text-dark-text-muted dark:hover:text-brand-teal-light"
          >
            <ArrowLeft
              size={16}
              className="transition-transform group-hover:-translate-x-0.5"
            />
            Back to Discover
          </Link>
        </div>

        <DiscoveryPageHeader
          eyebrow="Fresh releases"
          title="Recently Released"
          description="Catch up on newly released songs and albums from artists on VibeNationHQ."
          icon="music"
        />

        <nav
          aria-label="Explore other music collections"
          className="mt-6 flex flex-wrap gap-2.5"
        >
          <CategoryLink href="/music/discover/trending">
            Trending
            <ArrowRight size={15} />
          </CategoryLink>

          <CategoryLink href="/music/discover/most-favorited">
            Most Favorited
            <ArrowRight size={15} />
          </CategoryLink>

          <CategoryLink href="/music/discover/top-rated">
            Top Rated
            <ArrowRight size={15} />
          </CategoryLink>
        </nav>

        <div className="mt-10 space-y-12 sm:mt-12 sm:space-y-14">
          <DiscoverySection
            title="Recently Released Songs"
            description="Fresh tracks to discover and add to your favorites."
            icon="music"
          >
            {songs.length > 0 ? (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5">
                {songs.map((song, index) => (
                  <DiscoverySongCard
                    key={song.id}
                    song={song}
                    rank={index + 1}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                title="No recent song releases yet"
                description="Newly released songs will appear here when available."
              />
            )}
          </DiscoverySection>

          <DiscoverySection
            title="Recently Released Albums"
            description="Explore the latest albums and other releases."
            icon="disc"
          >
            {albums.length > 0 ? (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5">
                {albums.map((album, index) => (
                  <DiscoveryAlbumCard
                    key={album.id}
                    album={album}
                    rank={index + 1}
                  />
                ))}
              </div>
            ) : (
              <EmptyState
                title="No recent album releases yet"
                description="Newly released albums will appear here when available."
              />
            )}
          </DiscoverySection>
        </div>

        <section className="relative mt-12 overflow-hidden rounded-2xl bg-light-surface p-5 sm:p-7 dark:bg-dark-surface">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-12 -top-16 h-40 w-40 rounded-full bg-brand-teal/10 blur-3xl"
          />

          <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light">
                <Clock3 size={23} aria-hidden="true" />
              </div>

              <div>
                <h2 className="font-semibold text-light-text dark:text-dark-text">
                  Stay up to date
                </h2>

                <p className="mt-1 max-w-lg text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                  Explore fresh releases alongside trending tracks,
                  community favorites, and top-rated music.
                </p>
              </div>
            </div>

            <Link
              href="/music/discover"
              className="inline-flex shrink-0 items-center justify-center gap-2 self-start rounded-xl bg-brand-teal px-4 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 sm:self-center"
            >
              Explore Discover
              <ArrowRight size={16} />
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}