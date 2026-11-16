import Link from 'next/link';
import type { ReactNode } from 'react';

type MentionTextProps = {
  content: string;
  mentionedUsernames: string[];
  className?: string;
  textHref?: string;
  onMentionClick?: () => void;
};

/**
 * Matches VibeNationHQ usernames:
 * - Letters, numbers and underscores.
 * - Between 3 and 30 characters.
 * - Case-insensitive profile matching.
 */
const MENTION_PATTERN =
  /(^|[^A-Za-z0-9_@.+-])@([A-Za-z0-9_]{3,30})(?![A-Za-z0-9_])/g;

export default function MentionText({
  content,
  mentionedUsernames,
  className,
  textHref,
  onMentionClick,
}: MentionTextProps) {
  const parts: ReactNode[] = [];

  const resolvedUsernames = new Set(
    mentionedUsernames.map((username) =>
      username.trim().replace(/^@/, '').toLowerCase(),
    ),
  );

  const pushText = (text: string, key: string) => {
    if (!text) return;

    parts.push(
      textHref ? (
        <Link
          key={key}
          href={textHref}
          className="text-inherit"
        >
          {text}
        </Link>
      ) : (
        <span key={key}>{text}</span>
      ),
    );
  };

  let lastIndex = 0;
  let match: RegExpExecArray | null;

  MENTION_PATTERN.lastIndex = 0;

  while ((match = MENTION_PATTERN.exec(content)) !== null) {
    const precedingText = match[1];
    const username = match[2];

    const mentionStart = match.index + precedingText.length;
    const mentionEnd = mentionStart + username.length + 1;

    const isResolved = resolvedUsernames.has(
      username.toLowerCase(),
    );

    pushText(
      content.slice(lastIndex, match.index),
      `text-before-${mentionStart}`,
    );

    pushText(
      precedingText,
      `text-prefix-${mentionStart}`,
    );

    if (isResolved) {
      parts.push(
        <Link
          key={`mention-${mentionStart}-${username}`}
          href={`/account/${encodeURIComponent(username)}`}
          onClick={(event) => {
            event.stopPropagation();
            onMentionClick?.();
          }}
          className="font-medium text-brand-teal transition-colors hover:underline focus-visible:outline-none focus-visible:underline"
        >
          @{username}
        </Link>,
      );
    } else {
      pushText(
        `@${username}`,
        `unresolved-${mentionStart}-${username}`,
      );
    }

    lastIndex = mentionEnd;
  }

  pushText(
    content.slice(lastIndex),
    `text-after-${lastIndex}`,
  );

  return <span className={className}>{parts}</span>;
}
