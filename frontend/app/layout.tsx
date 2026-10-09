import "./globals.css";

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import AuthProvider from "@/components/auth/AuthProvider";
import ThemeProvider from "@/components/ThemeProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ??
  "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),

  title: {
    default: "VibeNationHQ | Music, News & Entertainment",
    template: "%s | VibeNationHQ",
  },

  description:
    "VibeNationHQ is an entertainment and media platform for music, news, culture, and conversations.",

  openGraph: {
    type: "website",
    siteName: "VibeNationHQ",
    title: "VibeNationHQ | Music, News & Entertainment",
    description:
      "VibeNationHQ is an entertainment and media platform for music, news, culture, and conversations.",
    url: siteUrl,
  },

  twitter: {
    card: "summary",
    title: "VibeNationHQ | Music, News & Entertainment",
    description:
      "VibeNationHQ is an entertainment and media platform for music, news, culture, and conversations.",
  },

  robots: {
    index: true,
    follow: true,
  },
};

const websiteStructuredData = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "VibeNationHQ",
  url: siteUrl,
  description:
    "VibeNationHQ is an entertainment and media platform for music, news, culture, and conversations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-screen">
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>

        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(
              websiteStructuredData,
            ),
          }}
        />
      </body>
    </html>
  );
}