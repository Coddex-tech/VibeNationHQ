import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  ArrowRight,
  MessageCircle,
  Music2,
} from 'lucide-react';

import MusicNavigation from '@/components/music/MusicNavigation';
import DiscoveryPageHeader from '@/components/music/discovery/DiscoveryPageHeader';
import DiscoverySection from '@/components/music/discovery/DiscoverySection';
import DiscoverySongCard from '@/components/music/discovery/DiscoverySongCard';
import DiscoveryAlbumCard from '@/components/music/discovery/DiscoveryAlbumCard';
import { getMusicDiscovery } from '@/lib/music/MusicDiscovery';

export const metadata: Metadata = {
  title: 'Most Discussed Music | VibeNationHQ',
  description:
    'Explore the songs and albums generating the most conversations on VibeNationHQ.',
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
        <MessageCircle size={26} />
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

export default async function MostDiscussedPage() {
  let discovery;

  try {
    discovery = await getMusicDiscovery();
  } catch {
    discovery = null;
  }

  const songs = discovery?.most_discussed_songs ?? [];
  const albums = discovery?.most_discussed_albums ?? [];

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
          eyebrow="Community activity"
          title="Most Discussed"
          description="Discover the songs and albums getting people talking. Explore the music inspiring conversations across VibeNationHQ."
          icon="message"
        />

        <nav
          aria-label="Explore other music collections"
          className="mt-6 flex flex-wrap gap-2.5"
        >
          <CategoryLink href="/music/discover/trending">
            <ArrowRight size={15} />
            Trending
          </CategoryLink>

          <CategoryLink href="/music/discover/most-favorited">
            <Music2 size={15} />
            Most Favorited
          </CategoryLink>

          <CategoryLink href="/music/discover/top-rated">
            <ArrowRight size={15} />
            Top Rated
          </CategoryLink>
        </nav>

        <div className="mt-10 space-y-12 sm:mt-12 sm:space-y-14">
          <DiscoverySection
            title="Most Discussed Songs"
            description="Songs attracting the most community conversation."
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
                title="No discussed songs yet"
                description="When songs start attracting community conversations, you'll find them here."
              />
            )}
          </DiscoverySection>

          <DiscoverySection
            title="Most Discussed Albums"
            description="Albums inspiring listeners to share their thoughts."
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
                title="No discussed albums yet"
                description="Albums will appear here as listeners join the conversation."
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
                <Music2 size={23} />
              </div>

              <div>
                <h2 className="font-semibold text-light-text dark:text-dark-text">
                  Keep exploring
                </h2>

                <p className="mt-1 max-w-lg text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                  Find more music through favorites, ratings, and new releases.
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