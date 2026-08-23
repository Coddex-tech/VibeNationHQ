import type { Metadata } from 'next';
import { NewsIcon, MusicIcon, WrenchIcon, MailIcon, WhatsappIcon } from '@/components/Icons';
import FadeIn from '@/components/FadeIn';

export const metadata: Metadata = {
  title: 'Contact Us | VibeNationHQ Corporate & Editorial Communications',
  description:
    "Contact VibeNationHQ for news tips, press releases, music submissions, advertising, partnerships, technical support, and other media inquiries.",
};

export default function ContactPage() {
  const currentYear = new Date().getFullYear();
  const whatsappMusicMessage = encodeURIComponent(
    'Hello VibeNationHQ, I want to promote my song'
  );

  const socialLinks = [
    { name: 'Facebook', href: '#' },
    { name: 'Instagram', href: 'https://instagram.com/vibenationhqofficial' },
    { name: 'X (Twitter)', href: 'https://x.com/VibeNationHQ' },
    { name: 'WhatsApp Channel', href: 'https://whatsapp.com/channel/0029Vb85LFb05MUcD4jtFN0A' },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 overflow-hidden">
      
      {/* 1. BRAND HERO SECTION */}
      <FadeIn direction="up" delay={0.1}>
        <div className="relative rounded-3xl bg-slate-950 text-white p-8 sm:p-14 lg:p-20 text-center mb-16 border border-slate-800 shadow-2xl overflow-hidden">
          {/* Ambient Background Glows */}
          <div className="absolute -top-32 -left-32 w-80 h-80 bg-teal-500/20 rounded-full blur-[100px] pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-80 h-80 bg-cyan-500/20 rounded-full blur-[100px] pointer-events-none" />

          {/* Status Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 text-teal-400 text-xs font-semibold uppercase tracking-widest mb-6">
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
            Direct Communications Desk
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] mb-6">
            Connect With <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-teal-400 via-cyan-400 to-yellow-400 bg-clip-text text-transparent">
              VibeNationHQ
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Your direct line to Africa’s high-fidelity news and culture engine.
          </p>
        </div>
      </FadeIn>

      {/* 2. INTRO SECTION */}
      <FadeIn direction="up" delay={0.2}>
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-1.5 h-7 bg-teal-500 rounded-full" />
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
              Professional Communication
            </h2>
          </div>
          <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
            At <strong className="text-slate-900 dark:text-white font-bold">VibeNationHQ</strong>, we prioritize open, high-integrity communication. Whether you are a whistleblower with an industry tip, an artist seeking a global platform, or a brand looking for premium campaign integration, our specialized desks are built to engage directly with you.
          </p>
        </section>
      </FadeIn>

      {/* 3. COMMUNICATION DESKS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
        
        {/* DESK 1: EDITORIAL */}
        <FadeIn direction="up" delay={0.1}>
          <div className="h-full p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:border-teal-500/50 hover:shadow-md transition-all duration-300 flex flex-col justify-between group">
            <div>
              <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <NewsIcon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-3">
                Editorial & News Desk
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-6">
                Have a breaking story, press release, or verified tip? Our Chief Editor reviews all submissions for clarity and impact using our Raw Fact + Analysis model.
              </p>
            </div>
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800/60 flex items-center gap-2 text-sm">
              <MailIcon className="w-4 h-4 text-teal-500" />
              <a
                href="mailto:newsroom@vibenationhq.com"
                className="font-semibold text-slate-900 dark:text-slate-200 hover:text-teal-500 dark:hover:text-teal-400 transition-colors"
              >
                newsroom@vibenationhq.com
              </a>
            </div>
          </div>
        </FadeIn>

        {/* DESK 2: MUSIC & A&R */}
        <FadeIn direction="up" delay={0.25}>
          <div className="h-full p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:border-cyan-500/50 hover:shadow-md transition-all duration-300 flex flex-col justify-between group">
            <div>
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <MusicIcon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-3">
                Music & A&R Department
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-6">
                Artists and labels: Submit high-fidelity audio tracks, artwork, and press materials for featured placement across our global charts and music discovery hub.
              </p>
            </div>
            <div>
              <a
                href={`https://wa.me/2347035101511?text=${whatsappMusicMessage}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-5 py-2.5 rounded-xl text-xs uppercase tracking-wider transition-all shadow-sm"
              >
                <WhatsappIcon className="w-4 h-4" />
                Submit via WhatsApp
              </a>
            </div>
          </div>
        </FadeIn>

        {/* DESK 3: TECHNICAL SUPPORT */}
        <FadeIn direction="up" delay={0.4}>
          <div className="h-full p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:border-yellow-500/50 hover:shadow-md transition-all duration-300 flex flex-col justify-between group">
            <div>
              <div className="w-12 h-12 rounded-xl bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <WrenchIcon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-3">
                Technical Support
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-6">
                Encountering an issue on our custom architecture? Our engineering team monitors bug reports to ensure an uninterrupted, high-performance platform experience.
              </p>
            </div>
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800/60 flex items-center gap-2 text-sm">
              <MailIcon className="w-4 h-4 text-yellow-500" />
              <a
                href="mailto:support@vibenationhq.com"
                className="font-semibold text-slate-900 dark:text-slate-200 hover:text-yellow-500 dark:hover:text-yellow-400 transition-colors"
              >
                support@vibenationhq.com
              </a>
            </div>
          </div>
        </FadeIn>

      </div>

      {/* 4. CORPORATE PARTNERSHIPS SECTION */}
      <section className="mb-20">
        <FadeIn direction="up" delay={0.1}>
          <div className="p-8 sm:p-12 rounded-3xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-1.5 h-7 bg-cyan-500 rounded-full" />
              <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                Corporate Partnerships
              </h2>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-base sm:text-lg mb-8 max-w-4xl">
              VibeNationHQ provides a dedicated ecosystem for high-impact brand storytelling. Moving beyond intrusive ad banners, we execute multi-channel campaigns that truly resonate with modern African consumers.
            </p>

            <div className="p-8 rounded-2xl bg-slate-900 text-white border border-slate-800 text-center sm:text-left sm:flex sm:items-center sm:justify-between gap-6 shadow-xl">
              <div>
                <h3 className="text-xl font-bold mb-2">Advertise With Us</h3>
                <p className="text-slate-400 text-sm max-w-xl">
                  Reach out for high-impact enterprise media campaigns, custom brand placements, and strategic event coverage.
                </p>
              </div>
              <div className="mt-6 sm:mt-0 shrink-0">
                <a
                  href="mailto:ads@vibenationhq.com"
                  className="inline-flex items-center justify-center bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold px-6 py-3 rounded-xl uppercase tracking-wider text-xs transition-all shadow-md transform hover:-translate-y-0.5"
                >
                  Request {currentYear} Rate Card
                </a>
              </div>
            </div>
          </div>
        </FadeIn>
      </section>

      {/* 5. SOCIAL MEDIA FOOTPRINT */}
      <FadeIn direction="up" delay={0.1}>
        <section className="text-center p-8 sm:p-12 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm">
          <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white mb-3">
            Follow the Movement
          </h2>
          <p className="text-slate-600 dark:text-slate-400 text-sm max-w-xl mx-auto mb-8">
            Stay updated with breaking news and real-time VibeNation Analysis across our official verified channels.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4">
            {socialLinks.map((item, idx) => (
              <a
                key={idx}
                href={item.href}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:text-teal-600 dark:hover:text-teal-400 hover:border-teal-500/50 text-xs font-semibold tracking-wide transition-all"
              >
                {item.name}
              </a>
            ))}
          </div>
        </section>
      </FadeIn>

    </div>
  );
}