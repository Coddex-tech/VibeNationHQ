import HeroNewsSection from '@/components/NewsHeroSection';
import CategoryNewsGrid from '@/components/CategoryNewsGrid';
import HorizontalNewsCarousel from '@/components/HorizontalNewsCarousel';

async function getHomepageData() {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL
    const res = await fetch(`${baseUrl}/api/news/homepage/`, {
      next: { revalidate: 60 },
    });

    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error('Failed to fetch homepage data:', error);
    return null;
  }
}

export default async function HomePage() {
  const data = await getHomepageData();

  if (!data) {
    return (
      <main className="max-w-7xl mx-auto px-4 py-12 text-center text-slate-500">
        Failed to load homepage feeds.
      </main>
    );
  }

  const { hero_blocks } = data;

  return (
    /* Expanded max-width up to 1600px with minimal side padding */
    <main className="max-w-[1600px] mx-auto px-2 sm:px-4 py-4">

      {/* 3-Column Hero Section */}
      <HeroNewsSection
        globalFeatured={hero_blocks?.global_featured || null}
        sponsoredFeature={hero_blocks?.sponsored_feature || null}
        topNews={hero_blocks?.top_news || []}
        latestNews={hero_blocks?.latest_news || []}
      />

      {/* News Homepage Category grid list */}
      <CategoryNewsGrid
        categoryTitle="Music News"
        newsList={data.categorized_feeds.music_news}
      />
      
      <CategoryNewsGrid
        categoryTitle="Politics"
        newsList={data.categorized_feeds.politics}
      />

      <CategoryNewsGrid
        categoryTitle="Entertainment"
        newsList={data.categorized_feeds.entertainment}
      />

      <CategoryNewsGrid
        categoryTitle="Education"
        newsList={data.categorized_feeds.education}
      />

      <CategoryNewsGrid
        categoryTitle="Sports"
        newsList={data.categorized_feeds.sports}
      />

      <CategoryNewsGrid
        categoryTitle="Technology"
        newsList={data.categorized_feeds.technology}
      />

      <CategoryNewsGrid
        categoryTitle="Foreign News"
        newsList={data.categorized_feeds.foreign_news}
      />

      <HorizontalNewsCarousel
        categoryTitle="Opinion"
        newsList={data.categorized_feeds.opinion}
      />

      <HorizontalNewsCarousel
        categoryTitle="Lifestyle"
        newsList={data.categorized_feeds.lifestyle}
      />

      <HorizontalNewsCarousel
        categoryTitle="Events"
        newsList={data.categorized_feeds.events}
      />
    </main>
  );
}