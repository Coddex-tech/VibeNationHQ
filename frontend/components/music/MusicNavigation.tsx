'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Compass,
  Search,
  Sparkles,
  UserRound,
} from 'lucide-react';

type MusicNavigationItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{
    className?: string;
  }>;
};

const musicNavigationItems: MusicNavigationItem[] = [
  {
    href: '/music',
    label: 'Explore',
    icon: Compass,
  },
  {
    href: '/music/discover',
    label: 'Discover',
    icon: Sparkles,
  },
  {
    href: '/music/search',
    label: 'Search',
    icon: Search,
  },
  {
    href: '/account',
    label: 'You',
    icon: UserRound,
  },
];

function isMusicNavigationItemActive(
  pathname: string,
  href: string,
): boolean {
  if (href === '/music') {
    return pathname === '/music';
  }

  if (href === '/account') {
    return pathname.startsWith('/account');
  }

  return (
    pathname === href ||
    pathname.startsWith(`${href}/`)
  );
}

export default function MusicNavigation() {
  const pathname = usePathname();

  return (
    <nav
      className="
        border-b
        border-light-border-soft
        bg-light-surface
        dark:border-dark-border-soft
        dark:bg-dark-surface
      "
      aria-label="Music navigation"
    >
      <div
        className="
          mx-auto
          flex w-full max-w-7xl
          items-center justify-center
          px-4
          sm:px-6
          lg:px-8
        "
      >
        <div
          className="
            flex
            items-center
            justify-center
            gap-10
            py-3
            sm:gap-5
            sm:py-3.5
            lg:gap-7
          "
        >
          {musicNavigationItems.map((item) => {
            const Icon = item.icon;

            const active =
              isMusicNavigationItemActive(
                pathname,
                item.href,
              );

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-label={item.label}
                aria-current={
                  active ? 'page' : undefined
                }
                className={`
                  group
                  relative
                  inline-flex
                  h-11
                  min-w-11
                  items-center
                  justify-center
                  rounded-xl
                  px-2.5
                  transition-all duration-200
                  focus:outline-none
                  focus-visible:ring-4
                  focus-visible:ring-brand-teal/15

                  sm:h-10
                  sm:min-w-0
                  sm:gap-2
                  sm:px-3.5

                  ${
                    active
                      ? `
                        bg-brand-teal/10
                        text-brand-teal-dark
                        dark:bg-brand-teal/15
                        dark:text-brand-teal-light
                      `
                      : `
                        text-light-text-muted
                        hover:bg-light-surface-soft
                        hover:text-light-text
                        dark:text-dark-text-muted
                        dark:hover:bg-dark-surface-soft
                        dark:hover:text-dark-text
                      `
                  }
                `}
              >
                <Icon
                  className={`
                    h-[19px] w-[19px]
                    shrink-0
                    transition-transform duration-200
                    ${
                      active
                        ? 'text-brand-teal'
                        : 'group-hover:scale-[1.03]'
                    }
                  `}
                  strokeWidth={active ? 2.2 : 1.9}
                />

                {/* Desktop labels */}
                <span
                  className="
                    hidden
                    text-sm
                    font-semibold
                    sm:inline
                  "
                >
                  {item.label}
                </span>

                {/* Active indicator */}
                {active && (
                  <span
                    className="
                      absolute
                      bottom-0
                      left-1/2
                      h-0.5
                      w-6
                      -translate-x-1/2
                      rounded-full
                      bg-brand-teal
                    "
                    aria-hidden="true"
                  />
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}