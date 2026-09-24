import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";

export default function PublicLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen">
      <Navbar />

      <main className="min-h-[calc(100vh-4rem)]">
        {children}
      </main>

      <Footer />
    </div>
  );
}