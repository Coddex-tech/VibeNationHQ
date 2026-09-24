import type { Metadata } from "next";
import {
  RocketIcon,
  ShieldIcon,
  AnalyticsIcon,
} from "@/components/Icons";
import FadeIn from "@/components/FadeIn";

export const metadata: Metadata = {
  title: "Advertise on VibeNationHQ | Media Kit & Brand Partnerships",
  description:
    "Advertise with VibeNationHQ through sponsored content, banner placements, music promotion, and brand partnerships reaching audiences interested in African news, music, entertainment, and culture.",
};

export default function AdvertisePage() {
  const currentYear = new Date().getFullYear();

  const whatsappMessage = encodeURIComponent(
    "Hi, I am interested in advertising or partnering with VibeNationHQ. Please share your available packages and media kit."
  );

  const benefits = [
    {
      title: "Relevant Content Placement",
      description:
        "Place your brand alongside content relevant to your audience, including African news, music releases, entertainment stories, culture, and original analysis.",
      icon: RocketIcon,
    },
    {
      title: "Professional Brand Environment",
      description:
        "Your campaign appears within a professionally designed publishing environment built around readability, clear content structure, and responsible editorial standards.",
      icon: ShieldIcon,
    },
    {
      title: "Campaign Reporting",
      description:
        "Where applicable, campaign reporting can provide useful information about advertising performance, helping partners understand how their placements perform.",
      icon: AnalyticsIcon,
    },
  ];

  const solutions = [
    {
      number: "01",
      title: "Sponsored Editorial & Featured Content",
      description:
        "Promote a product, service, release, campaign, event, or announcement through clearly identified sponsored or branded content created for your campaign.",
    },
    {
      number: "02",
      title: "Music & Artist Promotion",
      description:
        "Give artists, labels, and music campaigns additional exposure through promotional placements, release features, artist spotlights, and other available music marketing opportunities.",
    },
    {
      number: "03",
      title: "Display Advertising & Custom Placements",
      description:
        "Promote your brand through available banner placements, sponsored sections, homepage opportunities, and custom advertising packages designed around your campaign objectives.",
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
            aria-labelledby="advertise-page-title"
            className="relative mb-20 overflow-hidden rounded-3xl border border-dark-border bg-dark-surface px-6 py-14 text-center text-white shadow-sm sm:px-12 sm:py-18 lg:px-20 lg:py-24"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-brand-teal/70" />

            <div className="relative mx-auto max-w-4xl">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-brand-teal/30 bg-brand-teal/10 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.18em] text-brand-teal-hover">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-teal" />
                Advertising & Partnerships
              </div>

              <h1
                id="advertise-page-title"
                className="mb-6 text-4xl font-black leading-[1.02] tracking-[-0.045em] text-dark-text sm:text-5xl lg:text-7xl"
              >
                Put Your Brand
                <br className="hidden sm:inline" />
                <span className="text-brand-teal"> in the Vibe.</span>
              </h1>

              <p className="mx-auto mb-9 max-w-2xl text-base leading-8 text-dark-text-muted sm:text-lg">
                Connect your brand with audiences interested in African news,
                music, entertainment, culture, and original media coverage.
              </p>

              <a
                href="mailto:ads@vibenationhq.com?subject=VibeNationHQ%20Media%20Kit%20Request"
                className="inline-flex items-center justify-center rounded-xl bg-brand-teal px-8 py-4 text-xs font-bold uppercase tracking-wider text-white transition-all duration-200 hover:-translate-y-0.5 hover:bg-brand-teal-hover focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-dark-surface sm:text-sm"
              >
                Request {currentYear} Media Kit
              </a>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            VALUE PROPOSITION
        ===================================================== */}

        <FadeIn direction="up" delay={0.15}>
          <section
            className="mb-20"
            aria-labelledby="advertising-advantage-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="advertising-advantage-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Why Partner With VibeNationHQ?
              </h2>
            </div>

            <p className="max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              VibeNationHQ is built around content discovery. Our platform
              brings together news, music, entertainment, and culture, giving
              brands opportunities to appear alongside relevant editorial and
              creative content in a clean, modern publishing environment.
            </p>
          </section>
        </FadeIn>

        {/* =====================================================
            BENEFITS
        ===================================================== */}

        <section
          className="mb-20"
          aria-labelledby="advertising-benefits-heading"
        >
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-8 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="advertising-benefits-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Built for Brand Visibility
              </h2>
            </div>
          </FadeIn>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;

              return (
                <FadeIn
                  key={benefit.title}
                  direction="up"
                  delay={0.1 + index * 0.1}
                >
                  <article
                    className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/30 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40"
                  >
                    <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal dark:border-brand-teal/25 dark:bg-brand-teal/10 dark:text-brand-teal">
                      <Icon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                    </div>

                    <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                      {benefit.title}
                    </h3>

                    <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                      {benefit.description}
                    </p>
                  </article>
                </FadeIn>
              );
            })}
          </div>
        </section>

        {/* =====================================================
            SOLUTIONS
        ===================================================== */}

        <section
          className="mb-20"
          aria-labelledby="advertising-solutions-heading"
        >
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="advertising-solutions-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Advertising & Partnership Solutions
              </h2>
            </div>

            <p className="mb-8 max-w-3xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              We offer flexible promotional opportunities for brands, artists,
              record labels, businesses, agencies, and other organizations.
            </p>
          </FadeIn>

          <div className="space-y-4">
            {solutions.map((solution, index) => (
              <FadeIn
                key={solution.number}
                direction="up"
                delay={0.15 + index * 0.1}
              >
                <article
                  className="group rounded-2xl border border-light-border border-l-4 border-l-brand-teal bg-light-surface p-6 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md dark:border-dark-border dark:border-l-brand-teal dark:bg-dark-surface sm:p-8"
                >
                  <div className="flex gap-5">
                    <span className="hidden pt-0.5 text-xs font-black tracking-[0.18em] text-brand-teal sm:block">
                      {solution.number}
                    </span>

                    <div>
                      <h3 className="mb-2 text-lg font-bold text-light-text dark:text-dark-text sm:text-xl">
                        {solution.title}
                      </h3>

                      <p className="max-w-4xl text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                        {solution.description}
                      </p>
                    </div>
                  </div>
                </article>
              </FadeIn>
            ))}
          </div>
        </section>

        {/* =====================================================
            CTA
        ===================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section
            aria-labelledby="advertising-cta-heading"
            className="relative overflow-hidden rounded-3xl border border-light-border bg-light-surface px-7 py-12 text-center text-light-text shadow-sm sm:px-12 sm:py-16 dark:border-brand-teal/25 dark:bg-dark-surface dark:text-dark-text"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-brand-teal/60" />

            <div className="relative mx-auto max-w-3xl">
              <div className="mx-auto mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-brand-teal/25 bg-brand-teal/10">
                <span className="h-2 w-2 rounded-full bg-brand-teal" />
              </div>

              <h2
                id="advertising-cta-heading"
                className="mb-4 text-2xl font-black tracking-tight text-light-text sm:text-4xl dark:text-dark-text"
              >
                Let&apos;s Build Your Campaign
              </h2>

              <p className="mx-auto mb-8 max-w-xl text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                Tell us about your brand, campaign, or promotional goals and
                our advertising team will help you explore the right
                VibeNationHQ partnership option.
              </p>

              <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
                <a
                  href={`https://wa.me/2347035101511?text=${whatsappMessage}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full rounded-xl bg-brand-teal px-8 py-4 text-xs font-bold uppercase tracking-wider text-white transition-colors duration-200 hover:bg-brand-teal-light focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-light-surface sm:w-auto dark:focus:ring-offset-dark-surface"
                >
                  Chat With Our Team
                </a>

                <a
                  href="mailto:ads@vibenationhq.com?subject=VibeNationHQ%20Advertising%20Inquiry"
                  className="w-full rounded-xl border border-light-border bg-light-surface-soft px-8 py-4 text-xs font-bold uppercase tracking-wider text-light-text transition-colors duration-200 hover:bg-light-surface-muted focus:outline-none focus:ring-2 focus:ring-brand-teal/40 focus:ring-offset-2 focus:ring-offset-light-surface sm:w-auto dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:hover:bg-dark-surface-muted dark:focus:ring-offset-dark-surface"
                >
                  Email Advertising Team
                </a>
              </div>
            </div>
          </section>
        </FadeIn>
      </div>
    </main>
  );
}