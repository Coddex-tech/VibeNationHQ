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

  return (
    <main className="mx-auto max-w-6xl overflow-hidden px-4 py-12 sm:px-6 md:py-20 lg:px-8">

      {/* =====================================================
          1. HERO
      ===================================================== */}

      <FadeIn direction="up" delay={0.1}>
        <section
          aria-labelledby="advertise-page-title"
          className="relative mb-16 overflow-hidden rounded-3xl border border-slate-800 bg-slate-950 p-8 text-center text-white shadow-2xl sm:p-14 lg:p-20"
        >
          <div className="pointer-events-none absolute -left-32 -top-32 h-80 w-80 rounded-full bg-teal-500/20 blur-[100px]" />

          <div className="pointer-events-none absolute -bottom-32 -right-32 h-80 w-80 rounded-full bg-cyan-500/20 blur-[100px]" />

          <div className="relative">

            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-3.5 py-1.5 text-xs font-semibold uppercase tracking-widest text-teal-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-teal-400" />
              Advertising & Partnerships
            </div>

            <h1
              id="advertise-page-title"
              className="mb-6 text-3xl font-black leading-[1.1] tracking-tight text-white sm:text-5xl lg:text-6xl"
            >
              Advertise on
              <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-teal-400 via-cyan-400 to-yellow-400 bg-clip-text text-transparent">
                {" "}
                VibeNationHQ
              </span>
            </h1>

            <p className="mx-auto mb-8 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg">
              Connect your brand with readers interested in African news,
              music, entertainment, culture, and original media coverage.
            </p>

            <a
              href="mailto:ads@vibenationhq.com?subject=VibeNationHQ%20Media%20Kit%20Request"
              className="inline-flex items-center justify-center rounded-xl bg-teal-500 px-8 py-4 text-xs font-bold uppercase tracking-wider text-slate-950 shadow-lg shadow-teal-500/20 transition-all duration-300 hover:-translate-y-0.5 hover:bg-teal-400 sm:text-sm"
            >
              Request {currentYear} Media Kit
            </a>

          </div>
        </section>
      </FadeIn>

      {/* =====================================================
          2. VALUE PROPOSITION
      ===================================================== */}

      <FadeIn direction="up" delay={0.2}>
        <section
          className="mb-16"
          aria-labelledby="advertising-advantage-heading"
        >
          <div className="mb-4 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-teal-500" />

            <h2
              id="advertising-advantage-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              Why Advertise With VibeNationHQ?
            </h2>
          </div>

          <p className="max-w-4xl text-base leading-relaxed text-slate-600 dark:text-slate-300 sm:text-lg">
            VibeNationHQ is built around content discovery. Our platform
            brings together news, music, entertainment, and culture, giving
            brands opportunities to appear alongside relevant editorial and
            creative content in a clean, modern publishing environment.
          </p>
        </section>
      </FadeIn>

      {/* =====================================================
          3. ADVERTISING BENEFITS
      ===================================================== */}

      <section
        className="mb-20"
        aria-labelledby="advertising-benefits-heading"
      >
        <FadeIn direction="up" delay={0.1}>
          <div className="mb-8 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-cyan-500" />

            <h2
              id="advertising-benefits-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              Built for Brand Visibility
            </h2>
          </div>
        </FadeIn>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

          {/* CARD 1 */}

          <FadeIn direction="up" delay={0.1}>
            <article className="group h-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-teal-500/50 hover:shadow-md dark:border-slate-800 dark:bg-slate-950">

              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400">
                <RocketIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-110" />
              </div>

              <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
                Relevant Content Placement
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Place your brand alongside content relevant to your audience,
                including African news, music releases, entertainment stories,
                culture, and original analysis.
              </p>

            </article>
          </FadeIn>

          {/* CARD 2 */}

          <FadeIn direction="up" delay={0.25}>
            <article className="group h-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-cyan-500/50 hover:shadow-md dark:border-slate-800 dark:bg-slate-950">

              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
                <ShieldIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-110" />
              </div>

              <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
                Professional Brand Environment
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Your campaign appears within a professionally designed
                publishing environment built around readability, clear
                content structure, and responsible editorial standards.
              </p>

            </article>
          </FadeIn>

          {/* CARD 3 */}

          <FadeIn direction="up" delay={0.4}>
            <article className="group h-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-yellow-500/50 hover:shadow-md dark:border-slate-800 dark:bg-slate-950">

              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-500/10 text-yellow-600 dark:text-yellow-400">
                <AnalyticsIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-110" />
              </div>

              <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
                Campaign Reporting
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Where applicable, campaign reporting can provide useful
                information about advertising performance, helping partners
                understand how their placements perform.
              </p>

            </article>
          </FadeIn>

        </div>
      </section>

      {/* =====================================================
          4. ADVERTISING SOLUTIONS
      ===================================================== */}

      <section
        className="mb-20"
        aria-labelledby="advertising-solutions-heading"
      >
        <FadeIn direction="up" delay={0.1}>

          <div className="mb-4 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-cyan-500" />

            <h2
              id="advertising-solutions-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              Advertising & Partnership Solutions
            </h2>
          </div>

          <p className="mb-8 max-w-3xl text-base leading-relaxed text-slate-600 dark:text-slate-400">
            We offer flexible promotional opportunities for brands, artists,
            record labels, businesses, agencies, and other organizations.
          </p>

        </FadeIn>

        <div className="space-y-4">

          {/* SOLUTION 1 */}

          <FadeIn direction="up" delay={0.15}>
            <article className="rounded-2xl border border-slate-200 border-l-4 border-l-teal-500 bg-white p-6 dark:border-slate-800 dark:bg-slate-950 sm:p-8">

              <h3 className="mb-2 text-lg font-bold text-slate-900 dark:text-white">
                1. Sponsored Editorial & Featured Content
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Promote a product, service, release, campaign, event, or
                announcement through clearly identified sponsored or branded
                content created for your campaign.
              </p>

            </article>
          </FadeIn>

          {/* SOLUTION 2 */}

          <FadeIn direction="up" delay={0.3}>
            <article className="rounded-2xl border border-slate-200 border-l-4 border-l-cyan-500 bg-white p-6 dark:border-slate-800 dark:bg-slate-950 sm:p-8">

              <h3 className="mb-2 text-lg font-bold text-slate-900 dark:text-white">
                2. Music & Artist Promotion
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Give artists, labels, and music campaigns additional exposure
                through promotional placements, release features, artist
                spotlights, and other available music marketing opportunities.
              </p>

            </article>
          </FadeIn>

          {/* SOLUTION 3 */}

          <FadeIn direction="up" delay={0.45}>
            <article className="rounded-2xl border border-slate-200 border-l-4 border-l-yellow-500 bg-white p-6 dark:border-slate-800 dark:bg-slate-950 sm:p-8">

              <h3 className="mb-2 text-lg font-bold text-slate-900 dark:text-white">
                3. Display Advertising & Custom Placements
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Promote your brand through available banner placements,
                sponsored sections, homepage opportunities, and custom
                advertising packages designed around your campaign objectives.
              </p>

            </article>
          </FadeIn>

        </div>
      </section>

      {/* =====================================================
          5. PARTNERSHIP CTA
      ===================================================== */}

      <FadeIn direction="up" delay={0.1}>
        <section className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 p-8 text-center text-white shadow-2xl sm:p-14">

          <div className="pointer-events-none absolute left-1/2 top-0 h-1 w-3/4 -translate-x-1/2 bg-gradient-to-r from-transparent via-teal-500 to-transparent opacity-60" />

          <h2 className="mb-4 text-2xl font-black tracking-tight sm:text-4xl">
            Let&apos;s Build Your Campaign
          </h2>

          <p className="mx-auto mb-8 max-w-xl text-base leading-relaxed text-slate-400">
            Tell us about your brand, campaign, or promotional goals and our
            advertising team will help you explore the right VibeNationHQ
            partnership option.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">

            <a
              href={`https://wa.me/2347035101511?text=${whatsappMessage}`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full rounded-xl bg-teal-500 px-8 py-4 text-xs font-bold uppercase tracking-wider text-slate-950 shadow-md transition-all hover:-translate-y-0.5 hover:bg-teal-400 sm:w-auto"
            >
              Chat With Our Team
            </a>

            <a
              href="mailto:ads@vibenationhq.com?subject=VibeNationHQ%20Advertising%20Inquiry"
              className="w-full rounded-xl border border-slate-700 bg-slate-800 px-8 py-4 text-xs font-bold uppercase tracking-wider text-white transition-all hover:-translate-y-0.5 hover:bg-slate-700 sm:w-auto"
            >
              Email Advertising Team
            </a>

          </div>

        </section>
      </FadeIn>

    </main>
  );
}