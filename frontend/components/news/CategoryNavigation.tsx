'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    ChevronRight,
    Cpu,
    Film,
    GraduationCap,
    Landmark,
    Leaf,
    MessageSquare,
    Music,
    Trophy,
    Vote,
    Calendar,
} from 'lucide-react';

export interface CategoryItem {
    name: string;
    slug: string;
    icon: React.ReactNode;
    basePath: string;
}

/* =========================================================
   NEWS CATEGORIES
========================================================= */

const NEWS_CATEGORIES: CategoryItem[] = [
    {
        name: 'Politics',
        slug: 'politics',
        icon: <Vote className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Entertainment',
        slug: 'entertainment',
        icon: <Film className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Business',
        slug: 'business',
        icon: <Landmark className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Lifestyle',
        slug: 'lifestyle',
        icon: <Leaf className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Technology',
        slug: 'technology',
        icon: <Cpu className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Sports',
        slug: 'sports',
        icon: <Trophy className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Music News',
        slug: 'music-news',
        icon: <Music className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Events',
        slug: 'events',
        icon: <Calendar className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Education',
        slug: 'education',
        icon: <GraduationCap className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Opinion',
        slug: 'opinion',
        icon: <MessageSquare className="w-5 h-5" />,
        basePath: '/news',
    },
];

/* =========================================================
   NEWS CATEGORY NAVIGATION
========================================================= */

export default function CategoryNavigation() {
    const pathname = usePathname();

    const scrollRef = useRef<HTMLDivElement>(null);

    const [canScrollRight, setCanScrollRight] = useState(true);

    const checkScroll = () => {
        if (!scrollRef.current) return;

        const {
            scrollLeft,
            scrollWidth,
            clientWidth,
        } = scrollRef.current;

        setCanScrollRight(
            scrollLeft + clientWidth < scrollWidth - 12
        );
    };

    useEffect(() => {
        const element = scrollRef.current;

        if (!element) return;

        checkScroll();

        element.addEventListener('scroll', checkScroll);
        window.addEventListener('resize', checkScroll);

        return () => {
            element.removeEventListener(
                'scroll',
                checkScroll
            );

            window.removeEventListener(
                'resize',
                checkScroll
            );
        };
    }, []);

    return (
        <nav
            aria-label="News category navigation"
            className="my-6 w-full"
        >
            <div
                className="
                    relative w-full
                    rounded-2xl
                    border border-slate-200/80
                    bg-slate-100/80
                    p-3
                    shadow-xs
                    backdrop-blur-md
                    dark:border-slate-800
                    dark:bg-slate-900/60
                    sm:p-4
                "
            >
                {/* Category Track */}
                <div
                    ref={scrollRef}
                    className="
                        flex items-center
                        gap-3
                        overflow-x-auto
                        px-1 py-1
                        snap-x
                        scroll-smooth
                        scrollbar-none
                        sm:gap-4
                        lg:justify-between
                        lg:gap-2
                    "
                    style={{
                        scrollbarWidth: 'none',
                        msOverflowStyle: 'none',
                    }}
                >
                    {NEWS_CATEGORIES.map((category) => {
                        const targetHref =
                            `${category.basePath}/${category.slug}`;

                        const isActive =
                            pathname === targetHref;

                        return (
                            <Link
                                key={`${category.basePath}-${category.slug}`}
                                href={targetHref}
                                aria-current={
                                    isActive
                                        ? 'page'
                                        : undefined
                                }
                                className="
                                    group
                                    flex shrink-0 snap-start
                                    flex-col items-center
                                    gap-2
                                    transition-all
                                    duration-200
                                    focus:outline-hidden
                                    lg:shrink
                                "
                            >
                                {/* Icon */}
                                <div
                                    className={`
                                        flex
                                        h-12 w-12
                                        items-center
                                        justify-center
                                        rounded-2xl
                                        shadow-xs
                                        transition-all
                                        duration-300
                                        sm:h-14 sm:w-14

                                        ${
                                            isActive
                                                ? `
                                                    scale-105
                                                    bg-rose-500
                                                    text-white
                                                    shadow-lg
                                                    shadow-rose-500/25
                                                `
                                                : `
                                                    border
                                                    border-slate-200/60
                                                    bg-white
                                                    text-slate-600

                                                    group-hover:scale-105
                                                    group-hover:border-rose-500/50
                                                    group-hover:text-rose-500
                                                    group-hover:shadow-md

                                                    dark:border-slate-700/60
                                                    dark:bg-slate-800
                                                    dark:text-slate-300
                                                    dark:group-hover:border-rose-500/50
                                                    dark:group-hover:text-rose-400
                                                `
                                        }
                                    `}
                                >
                                    {category.icon}
                                </div>

                                {/* Category Name */}
                                <span
                                    className={`
                                        whitespace-nowrap
                                        text-center
                                        text-[11px]
                                        font-bold
                                        tracking-tight
                                        transition-colors
                                        duration-200
                                        sm:text-xs

                                        ${
                                            isActive
                                                ? `
                                                    font-extrabold
                                                    text-rose-600
                                                    dark:text-rose-400
                                                `
                                                : `
                                                    text-slate-700
                                                    group-hover:text-rose-600
                                                    dark:text-slate-300
                                                    dark:group-hover:text-rose-400
                                                `
                                        }
                                    `}
                                >
                                    {category.name}
                                </span>
                            </Link>
                        );
                    })}
                </div>

                {/* Mobile Scroll Cue */}
                {canScrollRight && (
                    <div
                        className="
                            pointer-events-none
                            absolute
                            right-0
                            top-0
                            bottom-0
                            flex w-14
                            items-center
                            justify-end
                            rounded-r-2xl
                            bg-gradient-to-l
                            from-slate-100
                            to-transparent
                            pr-2
                            transition-opacity
                            duration-300
                            lg:hidden
                            dark:from-slate-900
                        "
                    >
                        <div
                            className="
                                flex
                                h-6 w-6
                                items-center
                                justify-center
                                rounded-full
                                bg-slate-900/10
                                text-slate-600
                                backdrop-blur-xs
                                animate-pulse
                                dark:bg-white/10
                                dark:text-slate-300
                            "
                        >
                            <ChevronRight className="h-4 w-4" />
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}