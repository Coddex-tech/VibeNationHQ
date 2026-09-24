import CategoryNavigation from '@/components/CategoryNavigation';

export default function NewsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <CategoryNavigation mode="music" />

            {children}
        </>
    );
}