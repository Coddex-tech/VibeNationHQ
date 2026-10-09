'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import {
  ArrowRightIcon,
  BookOpenIcon,
  CalendarIcon,
  HeartIcon,
  MessageCircleIcon,
  MusicIcon,
  UserIcon,
} from '@/components/Icons';
import {
  getEditorialArticles,
  type EditorialArticleCard,
} from '@/lib/music/EditorialArticles';

function formatPublishedDate(
  value: string | null,
) {
  if (!value) {
    return 'Recently published';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return 'Recently published';
  }

  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

function getArticleTarget(
  article: EditorialArticleCard,
) {
  if (article.song) {
    return {
      label: 'Song',
      title: article.song.title,
      subtitle: article.song.artists
        .map((artist) => artist.name)
        .join(', '),
      artwork: article.song.artwork,
    };
  }

  if (article.album) {
    return {
      label: 'Album',
      title: article.album.title,
      subtitle: article.album.artists
        .map((artist) => artist.name)
        .join(', '),
      artwork: article.album.artwork,
    };
  }

  if (article.artist) {
    return {
      label: 'Artist',
      title: article.artist.name,
      subtitle: 'Artist spotlight',
      artwork: article.artist.profile_image,
    };
  }

  return null;
}

function EditorialImage({
  src,
  alt,
}: {
  src: string | null;
  alt: string;
}) {
  if (!src) {
    return (
      <div
        className="
          flex h-full w-full
          items-center justify-center
          bg-light-surface-soft
          text-light-text-soft
          dark:bg-dark-surface-soft
          dark:text-dark-text-soft
        "
      >
        <BookOpenIcon className="h-7 w-7" />
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      fill
      sizes="
        (max-width: 639px) 100vw,
        (max-width: 1023px) 50vw,
        320px
      "
      className="object-cover"
    />
  );
}

function LoadingCard() {
  return (
    <article
      className="
        overflow-hidden rounded-2xl
        border border-light-border
        bg-light-surface
        dark:border-dark-border
        dark:bg-dark-surface
      "
    >
      <div
        className="
          aspect-[16/9]
          animate-pulse
          bg-light-surface-muted
          dark:bg-dark-surface-muted
        "
      />

      <div className="animate-pulse p-5">
        <div
          className="
            h-3 w-20 rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-3 h-5 w-full rounded
            bg-light-surface-muted
            dark:bg-dark-surface-muted
          "
        />

        <div
          className="
            mt-2 h-5 w-4/5 rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />

        <div
          className="
            mt-4 h-4 w-full rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />

        <div
          className="
            mt-2 h-4 w-3/4 rounded
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        />

        <div className="mt-5 flex gap-3">
          <div
            className="
              h-3 w-20 rounded
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />

          <div
            className="
              h-3 w-16 rounded
              bg-light-surface-soft
              dark:bg-dark-surface-soft
            "
          />
        </div>
      </div>
    </article>
  );
}

function EditorialCard({
  article,
}: {
  article: EditorialArticleCard;
}) {
  const target = getArticleTarget(article);

  return (
    <article
      className="
        group overflow-hidden
        rounded-2xl
        border border-light-border
        bg-light-surface
        shadow-sm shadow-black/[0.03]
        transition-all duration-200
        hover:-translate-y-0.5
        hover:shadow-md hover:shadow-black/[0.05]
        dark:border-dark-border
        dark:bg-dark-surface
        dark:shadow-black/10
      "
    >
      <Link
        href={`/music/editorial/${article.slug}`}
        className="block"
        aria-label={`Read ${article.title}`}
      >
        <div
          className="
            relative aspect-[16/9]
            overflow-hidden
            bg-light-surface-soft
            dark:bg-dark-surface-soft
          "
        >
          <EditorialImage
            src={target?.artwork ?? null}
            alt={
              target
                ? `${target.title} artwork`
                : article.title
            }
          />

          <div
            className="
              absolute inset-x-0 bottom-0
              h-20
              bg-gradient-to-t
              from-black/45
              to-transparent
            "
          />

          <div
            className="
              absolute left-4 top-4
              inline-flex items-center gap-1.5
              rounded-full
              bg-black/55
              px-2.5 py-1.5
              text-[11px] font-bold
              text-white
              backdrop-blur-sm
            "
          >
            <BookOpenIcon className="h-3.5 w-3.5" />
            Editorial
          </div>

          {article.is_featured && (
            <div
              className="
                absolute bottom-4 right-4
                inline-flex items-center gap-1.5
                rounded-full
                bg-brand-teal
                px-2.5 py-1.5
                text-[11px] font-bold
                text-white
                shadow-sm
              "
            >
              Featured
            </div>
          )}
        </div>
      </Link>

      <div className="p-5">
        {target && (
          <div
            className="
              mb-3 flex min-w-0
              items-center gap-2
              text-xs
            "
          >
            <MusicIcon
              className="
                h-3.5 w-3.5 shrink-0
                text-brand-teal
              "
            />

            <span
              className="
                shrink-0 font-bold
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              {target.label}
            </span>

            <span
              className="
                truncate
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {target.title}
            </span>
          </div>
        )}

        <Link
          href={`/music/editorial/${article.slug}`}
          className="
            block
            text-lg font-black leading-snug
            tracking-tight
            text-light-text
            transition-colors
            group-hover:text-brand-teal-dark
            dark:text-dark-text
            dark:group-hover:text-brand-teal-light
          "
        >
          {article.title}
        </Link>

        {article.excerpt && (
          <p
            className="
              mt-3 line-clamp-3
              text-sm leading-6
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            {article.excerpt}
          </p>
        )}

        <div
          className="
            mt-5 flex flex-wrap
            items-center gap-x-4 gap-y-2
            text-xs
            text-light-text-soft
            dark:text-dark-text-soft
          "
        >
          <span className="inline-flex items-center gap-1.5">
            <UserIcon className="h-3.5 w-3.5" />
            {article.author.name}
          </span>

          <span className="inline-flex items-center gap-1.5">
            <CalendarIcon className="h-3.5 w-3.5" />
            {formatPublishedDate(
              article.published_at,
            )}
          </span>
        </div>

        <div
          className="
            mt-4 flex flex-wrap
            items-center gap-4
            border-t border-light-border-soft
            pt-4
            text-xs font-semibold
            text-light-text-soft
            dark:border-dark-border-soft
            dark:text-dark-text-soft
          "
        >
          <span className="inline-flex items-center gap-1.5">
            <HeartIcon className="h-3.5 w-3.5" />
            {article.likes_count}
          </span>

          <span className="inline-flex items-center gap-1.5">
            <MessageCircleIcon className="h-3.5 w-3.5" />
            {article.comments_count}
          </span>

          <span className="ml-auto">
            {article.views_count} views
          </span>
        </div>
      </div>
    </article>
  );
}

export default function HomeEditorialSection() {
  const [articles, setArticles] = useState<
    EditorialArticleCard[]
  >([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    async function loadEditorialArticles() {
      setIsLoading(true);
      setError('');

      try {
        const data =
          await getEditorialArticles({
            pageSize: 3,
          });

        if (!isMounted) {
          return;
        }

        setArticles(data.results);
      } catch {
        if (!isMounted) {
          return;
        }

        setError(
          'Unable to load editorial articles right now.',
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadEditorialArticles();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section
      aria-labelledby="home-editorial-heading"
      className="
        border-b border-light-border
        bg-light-surface-soft
        dark:border-dark-border
        dark:bg-dark-surface-soft
      "
    >
      <div
        className="
          mx-auto w-full max-w-7xl
          px-4 py-12
          sm:px-6 sm:py-14
          lg:px-8 lg:py-16
        "
      >
        <FadeIn>
          <div
            className="
              flex flex-col gap-5
              sm:flex-row sm:items-end
              sm:justify-between
            "
          >
            <div className="max-w-2xl">
              <p
                className="
                  text-sm font-bold
                  text-brand-teal-dark
                  dark:text-brand-teal-light
                "
              >
                VibeNationHQ Editorial
              </p>

              <h2
                id="home-editorial-heading"
                className="
                  mt-2
                  text-2xl font-black
                  tracking-tight
                  text-light-text
                  dark:text-dark-text
                  sm:text-3xl
                "
              >
                Stories, reviews and music insight.
              </h2>

              <p
                className="
                  mt-3 text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                  sm:text-base
                "
              >
                Explore deeper stories,
                conversations and perspectives
                around the music shaping the culture.
              </p>
            </div>

            <Link
              href="/music/editorial"
              className="
                inline-flex w-fit
                items-center gap-2
                text-sm font-bold
                text-brand-teal-dark
                transition-colors
                hover:text-brand-teal
                dark:text-brand-teal-light
              "
            >
              Explore editorial
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
          </div>
        </FadeIn>

        {isLoading ? (
          <div
            className="
              mt-8 grid gap-5
              sm:grid-cols-2
              lg:grid-cols-3
            "
          >
            <LoadingCard />
            <LoadingCard />
            <LoadingCard />
          </div>
        ) : error ? (
          <FadeIn className="mt-8">
            <div
              role="alert"
              className="
                rounded-2xl
                border border-red-200
                bg-red-50
                px-5 py-6
                text-sm leading-6
                text-red-700
                dark:border-red-500/20
                dark:bg-red-500/10
                dark:text-red-300
              "
            >
              {error}
            </div>
          </FadeIn>
        ) : articles.length === 0 ? (
          <FadeIn className="mt-8">
            <div
              className="
                rounded-2xl
                border border-light-border
                bg-light-surface
                px-5 py-10
                text-center
                dark:border-dark-border
                dark:bg-dark-surface
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
                <BookOpenIcon className="h-6 w-6" />
              </div>

              <h3
                className="
                  mt-4 text-base font-bold
                  text-light-text
                  dark:text-dark-text
                "
              >
                Editorial stories are coming soon.
              </h3>

              <p
                className="
                  mx-auto mt-2 max-w-md
                  text-sm leading-6
                  text-light-text-muted
                  dark:text-dark-text-muted
                "
              >
                We are preparing stories,
                reviews and deeper music coverage
                for VibeNationHQ.
              </p>
            </div>
          </FadeIn>
        ) : (
          <div
            className="
              mt-8 grid gap-5
              sm:grid-cols-2
              lg:grid-cols-3
            "
          >
            {articles.map((article) => (
              <FadeIn key={article.id}>
                <EditorialCard
                  article={article}
                />
              </FadeIn>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}