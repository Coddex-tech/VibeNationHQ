'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  Bell,
  Heart,
  Home,
  LogIn,
  LogOut,
  Menu,
  Music2,
  Newspaper,
  UserRound,
  X,
} from 'lucide-react';
import { useEffect, useState } from 'react';

import ThemeToggle from '@/components/ThemeToggle';
import ConfirmationModal from '../ui/ConfirmationModal';
import { useAuth } from '@/components/auth/AuthProvider';
import {
  ApiError,
  apiRequest,
  getMediaUrl,
} from '@/lib/api';

type NavItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{
    className?: string;
  }>;
};

const navItems: NavItem[] = [
  {
    href: '/',
    label: 'Home',
    icon: Home,
  },
  {
    href: '/music',
    label: 'Music',
    icon: Music2,
  },
  {
    href: '/news',
    label: 'News',
    icon: Newspaper,
  },
];

const footerLinks = [
  {
    href: '/about',
    label: 'About Us',
  },
  {
    href: '/advertise',
    label: 'Advertise With Us',
  },
  {
    href: '/contact',
    label: 'Contact Us',
  },
  {
    href: '/privacy',
    label: 'Privacy Policy',
  },
  {
    href: '/services',
    label: 'Services',
  },
  {
    href: '/dmca',
    label: 'DMCA',
  },
];

function isNavItemActive(
  pathname: string,
  href: string,
): boolean {
  if (href === '/') {
    return pathname === '/';
  }

  return (
    pathname === href ||
    pathname.startsWith(`${href}/`)
  );
}

function getUserInitials(
  displayName: string,
  username: string,
): string {
  const name = displayName.trim();

  if (name) {
    const parts = name.split(/\s+/);

    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }

    return name.slice(0, 2).toUpperCase();
  }

  return username.slice(0, 2).toUpperCase();
}

export default function HomeNav() {
  const pathname = usePathname();
  const router = useRouter();

  const {
    user,
    isAuthenticated,
    isLoading,
  } = useAuth();

  const [isMenuOpen, setIsMenuOpen] =
    useState(false);

  const [isLogoutModalOpen, setIsLogoutModalOpen] =
    useState(false);

  const [isLoggingOut, setIsLoggingOut] =
    useState(false);

  const [logoutError, setLogoutError] =
    useState('');

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  const openLogoutModal = () => {
    setLogoutError('');
    setIsMenuOpen(false);
    setIsLogoutModalOpen(true);
  };

  const closeLogoutModal = () => {
    if (isLoggingOut) {
      return;
    }

    setIsLogoutModalOpen(false);
    setLogoutError('');
  };

  const handleLogout = async () => {
    if (isLoggingOut) {
      return;
    }

    setLogoutError('');
    setIsLoggingOut(true);

    try {
      await apiRequest<{
        message: string;
      }>('/api/accounts/logout/', {
        method: 'POST',
      });

      setIsLogoutModalOpen(false);

      router.push('/login');
    } catch (error) {
      if (error instanceof ApiError) {
        setLogoutError(
          error.data?.detail ??
            'Unable to log you out. Please try again.',
        );
      } else {
        setLogoutError(
          'Unable to log you out. Please try again.',
        );
      }
    } finally {
      setIsLoggingOut(false);
    }
  };

  useEffect(() => {
    closeMenu();
    setIsLogoutModalOpen(false);
    setLogoutError('');
  }, [pathname]);

  useEffect(() => {
    if (!isMenuOpen && !isLogoutModalOpen) {
      document.body.style.overflow = '';
      return;
    }

    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = '';
    };
  }, [isMenuOpen, isLogoutModalOpen]);

  useEffect(() => {
    if (!isMenuOpen && !isLogoutModalOpen) {
      return;
    }

    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      if (event.key !== 'Escape') {
        return;
      }

      if (isLogoutModalOpen) {
        closeLogoutModal();
        return;
      }

      closeMenu();
    };

    window.addEventListener(
      'keydown',
      handleKeyDown,
    );

    return () => {
      window.removeEventListener(
        'keydown',
        handleKeyDown,
      );
    };
  }, [
    isMenuOpen,
    isLogoutModalOpen,
    isLoggingOut,
  ]);

  return (
    <>
      <header
        className="
          sticky top-0 z-50
          border-b
          border-light-border/80
          bg-light-surface/95
          backdrop-blur-xl
          transition-colors duration-300
          dark:border-dark-border/80
          dark:bg-dark-surface/95
        "
      >
        <div
          className="
            mx-auto flex h-16 w-full max-w-7xl
            items-center
            gap-3
            px-4
            sm:px-6
            lg:px-8
          "
        >
          {/* Hamburger */}
          <button
            type="button"
            onClick={() => setIsMenuOpen(true)}
            aria-label="Open navigation menu"
            aria-expanded={isMenuOpen}
            className="
              inline-flex h-10 w-10
              shrink-0
              items-center justify-center
              rounded-lg
              text-light-text-muted
              transition-colors
              hover:bg-light-surface-soft
              hover:text-light-text
              focus:outline-none
              focus-visible:ring-4
              focus-visible:ring-brand-teal/15
              dark:text-dark-text-muted
              dark:hover:bg-dark-surface-soft
              dark:hover:text-dark-text
            "
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Brand */}
          <Link
            href="/"
            className="
              inline-flex shrink-0 items-center
              rounded-lg
              py-1
              focus:outline-none
              focus-visible:ring-4
              focus-visible:ring-brand-teal/15
            "
            aria-label="VibeNationHQ home"
          >
            <span
              className="
                text-xl font-black
                tracking-[-0.04em]
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

          <div className="min-w-0 flex-1" />

          {/* Desktop notification */}
          {!isLoading &&
            isAuthenticated === true && (
              <Link
                href="/notifications"
                aria-label="Notifications"
                className={`relative
                  inline-flex h-10 w-10
                  shrink-0
                  items-center justify-center
                  rounded-lg
                  transition-colors
                  focus:outline-none
                  focus-visible:ring-4
                  focus-visible:ring-brand-teal/15
                  ${
                    pathname.startsWith('/notifications')
                      ? `
                        bg-brand-teal/10
                        text-brand-teal
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
                <Bell className="h-[18px] w-[18px]" />
              </Link>
            )}

          {/* User profile picture */}
          {!isLoading &&
            isAuthenticated === true &&
            user && (
              <Link
                href={`/account/${encodeURIComponent(user.username)}`}
                aria-label={`View ${user.display_name || user.username}'s profile`}
                title={user.display_name || user.username}
                className="
                  relative
                  inline-flex h-10 w-10
                  shrink-0 items-center justify-center
                  overflow-hidden
                  rounded-full
                  border border-light-border
                  bg-light-surface-soft
                  text-sm font-bold
                  text-brand-teal
                  transition-all duration-200
                  hover:border-brand-teal
                  hover:ring-4
                  hover:ring-brand-teal/10
                  focus:outline-none
                  focus-visible:ring-4
                  focus-visible:ring-brand-teal/20
                  dark:border-dark-border
                  dark:bg-dark-surface-soft
                  dark:text-brand-teal-light
                "
              >
                {user.profile_image ? (
                  <Image
                    src={getMediaUrl(user.profile_image)}
                    alt={`${user.display_name || user.username}'s profile picture`}
                    fill
                    sizes="40px"
                    className="object-cover"
                  />
                ) : (
                  <span>
                    {getUserInitials(
                      user.display_name,
                      user.username,
                    )}
                  </span>
                )}
              </Link>
            )}

          {/* Theme */}
          <ThemeToggle />
        </div>
      </header>

      {/* Navigation drawer */}
      {isMenuOpen && (
        <div
          className="
            fixed inset-0 z-[100]
            bg-black/40
            backdrop-blur-[2px]
          "
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeMenu();
            }
          }}
        >
          <aside
            className="
              flex h-full
              w-full
              max-w-none
              flex-col
              border-r
              border-light-border
              bg-light-surface
              text-light-text
              shadow-2xl shadow-black/20
              dark:border-dark-border
              dark:bg-dark-surface
              dark:text-dark-text
              md:max-w-sm
            "
            role="dialog"
            aria-modal="true"
            aria-label="Navigation menu"
            onMouseDown={(event) => event.stopPropagation()}
          >
            {/* Drawer header */}
            <div
              className="
                flex h-16 shrink-0
                items-center justify-between
                border-b
                border-light-border
                px-4
                sm:px-6
                dark:border-dark-border
              "
            >
              <Link
                href="/"
                onClick={closeMenu}
                className="
                  inline-flex items-center
                  rounded-lg
                  py-1
                  focus:outline-none
                  focus-visible:ring-4
                  focus-visible:ring-brand-teal/15
                "
                aria-label="VibeNationHQ home"
              >
                <span
                  className="
                    text-xl font-black
                    tracking-[-0.04em]
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

              <button
                type="button"
                onClick={closeMenu}
                aria-label="Close navigation menu"
                className="
                  inline-flex h-10 w-10
                  items-center justify-center
                  rounded-lg
                  text-light-text-muted
                  transition-colors
                  hover:bg-light-surface-soft
                  hover:text-light-text
                  focus:outline-none
                  focus-visible:ring-4
                  focus-visible:ring-brand-teal/15
                  dark:text-dark-text-muted
                  dark:hover:bg-dark-surface-soft
                  dark:hover:text-dark-text
                "
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Drawer content */}
            <div
              className="
                flex flex-1
                flex-col
                overflow-y-auto
                px-4 py-6
                sm:px-6
              "
            >
              <nav
                className="mx-auto w-full max-w-lg"
                aria-label="Primary navigation"
              >
                <p
                  className="
                    px-3
                    text-[11px] font-bold
                    uppercase tracking-[0.12em]
                    text-light-text-soft
                    dark:text-dark-text-soft
                  "
                >
                  Explore VibeNationHQ
                </p>

                <div className="mt-3 space-y-1">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const active = isNavItemActive(
                      pathname,
                      item.href,
                    );

                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={closeMenu}
                        aria-current={
                          active ? 'page' : undefined
                        }
                        className={`
                          flex min-h-12
                          items-center gap-4
                          rounded-xl
                          px-3
                          text-base font-semibold
                          transition-colors
                          ${
                            active
                              ? `
                                bg-brand-teal/10
                                text-brand-teal-dark
                                dark:bg-brand-teal/15
                                dark:text-brand-teal-light
                              `
                              : `
                                text-light-text
                                hover:bg-light-surface-soft
                                dark:text-dark-text
                                dark:hover:bg-dark-surface-soft
                              `
                          }
                        `}
                      >
                        <span
                          className={`
                            flex h-9 w-9
                            items-center justify-center
                            rounded-lg
                            ${
                              active
                                ? `
                                  bg-brand-teal/10
                                  text-brand-teal
                                  dark:bg-brand-teal/15
                                `
                                : `
                                  bg-light-surface-soft
                                  text-light-text-muted
                                  dark:bg-dark-surface-soft
                                  dark:text-dark-text-muted
                                `
                            }
                          `}
                        >
                          <Icon className="h-[18px] w-[18px]" />
                        </span>

                        <span>{item.label}</span>
                      </Link>
                    );
                  })}

                  {/* Notifications and Favorites */}
                  {!isLoading &&
                    isAuthenticated === true && (
                      <>
                        <Link
                          href="/notifications"
                          onClick={closeMenu}
                          aria-current={
                            pathname.startsWith('/notifications')
                              ? 'page'
                              : undefined
                          }
                          className={`
                            flex min-h-12
                            items-center gap-4
                            rounded-xl px-3
                            text-base font-semibold
                            transition-colors
                            ${
                              pathname.startsWith('/notifications')
                                ? `
                                  bg-brand-teal/10
                                  text-brand-teal-dark
                                  dark:bg-brand-teal/15
                                  dark:text-brand-teal-light
                                `
                                : `
                                  text-light-text
                                  hover:bg-light-surface-soft
                                  dark:text-dark-text
                                  dark:hover:bg-dark-surface-soft
                                `
                            }
                          `}
                        >
                          <span
                            className="
                              flex h-9 w-9
                              items-center justify-center
                              rounded-lg
                              bg-light-surface-soft
                              text-light-text-muted
                              dark:bg-dark-surface-soft
                              dark:text-dark-text-muted
                            "
                          >
                            <Bell className="h-[18px] w-[18px]" />
                          </span>
                          <span>Notifications</span>
                        </Link>

                        <Link
                          href="/favorites"
                          onClick={closeMenu}
                          aria-current={
                            pathname.startsWith('/favorites')
                              ? 'page'
                              : undefined
                          }
                          className={`
                            flex min-h-12
                            items-center gap-4
                            rounded-xl px-3
                            text-base font-semibold
                            transition-colors
                            ${
                              pathname.startsWith('/favorites')
                                ? `
                                  bg-brand-teal/10
                                  text-brand-teal-dark
                                  dark:bg-brand-teal/15
                                  dark:text-brand-teal-light
                                `
                                : `
                                  text-light-text
                                  hover:bg-light-surface-soft
                                  dark:text-dark-text
                                  dark:hover:bg-dark-surface-soft
                                `
                            }
                          `}
                        >
                          <span
                            className="
                              flex h-9 w-9
                              items-center justify-center
                              rounded-lg
                              bg-light-surface-soft
                              text-light-text-muted
                              dark:bg-dark-surface-soft
                              dark:text-dark-text-muted
                            "
                          >
                            <Heart className="h-[18px] w-[18px]" />
                          </span>
                          <span>Favorites</span>
                        </Link>
                      </>
                    )}

                  {/* Account */}
                  {!isLoading &&
                    isAuthenticated === true && (
                      <Link
                        href="/account"
                        onClick={closeMenu}
                        aria-current={
                          pathname.startsWith('/account')
                            ? 'page'
                            : undefined
                        }
                        className={`
                          flex min-h-12
                          items-center gap-4
                          rounded-xl px-3
                          text-base font-semibold
                          transition-colors
                          ${
                            pathname.startsWith('/account')
                              ? `
                                bg-brand-teal/10
                                text-brand-teal-dark
                                dark:bg-brand-teal/15
                                dark:text-brand-teal-light
                              `
                              : `
                                text-light-text
                                hover:bg-light-surface-soft
                                dark:text-dark-text
                                dark:hover:bg-dark-surface-soft
                              `
                          }
                        `}
                      >
                        <span
                          className="
                            flex h-9 w-9
                            items-center justify-center
                            rounded-lg
                            bg-light-surface-soft
                            text-light-text-muted
                            dark:bg-dark-surface-soft
                            dark:text-dark-text-muted
                          "
                        >
                          <UserRound className="h-[18px] w-[18px]" />
                        </span>
                        <span>Account</span>
                      </Link>
                    )}

                  {/* Sign in */}
                  {!isLoading &&
                    isAuthenticated === false && (
                      <>
                        <Link
                          href="/login"
                          onClick={closeMenu}
                          className="
                            flex min-h-12
                            items-center gap-4
                            rounded-xl px-3
                            text-base font-semibold
                            text-light-text
                            transition-colors
                            hover:bg-light-surface-soft
                            dark:text-dark-text
                            dark:hover:bg-dark-surface-soft
                          "
                        >
                          <span
                            className="
                              flex h-9 w-9
                              items-center justify-center
                              rounded-lg
                              bg-light-surface-soft
                              text-light-text-muted
                              dark:bg-dark-surface-soft
                              dark:text-dark-text-muted
                            "
                          >
                            <LogIn className="h-[18px] w-[18px]" />
                          </span>
                          <span>Sign in</span>
                        </Link>
                      </>
                    )}
                </div>
              </nav>

              {/* Company and legal links */}
              <div
                className="
                  mx-auto mt-6
                  w-full max-w-lg
                  border-t
                  border-light-border-soft
                  pt-4
                  dark:border-dark-border-soft
                "
              >
                <p
                  className="
                    px-3
                    text-[10px] font-bold
                    uppercase tracking-[0.12em]
                    text-light-text-soft
                    dark:text-dark-text-soft
                  "
                >
                  Company &amp; Legal
                </p>

                <nav
                  aria-label="Company and legal links"
                  className="
                    mt-3 flex flex-wrap
                    items-center
                    gap-x-4 gap-y-3
                    px-3
                  "
                >
                  {footerLinks.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={closeMenu}
                      className="
                        text-xs
                        text-light-text-muted
                        transition-colors
                        hover:text-brand-teal
                        focus:outline-none
                        focus-visible:underline
                        dark:text-dark-text-muted
                        dark:hover:text-brand-teal-light
                      "
                    >
                      {item.label}
                    </Link>
                  ))}
                </nav>

                <p
                  className="
                    mt-4 px-3
                    text-[11px]
                    text-light-text-soft
                    dark:text-dark-text-soft
                  "
                >
                  © {new Date().getFullYear()} VibeNationHQ
                </p>
              </div>

              {/* Bottom actions */}
              <div className="mt-auto pt-6">
                <div
                  className="
                    border-t
                    border-light-border-soft
                    dark:border-dark-border-soft
                  "
                />

                {/* Appearance */}
                <div
                  className="
                    mt-5
                    flex items-center
                    justify-between
                    rounded-xl
                    px-3 py-3
                  "
                >
                  <div>
                    <p
                      className="
                        text-sm font-semibold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Appearance
                    </p>

                    <p
                      className="
                        mt-0.5 text-xs
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    >
                      Switch between light and dark mode
                    </p>
                  </div>

                  <ThemeToggle />
                </div>

                {/* Logout */}
                {!isLoading &&
                  isAuthenticated === true && (
                    <button
                      type="button"
                      onClick={openLogoutModal}
                      className="
                        mt-2
                        flex min-h-12
                        w-full
                        items-center gap-4
                        rounded-xl
                        px-3
                        text-left
                        text-base font-semibold
                        text-red-600
                        transition-colors
                        hover:bg-red-500/10
                        focus:outline-none
                        focus-visible:ring-4
                        focus-visible:ring-red-500/10
                        dark:text-red-300
                        dark:hover:bg-red-500/10
                      "
                    >
                      <span
                        className="
                          flex h-9 w-9
                          items-center justify-center
                          rounded-lg
                          bg-red-500/10
                          text-red-600
                          dark:text-red-300
                        "
                      >
                        <LogOut className="h-[18px] w-[18px]" />
                      </span>
                      <span>Log out</span>
                    </button>
                  )}

                {/* Create account */}
                {!isLoading &&
                  isAuthenticated === false && (
                    <Link
                      href="/signup"
                      onClick={closeMenu}
                      className="
                        mt-2
                        flex min-h-12
                        w-full
                        items-center justify-center
                        rounded-xl
                        bg-brand-teal
                        px-4
                        text-sm font-semibold
                        text-white
                        transition-colors
                        hover:bg-brand-teal-dark
                        focus:outline-none
                        focus-visible:ring-4
                        focus-visible:ring-brand-teal/20
                      "
                    >
                      Create account
                    </Link>
                  )}
              </div>
            </div>
          </aside>
        </div>
      )}

      {/* Logout confirmation */}
      <ConfirmationModal
        open={isLogoutModalOpen}
        title="Log out of VibeNationHQ?"
        description={
          logoutError ||
          'You will be signed out of this browser. Your other active sessions will remain signed in.'
        }
        confirmLabel="Log out"
        cancelLabel="Cancel"
        destructive
        isLoading={isLoggingOut}
        onConfirm={handleLogout}
        onCancel={closeLogoutModal}
      />
    </>
  );
}