
import type { Metadata } from 'next';

import MusicFeed from '@/components/music/MusicFeed';
import MusicFeedTabs from '@/components/music/MusicFeedTabs';
import MusicNavigation from '@/components/music/MusicNavigation';
import MusicRightSidebar from '@/components/music/MusicRightSidebar';

import { getInitialMusicFeed } from '@/lib/music/MusicFeedServer';

type MusicPageProps = {
  searchParams: Promise<{
    new_post_id?: string | string[];
  }>;
};

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ??
  'http://localhost:3000';

const musicTitle =
  'Music Community, Songs & Artists';

const musicDescription =
  'Discover songs, artists and albums, share your thoughts, follow artists, and join music conversations on VibeNationHQ.';

export const metadata: Metadata = {
  title: musicTitle,

  description: musicDescription,

  alternates: {
    canonical: '/music',
  },

  openGraph: {
    type: 'website',
    title: musicTitle,
    description: musicDescription,
    url: '/music',
  },

  twitter: {
    card: 'summary',
    title: musicTitle,
    description: musicDescription,
  },
};

export default async function MusicPage({
  searchParams,
}: MusicPageProps) {
  const params = await searchParams;

  const newPostId =
    typeof params.new_post_id === 'string'
      ? params.new_post_id
      : undefined;

  const initialFeed =
    await getInitialMusicFeed(newPostId);

  const musicUrl = `${siteUrl}/music`;

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    '@id': `${musicUrl}#collectionpage`,
    name: musicTitle,
    description: musicDescription,
    url: musicUrl,

    isPartOf: {
      '@type': 'WebSite',
      '@id': `${siteUrl}#website`,
    },

    mainEntity: {
      '@type': 'ItemList',
      name: 'VibeNationHQ Music',
      url: musicUrl,
    },
  };

  return (
    <div
      className="
        min-h-screen
        bg-light-bg
        text-light-text
        dark:bg-dark-bg
        dark:text-dark-text
      "
    >
      <MusicNavigation />

      <div
        className="
          sticky top-0 z-40
        "
      >
        <MusicFeedTabs />
      </div>

      <main
        className="
          mx-auto
          w-full max-w-7xl
          px-4
          py-6
          sm:px-6
          lg:px-8
        "
      >
        <h1 className="sr-only">
          Music Community, Songs and Artists
        </h1>

        <div
          className="
            grid
            grid-cols-1
            gap-8
            lg:grid-cols-[minmax(0,1fr)_320px]
            lg:items-start
            xl:gap-10
          "
        >
          <section
            className="
              mx-auto w-full
              min-w-0 max-w-3xl
              lg:mx-0
            "
            aria-label="Music community feed"
          >
            <MusicFeed
              initialFeed={initialFeed}
            />
          </section>

          <MusicRightSidebar />
        </div>
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            structuredData,
          ),
        }}
      />
    </div>
  );
}
