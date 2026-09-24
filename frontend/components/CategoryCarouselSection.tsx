'use client';

import { useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
    ChevronLeft,
    ChevronRight,
    ArrowRight,
} from 'lucide-react';

export interface Article {
    id: string | number;
    title: string;
    slug: string;
    category: {
        name: string;
        slug: string;
    };
    thumbnail_url?: string;
    friendly_date?: string;
}

interface CategoryCarouselSectionProps {
    sectionTitle: string;
    sectionSlug?: string;
    articles: Article[];
    basePath?: string;
}

export default function CategoryCarouselSection({
    sectionTitle,
    sectionSlug,
    articles,
    basePath = '/news/article',
}: CategoryCarouselSectionProps) {
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const handleScroll = (direction: 'left' | 'right') => {
        if (!scrollContainerRef.current) {
            return;
        }

        const scrollAmount =
            scrollContainerRef.current.clientWidth * 0.75;

        scrollContainerRef.current.scrollBy({
            left:
                direction === 'left'
                    ? -scrollAmount
                    : scrollAmount,
            behavior: 'smooth',
        });
    };

    if (!articles || articles.length === 0) {
        return null;
    }

    return (
        <section className="w-full my-10">

            {/* Header */}
            <div className="flex items-center justify-between mb-4 px-1">

                <div className="flex items-center gap-2">
                    <span
                        className="
                            w-2.5 h-6 rounded-full
                            bg-emerald-600 dark:bg-emerald-500
                        "
                    />

                    <h2
                        className="
                            text-xl sm:text-2xl
                            font-black tracking-tight
                            text-emerald-800 dark:text-emerald-400
                        "
                    >
                        {sectionSlug ? (
                            <Link
                                href={`/news/category/${sectionSlug}`}
                                className="hover:underline"
                            >
                                {sectionTitle}
                            </Link>
                        ) : (
                            sectionTitle
                        )}
                    </h2>
                </div>

                {/* Arrow Controls */}
                <div className="flex items-center gap-2">

                    <button
                        type="button"
                        onClick={() => handleScroll('left')}
                        aria-label="Scroll left"
                        className="
                            w-9 h-9 rounded-full
                            bg-slate-100 dark:bg-slate-800
                            border border-slate-200 dark:border-slate-700/80
                            flex items-center justify-center
                            text-slate-700 dark:text-slate-300
                            hover:bg-emerald-600 hover:text-white
                            dark:hover:bg-emerald-500
                            hover:border-emerald-600
                            transition-all duration-200
                            cursor-pointer
                        "
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>

                    <button
                        type="button"
                        onClick={() => handleScroll('right')}
                        aria-label="Scroll right"
                        className="
                            w-9 h-9 rounded-full
                            bg-slate-100 dark:bg-slate-800
                            border border-slate-200 dark:border-slate-700/80
                            flex items-center justify-center
                            text-slate-700 dark:text-slate-300
                            hover:bg-emerald-600 hover:text-white
                            dark:hover:bg-emerald-500
                            hover:border-emerald-600
                            transition-all duration-200
                            cursor-pointer
                        "
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>

                </div>
            </div>

            {/* Horizontal Scroll Track */}
            <div
                ref={scrollContainerRef}
                className="
                    flex items-stretch gap-5
                    overflow-x-auto
                    scrollbar-none
                    py-2 px-1
                    snap-x scroll-smooth
                "
                style={{
                    scrollbarWidth: 'none',
                    msOverflowStyle: 'none',
                }}
            >
                {articles.map((article) => {

                    const articleUrl =
                        `${basePath}/${article.slug}`;

                    const imageUrl =
                        article.thumbnail_url ||
                        '/images/default-news.jpg';

                    return (
                        <article
                            key={article.id}
                            className="
                                group flex flex-col
                                w-[260px] sm:w-[280px] md:w-[300px]
                                shrink-0
                                bg-white dark:bg-slate-900
                                border border-slate-200/80
                                dark:border-slate-800
                                rounded-2xl overflow-hidden
                                shadow-xs hover:shadow-xl
                                transition-all duration-300
                                snap-start
                            "
                        >

                            {/* Card Image */}
                            <Link
                                href={articleUrl}
                                aria-label={`Read ${article.title}`}
                                className="
                                    relative block w-full aspect-16/10
                                    overflow-hidden
                                    bg-slate-100 dark:bg-slate-800
                                "
                            >
                                <Image
                                    src={imageUrl}
                                    alt={article.title}
                                    fill
                                    unoptimized
                                    sizes="
                                        (max-width: 640px) 260px,
                                        (max-width: 768px) 280px,
                                        300px
                                    "
                                    className="
                                        object-cover
                                        transition-transform duration-500
                                        group-hover:scale-105
                                    "
                                />
                            </Link>

                            {/* Card Content */}
                            <div
                                className="
                                    p-4
                                    flex flex-col
                                    justify-between
                                    flex-1
                                "
                            >
                                <div>

                                    {/* Category */}
                                    <Link
                                        href={`/news/category/${article.category.slug}`}
                                        className="
                                            inline-block
                                            text-[11px]
                                            font-black
                                            uppercase
                                            tracking-wider
                                            text-amber-600
                                            dark:text-amber-500
                                            mb-2
                                            hover:underline
                                        "
                                    >
                                        {article.category.name}
                                    </Link>

                                    {/* Article Title */}
                                    <h3
                                        className="
                                            text-sm sm:text-base
                                            font-bold
                                            text-slate-900
                                            dark:text-slate-100
                                            leading-snug
                                            group-hover:text-emerald-600
                                            dark:group-hover:text-emerald-400
                                            transition-colors duration-200
                                            line-clamp-3
                                        "
                                    >
                                        <Link href={articleUrl}>
                                            {article.title}
                                        </Link>
                                    </h3>

                                </div>

                                {/* Footer */}
                                <div
                                    className="
                                        mt-4 pt-3
                                        border-t
                                        border-slate-100
                                        dark:border-slate-800/80
                                        flex items-center
                                        justify-between
                                        text-xs font-semibold
                                        text-slate-500
                                        dark:text-slate-400
                                    "
                                >
                                    {article.friendly_date ? (
                                        <span>
                                            {article.friendly_date}
                                        </span>
                                    ) : (
                                        <Link
                                            href={articleUrl}
                                            className="
                                                flex items-center gap-1
                                                text-emerald-600
                                                dark:text-emerald-400
                                                font-bold
                                                group-hover:translate-x-1
                                                transition-transform
                                                duration-200
                                            "
                                        >
                                            Read Story
                                            <ArrowRight
                                                className="w-3.5 h-3.5"
                                            />
                                        </Link>
                                    )}
                                </div>

                            </div>
                        </article>
                    );
                })}
            </div>

        </section>
    );
}