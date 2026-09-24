'use client';

import Link from 'next/link';

import ThemeToggle from '@/components/ThemeToggle';
import { HomeIcon } from '@/components/Icons';

export default function HomeNav() {
  return (
    <header
      className="
        border-b
        border-light-border
        bg-light-surface
        dark:border-dark-border
        dark:bg-dark-surface
      "
    >
      <div
        className="
          mx-auto flex w-full max-w-6xl
          items-center justify-between
          px-4 py-4
          sm:px-6
          lg:px-8
        "
      >
        {/* Logo */}
        <Link
          href="/"
          className="inline-flex items-center"
          aria-label="VibeNationHQ home"
        >
          <span
            className="
              text-xl font-black tracking-tight
              text-light-text
              dark:text-dark-text
            "
          >
            VibeNation
            <span className="text-brand-teal">
              HQ
            </span>
          </span>
        </Link>

        {/* Navigation actions */}
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="
              hidden h-10 items-center gap-2
              rounded-lg
              px-3
              text-sm font-semibold
              text-light-text-muted
              transition-colors
              hover:bg-light-surface-soft
              hover:text-light-text
              dark:text-dark-text-muted
              dark:hover:bg-dark-surface-soft
              dark:hover:text-dark-text
              sm:inline-flex
            "
          >
            <HomeIcon className="h-4 w-4" />
            Home
          </Link>

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}