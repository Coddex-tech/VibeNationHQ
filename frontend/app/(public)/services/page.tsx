import type { Metadata } from 'next';
import {
  ScaleIcon,
  CopyrightIcon,
  ShieldCheckIcon,
  DocumentIcon,
  AlertTriangleIcon,
  RefreshIcon,
  MailIcon,
  MusicIcon,
  CheckCircleIcon,
} from '@/components/Icons';
import FadeIn from '@/components/FadeIn';

export const metadata: Metadata = {
  title: 'Terms of Service | VibeNationHQ',
  description:
    'The official Terms of Service for VibeNationHQ. Understand the rules governing use of our news, music discovery, entertainment, culture, and media platform.',
};

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 md:py-20 overflow-hidden">

        {/* =====================================================
            1. GOVERNANCE HERO
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="relative rounded-3xl bg-dark-bg text-dark-text p-7 sm:p-12 lg:p-20 text-center mb-14 sm:mb-16 border border-dark-border-teal overflow-hidden">

            <div className="relative z-10">

              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-dark-border-teal bg-dark-surface-teal text-brand-teal-light text-[11px] sm:text-xs font-bold uppercase tracking-[0.18em] mb-6">
                <ScaleIcon className="w-4 h-4 shrink-0" />
                Terms & Platform Rules
              </div>

              <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] mb-6 text-dark-text">
                Terms of{' '}
                <span className="text-brand-teal-light">
                  Service
                </span>
              </h1>

              <p className="text-sm sm:text-base lg:text-lg text-dark-text-muted max-w-2xl mx-auto leading-relaxed">
                The framework governing your use of the VibeNationHQ digital
                media platform.
              </p>

            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            2. ACCEPTANCE OF TERMS
        ====================================================== */}
        <FadeIn direction="up" delay={0.15}>
          <section className="mb-14 sm:mb-16">

            <div className="flex items-center gap-3 mb-4">
              <span className="w-1.5 h-7 sm:h-8 bg-brand-teal rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                1. Acceptance of Terms
              </h2>
            </div>

            <p className="text-light-text-muted dark:text-dark-text-muted leading-relaxed text-base sm:text-lg max-w-4xl">
              By accessing or using{' '}
              <strong className="text-light-text dark:text-dark-text font-bold">
                VibeNationHQ
              </strong>
              , you agree to comply with these Terms of Service and applicable
              laws and regulations. VibeNationHQ provides news, music discovery,
              entertainment, cultural content, community features, and related
              media services through its digital platform.
            </p>

            <p className="mt-4 text-light-text-muted dark:text-dark-text-muted leading-relaxed text-base sm:text-lg max-w-4xl">
              If you do not agree with these terms, please discontinue use of
              the platform.
            </p>

          </section>
        </FadeIn>

        {/* =====================================================
            3. CORE GOVERNANCE PRINCIPLES
        ====================================================== */}
        <section className="mb-16 sm:mb-20">

          <FadeIn direction="up" delay={0.1}>
            <div className="flex items-center gap-3 mb-7">

              <span className="w-1.5 h-7 sm:h-8 bg-brand-cyan rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                Core Governance Principles
              </h2>

            </div>
          </FadeIn>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6">

            {/* Intellectual Property */}
            <FadeIn direction="up" delay={0.15}>
              <div className="h-full p-6 sm:p-8 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface transition-colors duration-300 hover:border-brand-teal/40 dark:hover:border-brand-teal/50">

                <div className="w-12 h-12 rounded-xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light flex items-center justify-center mb-6 border border-brand-teal/15">
                  <CopyrightIcon className="w-6 h-6" />
                </div>

                <h3 className="text-lg font-black text-light-text dark:text-dark-text mb-3">
                  Intellectual Property
                </h3>

                <p className="text-light-text-muted dark:text-dark-text-muted text-sm leading-relaxed">
                  Original VibeNationHQ articles, analysis, branding, visual
                  assets, software, designs, and other original materials are
                  protected by applicable intellectual property laws. Unauthorized
                  reproduction, substantial copying, scraping, or commercial
                  redistribution of protected VibeNationHQ content is prohibited
                  unless permission or applicable law allows it.
                </p>

              </div>
            </FadeIn>

            {/* Editorial Integrity */}
            <FadeIn direction="up" delay={0.25}>
              <div className="h-full p-6 sm:p-8 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface transition-colors duration-300 hover:border-brand-cyan/40 dark:hover:border-brand-cyan/50">

                <div className="w-12 h-12 rounded-xl bg-brand-cyan/10 text-brand-cyan dark:bg-brand-cyan/15 flex items-center justify-center mb-6 border border-brand-cyan/15">
                  <ScaleIcon className="w-6 h-6" />
                </div>

                <h3 className="text-lg font-black text-light-text dark:text-dark-text mb-3">
                  Editorial Integrity
                </h3>

                <p className="text-light-text-muted dark:text-dark-text-muted text-sm leading-relaxed">
                  VibeNationHQ combines reporting, commentary, reviews, and
                  editorial analysis. We aim to provide useful and accurate
                  information, but news, entertainment, music releases, public
                  information, and other content can change over time. Content
                  should not be treated as a guarantee of completeness or
                  accuracy in every circumstance.
                </p>

              </div>
            </FadeIn>

            {/* Platform Security */}
            <FadeIn direction="up" delay={0.35}>
              <div className="h-full p-6 sm:p-8 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface transition-colors duration-300 hover:border-brand-gold/40 dark:hover:border-brand-gold/50">

                <div className="w-12 h-12 rounded-xl bg-brand-gold/10 text-brand-gold dark:bg-brand-gold/10 flex items-center justify-center mb-6 border border-brand-gold/15">
                  <ShieldCheckIcon className="w-6 h-6" />
                </div>

                <h3 className="text-lg font-black text-light-text dark:text-dark-text mb-3">
                  Platform Security
                </h3>

                <p className="text-light-text-muted dark:text-dark-text-muted text-sm leading-relaxed">
                  Users must not attempt to compromise, disrupt, reverse
                  engineer, exploit, or gain unauthorized access to VibeNationHQ
                  systems, APIs, databases, accounts, or other technical
                  infrastructure.
                </p>

              </div>
            </FadeIn>

          </div>
        </section>

        {/* =====================================================
            4. PERMITTED USE & LICENSING
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="mb-14 sm:mb-16">

            <div className="flex items-center gap-3 mb-4">

              <span className="w-1.5 h-7 sm:h-8 bg-brand-teal rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                2. Permitted Use & Licensing
              </h2>

            </div>

            <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl mb-7">
              VibeNationHQ provides users with a limited, non-exclusive,
              non-transferable right to access and use the platform for lawful
              purposes, subject to these terms and any additional rules that
              apply to specific features.
            </p>

            <div className="space-y-4">

              {/* News */}
              <div className="flex items-start gap-4 p-5 sm:p-6 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface">

                <div className="w-10 h-10 rounded-xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light flex items-center justify-center shrink-0">
                  <DocumentIcon className="w-5 h-5" />
                </div>

                <div>
                  <h3 className="text-base sm:text-lg font-bold text-light-text dark:text-dark-text mb-1">
                    News & Editorial Content
                  </h3>

                  <p className="text-sm sm:text-base text-light-text-muted dark:text-dark-text-muted leading-relaxed">
                    You may share links to VibeNationHQ articles and reference
                    our reporting provided that appropriate attribution is
                    maintained. Republishing substantial portions of our
                    original articles or systematically reproducing our content
                    without permission is not permitted.
                  </p>
                </div>

              </div>

              {/* Music */}
              <div className="flex items-start gap-4 p-5 sm:p-6 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface">

                <div className="w-10 h-10 rounded-xl bg-brand-cyan/10 text-brand-cyan dark:bg-brand-cyan/15 flex items-center justify-center shrink-0">
                  <MusicIcon className="w-5 h-5" />
                </div>

                <div>
                  <h3 className="text-base sm:text-lg font-bold text-light-text dark:text-dark-text mb-1">
                    Music Discovery & Discussion
                  </h3>

                  <p className="text-sm sm:text-base text-light-text-muted dark:text-dark-text-muted leading-relaxed">
                    VibeNationHQ may provide music discovery features including
                    artist, track, and album information, release coverage,
                    reviews, ratings, editorial analysis, user discussions,
                    comments, and related promotional content. Where listening
                    access is provided, VibeNationHQ may link to or embed
                    official or authorized third-party platforms.
                  </p>

                  <p className="text-sm sm:text-base text-light-text-muted dark:text-dark-text-muted leading-relaxed mt-3">
                    VibeNationHQ does not grant users ownership of music or other
                    copyrighted media featured on the platform. Any music,
                    artwork, recordings, or other third-party material remains
                    subject to the rights and terms of its respective owners and
                    platforms.
                  </p>
                </div>

              </div>

            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            5. USER CONTENT & COMMUNITY
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="mb-14 sm:mb-16">

            <div className="flex items-center gap-3 mb-4">

              <span className="w-1.5 h-7 sm:h-8 bg-brand-cyan rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                3. User Content & Community
              </h2>

            </div>

            <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl mb-5">
              Where VibeNationHQ allows users to publish comments, replies,
              discussions, reviews, ratings, or other user-generated content,
              users are responsible for the material they submit.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

              {[
                'Do not submit content that is unlawful, fraudulent, threatening, or deliberately misleading.',
                'Do not infringe the copyright, trademark, privacy, or other rights of another person or organization.',
                'Do not impersonate another person, artist, organization, or VibeNationHQ representative.',
                'Do not use community features to distribute spam, malicious links, scams, or harmful material.',
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-start gap-3 p-5 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface"
                >
                  <CheckCircleIcon className="w-5 h-5 text-brand-teal dark:text-brand-teal-light shrink-0 mt-0.5" />

                  <p className="text-sm sm:text-base leading-relaxed text-light-text-muted dark:text-dark-text-muted">
                    {item}
                  </p>
                </div>
              ))}

            </div>

            <p className="text-light-text-muted dark:text-dark-text-muted text-sm sm:text-base leading-relaxed max-w-4xl mt-5">
              VibeNationHQ may moderate, restrict, remove, or otherwise act on
              user-generated content where reasonably necessary to enforce these
              terms, protect users, comply with applicable law, or maintain the
              integrity of the platform.
            </p>

          </section>
        </FadeIn>

        {/* =====================================================
            6. PROHIBITED CONDUCT
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="mb-14 sm:mb-16">

            <div className="flex items-center gap-3 mb-4">

              <span className="w-1.5 h-7 sm:h-8 bg-red-500 rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                4. Prohibited Conduct
              </h2>

            </div>

            <div className="rounded-2xl border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 p-6 sm:p-8">

              <div className="flex items-start gap-4">

                <div className="w-10 h-10 rounded-xl bg-red-500/10 text-red-600 dark:text-red-400 flex items-center justify-center shrink-0">
                  <AlertTriangleIcon className="w-5 h-5" />
                </div>

                <div>

                  <p className="text-light-text-muted dark:text-dark-text-muted text-sm sm:text-base leading-relaxed mb-4">
                    You agree not to use VibeNationHQ to:
                  </p>

                  <ul className="space-y-3 text-sm sm:text-base text-light-text-muted dark:text-dark-text-muted list-disc pl-5">
                    <li>
                      Attempt unauthorized access to our systems, APIs,
                      databases, accounts, or administrative tools.
                    </li>

                    <li>
                      Introduce malware, malicious scripts, harmful code, or
                      other technologies intended to damage or disrupt the
                      platform.
                    </li>

                    <li>
                      Interfere with the availability, security, or normal
                      operation of VibeNationHQ.
                    </li>

                    <li>
                      Scrape, harvest, or systematically reproduce substantial
                      portions of our content without permission.
                    </li>

                    <li>
                      Impersonate VibeNationHQ, its staff, contributors,
                      partners, artists, or other individuals or organizations.
                    </li>

                    <li>
                      Upload, publish, or distribute content that infringes
                      another person's intellectual property or other legal
                      rights.
                    </li>

                    <li>
                      Use the platform for unlawful, fraudulent, abusive, or
                      deceptive purposes.
                    </li>
                  </ul>

                </div>
              </div>

            </div>
          </section>
        </FadeIn>

        {/* =====================================================
            7. THIRD-PARTY SERVICES & LINKS
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="mb-14 sm:mb-16">

            <div className="flex items-center gap-3 mb-4">

              <span className="w-1.5 h-7 sm:h-8 bg-brand-teal rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                5. Third-Party Services & Links
              </h2>

            </div>

            <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl">
              VibeNationHQ may link to or integrate third-party services,
              including music streaming platforms, video platforms, social
              networks, advertising services, analytics providers, payment
              services, and other external websites or applications.
            </p>

            <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl mt-4">
              Third-party services operate independently from VibeNationHQ and
              may have their own terms, privacy policies, content rules, and
              licensing arrangements. Your use of those services is subject to
              the terms established by the relevant third party.
            </p>

          </section>
        </FadeIn>

        {/* =====================================================
            8. LIMITATION OF LIABILITY
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="mb-14 sm:mb-16">

            <div className="flex items-center gap-3 mb-4">

              <span className="w-1.5 h-7 sm:h-8 bg-brand-gold rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                6. Limitation of Liability
              </h2>

            </div>

            <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl">
              VibeNationHQ strives to maintain a reliable and secure platform,
              but we do not guarantee that the service will always be
              uninterrupted, completely error-free, or continuously available.
              To the extent permitted by applicable law, VibeNationHQ is not
              responsible for losses arising from reliance on information
              published on the platform, temporary service interruptions,
              technical failures, or the acts or omissions of third-party
              services.
            </p>

          </section>
        </FadeIn>

        {/* =====================================================
            9. SERVICE EVOLUTION
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="mb-16 sm:mb-20">

            <div className="flex items-center gap-3 mb-4">

              <span className="w-1.5 h-7 sm:h-8 bg-brand-cyan rounded-full shrink-0" />

              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                7. Service Evolution
              </h2>

            </div>

            <div className="flex items-start gap-4 p-6 sm:p-8 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface-soft dark:bg-dark-surface-soft">

              <div className="w-11 h-11 rounded-xl bg-brand-cyan/10 text-brand-cyan dark:bg-brand-cyan/15 flex items-center justify-center shrink-0">
                <RefreshIcon className="w-5 h-5" />
              </div>

              <p className="text-light-text-muted dark:text-dark-text-muted text-sm sm:text-base leading-relaxed">
                VibeNationHQ may modify, improve, suspend, restrict, or
                discontinue features of the platform as our technology,
                editorial operations, community features, and business needs
                evolve. Where appropriate, significant changes to these Terms
                of Service will be reflected on this page.
              </p>

            </div>
          </section>
        </FadeIn>

        {/* =====================================================
         10. CONTACT / FINAL GOVERNANCE CARD
        ====================================================== */}
        <FadeIn direction="up" delay={0.1}>
          <section className="rounded-3xl bg-light-surface dark:bg-dark-surface-teal text-light-text dark:text-dark-text p-8 sm:p-12 text-center border border-light-border dark:border-dark-border-teal">

            <div className="w-12 h-12 mx-auto rounded-xl bg-brand-teal/10 text-brand-teal dark:text-brand-teal-light flex items-center justify-center mb-5 border border-brand-teal/20 dark:border-dark-border-teal">
              <ScaleIcon className="w-6 h-6" />
            </div>

            <h3 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight mb-3 text-light-text dark:text-dark-text">
              Questions About These Terms?
            </h3>

            <p className="text-light-text-muted dark:text-dark-text-muted text-sm sm:text-base max-w-xl mx-auto mb-7 leading-relaxed">
              If you have questions about these Terms of Service, platform
              policies, or how a particular feature works, our legal desk is
              available to assist.
            </p>

            <a
              href="mailto:legal@vibenationhq.com"
              className="inline-flex items-center justify-center gap-2 bg-brand-teal hover:bg-brand-teal-light text-white font-bold px-6 sm:px-8 py-3.5 sm:py-4 rounded-xl uppercase tracking-wider text-[11px] sm:text-xs transition-colors"
            >
              <MailIcon className="w-4 h-4" />
              Contact Legal Desk
            </a>

            <p className="mt-6 text-xs text-light-text-soft dark:text-dark-text-soft">
              <strong className="text-light-text-muted dark:text-dark-text-muted">
                Effective Date:
              </strong>{' '}
              May 13, 2026
            </p>

          </section>
        </FadeIn>

      </div>
    </main>
  );
}