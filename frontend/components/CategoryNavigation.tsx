'use client';

import { useRef, useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Film,
    Landmark,
    Leaf,
    Cpu,
    Trophy,
    Music,
    Calendar,
    GraduationCap,
    MessageSquare,
    Flame,
    Disc,
    Headphones,
    Globe2,
    Church,
    ChevronRight,
    Sparkles,
    Vote,
} from 'lucide-react';

export interface CategoryItem {
    name: string;
    slug: string;
    icon: React.ReactNode;
    basePath: string;
}

/* =========================================================
   NEWS CATEGORIES
   Used throughout /news/*
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
   MUSIC CATEGORIES
   Used throughout /music/*
========================================================= */

const MUSIC_CATEGORIES: CategoryItem[] = [
    {
        name: 'Latest Music',
        slug: 'latest-music',
        icon: <Music className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Gospel',
        slug: 'gospel',
        icon: <Church className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Trending',
        slug: 'trending',
        icon: <Flame className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Albums',
        slug: 'albums',
        icon: <Disc className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'DJ Mix',
        slug: 'dj-mix',
        icon: <Headphones className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'African Music',
        slug: 'african-music',
        icon: <Globe2 className="w-5 h-5" />,
        basePath: '/music/category',
    },
];

/* =========================================================
   HOMEPAGE CATEGORIES
   Curated selection shown on /
========================================================= */

const HOMEPAGE_CATEGORIES: CategoryItem[] = [
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
        name: 'Latest Music',
        slug: 'latest-music',
        icon: <Music className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Trending',
        slug: 'trending',
        icon: <Flame className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Sports',
        slug: 'sports',
        icon: <Trophy className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'African Music',
        slug: 'african-music',
        icon: <Globe2 className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Celebrity Gossip',
        slug: 'celebrity-gossip',
        icon: <Sparkles className="w-5 h-5" />,
        basePath: '/news',
    },
    {
        name: 'Gospel',
        slug: 'gospel',
        icon: <Church className="w-5 h-5" />,
        basePath: '/music/category',
    },
    {
        name: 'Music News',
        slug: 'music-news',
        icon: <Music className="w-5 h-5" />,
        basePath: '/news',
    },
];

/* =========================================================
   CATEGORY CONFIGURATION
========================================================= */

const CATEGORY_CONFIG = {
    homepage: HOMEPAGE_CATEGORIES,
    news: NEWS_CATEGORIES,
    music: MUSIC_CATEGORIES,
} as const;

interface CategoryNavigationProps {
    mode?: keyof typeof CATEGORY_CONFIG;
}

export default function CategoryNavigation({
    mode = 'homepage',
}: CategoryNavigationProps) {
    const pathname = usePathname();

    const scrollRef = useRef<HTMLDivElement>(null);

    const [canScrollRight, setCanScrollRight] = useState(true);

    const categories = CATEGORY_CONFIG[mode];

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
            element.removeEventListener('scroll', checkScroll);
            window.removeEventListener('resize', checkScroll);
        };
    }, [mode]);

    return (
        <nav
            aria-label="Category Navigation"
            className="w-full my-6"
        >
            <div
                className="
                    relative w-full
                    bg-slate-100/80 dark:bg-slate-900/60
                    border border-slate-200/80 dark:border-slate-800
                    rounded-2xl
                    p-3 sm:p-4
                    shadow-xs
                    backdrop-blur-md
                "
            >
                {/* Category Track */}
                <div
                    ref={scrollRef}
                    className="
                        flex items-center
                        gap-3 sm:gap-4 lg:gap-2
                        lg:justify-between
                        overflow-x-auto
                        scrollbar-none
                        py-1 px-1
                        snap-x
                        scroll-smooth
                    "
                    style={{
                        scrollbarWidth: 'none',
                        msOverflowStyle: 'none',
                    }}
                >
                    {categories.map((category) => {
                        const targetHref =
                            `${category.basePath}/${category.slug}`;

                        const isActive =
                            pathname === targetHref;

                        return (
                            <Link
                                key={`${category.basePath}-${category.slug}`}
                                href={targetHref}
                                className="
                                    group
                                    flex flex-col
                                    items-center
                                    gap-2
                                    shrink-0 lg:shrink
                                    snap-start
                                    transition-all duration-200
                                    focus:outline-hidden
                                "
                            >
                                {/* Icon */}
                                <div
                                    className={`
                                        w-12 h-12
                                        sm:w-14 sm:h-14
                                        rounded-2xl
                                        flex items-center justify-center
                                        transition-all duration-300
                                        shadow-xs

                                        ${isActive
                                            ? `
                                                    bg-rose-500
                                                    text-white
                                                    shadow-rose-500/25
                                                    shadow-lg
                                                    scale-105
                                                `
                                            : `
                                                    bg-white
                                                    dark:bg-slate-800
                                                    text-slate-600
                                                    dark:text-slate-300
                                                    border
                                                    border-slate-200/60
                                                    dark:border-slate-700/60
                                                    group-hover:border-rose-500/50
                                                    dark:group-hover:border-rose-500/50
                                                    group-hover:text-rose-500
                                                    dark:group-hover:text-rose-400
                                                    group-hover:shadow-md
                                                    group-hover:scale-105
                                                `
                                        }
                                    `}
                                >
                                    {category.icon}
                                </div>

                                {/* Category Name */}
                                <span
                                    className={`
                                        text-[11px]
                                        sm:text-xs
                                        font-bold
                                        tracking-tight
                                        text-center
                                        whitespace-nowrap
                                        transition-colors duration-200

                                        ${isActive
                                            ? `
                                                    text-rose-600
                                                    dark:text-rose-400
                                                    font-extrabold
                                                `
                                            : `
                                                    text-slate-700
                                                    dark:text-slate-300
                                                    group-hover:text-rose-600
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
                            lg:hidden
                            pointer-events-none
                            absolute
                            right-0
                            top-0
                            bottom-0
                            w-14
                            rounded-r-2xl
                            bg-gradient-to-l
                            from-slate-100
                            dark:from-slate-900
                            to-transparent
                            flex items-center
                            justify-end
                            pr-2
                            transition-opacity duration-300
                        "
                    >
                        <div
                            className="
                                w-6 h-6
                                rounded-full
                                bg-slate-900/10
                                dark:bg-white/10
                                backdrop-blur-xs
                                flex items-center justify-center
                                text-slate-600
                                dark:text-slate-300
                                animate-pulse
                            "
                        >
                            <ChevronRight className="w-4 h-4" />
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}