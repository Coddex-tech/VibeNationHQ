'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowUpRight,
  LoaderCircle,
  MessageCircle,
  Music2,
} from 'lucide-react';

import MusicPost from '@/components/music/CommunityPost';
import {
  getCommunityPosts,
  type CommunityPost,
  type CommunityTargetType,
} from '@/lib/music/CommunityPosts';

type TargetType = Exclude<CommunityTargetType, 'external'>;
type Ordering = 'latest' | 'relevant';

type TargetCommunityPostsProps = {
  targetType: TargetType;
  targetId: number;
  createPostUrl: string;
};

const PAGE_SIZE = 20;

export default function TargetCommunityPosts({
  targetType,
  targetId,
  createPostUrl,
}: TargetCommunityPostsProps) {
  const [ordering, setOrdering] = useState<Ordering>('latest');
  const [page, setPage] = useState(1);
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadPosts() {
      setLoading(true);
      setError(null);

      try {
        const response = await getCommunityPosts({
          targetType,
          targetId,
          ordering,
          page,
          pageSize: PAGE_SIZE,
        });

        if (!active) return;

        setPosts((currentPosts) => {
          if (page === 1) {
            return response.results;
          }

          // Avoid duplicate posts if a page is retried.
          const existingIds = new Set(
            currentPosts.map((post) => post.id),
          );

          const newPosts = response.results.filter(
            (post) => !existingIds.has(post.id),
          );

          return [...currentPosts, ...newPosts];
        });

        setHasMore(response.next !== null);
      } catch (err) {
        if (!active) return;

        console.error('Failed to load community posts:', err);

        setError(
          'We could not load the community posts. Please try again.',
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadPosts();

    return () => {
      active = false;
    };
  }, [targetType, targetId, ordering, page, retryKey]);

  function changeOrdering(nextOrdering: Ordering) {
    if (nextOrdering === ordering) return;

    setPosts([]);
    setHasMore(false);
    setPage(1);
    setOrdering(nextOrdering);
  }

  function retryLoading() {
    setRetryKey((current) => current + 1);
  }

  const isInitialLoading = loading && posts.length === 0;

  return (
    <section className="mt-7 border-t border-light-border pt-5 dark:border-dark-border sm:mt-8 sm:pt-6">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.2em] text-brand-teal-dark dark:text-brand-teal-light">
            The community
          </p>

          <h2 className="text-xl font-semibold tracking-tight text-light-text dark:text-dark-text sm:text-2xl">
            What listeners are saying
          </h2>

          <p className="mt-1.5 max-w-xl text-sm leading-5 text-light-text-soft dark:text-dark-text-soft">
            Reviews, reactions and conversations from the VibeNationHQ
            community.
          </p>
        </div>

        <Link
          href={createPostUrl}
          className="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 self-start rounded-full bg-brand-teal px-4 text-sm font-semibold text-white transition hover:opacity-90 sm:self-auto"
        >
          Write a review
          <ArrowUpRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Latest / Relevant tabs */}
      <div
        className="mt-5 flex items-center gap-1 border-b border-light-border dark:border-dark-border"
        role="tablist"
        aria-label="Sort community posts"
      >
        <button
          type="button"
          role="tab"
          aria-selected={ordering === 'latest'}
          onClick={() => changeOrdering('latest')}
          className={`relative min-h-10 px-4 text-sm font-semibold transition ${
            ordering === 'latest'
              ? 'text-brand-teal-dark dark:text-brand-teal-light'
              : 'text-light-text-soft hover:text-light-text dark:text-dark-text-soft dark:hover:text-dark-text'
          }`}
        >
          Latest

          {ordering === 'latest' && (
            <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-brand-teal" />
          )}
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={ordering === 'relevant'}
          onClick={() => changeOrdering('relevant')}
          className={`relative min-h-10 px-4 text-sm font-semibold transition ${
            ordering === 'relevant'
              ? 'text-brand-teal-dark dark:text-brand-teal-light'
              : 'text-light-text-soft hover:text-light-text dark:text-dark-text-soft dark:hover:text-dark-text'
          }`}
        >
          Relevant

          {ordering === 'relevant' && (
            <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-brand-teal" />
          )}
        </button>
      </div>

      {/* Loading state */}
      {isInitialLoading && (
        <div
          className="flex items-center justify-center gap-2 py-10 text-sm text-light-text-soft dark:text-dark-text-soft"
          role="status"
        >
          <LoaderCircle className="h-4 w-4 animate-spin text-brand-teal" />
          Loading community posts...
        </div>
      )}

      {/* Error state */}
      {!isInitialLoading && error && posts.length === 0 && (
        <div className="mt-4 rounded-xl border border-light-border px-5 py-7 text-center dark:border-dark-border">
          <p className="text-sm text-light-text-soft dark:text-dark-text-soft">
            {error}
          </p>

          <button
            type="button"
            onClick={retryLoading}
            className="mt-3 inline-flex min-h-9 items-center justify-center rounded-full bg-brand-teal px-4 text-sm font-semibold text-white transition hover:opacity-90"
          >
            Try again
          </button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && posts.length === 0 && (
        <div className="mt-4 rounded-xl border border-dashed border-light-border px-5 py-7 text-center dark:border-dark-border sm:py-8">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl border border-light-border bg-light-surface-soft dark:border-dark-border dark:bg-dark-surface-soft">
            <Music2 className="h-5 w-5 text-brand-teal" />
          </div>

          <h3 className="mt-3 text-sm font-semibold text-light-text dark:text-dark-text">
            Start the conversation
          </h3>

          <p className="mx-auto mt-1.5 max-w-sm text-sm leading-5 text-light-text-soft dark:text-dark-text-soft">
            There are no community posts for this music profile yet.
            Share your thoughts and help get things started.
          </p>

          <Link
            href={createPostUrl}
            className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-teal-dark transition hover:opacity-80 dark:text-brand-teal-light"
          >
            Write the first review
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
      )}

      {/* Posts */}
      {posts.length > 0 && (
        <div className="mt-4 space-y-1">
          {posts.map((post) => (
            <MusicPost
              key={post.id}
              post={post}
              variant="feed"
              showFollowButton={false}
              hideMusicAttachment
              likeCommentOnly
            />
          ))}
        </div>
      )}

      {/* Error while loading another page */}
      {error && posts.length > 0 && (
        <div className="mt-4 rounded-xl border border-light-border px-4 py-4 text-center dark:border-dark-border">
          <p className="text-sm text-light-text-soft dark:text-dark-text-soft">
            {error}
          </p>

          <button
            type="button"
            onClick={retryLoading}
            className="mt-2 text-sm font-semibold text-brand-teal-dark hover:opacity-80 dark:text-brand-teal-light"
          >
            Try again
          </button>
        </div>
      )}

      {/* Pagination */}
      {hasMore && !error && (
        <div className="mt-5 flex justify-center">
          <button
            type="button"
            onClick={() => setPage((current) => current + 1)}
            disabled={loading}
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-full border border-light-border bg-light-surface px-5 text-sm font-semibold text-light-text transition hover:border-brand-teal hover:text-brand-teal-dark disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface dark:text-dark-text dark:hover:text-brand-teal-light"
          >
            {loading ? (
              <>
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <MessageCircle className="h-4 w-4" />
                Load more
              </>
            )}
          </button>
        </div>
      )}
    </section>
  );
}
