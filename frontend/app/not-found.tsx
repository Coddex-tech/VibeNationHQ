import Link from 'next/link';
import { HomeIcon, SearchIcon, RadioIcon } from '@/components/Icons';
import FadeIn from '@/components/FadeIn';

export default function NotFound() {
    return (
        <main className="min-h-[calc(100vh-5rem)] flex items-center justify-center px-4 sm:px-6 py-16 overflow-hidden">

            <FadeIn direction="up" delay={0.1}>
                <div className="w-full max-w-3xl text-center">

                    {/* Visual */}
                    <div className="relative mx-auto mb-8 w-fit">

                        {/* Decorative glow */}
                        <div className="absolute inset-0 bg-teal-500/20 dark:bg-teal-400/10 blur-3xl rounded-full scale-150 pointer-events-none" />

                        <div className="relative flex items-center justify-center w-32 h-32 sm:w-40 sm:h-40 rounded-full border border-teal-500/20 bg-teal-500/5 dark:bg-teal-500/10">

                            <RadioIcon className="w-14 h-14 sm:w-16 sm:h-16 text-teal-600 dark:text-teal-400" />

                            {/* Signal dots */}
                            <span className="absolute top-4 right-6 w-2 h-2 rounded-full bg-teal-500 animate-pulse" />
                            <span className="absolute top-8 right-2 w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                            <span className="absolute bottom-7 left-5 w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />

                        </div>
                    </div>

                    {/* 404 */}
                    <p className="text-7xl sm:text-8xl md:text-9xl font-black tracking-tighter text-slate-400 dark:text-slate-800 select-none">
                        404
                    </p>

                    {/* Heading */}
                    <h1 className="mt-2 text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-slate-950 dark:text-white">
                        This vibe went missing.
                    </h1>

                    {/* Description */}
                    <p className="mt-5 max-w-xl mx-auto text-base sm:text-lg leading-relaxed text-slate-600 dark:text-slate-300">
                        The page you're looking for may have been moved, removed,
                        or the URL might have a little typo in it.
                    </p>

                    {/* Actions */}
                    <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">

                        <Link
                            href="/"
                            className="inline-flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm transition-all duration-200 shadow-md hover:shadow-lg active:scale-95"
                        >
                            <HomeIcon className="w-4 h-4" />
                            Back to Home
                        </Link>

                        <Link
                            href="/news"
                            className="inline-flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 hover:border-teal-500 hover:text-teal-600 dark:hover:text-teal-400 font-bold text-sm transition-all duration-200 active:scale-95"
                        >
                            Explore News
                        </Link>

                    </div>

                    {/* Search */}
                    <div className="mt-10 max-w-md mx-auto">

                        <p className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">
                            Or search VibeNationHQ
                        </p>

                        <Link
                            href="/search"
                            className="group flex items-center gap-3 w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 text-left transition-all duration-200 hover:border-teal-500/50"
                        >
                            <SearchIcon className="w-5 h-5 text-slate-400 group-hover:text-teal-500 transition-colors" />

                            <span className="flex-1 text-sm text-slate-500 dark:text-slate-400">
                                Search for songs, artists or news...
                            </span>

                            <span className="text-xs font-bold text-teal-600 dark:text-teal-400">
                                Search
                            </span>
                        </Link>

                    </div>

                    {/* Small brand message */}
                    <p className="mt-12 text-xs text-slate-400 dark:text-slate-600">
                        VibeNationHQ · News · Music · Culture
                    </p>

                </div>
            </FadeIn>

        </main>
    );
}