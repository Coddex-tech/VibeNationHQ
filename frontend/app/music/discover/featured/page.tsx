
import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  ArrowRight,
  Disc3,
  Music2,
  Users,
} from 'lucide-react';

import { getMusicDiscovery } from '@/lib/music/MusicDiscovery';
import DiscoveryPageHeader from '@/components/music/discovery/DiscoveryPageHeader';
import DiscoverySection from '@/components/music/discovery/DiscoverySection';
import DiscoverySongCard from '@/components/music/discovery/DiscoverySongCard';
import DiscoveryAlbumCard from '@/components/music/discovery/DiscoveryAlbumCard';
import DiscoveryArtistCard from '@/components/music/discovery/DiscoveryArtistCard';

export const metadata: Metadata = {
  title: 'Featured Music | VibeNationHQ',
  description:
    'Explore featured songs, albums, and artists selected for discovery on VibeNationHQ.',
};

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
      className="
        inline-flex items-center gap-2
        rounded-full px-4 py-2
        text-sm font-medium
        text-light-text-muted
        transition-colors duration-200
        hover:bg-light-surface-hover
        hover:text-light-text
        dark:text-dark-text-muted
        dark:hover:bg-dark-surface-hover
        dark:hover:text-dark-text
      "
    >
      {children}
    </Link>
  );
}

export default async function FeaturedMusicPage() {
  let discovery = null;

  try {
    discovery = await getMusicDiscovery();
  } catch {
    discovery = null;
  }

  const songs = discovery?.featured_songs ?? [];
  const albums = discovery?.featured_albums ?? [];
  const artists = discovery?.featured_artists ?? [];

  return (
    <main className="mx-auto w-full min-w-0 max-w-7xl space-y-6 px-4 py-6 sm:px-6 lg:px-8">
      <Link
        href="/music/discover"
        className="
          inline-flex items-center gap-2
          text-sm font-medium
          text-light-text-muted
          transition-colors
          hover:text-light-text
          dark:text-dark-text-muted
          dark:hover:text-dark-text
        "
      >
        <ArrowLeft size={16} />
        Back to Discover
      </Link>

      <DiscoveryPageHeader
        eyebrow="Handpicked for You"
        title="Featured Music"
        description="Discover songs, albums, and artists we're putting in the spotlight."
        icon="star"
      />

      <div className="flex flex-wrap gap-1">
        <CategoryLink href="/music/discover/trending">
          Trending
          <ArrowRight size={14} />
        </CategoryLink>

        <CategoryLink href="/music/discover/most-discussed">
          Most Discussed
          <ArrowRight size={14} />
        </CategoryLink>

        <CategoryLink href="/music/discover/recent">
          Recently Released
          <ArrowRight size={14} />
        </CategoryLink>
      </div>

      <DiscoverySection
        title="Featured Songs"
        description="Tracks in the spotlight right now."
        icon="music"
      >
        {songs.length > 0 ? (
          <div className="grid min-w-0 grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5">
            {songs.map((song, index) => (
              <DiscoverySongCard
                key={song.id}
                song={song}
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl bg-light-bg px-5 py-10 text-center dark:bg-dark-bg">
            <Music2
              size={30}
              className="mx-auto mb-3 text-light-text-muted dark:text-dark-text-muted"
            />
            <p className="font-semibold text-light-text dark:text-dark-text">
              No featured songs yet
            </p>
            <p className="mt-1 text-sm text-light-text-muted dark:text-dark-text-muted">
              Featured tracks will appear here when available.
            </p>
          </div>
        )}
      </DiscoverySection>

      <DiscoverySection
        title="Featured Albums"
        description="Albums worth adding to your discovery list."
        icon="disc"
      >
        {albums.length > 0 ? (
          <div className="grid min-w-0 grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5">
            {albums.map((album, index) => (
              <DiscoveryAlbumCard
                key={album.id}
                album={album}
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl bg-light-bg px-5 py-10 text-center dark:bg-dark-bg">
            <Disc3
              size={30}
              className="mx-auto mb-3 text-light-text-muted dark:text-dark-text-muted"
            />
            <p className="font-semibold text-light-text dark:text-dark-text">
              No featured albums yet
            </p>
            <p className="mt-1 text-sm text-light-text-muted dark:text-dark-text-muted">
              Featured albums will appear here when available.
            </p>
          </div>
        )}
      </DiscoverySection>

      <DiscoverySection
        title="Featured Artists"
        description="Meet the artists currently in the spotlight."
        icon="users"
      >
        {artists.length > 0 ? (
          <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {artists.map((artist, index) => (
              <DiscoveryArtistCard
                key={artist.id}
                artist={artist}
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl bg-light-bg px-5 py-10 text-center dark:bg-dark-bg">
            <Users
              size={30}
              className="mx-auto mb-3 text-light-text-muted dark:text-dark-text-muted"
            />
            <p className="font-semibold text-light-text dark:text-dark-text">
              No featured artists yet
            </p>
            <p className="mt-1 text-sm text-light-text-muted dark:text-dark-text-muted">
              Featured artists will appear here when available.
            </p>
          </div>
        )}
      </DiscoverySection>

      <div className="flex justify-center pt-2">
        <Link
          href="/music/discover"
          className="
            inline-flex items-center gap-2
            rounded-full px-5 py-3
            text-sm font-semibold
            text-light-text
            transition-colors
            hover:bg-light-surface-hover
            dark:text-dark-text
            dark:hover:bg-dark-surface-hover
          "
        >
          <ArrowLeft size={16} />
          Explore All Discoveries
        </Link>
      </div>
    </main>
  );
}
