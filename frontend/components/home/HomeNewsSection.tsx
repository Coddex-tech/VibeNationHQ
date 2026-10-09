'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  ArrowRightIcon,
  NewsIcon,
} from '@/components/Icons';
import {
  getNewsHome,
  type NewsCard,
  type NewsHomeResponse,
} from '@/lib/news/NewsHome';

function NewsImage({
  src,
  alt,
  className = '',
}: {
  src: string | null;
  alt: string;
  className?: string;
}) {
  if (!src) {
    return (
      <div
        aria-hidden="true"
        className={`
          flex h-full w-full items-center justify-center
          bg-brand-teal/10
          text-brand-teal
          ${className}
        `}
      >
        <NewsIcon className="h-7 w-7" />
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      fill
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      className={`
        object-cover
        ${className}
      `}
    />
  );
}

function NewsCardItem({
  article,
}: {
  article: NewsCard;
}) {
  return (
    <Link
      href={`/news/${article.slug}`}
      className="
        group
        flex gap-4
        rounded-xl
        border border-light-border
        bg-light-bg
        p-3
        transition-all duration-200
        hover:border-brand-teal/35
        hover:shadow-md hover:shadow-black/[0.03]
        dark:border-dark-border
        dark:bg-dark-bg
        dark:hover:border-brand-teal/35
        dark:hover:shadow-black/20
      "
    >
      <div
        className="
          relative
          h-20 w-24 shrink-0
          overflow-hidden rounded-lg
          bg-light-surface-soft
          dark:bg-dark-surface-soft
        "
      >
        <NewsImage
          src={article.thumbnail_url}
          alt=""
        />
      </div>

      <div className="min-w-0 flex-1 py-0.5">
        <p
          className="
            line-clamp-2
            text-sm font-bold leading-5
            text-light-text
            transition-colors
            group-hover:text-brand-teal-dark
            dark:text-dark-text
            dark:group-hover:text-brand-teal-light
          "
        >
          {article.title}
        </p>

        <p
          className="
            mt-2 text-xs
            text-light-text-soft
            dark:text-dark-text-soft
          "
        >
          {article.friendly_date}
        </p>
      </div>

      <ArrowRightIcon
        className="
          mt-1 h-4 w-4 shrink-0
          text-light-text-soft
          transition-transform
          group-hover:translate-x-0.5
          dark:text-dark-text-soft
        "
      />
    </Link>
  );
}

function LoadingCard({
  large = false,
}: {
  large?: boolean;
}) {
  return (
    <div
      className={`
        animate-pulse overflow-hidden rounded-2xl
        border border-light-border
        bg-light-bg
        dark:border-dark-border
        dark:bg-dark-bg
        ${large ? 'min-h-[330px]' : 'min-h-[100px]'}
      `}
    >
      {large ? (
        <>
          <div
            className="
              h-48
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />

          <div className="p-5">
            <div
              className="
                h-4 w-24 rounded
                bg-light-border
                dark:bg-dark-border
              "
            />

            <div
              className="
                mt-3 h-5 w-4/5 rounded
                bg-light-border
                dark:bg-dark-border
              "
            />

            <div
              className="
                mt-2 h-5 w-3/5 rounded
                bg-light-border-soft
                dark:bg-dark-border-soft
              "
            />

            <div
              className="
                mt-4 h-3 w-28 rounded
                bg-light-border-soft
                dark:bg-dark-border-soft
              "
            />
          </div>
        </>
      ) : (
        <div className="flex gap-4 p-3">
          <div
            className="
              h-20 w-24 shrink-0 rounded-lg
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />

          <div className="flex-1 py-1">
            <div
              className="
                h-3.5 w-4/5 rounded
                bg-light-border
                dark:bg-dark-border
              "
            />

            <div
              className="
                mt-2 h-3.5 w-3/5 rounded
                bg-light-border-soft
                dark:bg-dark-border-soft
              "
            />

            <div
              className="
                mt-4 h-2.5 w-20 rounded
                bg-light-border-soft
                dark:bg-dark-border-soft
              "
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default function HomeNewsSection() {
  const [newsHome, setNewsHome] =
    useState<NewsHomeResponse | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState('');

  useEffect(() => {
    let isMounted = true;

    const loadNewsHome = async () => {
      setIsLoading(true);
      setError('');

      try {
        const data = await getNewsHome();

        if (!isMounted) {
          return;
        }

        setNewsHome(data);
      } catch {
        if (!isMounted) {
          return;
        }

        setError(
          'Unable to load the latest news right now.',
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadNewsHome();

    return () => {
      isMounted = false;
    };
  }, []);

  const featured =
    newsHome?.hero_blocks.global_featured ?? null;

  const topNews =
    newsHome?.hero_blocks.top_news ?? [];

  const latestNews =
    newsHome?.hero_blocks.latest_news ?? [];

  const hasNews =
    featured !== null ||
    topNews.length > 0 ||
    latestNews.length > 0;

  return (
    <section
      aria-labelledby="home-news-heading"
      className="
        border-b border-light-border
        bg-light-surface
        dark:border-dark-border
        dark:bg-dark-surface
      "
    >
      <div
        className="
          mx-auto w-full max-w-7xl
          px-5 py-14
          sm:px-6 sm:py-16
          lg:px-8 lg:py-20
        "
      >
        {/* Heading */}
        <FadeIn>
          <div
            className="
              flex flex-col gap-5
              sm:flex-row sm:items-end sm:justify-between
            "
          >
            <div className="max-w-2xl">
              <div
                className="
                  mb-3 inline-flex items-center gap-2
                  text-xs font-bold uppercase tracking-wider
                  text-brand-teal-dark
                  dark:text-brand-teal-light
                "
              >
                <NewsIcon className="h-4 w-4" />
                VibeNation News
              </div>

              <h2
                id="home-news-heading"
                className="
                  text-2xl font-black tracking-tight
                  text-light-text
                  dark:text-dark-text
                  sm:text-3xl
                "
              >
                Stories worth knowing.
              </h2>

              <p
                className="
                  mt-2 max-w-xl
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-base
                "
              >
                Stay connected to the latest conversations, people,
                culture, business and entertainment shaping the world
                around you.
              </p>
            </div>

            <Link
              href="/news"
              className="
                inline-flex shrink-0 items-center gap-2
                text-sm font-bold
                text-brand-teal-dark
                transition-colors
                hover:text-brand-teal
                dark:text-brand-teal-light
                dark:hover:text-brand-teal
              "
            >
              Explore all news
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
          </div>
        </FadeIn>

        {/* Loading */}
        {isLoading && (
          <FadeIn
            delay={0.08}
            className="mt-8"
          >
            <div
              className="
                grid gap-4
                lg:grid-cols-[1.35fr_0.65fr]
              "
            >
              <LoadingCard large />

              <div className="grid gap-4">
                <LoadingCard />
                <LoadingCard />
                <LoadingCard />
              </div>
            </div>
          </FadeIn>
        )}

        {/* Error */}
        {!isLoading && error && (
          <FadeIn
            delay={0.08}
            className="mt-8"
          >
            <div
              role="alert"
              className="
                rounded-2xl
                border border-red-200
                bg-red-50
                px-5 py-8
                text-center
                dark:border-red-500/20
                dark:bg-red-500/10
              "
            >
              <div
                className="
                  mx-auto flex h-11 w-11
                  items-center justify-center
                  rounded-xl
                  bg-red-500/10
                  text-red-600
                  dark:text-red-300
                "
              >
                <NewsIcon className="h-5 w-5" />
              </div>

              <h3
                className="
                  mt-4 text-base font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                News is temporarily unavailable
              </h3>

              <p
                className="
                  mx-auto mt-2 max-w-md
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                {error}
              </p>
            </div>
          </FadeIn>
        )}

        {/* Empty */}
        {!isLoading && !error && !hasNews && (
          <FadeIn
            delay={0.08}
            className="mt-8"
          >
            <div
              className="
                rounded-2xl
                border border-light-border
                bg-light-bg
                px-5 py-12
                text-center
                dark:border-dark-border
                dark:bg-dark-bg
              "
            >
              <div
                className="
                  mx-auto flex h-12 w-12
                  items-center justify-center
                  rounded-xl
                  bg-brand-teal/10
                  text-brand-teal
                "
              >
                <NewsIcon className="h-6 w-6" />
              </div>

              <h3
                className="
                  mt-4 text-base font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                No news yet
              </h3>

              <p
                className="
                  mx-auto mt-2 max-w-md
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                Check back soon for the latest stories from
                VibeNationHQ.
              </p>
            </div>
          </FadeIn>
        )}

        {/* Real news */}
        {!isLoading && !error && hasNews && (
          <>
            {/* Featured + top news */}
            <FadeIn
              delay={0.08}
              className="mt-8"
            >
              <div
                className="
                  grid gap-4
                  lg:grid-cols-[1.35fr_0.65fr]
                "
              >
                {/* Featured */}
                {featured ? (
                  <Link
                    href={`/news/${featured.slug}`}
                    className="
                      group relative
                      min-h-[330px]
                      overflow-hidden rounded-2xl
                      border border-light-border
                      bg-light-bg
                      transition-all duration-200
                      hover:border-brand-teal/35
                      hover:shadow-lg hover:shadow-black/[0.04]
                      dark:border-dark-border
                      dark:bg-dark-bg
                      dark:hover:border-brand-teal/35
                      dark:hover:shadow-black/20
                    "
                  >
                    <div className="absolute inset-0">
                      <NewsImage
                        src={featured.thumbnail}
                        alt={featured.title}
                      />
                    </div>

                    <div
                      aria-hidden="true"
                      className="
                        absolute inset-0
                        bg-gradient-to-t
                        from-black/85
                        via-black/35
                        to-black/5
                      "
                    />

                    <div
                      className="
                        relative flex min-h-[330px]
                        flex-col justify-end
                        p-5 sm:p-7
                      "
                    >
                      <span
                        className="
                          mb-3 inline-flex w-fit
                          rounded-full
                          border border-white/20
                          bg-white/10
                          px-3 py-1.5
                          text-[11px] font-bold
                          uppercase tracking-wider
                          text-white
                          backdrop-blur-sm
                        "
                      >
                        Featured story
                      </span>

                      <h3
                        className="
                          max-w-2xl
                          text-xl font-black
                          leading-tight
                          text-white
                          sm:text-2xl
                        "
                      >
                        {featured.title}
                      </h3>

                      <div
                        className="
                          mt-4 inline-flex
                          items-center gap-2
                          text-sm font-bold
                          text-white/85
                          transition-colors
                          group-hover:text-white
                        "
                      >
                        Read the story
                        <ArrowRightIcon
                          className="
                            h-4 w-4
                            transition-transform
                            group-hover:translate-x-0.5
                          "
                        />
                      </div>
                    </div>
                  </Link>
                ) : (
                  <div
                    className="
                      rounded-2xl
                      border border-light-border
                      bg-light-bg
                      px-5 py-12
                      text-center
                      dark:border-dark-border
                      dark:bg-dark-bg
                    "
                  >
                    <NewsIcon
                      className="
                        mx-auto h-7 w-7
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    />

                    <p
                      className="
                        mt-3 text-sm font-semibold
                        text-light-text-muted
                        dark:text-dark-text-muted
                      "
                    >
                      No featured story right now.
                    </p>
                  </div>
                )}

                {/* Top news */}
                <div className="grid gap-4">
                  {topNews
                    .slice(0, 3)
                    .map((article) => (
                      <NewsCardItem
                        key={article.id}
                        article={article}
                      />
                    ))}

                  {topNews.length === 0 && (
                    <div
                      className="
                        flex min-h-[155px]
                        items-center justify-center
                        rounded-2xl
                        border border-light-border
                        bg-light-bg
                        px-5 text-center
                        dark:border-dark-border
                        dark:bg-dark-bg
                      "
                    >
                      <p
                        className="
                          text-sm
                          text-light-text-muted
                          dark:text-dark-text-muted
                        "
                      >
                        No top stories available yet.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </FadeIn>

            {/* Latest */}
            {latestNews.length > 0 && (
              <FadeIn
                delay={0.14}
                className="mt-8"
              >
                <div
                  className="
                    flex flex-col gap-5
                    sm:flex-row sm:items-end
                    sm:justify-between
                  "
                >
                  <div>
                    <p
                      className="
                        text-xs font-bold uppercase
                        tracking-wider
                        text-brand-teal-dark
                        dark:text-brand-teal-light
                      "
                    >
                      Latest
                    </p>

                    <h3
                      className="
                        mt-1 text-xl font-black
                        tracking-tight
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Fresh from the newsroom.
                    </h3>
                  </div>

                  <Link
                    href="/news"
                    className="
                      inline-flex items-center gap-2
                      text-sm font-bold
                      text-brand-teal-dark
                      hover:text-brand-teal
                      dark:text-brand-teal-light
                    "
                  >
                    See all stories
                    <ArrowRightIcon className="h-4 w-4" />
                  </Link>
                </div>

                <div
                  className="
                    mt-5 grid gap-4
                    sm:grid-cols-2
                    lg:grid-cols-4
                  "
                >
                  {latestNews
                    .slice(0, 4)
                    .map((article) => (
                      <Link
                        key={article.id}
                        href={`/news/${article.slug}`}
                        className="
                          group overflow-hidden
                          rounded-2xl
                          border border-light-border
                          bg-light-bg
                          transition-all duration-200
                          hover:-translate-y-0.5
                          hover:border-brand-teal/35
                          hover:shadow-md
                          hover:shadow-black/[0.03]
                          dark:border-dark-border
                          dark:bg-dark-bg
                          dark:hover:border-brand-teal/35
                          dark:hover:shadow-black/20
                        "
                      >
                        <div
                          className="
                            relative
                            aspect-[16/10]
                            overflow-hidden
                            bg-light-surface-soft
                            dark:bg-dark-surface-soft
                          "
                        >
                          <NewsImage
                            src={article.thumbnail_url}
                            alt={article.title}
                            className="
                              transition-transform
                              duration-300
                              group-hover:scale-[1.03]
                            "
                          />
                        </div>

                        <div className="p-4">
                          <h4
                            className="
                              line-clamp-3
                              text-sm font-bold leading-5
                              text-light-text
                              transition-colors
                              group-hover:text-brand-teal-dark
                              dark:text-dark-text
                              dark:group-hover:text-brand-teal-light
                            "
                          >
                            {article.title}
                          </h4>

                          <p
                            className="
                              mt-3 text-xs
                              text-light-text-soft
                              dark:text-dark-text-soft
                            "
                          >
                            {article.friendly_date}
                          </p>
                        </div>
                      </Link>
                    ))}
                </div>
              </FadeIn>
            )}

            {/* News categories */}
            <FadeIn
              delay={0.18}
              className="mt-6"
            >
              <div className="flex flex-wrap gap-2">
                {[
                  'Politics',
                  'Business',
                  'Music News',
                  'Celebrity Gossip',
                  'Technology',
                  'Lifestyle',
                ].map((category) => (
                  <Link
                    key={category}
                    href={`/news?category=${encodeURIComponent(category)}`}
                    className="
                      rounded-full
                      border border-light-border
                      bg-light-bg
                      px-3.5 py-2
                      text-xs font-semibold
                      text-light-text-muted
                      transition-colors
                      hover:border-brand-teal/35
                      hover:text-brand-teal-dark
                      dark:border-dark-border
                      dark:bg-dark-bg
                      dark:text-dark-text-muted
                      dark:hover:border-brand-teal/35
                      dark:hover:text-brand-teal-light
                    "
                  >
                    {category}
                  </Link>
                ))}
              </div>
            </FadeIn>
          </>
        )}
      </div>
    </section>
  );
}