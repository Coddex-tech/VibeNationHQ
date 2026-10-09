import { apiRequest } from '@/lib/api';

export type MusicDiscoveryArtist = {
  id: number;
  name: string;
  slug: string;
  profile_image: string | null;
  followers_count: number;
  is_verified: boolean;
};

export type MusicDiscoveryAlbum = {
  id: number;
  title: string;
  slug: string;
  artists: MusicDiscoveryArtist[];
  artwork: string | null;
  release_date: string | null;
  favorites_count: number;
  ratings_count: number;
  average_rating: number | null;
};

export type MusicDiscoverySong = {
  id: number;
  title: string;
  slug: string;
  artists: MusicDiscoveryArtist[];
  featured_artists: MusicDiscoveryArtist[];
  artwork: string | null;
  release_date: string | null;
  duration_seconds: number | null;
  duration_display: string | null;
  favorites_count: number;
  ratings_count: number;
  average_rating: number | null;
};

export type MusicDiscoveryResponse = {
  trending_songs: MusicDiscoverySong[];
  trending_albums: MusicDiscoveryAlbum[];
  trending_artists: MusicDiscoveryArtist[];

  most_discussed_songs: MusicDiscoverySong[];
  most_discussed_albums: MusicDiscoveryAlbum[];

  most_favorited_songs: MusicDiscoverySong[];
  most_favorited_albums: MusicDiscoveryAlbum[];

  top_rated_songs: MusicDiscoverySong[];
  top_rated_albums: MusicDiscoveryAlbum[];

  featured_songs: MusicDiscoverySong[];
  featured_albums: MusicDiscoveryAlbum[];
  featured_artists: MusicDiscoveryArtist[];

  recently_released_songs: MusicDiscoverySong[];
  recently_released_albums: MusicDiscoveryAlbum[];
};

export async function getMusicDiscovery(): Promise<MusicDiscoveryResponse> {
  return apiRequest<MusicDiscoveryResponse>(
    '/api/v1/music/discovery/',
  );
}