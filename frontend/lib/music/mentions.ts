import { apiRequest } from '@/lib/api';

export type MentionUser = {
  id: string | number;
  username: string;
  display_name?: string | null;
  profile_image?: string | null;
  is_verified?: boolean;
  is_identity_verified?: boolean;
};

type MentionSuggestionsResponse = {
  results: MentionUser[];
};

/**
 * Loads users for mention autocomplete.
 *
 * The backend returns at most five suggestions.
 */
export async function loadMentionSuggestions(
  query: string,
): Promise<MentionUser[]> {
  const params = new URLSearchParams();
  params.set('q', query);

  const response = await apiRequest<MentionSuggestionsResponse>(
    `/api/v1/music/mentions/suggestions/?${params.toString()}`,
    {
      method: 'GET',
    },
  );

  return Array.isArray(response.results)
    ? response.results.slice(0, 5)
    : [];
}