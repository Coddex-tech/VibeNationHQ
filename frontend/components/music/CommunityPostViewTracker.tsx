
'use client';

import { useEffect } from 'react';

import { apiRequest } from '@/lib/api';

type CommunityPostViewTrackerProps = {
  postId: number;
};

type RecordViewResponse = {
  views_count: number;
  counted: boolean;
};

export default function CommunityPostViewTracker({
  postId,
}: CommunityPostViewTrackerProps) {
  useEffect(() => {
    if (!Number.isInteger(postId) || postId <= 0) {
      return;
    }

    let cancelled = false;

    async function recordView() {
      const navigationEntry =
        performance.getEntriesByType('navigation')[0] as
          | PerformanceNavigationTiming
          | undefined;

      const navigationType =
        navigationEntry?.type === 'reload'
          ? 'reload'
          : 'navigate';

      try {
        const response = await apiRequest<RecordViewResponse>(
          `/api/v1/music/community/posts/${postId}/view/`,
          {
            method: 'POST',
            body: JSON.stringify({
              navigation_type: navigationType,
            }),
          },
        );

        if (cancelled || !response.counted) {
          return;
        }

        window.dispatchEvent(
          new CustomEvent('community-post-view-updated', {
            detail: {
              postId,
              viewsCount: response.views_count,
            },
          }),
        );
      } catch (error) {
        // Unauthenticated requests are rejected by Django.
        // Avoid interrupting page rendering if recording fails.
        if (
          error instanceof Error &&
          'status' in error &&
          (error as { status?: number }).status === 401
        ) {
          return;
        }

        console.error(
          'Failed to record community post view.',
          error,
        );
      }
    }

    void recordView();

    return () => {
      cancelled = true;
    };
  }, [postId]);

  return null;
}
