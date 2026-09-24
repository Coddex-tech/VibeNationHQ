'use client';

import {
  FormEvent,
  useEffect,
  useState,
} from 'react';
import { useRouter } from 'next/navigation';

import HomeNav from '@/components/special/HomeNav';
import FadeIn from '@/components/FadeIn';
import {
  ArrowLeftIcon,
  LockIcon,
  PhoneIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';

type CurrentUserResponse = {
  user: {
    id: string;
    email: string;
    username: string;
    is_active?: boolean;
    phone?: {
      phone_number: string;
      is_verified: boolean;
      verified_at?: string | null;
    } | null;
  };
};

type PhoneChangeRequestResponse = {
  detail?: string;
};

const countries = [
  {
    code: 'NG',
    name: 'Nigeria',
    dialCode: '+234',
  },
  {
    code: 'GH',
    name: 'Ghana',
    dialCode: '+233',
  },
  {
    code: 'KE',
    name: 'Kenya',
    dialCode: '+254',
  },
  {
    code: 'ZA',
    name: 'South Africa',
    dialCode: '+27',
  },
  {
    code: 'GB',
    name: 'United Kingdom',
    dialCode: '+44',
  },
  {
    code: 'US',
    name: 'United States',
    dialCode: '+1',
  },
];

const formatPhoneNumber = (value: string) => {
  if (!value) {
    return '';
  }

  if (value.length <= 7) {
    return value;
  }

  return `${value.slice(0, 4)}••••${value.slice(-3)}`;
};

export default function ChangePhonePage() {
  const router = useRouter();

  const [currentUser, setCurrentUser] =
    useState<CurrentUserResponse['user'] | null>(
      null,
    );

  const [countryCode, setCountryCode] =
    useState('NG');

  const [phoneNumber, setPhoneNumber] =
    useState('');

  const [password, setPassword] =
    useState('');

  const [loadingUser, setLoadingUser] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState('');

  const selectedCountry = countries.find(
    (country) => country.code === countryCode,
  );

  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        setLoadingUser(true);
        setError('');

        const data =
          await apiRequest<CurrentUserResponse>(
            '/api/accounts/me/',
          );

        setCurrentUser(data.user);
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 401) {
            router.replace(
              '/login?next=/settings/security/phone/change',
            );

            return;
          }

          setError(err.message);
        } else {
          setError(
            'Unable to load your account. Please try again.',
          );
        }
      } finally {
        setLoadingUser(false);
      }
    };

    loadCurrentUser();
  }, [router]);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!phoneNumber.trim()) {
      setError(
        'Enter your new phone number.',
      );
      return;
    }

    if (!password) {
      setError(
        'Enter your current password.',
      );
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await apiRequest<PhoneChangeRequestResponse>(
        '/api/phone/change/',
        {
          method: 'POST',
          body: JSON.stringify({
            current_password: password,
            phone_number: phoneNumber.trim(),
            country_code:
              selectedCountry?.code ?? 'NG',
          }),
        },
      );

      const params = new URLSearchParams({
        phone: phoneNumber.trim(),
        country_code:
          selectedCountry?.code ?? 'NG',
      });

      router.push(
        `/settings/security/phone/change/verify?${params.toString()}`,
      );
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
                  '/settings/security',
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
              Security
            </button>
          </div>

          <div
            className="
              overflow-hidden rounded-2xl
              border border-light-border
              bg-light-surface
              shadow-sm
              dark:border-dark-border
              dark:bg-dark-surface
            "
          >
            <div
              className="
                border-b border-light-border-soft
                px-5 py-6
                sm:px-7
                dark:border-dark-border-soft
              "
            >
              <div className="flex items-start gap-4">
                <div
                  className="
                    flex h-11 w-11 shrink-0
                    items-center justify-center
                    rounded-xl
                    border border-brand-teal/20
                    bg-brand-teal/10
                    text-brand-teal
                    dark:border-brand-teal/30
                  "
                >
                  <PhoneIcon className="h-5 w-5" />
                </div>

                <div>
                  <h1 className="text-xl font-bold tracking-tight sm:text-2xl">
                    Change phone number
                  </h1>

                  <p className="mt-1.5 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    Update the phone number associated
                    with your VibeNationHQ account.
                  </p>
                </div>
              </div>
            </div>

            <div className="px-5 py-6 sm:px-7 sm:py-8">
              {/* Current phone */}
              <div
                className="
                  rounded-xl
                  border border-light-border-soft
                  bg-light-surface-soft
                  p-4
                  dark:border-dark-border-soft
                  dark:bg-dark-surface-soft
                "
              >
                <p className="text-xs font-semibold uppercase tracking-wide text-light-text-soft dark:text-dark-text-soft">
                  Current phone number
                </p>

                {loadingUser ? (
                  <div className="mt-2 h-5 w-32 animate-pulse rounded bg-light-surface-muted dark:bg-dark-surface-muted" />
                ) : currentUser?.phone?.is_verified ? (
                  <div className="mt-2 flex items-center gap-2">
                    <p className="text-sm font-semibold text-light-text dark:text-dark-text">
                      {formatPhoneNumber(
                        currentUser.phone.phone_number,
                      )}
                    </p>

                    <span
                      className="
                        inline-flex items-center
                        rounded-full
                        bg-brand-teal/10
                        px-2 py-0.5
                        text-[11px] font-semibold
                        text-brand-teal-dark
                        dark:text-brand-teal-light
                      "
                    >
                      Verified
                    </span>
                  </div>
                ) : (
                  <p className="mt-2 text-sm text-light-text-muted dark:text-dark-text-muted">
                    No verified phone number
                  </p>
                )}
              </div>

              <div className="my-7 h-px bg-light-border-soft dark:bg-dark-border-soft" />

              <form
                onSubmit={handleSubmit}
                className="space-y-5"
              >
                {/* Current password */}
                <div>
                  <label
                    htmlFor="current-password"
                    className="
                      mb-2 block text-sm font-semibold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Current password
                  </label>

                  <div className="relative">
                    <LockIcon
                      className="
                        pointer-events-none
                        absolute left-3.5 top-1/2
                        h-5 w-5
                        -translate-y-1/2
                        text-light-text-soft
                        dark:text-dark-text-soft
                      "
                    />

                    <input
                      id="current-password"
                      name="currentPassword"
                      type="password"
                      autoComplete="current-password"
                      value={password}
                      onChange={(event) =>
                        setPassword(
                          event.target.value,
                        )
                      }
                      placeholder="Enter your current password"
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
                        dark:border-dark-border
                        dark:bg-dark-surface-soft
                        dark:text-dark-text
                        dark:placeholder:text-dark-text-soft
                        dark:focus:border-brand-teal
                        dark:focus:ring-brand-teal/15
                      "
                    />
                  </div>

                  <p className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                    Confirm your current password before
                    changing this number.
                  </p>
                </div>

                {/* Country */}
                <div>
                  <label
                    htmlFor="country"
                    className="
                      mb-2 block text-sm font-semibold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    Country
                  </label>

                  <select
                    id="country"
                    name="country"
                    value={countryCode}
                    onChange={(event) =>
                      setCountryCode(
                        event.target.value,
                      )
                    }
                    className="
                      h-12 w-full rounded-xl
                      border border-light-border
                      bg-light-surface
                      px-4
                      text-sm text-light-text
                      outline-none
                      transition-all duration-200
                      focus:border-brand-teal
                      focus:ring-4
                      focus:ring-brand-teal/10
                      dark:border-dark-border
                      dark:bg-dark-surface-soft
                      dark:text-dark-text
                      dark:focus:border-brand-teal
                    "
                  >
                    {countries.map(
                      (country) => (
                        <option
                          key={country.code}
                          value={country.code}
                        >
                          {country.name} (
                          {country.dialCode})
                        </option>
                      ),
                    )}
                  </select>
                </div>

                {/* New phone */}
                <div>
                  <label
                    htmlFor="phone-number"
                    className="
                      mb-2 block text-sm font-semibold
                      text-light-text
                      dark:text-dark-text
                    "
                  >
                    New phone number
                  </label>

                  <div className="flex gap-2">
                    <div
                      className="
                        flex h-12 shrink-0
                        items-center
                        rounded-xl
                        border border-light-border
                        bg-light-surface-soft
                        px-3.5
                        text-sm font-semibold
                        text-light-text-muted
                        dark:border-dark-border
                        dark:bg-dark-surface-muted
                        dark:text-dark-text-muted
                      "
                    >
                      {selectedCountry?.dialCode}
                    </div>

                    <input
                      id="phone-number"
                      name="phoneNumber"
                      type="tel"
                      inputMode="tel"
                      autoComplete="tel"
                      value={phoneNumber}
                      onChange={(event) =>
                        setPhoneNumber(
                          event.target.value,
                        )
                      }
                      placeholder="801 234 5678"
                      className="
                        h-12 min-w-0 flex-1 rounded-xl
                        border border-light-border
                        bg-light-surface
                        px-4
                        text-sm text-light-text
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
                      "
                    />
                  </div>

                  <p className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                    We’ll send a verification code to your
                    new number.
                  </p>
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
                      text-sm leading-6
                      text-red-700
                      dark:text-red-300
                    "
                  >
                    {error}
                  </div>
                )}

                {/* Submit */}
                <button
                  type="submit"
                  disabled={
                    submitting ||
                    loadingUser
                  }
                  className="
                    flex h-12 w-full
                    items-center justify-center
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
                  {submitting
                    ? 'Sending verification code...'
                    : 'Send verification code'}
                </button>
              </form>

              <div className="mt-6">
                <p className="text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                  Your current verified phone number will
                  remain active until the new number is
                  successfully verified.
                </p>
              </div>
            </div>
          </div>
        </FadeIn>
      </main>
    </div>
  );
}