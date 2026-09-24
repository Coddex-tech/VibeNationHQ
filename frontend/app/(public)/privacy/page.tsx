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
        'Learn how VibeNationHQ handles personal information, cookies, analytics, advertising technologies, and third-party services while respecting user privacy.',
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
            title: 'No Sale of Personal Data',
            description:
                'VibeNationHQ does not sell, rent, or trade personal information to third-party data brokers. Information is handled for legitimate platform, operational, security, and service-related purposes.',
            icon: LockIcon,
            color: 'teal',
        },
        {
            title: 'Purposeful Collection',
            description:
                'We aim to collect information that is relevant to operating, securing, improving, and understanding the platform, such as account information, device details, browser information, and aggregated engagement data.',
            icon: AnalyticsIcon,
            color: 'cyan',
        },
        {
            title: 'Security & Integrity',
            description:
                'We use reasonable technical and organizational measures designed to protect information handled through VibeNationHQ against unauthorized access, misuse, alteration, loss, or disclosure.',
            icon: WrenchIcon,
            color: 'amber',
        },
    ];

    const cookieTypes = [
        {
            title: 'Session & Functional Cookies',
            description:
                'These technologies may help maintain sessions, remember preferences, support navigation, and provide essential functionality across different areas of the platform.',
        },
        {
            title: 'Analytics',
            description:
                'Analytics technologies may provide aggregated information about page visits, traffic sources, content engagement, and platform performance so we can understand how VibeNationHQ is used and improve it.',
        },
        {
            title: 'Advertising Technologies',
            description:
                'Advertising partners, including services such as Google and other advertising providers, may use cookies or similar technologies to deliver, personalize, measure, or improve advertisements according to their own policies.',
        },
    ];

    return (
        <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 md:py-20 overflow-hidden">

                {/* =====================================================
                    1. HERO
                ===================================================== */}
                <FadeIn direction="up" delay={0.1}>
                    <section className="relative rounded-3xl bg-dark-bg text-dark-text p-7 sm:p-12 lg:p-20 text-center mb-14 sm:mb-16 border border-dark-border-teal overflow-hidden">

                        <div className="relative z-10">

                            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-dark-border-teal bg-dark-surface-teal text-brand-teal-light text-[11px] sm:text-xs font-bold uppercase tracking-[0.18em] mb-6">
                                <span className="w-2 h-2 rounded-full bg-brand-teal animate-pulse" />
                                <LockIcon className="w-4 h-4" />
                                Data Protection & Privacy
                            </div>

                            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] mb-6 text-dark-text">
                                Privacy{' '}
                                <span className="text-brand-teal-light">
                                    Policy
                                </span>
                            </h1>

                            <p className="text-sm sm:text-lg text-dark-text-muted max-w-2xl mx-auto leading-relaxed">
                                A clear overview of how VibeNationHQ handles information,
                                cookies, analytics, advertising technologies, and
                                third-party services.
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
                            <span className="w-1.5 h-7 bg-brand-teal rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                                Our Data Philosophy
                            </h2>
                        </div>

                        <p className="text-light-text-muted dark:text-dark-text-muted leading-relaxed text-base sm:text-lg max-w-4xl">
                            At{' '}
                            <strong className="text-brand-teal dark:text-brand-teal-light font-black">
                                VibeNationHQ
                            </strong>
                            , we believe personal information should be handled with
                            transparency, respect, and appropriate care. Our platform
                            is designed to deliver news, music discovery, entertainment,
                            culture, and community features while taking privacy and
                            security into consideration.
                        </p>

                        <p className="text-light-text-muted dark:text-dark-text-muted leading-relaxed text-base sm:text-lg max-w-4xl mt-4">
                            This policy explains the types of information VibeNationHQ
                            may collect, how that information may be used, the role of
                            third-party services, and some of the choices available to
                            you when using the platform.
                        </p>

                    </section>
                </FadeIn>

                {/* =====================================================
                    3. CORE DATA PRINCIPLES
                ===================================================== */}
                <section className="mb-16 sm:mb-20">

                    <FadeIn direction="up" delay={0.1}>
                        <div className="flex items-center gap-3 mb-7">

                            <span className="w-1.5 h-7 bg-brand-cyan rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
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
                                        'bg-brand-teal/10 text-brand-teal border-brand-teal/20 dark:bg-brand-teal/15 dark:text-brand-teal-light dark:border-dark-border-teal',
                                    hover: 'hover:border-brand-teal/40 dark:hover:border-brand-teal/50',
                                },

                                cyan: {
                                    wrapper:
                                        'bg-brand-cyan/10 text-brand-cyan border-brand-cyan/20 dark:bg-brand-cyan/15 dark:text-brand-cyan dark:border-brand-cyan/30',
                                    hover: 'hover:border-brand-cyan/40 dark:hover:border-brand-cyan/50',
                                },

                                amber: {
                                    wrapper:
                                        'bg-brand-gold/10 text-brand-gold border-brand-gold/20 dark:bg-brand-gold/10 dark:text-brand-gold dark:border-brand-gold/25',
                                    hover: 'hover:border-brand-gold/40 dark:hover:border-brand-gold/40',
                                },
                            }[item.color];

                            return (
                                <FadeIn
                                    key={item.title}
                                    direction="up"
                                    delay={0.15 * (index + 1)}
                                >
                                    <div
                                        className={`h-full p-7 sm:p-8 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface transition-colors duration-300 ${iconStyles.hover}`}
                                    >

                                        <div
                                            className={`w-12 h-12 rounded-xl border flex items-center justify-center mb-6 ${iconStyles.wrapper}`}
                                        >
                                            <Icon className="w-6 h-6" />
                                        </div>

                                        <h3 className="text-lg font-black text-light-text dark:text-dark-text mb-3">
                                            {item.title}
                                        </h3>

                                        <p className="text-light-text-muted dark:text-dark-text-muted text-sm leading-relaxed">
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

                            <span className="w-1.5 h-7 bg-brand-teal rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                                Cookies & Tracking
                            </h2>

                        </div>

                        <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl mb-6">
                            VibeNationHQ may use cookies and similar technologies to
                            support website functionality, remember preferences,
                            understand how visitors interact with the platform, improve
                            performance, and support advertising services.
                        </p>

                        <div className="space-y-4">

                            {cookieTypes.map((item) => (
                                <div
                                    key={item.title}
                                    className="flex items-start gap-4 p-5 sm:p-6 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface-soft dark:bg-dark-surface-soft"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light flex items-center justify-center shrink-0 mt-0.5">
                                        <CheckCircleIcon className="w-5 h-5" />
                                    </div>

                                    <div>
                                        <h3 className="text-base sm:text-lg font-bold text-light-text dark:text-dark-text mb-1">
                                            {item.title}
                                        </h3>

                                        <p className="text-sm leading-relaxed text-light-text-muted dark:text-dark-text-muted">
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

                            <span className="w-1.5 h-7 bg-brand-cyan rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                                Third-Party Services
                            </h2>

                        </div>

                        <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl">
                            VibeNationHQ may integrate or link to third-party services
                            such as YouTube embeds, Spotify players, social-media
                            platforms, analytics services, advertising platforms,
                            authentication providers, and other external services.
                        </p>

                        <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl mt-4">
                            These third parties may collect or process information
                            according to their own privacy policies and terms. When you
                            interact with embedded content, advertisements, or external
                            platforms, their privacy practices may apply in addition to
                            this policy.
                        </p>

                    </section>
                </FadeIn>

                {/* =====================================================
                    6. INFORMATION YOU PROVIDE
                ===================================================== */}
                <FadeIn direction="up" delay={0.1}>
                    <section className="mb-14 sm:mb-16">

                        <div className="flex items-center gap-3 mb-4">

                            <span className="w-1.5 h-7 bg-brand-teal rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                                Information You Provide
                            </h2>

                        </div>

                        <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl">
                            Depending on the features you use, VibeNationHQ may receive
                            information that you voluntarily provide, such as account
                            details, comments, replies, contact messages, support
                            requests, or other information submitted through the
                            platform.
                        </p>

                        <p className="text-light-text-muted dark:text-dark-text-muted text-base sm:text-lg leading-relaxed max-w-4xl mt-4">
                            We may also collect technical information associated with
                            your interaction with the platform, such as browser type,
                            device information, approximate location derived from
                            technical data, IP address, and information about how the
                            website is accessed and used.
                        </p>

                    </section>
                </FadeIn>

                {/* =====================================================
                    7. HOW INFORMATION MAY BE USED
                ===================================================== */}
                <FadeIn direction="up" delay={0.1}>
                    <section className="mb-14 sm:mb-16">

                        <div className="flex items-center gap-3 mb-4">

                            <span className="w-1.5 h-7 bg-brand-cyan rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                                How Information May Be Used
                            </h2>

                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

                            {[
                                'Provide and maintain VibeNationHQ services and features.',
                                'Create, manage, and secure user accounts where applicable.',
                                'Process comments, replies, submissions, and support requests.',
                                'Improve website performance, usability, and content experience.',
                                'Understand aggregated audience and content engagement patterns.',
                                'Detect, prevent, and investigate abuse, fraud, security incidents, or unauthorized activity.',
                                'Deliver and measure advertising or sponsored campaigns where applicable.',
                                'Communicate with users about service-related matters.',
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

                    </section>
                </FadeIn>

                {/* =====================================================
                    8. YOUR RIGHTS
                ===================================================== */}
                <FadeIn direction="up" delay={0.1}>
                    <section className="mb-16 p-7 sm:p-10 rounded-3xl border border-light-border dark:border-dark-border bg-light-surface-soft dark:bg-dark-surface-soft">

                        <div className="flex items-center gap-3 mb-4">

                            <span className="w-1.5 h-7 bg-brand-gold rounded-full shrink-0" />

                            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text">
                                Your Rights & Control
                            </h2>

                        </div>

                        <p className="text-light-text-muted dark:text-dark-text-muted leading-relaxed text-base sm:text-lg max-w-4xl mb-5">
                            Depending on the information involved and applicable law,
                            you may have rights relating to access, correction,
                            deletion, objection, restriction, or other forms of control
                            over certain personal information.
                        </p>

                        <p className="text-light-text-muted dark:text-dark-text-muted leading-relaxed text-base sm:text-lg max-w-4xl">
                            You can also manage or disable cookies through your browser
                            settings. Disabling certain cookies may affect some
                            functionality, personalization, analytics, or advertising
                            features of the platform.
                        </p>

                    </section>
                </FadeIn>

                {/* =====================================================
                    9. PRIVACY CONTACT CTA
                ===================================================== */}
                <FadeIn direction="up" delay={0.1}>
                    <section className="rounded-3xl border border-light-border bg-light-surface p-8 text-center text-light-text sm:p-12 dark:border-dark-border-teal dark:bg-dark-surface-teal dark:text-dark-text">

                        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl border border-brand-teal/20 bg-brand-teal/10 text-brand-teal">
                            <MailIcon className="h-7 w-7 dark:text-brand-teal-light" />
                        </div>

                        <h3 className="mb-3 text-2xl font-black tracking-tight text-light-text sm:text-3xl dark:text-dark-text">
                            Privacy Is a Priority.
                        </h3>

                        <p className="mx-auto mb-7 max-w-xl text-sm leading-relaxed text-light-text-muted sm:text-base dark:text-dark-text-muted">
                            Have a question about your information, our privacy practices,
                            or how VibeNationHQ handles data? Contact our Privacy Desk
                            for assistance.
                        </p>

                        <a
                            href="mailto:privacy@vibenationhq.com"
                            className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-teal px-6 py-3.5 text-xs font-black uppercase tracking-wider text-white transition-colors hover:bg-brand-teal-light sm:px-8 sm:py-4 sm:text-sm focus:outline-none focus:ring-2 focus:ring-brand-teal focus:ring-offset-2 focus:ring-offset-light-surface dark:focus:ring-offset-dark-surface-teal"
                        >
                            <MailIcon className="h-4 w-4" />
                            Contact Privacy Desk
                        </a>

                        <p className="mt-6 text-xs text-light-text-soft dark:text-dark-text-soft">
                            <strong className="text-light-text-muted dark:text-dark-text-muted">
                                Last Updated:
                            </strong>{' '}
                            May 2026
                        </p>

                    </section>
                </FadeIn>

            </div>
        </main>
    );
}