import type { Metadata } from 'next';

import { getEditorialArticle } from '@/lib/music/EditorialArticles';
import EditorialArticleDetailClient from '@/components/music/EditorialArticleDetailClient';

type EditorialPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata({
  params,
}: EditorialPageProps): Promise<Metadata> {
  const { slug } = await params;

  try {
    const article = await getEditorialArticle(slug);

    return {
      title: article.title,
      description:
        article.excerpt ||
        'Read the latest music editorial stories on VibeNationHQ.',
      alternates: {
        canonical: `/music/editorial/${article.slug}`,
      },
      openGraph: {
        type: 'article',
        title: article.title,
        description: article.excerpt,
        publishedTime: article.published_at ?? undefined,
        authors: [article.author.name],
      },
      twitter: {
        card: 'summary',
        title: article.title,
        description: article.excerpt,
      },
    };
  } catch {
    return {
      title: 'Music Editorial',
      description:
        'Music stories, insights, and entertainment on VibeNationHQ.',
    };
  }
}

export default async function EditorialArticlePage({
  params,
}: EditorialPageProps) {
  const { slug } = await params;

  return <EditorialArticleDetailClient slug={slug} />;
}