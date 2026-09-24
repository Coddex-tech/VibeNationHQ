import Image from 'next/image';
import Link from 'next/link';

export interface FeaturedArticle {
    id: string | number;
    title: string;
    slug: string;
    friendly_date?: string;
    thumbnail_url?: string;
    thumbnail?: string;
}

export interface PaginatedNews {
    count: number;
    next: string | null;
    previous: string | null;
    current_page: number;
    total_pages: number;
    results: FeaturedArticle[];
}

interface FeaturedArticlesGridProps {
    pagination: PaginatedNews;
    categoryName: string;
    categorySlug: string;
    title?: string;
}

export default function FeaturedArticlesGrid({
    pagination,
    categoryName,
    categorySlug,
    title,
}: FeaturedArticlesGridProps) {
    const {
        results: articles,
        current_page: currentPage,
        total_pages: totalPages,
    } = pagination;

    const sectionTitle = title || `More ${categoryName}`;

    if (!articles || articles.length === 0) {
        return null;
    }

    const getPageNumbers = (): (number | 'ellipsis')[] => {
        if (totalPages <= 7) {
            return Array.from(
                { length: totalPages },
                (_, index) => index + 1
            );
        }

        const pages: (number | 'ellipsis')[] = [1];

        if (currentPage > 4) {
            pages.push('ellipsis');
        }

        const start = Math.max(2, currentPage - 1);
        const end = Math.min(totalPages - 1, currentPage + 1);

        for (let page = start; page <= end; page++) {
            pages.push(page);
        }

        if (currentPage < totalPages - 3) {
            pages.push('ellipsis');
        }

        pages.push(totalPages);

        return pages;
    };

    const pageNumbers = getPageNumbers();

    return (
        <section className="w-full my-8">

            {/* SECTION HEADING */}
            <div className="flex items-center gap-2 mb-4">
                <span className="w-2 h-6 bg-rose-500 rounded-full shrink-0" />

                <h2 className="text-xl sm:text-2xl font-black tracking-tight text-slate-950 dark:text-white">
                    {sectionTitle}
                </h2>
            </div>

            {/* ARTICLES */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">

                {articles.map((article) => {
                    const imageUrl =
                        article.thumbnail_url ||
                        article.thumbnail ||
                        '/images/default-news.jpg';

                    return (
                        <article
                            key={`${article.id}-${article.slug}`}
                            className="
                                group flex flex-row md:flex-col
                                bg-white dark:bg-slate-900
                                border border-slate-200/80 dark:border-slate-800
                                rounded-2xl overflow-hidden shadow-sm
                                hover:shadow-lg transition-all duration-300
                            "
                        >

                            {/* IMAGE */}
                            <Link
                                href={`/news/article/${article.slug}`}
                                aria-label={`Read ${article.title}`}
                                className="
                                    relative shrink-0 w-[115px] h-[115px]
                                    sm:w-[135px] sm:h-[135px]
                                    md:w-full md:h-[200px] lg:h-[210px]
                                    overflow-hidden bg-slate-100 dark:bg-slate-800
                                "
                            >
                                <Image
                                    src={imageUrl}
                                    alt={article.title}
                                    fill
                                    unoptimized
                                    sizes="
                                        (max-width: 640px) 115px,
                                        (max-width: 768px) 135px,
                                        (max-width: 1024px) 50vw,
                                        33vw
                                    "
                                    className="
                                        object-cover transition-transform
                                        duration-500 group-hover:scale-105
                                    "
                                />
                            </Link>

                            {/* CONTENT */}
                            <div className="flex flex-col justify-between flex-1 min-w-0 p-3 sm:p-4 md:p-5">

                                <div>

                                    {/* CATEGORY */}
                                    <Link
                                        href={`/news/category/${categorySlug}`}
                                        className="
                                            inline-flex items-center rounded-md
                                            bg-rose-500/10 dark:bg-rose-500/15
                                            px-2 py-1 mb-2
                                            text-[9px] sm:text-[10px] font-extrabold
                                            uppercase tracking-wider
                                            text-rose-600 dark:text-rose-400
                                            hover:bg-rose-500/15 dark:hover:bg-rose-500/20
                                            transition-colors
                                        "
                                    >
                                        {categoryName}
                                    </Link>

                                    {/* TITLE */}
                                    <h3 className="
                                        text-sm sm:text-base lg:text-lg
                                        font-bold text-slate-900 dark:text-white
                                        leading-snug
                                        group-hover:text-rose-600 dark:group-hover:text-rose-400
                                        transition-colors duration-200 line-clamp-3
                                    ">
                                        <Link href={`/news/article/${article.slug}`}>
                                            {article.title}
                                        </Link>
                                    </h3>

                                </div>

                                {/* DATE */}
                                {article.friendly_date && (
                                    <p className="
                                        mt-2 md:mt-3
                                        text-[10px] sm:text-xs font-medium
                                        text-slate-500 dark:text-slate-400
                                    ">
                                        {article.friendly_date}
                                    </p>
                                )}

                            </div>

                        </article>
                    );
                })}

            </div>

            {/* PAGINATION */}
            {totalPages > 1 && (
                <nav
                    aria-label="News pagination"
                    className="flex items-center justify-center gap-1.5 sm:gap-2 mt-8"
                >

                    {/* PREVIOUS */}
                    {currentPage > 1 ? (
                        <Link
                            href={`?page=${currentPage - 1}`}
                            scroll={false}
                            className="
                                inline-flex items-center justify-center
                                min-w-9 h-9 px-2 rounded-lg
                                border border-slate-200 dark:border-slate-700
                                bg-white dark:bg-slate-900
                                text-slate-700 dark:text-slate-300
                                text-sm font-bold
                                hover:bg-slate-50 dark:hover:bg-slate-800
                                transition-colors
                            "
                        >
                            <span>‹</span>
                            <span className="hidden sm:inline ml-1">
                                Previous
                            </span>
                        </Link>
                    ) : (
                        <span className="
                            inline-flex items-center justify-center
                            min-w-9 h-9 px-2 rounded-lg
                            border border-slate-200 dark:border-slate-700
                            bg-white dark:bg-slate-900
                            text-slate-400 dark:text-slate-600
                            text-sm font-bold opacity-50 cursor-not-allowed
                        ">
                            <span>‹</span>
                            <span className="hidden sm:inline ml-1">
                                Previous
                            </span>
                        </span>
                    )}

                    {/* PAGE NUMBERS */}
                    <div className="flex items-center gap-1.5 sm:gap-2">

                        {pageNumbers.map((page, index) => {
                            if (page === 'ellipsis') {
                                return (
                                    <span
                                        key={`ellipsis-${index}`}
                                        className="
                                            inline-flex items-center justify-center
                                            w-8 h-9 text-slate-500
                                            dark:text-slate-400 font-bold
                                        "
                                    >
                                        …
                                    </span>
                                );
                            }

                            const isCurrent = page === currentPage;

                            if (isCurrent) {
                                return (
                                    <span
                                        key={page}
                                        aria-current="page"
                                        className="
                                            inline-flex items-center justify-center
                                            min-w-9 h-9 px-2 rounded-lg
                                            bg-rose-500 text-white text-sm
                                            font-bold shadow-sm
                                        "
                                    >
                                        {page}
                                    </span>
                                );
                            }

                            return (
                                <Link
                                    key={page}
                                    href={`?page=${page}`}
                                    scroll={false}
                                    className="
                                        inline-flex items-center justify-center
                                        min-w-9 h-9 px-2 rounded-lg
                                        border border-slate-200 dark:border-slate-700
                                        bg-white dark:bg-slate-900
                                        text-slate-700 dark:text-slate-300
                                        text-sm font-bold
                                        hover:bg-slate-50 dark:hover:bg-slate-800
                                        transition-colors
                                    "
                                >
                                    {page}
                                </Link>
                            );
                        })}

                    </div>

                    {/* NEXT */}
                    {currentPage < totalPages ? (
                        <Link
                            href={`?page=${currentPage + 1}`}
                            scroll={false}
                            className="
                                inline-flex items-center justify-center
                                min-w-9 h-9 px-2 rounded-lg
                                border border-slate-200 dark:border-slate-700
                                bg-white dark:bg-slate-900
                                text-slate-700 dark:text-slate-300
                                text-sm font-bold
                                hover:bg-slate-50 dark:hover:bg-slate-800
                                transition-colors
                            "
                        >
                            <span className="hidden sm:inline mr-1">
                                Next
                            </span>
                            <span>›</span>
                        </Link>
                    ) : (
                        <span className="
                            inline-flex items-center justify-center
                            min-w-9 h-9 px-2 rounded-lg
                            border border-slate-200 dark:border-slate-700
                            bg-white dark:bg-slate-900
                            text-slate-400 dark:text-slate-600
                            text-sm font-bold opacity-50 cursor-not-allowed
                        ">
                            <span className="hidden sm:inline mr-1">
                                Next
                            </span>
                            <span>›</span>
                        </span>
                    )}

                </nav>
            )}

        </section>
    );
}