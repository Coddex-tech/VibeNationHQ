'use client';

import { useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';

export interface CarouselNewsItem {
    id: number;
    title: string;
    slug: string;
    category_name?: string;
    friendly_date?: string;
    thumbnail_url?: string;
    thumbnail?: string;
}

interface HorizontalNewsCarouselProps {
    categoryTitle?: string;
    newsList: CarouselNewsItem[];
}

export default function HorizontalNewsCarousel({
    categoryTitle,
    newsList = [],
}: HorizontalNewsCarouselProps) {
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    if (!newsList || newsList.length === 0) return null;

    const handleScroll = (direction: 'left' | 'right') => {
        if (!scrollContainerRef.current) return;
        const scrollAmount = scrollContainerRef.current.clientWidth * 0.75;
        scrollContainerRef.current.scrollBy({
            left: direction === 'left' ? -scrollAmount : scrollAmount,
            behavior: 'smooth',
        });
    };

    const getNewsImg = (item: CarouselNewsItem) =>
        item.thumbnail_url || item.thumbnail || '/images/default-news.jpg';

    return (
        <section className="w-full my-8 px-2 sm:px-4">
            {/* Category Header */}
            {categoryTitle && (
                <div className="flex items-center gap-2 mb-4">
                    <span className="w-2.5 h-2.5 rounded-full bg-teal-600 dark:bg-teal-400 shrink-0" />
                    <h2 className="text-xl sm:text-2xl font-black text-teal-900 dark:text-teal-400 tracking-tight">
                        {categoryTitle}
                    </h2>
                </div>
            )}

            {/* Carousel Container Wrapper */}
            <div className="relative group/carousel">

                {/* Left Navigation Arrow */}
                <button
                    onClick={() => handleScroll('left')}
                    aria-label="Scroll Left"
                    className="absolute -left-2 sm:-left-4 top-1/2 -translate-y-1/2 z-20 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-teal-700 hover:bg-teal-800 text-white flex items-center justify-center shadow-lg transition-all duration-200 opacity-90 hover:opacity-100 hover:scale-105 active:scale-95 border border-white/20"
                >
                    <svg
                        className="w-5 h-5 stroke-[2.5]"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                    </svg>
                </button>

                {/* Scrollable Track */}
                <div
                    ref={scrollContainerRef}
                    className="flex gap-3 sm:gap-4 overflow-x-auto scrollbar-none snap-x snap-mandatory py-2 px-1 scroll-smooth"
                    style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                >
                    {newsList.map((item) => (
                        <div
                            key={`${item.id}-${item.slug}`}
                            className="snap-start shrink-0 w-[45%] sm:w-[30%] lg:w-[23.5%] min-w-[160px] sm:min-w-[220px]"
                        >
                            <Link
                                href={`/news/${item.slug}`}
                                className="group/card flex flex-col h-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 overflow-hidden shadow-xs hover:shadow-md transition-all duration-300"
                            >
                                {/* Thumbnail */}
                                <div className="relative w-full h-32 sm:h-44 bg-slate-100 dark:bg-slate-800 overflow-hidden">
                                    <Image
                                        src={getNewsImg(item)}
                                        alt={item.title}
                                        fill
                                        unoptimized
                                        sizes="(max-width: 640px) 45vw, (max-width: 1024px) 30vw, 25vw"
                                        className="object-cover transition-transform duration-500 group-hover/card:scale-105"
                                    />
                                </div>

                                {/* Content Details */}
                                <div className="flex flex-col justify-between flex-1 p-3 sm:p-4">
                                    <div>
                                        {item.category_name && (
                                            <span className="text-[10px] sm:text-[11px] font-extrabold text-teal-600 dark:text-teal-400 uppercase tracking-wider mb-1 block">
                                                {item.category_name}
                                            </span>
                                        )}
                                        <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 group-hover/card:text-teal-600 dark:group-hover/card:text-teal-400 transition-colors line-clamp-3 sm:line-clamp-2 leading-snug">
                                            {item.title}
                                        </h3>
                                    </div>

                                    {item.friendly_date && (
                                        <p className="text-[10px] sm:text-[11px] font-medium text-slate-400 dark:text-slate-500 mt-2 sm:mt-3">
                                            {item.friendly_date}
                                        </p>
                                    )}
                                </div>
                            </Link>
                        </div>
                    ))}
                </div>

                {/* Right Navigation Arrow */}
                <button
                    onClick={() => handleScroll('right')}
                    aria-label="Scroll Right"
                    className="absolute -right-2 sm:-right-4 top-1/2 -translate-y-1/2 z-20 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-teal-700 hover:bg-teal-800 text-white flex items-center justify-center shadow-lg transition-all duration-200 opacity-90 hover:opacity-100 hover:scale-105 active:scale-95 border border-white/20"
                >
                    <svg
                        className="w-5 h-5 stroke-[2.5]"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                </button>

            </div>
        </section>
    );
}