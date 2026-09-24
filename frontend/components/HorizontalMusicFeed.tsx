import Image from 'next/image';
import Link from 'next/link';

export interface Artist {
    id: number;
    name: string;
}

export interface SongItem {
    id: number;
    title: string;
    slug: string;
    artists: Artist[];
    media?: {
        url: string;
        alt: string;
    };
}

interface HorizontalMusicFeedProps {
    title?: string;
    songs: SongItem[];
}

export default function HorizontalMusicFeed({
    title = 'Latest Music',
    songs,
}: HorizontalMusicFeedProps) {
    return (
        <section className="w-full my-6 sm:my-8">
            {/* Section Header */}
            <div className="flex items-center justify-between gap-4 mb-3 sm:mb-4">
                <div className="flex items-center gap-2 min-w-0">
                    <span className="w-2 h-6 bg-purple-600 dark:bg-purple-500 rounded-full shrink-0" />

                    <h2 className="text-lg sm:text-xl font-black text-slate-950 dark:text-white tracking-tight truncate">
                        {title}
                    </h2>
                </div>

                <Link
                    href="/music"
                    className="shrink-0 text-xs sm:text-sm font-bold text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors"
                >
                    Listen More →
                </Link>
            </div>

            {/* Horizontal Scroll Container */}
            <div className="flex gap-3 sm:gap-4 overflow-x-auto pb-3 sm:pb-4 pt-1 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700 scrollbar-track-transparent">
                {songs.map((song) => {
                    const artistNames = song.artists
                        .map((a) => a.name)
                        .join(', ');

                    const coverImg =
                        song.media?.url || '/images/default-cover.jpg';

                    return (
                        <Link
                            key={song.id}
                            href={`/music/songs/${song.slug}`}
                            className="group shrink-0 w-28 sm:w-40 lg:w-44 flex flex-col gap-1.5 sm:gap-2"
                        >
                            {/* Cover Image */}
                            <div className="relative aspect-square w-full rounded-lg sm:rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-800 shadow-sm group-hover:shadow-md transition-all duration-300">
                                <Image
                                    src={coverImg}
                                    alt={song.media?.alt || song.title}
                                    fill
                                    unoptimized
                                    sizes="(max-width: 640px) 112px, (max-width: 1024px) 160px, 176px"
                                    className="object-cover transition-transform duration-300 group-hover:scale-105"
                                />
                            </div>

                            {/* Text Info */}
                            <div className="flex flex-col min-w-0">
                                <h3 className="text-[11px] sm:text-sm font-bold text-slate-900 dark:text-slate-100 truncate group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                                    {song.title}
                                </h3>

                                <p className="text-[10px] sm:text-xs font-medium text-slate-500 dark:text-slate-400 truncate">
                                    {artistNames}
                                </p>
                            </div>
                        </Link>
                    );
                })}
            </div>
        </section>
    );
}