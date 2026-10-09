'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';

import FadeIn from '@/components/FadeIn';
import { useAuth } from '@/components/auth/AuthProvider';

type ProtectedRouteProps = {
  children: React.ReactNode;
};

export default function ProtectedRoute({
  children,
}: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();

  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  useEffect(() => {
    if (
      isLoading ||
      isAuthenticated !== false
    ) {
      return;
    }

    const nextPath =
      pathname || '/settings';

    router.replace(
      `/login?next=${encodeURIComponent(
        nextPath,
      )}`,
    );
  }, [
    isAuthenticated,
    isLoading,
    pathname,
    router,
  ]);

  if (
    isLoading ||
    isAuthenticated === null
  ) {
    return (
      <div
        className="
          min-h-screen
          bg-light-bg
          text-light-text
          dark:bg-dark-bg
          dark:text-dark-text
        "
      >
        <div
          className="
            mx-auto flex min-h-screen
            w-full max-w-5xl
            items-center justify-center
            px-4 py-8
            sm:px-6
            lg:px-8
          "
        >
          <FadeIn className="w-full max-w-md">
            <div
              className="
                rounded-2xl
                border border-light-border
                bg-light-surface
                p-6
                shadow-sm shadow-black/[0.03]
                dark:border-dark-border
                dark:bg-dark-surface
                dark:shadow-black/10
              "
            >
              <div className="animate-pulse">
                <div
                  className="
                    mx-auto h-10 w-10
                    rounded-xl
                    bg-light-surface-muted
                    dark:bg-dark-surface-muted
                  "
                />

                <div
                  className="
                    mx-auto mt-4 h-4 w-40
                    rounded
                    bg-light-surface-muted
                    dark:bg-dark-surface-muted
                  "
                />

                <div
                  className="
                    mx-auto mt-2 h-3 w-56
                    max-w-full rounded
                    bg-light-surface-soft
                    dark:bg-dark-surface-soft
                  "
                />
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return children;
}