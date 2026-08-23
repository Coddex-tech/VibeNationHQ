'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import { useState, FormEvent } from 'react';
import ThemeToggle from './ThemeToggle';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'News', href: '/news' },
    { name: 'Music', href: '/music' },
  ];

  const handleSearch = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const query = searchQuery.trim();

    if (!query) return;

    router.push(`/search?q=${encodeURIComponent(query)}`);
    setSearchQuery('');
    setMobileMenuOpen(false);
  };

  const isActiveLink = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }

    return pathname === href || pathname.startsWith(`${href}/`);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#032b2b]/95 text-white shadow-lg backdrop-blur-xl">
      <div className="mx-auto w-full max-w-7xl px-3 sm:px-5 lg:px-8">

        {/* =====================================================
            MAIN NAVBAR ROW
        ====================================================== */}
        <div className="flex min-h-14 items-center justify-between gap-3 sm:min-h-20">

          {/* LOGO */}
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="flex shrink-0 items-center"
            aria-label="VibeNationHQ home"
          >
            <Image
              src="/vibenation_nav_logo.png"
              alt="VibeNationHQ"
              width={180}
              height={50}
              priority
              className="h-8 w-auto object-contain sm:h-10"
            />
          </Link>

          {/* =================================================
              DESKTOP NAVIGATION
          ================================================== */}
          <nav
            aria-label="Primary navigation"
            className="hidden items-center gap-5 md:flex lg:gap-7"
          >
            {navLinks.map((link) => {
              const active = isActiveLink(link.href);

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  aria-current={active ? 'page' : undefined}
                  className={`
                    relative whitespace-nowrap py-2 text-sm font-semibold
                    transition-colors duration-200
                    lg:text-base
                    ${active
                      ? 'text-[#00c99b]'
                      : 'text-white/90 hover:text-[#00c99b]'
                    }
                  `}
                >
                  {link.name}

                  {/* Active indicator */}
                  <span
                    className={`
                      absolute bottom-0 left-0 h-0.5 rounded-full
                      bg-[#00a884] transition-all duration-200
                      ${active ? 'w-full' : 'w-0'}
                    `}
                  />
                </Link>
              );
            })}
          </nav>

          {/* =================================================
              DESKTOP SEARCH + THEME
          ================================================== */}
          <div className="hidden items-center gap-3 md:flex lg:gap-4">

            <form
              onSubmit={handleSearch}
              role="search"
              className="flex items-center gap-2"
            >
              <label htmlFor="desktop-search" className="sr-only">
                Search VibeNationHQ
              </label>

              <input
                id="desktop-search"
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search artists, songs & news..."
                autoComplete="off"
                className="
                  h-9 w-48 rounded-lg
                  border border-white/10
                  bg-white px-3
                  text-sm text-slate-900
                  placeholder:text-slate-500
                  shadow-sm
                  outline-none
                  transition-all
                  focus:border-[#00a884]
                  focus:ring-2
                  focus:ring-[#00a884]/30
                  lg:w-60
                  xl:w-72
                "
              />

              <button
                type="submit"
                className="
                  h-9 shrink-0 rounded-lg
                  bg-[#00a884] px-4
                  text-sm font-semibold text-white
                  shadow-sm
                  transition-all duration-200
                  hover:bg-[#00bd98]
                  active:scale-95
                  focus:outline-none
                  focus:ring-2
                  focus:ring-[#00a884]/50
                  focus:ring-offset-2
                  focus:ring-offset-[#032b2b]
                "
              >
                Search
              </button>
            </form>

            <ThemeToggle />
          </div>

          {/* =================================================
              MOBILE CONTROLS
          ================================================== */}
          <div className="flex shrink-0 items-center gap-1 md:hidden">

            <ThemeToggle />

            <button
              type="button"
              aria-label={
                mobileMenuOpen
                  ? 'Close navigation menu'
                  : 'Open navigation menu'
              }
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-navigation"
              onClick={() => setMobileMenuOpen((open) => !open)}
              className="
                flex h-9 w-9 items-center justify-center
                rounded-lg
                text-white
                transition-colors duration-200
                hover:bg-white/10
                focus:outline-none
                focus:ring-2
                focus:ring-[#00a884]/60
              "
            >
              {mobileMenuOpen ? (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* =====================================================
            MOBILE SEARCH
            Always visible — intentionally outside the menu.
        ====================================================== */}
        <div className="pb-3 md:hidden">
          <form
            onSubmit={handleSearch}
            role="search"
            className="flex w-full items-center gap-2"
          >
            <label htmlFor="mobile-search" className="sr-only">
              Search VibeNationHQ
            </label>

            <div className="relative min-w-0 flex-1">
              <svg
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m21 21-4.35-4.35m2.1-5.4a7.5 7.5 0 11-15 0 7.5 7.5 0 0115 0z"
                />
              </svg>

              <input
                id="mobile-search"
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search artists, songs & news..."
                autoComplete="off"
                className="
                  h-10 w-full rounded-lg
                  border border-white/10
                  bg-white
                  pl-9 pr-3
                  text-sm text-slate-900
                  placeholder:text-slate-500
                  outline-none
                  transition-all
                  focus:border-[#00a884]
                  focus:ring-2
                  focus:ring-[#00a884]/30
                "
              />
            </div>

            <button
              type="submit"
              className="
                h-10 shrink-0
                rounded-lg
                bg-[#00a884]
                px-3.5
                text-sm font-semibold text-white
                transition-all duration-200
                hover:bg-[#00bd98]
                active:scale-95
                focus:outline-none
                focus:ring-2
                focus:ring-[#00a884]/50
              "
            >
              Search
            </button>
          </form>
        </div>

        {/* =====================================================
            MOBILE NAVIGATION MENU
        ====================================================== */}
        <div
          id="mobile-navigation"
          className={`
            overflow-hidden transition-all duration-300 ease-in-out md:hidden
            ${mobileMenuOpen
              ? 'max-h-96 border-t border-white/10 opacity-100'
              : 'max-h-0 opacity-0'
            }
          `}
        >
          <nav
            aria-label="Mobile navigation"
            className="flex flex-col gap-1 py-3"
          >
            {navLinks.map((link) => {
              const active = isActiveLink(link.href);

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  aria-current={active ? 'page' : undefined}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`
                    flex min-h-11 items-center rounded-lg px-3
                    text-sm font-semibold
                    transition-colors duration-200
                    ${active
                      ? 'bg-[#00a884]/15 text-[#00d6a4]'
                      : 'text-white/90 hover:bg-white/5 hover:text-[#00c99b]'
                    }
                  `}
                >
                  {link.name}
                </Link>
              );
            })}
          </nav>
        </div>

      </div>
    </header>
  );
}