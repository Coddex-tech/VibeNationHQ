
import MusicNavigation from '@/components/music/MusicNavigation';

function SkeletonBlock({
  className = '',
  width,
}: {
  className?: string;
  width?: number;
}) {
  return (
    <div
      style={width ? { width } : undefined}
      className={`
        animate-pulse rounded-lg
        bg-light-border-soft
        dark:bg-dark-border-soft
        ${className}
      `}
      aria-hidden="true"
    />
  );
}

function DiscoveryCardSkeleton() {
  return (
    <div
      className="
        flex min-w-0 gap-3
        rounded-xl border
        border-light-border-soft
        bg-light-surface p-3
        dark:border-dark-border-soft
        dark:bg-dark-surface
      "
      aria-hidden="true"
    >
      <SkeletonBlock className="h-20 w-20 shrink-0 rounded-lg" />

      <div className="min-w-0 flex-1 space-y-3 py-1">
        <SkeletonBlock className="h-4 w-4/5" />
        <SkeletonBlock className="h-3 w-3/5" />

        <div className="flex gap-3">
          <SkeletonBlock className="h-3 w-12" />
          <SkeletonBlock className="h-3 w-12" />
        </div>
      </div>
    </div>
  );
}

function DiscoverySectionSkeleton({
  cardCount = 4,
}: {
  cardCount?: number;
}) {
  return (
    <section
      className="
        rounded-2xl border
        border-light-border-soft
        bg-light-surface p-4
        sm:p-6
        dark:border-dark-border-soft
        dark:bg-dark-surface
      "
      aria-hidden="true"
    >
      <div className="mb-5">
        <SkeletonBlock className="h-3 w-28" />
        <SkeletonBlock className="mt-3 h-6 w-48 max-w-full" />
        <SkeletonBlock className="mt-2 h-4 w-64 max-w-full" />
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {Array.from({ length: cardCount }, (_, index) => (
          <DiscoveryCardSkeleton key={index} />
        ))}
      </div>
    </section>
  );
}

export default function MusicDiscoveryLoading() {
  return (
    <div
      className="
        min-h-screen
        bg-light-bg text-light-text
        dark:bg-dark-bg dark:text-dark-text
      "
      role="status"
      aria-label="Loading music discovery"
    >
      <MusicNavigation />

      <main
        className="
          mx-auto w-full max-w-7xl
          space-y-7 px-4 py-6
          sm:px-6 sm:py-8 lg:px-8
        "
      >
        {/* Page introduction skeleton */}
        <div
          className="
            relative overflow-hidden
            rounded-2xl border
            border-light-border-soft
            bg-light-surface p-5
            sm:p-7
            dark:border-dark-border-soft
            dark:bg-dark-surface
          "
          aria-hidden="true"
        >
          <SkeletonBlock className="h-3 w-36" />
          <SkeletonBlock className="mt-4 h-9 w-64 max-w-full" />
          <SkeletonBlock className="mt-3 h-4 w-full max-w-2xl" />
          <SkeletonBlock className="mt-2 h-4 w-3/4 max-w-xl" />
        </div>

        {/* Category navigation skeleton */}
        <div className="flex gap-2 overflow-hidden" aria-hidden="true">
        {[112, 145, 145, 110, 105, 95].map((width, index) => (
            <SkeletonBlock
            key={index}
            width={width}
            className="h-10 shrink-0 rounded-full"
            />
        ))}
        </div>

        {/* Featured trending area skeleton */}
        <section
          className="
            overflow-hidden rounded-3xl
            border border-light-border-soft
            bg-light-surface
            dark:border-dark-border-soft
            dark:bg-dark-surface
          "
          aria-hidden="true"
        >
          <div className="bg-gradient-to-br from-teal-950 via-teal-900 to-slate-950 px-5 py-7 sm:px-8 sm:py-9">
            <SkeletonBlock className="h-6 w-44 bg-white/15" />
            <SkeletonBlock className="mt-5 h-8 w-full max-w-md bg-white/15" />
            <SkeletonBlock className="mt-2 h-8 w-3/4 max-w-sm bg-white/15" />
            <SkeletonBlock className="mt-4 h-4 w-full max-w-xl bg-white/15" />
            <SkeletonBlock className="mt-5 h-11 w-40 rounded-xl bg-white/15" />
          </div>

          <div className="space-y-8 p-4 sm:p-6">
            <div>
              <SkeletonBlock className="mb-3 h-3 w-28" />
              <SkeletonBlock className="mb-4 h-6 w-44" />
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {[1, 2, 3, 4].map((item) => (
                  <DiscoveryCardSkeleton key={item} />
                ))}
              </div>
            </div>
          </div>
        </section>

        <DiscoverySectionSkeleton />
        <DiscoverySectionSkeleton />
        <DiscoverySectionSkeleton cardCount={2} />

        <p className="sr-only">
          Loading discovery content. Please wait.
        </p>
      </main>
    </div>
  );
}
