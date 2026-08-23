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
} from '@/components/Icons';
import FadeIn from '@/components/FadeIn';

export const metadata: Metadata = {
  title: 'Terms of Service | VibeNationHQ Corporate Governance',
  description:
    'The official terms of service for VibeNationHQ. Understand the legal framework governing our news, music discovery, and media platform.',
};

export default function TermsPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 md:py-20 overflow-hidden">

      {/* =====================================================
          1. GOVERNANCE HERO
      ====================================================== */}
      <FadeIn direction="up" delay={0.1}>
        <section className="relative rounded-3xl bg-slate-950 text-white p-7 sm:p-12 lg:p-20 text-center mb-14 sm:mb-16 border border-slate-800 shadow-2xl overflow-hidden">

          {/* Decorative glow */}
          <div className="absolute -top-32 -left-32 w-80 h-80 bg-teal-500/20 rounded-full blur-[100px] pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-80 h-80 bg-cyan-500/20 rounded-full blur-[100px] pointer-events-none" />

          {/* Badge */}
          <div className="relative inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 text-teal-300 text-[11px] sm:text-xs font-bold uppercase tracking-[0.18em] mb-6">
            <ScaleIcon className="w-4 h-4 shrink-0" />
            Corporate Governance
          </div>

          {/* Heading */}
          <h1 className="relative text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] mb-6 text-white">
            Terms of{' '}
            <span className="bg-gradient-to-r from-teal-300 via-cyan-400 to-yellow-400 bg-clip-text text-transparent">
              Service
            </span>
          </h1>

          <p className="relative text-sm sm:text-base lg:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            The framework governing your use of the VibeNationHQ digital
            ecosystem.
          </p>
        </section>
      </FadeIn>

      {/* =====================================================
          2. ACCEPTANCE OF TERMS
      ====================================================== */}
      <FadeIn direction="up" delay={0.15}>
        <section className="mb-14 sm:mb-16">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-7 sm:h-8 bg-teal-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              1. Acceptance of Terms
            </h2>
          </div>

          <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
            By accessing or using <strong className="text-slate-900 dark:text-white font-bold">
              VibeNationHQ
            </strong>
            , you agree to comply with these Terms of Service and all
            applicable laws and regulations. VibeNationHQ provides news,
            music discovery, entertainment, and cultural content through a
            technology-driven media platform.
          </p>

          <p className="mt-4 text-slate-600 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
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
            <span className="w-1.5 h-7 sm:h-8 bg-cyan-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              Core Governance Principles
            </h2>
          </div>
        </FadeIn>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6">

          {/* Intellectual Property */}
          <FadeIn direction="up" delay={0.15}>
            <div className="h-full p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:border-teal-500/50 hover:shadow-md transition-all duration-300">

              <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-6 border border-teal-500/10">
                <CopyrightIcon className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                Intellectual Property
              </h3>

              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                Original VibeNationHQ articles, analysis, branding, visual
                assets, software, and other original materials are protected
                by applicable intellectual property laws. Unauthorized
                reproduction, scraping, commercial redistribution, or
                substantial copying of original content is prohibited.
              </p>
            </div>
          </FadeIn>

          {/* Editorial Integrity */}
          <FadeIn direction="up" delay={0.25}>
            <div className="h-full p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:border-cyan-500/50 hover:shadow-md transition-all duration-300">

              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-6 border border-cyan-500/10">
                <ScaleIcon className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                Editorial Integrity
              </h3>

              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                VibeNationHQ combines factual reporting with editorial
                analysis. While we make reasonable efforts to maintain
                accuracy, news and entertainment information can change
                rapidly. Content is provided for general informational and
                entertainment purposes.
              </p>
            </div>
          </FadeIn>

          {/* Platform Security */}
          <FadeIn direction="up" delay={0.35}>
            <div className="h-full p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:border-amber-500/50 hover:shadow-md transition-all duration-300">

              <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-6 border border-amber-500/10">
                <ShieldCheckIcon className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                Platform Security
              </h3>

              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                Users must not attempt to compromise, disrupt, reverse
                engineer, exploit, or gain unauthorized access to VibeNationHQ
                systems, APIs, databases, or other technical infrastructure.
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
            <span className="w-1.5 h-7 sm:h-8 bg-teal-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              2. Permitted Use & Licensing
            </h2>
          </div>

          <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg leading-relaxed max-w-4xl mb-7">
            VibeNationHQ grants visitors a limited, non-exclusive,
            non-transferable right to access and use the platform for
            personal, lawful, and non-commercial purposes, subject to these
            terms.
          </p>

          <div className="space-y-4">

            {/* News */}
            <div className="flex items-start gap-4 p-5 sm:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center shrink-0">
                <DocumentIcon className="w-5 h-5" />
              </div>

              <div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white mb-1">
                  News & Editorial Content
                </h3>

                <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
                  You may share links to VibeNationHQ articles and reference
                  our reporting provided that proper attribution and a direct
                  link to the original article are maintained.
                </p>
              </div>
            </div>

            {/* Music */}
            <div className="flex items-start gap-4 p-5 sm:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
                <MusicIcon className="w-5 h-5" />
              </div>

              <div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white mb-1">
                  Music
                </h3>

                <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
                  Music and other media made available through VibeNationHQ
                  may be subject to rights held by artists, labels,
                  distributors, or other third parties. Users are responsible
                  for complying with applicable copyright and licensing
                  restrictions.
                </p>
              </div>
            </div>

          </div>
        </section>
      </FadeIn>

      {/* =====================================================
          5. PROHIBITED CONDUCT
      ====================================================== */}
      <FadeIn direction="up" delay={0.1}>
        <section className="mb-14 sm:mb-16">

          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-7 sm:h-8 bg-red-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              Prohibited Conduct
            </h2>
          </div>

          <div className="rounded-2xl border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 p-6 sm:p-8">

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-red-500/10 text-red-600 dark:text-red-400 flex items-center justify-center shrink-0">
                <AlertTriangleIcon className="w-5 h-5" />
              </div>

              <div>
                <p className="text-slate-700 dark:text-slate-300 text-sm sm:text-base leading-relaxed mb-4">
                  You agree not to use VibeNationHQ to:
                </p>

                <ul className="space-y-3 text-sm sm:text-base text-slate-600 dark:text-slate-400 list-disc pl-5">
                  <li>Attempt unauthorized access to our systems or accounts.</li>
                  <li>Introduce malware, malicious scripts, or harmful code.</li>
                  <li>Interfere with the availability or operation of the platform.</li>
                  <li>Scrape or systematically reproduce substantial portions of our content without permission.</li>
                  <li>Impersonate VibeNationHQ, its staff, contributors, or partners.</li>
                  <li>Use the platform for unlawful or fraudulent purposes.</li>
                </ul>
              </div>
            </div>

          </div>
        </section>
      </FadeIn>

      {/* =====================================================
          6. LIMITATION OF LIABILITY
      ====================================================== */}
      <FadeIn direction="up" delay={0.1}>
        <section className="mb-14 sm:mb-16">

          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-7 sm:h-8 bg-amber-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              3. Limitation of Liability
            </h2>
          </div>

          <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg leading-relaxed max-w-4xl">
            VibeNationHQ strives to maintain a reliable and secure platform,
            but we do not guarantee that the service will always be
            uninterrupted, completely error-free, or continuously available.
            To the extent permitted by applicable law, VibeNationHQ is not
            responsible for losses arising from reliance on information
            published on the platform, temporary service interruptions,
            technical failures, or third-party services.
          </p>
        </section>
      </FadeIn>

      {/* =====================================================
          7. SERVICE EVOLUTION
      ====================================================== */}
      <FadeIn direction="up" delay={0.1}>
        <section className="mb-16 sm:mb-20">

          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-7 sm:h-8 bg-cyan-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              4. Service Evolution
            </h2>
          </div>

          <div className="flex items-start gap-4 p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">

            <div className="w-11 h-11 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
              <RefreshIcon className="w-5 h-5" />
            </div>

            <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base leading-relaxed">
              VibeNationHQ may modify, improve, suspend, or discontinue
              features of the platform as our technology, editorial
              operations, and business needs evolve. Where appropriate,
              significant changes to these Terms of Service will be reflected
              on this page.
            </p>

          </div>
        </section>
      </FadeIn>

      {/* =====================================================
          8. CONTACT / FINAL GOVERNANCE CARD
      ====================================================== */}
      <FadeIn direction="up" delay={0.1}>
        <section className="relative rounded-3xl bg-slate-950 text-white p-8 sm:p-12 text-center border border-slate-800 shadow-2xl overflow-hidden">

          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-teal-500 to-transparent opacity-60" />

          <div className="relative">

            <div className="mx-auto w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center mb-5 border border-teal-500/20">
              <ScaleIcon className="w-6 h-6" />
            </div>

            <h3 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight mb-3 text-white">
              Excellence Through Integrity.
            </h3>

            <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto mb-7 leading-relaxed">
              Questions about these Terms of Service or VibeNationHQ's
              platform policies? Our legal desk is available to assist.
            </p>

            <a
              href="mailto:legal@vibenationhq.com"
              className="inline-flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold px-6 sm:px-8 py-3.5 sm:py-4 rounded-xl uppercase tracking-wider text-[11px] sm:text-xs transition-all shadow-md hover:-translate-y-0.5"
            >
              <MailIcon className="w-4 h-4" />
              Contact Legal Desk
            </a>

            <p className="mt-6 text-xs text-slate-400">
              <strong className="text-slate-300">Effective Date:</strong>{' '}
              May 13, 2026
            </p>

          </div>
        </section>
      </FadeIn>

    </div>
  );
}