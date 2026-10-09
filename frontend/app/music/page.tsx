import type { Metadata } from 'next';

import MusicFeed from '@/components/music/MusicFeed';
import MusicFeedTabs from '@/components/music/MusicFeedTabs';
import MusicNavigation from '@/components/music/MusicNavigation';
import { getInitialMusicFeed } from '@/lib/music/MusicFeedServer';

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

export default async function MusicPage() {
  const initialFeed =
    await getInitialMusicFeed();

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
          mx-auto w-full max-w-3xl
        "
      >
        <h1 className="sr-only">
          Music Community, Songs and Artists
        </h1>

        <MusicFeed
          initialFeed={initialFeed}
        />
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