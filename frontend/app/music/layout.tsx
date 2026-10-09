import HomeNav from "@/components/special/HomeNav";

export default function NewsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
        <HomeNav />
            {children}
        </>
    );
}