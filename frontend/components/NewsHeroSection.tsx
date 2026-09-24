import Image from 'next/image';
import Link from 'next/link';

export interface BaseNewsArticle {
    id: number;
    title: string;
    slug: string;
    friendly_date?: string;
    thumbnail_url?: string;
    thumbnail?: string;
    is_sponsored?: boolean;
}

interface HeroNewsSectionProps {
    globalFeatured: BaseNewsArticle | null;
    sponsoredFeature: BaseNewsArticle | null;
    topNews: BaseNewsArticle[];
    latestNews: BaseNewsArticle[];
    categoryName?: string;
}

export default function HeroNewsSection({
    globalFeatured,
    sponsoredFeature,
    topNews,
    latestNews,
    categoryName,
}: HeroNewsSectionProps) {
    const combinedTopNews: BaseNewsArticle[] = [
        ...(sponsoredFeature ? [{ ...sponsoredFeature, is_sponsored: true }] : []),
        ...topNews,
    ].slice(0, 5);

    return (
        <section className="w-full my-4">
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.2fr_1fr] gap-4 items-start">

                {/* CENTER COLUMN: Featured Article */}
                <div className="flex flex-col min-w-0 order-1 lg:order-2">

                    {globalFeatured ? (
                        <Link
                            href={`/news/article/${globalFeatured.slug}`}
                            className="group relative w-full min-h-[380px] sm:min-h-[420px] lg:min-h-[460px] rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-xl flex flex-col justify-end p-5 sm:p-8"
                        >
                            <Image
                                src={
                                    globalFeatured.thumbnail ||
                                    globalFeatured.thumbnail_url ||
                                    '/images/default-hero.jpg'
                                }
                                alt={globalFeatured.title}
                                fill
                                priority
                                unoptimized
                                sizes="(max-width: 1024px) 100vw, 42vw"
                                className="object-cover transition-transform duration-700 group-hover:scale-105 opacity-60 group-hover:opacity-75"
                            />

                            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent pointer-events-none" />

                            <div className="relative z-10">
                                <span className="inline-block px-3 py-1 rounded-full bg-teal-500 text-slate-950 font-black text-xs uppercase tracking-widest mb-3 shadow-md">
                                    Featured Story
                                </span>

                                <h1 className="text-2xl sm:text-3xl lg:text-3xl font-black text-white tracking-tight leading-snug group-hover:text-teal-300 transition-colors line-clamp-3">
                                    {globalFeatured.title}
                                </h1>

                                {globalFeatured.friendly_date && (
                                    <p className="text-xs font-semibold text-slate-300 mt-3 flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                                        {globalFeatured.friendly_date}
                                    </p>
                                )}
                            </div>
                        </Link>
                    ) : (
                        <div className="min-h-[380px] sm:min-h-[420px] lg:min-h-[460px] rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-slate-400">
                            No featured story available.
                        </div>
                    )}
                </div>


                {/* LEFT COLUMN: Top News */}
                <div className="flex flex-col min-w-0 order-2 lg:order-1">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="w-2 h-6 bg-teal-500 rounded-full shrink-0" />
                        <h2 className="text-xl font-black text-slate-950 dark:text-white tracking-tight">
                            {categoryName ? `Top ${categoryName}` : 'Top News'}
                        </h2>
                    </div>

                    <div className="flex flex-col gap-2.5">
                        {combinedTopNews.map((article) => {
                            const isSponsored = article.is_sponsored;

                            const imgUrl =
                                article.thumbnail_url ||
                                article.thumbnail ||
                                '/images/default-news.jpg';

                            return (
                                <Link
                                    key={`${article.id}-${article.slug}`}
                                    href={`/news/article/${article.slug}`}
                                    className={`group relative flex items-center justify-between gap-3 p-2.5 rounded-xl border transition-all duration-200 ${isSponsored
                                            ? 'bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-amber-500/40 dark:border-amber-500/50 shadow-sm'
                                            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800/80 hover:border-teal-500/50 dark:hover:border-teal-500/40 shadow-sm'
                                        }`}
                                >
                                    <div className="flex-1 min-w-0">
                                        {isSponsored && (
                                            <span className="inline-block px-2 py-0.5 mb-1 text-[10px] font-black uppercase tracking-wider bg-amber-500 text-slate-950 rounded-md">
                                                ★ Sponsored
                                            </span>
                                        )}

                                        <h3
                                            className={`text-xs sm:text-sm font-bold line-clamp-2 leading-snug transition-colors ${isSponsored
                                                    ? 'text-amber-950 dark:text-amber-300 group-hover:text-amber-600'
                                                    : 'text-slate-900 dark:text-slate-100 group-hover:text-teal-600 dark:group-hover:text-teal-400'
                                                }`}
                                        >
                                            {article.title}
                                        </h3>
                                    </div>

                                    <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-lg overflow-hidden shrink-0 bg-slate-100 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
                                        <Image
                                            src={imgUrl}
                                            alt={article.title}
                                            fill
                                            unoptimized
                                            sizes="64px"
                                            className="object-cover transition-transform duration-300 group-hover:scale-105"
                                        />
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>


                {/* RIGHT COLUMN: Latest News */}
                <div className="flex flex-col min-w-0 order-3 lg:order-3">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="w-2 h-6 bg-cyan-500 rounded-full shrink-0" />
                        <h2 className="text-xl font-black text-slate-950 dark:text-white tracking-tight">
                            {categoryName ? `Latest ${categoryName}` : 'Latest News'}
                        </h2>
                    </div>

                    <div className="flex flex-col gap-2.5">
                        {latestNews.slice(0, 5).map((article) => (
                            <Link
                                key={article.id}
                                href={`/news/article/${article.slug}`}
                                className="group relative flex items-center justify-between gap-3 p-2.5 rounded-xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900 hover:border-cyan-500/50 dark:hover:border-cyan-500/40 transition-all duration-200 shadow-sm"
                            >
                                <div className="flex-1 min-w-0">
                                    <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 line-clamp-2 leading-snug group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                                        {article.title}
                                    </h3>

                                    {article.friendly_date && (
                                        <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 mt-1">
                                            {article.friendly_date}
                                        </p>
                                    )}
                                </div>

                                <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-lg overflow-hidden shrink-0 bg-slate-100 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
                                    <Image
                                        src={
                                            article.thumbnail_url ||
                                            '/images/default-news.jpg'
                                        }
                                        alt={article.title}
                                        fill
                                        unoptimized
                                        sizes="64px"
                                        className="object-cover transition-transform duration-300 group-hover:scale-105"
                                    />
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>

            </div>
        </section>
    );
}