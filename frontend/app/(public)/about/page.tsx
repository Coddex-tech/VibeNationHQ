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
    "Learn about VibeNationHQ, an African media platform covering news, music, entertainment, culture, and original analysis for audiences across Africa and beyond.",
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
    <main className="min-h-screen bg-light-bg text-light-text transition-colors duration-200 dark:bg-dark-bg dark:text-dark-text">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 md:py-16 lg:px-8 lg:py-20">

        {/* =====================================================
            HERO
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            aria-labelledby="about-page-title"
            className="relative mb-16 overflow-hidden rounded-3xl border border-dark-border bg-dark-surface px-6 py-12 text-center text-dark-text shadow-sm sm:px-12 sm:py-16 lg:px-20 lg:py-20"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-brand-teal/70" />

            <div className="relative mx-auto max-w-4xl">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-brand-teal/30 bg-brand-teal/10 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.18em] text-brand-teal-hover">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-teal" />
                Inside VibeNationHQ
              </div>

              <h1
                id="about-page-title"
                className="mb-6 text-4xl font-black leading-[1.05] tracking-[-0.04em] text-dark-text sm:text-5xl lg:text-7xl"
              >
                African News.
                <br className="hidden sm:inline" />
                <span className="text-brand-teal"> Music. Culture.</span>
              </h1>

              <p className="mx-auto max-w-2xl text-base leading-8 text-dark-text-muted sm:text-lg">
                VibeNationHQ brings together African news, music, entertainment,
                culture, and original analysis in one modern digital media
                platform.
              </p>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            ABOUT VIBENATIONHQ
        ===================================================== */}

        <FadeIn direction="up" delay={0.2}>
          <section
            className="mb-20"
            aria-labelledby="about-vibenation-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="about-vibenation-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                About VibeNationHQ
              </h2>
            </div>

            <div className="max-w-4xl space-y-5 text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              <p>
                VibeNationHQ is an African digital media platform focused on
                news, music, entertainment, culture, and original analysis.
                We are building a place where people can discover important
                stories, explore new music, follow the conversations around
                culture, and keep up with the people and moments shaping
                African media.
              </p>

              <p>
                Our editorial approach combines{" "}
                <strong className="font-bold text-light-text dark:text-dark-text">
                  factual reporting with original analysis
                </strong>
                . We aim to give readers more than headlines by providing
                useful context around the stories, releases, people, and
                developments that matter.
              </p>

              <p>
                At the same time, VibeNationHQ is designed to be more than a
                publication. It is being built as a platform where content can
                be discovered and discussed, bringing editorial media and
                community interaction together in one experience.
              </p>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            CORE COVERAGE
        ===================================================== */}

        <section className="mb-20" aria-labelledby="coverage-heading">
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-8 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="coverage-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                What We Cover
              </h2>
            </div>
          </FadeIn>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

            {/* NEWS */}

            <FadeIn direction="up" delay={0.1}>
              <article className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40">
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                  <NewsIcon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                </div>

                <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                  News & Analysis
                </h3>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                  We cover important developments across Africa with a focus
                  on factual reporting, context, and original analysis. Our
                  coverage spans areas such as politics, business, technology,
                  education, lifestyle, events, and the stories shaping
                  everyday life and culture.
                </p>
              </article>
            </FadeIn>

            {/* MUSIC */}

            <FadeIn direction="up" delay={0.2}>
              <article className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40">
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                  <MusicIcon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                </div>

                <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                  Music Discovery & Discussion
                </h3>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                  Discover African music through artists, songs, albums,
                  releases, reviews, ratings, and music conversations.
                  VibeNationHQ connects listeners with official listening
                  options while giving the community a place to discuss songs,
                  share opinions, and follow artists they care about.
                </p>
              </article>
            </FadeIn>

            {/* ENTERTAINMENT */}

            <FadeIn direction="up" delay={0.3}>
              <article className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-brand-teal/40">
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                  <FilmIcon className="h-6 w-6 transition-transform duration-200 group-hover:scale-105" />
                </div>

                <h3 className="mb-3 text-lg font-bold text-light-text dark:text-dark-text">
                  Entertainment & Culture
                </h3>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                  From entertainment news and celebrity coverage to cultural
                  stories and industry developments, we follow the people,
                  ideas, releases, and moments influencing African popular
                  culture.
                </p>
              </article>
            </FadeIn>

          </div>
        </section>

        {/* =====================================================
            MUSIC EXPERIENCE
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            className="mb-20 rounded-3xl border border-light-border bg-light-surface p-7 shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-10"
            aria-labelledby="music-experience-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="music-experience-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                A Different Way to Experience Music
              </h2>
            </div>

            <div className="max-w-4xl space-y-5 text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              <p>
                Music on VibeNationHQ is built around{" "}
                <strong className="font-bold text-light-text dark:text-dark-text">
                  discovery, context, and conversation
                </strong>
                . The platform focuses on helping listeners find songs and connect with the
                official places where they can listen.
              </p>

              <p>
                Users can explore songs through artists, tracks, and albums,
                read reviews and analysis, rate music, leave comments, and join
                discussions around individual songs. Music can also become a
                starting point for following artists and discovering related
                conversations across the platform.
              </p>

              <p>
                The goal is simple: make VibeNationHQ a place where discovering
                a song can naturally lead to discovering the artist, the story
                behind the music, and what other listeners think about it.
              </p>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            TECHNICAL CRAFTSMANSHIP
        ===================================================== */}

        <section className="mb-20" aria-labelledby="technology-heading">
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="technology-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Built for the Modern Web
              </h2>
            </div>

            <p className="mb-8 max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              VibeNationHQ is built with a focus on performance, accessibility,
              security, and a clean reading experience. Rather than relying on
              a heavy publishing theme, the platform uses a dedicated
              architecture designed around the needs of a modern digital media
              platform.
            </p>
          </FadeIn>

          <div className="space-y-4">
            {technicalPillars.map((item, index) => (
              <FadeIn
                key={item.title}
                direction="up"
                delay={0.15 * (index + 1)}
              >
                <article className="flex items-start gap-4 rounded-2xl border border-light-border bg-light-surface p-6 shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-7">
                  <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                    <CheckCircleIcon className="h-5 w-5" />
                  </div>

                  <div>
                    <h3 className="mb-1.5 text-base font-bold text-light-text dark:text-dark-text sm:text-lg">
                      {item.title}
                    </h3>

                    <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                      {item.description}
                    </p>
                  </div>
                </article>
              </FadeIn>
            ))}
          </div>
        </section>

        {/* =====================================================
            MISSION
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            className="mb-20 rounded-3xl border border-light-border bg-light-surface p-8 shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-12"
            aria-labelledby="mission-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-7 w-1 rounded-full bg-brand-teal" />

              <h2
                id="mission-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Our Mission
              </h2>
            </div>

            <p className="max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              Our mission is to document and celebrate African creativity
              while making reliable information and meaningful conversations
              easier to discover. We aim to inform readers, spotlight
              creators, encourage music discovery, and contribute to the
              global conversation around African news, entertainment, music,
              and culture.
            </p>
          </section>
        </FadeIn>

        {/* =====================================================
            CTA
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            className="relative overflow-hidden rounded-3xl border border-light-border bg-light-surface px-7 py-12 text-center text-light-text shadow-sm sm:px-12 sm:py-14 dark:border-dark-border dark:bg-dark-surface dark:text-dark-text"
            aria-labelledby="cta-heading"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-brand-teal/70" />

            <div className="relative">
              <h2
                id="cta-heading"
                className="mb-4 text-2xl font-black tracking-tight text-light-text sm:text-4xl dark:text-dark-text"
              >
                Stay in the Vibe.
              </h2>

              <p className="mx-auto mb-8 max-w-xl text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                Explore the latest African news, discover music, follow the
                conversation, and stay connected to the culture shaping the
                continent.
              </p>

              <a
                href="mailto:contact@vibenationhq.com"
                className="inline-flex items-center justify-center rounded-xl bg-brand-teal px-7 py-3.5 text-sm font-bold text-white shadow-sm transition-colors duration-200 hover:bg-brand-teal-light focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-light-surface dark:focus:ring-offset-dark-surface"
              >
                Partner With Us
              </a>
            </div>
          </section>
        </FadeIn>
      </div>
    </main>
  );
}