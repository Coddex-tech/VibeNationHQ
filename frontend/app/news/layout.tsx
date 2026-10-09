import CategoryNavigation from "@/components/news/CategoryNavigation";
import Footer from "@/components/news/Footer";
import HomeNav from "@/components/special/HomeNav";

export default function NewsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <HomeNav />
            <div className="w-full">
                <div className="max-w-[1500px] mx-auto px-4">
                    <CategoryNavigation />
                </div>
            </div>

            {children}

            <Footer />
        </>
    );
}