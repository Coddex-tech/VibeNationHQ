'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
    CheckCircleIcon,
    LockIcon,
    MailIcon,
    ShieldCheckIcon,
} from '@/components/Icons';
import { apiRequest, ApiError } from '@/lib/api';

type ForgotPasswordResponse = {
    message: string;
};

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (
        event: FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        if (!email.trim() || isSubmitting) {
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            await apiRequest<ForgotPasswordResponse>(
                '/api/accounts/password/forgot/',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        email: email.trim(),
                    }),
                },
            );

            setIsSubmitted(true);
        } catch (error) {
            if (error instanceof ApiError) {
                setError(
                    error.data?.detail ??
                        'Something went wrong. Please try again.',
                );
            } else {
                setError(
                    'Something went wrong. Please try again.',
                );
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-light-bg text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text">
            <div className="mx-auto flex min-h-screen w-full max-w-7xl items-start px-4 py-5 sm:items-center sm:px-6 sm:py-8 lg:px-8 lg:py-10">
                <div
                    className="
                    relative grid w-full overflow-hidden rounded-2xl
                    border border-light-border
                    bg-[#f7f8f8]
                    shadow-lg shadow-black/[0.04]
                    dark:border-dark-border
                    dark:bg-dark-surface
                    dark:shadow-black/20
                    lg:min-h-[620px]
                    lg:grid-cols-[0.9fr_1.1fr]
                "
                >
                    {/* Theme toggle */}
                    <div className="absolute right-4 top-4 z-50 sm:right-5 sm:top-5">
                        <ThemeToggle />
                    </div>

                    {/* Brand / editorial side */}
                    <section
                        className="
                        relative hidden overflow-hidden
                        border-r border-light-border
                        bg-light-surface-soft
                        p-8
                        dark:border-dark-border
                        dark:bg-dark-surface-soft
                        lg:flex lg:flex-col lg:justify-between
                        lg:p-10
                        xl:p-12
                        "
                    >
                        <div className="relative z-10">
                            <Link
                                href="/"
                                className="inline-flex items-center"
                                aria-label="VibeNationHQ home"
                            >
                                <span className="text-2xl font-black tracking-tight text-light-text dark:text-dark-text">
                                    VibeNation
                                    <span className="text-brand-teal">
                                        HQ
                                    </span>
                                </span>
                            </Link>

                            <div className="mt-20 max-w-md xl:mt-24">
                                <FadeIn>
                                    <div
                                        className="
                                        mb-5 inline-flex items-center gap-2
                                        rounded-full
                                        border border-brand-teal/20
                                        bg-brand-teal/10
                                        px-3 py-1.5
                                        text-xs font-semibold
                                        text-brand-teal-dark
                                        dark:border-brand-teal/30
                                        dark:bg-brand-teal/10
                                        dark:text-brand-teal-light
                                        "
                                    >
                                        <ShieldCheckIcon className="h-4 w-4" />
                                        Account recovery
                                    </div>

                                    <h1 className="text-4xl font-black leading-tight tracking-tight text-light-text dark:text-dark-text xl:text-5xl">
                                        Get back to your
                                        <span className="text-brand-teal">
                                            {' '}
                                            Vibe.
                                        </span>
                                    </h1>

                                    <p className="mt-5 max-w-lg text-base leading-7 text-light-text-muted dark:text-dark-text-muted">
                                        We’ll help you securely regain
                                        access to your VibeNationHQ
                                        account and get you back to the
                                        stories, music, entertainment,
                                        and culture you care about.
                                    </p>
                                </FadeIn>
                            </div>
                        </div>

                        <div className="relative z-10">
                            <div
                                className="
                                rounded-xl
                                border border-light-border-soft
                                bg-light-surface
                                p-4
                                dark:border-dark-border-soft
                                dark:bg-dark-surface
                                "
                            >
                                <div className="flex items-start gap-3">
                                    <div
                                        className="
                                        flex h-9 w-9 shrink-0 items-center justify-center
                                        rounded-lg
                                        bg-brand-teal/10
                                        text-brand-teal
                                        "
                                    >
                                        <LockIcon className="h-4 w-4" />
                                    </div>

                                    <div>
                                        <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                                            Your account stays protected
                                        </p>

                                        <p className="mt-1 text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                                            Password recovery uses
                                            verified account information
                                            to help keep your account
                                            secure.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div
                            className="
                            pointer-events-none absolute
                            -bottom-28 -right-28
                            h-72 w-72
                            rounded-full
                            bg-brand-teal/[0.07]
                            blur-3xl
                        "
                        />
                    </section>

                    {/* Forgot password form */}
                    <section
                        className="
                        flex items-center justify-center
                        px-5 pb-7 pt-20
                        sm:px-8 sm:pb-10 sm:pt-20
                        lg:p-10
                        xl:p-14
                        "
                    >
                        <FadeIn className="w-full max-w-md">
                            {/* Mobile brand */}
                            <div className="lg:hidden">
                                <Link
                                    href="/"
                                    className="inline-flex items-center"
                                    aria-label="VibeNationHQ home"
                                >
                                    <span className="text-xl font-black tracking-tight text-light-text dark:text-dark-text">
                                        VibeNation
                                        <span className="text-brand-teal">
                                            HQ
                                        </span>
                                    </span>
                                </Link>
                            </div>

                            <div className="mt-8 lg:mt-0">
                                {!isSubmitted ? (
                                    <>
                                        <div className="mb-8">
                                            <div
                                                className="
                                                mb-4 flex h-11 w-11 items-center justify-center
                                                rounded-xl
                                                border border-brand-teal/20
                                                bg-brand-teal/10
                                                text-brand-teal
                                                dark:border-brand-teal/30
                                                dark:bg-brand-teal/10
                                                "
                                            >
                                                <LockIcon className="h-5 w-5" />
                                            </div>

                                            <h2 className="text-2xl font-bold tracking-tight text-light-text dark:text-dark-text sm:text-3xl">
                                                Forgot your password?
                                            </h2>

                                            <p className="mt-2 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                                                Enter the email address
                                                linked to your account and
                                                we’ll send you instructions
                                                to reset your password.
                                            </p>
                                        </div>

                                        <form
                                            className="space-y-5"
                                            onSubmit={handleSubmit}
                                        >
                                            {/* Email */}
                                            <div>
                                                <label
                                                    htmlFor="email"
                                                    className="mb-2 block text-sm font-semibold text-light-text dark:text-dark-text"
                                                >
                                                    Email address
                                                </label>

                                                <div className="relative">
                                                    <MailIcon
                                                        className="
                                                        pointer-events-none absolute left-3.5 top-1/2
                                                        h-5 w-5 -translate-y-1/2
                                                        text-light-text-soft
                                                        dark:text-dark-text-soft
                                                        "
                                                    />

                                                    <input
                                                        id="email"
                                                        name="email"
                                                        type="email"
                                                        autoComplete="email"
                                                        placeholder="you@example.com"
                                                        value={email}
                                                        onChange={(event) => {
                                                            setEmail(
                                                                event.target.value,
                                                            );

                                                            if (error) {
                                                                setError('');
                                                            }
                                                        }}
                                                        disabled={isSubmitting}
                                                        required
                                                        className="
                                                            h-12 w-full rounded-xl
                                                            border border-light-border
                                                            bg-light-surface
                                                            pl-11 pr-4
                                                            text-sm text-light-text
                                                            placeholder:text-light-text-soft
                                                            outline-none
                                                            transition-all duration-200
                                                            focus:border-brand-teal
                                                            focus:ring-4
                                                            focus:ring-brand-teal/10
                                                            disabled:cursor-not-allowed
                                                            disabled:opacity-60
                                                            dark:border-dark-border
                                                            dark:bg-dark-surface-soft
                                                            dark:text-dark-text
                                                            dark:placeholder:text-dark-text-soft
                                                            dark:focus:border-brand-teal
                                                            dark:focus:ring-brand-teal/15
                                                        "
                                                    />
                                                </div>
                                            </div>

                                            {/* Error */}
                                            {error && (
                                                <div
                                                    role="alert"
                                                    className="
                                                    rounded-xl
                                                    border border-red-500/20
                                                    bg-red-500/5
                                                    px-4 py-3
                                                    text-sm leading-5
                                                    text-red-600
                                                    dark:border-red-400/20
                                                    dark:bg-red-400/5
                                                    dark:text-red-400
                                                    "
                                                >
                                                    {error}
                                                </div>
                                            )}

                                            {/* Submit */}
                                            <button
                                                type="submit"
                                                disabled={
                                                    isSubmitting ||
                                                    !email.trim()
                                                }
                                                className="
                                                    flex h-12 w-full items-center justify-center
                                                    rounded-xl
                                                    bg-brand-teal
                                                    px-4
                                                    text-sm font-bold text-white
                                                    shadow-sm shadow-brand-teal/20
                                                    transition-all duration-200
                                                    hover:bg-brand-teal-dark
                                                    active:scale-[0.99]
                                                    focus:outline-none
                                                    focus:ring-4
                                                    focus:ring-brand-teal/20
                                                    disabled:cursor-not-allowed
                                                    disabled:opacity-60
                                                "
                                            >
                                                {isSubmitting
                                                    ? 'Sending...'
                                                    : 'Send reset link'}
                                            </button>
                                        </form>
                                    </>
                                ) : (
                                    <div className="text-center">
                                        <div
                                            className="
                                            mx-auto mb-5 flex h-14 w-14 items-center justify-center
                                            rounded-2xl
                                            border border-brand-teal/20
                                            bg-brand-teal/10
                                            text-brand-teal
                                            "
                                        >
                                            <CheckCircleIcon className="h-7 w-7" />
                                        </div>

                                        <h2 className="text-2xl font-bold tracking-tight text-light-text dark:text-dark-text sm:text-3xl">
                                            Check your email
                                        </h2>

                                        <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                                            If an account exists for{' '}
                                            <span className="font-semibold text-light-text dark:text-dark-text">
                                                {email.trim()}
                                            </span>
                                            , we’ve sent a password reset
                                            link to that address.
                                        </p>

                                        <div
                                            className="
                                            mt-6 rounded-xl
                                            border border-light-border-soft
                                            bg-light-surface-soft
                                            px-4 py-3
                                            text-left
                                            dark:border-dark-border-soft
                                            dark:bg-dark-surface-soft
                                            "
                                        >
                                            <p className="text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                                                The reset link will expire
                                                after 1 hour. If you don’t
                                                see the email, check your
                                                spam or junk folder.
                                            </p>
                                        </div>

                                        <Link
                                            href="/login"
                                            className="
                                            mt-7 inline-flex
                                            text-sm font-semibold
                                            text-brand-teal-dark
                                            transition-colors
                                            hover:text-brand-teal
                                            dark:text-brand-teal-light
                                            dark:hover:text-brand-teal
                                            "
                                        >
                                            Back to sign in
                                        </Link>
                                    </div>
                                )}

                                {/* Security note */}
                                <div
                                    className="
                                    mt-8 flex items-start gap-3
                                    border-t border-light-border-soft
                                    pt-5
                                    dark:border-dark-border-soft
                                "
                                >
                                    <ShieldCheckIcon
                                        className="
                                        mt-0.5 h-4 w-4 shrink-0
                                        text-light-text-soft
                                        dark:text-dark-text-soft
                                        "
                                    />

                                    <p className="text-[11px] leading-5 text-light-text-soft dark:text-dark-text-soft">
                                        For your security, recovery
                                        instructions are sent only to
                                        verified account recovery methods.
                                    </p>
                                </div>
                            </div>
                        </FadeIn>
                    </section>
                </div>
            </div>
        </div>
    );
}