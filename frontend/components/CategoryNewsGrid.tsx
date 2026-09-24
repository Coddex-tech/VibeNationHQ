import Image from 'next/image';
import Link from 'next/link';

export interface CategoryNewsItem {
    id: number;
    title: string;
    slug: string;
    category_name?: string;
    friendly_date?: string;
    thumbnail_url?: string;
    thumbnail?: string;
}

interface CategoryNewsGridProps {
    categoryTitle?: string;
    newsList: CategoryNewsItem[];
}

export default function CategoryNewsGrid({
    categoryTitle,
    newsList = [],
}: CategoryNewsGridProps) {
    if (!newsList || newsList.length === 0) return null;

    // First item gets the large feature card
    const mainFeaturedNews = newsList[0];

    // Next 4 items go into the 2x2 grid
    const secondaryNewsList = newsList.slice(1, 5);

    const getNewsImg = (item: CategoryNewsItem) =>
        item.thumbnail_url ||
        item.thumbnail ||
        '/images/default-news.jpg';

    // Use the article's category if available.
    // Otherwise, fall back to the category title of this section.
    const getCategoryName = (item: CategoryNewsItem) =>
        item.category_name || categoryTitle;

    return (
        <section className="w-full my-8 px-2 sm:px-4">

            {/* Category Section Header */}
            {categoryTitle && (
                <div className="flex items-center gap-2 mb-4">
                    <span className="w-2 h-6 bg-rose-500 rounded-full shrink-0" />

                    <h2 className="text-xl sm:text-2xl font-black text-slate-950 dark:text-white tracking-tight">
                        {categoryTitle}
                    </h2>
                </div>
            )}

            {/* Main Responsive Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-5 items-stretch">

                {/* =====================================================
                    LEFT: MAIN FEATURED NEWS
                    Full width on mobile
                    6 columns on desktop
                ====================================================== */}
                <div className="lg:col-span-6 flex flex-col">

                    <Link
                        href={`/news/${mainFeaturedNews.slug}`}
                        aria-label={`Read ${mainFeaturedNews.title}`}
                        className="group flex flex-col h-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300"
                    >

                        {/* Featured Image */}
                        <div className="relative w-full h-[180px] sm:h-[300px] lg:h-[360px] bg-slate-100 dark:bg-slate-800 overflow-hidden">

                            <Image
                                src={getNewsImg(mainFeaturedNews)}
                                alt={mainFeaturedNews.title}
                                fill
                                priority
                                unoptimized
                                sizes="(max-width: 1024px) 100vw, 50vw"
                                className="object-cover transition-transform duration-500 group-hover:scale-105"
                            />

                        </div>

                        {/* Featured Content */}
                        <div className="flex flex-col justify-between flex-1 p-3.5 sm:p-5 lg:p-6">

                            <div>

                                {/* Category Tag */}
                                {getCategoryName(mainFeaturedNews) && (
                                    <span className="inline-flex items-center px-2 py-1 mb-2 rounded-md bg-rose-500/10 dark:bg-rose-500/15 text-[9px] sm:text-[10px] font-extrabold text-rose-600 dark:text-rose-400 uppercase tracking-wider">
                                        {getCategoryName(mainFeaturedNews)}
                                    </span>
                                )}

                                {/* Title */}
                                <h3 className="text-base sm:text-xl lg:text-2xl font-extrabold text-slate-900 dark:text-slate-50 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors leading-snug line-clamp-3">
                                    {mainFeaturedNews.title}
                                </h3>

                            </div>

                            {/* Date */}
                            {mainFeaturedNews.friendly_date && (
                                <p className="text-[10px] sm:text-xs font-medium text-slate-400 mt-3 sm:mt-4">
                                    {mainFeaturedNews.friendly_date}
                                </p>
                            )}

                        </div>

                    </Link>

                </div>


                {/* =====================================================
                    RIGHT: SECONDARY NEWS
                    2 cards per row on mobile
                    2x2 grid on desktop
                ====================================================== */}
                <div className="lg:col-span-6 grid grid-cols-2 gap-2.5 sm:gap-4">

                    {secondaryNewsList.map((newsItem) => (

                        <Link
                            key={`${newsItem.id}-${newsItem.slug}`}
                            href={`/news/${newsItem.slug}`}
                            aria-label={`Read ${newsItem.title}`}
                            className="group flex flex-col bg-white dark:bg-slate-900 rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300"
                        >

                            {/* Card Image */}
                            <div className="relative w-full h-28 sm:h-36 lg:h-40 bg-slate-100 dark:bg-slate-800 overflow-hidden">

                                <Image
                                    src={getNewsImg(newsItem)}
                                    alt={newsItem.title}
                                    fill
                                    unoptimized
                                    sizes="(max-width: 1024px) 50vw, 25vw"
                                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                                />

                            </div>


                            {/* Card Details */}
                            <div className="flex flex-col justify-between flex-1 p-2.5 sm:p-4">

                                <div>

                                    {/* Category Tag */}
                                    {getCategoryName(newsItem) && (
                                        <span className="inline-flex items-center px-1.5 py-0.5 mb-1.5 rounded-md bg-rose-500/10 dark:bg-rose-500/15 text-[8px] sm:text-[10px] font-extrabold text-rose-600 dark:text-rose-400 uppercase tracking-wider">
                                            {getCategoryName(newsItem)}
                                        </span>
                                    )}

                                    {/* Title */}
                                    <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors line-clamp-2 leading-tight sm:leading-snug">
                                        {newsItem.title}
                                    </h4>

                                </div>


                                {/* Date */}
                                {newsItem.friendly_date && (
                                    <p className="text-[9px] sm:text-[11px] font-medium text-slate-400 mt-2 sm:mt-3">
                                        {newsItem.friendly_date}
                                    </p>
                                )}

                            </div>

                        </Link>

                    ))}

                </div>

            </div>

        </section>
    );
}