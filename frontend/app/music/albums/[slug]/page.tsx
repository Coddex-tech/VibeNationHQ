import type { Metadata } from 'next';

import Image from 'next/image';
import Link from 'next/link';
import {
    notFound,
    permanentRedirect,
} from 'next/navigation';

import MusicNavigation from '@/components/music/MusicNavigation';
import TargetCommunityPosts from '@/components/music/TargetCommunityPosts';
import { getMediaUrl } from '@/lib/api';

import { ArrowLeft } from 'lucide-react';

type AlbumArtist = {
    id: number;
    name: string;
    slug: string;
    profile_image: string | null;
    is_verified: boolean;
    followers_count: number;
};

type AlbumTrackSong = {
    id: number;
    title: string;
    slug: string;
    artists: AlbumArtist[];
    featured_artists: AlbumArtist[];
    artwork: string | null;
    release_date: string | null;
    duration_seconds: number | null;
    duration_display: string | null;
    favorites_count: number;
    ratings_count: number;
    preview_url: string | null;
};

type AlbumTrack = {
    id: number;
    track_number: number;
    song: AlbumTrackSong;
};

type AlbumDetail = {
    id: number;
    title: string;
    slug: string;
    artists: AlbumArtist[];
    release_type: string;
    artwork: string | null;
    release_date: string | null;
    description: string | null;
    editorial_review: string | null;
    editorial_score: number | null;
    spotify_url: string | null;
    apple_music_url: string | null;
    youtube_url: string | null;
    audiomack_url: string | null;
    boomplay_url: string | null;
    published_at: string | null;
    is_featured: boolean;
    favorites_count: number;
    ratings_count: number;
    tracks: AlbumTrack[];
    community_rating_average: number | null;
    community_rating_count: number;
    track_community_rating_average: number | null;
    track_community_rating_count: number;
};

type AlbumPageProps = {
    params: Promise<{
        slug: string;
    }>;
};

const API_URL =
    process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

const SITE_URL =
    process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000';

const BRAND_TEAL = '#008080';

function cleanText(value: string | null | undefined): string {
    return value?.replace(/\s+/g, ' ').trim() ?? '';
}

function getArtistNames(artists: AlbumArtist[]): string {
    return artists.map((artist) => artist.name).join(', ');
}

function getAlbumTitle(album: AlbumDetail): string {
    const artistNames = getArtistNames(album.artists);

    return artistNames
        ? `${album.title} by ${artistNames} | VibeNationHQ`
        : `${album.title} | VibeNationHQ`;
}

function getAlbumDescription(album: AlbumDetail): string {
    const description = cleanText(
        album.description || album.editorial_review,
    );

    if (description) {
        return description.length > 160
            ? `${description.slice(0, 157).trimEnd()}...`
            : description;
    }

    const artistNames = getArtistNames(album.artists);

    return artistNames
        ? `Explore ${album.title} by ${artistNames} on VibeNationHQ. Discover the tracklist and join the community discussion.`
        : `Explore ${album.title} on VibeNationHQ. Discover the tracklist and join the community discussion.`;
}

async function getAlbumBySlug(
    slug: string,
): Promise<AlbumDetail> {
    const response = await fetch(
        `${API_URL}/api/v1/music/albums/${encodeURIComponent(slug)}/`,
        {
            next: {
                revalidate: 60,
            },
        },
    );

    if (response.status === 404) {
        notFound();
    }

    if (!response.ok) {
        throw new Error(
            `Unable to load album details. The music API returned ${response.status}.`,
        );
    }

    return response.json() as Promise<AlbumDetail>;
}

export async function generateMetadata({
    params,
}: AlbumPageProps): Promise<Metadata> {
    const { slug } = await params;
    const album = await getAlbumBySlug(slug);

    const title = getAlbumTitle(album);
    const description = getAlbumDescription(album);
    const canonicalPath =
        `/music/albums/${encodeURIComponent(album.slug)}`;
    const artworkUrl = getMediaUrl(album.artwork);

    return {
        title,
        description,
        alternates: {
            canonical: canonicalPath,
        },
        openGraph: {
            type: 'music.album',
            title,
            description,
            url: new URL(canonicalPath, SITE_URL).toString(),
            siteName: 'VibeNationHQ',
            images: artworkUrl ? [artworkUrl] : [],
        },
        twitter: {
            card: artworkUrl ? 'summary_large_image' : 'summary',
            title,
            description,
            images: artworkUrl ? [artworkUrl] : [],
        },
    };
}

function formatReleaseDate(
    releaseDate: string | null,
): string | null {
    if (!releaseDate) return null;

    const date = new Date(releaseDate);

    if (Number.isNaN(date.getTime())) {
        return releaseDate;
    }

    return new Intl.DateTimeFormat('en', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    }).format(date);
}

function formatCount(value: number): string {
    return new Intl.NumberFormat('en').format(value);
}

function getTrackArtists(song: AlbumTrackSong): AlbumArtist[] {
    const artists = [...song.artists, ...song.featured_artists];

    return artists.filter(
        (artist, index) =>
            artists.findIndex(
                (candidate) => candidate.id === artist.id,
            ) === index,
    );
}

function getReleaseTypeLabel(releaseType: string): string {
    return releaseType.replace(/[_-]+/g, ' ').trim();
}

function RatingStars({
    average,
}: {
    average: number;
}) {
    const rating = Math.min(5, Math.max(0, average));

    return (
        <span
            className="inline-flex items-center gap-0.5"
            role="img"
            aria-label={`${rating.toFixed(1)} out of 5 stars`}
        >
            {Array.from({ length: 5 }, (_, index) => {
                const fillPercentage = Math.min(
                    100,
                    Math.max(0, (rating - index) * 100),
                );

                return (
                    <span
                        key={index}
                        className="relative inline-block text-base leading-none sm:text-lg"
                        aria-hidden="true"
                    >
                        <span className="text-light-border dark:text-dark-border">
                            ★
                        </span>

                        <span
                            className="absolute inset-y-0 left-0 overflow-hidden"
                            style={{
                                width: `${fillPercentage}%`,
                                color: BRAND_TEAL,
                            }}
                        >
                            ★
                        </span>
                    </span>
                );
            })}
        </span>
    );
}

function AlbumRatingStrip({
    album,
}: {
    album: AlbumDetail;
}) {
    const hasAlbumRatings =
        album.community_rating_average !== null &&
        album.community_rating_count > 0;

    const hasTrackRatings =
        album.track_community_rating_average !== null &&
        album.track_community_rating_count > 0;

    return (
        <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-3 border-y border-light-border py-3.5 dark:border-dark-border">
            <div className="min-w-0">
                <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.14em] text-light-muted dark:text-dark-muted">
                    Album rating
                </p>

                <div className="flex flex-wrap items-center gap-x-2 gap-y-1.5">
                    <RatingStars
                        average={
                            hasAlbumRatings
                                ? album.community_rating_average!
                                : 0
                        }
                    />

                    {hasAlbumRatings ? (
                        <>
                            <span className="text-sm font-bold tabular-nums text-light-text dark:text-dark-text">
                                {album.community_rating_average!.toFixed(1)}
                            </span>

                            <span className="text-xs text-light-muted dark:text-dark-muted">
                                ({formatCount(album.community_rating_count)})
                            </span>
                        </>
                    ) : (
                        <span className="text-xs text-light-muted dark:text-dark-muted">
                            No ratings yet
                        </span>
                    )}
                </div>
            </div>

            <span
                className="hidden h-9 w-px bg-light-border dark:bg-dark-border sm:block"
                aria-hidden="true"
            />

            <div className="min-w-0">
                <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.14em] text-light-muted dark:text-dark-muted">
                    Track ratings
                </p>

                <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                    {hasTrackRatings
                        ? album.track_community_rating_average!.toFixed(1)
                        : '—'}
                    <span className="ml-1 text-xs font-normal text-light-muted dark:text-dark-muted">
                        / 5 average
                    </span>
                </p>

                <p className="mt-0.5 text-[11px] text-light-muted dark:text-dark-muted">
                    {formatCount(album.track_community_rating_count)}{' '}
                    {album.track_community_rating_count === 1
                        ? 'track rating'
                        : 'track ratings'}
                </p>
            </div>
        </div>
    );
}

function ExternalMusicLinks({
    album,
}: {
    album: AlbumDetail;
}) {
    const links = [
        { label: 'Spotify', url: album.spotify_url },
        { label: 'Apple Music', url: album.apple_music_url },
        { label: 'YouTube', url: album.youtube_url },
        { label: 'Audiomack', url: album.audiomack_url },
        { label: 'Boomplay', url: album.boomplay_url },
    ].filter(
        (item): item is { label: string; url: string } =>
            Boolean(item.url),
    );

    if (links.length === 0) return null;

    return (
        <div className="flex flex-wrap gap-2">
            {links.map((item) => (
                <a
                    key={item.label}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
            inline-flex min-h-9 items-center justify-center gap-1.5
            rounded-full border border-light-border px-3.5 py-1.5
            text-xs font-semibold transition duration-200
            hover:border-brand hover:bg-brand/5 hover:text-brand
            focus-visible:outline-none focus-visible:ring-2
            focus-visible:ring-brand focus-visible:ring-offset-2
            dark:border-dark-border
            dark:focus-visible:ring-offset-dark-bg
            sm:min-h-10 sm:text-sm
          "
                >
                    Listen on {item.label}
                    <span aria-hidden="true">↗</span>
                </a>
            ))}
        </div>
    );
}

function AlbumArtwork({
    artworkUrl,
    title,
}: {
    artworkUrl: string | null;
    title: string;
}) {
    return (
        <div className="relative aspect-square w-full overflow-hidden rounded-2xl bg-light-muted/10 shadow-lg shadow-black/10 ring-1 ring-black/5 dark:bg-dark-muted/10 dark:ring-white/10">
            {artworkUrl ? (
                <Image
                    src={artworkUrl}
                    alt={`${title} album artwork`}
                    fill
                    priority
                    sizes="(max-width: 767px) min(72vw, 320px), 280px"
                    className="object-cover"
                />
            ) : (
                <div
                    className="flex h-full items-center justify-center bg-gradient-to-br from-brand/20 via-brand/10 to-transparent text-7xl text-brand"
                    role="img"
                    aria-label={`Artwork unavailable for ${title}`}
                >
                    ♫
                </div>
            )}
        </div>
    );
}

export default async function AlbumDetailPage({
    params,
}: AlbumPageProps) {
    const { slug } = await params;

    if (!slug.trim()) {
        notFound();
    }

    const album = await getAlbumBySlug(slug);

    const canonicalPath =
        `/music/albums/${encodeURIComponent(album.slug)}`;

    if (slug !== album.slug) {
        permanentRedirect(canonicalPath);
    }

    const artworkUrl = getMediaUrl(album.artwork);
    const releaseDate = formatReleaseDate(album.release_date);
    const artistNames = getArtistNames(album.artists);

    const createAlbumPostUrl = (() => {
        const params = new URLSearchParams({
            target_type: 'album',
            target_id: String(album.id),
            target_title: album.title,
            target_slug: album.slug,
            target_artwork: album.artwork ?? '',
            target_artist: artistNames,
        });

        return `/music/create?${params.toString()}`;
    })();

    const canonicalUrl = new URL(canonicalPath, SITE_URL).toString();

    const structuredData = {
        '@context': 'https://schema.org',
        '@type': 'MusicAlbum',
        '@id': `${canonicalUrl}#album`,
        url: canonicalUrl,
        name: album.title,
        image: artworkUrl ?? undefined,
        datePublished: album.release_date ?? undefined,
        description: cleanText(album.description) || undefined,
        numTracks: album.tracks.length,
        byArtist: album.artists.map((artist) => ({
            '@type': 'MusicGroup',
            name: artist.name,
            url: new URL(
                `/music/artists/${encodeURIComponent(artist.slug)}`,
                SITE_URL,
            ).toString(),
        })),
        track: album.tracks.map((track) => ({
            '@type': 'MusicRecording',
            position: track.track_number,
            name: track.song.title,
            url: new URL(
                `/music/songs/${encodeURIComponent(track.song.slug)}`,
                SITE_URL,
            ).toString(),
            ...(track.song.duration_seconds
                ? {
                    duration: `PT${track.song.duration_seconds}S`,
                }
                : {}),
        })),
    };

    return (
        <div className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
            <MusicNavigation />

            <main className="mx-auto w-full max-w-6xl px-4 py-5 sm:px-6 sm:py-8 lg:px-8">
                <nav
                    aria-label="Breadcrumb"
                    className="mb-5 flex flex-wrap items-center gap-2 text-xs text-light-muted dark:text-dark-muted sm:mb-6 sm:text-sm"
                >
                    <Link
                        href="/music/albums"
                        className="transition hover:text-brand"
                    >
                        Albums
                    </Link>

                    <span aria-hidden="true">/</span>

                    <span
                        aria-current="page"
                        className="max-w-full truncate font-medium text-light-text dark:text-dark-text"
                    >
                        {album.title}
                    </span>
                </nav>

                {/* Compact album hero */}
                <section
                    aria-labelledby="album-title"
                    className="overflow-hidden rounded-3xl border border-light-border bg-light-surface dark:border-dark-border dark:bg-dark-surface"
                >
                    <div className="grid gap-5 p-4 sm:gap-7 sm:p-6 md:grid-cols-[220px_minmax(0,1fr)] md:items-start lg:grid-cols-[260px_minmax(0,1fr)] lg:gap-8 lg:p-7">
                        <div className="mx-auto w-full max-w-[280px] md:max-w-none">
                            <AlbumArtwork
                                artworkUrl={artworkUrl}
                                title={album.title}
                            />
                        </div>

                        <div className="min-w-0">
                            <div className="mb-3 flex flex-wrap items-center gap-2">
                                <span className="rounded-full bg-brand/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.12em] text-brand">
                                    {getReleaseTypeLabel(album.release_type)}
                                </span>

                                {album.is_featured && (
                                    <span className="inline-flex items-center gap-1 rounded-full border border-brand/30 px-3 py-1 text-[10px] font-semibold text-brand">
                                        <span aria-hidden="true">✦</span>
                                        Featured
                                    </span>
                                )}
                            </div>

                            <h1
                                id="album-title"
                                className="break-words text-2xl font-bold tracking-tight sm:text-3xl lg:text-4xl"
                            >
                                {album.title}
                            </h1>

                            {album.artists.length > 0 ? (
                                <div className="mt-2.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm sm:text-base">
                                    {album.artists.map((artist, index) => (
                                        <span
                                            key={artist.id}
                                            className="inline-flex items-center"
                                        >
                                            {index > 0 && (
                                                <span
                                                    className="mr-2 text-light-muted dark:text-dark-muted"
                                                    aria-hidden="true"
                                                >
                                                    ·
                                                </span>
                                            )}

                                            <Link
                                                href={`/music/artists/${encodeURIComponent(artist.slug)}`}
                                                className="font-semibold transition hover:text-brand"
                                            >
                                                {artist.name}
                                            </Link>

                                            {artist.is_verified && (
                                                <span
                                                    className="ml-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-brand text-[10px] font-bold text-white"
                                                    aria-label={`${artist.name} is verified`}
                                                    title="Verified artist"
                                                >
                                                    ✓
                                                </span>
                                            )}
                                        </span>
                                    ))}
                                </div>
                            ) : (
                                <p className="mt-2 text-sm text-light-muted dark:text-dark-muted">
                                    Artist information unavailable
                                </p>
                            )}

                            <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-light-muted dark:text-dark-muted sm:text-sm">
                                {releaseDate && <span>{releaseDate}</span>}

                                {releaseDate && (
                                    <span aria-hidden="true">·</span>
                                )}

                                <span>
                                    {formatCount(album.tracks.length)}{' '}
                                    {album.tracks.length === 1 ? 'track' : 'tracks'}
                                </span>

                                <span aria-hidden="true">·</span>

                                <span>
                                    {formatCount(album.favorites_count)}{' '}
                                    {album.favorites_count === 1 ? 'favorite' : 'favorites'}
                                </span>
                            </div>

                            <AlbumRatingStrip album={album} />

                            {album.description && (
                                <p className="mt-4 whitespace-pre-line text-sm leading-6 text-light-muted dark:text-dark-muted sm:leading-7">
                                    {album.description}
                                </p>
                            )}

                            <div className="mt-4">
                                <ExternalMusicLinks album={album} />
                            </div>

                            <div className="mt-5 flex flex-wrap gap-2.5">
                                <Link
                                    href="#tracklist"
                                    className="inline-flex min-h-10 items-center justify-center rounded-full bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 dark:focus-visible:ring-offset-dark-surface"
                                >
                                    Explore tracklist
                                </Link>

                                <Link
                                    href={createAlbumPostUrl}
                                    className="inline-flex min-h-10 items-center justify-center rounded-full border border-light-border px-4 py-2 text-sm font-semibold transition hover:border-brand hover:bg-brand/5 hover:text-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand dark:border-dark-border"
                                >
                                    Start a discussion
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Tracklist */}
                <section
                    id="tracklist"
                    aria-labelledby="tracklist-title"
                    className="mt-9 scroll-mt-6 sm:mt-11"
                >
                    <div className="mb-4 flex flex-wrap items-end justify-between gap-3 sm:mb-5">
                        <div>
                            <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.18em] text-brand">
                                Inside the album
                            </p>

                            <h2
                                id="tracklist-title"
                                className="text-2xl font-bold tracking-tight sm:text-3xl"
                            >
                                Tracklist
                            </h2>

                            <p className="mt-1.5 max-w-xl text-sm leading-6 text-light-muted dark:text-dark-muted">
                                Select a song to explore its details, ratings, and community discussion.
                            </p>
                        </div>

                        <span className="shrink-0 rounded-full border border-light-border px-3 py-1.5 text-xs font-medium text-light-muted dark:border-dark-border dark:text-dark-muted">
                            {formatCount(album.tracks.length)}{' '}
                            {album.tracks.length === 1 ? 'track' : 'tracks'}
                        </span>
                    </div>

                    {album.tracks.length === 0 ? (
                        <div className="rounded-2xl border border-dashed border-light-border bg-light-surface px-5 py-12 text-center dark:border-dark-border dark:bg-dark-surface">
                            <div
                                className="text-4xl text-brand"
                                aria-hidden="true"
                            >
                                ♫
                            </div>

                            <h3 className="mt-4 font-semibold">
                                Tracklist coming soon
                            </h3>

                            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-light-muted dark:text-dark-muted">
                                The songs for this album are not available yet. Check back later for the complete tracklist.
                            </p>
                        </div>
                    ) : (
                        <ol className="overflow-hidden rounded-2xl border border-light-border bg-light-surface dark:border-dark-border dark:bg-dark-surface">
                            {album.tracks.map((track) => {
                                const song = track.song;
                                const trackArtwork = getMediaUrl(song.artwork);
                                const trackArtists = getTrackArtists(song);
                                const songUrl =
                                    `/music/songs/${encodeURIComponent(song.slug)}`;

                                return (
                                    <li
                                        key={track.id}
                                        className="border-b border-light-border last:border-b-0 dark:border-dark-border"
                                    >
                                        <Link
                                            href={songUrl}
                                            aria-label={`View ${song.title} song details`}
                                            className="
                        group relative flex min-w-0 items-center gap-3
                        px-3 py-3 transition-colors duration-200
                        hover:bg-[#008080]/[0.10]
                        focus-visible:z-10 focus-visible:outline-none
                        focus-visible:ring-2 focus-visible:ring-inset
                        focus-visible:ring-[#008080]
                        dark:hover:bg-[#008080]/[0.20]
                        sm:gap-4 sm:px-4 sm:py-3.5
                      "
                                        >
                                            <span className="hidden w-7 shrink-0 text-center text-sm tabular-nums text-light-muted dark:text-dark-muted sm:block">
                                                {track.track_number}
                                            </span>

                                            <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-light-muted/10 ring-1 ring-black/5 dark:bg-dark-muted/10 dark:ring-white/10 sm:h-14 sm:w-14">
                                                {trackArtwork ? (
                                                    <Image
                                                        src={trackArtwork}
                                                        alt=""
                                                        fill
                                                        sizes="56px"
                                                        className="object-cover transition-transform duration-300 group-hover:scale-105"
                                                    />
                                                ) : (
                                                    <div
                                                        className="flex h-full items-center justify-center text-xl text-brand"
                                                        aria-hidden="true"
                                                    >
                                                        ♫
                                                    </div>
                                                )}
                                            </div>

                                            <div className="min-w-0 flex-1">
                                                <p className="flex items-start gap-1.5">
                                                    <span className="text-xs tabular-nums text-light-muted dark:text-dark-muted sm:hidden">
                                                        {track.track_number}.
                                                    </span>

                                                    <span className="min-w-0 break-words text-sm font-semibold text-light-text transition-colors duration-200 group-hover:text-[#008080] dark:text-dark-text dark:group-hover:text-[#20B2AA] sm:text-base">
                                                        {song.title}
                                                    </span>
                                                </p>

                                                <p className="mt-1 break-words text-xs text-light-muted dark:text-dark-muted sm:text-sm">
                                                    {getArtistNames(trackArtists) ||
                                                        artistNames ||
                                                        'Unknown artist'}
                                                </p>

                                                {song.duration_display && (
                                                    <p className="mt-1 text-[11px] text-light-muted dark:text-dark-muted sm:text-xs">
                                                        {song.duration_display}
                                                    </p>
                                                )}
                                            </div>

                                            <span
                                                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-light-muted transition-all duration-200 group-hover:bg-[#008080]/10 group-hover:text-[#008080] group-hover:translate-x-0.5 dark:text-dark-muted dark:group-hover:bg-[#008080]/20 dark:group-hover:text-[#20B2AA]"
                                                aria-hidden="true"
                                            >
                                                <svg
                                                    viewBox="0 0 24 24"
                                                    className="h-4 w-4"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    strokeWidth="1.8"
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                >
                                                    <path d="M7 17 17 7" />
                                                    <path d="M7 7h10v10" />
                                                </svg>
                                            </span>
                                        </Link>
                                    </li>
                                );
                            })}
                        </ol>
                    )}
                </section>

                {/* Editorial review */}
                {album.editorial_review && (
                    <section
                        aria-labelledby="editorial-review-title"
                        className="mt-9 rounded-2xl border border-light-border bg-light-surface p-5 dark:border-dark-border dark:bg-dark-surface sm:mt-11 sm:p-7"
                    >
                        <div className="flex items-start gap-3">
                            <div
                                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand/10 text-lg text-brand"
                                aria-hidden="true"
                            >
                                ✦
                            </div>

                            <div className="min-w-0">
                                <h2
                                    id="editorial-review-title"
                                    className="text-xl font-bold sm:text-2xl"
                                >
                                    Editorial review
                                </h2>

                                <p className="mt-1 text-sm text-light-muted dark:text-dark-muted">
                                    VibeNationHQ editorial coverage
                                </p>
                            </div>
                        </div>

                        <p className="mt-4 whitespace-pre-line text-sm leading-7 text-light-muted dark:text-dark-muted sm:mt-5 sm:text-base">
                            {album.editorial_review}
                        </p>
                    </section>
                )}

                {/* Album-targeted community posts */}
                <section className="mt-9 sm:mt-11">
                    <TargetCommunityPosts
                        targetType="album"
                        targetId={album.id}
                        createPostUrl={createAlbumPostUrl}
                    />
                </section>
            </main>

            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{
                    __html: JSON.stringify(structuredData).replace(
                        /</g,
                        '\\u003c',
                    ),
                }}
            />
        </div>
    );
}
