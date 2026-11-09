import Image from 'next/image';
import Link from 'next/link';
import { CalendarDays, Heart, Star } from 'lucide-react';

import { getMediaUrl } from '@/lib/api';
import type { MusicDiscoveryAlbum } from '@/lib/music/MusicDiscovery';

type DiscoveryAlbumCardProps = {
  album: MusicDiscoveryAlbum;
  rank?: number;
};

const compactNumberFormatter = new Intl.NumberFormat('en-NG', {
  notation: 'compact',
  maximumFractionDigits: 1,
});

function formatCount(value: number): string {
  return value >= 10000
    ? compactNumberFormatter.format(value)
    : value.toLocaleString('en-NG');
}

function formatReleaseDate(value: string | null): string | null {
  if (!value) {
    return null;
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat('en-NG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

function formatReleaseType(value: string): string {
  if (!value.trim()) {
    return 'Release';
  }

  return value
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export default function DiscoveryAlbumCard({
  album,
  rank,
}: DiscoveryAlbumCardProps) {
  const artists = album.artists.filter(
    (artist, index, allArtists) =>
      allArtists.findIndex(
        (item) => item.id === artist.id,
      ) === index,
  );

  const releaseDate = formatReleaseDate(album.release_date);
  const artworkUrl = getMediaUrl(album.artwork);

  return (
    <Link
      href={`/music/albums/${encodeURIComponent(album.slug)}`}
      aria-label={`View ${album.title}`}
      className="
        group block min-w-0
        rounded-2xl p-2
        transition-transform duration-200 ease-out
        hover:-translate-y-1
        focus:outline-none
        focus-visible:ring-2
        focus-visible:ring-brand-teal
        focus-visible:ring-offset-2
        focus-visible:ring-offset-light-bg
        dark:focus-visible:ring-offset-dark-bg
      "
    >
      <article className="min-w-0">
        <div
          className="
            relative aspect-square w-full
            overflow-hidden rounded-2xl
            bg-light-surface-hover
            shadow-sm
            transition-shadow duration-200
            group-hover:shadow-lg
            dark:bg-dark-surface-hover
          "
        >
          {artworkUrl ? (
            <Image
              src={artworkUrl}
              alt={`${album.title} artwork`}
              fill
              sizes="
                (max-width: 640px) 45vw,
                (max-width: 1024px) 30vw,
                (max-width: 1280px) 25vw,
                240px
              "
              className="
                object-cover
                transition-transform duration-300
                ease-out
                group-hover:scale-[1.04]
              "
            />
          ) : (
            <div
              className="
                flex h-full w-full
                items-center justify-center
                bg-brand-teal/10
                text-5xl font-bold
                text-brand-teal
                dark:bg-brand-teal/15
                dark:text-brand-teal-light
              "
              aria-label="Artwork unavailable"
            >
              ♫
            </div>
          )}

          <div
            className="
              pointer-events-none absolute inset-0
              bg-gradient-to-t
              from-black/25 via-transparent to-black/10
              opacity-70
              transition-opacity duration-200
              group-hover:opacity-100
            "
            aria-hidden="true"
          />

          {typeof rank === 'number' && rank > 0 && (
            <span
              className="
                absolute left-2.5 top-2.5
                flex h-7 min-w-7
                items-center justify-center
                rounded-full
                bg-black/65 px-2
                text-xs font-bold text-white
                shadow-sm backdrop-blur-sm
              "
              aria-label={`Rank ${rank}`}
            >
              {rank}
            </span>
          )}

          <span
            className="
              absolute bottom-2.5 left-2.5
              max-w-[calc(100%-1.25rem)]
              truncate rounded-lg
              bg-black/65 px-2.5 py-1.5
              text-[10px] font-semibold uppercase
              tracking-wider text-white
              backdrop-blur-sm
            "
          >
            {formatReleaseType(album.release_type)}
          </span>
        </div>

        <div className="min-w-0 px-1 pt-3">
          <h3
            className="
              line-clamp-2 break-words
              text-sm font-bold leading-snug
              text-light-text
              transition-colors duration-200
              group-hover:text-brand-teal
              dark:text-dark-text
              dark:group-hover:text-brand-teal-light
              sm:text-base
            "
            title={album.title}
          >
            {album.title}
          </h3>

          <p
            className="
              mt-1.5 line-clamp-1 break-words
              text-xs leading-relaxed
              text-light-text-muted
              dark:text-dark-text-muted
              sm:text-sm
            "
            title={
              artists.length > 0
                ? artists.map((artist) => artist.name).join(', ')
                : 'Unknown artist'
            }
          >
            {artists.length > 0
              ? artists.map((artist) => artist.name).join(', ')
              : 'Unknown artist'}
          </p>

          <div
            className="
              mt-3 flex min-w-0 flex-wrap
              items-center gap-x-3 gap-y-2
              text-xs
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            <span
              className="inline-flex items-center gap-1.5"
              title={`${album.favorites_count.toLocaleString('en-NG')} favorites`}
            >
              <Heart
                className="h-3.5 w-3.5 shrink-0"
                aria-hidden="true"
              />
              <span>{formatCount(album.favorites_count)}</span>
            </span>

            {album.average_rating !== null && (
              <span
                className="inline-flex items-center gap-1.5"
                title={`Average rating: ${album.average_rating}`}
              >
                <Star
                  className="h-3.5 w-3.5 shrink-0"
                  aria-hidden="true"
                />
                <span>
                  {Number(album.average_rating).toFixed(1)}
                </span>
                {album.ratings_count > 0 && (
                  <span>
                    ({formatCount(album.ratings_count)})
                  </span>
                )}
              </span>
            )}

            {releaseDate && (
              <span
                className="inline-flex items-center gap-1.5"
                title={`Released ${releaseDate}`}
              >
                <CalendarDays
                  className="h-3.5 w-3.5 shrink-0"
                  aria-hidden="true"
                />
                <span>{releaseDate}</span>
              </span>
            )}
          </div>
        </div>
      </article>
    </Link>
  );
}