
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import {
    ArrowLeft,
    ArrowUpRight,
    Disc3,
    Music2,
    Radio,
    Star,
} from 'lucide-react';

import { getMediaUrl } from '@/lib/api';
import TargetCommunityPosts from '@/components/music/TargetCommunityPosts';
import SongPreviewPlayer from '@/components/music/SongPreviewPlayer';

type Artist = {
    id: number;
    name: string;
    slug: string;
    profile_image: string | null;
    is_verified: boolean;
    followers_count: number;
};

type SongAlbum = {
    id: number;
    title: string;
    slug: string;
    release_type: string;
    artwork: string | null;
    release_date: string | null;
    favorites_count: number;
    ratings_count: number;
    artists: Artist[];
};

type SongDetail = {
    id: number;
    title: string;
    slug: string;
    artwork: string | null;
    release_date: string | null;
    duration_display: string | null;
    duration_seconds: number | null;
    description: string | null;
    editorial_review: string | null;
    preview_url: string | null;
    community_rating_average: number | null;
    community_rating_count: number;
    ratings_count: number;
    favorites_count: number;
    artists: Artist[];
    featured_artists: Artist[];
    album: SongAlbum | null;
    genres: Array<{
        id: number;
        name: string;
        slug?: string;
    }>;
    spotify_url: string | null;
    apple_music_url: string | null;
    youtube_url: string | null;
    audiomack_url: string | null;
    boomplay_url: string | null;
};

async function getSong(slug: string): Promise<SongDetail | null> {
    const apiBase =
        process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

    try {
        const response = await fetch(
            `${apiBase.replace(/\/$/, '')}/api/v1/music/songs/${encodeURIComponent(slug)}/`,
            {
                next: { revalidate: 60 },
            },
        );

        if (response.status === 404) {
            return null;
        }

        if (!response.ok) {
            throw new Error(`Song API returned ${response.status}`);
        }

        return (await response.json()) as SongDetail;
    } catch (error) {
        console.error('Failed to fetch song details:', error);
        throw error;
    }
}

function formatDate(value: string | null): string | null {
    if (!value) return null;

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat('en', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    }).format(date);
}

function ArtistLinks({ artists }: { artists: Artist[] }) {
    if (!artists.length) {
        return (
            <span className="text-sm text-light-text-soft dark:text-dark-text-soft">
                Unknown artist
            </span>
        );
    }

    return (
        <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
            {artists.map((artist, index) => (
                <span key={artist.id} className="inline-flex items-center gap-2">
                    <Link
                        href={`/music/artists/${artist.slug}`}
                        className="text-light-text transition hover:text-brand-teal dark:text-dark-text dark:hover:text-brand-teal-light"
                    >
                        {artist.name}
                    </Link>

                    {artist.is_verified && (
                        <span
                            title="Verified artist"
                            aria-label="Verified artist"
                            className="flex h-4 w-4 items-center justify-center rounded-full bg-brand-teal/15 text-[10px] font-bold text-brand-teal-dark dark:text-brand-teal-light"
                        >
                            ✓
                        </span>
                    )}

                    {index < artists.length - 1 && (
                        <span className="text-light-border dark:text-dark-border">
                            ·
                        </span>
                    )}
                </span>
            ))}
        </span>
    );
}

function StreamingLink({
    href,
    label,
}: {
    href: string | null;
    label: string;
}) {
    if (!href) return null;

    return (
        <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-9 items-center gap-2 rounded-full border border-light-border bg-light-surface-soft px-3.5 text-xs font-medium text-light-text-soft transition hover:border-brand-teal hover:text-brand-teal-dark dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text-soft dark:hover:text-brand-teal-light"
        >
            {label}
            <ArrowUpRight className="h-3.5 w-3.5" />
        </a>
    );
}

function SongRatingInline({
    average,
    count,
}: {
    average: number | null;
    count: number;
}) {
    const hasRatings =
        typeof average === 'number' &&
        Number.isFinite(average) &&
        average > 0 &&
        count > 0;

    const rating = hasRatings
        ? Math.min(5, Math.max(0, average))
        : 0;

    const ratingLabel = hasRatings ? rating.toFixed(1) : null;

    return (
        <div
            className="mt-3 flex flex-wrap items-center justify-center gap-x-2 gap-y-1.5 sm:justify-start"
            aria-label={
                hasRatings
                    ? `Community rating ${ratingLabel} out of 5, based on ${count} ${count === 1 ? 'rating' : 'ratings'
                    }`
                    : 'No community ratings yet'
            }
        >
            <div className="flex items-center gap-0.5" aria-hidden="true">
                {[1, 2, 3, 4, 5].map((star) => {
                    const fillPercent = hasRatings
                        ? Math.max(0, Math.min(100, (rating - star + 1) * 100))
                        : 0;

                    return (
                        <span
                            key={star}
                            className="relative inline-flex h-4 w-4 shrink-0"
                        >
                            <Star
                                className="absolute inset-0 h-4 w-4 text-light-border dark:text-dark-border"
                                strokeWidth={1.7}
                            />

                            {fillPercent > 0 && (
                                <Star
                                    className="absolute inset-0 h-4 w-4 fill-brand-teal text-brand-teal"
                                    strokeWidth={1.7}
                                    style={{
                                        clipPath: `inset(0 ${100 - fillPercent}% 0 0)`,
                                    }}
                                />
                            )}
                        </span>
                    );
                })}
            </div>

            <span className="text-sm font-semibold tabular-nums text-light-text dark:text-dark-text">
                {hasRatings ? `${ratingLabel}/5` : 'No ratings yet'}
            </span>

            <span className="text-xs text-light-text-soft dark:text-dark-text-soft">
                ({count.toLocaleString()} {count === 1 ? 'rating' : 'ratings'})
            </span>
        </div>
    );
}

export default async function SongDetailsPage({
    params,
}: {
    params: Promise<{ slug: string }>;
}) {
    const { slug } = await params;
    const song = await getSong(slug);

    if (!song) {
        notFound();
    }

    const artworkUrl = song.artwork ? getMediaUrl(song.artwork) : null;

    const albumArtworkUrl = song.album?.artwork
        ? getMediaUrl(song.album.artwork)
        : null;

    const releaseDate = formatDate(song.release_date);

    const streamingLinks = [
        { label: 'Spotify', href: song.spotify_url },
        { label: 'Apple Music', href: song.apple_music_url },
        { label: 'YouTube', href: song.youtube_url },
        { label: 'Audiomack', href: song.audiomack_url },
        { label: 'Boomplay', href: song.boomplay_url },
    ].filter((item) => Boolean(item.href));

    const createPostParams = new URLSearchParams({
        target_type: 'song',
        target_id: String(song.id),
        target_title: song.title,
        target_slug: song.slug,
        ...(song.artwork ? { target_artwork: song.artwork } : {}),
        ...(song.artists?.length
            ? { target_artist: song.artists.map((artist) => artist.name).join(', ') }
            : {}),
        ...(song.album ? { target_album_title: song.album.title } : {}),
    });

    const createPostUrl = `/music/create?${createPostParams.toString()}`;

    return (
        <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
            <div className="mx-auto w-full max-w-7xl px-4 pb-16 pt-5 sm:px-6 sm:pt-7 lg:px-10">
                {/* Breadcrumb */}
                <nav className="mb-6 flex items-center justify-between sm:mb-7">
                    <Link
                        href="/music"
                        className="inline-flex items-center gap-2 text-sm text-light-text-soft transition hover:text-light-text dark:text-dark-text-soft dark:hover:text-dark-text"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to music
                    </Link>

                    <span className="hidden items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-light-text-soft dark:text-dark-text-soft sm:flex">
                        <span className="h-1.5 w-1.5 rounded-full bg-brand-teal" />
                        VibeNationHQ Music
                    </span>
                </nav>

                {/* Song hero */}
                <section className="grid gap-7 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-center lg:gap-10">
                    <div className="flex min-w-0 flex-col gap-6 sm:flex-row sm:items-center sm:gap-7 lg:gap-9">
                        {/* Artwork */}
                        <div className="group relative mx-auto aspect-square w-full max-w-[280px] shrink-0 sm:mx-0 sm:w-[230px] lg:w-[280px]">
                            <div className="relative h-full w-full overflow-hidden rounded-2xl border border-light-border bg-light-surface dark:border-dark-border dark:bg-dark-surface">
                                {artworkUrl ? (
                                    <Image
                                        src={artworkUrl}
                                        alt={`${song.title} artwork`}
                                        fill
                                        priority
                                        sizes="(max-width: 639px) min(100vw - 2rem, 280px), (max-width: 1023px) 230px, 280px"
                                        className="object-cover transition duration-500 group-hover:scale-[1.025]"
                                    />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center">
                                        <Music2 className="h-16 w-16 text-brand-teal/50" />
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Song information */}
                        <div className="min-w-0 flex-1 text-center sm:text-left">
                            <div className="mb-3 flex flex-wrap items-center justify-center gap-2 sm:justify-start">
                                <span className="inline-flex items-center gap-1.5 rounded-full border border-brand-teal/20 bg-brand-teal/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.15em] text-brand-teal-dark dark:text-brand-teal-light">
                                    <Radio className="h-3 w-3" />
                                    Song profile
                                </span>

                                {song.genres?.slice(0, 2).map((genre) => (
                                    <span
                                        key={genre.id}
                                        className="rounded-full border border-light-border px-3 py-1.5 text-[10px] font-medium uppercase tracking-wider text-light-text-soft dark:border-dark-border dark:text-dark-text-soft"
                                    >
                                        {genre.name}
                                    </span>
                                ))}
                            </div>

                            <h1 className="break-words text-3xl font-semibold leading-[1.1] tracking-[-0.04em] text-light-text dark:text-dark-text sm:text-4xl lg:text-5xl">
                                {song.title}
                            </h1>

                            <div className="mt-3 flex flex-wrap items-center justify-center gap-x-2 gap-y-2 text-sm sm:justify-start sm:text-base">
                                <ArtistLinks artists={song.artists ?? []} />
                            </div>

                            {song.featured_artists?.length > 0 && (
                                <div className="mt-2 flex flex-wrap items-center justify-center gap-2 text-sm text-light-text-soft dark:text-dark-text-soft sm:justify-start">
                                    <span>Featuring</span>
                                    <ArtistLinks artists={song.featured_artists} />
                                </div>
                            )}

                            <div className="mt-4 flex flex-wrap items-center justify-center gap-x-3 gap-y-2 text-xs text-light-text-soft dark:text-dark-text-soft">
                                {song.album && (
                                    <>
                                        <Link
                                            href={`/music/albums/${song.album.slug}`}
                                            className="inline-flex items-center gap-1.5 transition hover:text-brand-teal-dark dark:hover:text-brand-teal-light"
                                        >
                                            <Disc3 className="h-3.5 w-3.5" />
                                            {song.album.title}
                                        </Link>

                                        <span className="text-light-border dark:text-dark-border">
                                            /
                                        </span>
                                    </>
                                )}

                                {releaseDate && <span>{releaseDate}</span>}

                                {song.duration_display && (
                                    <>
                                        {releaseDate && (
                                            <span className="text-light-border dark:text-dark-border">
                                                /
                                            </span>
                                        )}
                                        <span>{song.duration_display}</span>
                                    </>
                                )}
                            </div>

                            {/* Overall community rating */}
                            <SongRatingInline
                                average={song.community_rating_average}
                                count={song.community_rating_count}
                            />

                            {/* Official preview player */}
                            <div className="mt-4">
                                <SongPreviewPlayer
                                    previewUrl={song.preview_url}
                                    title={song.title}
                                />
                            </div>

                            {/* Official streaming platforms */}
                            {streamingLinks.length > 0 && (
                                <div className="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
                                    {streamingLinks.map((item) => (
                                        <StreamingLink
                                            key={item.label}
                                            href={item.href}
                                            label={item.label}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                {/* Community posts with Latest / Relevant sorting */}
                <TargetCommunityPosts
                    targetType="song"
                    targetId={song.id}
                    createPostUrl={createPostUrl}
                />

                {/* About and sidebar follow the community section */}
                <div className="mt-8 grid gap-7 lg:grid-cols-[minmax(0,1fr)_280px] lg:gap-10">
                    <div className="min-w-0">
                        {(song.description || song.editorial_review) && (
                            <section className="border-t border-light-border pt-6 dark:border-dark-border">
                                <div className="mb-4 flex items-center gap-3">
                                    <span className="h-5 w-1 rounded-full bg-brand-teal" />
                                    <h2 className="text-lg font-semibold tracking-tight text-light-text dark:text-dark-text">
                                        About this song
                                    </h2>
                                </div>

                                {song.description && (
                                    <p className="max-w-3xl whitespace-pre-line text-sm leading-7 text-light-text-soft dark:text-dark-text-soft">
                                        {song.description}
                                    </p>
                                )}

                                {song.editorial_review && (
                                    <div className="mt-5 rounded-xl border border-light-border bg-light-surface p-4 sm:p-5 dark:border-dark-border dark:bg-dark-surface">
                                        <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-brand-teal-dark dark:text-brand-teal-light">
                                            Editorial notes
                                        </p>

                                        <p className="whitespace-pre-line text-sm leading-7 text-light-text dark:text-dark-text">
                                            {song.editorial_review}
                                        </p>
                                    </div>
                                )}
                            </section>
                        )}
                    </div>

                    {/* Sidebar */}
                    <aside className="space-y-4">
                        {song.album && (
                            <section className="rounded-xl border border-light-border bg-light-surface p-4 dark:border-dark-border dark:bg-dark-surface">
                                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-light-text-soft dark:text-dark-text-soft">
                                    From the album
                                </p>

                                <Link
                                    href={`/music/albums/${song.album.slug}`}
                                    className="group mt-3 flex items-center gap-3"
                                >
                                    <div className="relative h-[68px] w-[68px] shrink-0 overflow-hidden rounded-lg bg-light-surface-soft dark:bg-dark-surface-soft">
                                        {albumArtworkUrl ? (
                                            <Image
                                                src={albumArtworkUrl}
                                                alt={`${song.album.title} artwork`}
                                                fill
                                                sizes="68px"
                                                className="object-cover transition group-hover:scale-105"
                                            />
                                        ) : (
                                            <div className="flex h-full items-center justify-center">
                                                <Disc3 className="h-6 w-6 text-light-text-soft dark:text-dark-text-soft" />
                                            </div>
                                        )}
                                    </div>

                                    <div className="min-w-0">
                                        <h3 className="line-clamp-2 text-sm font-semibold text-light-text transition group-hover:text-brand-teal-dark dark:text-dark-text dark:group-hover:text-brand-teal-light">
                                            {song.album.title}
                                        </h3>

                                        <p className="mt-1 text-xs text-light-text-soft dark:text-dark-text-soft">
                                            {song.album.release_type}
                                        </p>

                                        <span className="mt-1.5 inline-flex items-center gap-1 text-xs text-brand-teal-dark dark:text-brand-teal-light">
                                            View album
                                            <ArrowUpRight className="h-3 w-3" />
                                        </span>
                                    </div>
                                </Link>
                            </section>
                        )}

                        {song.genres?.length > 0 && (
                            <section className="rounded-xl border border-light-border bg-light-surface p-4 dark:border-dark-border dark:bg-dark-surface">
                                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-light-text-soft dark:text-dark-text-soft">
                                    Genres
                                </p>

                                <div className="mt-3 flex flex-wrap gap-2">
                                    {song.genres.map((genre) => (
                                        <span
                                            key={genre.id}
                                            className="rounded-lg border border-light-border bg-light-surface-soft px-2.5 py-1.5 text-xs text-light-text-soft dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text-soft"
                                        >
                                            {genre.name}
                                        </span>
                                    ))}
                                </div>
                            </section>
                        )}

                        <section className="rounded-xl border border-brand-teal/20 bg-light-surface p-4 dark:bg-dark-surface">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-teal/10 text-brand-teal-dark dark:text-brand-teal-light">
                                <Music2 className="h-4 w-4" />
                            </div>

                            <h3 className="mt-3 text-sm font-semibold text-light-text dark:text-dark-text">
                                Music is better together.
                            </h3>

                            <p className="mt-1.5 text-sm leading-5 text-light-text-soft dark:text-dark-text-soft">
                                Rate songs, share your perspective and discover what other
                                listeners think.
                            </p>

                            <Link
                                href={createPostUrl}
                                className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-brand-teal-dark hover:opacity-80 dark:text-brand-teal-light"
                            >
                                Join the conversation
                                <ArrowUpRight className="h-4 w-4" />
                            </Link>
                        </section>
                    </aside>
                </div>
            </div>
        </main>
    );
}
