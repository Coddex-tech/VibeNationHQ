import Image from 'next/image';
import Link from 'next/link';
import {
  Disc3,
  Music2,
} from 'lucide-react';

import type {
  CommunityAlbum,
  CommunitySong,
} from '@/lib/music/CommunityPosts';

type MusicDiscoveryItemProps =
  | {
      type: 'song';
      item: CommunitySong;
    }
  | {
      type: 'album';
      item: CommunityAlbum;
    };

export default function MusicDiscoveryItem({
  type,
  item,
}: MusicDiscoveryItemProps) {
  const isSong = type === 'song';

  const title = item.title;

  const href = isSong
    ? `/music/songs/${item.slug}`
    : `/music/albums/${item.slug}`;

  const artists = item.artists;

  return (
    <article
      className="
        border-b
        border-light-border-soft
        px-4 py-5
        dark:border-dark-border-soft
        sm:px-6 sm:py-6
      "
    >
      <div className="flex items-center gap-3">
        {/* Artwork */}
        <Link
          href={href}
          aria-label={`View ${title}`}
          className="
            relative h-14 w-14
            shrink-0
            overflow-hidden
            rounded-xl
            bg-light-surface-soft
            transition-transform duration-200
            hover:scale-[1.02]
            focus:outline-none
            focus-visible:ring-4
            focus-visible:ring-brand-teal/15
            dark:bg-dark-surface-soft
          "
        >
          {item.artwork ? (
            <Image
              src={item.artwork}
              alt=""
              fill
              sizes="56px"
              className="object-cover"
            />
          ) : (
            <div
              className="
                flex h-full w-full
                items-center justify-center
                text-light-text-soft
                dark:text-dark-text-soft
              "
            >
              {isSong ? (
                <Music2 className="h-5 w-5" />
              ) : (
                <Disc3 className="h-5 w-5" />
              )}
            </div>
          )}
        </Link>

        {/* Metadata */}
        <div className="min-w-0 flex-1">
          <div
            className="
              flex items-center gap-2
            "
          >
            <span
              className="
                inline-flex shrink-0
                items-center gap-1
                text-[10px]
                font-bold uppercase
                tracking-wide
                text-brand-teal-dark
                dark:text-brand-teal-light
              "
            >
              {isSong ? (
                <Music2 className="h-3.5 w-3.5" />
              ) : (
                <Disc3 className="h-3.5 w-3.5" />
              )}

              {isSong ? 'Song' : 'Album'}
            </span>
          </div>

          <Link
            href={href}
            className="
              mt-1 block truncate
              text-sm font-bold
              text-light-text
              transition-colors
              hover:text-brand-teal-dark
              focus:outline-none
              focus-visible:underline
              dark:text-dark-text
              dark:hover:text-brand-teal-light
            "
          >
            {title}
          </Link>

          <div
            className="
              mt-0.5 flex min-w-0
              items-center gap-1
              text-xs
              text-light-text-muted
              dark:text-dark-text-muted
            "
          >
            {artists.length > 0 ? (
              <div className="min-w-0 truncate">
                {artists.map((artist, index) => (
                  <span key={artist.id}>
                    {index > 0 && ', '}

                    <Link
                      href={`/music/artists/${artist.slug}`}
                      className="
                        hover:text-brand-teal-dark
                        hover:underline
                        dark:hover:text-brand-teal-light
                      "
                    >
                      {artist.name}
                    </Link>
                  </span>
                ))}
              </div>
            ) : (
              <span>Unknown artist</span>
            )}
          </div>
        </div>

        {/* Secondary metadata */}
        <div
          className="
            hidden shrink-0
            text-right
            sm:block
          "
        >
          {isSong ? (
            <SongMetadata item={item} />
          ) : (
            <AlbumMetadata item={item} />
          )}
        </div>
      </div>
    </article>
  );
}

function SongMetadata({
  item,
}: {
  item: CommunitySong;
}) {
  return (
    <div className="space-y-1">
      {item.duration_display && (
        <p
          className="
            text-xs font-medium
            text-light-text-muted
            dark:text-dark-text-muted
          "
        >
          {item.duration_display}
        </p>
      )}

      <p
        className="
          text-[11px]
          text-light-text-soft
          dark:text-dark-text-soft
        "
      >
        {formatCount(item.favorites_count)}
        {' · '}
        {formatCount(item.ratings_count)}
      </p>
    </div>
  );
}

function AlbumMetadata({
  item,
}: {
  item: CommunityAlbum;
}) {
  return (
    <div className="space-y-1">
      <p
        className="
          text-xs font-medium
          text-light-text-muted
          dark:text-dark-text-muted
        "
      >
        {formatReleaseType(item.release_type)}
      </p>

      <p
        className="
          text-[11px]
          text-light-text-soft
          dark:text-dark-text-soft
        "
      >
        {formatCount(item.favorites_count)}
        {' · '}
        {formatCount(item.ratings_count)}
      </p>
    </div>
  );
}

function formatReleaseType(
  value: string,
): string {
  if (!value) {
    return 'Album';
  }

  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}

function formatCount(value: number): string {
  if (value < 1_000) {
    return String(value);
  }

  if (value < 1_000_000) {
    return `${(value / 1_000).toFixed(
      value >= 10_000 ? 0 : 1,
    )}K`;
  }

  return `${(value / 1_000_000).toFixed(
    value >= 10_000_000 ? 0 : 1,
  )}M`;
}