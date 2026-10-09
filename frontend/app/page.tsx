import HomeCommunitySection from "@/components/home/HomeCommunitySection";
import HomeEditorialSection from "@/components/home/HomeEditorialSection";
import HomeHero from "@/components/home/HomeHero";
import HomeMusicSection from "@/components/home/HomeMusicSection";
import HomeNewsSection from "@/components/home/HomeNewsSection";
import Footer from "@/components/news/Footer";
import HomeNav from "@/components/special/HomeNav";


export default function HomePage() {
  return (
    <main>
      <HomeNav />
      <HomeHero />
      <HomeMusicSection />
      <HomeCommunitySection />
      <HomeEditorialSection />
      <HomeNewsSection />
      <Footer />
    </main>
  );
}