import Link from 'next/link';
import {
  ArrowRight,
  Disc3,
  Flame,
  MessageCircle,
  Music2,
  Star,
  TrendingUp,
  Users,
} from 'lucide-react';
import type { ReactNode } from 'react';

type DiscoveryIconName =
  | 'disc'
  | 'flame'
  | 'message'
  | 'music'
  | 'star'
  | 'trending'
  | 'users';

type DiscoverySectionProps = {
  title: string;
  description?: string;
  icon: DiscoveryIconName;
  href?: string;
  children: ReactNode;
  className?: string;
};

const icons = {
  disc: Disc3,
  flame: Flame,
  message: MessageCircle,
  music: Music2,
  star: Star,
  trending: TrendingUp,
  users: Users,
};

export default function DiscoverySection({
  title,
  description,
  icon,
  href,
  children,
  className = '',
}: DiscoverySectionProps) {
  const Icon = icons[icon];

  return (
    <section
      className={`
        min-w-0 rounded-3xl
        bg-light-surface
        px-4 py-5
        transition-colors duration-200
        sm:px-5 sm:py-6
        dark:bg-dark-surface
        ${className}
      `}
    >
      <div className="mb-5 flex flex-wrap items-start justify-between gap-3 sm:mb-6">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <span
            className="
              flex h-10 w-10 shrink-0
              items-center justify-center
              rounded-2xl
              bg-brand-teal/10
              text-brand-teal
              dark:bg-brand-teal/15
              dark:text-brand-teal-light
            "
            aria-hidden="true"
          >
            <Icon size={20} strokeWidth={1.9} />
          </span>

          <div className="min-w-0 flex-1">
            <h2
              className="
                break-words
                text-base font-bold tracking-tight
                text-light-text
                sm:text-lg
                dark:text-dark-text
              "
            >
              {title}
            </h2>

            {description && (
              <p
                className="
                  mt-1 text-xs leading-relaxed
                  text-light-text-muted
                  sm:text-sm
                  dark:text-dark-text-muted
                "
              >
                {description}
              </p>
            )}
          </div>
        </div>

        {href && (
          <Link
            href={href}
            aria-label={`See all ${title}`}
            className="
              group inline-flex shrink-0
              items-center gap-1.5
              rounded-full px-3 py-2
              text-xs font-semibold
              text-light-text-muted
              transition-colors duration-200
              hover:bg-light-surface-hover
              hover:text-light-text
              focus:outline-none
              focus-visible:ring-2
              focus-visible:ring-brand-teal
              focus-visible:ring-offset-2
              focus-visible:ring-offset-light-surface
              sm:text-sm
              dark:text-dark-text-muted
              dark:hover:bg-dark-surface-hover
              dark:hover:text-dark-text
              dark:focus-visible:ring-offset-dark-surface
            "
          >
            <span>See all</span>
            <ArrowRight
              className="
                h-4 w-4
                transition-transform duration-200
                group-hover:translate-x-0.5
              "
              aria-hidden="true"
            />
          </Link>
        )}
      </div>

      {children}
    </section>
  );
}