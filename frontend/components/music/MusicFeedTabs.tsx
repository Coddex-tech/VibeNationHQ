'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Compass,
  Users,
} from 'lucide-react';

type MusicFeedTabsProps = {
  activeTab?: 'for-you' | 'following';
};

const tabs = [
  {
    key: 'for-you' as const,
    label: 'For You',
    href: '/music',
    icon: Compass,
  },
  {
    key: 'following' as const,
    label: 'Following',
    href: '/music?feed=following',
    icon: Users,
  },
];

export default function MusicFeedTabs({
  activeTab,
}: MusicFeedTabsProps) {
  const pathname = usePathname();

  const currentTab =
    activeTab ??
    (pathname === '/music' ? 'for-you' : 'for-you');

  return (
    <nav
      aria-label="Music feed"
      className="
        border-b
        border-light-border-soft
        bg-light-bg/95
        backdrop-blur-md
        dark:border-dark-border-soft
        dark:bg-dark-bg/95
      "
    >
      <div
        className="
          mx-auto flex w-full max-w-3xl
          items-center
          px-4
          sm:px-6
        "
      >
        <div
          className="
            flex w-full
            items-center justify-center
            gap-1
          "
        >
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.key;

            return (
              <Link
                key={tab.key}
                href={tab.href}
                aria-current={
                  isActive ? 'page' : undefined
                }
                className={`
                  group relative
                  flex min-h-12
                  flex-1
                  items-center justify-center
                  gap-2
                  px-4
                  text-sm font-semibold
                  transition-colors duration-200
                  focus:outline-none
                  focus-visible:ring-4
                  focus-visible:ring-brand-teal/15
                  sm:flex-none
                  sm:min-w-32

                  ${
                    isActive
                      ? `
                        text-brand-teal-dark
                        dark:text-brand-teal-light
                      `
                      : `
                        text-light-text-muted
                        hover:text-light-text
                        dark:text-dark-text-muted
                        dark:hover:text-dark-text
                      `
                  }
                `}
              >
                <Icon
                  className={`
                    h-[17px] w-[17px]
                    shrink-0
                    transition-transform duration-200
                    ${
                      isActive
                        ? 'text-brand-teal'
                        : 'group-hover:scale-[1.03]'
                    }
                  `}
                  strokeWidth={isActive ? 2.2 : 1.9}
                />

                <span>{tab.label}</span>

                <span
                  className={`
                    absolute
                    bottom-0 left-1/2
                    h-0.5
                    -translate-x-1/2
                    rounded-full
                    bg-brand-teal
                    transition-all duration-200
                    ${
                      isActive
                        ? 'w-10 opacity-100'
                        : 'w-0 opacity-0'
                    }
                  `}
                  aria-hidden="true"
                />
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}