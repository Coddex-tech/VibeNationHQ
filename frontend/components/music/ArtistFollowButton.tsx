
'use client';

import { useState } from 'react';
import { Check, UserPlus, Users } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { ApiError, apiRequest } from '@/lib/api';
import { useAuth } from '@/components/auth/AuthProvider';

type ArtistFollowResponse = {
  following: boolean;
  followers_count: number;
};

type ArtistFollowButtonProps = {
  artistId: number | string;
  initialIsFollowing: boolean;
  initialFollowersCount: number;
  className?: string;
};

export default function ArtistFollowButton({
  artistId,
  initialIsFollowing,
  initialFollowersCount,
  className = '',
}: ArtistFollowButtonProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();

  const [isFollowing, setIsFollowing] = useState(
    initialIsFollowing,
  );
  const [followersCount, setFollowersCount] = useState(
    initialFollowersCount,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  async function handleFollowToggle() {
    if (isSubmitting || isAuthLoading) {
      return;
    }

    if (!isAuthenticated) {
      const returnTo =
        typeof window !== 'undefined'
          ? `${window.location.pathname}${window.location.search}${window.location.hash}`
          : `/music/artists`;

      router.push(
        `/login?next=${encodeURIComponent(returnTo)}`,
      );
      return;
    }

    setIsSubmitting(true);
    setErrorMessage('');

    try {
      const response = await apiRequest<ArtistFollowResponse>(
        `/api/v1/music/artists/${encodeURIComponent(String(artistId))}/follow/`,
        {
          method: isFollowing ? 'DELETE' : 'POST',
        },
      );

      setIsFollowing(response.following);
      setFollowersCount(response.followers_count);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        const returnTo =
          `${window.location.pathname}${window.location.search}${window.location.hash}`;

        router.push(
          `/login?next=${encodeURIComponent(returnTo)}`,
        );
        return;
      }

      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'Unable to update your follow status. Please try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  const buttonLabel = isSubmitting
    ? isFollowing
      ? 'Unfollowing…'
      : 'Following…'
    : isFollowing
      ? 'Following'
      : 'Follow artist';

  return (
    <div className={className}>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleFollowToggle}
          disabled={isSubmitting || isAuthLoading}
          aria-pressed={isFollowing}
          aria-label={
            isFollowing
              ? 'Unfollow this artist'
              : 'Follow this artist'
          }
          className={[
            'inline-flex min-h-10 items-center justify-center gap-2 rounded-full px-5 py-2',
            'text-sm font-semibold transition-colors',
            'focus-visible:outline-none focus-visible:ring-2',
            'focus-visible:ring-[#008080] focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-60',
            isFollowing
              ? 'border border-gray-300 bg-white text-gray-800 hover:border-red-300 hover:bg-red-50 hover:text-red-700 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:hover:border-red-700 dark:hover:bg-red-950/30 dark:hover:text-red-300'
              : 'bg-[#008080] text-white hover:bg-[#006b6b]',
          ].join(' ')}
        >
          {isSubmitting ? (
            <span
              className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent"
              aria-hidden="true"
            />
          ) : isFollowing ? (
            <Check size={16} aria-hidden="true" />
          ) : (
            <UserPlus size={16} aria-hidden="true" />
          )}

          <span>{buttonLabel}</span>
        </button>

        <div
          className="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300"
          aria-live="polite"
          aria-atomic="true"
        >
          <Users size={16} aria-hidden="true" />
          <span>
            {followersCount.toLocaleString()}{' '}
            {followersCount === 1 ? 'follower' : 'followers'}
          </span>
        </div>
      </div>

      {errorMessage && (
        <p
          role="alert"
          className="mt-2 text-sm text-red-600 dark:text-red-400"
        >
          {errorMessage}
        </p>
      )}
    </div>
  );
}
