export default function MusicFeedSkeleton() {
  return (
    <section
      aria-label="Loading music feed"
      aria-busy="true"
      className="w-full"
    >
      <div
        className="
          divide-y
          divide-light-border-soft
          dark:divide-dark-border-soft
        "
      >
        <MusicPostSkeleton />
        <MusicPostSkeleton />
        <MusicPostSkeleton />
      </div>
    </section>
  );
}

function MusicPostSkeleton() {
  return (
    <article
      className="
        px-4 py-5
        sm:px-6 sm:py-6
      "
    >
      {/* Post header */}
      <div className="flex items-start gap-3">
        <div
          className="
            h-10 w-10 shrink-0
            animate-pulse rounded-full
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div className="min-w-0 flex-1">
          <div
            className="
              h-3.5 w-28 max-w-full
              animate-pulse rounded
              bg-light-surface-muted
              dark:bg-dark-surface-muted
            "
          />

          <div
            className="
              mt-2 h-3 w-20
              animate-pulse rounded
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />
        </div>

        <div
          className="
            h-7 w-7 shrink-0
            animate-pulse rounded-lg
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />
      </div>

      {/* Thought */}
      <div className="mt-4 space-y-2">
        <div
          className="
            h-4 w-full
            animate-pulse rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            h-4 w-11/12
            animate-pulse rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            h-4 w-2/3
            animate-pulse rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />
      </div>

      {/* Music attachment */}
      <div
        className="
          mt-5
          rounded-2xl
          border border-light-border
          bg-light-surface-soft
          p-3.5
          dark:border-dark-border
          dark:bg-dark-surface-soft
        "
      >
        <div className="flex items-center gap-3">
          <div
            className="
              h-14 w-14 shrink-0
              animate-pulse rounded-xl
              bg-light-surface-muted
              dark:bg-dark-surface-muted
            "
          />

          <div className="min-w-0 flex-1">
            <div
              className="
                h-3.5 w-32 max-w-full
                animate-pulse rounded
                bg-light-surface-muted
                dark:bg-dark-surface-muted
              "
            />

            <div
              className="
                mt-2 h-3 w-24 max-w-full
                animate-pulse rounded
                bg-light-surface-soft
                dark:bg-dark-surface-soft
              "
            />

            <div
              className="
                mt-2 h-3 w-16
                animate-pulse rounded
                bg-light-surface-soft
                dark:bg-dark-surface-soft
              "
            />
          </div>

          <div
            className="
              h-9 w-9 shrink-0
              animate-pulse rounded-full
              bg-light-surface-muted
              dark:bg-dark-surface-muted
            "
          />
        </div>
      </div>

      {/* Engagement */}
      <div className="mt-4 flex items-center gap-5">
        <div
          className="
            h-4 w-12
            animate-pulse rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />

        <div
          className="
            h-4 w-12
            animate-pulse rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />

        <div
          className="
            h-4 w-10
            animate-pulse rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />

        <div className="ml-auto">
          <div
            className="
              h-4 w-10
              animate-pulse rounded
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />
        </div>
      </div>
    </article>
  );
}