'use client';

import Link from 'next/link';
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import {
  Loader2,
  Music2,
  Plus,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

import {
  getMusicFeed,
  type MusicFeedItem,
  type MusicFeedResponse,
} from '@/lib/music/MusicFeed';

import MusicEditorialPost from '../editorial/MusicEditorialPost';
import MusicPost from './CommunityPost';

type MusicFeedProps = {
  initialFeed: MusicFeedResponse;
};

export default function MusicFeed({
  initialFeed,
}: MusicFeedProps) {
  const [feed, setFeed] =
    useState<MusicFeedResponse>(initialFeed);

  const [isLoadingMore, setIsLoadingMore] =
    useState(false);

  const [loadMoreError, setLoadMoreError] =
    useState<string | null>(null);

  const [showCreateButton, setShowCreateButton] =
    useState(true);

  /*
   * The ref prevents multiple requests from starting
   * before React has updated the loading state.
   */
  const loadingMoreRef = useRef(false);

  /*
   * This element is observed by IntersectionObserver.
   * When it enters the viewport, the next feed page loads.
   */
  const loadMoreTriggerRef =
    useRef<HTMLDivElement | null>(null);

  /*
   * Only the first eligible community post from each author
   * receives a Follow button.
   *
   * This calculation includes every loaded page.
   */
  const followButtonPostIds = useMemo(() => {
    const eligiblePostIds = new Set<number>();
    const seenAuthorIds = new Set<number>();

    for (const item of feed.results) {
      if (item.content_type !== 'community_post') {
        continue;
      }

      const post = item.content;
      const authorId = Number(post.user.id);

      if (
        !Number.isFinite(authorId) ||
        authorId <= 0 ||
        post.user.is_following ||
        seenAuthorIds.has(authorId)
      ) {
        continue;
      }

      seenAuthorIds.add(authorId);
      eligiblePostIds.add(Number(post.id));
    }

    return eligiblePostIds;
  }, [feed.results]);

  /*
   * Fetch the next page from the backend's existing
   * mixed-feed snapshot.
   *
   * The backend remains responsible for:
   * - Community/editorial mixing
   * - Ranking
   * - Personalization
   * - Cursor pagination
   *
   * The frontend only appends the returned items.
   */
  const handleLoadMore = useCallback(async () => {
    if (
      loadingMoreRef.current ||
      !feed.has_more ||
      !feed.next_cursor
    ) {
      return;
    }

    loadingMoreRef.current = true;
    setIsLoadingMore(true);
    setLoadMoreError(null);

    try {
      const nextPage = await getMusicFeed({
        cursor: feed.next_cursor,
      });

      setFeed((currentFeed) => {
        /*
         * Protect against duplicate entries if an item
         * is unexpectedly repeated in a response.
         */
        const existingIds = new Set(
          currentFeed.results.map(
            (item) =>
              `${item.content_type}-${item.content.id}`,
          ),
        );

        const newItems = nextPage.results.filter(
          (item) =>
            !existingIds.has(
              `${item.content_type}-${item.content.id}`,
            ),
        );

        return {
          results: [
            ...currentFeed.results,
            ...newItems,
          ],
          has_more: nextPage.has_more,
          next_cursor: nextPage.next_cursor,
        };
      });
    } catch (error) {
      console.error(
        'Failed to load more music feed items:',
        error,
      );

      setLoadMoreError(
        'We couldn’t load more posts. Please try again.',
      );
    } finally {
      loadingMoreRef.current = false;
      setIsLoadingMore(false);
    }
  }, [feed.has_more, feed.next_cursor]);

  /*
   * Automatic infinite scrolling.
   *
   * When the loading trigger approaches the viewport,
   * fetch the next page automatically.
   *
   * The 600px root margin starts loading before the
   * user reaches the absolute bottom of the feed.
   */
  useEffect(() => {
    const trigger = loadMoreTriggerRef.current;

    if (
      !trigger ||
      !feed.has_more ||
      isLoadingMore ||
      loadMoreError
    ) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];

        if (entry?.isIntersecting) {
          void handleLoadMore();
        }
      },
      {
        root: null,
        rootMargin: '600px 0px',
        threshold: 0,
      },
    );

    observer.observe(trigger);

    return () => {
      observer.disconnect();
    };
  }, [
    feed.has_more,
    isLoadingMore,
    loadMoreError,
    handleLoadMore,
  ]);

  /*
   * Hide the floating create button while scrolling down.
   * Reveal it immediately when scrolling back up.
   */
  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDelta =
        currentScrollY - lastScrollY;

      if (scrollDelta > 4) {
        setShowCreateButton(false);
      } else if (scrollDelta < -4) {
        setShowCreateButton(true);
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener(
      'scroll',
      handleScroll,
      { passive: true },
    );

    return () => {
      window.removeEventListener(
        'scroll',
        handleScroll,
      );
    };
  }, []);

  return (
    <>
      <section
        aria-label="Music feed"
        className="w-full"
      >
        {feed.results.length === 0 ? (
          <MusicFeedEmptyState />
        ) : (
          <div>
            {feed.results.map((item) => (
              <MusicFeedItemView
                key={`${item.content_type}-${item.content.id}`}
                item={item}
                showFollowButton={
                  item.content_type === 'community_post' &&
                  followButtonPostIds.has(
                    Number(item.content.id),
                  )
                }
              />
            ))}
          </div>
        )}

        {/* Loading error and manual retry */}
        {loadMoreError && (
          <div
            role="alert"
            className="
              mt-6 rounded-xl
              border border-red-200
              bg-red-50
              px-4 py-4
              text-center
              dark:border-red-900/50
              dark:bg-red-950/20
            "
          >
            <p
              className="
                text-sm
                text-red-700
                dark:text-red-300
              "
            >
              {loadMoreError}
            </p>

            <button
              type="button"
              onClick={() => {
                void handleLoadMore();
              }}
              disabled={isLoadingMore}
              className="
                mt-3 inline-flex
                items-center gap-2
                rounded-full
                bg-red-100
                px-4 py-2
                text-xs font-semibold
                text-red-700
                transition-colors
                hover:bg-red-200
                disabled:cursor-not-allowed
                disabled:opacity-60
                dark:bg-red-900/30
                dark:text-red-300
                dark:hover:bg-red-900/50
              "
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Try again
            </button>
          </div>
        )}

        {/* Automatic loading trigger */}
        {feed.has_more && (
          <div
            ref={loadMoreTriggerRef}
            aria-live="polite"
            aria-busy={isLoadingMore}
            className="
              flex min-h-36
              flex-col
              items-center
              justify-center
              border-t border-light-border-soft
              px-5 py-10
              text-center
              dark:border-dark-border-soft
            "
          >
            <div
              className="
                flex h-10 w-10
                items-center justify-center
                rounded-full
                bg-brand-teal/10
                text-brand-teal
                dark:bg-brand-teal/15
              "
            >
              {isLoadingMore ? (
                <Loader2
                  className="
                    h-5 w-5
                    animate-spin
                  "
                />
              ) : (
                <Sparkles className="h-5 w-5" />
              )}
            </div>

            <p
              className="
                mt-3 text-sm font-semibold
                text-light-text
                dark:text-dark-text
              "
            >
              {isLoadingMore
                ? 'Finding more music for you...'
                : 'More music waiting for you'}
            </p>

            <p
              className="
                mt-1 text-xs leading-5
                text-light-text-muted
                dark:text-dark-text-muted
              "
            >
              {isLoadingMore
                ? 'Please wait while we load your next feed.'
                : 'Keep scrolling to discover more conversations and editorial stories.'}
            </p>
          </div>
        )}

        {/* All feed items exhausted */}
        {!feed.has_more &&
          feed.results.length > 0 && (
            <div
              className="
                border-t border-light-border-soft
                px-5 py-10
                text-center
                dark:border-dark-border-soft
              "
            >
              <div
                className="
                  mx-auto flex h-10 w-10
                  items-center justify-center
                  rounded-full
                  bg-brand-teal/10
                  text-brand-teal
                  dark:bg-brand-teal/15
                "
              >
                <Sparkles className="h-5 w-5" />
              </div>

              <p
                className="
                  mt-3 text-sm font-semibold
                  text-light-text
                  dark:text-dark-text
                "
              >
                You’re all caught up!
              </p>

              <p
                className="
                  mt-1 text-xs leading-5
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                You've reached the end of your music feed.
                Check back later for more.
              </p>
            </div>
          )}
      </section>

      {/* Floating create post button */}
      <Link
        href="/music/create"
        aria-label="Create music post"
        className={`
          fixed
          right-5
          bottom-[calc(1.25rem+env(safe-area-inset-bottom))]
          z-50

          flex
          h-14
          w-14
          items-center
          justify-center

          rounded-full
          bg-brand-teal
          text-white

          shadow-lg
          shadow-brand-teal/20

          transition-all
          duration-250
          ease-out

          hover:scale-[1.04]
          hover:shadow-xl
          hover:shadow-brand-teal/25

          active:scale-95

          focus:outline-none
          focus-visible:ring-4
          focus-visible:ring-brand-teal/25
          focus-visible:ring-offset-2
          focus-visible:ring-offset-light-bg

          dark:focus-visible:ring-offset-dark-bg

          sm:right-7
          sm:bottom-[calc(1.75rem+env(safe-area-inset-bottom))]

          ${
            showCreateButton
              ? `
                translate-y-0
                scale-100
                opacity-100
                pointer-events-auto
              `
              : `
                translate-y-24
                scale-95
                opacity-0
                pointer-events-none
              `
          }
        `}
      >
        <Plus
          className="
            h-6 w-6
            transition-transform
            duration-200
          "
          strokeWidth={2.5}
        />
      </Link>
    </>
  );
}

type MusicFeedItemViewProps = {
  item: MusicFeedItem;
  showFollowButton: boolean;
};

function MusicFeedItemView({
  item,
  showFollowButton,
}: MusicFeedItemViewProps) {
  switch (item.content_type) {
    case 'community_post':
      return (
        <MusicPost
          post={item.content}
          showFollowButton={showFollowButton}
        />
      );

    case 'editorial':
      return (
        <MusicEditorialPost
          article={item.content}
        />
      );

    default:
      return null;
  }
}

function MusicFeedEmptyState() {
  return (
    <div
      className="
        border-b border-light-border-soft
        px-5 py-16
        text-center
        dark:border-dark-border-soft
      "
    >
      <div
        className="
          mx-auto flex h-14 w-14
          items-center justify-center
          rounded-2xl
          bg-brand-teal/10
          text-brand-teal
          dark:bg-brand-teal/15
        "
      >
        <Music2 className="h-6 w-6" />
      </div>

      <h2
        className="
          mt-5 text-lg font-bold
          text-light-text
          dark:text-dark-text
        "
      >
        Your music feed is quiet
      </h2>

      <p
        className="
          mx-auto mt-2 max-w-md
          text-sm leading-6
          text-light-text-muted
          dark:text-dark-text-muted
        "
      >
        Follow artists, discover songs, and join
        conversations to start building your feed.
      </p>
    </div>
  );
}