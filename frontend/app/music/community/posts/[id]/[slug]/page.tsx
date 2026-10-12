import type { Metadata } from 'next';

import {
  notFound,
  permanentRedirect,
} from 'next/navigation';

import MusicPost from '@/components/music/MusicPost';
import CommunityPostViewTracker from '@/components/music/CommunityPostViewTracker';

import {
  CommunityPostFetchError,
  getCommunityPostById,
} from '@/lib/music/CommunityPostServer';

type CommunityPostPageProps = {
  params: Promise<{
    id: string;
    slug: string;
  }>;
};

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ??
  'http://localhost:3000';

function getPostTitle(content: string): string {
  const cleanContent = content
    .replace(/\s+/g, ' ')
    .trim();

  if (!cleanContent) {
    return 'Community Post | VibeNationHQ';
  }

  const title =
    cleanContent.length > 65
      ? `${cleanContent.slice(0, 62).trimEnd()}...`
      : cleanContent;

  return `${title} | VibeNationHQ`;
}

function getPostDescription(content: string): string {
  const cleanContent = content
    .replace(/\s+/g, ' ')
    .trim();

  if (!cleanContent) {
    return 'Read this community post on VibeNationHQ.';
  }

  return cleanContent.length > 160
    ? `${cleanContent.slice(0, 157).trimEnd()}...`
    : cleanContent;
}

async function fetchCommunityPost(id: string) {
  if (!/^[1-9]\d*$/.test(id)) {
    notFound();
  }

  const postId = Number(id);

  if (!Number.isSafeInteger(postId)) {
    notFound();
  }

  try {
    return await getCommunityPostById(postId);
  } catch (error) {
    if (
      error instanceof CommunityPostFetchError &&
      error.status === 404
    ) {
      notFound();
    }

    throw error;
  }
}

export async function generateMetadata({
  params,
}: CommunityPostPageProps): Promise<Metadata> {
  const { id } = await params;
  const post = await fetchCommunityPost(id);

  const title = getPostTitle(post.content);
  const description = getPostDescription(post.content);

  const canonicalUrl =
    `/music/community/posts/${post.id}/${encodeURIComponent(post.slug)}`;

  return {
    title,
    description,

    alternates: {
      canonical: canonicalUrl,
    },

    openGraph: {
      type: 'article',
      title,
      description,
      url: canonicalUrl,
      siteName: 'VibeNationHQ',
      publishedTime: post.created_at,
      modifiedTime: post.updated_at,
    },

    twitter: {
      card: 'summary',
      title,
      description,
    },
  };
}

export default async function CommunityPostPage({
  params,
}: CommunityPostPageProps) {
  const { id, slug } = await params;
  const post = await fetchCommunityPost(id);

  const canonicalPath =
    `/music/community/posts/${post.id}/${encodeURIComponent(post.slug)}`;

  if (slug !== post.slug) {
    permanentRedirect(canonicalPath);
  }

  const canonicalUrl = new URL(
    canonicalPath,
    siteUrl,
  ).toString();

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'DiscussionForumPosting',
    '@id': `${canonicalUrl}#discussion`,
    url: canonicalUrl,

    headline: post.content
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 110),

    articleBody: post.content,
    datePublished: post.created_at,
    dateModified: post.updated_at,

    author: {
      '@type': 'Person',
      name: post.user.username,
    },

    interactionStatistic: [
      {
        '@type': 'InteractionCounter',
        interactionType: {
          '@type': 'LikeAction',
        },
        userInteractionCount: post.likes_count,
      },
      {
        '@type': 'InteractionCounter',
        interactionType: {
          '@type': 'CommentAction',
        },
        userInteractionCount: post.comments_count,
      },
    ],
  };

  return (
    <div
      className="
        min-h-screen
        bg-light-bg
        text-light-text
        dark:bg-dark-bg
        dark:text-dark-text
      "
    >
      <main
        className="
          mx-auto
          w-full
          max-w-3xl
          px-3
          py-5
          sm:px-5
          sm:py-8
        "
      >
        <h1 className="sr-only">
          Community post by @{post.user.username}
        </h1>

        <CommunityPostViewTracker postId={post.id} />

        <MusicPost
          post={post}
          variant="detail"
        />
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            structuredData,
          ).replace(/</g, '\\u003c'),
        }}
      />
    </div>
  );
}