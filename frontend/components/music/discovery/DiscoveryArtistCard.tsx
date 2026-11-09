 'use client';

import Image from 'next/image';
import { BadgeCheck, Users } from 'lucide-react';

import { getMediaUrl } from '@/lib/api';
import type { MusicDiscoveryArtist } from '@/lib/music/MusicDiscovery';

type DiscoveryArtistCardProps = {
  artist: MusicDiscoveryArtist;
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

export default function DiscoveryArtistCard({
  artist,
  rank,
}: DiscoveryArtistCardProps) {
  const profileImageUrl = getMediaUrl(artist.profile_image);

  return (
    <article
      className="
        group relative flex min-w-0
        items-center gap-4
        rounded-2xl p-3
        transition-all duration-200 ease-out
        hover:-translate-y-0.5
        hover:bg-light-surface-hover
        dark:hover:bg-dark-surface-hover
      "
    >
      <div className="relative h-[4.5rem] w-[4.5rem] shrink-0">
        {profileImageUrl ? (
          <Image
            src={profileImageUrl}
            alt={`${artist.name} profile`}
            fill
            sizes="72px"
            className="
              rounded-full object-cover
              ring-2 ring-transparent
              transition-all duration-200
              group-hover:ring-brand-teal/40
              group-hover:ring-offset-2
              group-hover:ring-offset-light-bg
              dark:group-hover:ring-offset-dark-bg
            "
          />
        ) : (
          <div
            className="
              flex h-full w-full
              items-center justify-center
              rounded-full
              bg-brand-teal/10
              text-2xl font-bold
              text-brand-teal
              transition-colors duration-200
              group-hover:bg-brand-teal/15
              dark:bg-brand-teal/15
              dark:text-brand-teal-light
            "
            aria-label="Artist image unavailable"
          >
            {artist.name.trim().charAt(0).toUpperCase() || '?'}
          </div>
        )}

        {typeof rank === 'number' && rank > 0 && (
          <span
            className="
              absolute -left-1 -top-1
              flex h-6 min-w-6
              items-center justify-center
              rounded-full
              bg-black/75 px-1.5
              text-[10px] font-bold text-white
              shadow-sm backdrop-blur-sm
            "
            aria-label={`Rank ${rank}`}
          >
            {rank}
          </span>
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex min-w-0 items-center gap-1.5">
          <h3
            className="
              truncate text-sm font-bold
              text-light-text
              transition-colors duration-200
              group-hover:text-brand-teal
              dark:text-dark-text
              dark:group-hover:text-brand-teal-light
              sm:text-base
            "
            title={artist.name}
          >
            {artist.name}
          </h3>

          {artist.is_verified && (
            <BadgeCheck
              className="
                h-4 w-4 shrink-0
                text-brand-teal
                dark:text-brand-teal-light
              "
              aria-label="Verified artist"
              title="Verified artist"
            />
          )}
        </div>

        <p
          className="
            mt-1.5 flex items-center gap-1.5
            text-xs
            text-light-text-muted
            dark:text-dark-text-muted
            sm:text-sm
          "
        >
          <Users
            className="h-3.5 w-3.5 shrink-0"
            aria-hidden="true"
          />
          <span>
            {formatCount(artist.followers_count)} followers
          </span>
        </p>

        {artist.is_verified && (
          <span
            className="
              mt-2 inline-flex items-center
              rounded-full bg-brand-teal/10
              px-2 py-0.5
              text-[10px] font-semibold
              text-brand-teal
              dark:bg-brand-teal/15
              dark:text-brand-teal-light
            "
          >
            Verified artist
          </span>
        )}
      </div>
    </article>
  );
}