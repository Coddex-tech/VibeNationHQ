import { notFound } from 'next/navigation';
import HeroNewsSection from '@/components/NewsHeroSection';
import FeaturedArticlesGrid from '@/components/NewsCategoryGrid';
import CategoryCarouselSection from '@/components/CategoryCarouselSection';

interface NewsCard {
    id: number;
    title: string;
    slug: string;
    friendly_date?: string;
    thumbnail_url?: string;
    thumbnail?: string;
    is_sponsored?: boolean;
}

interface MoreNewsCard {
    id: number;
    title: string;
    slug: string;
    category: {
        name: string;
        slug: string;
    };
    friendly_date?: string;
    thumbnail_url?: string;
}

interface NewsCategory {
    name: string;
    slug: string;
}

interface PaginatedGrid {
    count: number;
    next: string | null;
    previous: string | null;
    current_page: number;
    total_pages: number;
    results: NewsCard[];
}

interface CategoryHomeResponse {
    category: NewsCategory;
    featured: NewsCard | null;
    sponsored: NewsCard | null;
    top_news: NewsCard[];
    latest_news: NewsCard[];
    more_news: MoreNewsCard[];
    paginated_grid: PaginatedGrid;
}

interface CategoryPageProps {
    params: Promise<{
        slug: string;
    }>;
    searchParams: Promise<{
        page?: string;
    }>;
}

async function getCategoryHome(
    slug: string,
    page: number
): Promise<CategoryHomeResponse | null> {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!baseUrl) {
        throw new Error(
            'NEXT_PUBLIC_API_URL is not defined in your environment variables.'
        );
    }

    const apiUrl = new URL(
        `${baseUrl}/api/news/${encodeURIComponent(slug)}/`
    );

    apiUrl.searchParams.set('page', String(page));

    const response = await fetch(apiUrl.toString(), {
        next: {
            revalidate: 300,
        },
    });

    if (response.status === 404) {
        return null;
    }

    if (!response.ok) {
        throw new Error(
            `Failed to fetch category "${slug}". Status: ${response.status}`
        );
    }

    return response.json();
}

export default async function NewsCategoryPage({
    params,
    searchParams,
}: CategoryPageProps) {
    const { slug } = await params;
    const { page } = await searchParams;

    const requestedPage = Number(page);

    const currentPage =
        Number.isInteger(requestedPage) && requestedPage > 0
            ? requestedPage
            : 1;

    const data = await getCategoryHome(
        slug,
        currentPage
    );

    if (!data) {
        notFound();
    }

    return (
        <main className="max-w-[1600px] mx-auto px-2 sm:px-4 py-4">

            {/* HERO / TOP / LATEST NEWS */}
            <HeroNewsSection
                globalFeatured={data.featured}
                sponsoredFeature={data.sponsored}
                topNews={data.top_news}
                latestNews={data.latest_news}
                categoryName={data.category.name}
            />

            {/* MAIN CATEGORY NEWS + PAGINATION */}
            <FeaturedArticlesGrid
                pagination={data.paginated_grid}
                categoryName={data.category.name}
                categorySlug={data.category.slug}
            />
            
            {/* MORE NEWS CAROUSEL */}
            <CategoryCarouselSection
                sectionTitle="More News"
                articles={data.more_news}
            />

        </main>
    );
}