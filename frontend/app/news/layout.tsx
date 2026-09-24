import CategoryNavigation from "@/components/CategoryNavigation";
import Footer from "@/components/Footer";

export default function NewsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <div className="w-full">
                <div className="max-w-[1500px] mx-auto px-4">
                    <CategoryNavigation mode="news" />
                </div>
            </div>

            {children}

            <Footer/>
        </>
    );
}