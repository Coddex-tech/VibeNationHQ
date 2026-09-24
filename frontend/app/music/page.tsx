import type { Metadata } from 'next';
import {
    LockIcon,
    AnalyticsIcon,
    WrenchIcon,
    MailIcon,
    CheckCircleIcon,
} from '@/components/Icons';
import FadeIn from '@/components/FadeIn';

export const metadata: Metadata = {
    title: 'Privacy Policy | VibeNationHQ Data Protection Standards',
    description:
        'Learn how VibeNationHQ handles your data. Our privacy policy outlines our commitment to security, transparency, and protecting our global audience.',
};

type DataPrinciple = {
    title: string;
    description: string;
    icon: typeof LockIcon;
    color: 'teal' | 'cyan' | 'amber';
};

export default function PrivacyPage() {
    const dataPrinciples: DataPrinciple[] = [
        {
            title: 'Zero-Sale Guarantee',
            description:
                'Your personal information is never for sale. VibeNationHQ does not trade, rent, or sell user data to third-party data brokers.',
            icon: LockIcon,
            color: 'teal',
        },
        {
            title: 'Essential Collection',
            description:
                'We collect only information that helps us improve the reliability, performance, and usability of our platform, such as device type, browser information, and page engagement metrics.',
            icon: AnalyticsIcon,
            color: 'cyan',
        },
        {
            title: 'Security & Integrity',
            description:
                'We take reasonable technical and organizational measures to protect information handled through our platform against unauthorized access, misuse, alteration, or disclosure.',
            icon: WrenchIcon,
            color: 'amber',
        },
    ];

    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 md:py-20 overflow-hidden">

            {/* =====================================================
          1. HERO
      ===================================================== */}
            <FadeIn direction="up" delay={0.1}>
                <section className="relative rounded-3xl bg-slate-950 text-white p-7 sm:p-12 lg:p-20 text-center mb-14 sm:mb-16 border border-slate-800 shadow-2xl overflow-hidden">

                    <div className="absolute -top-32 -left-32 w-72 sm:w-80 h-72 sm:h-80 bg-teal-500/20 rounded-full blur-[100px] pointer-events-none" />

                    <div className="absolute -bottom-32 -right-32 w-72 sm:w-80 h-72 sm:h-80 bg-cyan-500/20 rounded-full blur-[100px] pointer-events-none" />

                    <div className="relative z-10">

                        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 text-teal-300 text-[11px] sm:text-xs font-bold uppercase tracking-[0.18em] mb-6">
                            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse shadow-[0_0_8px_#2dd4bf]" />
                            <LockIcon className="w-4 h-4" />
                            Data Protection & Privacy
                        </div>

                        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] mb-6 text-white">
                            Privacy{' '}
                            <span className="bg-gradient-to-r from-teal-300 via-cyan-400 to-yellow-400 bg-clip-text text-transparent">
                                Policy
                            </span>
                        </h1>

                        <p className="text-sm sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
                            Safeguarding your digital footprint while delivering a fast,
                            reliable, and high-quality VibeNationHQ experience.
                        </p>

                    </div>
                </section>
            </FadeIn>

            {/* =====================================================
          2. DATA PHILOSOPHY
      ===================================================== */}
            <FadeIn direction="up" delay={0.2}>
                <section className="mb-14 sm:mb-16">

                    <div className="flex items-center gap-3 mb-4">
                        <span className="w-1.5 h-7 bg-teal-500 rounded-full shrink-0 shadow-[0_0_10px_rgba(20,184,166,0.5)]" />

                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                            Our Data Philosophy
                        </h2>
                    </div>

                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
                        At{' '}
                        <strong className="text-teal-700 dark:text-teal-400 font-black">
                            VibeNationHQ
                        </strong>
                        , we believe your personal information deserves transparency,
                        respect, and responsible handling. Our platform is engineered to
                        prioritize privacy while delivering relevant news, music, and
                        entertainment content.
                    </p>

                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl mt-4">
                        This policy explains what information we may collect, how it may
                        be used, and the choices available to you when interacting with
                        our platform.
                    </p>

                </section>
            </FadeIn>

            {/* =====================================================
          3. CORE DATA PRINCIPLES
      ===================================================== */}
            <section className="mb-16 sm:mb-20">

                <FadeIn direction="up" delay={0.1}>
                    <div className="flex items-center gap-3 mb-7">

                        <span className="w-1.5 h-7 bg-cyan-500 rounded-full shrink-0 shadow-[0_0_10px_rgba(6,182,212,0.5)]" />

                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                            Our Core Data Principles
                        </h2>

                    </div>
                </FadeIn>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6">

                    {dataPrinciples.map((item, index) => {

                        const Icon = item.icon;

                        const iconStyles = {
                            teal: {
                                wrapper:
                                    'bg-teal-500/10 text-teal-600 dark:bg-teal-500/20 dark:text-teal-400 border-teal-500/20',
                                hover: 'hover:border-teal-500/50',
                            },

                            cyan: {
                                wrapper:
                                    'bg-cyan-500/10 text-cyan-600 dark:bg-cyan-500/20 dark:text-cyan-400 border-cyan-500/20',
                                hover: 'hover:border-cyan-500/50',
                            },

                            amber: {
                                wrapper:
                                    'bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400 border-amber-500/20',
                                hover: 'hover:border-amber-500/50',
                            },
                        }[item.color];

                        return (
                            <FadeIn
                                key={item.title}
                                direction="up"
                                delay={0.15 * (index + 1)}
                            >
                                <div
                                    className={`h-full p-7 sm:p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:shadow-md ${iconStyles.hover} transition-all duration-300`}
                                >

                                    <div
                                        className={`w-12 h-12 rounded-xl border flex items-center justify-center mb-6 ${iconStyles.wrapper}`}
                                    >
                                        <Icon className="w-6 h-6" />
                                    </div>

                                    <h3 className="text-lg font-black text-slate-900 dark:text-white mb-3">
                                        {item.title}
                                    </h3>

                                    <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                                        {item.description}
                                    </p>

                                </div>
                            </FadeIn>
                        );
                    })}

                </div>
            </section>

            {/* =====================================================
          4. COOKIES
      ===================================================== */}
            <FadeIn direction="up" delay={0.1}>
                <section className="mb-14 sm:mb-16">

                    <div className="flex items-center gap-3 mb-4">

                        <span className="w-1.5 h-7 bg-teal-500 rounded-full shrink-0" />

                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                            Cookies & Tracking
                        </h2>

                    </div>

                    <p className="text-slate-700 dark:text-slate-300 text-base sm:text-lg leading-relaxed max-w-4xl mb-6">
                        VibeNationHQ may use cookies and similar technologies to improve
                        website functionality, understand how visitors interact with the
                        platform, remember preferences, and support advertising services.
                    </p>

                    <div className="space-y-4">

                        {[
                            {
                                title: 'Session & Functional Cookies',
                                description:
                                    'These technologies may help maintain navigation, preferences, and other functionality across different areas of the platform.',
                            },
                            {
                                title: 'Analytics',
                                description:
                                    'Analytics technologies may provide aggregated information about page visits, traffic patterns, and content engagement so we can improve the platform.',
                            },
                            {
                                title: 'Advertising Cookies',
                                description:
                                    'Advertising partners, including services such as Google, may use cookies or similar technologies to display and measure advertisements according to their own policies.',
                            },
                        ].map((item) => (
                            <div
                                key={item.title}
                                className="flex items-start gap-4 p-5 sm:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50"
                            >
                                <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center shrink-0 mt-0.5">
                                    <CheckCircleIcon className="w-5 h-5" />
                                </div>

                                <div>
                                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white mb-1">
                                        {item.title}
                                    </h3>

                                    <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                                        {item.description}
                                    </p>
                                </div>
                            </div>
                        ))}

                    </div>

                </section>
            </FadeIn>

            {/* =====================================================
          5. THIRD-PARTY SERVICES
      ===================================================== */}
            <FadeIn direction="up" delay={0.1}>
                <section className="mb-14 sm:mb-16">

                    <div className="flex items-center gap-3 mb-4">

                        <span className="w-1.5 h-7 bg-cyan-500 rounded-full shrink-0" />

                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                            Third-Party Services
                        </h2>

                    </div>

                    <p className="text-slate-700 dark:text-slate-300 text-base sm:text-lg leading-relaxed max-w-4xl">
                        VibeNationHQ may integrate third-party services such as YouTube
                        embeds, Spotify players, social-media tools, analytics services,
                        advertising platforms, or external links. These services may
                        collect information according to their own privacy policies.
                    </p>

                    <p className="text-slate-700 dark:text-slate-300 text-base sm:text-lg leading-relaxed max-w-4xl mt-4">
                        We encourage you to review the privacy policies of third-party
                        services before interacting with their embedded content or
                        external platforms.
                    </p>

                </section>
            </FadeIn>

            {/* =====================================================
          6. YOUR RIGHTS
      ===================================================== */}
            <FadeIn direction="up" delay={0.1}>
                <section className="mb-16 p-7 sm:p-10 rounded-3xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 shadow-sm">

                    <div className="flex items-center gap-3 mb-4">

                        <span className="w-1.5 h-7 bg-yellow-500 rounded-full shrink-0" />

                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                            Your Rights & Control
                        </h2>

                    </div>

                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl mb-5">
                        You have control over many aspects of your interaction with
                        VibeNationHQ. Depending on the information involved and applicable
                        law, you may have rights relating to access, correction,
                        deletion, objection, or restriction of certain personal data.
                    </p>

                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-base sm:text-lg max-w-4xl">
                        You can also manage or disable cookies through your browser
                        settings. Please note that disabling certain cookies may affect
                        some functionality or personalization features of the platform.
                    </p>

                </section>
            </FadeIn>

            {/* =====================================================
          7. PRIVACY CONTACT CTA
      ===================================================== */}
            <FadeIn direction="up" delay={0.1}>
                <section className="relative rounded-3xl bg-slate-950 text-white p-8 sm:p-12 text-center border border-slate-800 shadow-2xl overflow-hidden">

                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-teal-500 to-transparent opacity-60" />

                    <div className="relative z-10">

                        <div className="w-14 h-14 mx-auto rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center mb-6">
                            <MailIcon className="w-7 h-7" />
                        </div>

                        <h3 className="text-2xl sm:text-3xl font-black tracking-tight text-white mb-3">
                            Privacy Is a Priority.
                        </h3>

                        <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto mb-7 leading-relaxed">
                            Have a question about your information, our privacy practices,
                            or how we handle data? Our Privacy Desk is available to assist.
                        </p>

                        <a
                            href="mailto:privacy@vibenationhq.com"
                            className="inline-flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-black px-6 sm:px-8 py-3.5 sm:py-4 rounded-xl uppercase tracking-wider text-xs sm:text-sm transition-all shadow-md hover:-translate-y-0.5 active:translate-y-0"
                        >
                            <MailIcon className="w-4 h-4" />
                            Contact Privacy Officer
                        </a>

                        <p className="mt-6 text-xs text-slate-500">
                            <strong className="text-slate-400">Last Updated:</strong>{' '}
                            May 2026
                        </p>

                    </div>
                </section>
            </FadeIn>

        </div>
    );
}