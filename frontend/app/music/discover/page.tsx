
import type { Metadata } from 'next';
import Link from 'next/link';
import {
  ArrowRight,
  Clock3,
  Flame,
  Heart,
  MessageCircle,
  Music2,
  Sparkles,
  Star,
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
  title: 'Discover Music | VibeNationHQ',
  description:
    'Discover trending songs, popular albums, featured artists, top-rated music, and the latest releases on VibeNationHQ.',
};

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

function SongGrid({
  songs,
  emptyMessage,
  limit,
}: {
  songs: MusicDiscoverySong[];
  emptyMessage: string;
  limit?: number;
}) {
  const items = typeof limit === 'number' ? songs.slice(0, limit) : songs;

  if (items.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <div className="grid grid-cols-2 gap-x-3 gap-y-5 sm:grid-cols-3 sm:gap-x-4 sm:gap-y-6 lg:grid-cols-4 xl:grid-cols-5">
      {items.map((song, index) => (
        <DiscoverySongCard
          key={song.id}
          song={song}
          rank={index + 1}
        />
      ))}
    </div>
  );
}

function AlbumGrid({
  albums,
  emptyMessage,
  limit,
}: {
  albums: MusicDiscoveryAlbum[];
  emptyMessage: string;
  limit?: number;
}) {
  const items = typeof limit === 'number' ? albums.slice(0, limit) : albums;

  if (items.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <div className="grid grid-cols-2 gap-x-3 gap-y-5 sm:grid-cols-3 sm:gap-x-4 sm:gap-y-6 lg:grid-cols-4 xl:grid-cols-5">
      {items.map((album, index) => (
        <DiscoveryAlbumCard
          key={album.id}
          album={album}
          rank={index + 1}
        />
      ))}
    </div>
  );
}

function ArtistGrid({
  artists,
  emptyMessage,
  limit,
}: {
  artists: MusicDiscoveryArtist[];
  emptyMessage: string;
  limit?: number;
}) {
  const items = typeof limit === 'number' ? artists.slice(0, limit) : artists;

  if (items.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
      {items.map((artist, index) => (
        <DiscoveryArtistCard
          key={artist.id}
          artist={artist}
          rank={index + 1}
        />
      ))}
    </div>
  );
}

function SectionHeading({
  id,
  eyebrow,
  title,
  description,
  href,
}: {
  id?: string;
  eyebrow: string;
  title: string;
  description: string;
  href: string;
}) {
  return (
    <div className="mb-5 flex items-end justify-between gap-3 sm:gap-4">
      <div className="min-w-0">
        <p className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.18em] text-brand-teal dark:text-brand-teal-light">
          {eyebrow}
        </p>

        <h2
          id={id}
          className="text-xl font-extrabold tracking-tight text-light-text sm:text-2xl dark:text-dark-text"
        >
          {title}
        </h2>

        <p className="mt-1.5 max-w-xl text-sm leading-relaxed text-light-text-muted dark:text-dark-text-muted">
          {description}
        </p>
      </div>

      <Link
        href={href}
        className="inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-2 text-xs font-semibold text-brand-teal transition-colors hover:bg-black/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal sm:gap-1.5 sm:text-sm dark:text-brand-teal-light dark:hover:bg-white/5"
      >
        Explore
        <ArrowRight className="h-4 w-4" aria-hidden="true" />
      </Link>
    </div>
  );
}

const discoveryCategories = [
  {
    label: 'Trending',
    href: '/music/discover/trending',
    icon: Flame,
  },
  {
    label: 'Most discussed',
    href: '/music/discover/most-discussed',
    icon: MessageCircle,
  },
  {
    label: 'Most favorited',
    href: '/music/discover/most-favorited',
    icon: Heart,
  },
  {
    label: 'Top rated',
    href: '/music/discover/top-rated',
    icon: Star,
  },
  {
    label: 'Featured',
    href: '/music/discover/featured',
    icon: Sparkles,
  },
  {
    label: 'Recent',
    href: '/music/discover/recent',
    icon: Clock3,
  },
];

export default async function MusicDiscoveryPage() {
  let discovery;

  try {
    discovery = await getMusicDiscovery();
  } catch {
    return (
      <div className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
        <MusicNavigation />

        <main className="mx-auto flex w-full max-w-7xl justify-center px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
          <div className="w-full max-w-xl rounded-3xl bg-light-surface px-6 py-10 text-center dark:bg-dark-surface sm:px-10">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light">
              <Music2 className="h-8 w-8" aria-hidden="true" />
            </div>

            <h1 className="mt-5 text-xl font-extrabold tracking-tight sm:text-2xl">
              Music discovery is temporarily unavailable
            </h1>

            <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-light-text-muted dark:text-dark-text-muted">
              We couldn&apos;t retrieve the latest music right now. Please try
              loading the page again in a moment.
            </p>

            <Link
              href="/music/discover"
              className="mt-6 inline-flex items-center justify-center gap-2 rounded-full bg-brand-teal px-5 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal focus-visible:ring-offset-2 focus-visible:ring-offset-light-bg dark:focus-visible:ring-offset-dark-bg"
            >
              Reload discovery
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const hasTrending =
    discovery.trending_songs.length > 0 ||
    discovery.trending_albums.length > 0 ||
    discovery.trending_artists.length > 0;

  return (
    <div className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <MusicNavigation />

      <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <div className="space-y-10 sm:space-y-12">
          {/* Discovery introduction */}
          <DiscoveryPageHeader
            eyebrow="YOUR SOUND STARTS HERE"
            title="Discover Music"
            description="Find your next favorite song, explore standout albums, meet new artists, and see what the VibeNationHQ community is listening to."
            icon="music"
          />

          {/* Main discovery navigation */}
          <nav
            aria-label="Music discovery categories"
            className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-2 sm:mx-0 sm:flex-wrap sm:px-0"
          >
            {discoveryCategories.map(({ label, href, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="inline-flex shrink-0 items-center gap-2 rounded-full bg-light-surface px-4 py-2.5 text-sm font-medium text-light-text-muted transition-colors hover:bg-brand-teal/10 hover:text-brand-teal focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal dark:bg-dark-surface dark:text-dark-text-muted dark:hover:bg-brand-teal/10 dark:hover:text-brand-teal-light"
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {label}
              </Link>
            ))}
          </nav>

          {/* Trending feature area */}
          <section
            aria-labelledby="trending-heading"
            className="overflow-hidden rounded-3xl bg-light-surface dark:bg-dark-surface"
          >
            <div className="relative isolate overflow-hidden rounded-3xl bg-gradient-to-br from-teal-950 via-teal-900 to-slate-950 px-5 py-7 text-white sm:px-8 sm:py-10 lg:px-10 lg:py-12">
              <div
                className="pointer-events-none absolute -right-16 -top-24 -z-10 h-72 w-72 rounded-full bg-teal-400/15 blur-3xl"
                aria-hidden="true"
              />

              <div
                className="pointer-events-none absolute -bottom-32 left-1/3 -z-10 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl"
                aria-hidden="true"
              />

              <div className="relative flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
                <div className="max-w-2xl">
                  <span className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-teal-100 ring-1 ring-inset ring-white/10">
                    <Flame className="h-3.5 w-3.5" aria-hidden="true" />
                    WHAT&apos;S GETTING ATTENTION
                  </span>

                  <h2
                    id="trending-heading"
                    className="mt-4 text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl"
                  >
                    Catch the vibe.
                    <br />
                    Find your next favourite.
                  </h2>

                  <p className="mt-3 max-w-xl text-sm leading-6 text-teal-50/80 sm:text-base">
                    Explore the songs, albums, and artists making waves across
                    VibeNationHQ.
                  </p>
                </div>

                <Link
                  href="/music/discover/trending"
                  className="inline-flex w-fit shrink-0 items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-bold text-teal-950 transition-colors hover:bg-teal-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-teal-900"
                >
                  Explore trending
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              </div>
            </div>

            <div className="space-y-9 px-4 py-6 sm:space-y-10 sm:px-6 sm:py-8 lg:px-8">
              {!hasTrending ? (
                <EmptyState message="Trending music will appear here as discovery data becomes available." />
              ) : (
                <>
                  {discovery.trending_songs.length > 0 && (
                    <div>
                      <SectionHeading
                        eyebrow="ON REPEAT"
                        title="Trending songs"
                        description="Tracks catching listeners' attention."
                        href="/music/discover/trending"
                      />

                      <SongGrid
                        songs={discovery.trending_songs}
                        limit={4}
                        emptyMessage="No trending songs are available yet."
                      />
                    </div>
                  )}

                  {discovery.trending_albums.length > 0 && (
                    <div>
                      <SectionHeading
                        eyebrow="FULL PROJECTS"
                        title="Trending albums"
                        description="Albums worth exploring."
                        href="/music/discover/trending"
                      />

                      <AlbumGrid
                        albums={discovery.trending_albums}
                        limit={4}
                        emptyMessage="No trending albums are available yet."
                      />
                    </div>
                  )}

                  {discovery.trending_artists.length > 0 && (
                    <div>
                      <SectionHeading
                        eyebrow="MEET THE ARTISTS"
                        title="Trending artists"
                        description="Artists drawing attention from music fans."
                        href="/music/discover/trending"
                      />

                      <ArtistGrid
                        artists={discovery.trending_artists}
                        limit={4}
                        emptyMessage="No trending artists are available yet."
                      />
                    </div>
                  )}
                </>
              )}
            </div>
          </section>

          {/* Community activity */}
          <section aria-labelledby="community-picks-heading">
            <SectionHeading
              id="community-picks-heading"
              eyebrow="POWERED BY THE COMMUNITY"
              title="What fans are saying"
              description="Explore the music inspiring conversations and getting saved by listeners."
              href="/music/discover/most-discussed"
            />

            <div className="space-y-7">
              <DiscoverySection
                title="Most discussed"
                description="Music sparking conversations."
                icon="message"
                href="/music/discover/most-discussed"
              >
                <SongGrid
                  songs={discovery.most_discussed_songs}
                  limit={4}
                  emptyMessage="Songs with the most discussion will appear here."
                />

                {discovery.most_discussed_albums.length > 0 && (
                  <div className="mt-6">
                    <AlbumGrid
                      albums={discovery.most_discussed_albums}
                      limit={4}
                      emptyMessage="No discussed albums are available yet."
                    />
                  </div>
                )}
              </DiscoverySection>

              <DiscoverySection
                title="Most favorited"
                description="Songs and albums listeners are saving."
                icon="music"
                href="/music/discover/most-favorited"
              >
                <SongGrid
                  songs={discovery.most_favorited_songs}
                  limit={4}
                  emptyMessage="Favorited songs will appear here when data is available."
                />

                {discovery.most_favorited_albums.length > 0 && (
                  <div className="mt-6">
                    <AlbumGrid
                      albums={discovery.most_favorited_albums}
                      limit={4}
                      emptyMessage="No favorited albums are available yet."
                    />
                  </div>
                )}
              </DiscoverySection>
            </div>
          </section>

          {/* Ratings */}
          <section aria-labelledby="top-rated-heading">
            <SectionHeading
              id="top-rated-heading"
              eyebrow="THE LISTENERS HAVE SPOKEN"
              title="Top rated"
              description="Explore releases ranked by their average user ratings."
              href="/music/discover/top-rated"
            />

            <DiscoverySection
              title="Highly rated music"
              description="Discover the releases receiving strong ratings."
              icon="star"
              href="/music/discover/top-rated"
            >
              <SongGrid
                songs={discovery.top_rated_songs}
                limit={4}
                emptyMessage="Top-rated songs will appear here when ratings are available."
              />

              {discovery.top_rated_albums.length > 0 && (
                <div className="mt-6">
                  <AlbumGrid
                    albums={discovery.top_rated_albums}
                    limit={4}
                    emptyMessage="No top-rated albums are available yet."
                  />
                </div>
              )}
            </DiscoverySection>
          </section>

          {/* Editorial selections */}
          <section aria-labelledby="featured-heading">
            <SectionHeading
              id="featured-heading"
              eyebrow="HANDPICKED HIGHLIGHTS"
              title="Featured music"
              description="Songs, albums, and artists highlighted on VibeNationHQ."
              href="/music/discover/featured"
            />

            <div className="space-y-7">
              <DiscoverySection
                title="Featured songs"
                description="Selected tracks to check out."
                icon="star"
                href="/music/discover/featured"
              >
                <SongGrid
                  songs={discovery.featured_songs}
                  limit={4}
                  emptyMessage="Featured songs will appear here when available."
                />
              </DiscoverySection>

              {discovery.featured_albums.length > 0 && (
                <DiscoverySection
                  title="Featured albums"
                  description="Selected albums from the music catalog."
                  icon="music"
                  href="/music/discover/featured"
                >
                  <AlbumGrid
                    albums={discovery.featured_albums}
                    limit={4}
                    emptyMessage="Featured albums will appear here when available."
                  />
                </DiscoverySection>
              )}

              {discovery.featured_artists.length > 0 && (
                <DiscoverySection
                  title="Featured artists"
                  description="Artists worth getting to know."
                  icon="users"
                  href="/music/discover/featured"
                >
                  <ArtistGrid
                    artists={discovery.featured_artists}
                    limit={4}
                    emptyMessage="Featured artists will appear here when available."
                  />
                </DiscoverySection>
              )}
            </div>
          </section>

          {/* Latest releases */}
          <section aria-labelledby="recent-heading">
            <SectionHeading
              id="recent-heading"
              eyebrow="FRESH FROM THE CATALOG"
              title="Recently released"
              description="Catch up with newer songs and albums."
              href="/music/discover/recent"
            />

            <div className="space-y-7">
              <DiscoverySection
                title="Latest songs"
                description="Recently released tracks."
                icon="music"
                href="/music/discover/recent"
              >
                <SongGrid
                  songs={discovery.recently_released_songs}
                  limit={4}
                  emptyMessage="Recent songs will appear here when available."
                />
              </DiscoverySection>

              <DiscoverySection
                title="Latest albums"
                description="Newer albums added to the catalog."
                icon="trending"
                href="/music/discover/recent"
              >
                <AlbumGrid
                  albums={discovery.recently_released_albums}
                  limit={4}
                  emptyMessage="Recent albums will appear here when available."
                />
              </DiscoverySection>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
