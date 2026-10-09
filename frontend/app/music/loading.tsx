import MusicFeedSkeleton from '@/components/music/MusicFeedSkeleton';

export default function MusicLoading() {
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
      <MusicFeedSkeleton />
    </div>
  );
}