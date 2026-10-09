import { apiRequest } from '@/lib/api';

export type NewsCard = {
  id: number;
  title: string;
  slug: string;
  friendly_date: string;
  thumbnail_url: string | null;
};

export type NewsCategory = {
  id: number;
  name: string;
  slug: string;
};

export type NewsAuthor = {
  id: number;
  name: string;
  profile_image: string | null;
};

export type GlobalFeaturedNews = {
  id: number;
  title: string;
  slug: string;
  category: NewsCategory[];
  thumbnail: string | null;
  image_caption: string | null;
  content: string;
  article_content: string;
  author: NewsAuthor | null;
  friendly_date: string;
  tags: string[];
  is_sponsored: boolean;
  sponsor_name: string | null;
  is_featured: boolean;
  comments: unknown[];
  total_comments: number;
};

export type NewsCategorizedFeeds = {
  sports: NewsCard[];
  opinion: NewsCard[];
  education: NewsCard[];
  foreign_news: NewsCard[];
  events: NewsCard[];
  music_news: NewsCard[];
  celebrity_gossip: NewsCard[];
  technology: NewsCard[];
  lifestyle: NewsCard[];
  politics: NewsCard[];
  entertainment: NewsCard[];
};

export type NewsHomeResponse = {
  hero_blocks: {
    global_featured: GlobalFeaturedNews | null;
    sponsored_feature: NewsCard | null;
    top_news: NewsCard[];
    latest_news: NewsCard[];
  };
  categorized_feeds: NewsCategorizedFeeds;
};

export async function getNewsHome(): Promise<NewsHomeResponse> {
  return apiRequest<NewsHomeResponse>(
    '/api/news/news-home/',
  );
}