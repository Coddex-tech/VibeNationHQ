import type { Metadata } from "next";
import {
  NewsIcon,
  MusicIcon,
  FilmIcon,
  CheckCircleIcon,
} from "@/components/Icons";
import FadeIn from "@/components/FadeIn";

export const metadata: Metadata = {
  title: "About VibeNationHQ | African News, Music & Entertainment",
  description:
    "Learn about VibeNationHQ, an African media platform covering news, music, entertainment, culture, and original analysis for readers across Africa and beyond.",
};

export default function AboutPage() {
  const technicalPillars = [
    {
      title: "Optimized for Mobile Performance",
      description:
        "Designed for fast, efficient delivery across a wide range of devices and network conditions, with a focus on responsive performance and a smooth reading experience.",
    },
    {
      title: "Integrity-First Engagement",
      description:
        "A purpose-built comment and engagement system designed to reduce spam, automated activity, and low-quality interactions while keeping conversations useful.",
    },
    {
      title: "Search-Optimized Architecture",
      description:
        "A semantic, performance-focused web architecture designed to help search engines discover, understand, and index VibeNationHQ content effectively.",
    },
  ];

  return (
    <main className="mx-auto max-w-6xl overflow-hidden px-4 py-12 sm:px-6 md:py-20 lg:px-8">

      {/* =====================================================
          1. BRAND HERO
      ===================================================== */}

      <FadeIn direction="up" delay={0.1}>
        <section
          aria-labelledby="about-page-title"
          className="relative mb-16 overflow-hidden rounded-3xl border border-slate-800 bg-slate-950 p-8 text-center text-white shadow-2xl sm:p-14 lg:p-20"
        >
          <div className="pointer-events-none absolute -left-32 -top-32 h-80 w-80 rounded-full bg-teal-500/20 blur-[100px]" />
          <div className="pointer-events-none absolute -bottom-32 -right-32 h-80 w-80 rounded-full bg-cyan-500/20 blur-[100px]" />

          <div className="relative">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-3.5 py-1.5 text-xs font-semibold uppercase tracking-widest text-teal-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-teal-400" />
              Inside VibeNationHQ
            </div>

            <h1
              id="about-page-title"
              className="mb-6 text-3xl font-black leading-[1.1] tracking-tight text-white sm:text-5xl lg:text-6xl"
            >
              African News.
              <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-teal-400 via-cyan-400 to-yellow-400 bg-clip-text text-transparent">
                {" "}
                Music. Culture.
              </span>
            </h1>

            <p className="mx-auto max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg">
              VibeNationHQ brings together African news, music, entertainment,
              culture, and original analysis in one modern digital media
              platform.
            </p>
          </div>
        </section>
      </FadeIn>

      {/* =====================================================
          2. ABOUT VIBENATIONHQ
      ===================================================== */}

      <FadeIn direction="up" delay={0.2}>
        <section className="mb-16" aria-labelledby="about-vibenation-heading">
          <div className="mb-4 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-teal-500" />

            <h2
              id="about-vibenation-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              About VibeNationHQ
            </h2>
          </div>

          <div className="max-w-4xl space-y-4 text-base leading-relaxed text-slate-600 dark:text-slate-300 sm:text-lg">
            <p>
              VibeNationHQ is a digital media platform focused on African news,
              music, entertainment, and culture. Our goal is to make important
              stories easier to discover while giving readers context,
              analysis, and a modern reading experience.
            </p>

            <p>
              Our editorial approach combines{" "}
              <strong className="font-bold text-slate-900 dark:text-white">
                factual reporting with original analysis
              </strong>
              . We cover developments across the African creative and
              entertainment landscape while providing stories that help readers
              understand not only what happened, but why it matters.
            </p>
          </div>
        </section>
      </FadeIn>

      {/* =====================================================
          3. CORE COVERAGE
      ===================================================== */}

      <section className="mb-20" aria-labelledby="coverage-heading">
        <FadeIn direction="up" delay={0.1}>
          <div className="mb-8 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-cyan-500" />

            <h2
              id="coverage-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              What We Cover
            </h2>
          </div>
        </FadeIn>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

          {/* NEWS */}

          <FadeIn direction="up" delay={0.1}>
            <article className="group h-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-teal-500/50 hover:shadow-md dark:border-slate-800 dark:bg-slate-950">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400">
                <NewsIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-110" />
              </div>

              <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
                News & Analysis
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                We cover important developments across Africa with a focus on
                factual reporting, context, and original analysis. Our stories
                aim to help readers understand the events shaping society,
                business, entertainment, and culture.
              </p>
            </article>
          </FadeIn>

          {/* MUSIC */}

          <FadeIn direction="up" delay={0.25}>
            <article className="group h-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-cyan-500/50 hover:shadow-md dark:border-slate-800 dark:bg-slate-950">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
                <MusicIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-110" />
              </div>

              <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
                Music Discovery
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                Discover African music through artist coverage, releases,
                music news, charts, and available promotional downloads. We
                connect audiences with the sounds and creators shaping the
                continent&apos;s music scene.
              </p>
            </article>
          </FadeIn>

          {/* ENTERTAINMENT */}

          <FadeIn direction="up" delay={0.4}>
            <article className="group h-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-yellow-500/50 hover:shadow-md dark:border-slate-800 dark:bg-slate-950">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-500/10 text-yellow-600 dark:text-yellow-400">
                <FilmIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-110" />
              </div>

              <h3 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
                Entertainment & Culture
              </h3>

              <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                From entertainment news and celebrity coverage to cultural
                stories and industry developments, our platform follows the
                people, ideas, and moments influencing African popular culture.
              </p>
            </article>
          </FadeIn>

        </div>
      </section>

      {/* =====================================================
          4. TECHNICAL CRAFTSMANSHIP
      ===================================================== */}

      <section className="mb-20" aria-labelledby="technology-heading">
        <FadeIn direction="up" delay={0.1}>
          <div className="mb-4 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-cyan-500" />

            <h2
              id="technology-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              Built for the Modern Web
            </h2>
          </div>

          <p className="mb-8 max-w-4xl text-base leading-relaxed text-slate-600 dark:text-slate-300 sm:text-lg">
            VibeNationHQ is built with a focus on performance, accessibility,
            security, and a clean reading experience. Rather than relying on a
            heavy publishing theme, the platform uses a dedicated architecture
            designed around the needs of a modern digital media publication.
          </p>
        </FadeIn>

        <div className="space-y-4">
          {technicalPillars.map((item, index) => (
            <FadeIn
              key={item.title}
              direction="up"
              delay={0.15 * (index + 1)}
            >
              <article className="flex items-start gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-8">
                <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400">
                  <CheckCircleIcon className="h-5 w-5" />
                </div>

                <div>
                  <h3 className="mb-1 text-base font-bold text-slate-900 dark:text-white sm:text-lg">
                    {item.title}
                  </h3>

                  <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                    {item.description}
                  </p>
                </div>
              </article>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* =====================================================
          5. MISSION
      ===================================================== */}

      <FadeIn direction="up" delay={0.1}>
        <section
          className="mb-20 rounded-3xl border border-slate-200 bg-slate-50 p-8 dark:border-slate-800 dark:bg-slate-900/50 sm:p-12"
          aria-labelledby="mission-heading"
        >
          <div className="mb-4 flex items-center gap-3">
            <span className="h-7 w-1.5 shrink-0 rounded-full bg-yellow-500" />

            <h2
              id="mission-heading"
              className="text-2xl font-black tracking-tight text-slate-900 dark:text-white sm:text-3xl"
            >
              Our Mission
            </h2>
          </div>

          <p className="max-w-4xl text-base leading-relaxed text-slate-600 dark:text-slate-300 sm:text-lg">
            Our mission is to document and celebrate African creativity while
            making reliable information easier to discover. We aim to inform
            readers, spotlight creators, and contribute to the global
            conversation around African music, news, entertainment, and
            culture.
          </p>
        </section>
      </FadeIn>

      {/* =====================================================
          6. CTA
      ===================================================== */}

      <FadeIn direction="up" delay={0.1}>
        <section className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 p-8 text-center text-white shadow-2xl sm:p-14">
          <h2 className="mb-4 text-2xl font-black tracking-tight text-white sm:text-4xl">
            Discover. Read. Download. Vibe.
          </h2>

          <p className="mx-auto mb-8 max-w-xl text-base leading-relaxed text-slate-400">
            Explore the latest African news, music, entertainment, and culture
            from VibeNationHQ.
          </p>

          <a
            href="mailto:contact@vibenationhq.com"
            className="inline-flex items-center justify-center rounded-xl bg-teal-500 px-8 py-4 text-xs font-bold uppercase tracking-wider text-slate-950 shadow-md transition-all hover:-translate-y-0.5 hover:bg-teal-400 sm:text-sm"
          >
            Partner With Us
          </a>
        </section>
      </FadeIn>

    </main>
  );
}