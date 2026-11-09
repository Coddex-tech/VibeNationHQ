'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  ArrowLeft,
  Bookmark,
  CalendarDays,
  Check,
  Copy,
  Eye,
  Heart,
  MessageCircle,
  Music2,
  UserRound,
} from 'lucide-react';

import { ApiError } from '@/lib/api';

import EditorialArticleComments from '@/components/music/EditorialArticleComments';

import {
  favoriteEditorialArticle,
  getEditorialArticle,
  likeEditorialArticle,
  recordEditorialArticleView,
  unfavoriteEditorialArticle,
  unlikeEditorialArticle,
  type EditorialArticle,
} from '@/lib/music/EditorialArticles';

type EditorialArticleDetailClientProps = {
  slug: string;
};

function formatDate(value: string | null): string {
  if (!value) {
    return 'Date unavailable';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return 'Date unavailable';
  }

  return new Intl.DateTimeFormat('en-NG', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(date);
}

function formatCount(value: number): string {
  return new Intl.NumberFormat('en-NG', {
    notation: value >= 10000 ? 'compact' : 'standard',
    maximumFractionDigits: 1,
  }).format(value);
}

function EditorialArticleSkeleton() {
  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="animate-pulse space-y-6">
        <div className="h-5 w-32 rounded bg-gray-200 dark:bg-gray-700" />

        <div className="space-y-3">
          <div className="h-9 w-full max-w-3xl rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-9 w-4/5 max-w-2xl rounded bg-gray-200 dark:bg-gray-700" />
        </div>

        <div className="h-4 w-64 rounded bg-gray-200 dark:bg-gray-700" />

        <div className="h-32 rounded-2xl bg-gray-200 dark:bg-gray-700" />

        <div className="space-y-3">
          <div className="h-4 w-full rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-full rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-5/6 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-full rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    </main>
  );
}

export default function EditorialArticleDetailClient({
  slug,
}: EditorialArticleDetailClientProps) {
  const [article, setArticle] =
    useState<EditorialArticle | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [isLiking, setIsLiking] = useState(false);
  const [likeError, setLikeError] = useState<string | null>(null);

  const [isFavoriting, setIsFavoriting] = useState(false);
  const [favoriteError, setFavoriteError] = useState<string | null>(null);

  const [isCopied, setIsCopied] = useState(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const viewRecordedRef = useRef(false);
  const activeSlugRef = useRef(slug);
  const commentsAnchorRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (activeSlugRef.current !== slug) {
      activeSlugRef.current = slug;
      viewRecordedRef.current = false;
    }

    let cancelled = false;

    async function loadArticle() {
      setIsLoading(true);
      setLoadError(null);
      setArticle(null);

      try {
        const result = await getEditorialArticle(slug);

        if (cancelled) {
          return;
        }

        setArticle(result);

        // Record at most one view for this article visit.
        // The ref survives React Strict Mode's effect replay.
        if (!viewRecordedRef.current) {
          viewRecordedRef.current = true;

          try {
            const viewResult = await recordEditorialArticleView(
              result.id,
            );

            if (!cancelled) {
              setArticle((current) => {
                if (!current || current.id !== result.id) {
                  return current;
                }

                return {
                  ...current,
                  views_count: viewResult.views_count,
                };
              });
            }
          } catch {
            // A view-recording failure should not prevent
            // the article itself from being displayed.
          }
        }
      } catch (error) {
        if (cancelled) {
          return;
        }

        if (error instanceof ApiError && error.status === 404) {
          setLoadError(
            'This article could not be found. It may have been removed or is no longer published.',
          );
        } else {
          setLoadError(
            'We could not load this article. Please check your connection and try again.',
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadArticle();

    return () => {
      cancelled = true;
    };
  }, [slug]);

  // Support direct links such as /music/editorial/example#comments.
  // Wait until the article has loaded and the comments section exists.
  useEffect(() => {
    if (isLoading || !article || window.location.hash !== '#comments') {
      return;
    }

    const frame = window.requestAnimationFrame(() => {
      commentsAnchorRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    });

    return () => {
      window.cancelAnimationFrame(frame);
    };
  }, [isLoading, article]);

  async function handleLike() {
    if (!article || isLiking) {
      return;
    }

    setIsLiking(true);
    setLikeError(null);
    setFavoriteError(null);
    setActionNotice(null);

    try {
      const result = article.liked
        ? await unlikeEditorialArticle(article.id)
        : await likeEditorialArticle(article.id);

      setArticle((current) => {
        if (!current || current.id !== article.id) {
          return current;
        }

        return {
          ...current,
          liked: result.liked,
          likes_count: result.likes_count,
        };
      });
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401 || error.status === 403) {
          setLikeError(
            'Please sign in to like this article. If you are already signed in, refresh the page and try again.',
          );
        } else {
          setLikeError(
            error.message ||
              'Unable to update your like. Please try again.',
          );
        }
      } else {
        setLikeError(
          'Unable to update your like. Please check your connection and try again.',
        );
      }
    } finally {
      setIsLiking(false);
    }
  }

  async function handleFavorite() {
    if (!article || isFavoriting) {
      return;
    }

    setIsFavoriting(true);
    setFavoriteError(null);
    setLikeError(null);
    setActionNotice(null);

    try {
      const result = article.favorited
        ? await unfavoriteEditorialArticle(article.id)
        : await favoriteEditorialArticle(article.id);

      setArticle((current) => {
        if (!current || current.id !== article.id) {
          return current;
        }

        return {
          ...current,
          favorited: result.favorited,
          favorites_count: result.favorites_count,
        };
      });
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401 || error.status === 403) {
          setFavoriteError(
            'Please sign in to save this article to your favorites. If you are already signed in, refresh the page and try again.',
          );
        } else {
          setFavoriteError(
            error.message ||
              'Unable to update your favorites. Please try again.',
          );
        }
      } else {
        setFavoriteError(
          'Unable to update your favorites. Please check your connection and try again.',
        );
      }
    } finally {
      setIsFavoriting(false);
    }
  }

  async function handleCopyLink() {
    setActionNotice(null);
    setLikeError(null);
    setFavoriteError(null);

    try {
      await navigator.clipboard.writeText(window.location.href);
      setIsCopied(true);

      window.setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch {
      setActionNotice(
        'Unable to copy the link. Please copy the page URL from your browser.',
      );
    }
  }

  function handleComments() {
    setActionNotice(null);
    setLikeError(null);
    setFavoriteError(null);

    // Keep the URL in sync so the comments section can be linked directly.
    window.history.replaceState(
      null,
      '',
      `${window.location.pathname}${window.location.search}#comments`,
    );

    commentsAnchorRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }

  if (isLoading) {
    return <EditorialArticleSkeleton />;
  }

  if (loadError || !article) {
    return (
      <main className="mx-auto w-full max-w-3xl px-4 py-16 sm:px-6">
        <div className="rounded-2xl border border-light-border bg-light-surface p-6 dark:border-dark-border dark:bg-dark-surface sm:p-8">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-300">
            <AlertCircle size={24} />
          </div>

          <h1 className="text-xl font-bold text-light-text dark:text-dark-text">
            Unable to display this article
          </h1>

          <p className="mt-3 text-sm leading-6 text-light-muted dark:text-dark-muted">
            {loadError ?? 'Something went wrong while loading this article.'}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-6 rounded-xl bg-brand-teal px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-teal-dark"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  const relatedItems = [
    article.song
      ? {
          key: 'song',
          label: 'Related song',
          title: article.song.title,
          subtitle: [
            ...article.song.artists,
            ...article.song.featured_artists,
          ]
            .map((artist) => artist.name)
            .join(', '),
          image: article.song.artwork,
        }
      : null,

    article.artist
      ? {
          key: 'artist',
          label: 'Related artist',
          title: article.artist.name,
          subtitle: article.artist.is_verified
            ? 'Verified artist'
            : 'Artist',
          image: article.artist.profile_image,
        }
      : null,

    article.album
      ? {
          key: 'album',
          label: 'Related album',
          title: article.album.title,
          subtitle: article.album.artists
            .map((artist) => artist.name)
            .join(', '),
          image: article.album.artwork,
        }
      : null,
  ].filter((item) => item !== null);

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <Link
        href="/music"
        className="mb-8 inline-flex items-center gap-2 rounded-lg py-2 text-sm font-medium text-light-muted transition hover:text-brand-teal dark:text-dark-muted dark:hover:text-brand-teal-light"
      >
        <ArrowLeft size={17} />
        Back to music
      </Link>

      <article>
        <header>
          <div className="mb-5 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-brand-teal/10 px-3 py-1 text-xs font-semibold text-brand-teal dark:text-brand-teal-light">
              Music Editorial
            </span>

            {article.is_featured && (
              <span className="rounded-full border border-brand-teal/30 px-3 py-1 text-xs font-semibold text-brand-teal dark:text-brand-teal-light">
                Featured
              </span>
            )}
          </div>

          <h1 className="max-w-4xl text-3xl font-extrabold leading-tight tracking-tight text-light-text dark:text-dark-text sm:text-4xl lg:text-5xl">
            {article.title}
          </h1>

          {article.excerpt && (
            <p className="mt-5 max-w-3xl text-base leading-7 text-light-muted dark:text-dark-muted sm:text-lg sm:leading-8">
              {article.excerpt}
            </p>
          )}

          <div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-3 border-b border-light-border pb-6 text-sm text-light-muted dark:border-dark-border dark:text-dark-muted">
            <div className="inline-flex items-center gap-2">
              <UserRound size={17} className="shrink-0" />
              <span className="font-medium text-light-text dark:text-dark-text">
                {article.author.name}
              </span>
            </div>

            <div className="inline-flex items-center gap-2">
              <CalendarDays size={17} className="shrink-0" />
              <time dateTime={article.published_at ?? undefined}>
                {formatDate(article.published_at)}
              </time>
            </div>

            <div className="inline-flex items-center gap-2">
              <Eye size={17} className="shrink-0" />
              <span>{formatCount(article.views_count)} views</span>
            </div>
          </div>
        </header>

        {article.genres.length > 0 && (
          <div className="mt-6 flex flex-wrap gap-2">
            {article.genres.map((genre) => (
              <span
                key={genre.id}
                className="rounded-lg bg-light-surface px-3 py-1.5 text-xs font-medium text-light-muted dark:bg-dark-surface dark:text-dark-muted"
              >
                {genre.name}
              </span>
            ))}
          </div>
        )}

        <div className="mt-8 w-full">
          {/* Main article column */}
          <div className="min-w-0">
            {/* Article story */}
            <div className="rounded-2xl border border-light-border bg-light-surface p-5 dark:border-dark-border dark:bg-dark-surface sm:p-8">
              <div className="whitespace-pre-wrap break-words text-base leading-8 text-light-text dark:text-dark-text sm:text-[17px] sm:leading-9">
                {article.content}
              </div>
            </div>

            {/* Related music */}
            {relatedItems.length > 0 && (
              <aside className="mt-5 min-w-0 rounded-2xl border border-light-border bg-light-surface p-5 dark:border-dark-border dark:bg-dark-surface">
                <div className="mb-5 flex items-center gap-2">
                  <Music2
                    size={19}
                    className="text-brand-teal dark:text-brand-teal-light"
                  />

                  <h2 className="font-bold text-light-text dark:text-dark-text">
                    Related music
                  </h2>
                </div>

                <div className="space-y-5">
                  {relatedItems.map((item) => (
                    <div
                      key={item.key}
                      className="flex min-w-0 items-center gap-3"
                    >
                      <div className="h-14 w-14 shrink-0 overflow-hidden rounded-xl bg-gray-100 dark:bg-gray-800">
                        {item.image ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={item.image}
                            alt={item.title}
                            loading="lazy"
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="flex h-full w-full items-center justify-center text-light-muted dark:text-dark-muted">
                            <Music2 size={23} />
                          </div>
                        )}
                      </div>

                      <div className="min-w-0">
                        <p className="text-xs font-medium text-brand-teal dark:text-brand-teal-light">
                          {item.label}
                        </p>

                        <p className="mt-1 break-words text-sm font-semibold text-light-text dark:text-dark-text">
                          {item.title}
                        </p>

                        {item.subtitle && (
                          <p className="mt-1 line-clamp-2 text-xs text-light-muted dark:text-dark-muted">
                            {item.subtitle}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </aside>
            )}

            {/* Article engagement bar */}
            <section
              aria-label="Article interactions"
              className="mt-5 overflow-hidden rounded-2xl border border-light-border bg-light-surface dark:border-dark-border dark:bg-dark-surface"
            >
              <div className="grid grid-cols-4 divide-x divide-light-border dark:divide-dark-border">
                {/* Like */}
                <button
                  type="button"
                  onClick={handleLike}
                  disabled={isLiking}
                  aria-pressed={article.liked}
                  aria-label={
                    article.liked
                      ? 'Unlike this article'
                      : 'Like this article'
                  }
                  className={`flex min-w-0 flex-col items-center justify-center gap-1.5 px-1 py-4 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60 dark:hover:bg-gray-800/60 sm:flex-row sm:gap-2 sm:px-3 ${
                    article.liked
                      ? 'text-rose-600 dark:text-rose-400'
                      : 'text-light-muted dark:text-dark-muted'
                  }`}
                >
                  <Heart
                    size={20}
                    className={article.liked ? 'fill-current' : ''}
                  />

                  <span className="text-xs font-semibold sm:text-sm">
                    {formatCount(article.likes_count)}
                    <span className="hidden sm:inline"> Likes</span>
                  </span>
                </button>

                {/* Comments */}
                <button
                  type="button"
                  onClick={handleComments}
                  aria-label={`${formatCount(article.comments_count)} comments`}
                  className="flex min-w-0 flex-col items-center justify-center gap-1.5 px-1 py-4 text-light-muted transition hover:bg-gray-50 hover:text-brand-teal dark:text-dark-muted dark:hover:bg-gray-800/60 dark:hover:text-brand-teal-light sm:flex-row sm:gap-2 sm:px-3"
                >
                  <MessageCircle size={20} />

                  <span className="text-xs font-semibold sm:text-sm">
                    {formatCount(article.comments_count)}
                    <span className="hidden sm:inline"> Comments</span>
                  </span>
                </button>

                {/* Favorite */}
                <button
                  type="button"
                  onClick={handleFavorite}
                  disabled={isFavoriting}
                  aria-pressed={article.favorited}
                  aria-label={
                    article.favorited
                      ? 'Remove article from favorites'
                      : 'Add article to favorites'
                  }
                  className={`flex min-w-0 flex-col items-center justify-center gap-1.5 px-1 py-4 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60 dark:hover:bg-gray-800/60 sm:flex-row sm:gap-2 sm:px-3 ${
                    article.favorited
                      ? 'text-brand-teal dark:text-brand-teal-light'
                      : 'text-light-muted dark:text-dark-muted'
                  }`}
                >
                  <Bookmark
                    size={20}
                    className={article.favorited ? 'fill-current' : ''}
                  />

                  <span className="text-xs font-semibold sm:text-sm">
                    {formatCount(article.favorites_count)}
                    <span className="hidden sm:inline"> Favorites</span>
                    <span className="sm:hidden"> Save</span>
                  </span>
                </button>

                {/* Copy link */}
                <button
                  type="button"
                  onClick={handleCopyLink}
                  aria-label="Copy article link"
                  className="flex min-w-0 flex-col items-center justify-center gap-1.5 px-1 py-4 text-light-muted transition hover:bg-gray-50 hover:text-brand-teal dark:text-dark-muted dark:hover:bg-gray-800/60 dark:hover:text-brand-teal-light sm:flex-row sm:gap-2 sm:px-3"
                >
                  {isCopied ? (
                    <Check size={20} />
                  ) : (
                    <Copy size={20} />
                  )}

                  <span className="text-xs font-semibold sm:text-sm">
                    {isCopied ? 'Copied' : 'Copy link'}
                  </span>
                </button>
              </div>

              {(likeError || favoriteError || actionNotice) && (
                <div
                  role={
                    likeError || favoriteError ? 'alert' : 'status'
                  }
                  className={`border-t border-light-border px-4 py-3 text-sm dark:border-dark-border ${
                    likeError || favoriteError
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-light-muted dark:text-dark-muted'
                  }`}
                >
                  {likeError || favoriteError || actionNotice}
                </div>
              )}
            </section>

            {/* Editorial article comments */}
            <div
              id="comments"
              ref={commentsAnchorRef}
              className="scroll-mt-24"
            >
              <EditorialArticleComments
                articleId={article.id}
                initialCommentsCount={article.comments_count}
              />
            </div>
          </div>
        </div>
      </article>
    </main>
  );
}