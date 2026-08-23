import type { Metadata } from 'next';
import {
  CopyrightIcon,
  ShieldIcon,
  MailIcon,
  DownloadIcon,
  ScaleIcon,
} from '@/components/Icons';
import FadeIn from '@/components/FadeIn';

export const metadata: Metadata = {
  title: 'DMCA Policy & Legal Disclaimer | VibeNationHQ',
  description:
    'VibeNationHQ copyright and DMCA policy, takedown procedures, content disclaimers, and intellectual property standards.',
};

export default function DmcaPage() {
  const lastUpdated = 'May 13, 2026';

  const dmcaRequirements = [
    {
      title: 'Identify the Copyrighted Work',
      description:
        'Provide a clear description of the copyrighted work that you believe has been infringed. Where applicable, include the title, creator, or other information that helps us identify the work.',
    },
    {
      title: 'Identify the Material',
      description:
        'Provide the specific URL or other precise location on VibeNationHQ where the allegedly infringing material appears. Direct links help us investigate the report efficiently.',
    },
    {
      title: 'Provide Your Contact Information',
      description:
        'Include your full name, organization or company if applicable, mailing address, telephone number, and email address so that we can contact you regarding the notice.',
    },
    {
      title: 'Good-Faith Statement',
      description:
        'Include a statement that you have a good-faith belief that the disputed use of the material is not authorized by the copyright owner, its agent, or applicable law.',
    },
    {
      title: 'Accuracy & Authorization',
      description:
        'Include a statement that the information in your notification is accurate and, where applicable, that you are authorized to act on behalf of the copyright owner.',
    },
    {
      title: 'Electronic or Physical Signature',
      description:
        'Include a valid electronic or physical signature of the copyright owner or an authorized representative submitting the notification.',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 md:py-20 overflow-hidden">

      {/* =========================================================
          1. HERO
      ========================================================= */}
      <FadeIn direction="up" delay={0.1}>
        <section className="relative rounded-3xl bg-slate-950 text-white p-8 sm:p-14 lg:p-20 text-center mb-14 sm:mb-16 border border-slate-800 shadow-2xl overflow-hidden">

          <div className="absolute -top-32 -left-32 w-80 h-80 bg-teal-500/20 rounded-full blur-[100px] pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-80 h-80 bg-cyan-500/20 rounded-full blur-[100px] pointer-events-none" />

          <div className="relative z-10">

            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-teal-500/40 bg-teal-500/10 text-teal-300 text-[11px] sm:text-xs font-bold uppercase tracking-[0.16em] mb-6">
              <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
              Legal & Compliance
            </div>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] mb-6 text-white">
              Copyright <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-teal-300 via-cyan-400 to-yellow-400 bg-clip-text text-transparent">
                Notice & DMCA
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Our copyright standards, DMCA takedown procedure, and
              important disclaimers governing content published on
              VibeNationHQ.
            </p>

          </div>
        </section>
      </FadeIn>

      {/* =========================================================
          2. COPYRIGHT COMMITMENT
      ========================================================= */}
      <FadeIn direction="up" delay={0.2}>
        <section className="mb-16">

          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-8 bg-teal-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-950 dark:text-white">
              Our Commitment to Intellectual Property
            </h2>
          </div>

          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
            VibeNationHQ respects the intellectual property rights of
            creators, artists, publishers, photographers, and other
            copyright holders. We aim to publish original reporting and
            properly authorized or promotional material while responding
            responsibly to legitimate copyright concerns.
          </p>

          <p className="mt-4 text-slate-700 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
            This page explains how copyright holders or their authorized
            representatives can notify us of material they believe infringes
            their rights. VibeNationHQ may also consider applicable copyright
            laws and other relevant legal requirements when reviewing a
            complaint.
          </p>

        </section>
      </FadeIn>

      {/* =========================================================
          3. DMCA TAKEDOWN PROCEDURE
      ========================================================= */}
      <section className="mb-20">

        <FadeIn direction="up" delay={0.1}>
          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-8 bg-cyan-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-950 dark:text-white">
              DMCA Takedown Procedure
            </h2>
          </div>

          <p className="text-slate-700 dark:text-slate-300 text-base sm:text-lg mb-8 max-w-4xl leading-relaxed">
            If you believe that material available on VibeNationHQ infringes
            your copyright, you may send us a written copyright notification.
            Providing complete and accurate information helps our team review
            the complaint efficiently.
          </p>
        </FadeIn>

        {/* REQUIREMENTS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">

          {dmcaRequirements.map((item, index) => (
            <FadeIn
              key={item.title}
              direction="up"
              delay={0.1 + index * 0.08}
            >
              <div className="h-full p-6 sm:p-7 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:shadow-md hover:border-teal-500/50 transition-all duration-200">

                <div className="flex items-center gap-2 text-teal-600 dark:text-teal-400 font-black text-[11px] uppercase tracking-[0.14em] mb-3">
                  <span className="flex items-center justify-center w-6 h-6 rounded-md bg-teal-500/10 dark:bg-teal-500/20">
                    {String(index + 1).padStart(2, '0')}
                  </span>

                  Requirement
                </div>

                <h3 className="text-lg font-black text-slate-900 dark:text-white mb-2">
                  {item.title}
                </h3>

                <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">
                  {item.description}
                </p>

              </div>
            </FadeIn>
          ))}

        </div>

        {/* CONTACT CARD */}
        <FadeIn direction="up" delay={0.4}>
          <div className="p-6 sm:p-8 rounded-2xl border-l-4 border-l-teal-500 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-md">

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">

              <div className="flex items-start gap-4">

                <div className="w-12 h-12 rounded-xl bg-teal-500/10 dark:bg-teal-500/20 text-teal-600 dark:text-teal-400 flex items-center justify-center shrink-0 border border-teal-500/20">
                  <CopyrightIcon className="w-6 h-6" />
                </div>

                <div>
                  <h3 className="text-xl font-black text-slate-900 dark:text-white mb-1">
                    Submit a Copyright Notice
                  </h3>

                  <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed max-w-xl">
                    Send complete copyright notifications to our legal and
                    compliance desk. We will review submissions and take
                    appropriate action where warranted.
                  </p>
                </div>

              </div>

              <a
                href="mailto:support@vibenationhq.com"
                className="inline-flex items-center justify-center gap-2 shrink-0 bg-slate-900 hover:bg-teal-600 text-white dark:bg-white dark:hover:bg-teal-400 dark:text-slate-950 font-black px-6 py-3.5 rounded-xl text-xs uppercase tracking-widest transition-all shadow-md active:scale-95"
              >
                <MailIcon className="w-4 h-4" />
                Contact Legal Desk
              </a>

            </div>

          </div>
        </FadeIn>

      </section>

      {/* =========================================================
          4. CONTENT DISCLAIMER
      ========================================================= */}
      <section className="mb-20">

        <FadeIn direction="up" delay={0.1}>
          <div className="flex items-center gap-3 mb-4">

            <span className="w-1.5 h-8 bg-amber-500 rounded-full shrink-0" />

            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-950 dark:text-white">
              Content & Platform Disclaimer
            </h2>

          </div>

          <p className="text-slate-700 dark:text-slate-300 text-base sm:text-lg mb-8 max-w-4xl leading-relaxed">
            VibeNationHQ provides news, entertainment, music discovery, and
            cultural information for general informational and entertainment
            purposes. Although we make reasonable efforts to maintain
            accurate and current information, circumstances can change and
            published material may require correction or updating.
          </p>
        </FadeIn>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* NEWS ACCURACY */}
          <FadeIn direction="up" delay={0.15}>
            <div className="h-full p-7 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:border-teal-500/50 transition-all duration-200">

              <div className="w-12 h-12 rounded-xl bg-teal-500/10 dark:bg-teal-500/20 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-6 border border-teal-500/20">
                <ShieldIcon className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                News & Editorial Content
              </h3>

              <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">
                We work to distinguish reporting, analysis, commentary, and
                promotional material. Breaking stories may develop after
                publication, so readers should consider the publication date
                and subsequent updates when relying on reported information.
              </p>

            </div>
          </FadeIn>

          {/* DOWNLOADS */}
          <FadeIn direction="up" delay={0.3}>
            <div className="h-full p-7 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:border-cyan-500/50 transition-all duration-200">

              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-6 border border-cyan-500/20">
                <DownloadIcon className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                Music & Promotional Downloads
              </h3>

              <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">
                Where music or other downloadable media is provided for
                promotional purposes, VibeNationHQ does not automatically
                claim ownership of third-party material. Copyright remains
                with the applicable rights holder unless otherwise stated.
              </p>

            </div>
          </FadeIn>

          {/* THIRD PARTY */}
          <FadeIn direction="up" delay={0.45}>
            <div className="h-full p-7 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:border-amber-500/50 transition-all duration-200">

              <div className="w-12 h-12 rounded-xl bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-6 border border-amber-500/20">
                <ScaleIcon className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                Third-Party Services
              </h3>

              <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">
                VibeNationHQ may link to or embed content from third-party
                platforms. Those services operate independently and may have
                their own terms, privacy policies, cookies, and data practices.
              </p>

            </div>
          </FadeIn>

        </div>

      </section>

      {/* =========================================================
          5. COPYRIGHT OWNERSHIP & CORRECTIONS
      ========================================================= */}
      <FadeIn direction="up" delay={0.1}>
        <section className="mb-20 p-7 sm:p-10 rounded-3xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 shadow-sm">

          <div className="flex items-start gap-4">

            <div className="w-11 h-11 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-950 flex items-center justify-center shrink-0">
              <CopyrightIcon className="w-5 h-5" />
            </div>

            <div>

              <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white mb-3">
                Copyright Concerns & Corrections
              </h2>

              <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base leading-relaxed mb-4">
                If you believe that material published by VibeNationHQ
                infringes your copyright, contains an attribution error, or
                otherwise requires legal clarification, please contact our
                team with sufficient information for us to investigate.
              </p>

              <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base leading-relaxed">
                We may remove, restrict, correct, or otherwise modify content
                where appropriate following our review and applicable legal
                requirements.
              </p>

            </div>

          </div>

        </section>
      </FadeIn>

      {/* =========================================================
          6. LIMITATION OF LIABILITY
      ========================================================= */}
      <FadeIn direction="up" delay={0.1}>
        <section className="mb-20 p-7 sm:p-10 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">

          <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white mb-3">
            Limitation of Liability
          </h2>

          <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base leading-relaxed">
            To the extent permitted by applicable law, VibeNationHQ and its
            contributors are not responsible for losses or damages arising
            from reliance on information published on the platform, temporary
            service interruptions, third-party websites or services, or
            downloadable material supplied by third parties. Nothing in this
            policy is intended to exclude rights or protections that cannot
            lawfully be excluded.
          </p>

        </section>
      </FadeIn>

      {/* =========================================================
          7. FINAL CTA
      ========================================================= */}
      <FadeIn direction="up" delay={0.1}>
        <section className="rounded-3xl bg-slate-950 text-white p-8 sm:p-12 text-center border border-slate-800 shadow-2xl relative overflow-hidden">

          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-teal-500 to-transparent opacity-60" />

          <div className="relative z-10">

            <h3 className="text-2xl sm:text-3xl font-black tracking-tight mb-3 text-white">
              Copyright. Integrity. Accountability.
            </h3>

            <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto mb-7 leading-relaxed">
              We are committed to respecting creators and rights holders while
              maintaining a reliable, transparent media platform for our
              audience.
            </p>

            <a
              href="mailto:support@vibenationhq.com"
              className="inline-flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-black px-7 py-3.5 rounded-xl text-xs uppercase tracking-widest transition-all shadow-md active:scale-95"
            >
              <MailIcon className="w-4 h-4" />
              Contact Copyright Desk
            </a>

            <div className="mt-8 pt-6 border-t border-slate-800">
              <p className="text-xs text-slate-500">
                Last Updated: <span className="text-slate-400 font-medium">{lastUpdated}</span>
              </p>
            </div>

          </div>

        </section>
      </FadeIn>

    </div>
  );
}