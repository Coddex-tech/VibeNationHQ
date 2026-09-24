import type { Metadata } from "next";
import {
  NewsIcon,
  MusicIcon,
  WrenchIcon,
  MailIcon,
  WhatsappIcon,
} from "@/components/Icons";
import FadeIn from "@/components/FadeIn";

export const metadata: Metadata = {
  title: "Contact VibeNationHQ | Editorial, Music & Business Inquiries",
  description:
    "Contact VibeNationHQ for news tips, press releases, music submissions, advertising, partnerships, technical support, and other media inquiries.",
};

export default function ContactPage() {
  const currentYear = new Date().getFullYear();

  const whatsappMusicMessage = encodeURIComponent(
    "Hello VibeNationHQ, I want to promote my song."
  );

  const socialLinks = [
    {
      name: "Facebook",
      href: "#",
    },
    {
      name: "Instagram",
      href: "https://instagram.com/vibenationhqofficial",
    },
    {
      name: "X",
      href: "https://x.com/VibeNationHQ",
    },
    {
      name: "WhatsApp Channel",
      href: "https://whatsapp.com/channel/0029Vb85LFb05MUcD4jtFN0A",
    },
  ];

  return (
    <main className="min-h-screen bg-light-bg text-light-text transition-colors duration-200 dark:bg-dark-bg dark:text-dark-text">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 md:py-16 lg:px-8 lg:py-20">

        {/* =====================================================
            HERO
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            aria-labelledby="contact-page-title"
            className="relative mb-16 overflow-hidden rounded-3xl border border-dark-border bg-dark-surface px-6 py-14 text-center text-dark-text shadow-sm sm:px-12 sm:py-18 lg:px-20 lg:py-22"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-brand-teal/70" />

            <div className="relative mx-auto max-w-4xl">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-brand-teal/30 bg-brand-teal/10 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.18em] text-brand-teal-hover">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-teal" />
                Contact VibeNationHQ
              </div>

              <h1
                id="contact-page-title"
                className="mb-6 text-4xl font-black leading-[1.05] tracking-[-0.04em] text-dark-text sm:text-5xl lg:text-7xl"
              >
                Let&apos;s Start a
                <br className="hidden sm:inline" />
                <span className="text-brand-teal"> Conversation.</span>
              </h1>

              <p className="mx-auto max-w-2xl text-base leading-8 text-dark-text-muted sm:text-lg">
                Reach the right team at VibeNationHQ for editorial,
                music, business, partnership, or technical inquiries.
              </p>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            INTRO
        ===================================================== */}

        <FadeIn direction="up" delay={0.2}>
          <section
            className="mb-16"
            aria-labelledby="communication-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="communication-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Get in Touch
              </h2>
            </div>

            <p className="max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              Whether you have a story to share, music to introduce, a
              partnership idea, or an issue that needs attention, you can
              contact the team through the appropriate channel below. We aim to
              keep communication clear, direct, and useful.
            </p>
          </section>
        </FadeIn>

        {/* =====================================================
            COMMUNICATION DESKS
        ===================================================== */}

        <section
          className="mb-20"
          aria-labelledby="contact-desks-heading"
        >
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-8 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="contact-desks-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Contact the Right Team
              </h2>
            </div>
          </FadeIn>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

            {/* EDITORIAL */}

            <FadeIn direction="up" delay={0.1}>
              <article className="group flex h-full flex-col justify-between rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40">
                <div>
                  <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                    <NewsIcon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                  </div>

                  <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                    Editorial & News Desk
                  </h3>

                  <p className="mb-6 text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Have a news tip, press release, correction, story idea, or
                    information relevant to our coverage? Send it to our
                    editorial contact.
                  </p>
                </div>

                <div className="flex items-center gap-2 border-t border-light-border pt-4 text-sm dark:border-dark-border">
                  <MailIcon className="h-4 w-4 shrink-0 text-brand-teal" />

                  <a
                    href="mailto:newsroom@vibenationhq.com"
                    className="font-semibold text-light-text transition-colors hover:text-brand-teal dark:text-dark-text dark:hover:text-brand-teal-hover"
                  >
                    newsroom@vibenationhq.com
                  </a>
                </div>
              </article>
            </FadeIn>

            {/* MUSIC */}

            <FadeIn direction="up" delay={0.2}>
              <article className="group flex h-full flex-col justify-between rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40">
                <div>
                  <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                    <MusicIcon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                  </div>

                  <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                    Music & Artist Submissions
                  </h3>

                  <p className="mb-6 text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Artists, labels, and music teams can contact us about
                    releases, promotional opportunities, artist features,
                    music coverage, reviews, and official listening links.
                  </p>
                </div>

                <div>
                  <a
                    href={`https://wa.me/2347035101511?text=${whatsappMusicMessage}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 rounded-xl bg-brand-teal px-5 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition-all duration-200 hover:-translate-y-0.5 hover:bg-brand-teal-hover focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-light-surface dark:focus:ring-offset-dark-surface"
                  >
                    <WhatsappIcon className="h-4 w-4" />
                    Submit via WhatsApp
                  </a>
                </div>
              </article>
            </FadeIn>

            {/* TECHNICAL SUPPORT */}

            <FadeIn direction="up" delay={0.3}>
              <article className="group flex h-full flex-col justify-between rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40">
                <div>
                  <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                    <WrenchIcon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                  </div>

                  <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                    Technical Support
                  </h3>

                  <p className="mb-6 text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                    Experiencing a problem while using VibeNationHQ? Contact
                    us about account issues, broken features, technical
                    problems, or other platform-related concerns.
                  </p>
                </div>

                <div className="flex items-center gap-2 border-t border-light-border pt-4 text-sm dark:border-dark-border">
                  <MailIcon className="h-4 w-4 shrink-0 text-brand-teal" />

                  <a
                    href="mailto:support@vibenationhq.com"
                    className="font-semibold text-light-text transition-colors hover:text-brand-teal dark:text-dark-text dark:hover:text-brand-teal-hover"
                  >
                    support@vibenationhq.com
                  </a>
                </div>
              </article>
            </FadeIn>

          </div>
        </section>

        {/* =====================================================
            BUSINESS & PARTNERSHIPS
        ===================================================== */}

        <section
          className="mb-20"
          aria-labelledby="partnerships-heading"
        >
          <FadeIn direction="up" delay={0.1}>
            <div className="rounded-3xl border border-light-border bg-light-surface p-8 shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-12">
              <div className="mb-5 flex items-center gap-3">
                <span className="h-7 w-1 rounded-full bg-brand-teal" />

                <h2
                  id="partnerships-heading"
                  className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
                >
                  Advertising & Partnerships
                </h2>
              </div>

              <p className="mb-8 max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
                Looking to promote a brand, campaign, product, event, artist,
                or service? Our advertising and partnership team can help
                explore available placements and campaign opportunities across
                VibeNationHQ.
              </p>

              <div className="flex flex-col gap-6 rounded-2xl border border-dark-border bg-dark-surface-soft p-7 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="mb-2 text-xl font-bold text-dark-text">
                    Work With VibeNationHQ
                  </h3>

                  <p className="max-w-xl text-sm leading-7 text-dark-text-muted">
                    Contact us for media kits, advertising packages, sponsored
                    content, music promotion, custom placements, and other
                    partnership opportunities.
                  </p>
                </div>

                <div className="shrink-0">
                  <a
                    href="mailto:ads@vibenationhq.com?subject=VibeNationHQ%20Advertising%20Inquiry"
                    className="inline-flex items-center justify-center rounded-xl bg-brand-teal px-6 py-3.5 text-xs font-bold uppercase tracking-wider text-white transition-all duration-200 hover:-translate-y-0.5 hover:bg-brand-teal-hover focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-dark-surface-soft"
                  >
                    Request {currentYear} Media Kit
                  </a>
                </div>
              </div>
            </div>
          </FadeIn>
        </section>

        {/* =====================================================
            SOCIAL
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            className="rounded-3xl border border-light-border bg-light-surface p-8 text-center shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-12"
            aria-labelledby="social-heading"
          >
            <h2
              id="social-heading"
              className="mb-3 text-2xl font-black tracking-tight text-light-text dark:text-dark-text"
            >
              Follow VibeNationHQ
            </h2>

            <p className="mx-auto mb-8 max-w-xl text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
              Stay connected with the latest stories, music discoveries,
              entertainment coverage, and conversations from VibeNationHQ.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-3">
              {socialLinks.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-xl border border-light-border bg-light-surface-soft px-5 py-2.5 text-xs font-semibold tracking-wide text-light-text-muted transition-all duration-200 hover:border-brand-teal/40 hover:text-brand-teal dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text-muted dark:hover:border-brand-teal/40 dark:hover:text-brand-teal-hover"
                >
                  {item.name}
                </a>
              ))}
            </div>
          </section>
        </FadeIn>

      </div>
    </main>
  );
}