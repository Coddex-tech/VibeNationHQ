import type { Metadata } from "next";
import {
  CopyrightIcon,
  ShieldIcon,
  MailIcon,
  DownloadIcon,
  ScaleIcon,
} from "@/components/Icons";
import FadeIn from "@/components/FadeIn";

export const metadata: Metadata = {
  title: "DMCA Policy & Legal Disclaimer | VibeNationHQ",
  description:
    "VibeNationHQ copyright and DMCA policy, takedown procedures, content disclaimers, and intellectual property standards.",
};

export default function DmcaPage() {
  const lastUpdated = "May 13, 2026";

  const dmcaRequirements = [
    {
      title: "Identify the Copyrighted Work",
      description:
        "Provide a clear description of the copyrighted work that you believe has been infringed. Where applicable, include the title, creator, or other information that helps us identify the work.",
    },
    {
      title: "Identify the Material",
      description:
        "Provide the specific URL or other precise location on VibeNationHQ where the allegedly infringing material appears. Direct links help us investigate the report efficiently.",
    },
    {
      title: "Provide Your Contact Information",
      description:
        "Include your full name, organization or company if applicable, mailing address, telephone number, and email address so that we can contact you regarding the notice.",
    },
    {
      title: "Good-Faith Statement",
      description:
        "Include a statement that you have a good-faith belief that the disputed use of the material is not authorized by the copyright owner, its agent, or applicable law.",
    },
    {
      title: "Accuracy & Authorization",
      description:
        "Include a statement that the information in your notification is accurate and, where applicable, that you are authorized to act on behalf of the copyright owner.",
    },
    {
      title: "Electronic or Physical Signature",
      description:
        "Include a valid electronic or physical signature of the copyright owner or an authorized representative submitting the notification.",
    },
  ];

  return (
    <main className="min-h-screen bg-light-bg text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 md:py-16 lg:px-8 lg:py-20">

        {/* =====================================================
            HERO
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            aria-labelledby="dmca-page-title"
            className="relative mb-16 overflow-hidden rounded-[2rem] border border-light-border bg-dark-bg px-6 py-14 text-center text-white shadow-[0_24px_70px_rgba(0,0,0,0.12)] dark:border-dark-border sm:px-12 sm:py-18 lg:px-20 lg:py-24"
          >
            <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-dark-border-teal" />

            <div className="relative mx-auto max-w-4xl">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-dark-border-teal bg-dark-surface-teal px-4 py-2 text-[11px] font-bold uppercase tracking-[0.18em] text-brand-teal-light">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-teal" />
                Legal & Compliance
              </div>

              <h1
                id="dmca-page-title"
                className="mb-6 text-4xl font-black leading-[1.02] tracking-[-0.045em] text-white sm:text-5xl lg:text-7xl"
              >
                Copyright Notice
                <br className="hidden sm:inline" />
                <span className="text-brand-teal-light"> & DMCA</span>
              </h1>

              <p className="mx-auto max-w-2xl text-base leading-8 text-dark-text-muted sm:text-lg">
                Our copyright standards, takedown procedures, content
                disclaimers, and intellectual property practices at
                VibeNationHQ.
              </p>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            COPYRIGHT COMMITMENT
        ===================================================== */}

        <FadeIn direction="up" delay={0.2}>
          <section
            className="mb-20"
            aria-labelledby="copyright-commitment-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-8 w-1 rounded-full bg-brand-teal" />

              <h2
                id="copyright-commitment-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Our Commitment to Intellectual Property
              </h2>
            </div>

            <div className="max-w-4xl space-y-5 text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              <p>
                VibeNationHQ respects the intellectual property rights of
                creators, artists, publishers, photographers, journalists,
                labels, and other copyright holders. We aim to publish
                original reporting and properly authorized, licensed, or
                promotional material while responding responsibly to legitimate
                copyright concerns.
              </p>

              <p>
                Our music and entertainment coverage may reference or link to
                music and other creative works hosted by third-party services.
                Where applicable, those services remain responsible for the
                hosting and delivery of the underlying material.
              </p>

              <p>
                This page explains how copyright holders or their authorized
                representatives can notify us about material they believe
                infringes their rights. VibeNationHQ may consider applicable
                copyright laws and other relevant legal requirements when
                reviewing a complaint.
              </p>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            TAKEDOWN PROCEDURE
        ===================================================== */}

        <section
          className="mb-20"
          aria-labelledby="dmca-procedure-heading"
        >
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-5 flex items-center gap-3">
              <span className="h-8 w-1 rounded-full bg-brand-cyan" />

              <h2
                id="dmca-procedure-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                DMCA Takedown Procedure
              </h2>
            </div>

            <p className="mb-8 max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              If you believe material available on VibeNationHQ infringes your
              copyright, you may send us a written copyright notification.
              Providing complete and accurate information helps our team review
              the complaint efficiently.
            </p>
          </FadeIn>

          {/* REQUIREMENTS */}

          <div className="mb-8 grid grid-cols-1 gap-5 md:grid-cols-2">
            {dmcaRequirements.map((item, index) => (
              <FadeIn
                key={item.title}
                direction="up"
                delay={0.1 + index * 0.08}
              >
                <article className="h-full rounded-2xl border border-light-border bg-light-surface p-6 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-dark-border-teal sm:p-7">
                  <div className="mb-3 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.14em] text-brand-teal-dark dark:text-brand-teal-light">
                    <span className="flex h-6 w-6 items-center justify-center rounded-md border border-brand-teal/15 bg-brand-teal/10 text-[10px] dark:border-dark-border-teal dark:bg-dark-surface-teal">
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    Requirement
                  </div>

                  <h3 className="mb-2 text-lg font-black text-light-text dark:text-dark-text">
                    {item.title}
                  </h3>

                  <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                    {item.description}
                  </p>
                </article>
              </FadeIn>
            ))}
          </div>

          {/* CONTACT CARD */}

          <FadeIn direction="up" delay={0.4}>
            <article className="rounded-2xl border border-light-border border-l-4 border-l-brand-teal bg-light-surface p-6 shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-8">
              <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal-dark dark:border-dark-border-teal dark:bg-dark-surface-teal dark:text-brand-teal-light">
                    <CopyrightIcon className="h-6 w-6" />
                  </div>

                  <div>
                    <h3 className="mb-1 text-xl font-black text-light-text dark:text-dark-text">
                      Submit a Copyright Notice
                    </h3>

                    <p className="max-w-xl text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                      Send complete copyright notifications to our legal and
                      compliance desk. We will review submissions and take
                      appropriate action where warranted.
                    </p>
                  </div>
                </div>

                <a
                  href="mailto:support@vibenationhq.com"
                  className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-dark-bg px-6 py-3.5 text-xs font-black uppercase tracking-widest text-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:bg-brand-teal focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-light-surface dark:bg-dark-surface-soft dark:hover:bg-brand-teal dark:focus:ring-offset-dark-surface"
                >
                  <MailIcon className="h-4 w-4" />
                  Contact Legal Desk
                </a>
              </div>
            </article>
          </FadeIn>
        </section>

        {/* =====================================================
            CONTENT DISCLAIMER
        ===================================================== */}

        <section
          className="mb-20"
          aria-labelledby="content-disclaimer-heading"
        >
          <FadeIn direction="up" delay={0.1}>
            <div className="mb-5 flex items-center gap-3">
              <span className="h-8 w-1 rounded-full bg-brand-gold" />

              <h2
                id="content-disclaimer-heading"
                className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text sm:text-3xl"
              >
                Content & Platform Disclaimer
              </h2>
            </div>

            <p className="mb-8 max-w-4xl text-base leading-8 text-light-text-muted dark:text-dark-text-muted sm:text-lg">
              VibeNationHQ provides news, entertainment, music discovery, and
              cultural information for general informational and entertainment
              purposes. Although we make reasonable efforts to maintain
              accurate and current information, circumstances can change and
              published material may require correction or updating.
            </p>
          </FadeIn>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

            {/* NEWS ACCURACY */}

            <FadeIn direction="up" delay={0.15}>
              <article className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-teal/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-dark-border-teal sm:p-8">
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal-dark dark:border-dark-border-teal dark:bg-dark-surface-teal dark:text-brand-teal-light">
                  <ShieldIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-105" />
                </div>

                <h3 className="mb-3 text-lg font-black text-light-text dark:text-dark-text">
                  News & Editorial Content
                </h3>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                  We work to distinguish reporting, analysis, commentary, and
                  promotional material. Breaking stories may develop after
                  publication, so readers should consider the publication date
                  and subsequent updates when relying on reported information.
                </p>
              </article>
            </FadeIn>

            {/* MUSIC DISCOVERY */}

            <FadeIn direction="up" delay={0.3}>
              <article className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-cyan/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface dark:hover:border-cyan-800 sm:p-8">
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-cyan/20 bg-brand-cyan/10 text-cyan-600 dark:border-cyan-900/70 dark:bg-[#16363b] dark:text-cyan-300">
                  <DownloadIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-105" />
                </div>

                <h3 className="mb-3 text-lg font-black text-light-text dark:text-dark-text">
                  Music Discovery & External Media
                </h3>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                  VibeNationHQ does not operate as a general-purpose MP3
                  download or music-hosting service. Our music features may
                  include artist and song information, reviews, ratings,
                  promotional material, and links or embeds that direct users
                  to official or authorized third-party listening platforms.
                </p>
              </article>
            </FadeIn>

            {/* THIRD PARTY */}

            <FadeIn direction="up" delay={0.45}>
              <article className="group h-full rounded-2xl border border-light-border bg-light-surface p-7 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-gold/40 hover:shadow-md dark:border-dark-border dark:bg-dark-surface sm:p-8">
                <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-gold/20 bg-brand-gold/10 text-yellow-600 dark:border-yellow-900/70 dark:bg-[#3a351d] dark:text-yellow-300">
                  <ScaleIcon className="h-6 w-6 transition-transform duration-300 group-hover:scale-105" />
                </div>

                <h3 className="mb-3 text-lg font-black text-light-text dark:text-dark-text">
                  Third-Party Services
                </h3>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted">
                  VibeNationHQ may link to or embed content from third-party
                  platforms. Those services operate independently and may have
                  their own terms, privacy policies, cookies, licensing
                  arrangements, and data practices.
                </p>
              </article>
            </FadeIn>
          </div>
        </section>

        {/* =====================================================
            COPYRIGHT OWNERSHIP & CORRECTIONS
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            className="mb-20 rounded-[2rem] border border-light-border bg-light-surface p-7 shadow-sm dark:border-dark-border dark:bg-dark-surface-soft sm:p-10"
            aria-labelledby="copyright-concerns-heading"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-dark-border bg-dark-bg text-white dark:border-dark-border-soft dark:bg-dark-surface dark:text-dark-text">
                <CopyrightIcon className="h-5 w-5" />
              </div>

              <div>
                <h2
                  id="copyright-concerns-heading"
                  className="mb-3 text-xl font-black text-light-text dark:text-dark-text sm:text-2xl"
                >
                  Copyright Concerns & Corrections
                </h2>

                <p className="mb-4 text-sm leading-7 text-light-text-muted dark:text-dark-text-muted sm:text-base">
                  If you believe that material published by VibeNationHQ
                  infringes your copyright, contains an attribution error, or
                  otherwise requires legal clarification, please contact our
                  team with sufficient information for us to investigate.
                </p>

                <p className="text-sm leading-7 text-light-text-muted dark:text-dark-text-muted sm:text-base">
                  We may remove, restrict, correct, or otherwise modify content
                  where appropriate following our review and applicable legal
                  requirements.
                </p>
              </div>
            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            LIMITATION OF LIABILITY
        ===================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            className="mb-20 rounded-[2rem] border border-light-border bg-light-surface p-7 shadow-sm dark:border-dark-border dark:bg-dark-surface sm:p-10"
            aria-labelledby="liability-heading"
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="h-8 w-1 rounded-full bg-brand-gold" />

              <h2
                id="liability-heading"
                className="text-xl font-black text-light-text dark:text-dark-text sm:text-2xl"
              >
                Limitation of Liability
              </h2>
            </div>

            <p className="max-w-4xl text-sm leading-7 text-light-text-muted dark:text-dark-text-muted sm:text-base">
              To the extent permitted by applicable law, VibeNationHQ and its
              contributors are not responsible for losses or damages arising
              from reliance on information published on the platform,
              temporary service interruptions, third-party websites or
              services, or material supplied or delivered through third-party
              platforms. Nothing in this policy is intended to exclude rights
              or protections that cannot lawfully be excluded.
            </p>
          </section>
        </FadeIn>

        {/* =====================================================
    FINAL CTA
====================================================== */}

        <FadeIn direction="up" delay={0.1}>
          <section
            aria-labelledby="dmca-cta-heading"
            className="rounded-[2rem] border border-light-border bg-light-surface px-7 py-12 text-center text-light-text sm:px-12 sm:py-16 dark:border-dark-border-teal dark:bg-dark-surface-teal dark:text-dark-text"
          >
            <div className="mx-auto max-w-3xl">
              <div className="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal dark:border-dark-border-teal dark:bg-dark-surface-teal-soft dark:text-brand-teal-light">
                <CopyrightIcon className="h-5 w-5" />
              </div>

              <h3
                id="dmca-cta-heading"
                className="mb-4 text-2xl font-black tracking-tight text-light-text sm:text-4xl dark:text-dark-text"
              >
                Copyright. Integrity. Accountability.
              </h3>

              <p className="mx-auto mb-8 max-w-xl text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                We are committed to respecting creators and rights holders
                while maintaining a reliable and transparent media platform
                for our audience.
              </p>

              <a
                href="mailto:support@vibenationhq.com"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-teal px-7 py-3.5 text-xs font-black uppercase tracking-widest text-white shadow-sm transition-colors duration-200 hover:bg-brand-teal-light focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-light-surface dark:focus:ring-offset-dark-surface-teal"
              >
                <MailIcon className="h-4 w-4" />
                Contact Copyright Desk
              </a>

              <div className="mt-8 border-t border-light-border pt-6 dark:border-dark-border-teal">
                <p className="text-xs text-light-text-soft dark:text-dark-text-soft">
                  Last Updated:{" "}
                  <span className="font-medium text-light-text-muted dark:text-dark-text-muted">
                    {lastUpdated}
                  </span>
                </p>
              </div>
            </div>
          </section>
        </FadeIn>
      </div>
    </main>
  );
}