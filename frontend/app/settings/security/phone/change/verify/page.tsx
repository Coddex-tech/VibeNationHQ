'use client';

import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import HomeNav from '@/components/special/HomeNav';
import FadeIn from '@/components/FadeIn';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  PhoneIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';

type PhoneChangeConfirmResponse = {
  detail: string;
  phone_number: string;
  verified: boolean;
};

const countryDialCodes: Record<string, string> = {
  NG: '+234',
  GH: '+233',
  KE: '+254',
  ZA: '+27',
  GB: '+44',
  US: '+1',
};

const maskPhoneNumber = (
  phoneNumber: string,
) => {
  if (!phoneNumber) {
    return '';
  }

  if (phoneNumber.length <= 7) {
    return phoneNumber;
  }

  return `${phoneNumber.slice(0, 4)}••••${phoneNumber.slice(-3)}`;
};

export default function VerifyPhoneChangePage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const phoneNumber =
    searchParams.get('phone') ?? '';

  const countryCode =
    searchParams.get('country_code') ?? 'NG';

  const dialCode =
    countryDialCodes[countryCode] ?? '';

  const [code, setCode] = useState('');
  const [submitting, setSubmitting] =
    useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] =
    useState(false);

  const inputRef =
    useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!phoneNumber) {
      router.replace(
        '/settings/security/phone/change',
      );
      return;
    }

    inputRef.current?.focus();
  }, [phoneNumber, router]);

  const handleCodeChange = (
    value: string,
  ) => {
    const digitsOnly =
      value.replace(/\D/g, '').slice(0, 6);

    setCode(digitsOnly);
    setError('');
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (code.length !== 6) {
      setError(
        'Enter the 6-digit verification code.',
      );
      return;
    }

    if (!phoneNumber) {
      setError(
        'Your phone number is missing. Please start again.',
      );
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response =
        await apiRequest<PhoneChangeConfirmResponse>(
          '/api/phone/change/verify/',
          {
            method: 'POST',
            body: JSON.stringify({
              phone_number: phoneNumber,
              country_code: countryCode,
              code,
            }),
          },
        );

      if (!response.verified) {
        setError(
          'The phone number could not be verified.',
        );
        return;
      }

      setSuccess(true);

      setTimeout(() => {
        router.replace(
          '/settings/security',
        );
      }, 1200);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(
          'Something went wrong. Please try again.',
        );
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-light-bg text-light-text transition-colors duration-300 dark:bg-dark-bg dark:text-dark-text">
      <HomeNav />

      <main className="mx-auto w-full max-w-3xl px-4 pb-12 pt-6 sm:px-6 sm:pt-8 lg:px-8">
        <FadeIn>
          <div className="mb-6">
            <button
              type="button"
              onClick={() =>
                router.push(
                  '/settings/security/phone/change',
                )
              }
              className="
                inline-flex items-center gap-2
                text-sm font-semibold
                text-light-text-muted
                transition-colors
                hover:text-light-text
                dark:text-dark-text-muted
                dark:hover:text-dark-text
              "
            >
              <ArrowLeftIcon className="h-4 w-4" />
              Change phone number
            </button>
          </div>

          <div
            className="
              mx-auto max-w-xl
              overflow-hidden rounded-2xl
              border border-light-border
              bg-light-surface
              shadow-sm
              dark:border-dark-border
              dark:bg-dark-surface
            "
          >
            <div className="px-5 py-8 sm:px-8 sm:py-10">
              <div className="text-center">
                <div
                  className="
                    mx-auto flex h-12 w-12
                    items-center justify-center
                    rounded-xl
                    border border-brand-teal/20
                    bg-brand-teal/10
                    text-brand-teal
                    dark:border-brand-teal/30
                  "
                >
                  {success ? (
                    <CheckCircleIcon className="h-6 w-6" />
                  ) : (
                    <PhoneIcon className="h-5 w-5" />
                  )}
                </div>

                <h1 className="mt-5 text-2xl font-bold tracking-tight sm:text-3xl">
                  {success
                    ? 'Phone number updated'
                    : 'Verify your new number'}
                </h1>

                {success ? (
                  <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    Your new phone number has been
                    verified successfully. Taking you
                    back to Security...
                  </p>
                ) : (
                  <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    We sent a 6-digit verification code
                    to your new phone number.
                  </p>
                )}
              </div>

              {!success && (
                <>
                  {/* Phone number */}
                  <div
                    className="
                      mx-auto mt-7 max-w-sm
                      rounded-xl
                      border border-light-border-soft
                      bg-light-surface-soft
                      px-4 py-3
                      text-center
                      dark:border-dark-border-soft
                      dark:bg-dark-surface-soft
                    "
                  >
                    <p className="text-xs font-semibold uppercase tracking-wide text-light-text-soft dark:text-dark-text-soft">
                      New phone number
                    </p>

                    <p className="mt-1.5 text-sm font-bold text-light-text dark:text-dark-text">
                      {maskPhoneNumber(
                        phoneNumber,
                      )}
                    </p>
                  </div>

                  <form
                    onSubmit={handleSubmit}
                    className="mx-auto mt-7 max-w-sm"
                  >
                    <label
                      htmlFor="verification-code"
                      className="
                        mb-2 block text-center
                        text-sm font-semibold
                        text-light-text
                        dark:text-dark-text
                      "
                    >
                      Verification code
                    </label>

                    <input
                      ref={inputRef}
                      id="verification-code"
                      name="code"
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      value={code}
                      onChange={(event) =>
                        handleCodeChange(
                          event.target.value,
                        )
                      }
                      placeholder="000000"
                      disabled={submitting}
                      className="
                        h-14 w-full rounded-xl
                        border border-light-border
                        bg-light-surface
                        px-4
                        text-center
                        text-xl font-bold
                        tracking-[0.45em]
                        text-light-text
                        placeholder:tracking-[0.35em]
                        placeholder:text-light-text-soft
                        outline-none
                        transition-all duration-200
                        focus:border-brand-teal
                        focus:ring-4
                        focus:ring-brand-teal/10
                        dark:border-dark-border
                        dark:bg-dark-surface-soft
                        dark:text-dark-text
                        dark:placeholder:text-dark-text-soft
                        dark:focus:border-brand-teal
                        dark:focus:ring-brand-teal/15
                        disabled:cursor-not-allowed
                        disabled:opacity-60
                      "
                    />

                    <p className="mt-2 text-center text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                      Enter the code sent to{' '}
                      {dialCode
                        ? `${dialCode} `
                        : ''}
                      {maskPhoneNumber(
                        phoneNumber,
                      )}
                    </p>

                    {error && (
                      <div
                        role="alert"
                        className="
                          mt-5 rounded-xl
                          border border-red-500/20
                          bg-red-500/5
                          px-4 py-3
                          text-center
                          text-sm leading-6
                          text-red-700
                          dark:text-red-300
                        "
                      >
                        {error}
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={
                        submitting ||
                        code.length !== 6
                      }
                      className="
                        mt-6 flex h-12 w-full
                        items-center justify-center
                        rounded-xl
                        bg-brand-teal
                        px-4
                        text-sm font-bold
                        text-white
                        shadow-sm
                        shadow-brand-teal/20
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
                      {submitting
                        ? 'Verifying...'
                        : 'Verify new phone number'}
                    </button>
                  </form>

                  <div className="mt-7 text-center">
                    <p className="text-sm text-light-text-muted dark:text-dark-text-muted">
                      Didn’t receive the code?
                    </p>

                    <button
                      type="button"
                      onClick={() =>
                        router.push(
                          '/settings/security/phone/change',
                        )
                      }
                      className="
                        mt-1.5
                        text-sm font-bold
                        text-brand-teal-dark
                        hover:text-brand-teal
                        dark:text-brand-teal-light
                        dark:hover:text-brand-teal
                      "
                    >
                      Start again
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </FadeIn>
      </main>
    </div>
  );
}