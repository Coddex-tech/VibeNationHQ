import type { Metadata } from 'next';

import MusicCreateForm from '@/components/music/MusicCreateForm';

export const metadata: Metadata = {
  title: 'Create a Music Post',
  description:
    'Share what you think, start a conversation, or share something you discovered with the VibeNationHQ community.',
  robots: {
    index: false,
    follow: true,
  },
};

export default function MusicCreatePage() {
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
      <main
        className="
          mx-auto
          w-full
          max-w-3xl
          px-4
          py-8
          sm:px-6
          sm:py-10
          lg:px-8
          lg:py-14
        "
      >
        <MusicCreateForm />
      </main>
    </div>
  );
}