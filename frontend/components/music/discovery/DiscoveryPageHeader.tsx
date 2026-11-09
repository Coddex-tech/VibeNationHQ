import {
  Disc3,
  Flame,
  MessageCircle,
  Music2,
  Star,
  TrendingUp,
  Users,
} from 'lucide-react';

type DiscoveryIconName =
  | 'disc'
  | 'flame'
  | 'message'
  | 'music'
  | 'star'
  | 'trending'
  | 'users';

type DiscoveryPageHeaderProps = {
  title: string;
  description: string;
  icon?: DiscoveryIconName;
  eyebrow?: string;
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

export default function DiscoveryPageHeader({
  title,
  description,
  icon,
  eyebrow = 'Music Discovery',
}: DiscoveryPageHeaderProps) {
  const Icon = icon ? icons[icon] : null;

  return (
    <header className="relative isolate overflow-hidden rounded-2xl bg-light-surface p-5 sm:p-7 dark:bg-dark-surface">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-12 -top-16 -z-10 h-48 w-48 rounded-full bg-brand-teal/10 blur-3xl dark:bg-brand-teal/15"
      />

      <div className="relative flex min-w-0 items-start gap-3 sm:gap-4">
        {Icon && (
          <div
            aria-hidden="true"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light sm:h-14 sm:w-14"
          >
            <Icon
              size={26}
              strokeWidth={1.8}
            />
          </div>
        )}

        <div className="min-w-0 flex-1">
          {eyebrow && (
            <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-brand-teal dark:text-brand-teal-light sm:text-xs">
              {eyebrow}
            </p>
          )}

          <h1 className="break-words text-2xl font-extrabold tracking-tight text-light-text sm:text-3xl dark:text-dark-text">
            {title}
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-light-text-muted sm:text-base sm:leading-7 dark:text-dark-text-muted">
            {description}
          </p>
        </div>
      </div>
    </header>
  );
}