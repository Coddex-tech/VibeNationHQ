export type CommentAvatarColor = {
  background: string;
  foreground: string;
};

const AVATAR_COLORS: readonly CommentAvatarColor[] = [
  { background: '#1E3A8A', foreground: '#FFFFFF' },
  { background: '#831843', foreground: '#FFFFFF' },
  { background: '#065F46', foreground: '#FFFFFF' },
  { background: '#92400E', foreground: '#FFFFFF' },
  { background: '#5B21B6', foreground: '#FFFFFF' },
  { background: '#9A3412', foreground: '#FFFFFF' },
  { background: '#155E75', foreground: '#FFFFFF' },
  { background: '#991B1B', foreground: '#FFFFFF' },
  { background: '#334155', foreground: '#FFFFFF' },
  { background: '#166534', foreground: '#FFFFFF' },
  { background: '#4338CA', foreground: '#FFFFFF' },
  { background: '#6D28D9', foreground: '#FFFFFF' },
];

/**
 * Normalize usernames consistently across the application.
 * Handles surrounding whitespace, a leading @, and casing.
 */
export function normalizeUsername(username: string): string {
  return username.trim().replace(/^@/, '').toLowerCase();
}

/**
 * Normalize user IDs before comparing them.
 * This prevents numeric IDs and their string equivalents
 * from being treated as different users.
 */
export function normalizeUserId(
  value: string | number | null | undefined,
): string | null {
  if (value === null || value === undefined) {
    return null;
  }

  return String(value);
}

/**
 * Generate a deterministic avatar colour from a username.
 *
 * Keep the hashing algorithm and palette aligned with MusicPost.tsx
 * so the same username receives the same colour across the site.
 */
export function getAvatarColor(
  username: string,
): CommentAvatarColor {
  const normalizedUsername = normalizeUsername(username);

  let hash = 0;

  for (
    let index = 0;
    index < normalizedUsername.length;
    index += 1
  ) {
    hash =
      (hash * 31 + normalizedUsername.charCodeAt(index)) >>> 0;
  }

  return AVATAR_COLORS[hash % AVATAR_COLORS.length];
}

/**
 * Get the initial displayed in a user's avatar.
 */
export function getAvatarLetter(username: string): string {
  return normalizeUsername(username).charAt(0).toUpperCase() || '?';
}

/**
 * Format a comment timestamp using the existing community conventions:
 * relative time for recent comments and a calendar date for older ones.
 */
export function formatCommentDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return '';
  }

  const elapsed = Math.max(0, Date.now() - date.getTime());
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (elapsed < minute) {
    return 'Just now';
  }

  if (elapsed < hour) {
    return `${Math.floor(elapsed / minute)}m ago`;
  }

  if (elapsed < day) {
    return `${Math.floor(elapsed / hour)}h ago`;
  }

  if (elapsed < 7 * day) {
    return `${Math.floor(elapsed / day)}d ago`;
  }

  return new Intl.DateTimeFormat(undefined, {
    day: 'numeric',
    month: 'short',
    year:
      date.getFullYear() !== new Date().getFullYear()
        ? 'numeric'
        : undefined,
  }).format(date);
}

/**
 * Format large counts compactly:
 * 950 -> "950"
 * 1,200 -> "1.2K"
 * 12,000 -> "12K"
 * 1,500,000 -> "1.5M"
 */
export function formatCount(count: number): string {
  if (!Number.isFinite(count)) {
    return '0';
  }

  if (count >= 1_000_000) {
    return `${(count / 1_000_000)
      .toFixed(count >= 10_000_000 ? 0 : 1)
      .replace(/\.0$/, '')}M`;
  }

  if (count >= 1_000) {
    return `${(count / 1_000)
      .toFixed(count >= 10_000 ? 0 : 1)
      .replace(/\.0$/, '')}K`;
  }

  return String(Math.max(0, Math.floor(count)));
}

/**
 * Determine whether a comment is still inside the allowed edit window.
 * The default matches VibeNationHQ's current 15-minute rule.
 */
export function canEditComment(
  createdAt: string,
  now: number = Date.now(),
  editWindowMs: number = 15 * 60 * 1000,
): boolean {
  const timestamp = new Date(createdAt).getTime();

  return (
    Number.isFinite(timestamp) &&
    now < timestamp + editWindowMs
  );
}

/**
 * Return the clean username used in profile URLs.
 */
export function getProfileUsername(username: string): string {
  return username.trim().replace(/^@/, '');
}
