'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';

import FadeIn from '@/components/FadeIn';
import ThemeToggle from '@/components/ThemeToggle';
import {
  CheckCircleIcon,
  HomeIcon,
  PhoneIcon,
  ShieldCheckIcon,
} from '@/components/Icons';
import { ApiError, apiRequest } from '@/lib/api';
import HomeNav from '@/components/special/HomeNav';

type PhoneStep = 'phone' | 'verify' | 'success';

type PhoneRequestResponse = {
  message: string;
};

type PhoneConfirmResponse = {
  message: string;
  phone?: {
    phone_number: string;
    country_code: string;
    is_verified?: boolean;
  };
};

type Country = {
  code: string;
  name: string;
  dialCode: string;
};

const countries: Country[] = [
  {
    code: 'AF',
    name: 'Afghanistan',
    dialCode: '+93',
  },
  {
    code: 'AL',
    name: 'Albania',
    dialCode: '+355',
  },
  {
    code: 'DZ',
    name: 'Algeria',
    dialCode: '+213',
  },
  {
    code: 'AD',
    name: 'Andorra',
    dialCode: '+376',
  },
  {
    code: 'AO',
    name: 'Angola',
    dialCode: '+244',
  },
  {
    code: 'AG',
    name: 'Antigua and Barbuda',
    dialCode: '+1',
  },
  {
    code: 'AR',
    name: 'Argentina',
    dialCode: '+54',
  },
  {
    code: 'AM',
    name: 'Armenia',
    dialCode: '+374',
  },
  {
    code: 'AU',
    name: 'Australia',
    dialCode: '+61',
  },
  {
    code: 'AT',
    name: 'Austria',
    dialCode: '+43',
  },
  {
    code: 'AZ',
    name: 'Azerbaijan',
    dialCode: '+994',
  },
  {
    code: 'BS',
    name: 'Bahamas',
    dialCode: '+1',
  },
  {
    code: 'BH',
    name: 'Bahrain',
    dialCode: '+973',
  },
  {
    code: 'BD',
    name: 'Bangladesh',
    dialCode: '+880',
  },
  {
    code: 'BB',
    name: 'Barbados',
    dialCode: '+1',
  },
  {
    code: 'BY',
    name: 'Belarus',
    dialCode: '+375',
  },
  {
    code: 'BE',
    name: 'Belgium',
    dialCode: '+32',
  },
  {
    code: 'BZ',
    name: 'Belize',
    dialCode: '+501',
  },
  {
    code: 'BJ',
    name: 'Benin',
    dialCode: '+229',
  },
  {
    code: 'BT',
    name: 'Bhutan',
    dialCode: '+975',
  },
  {
    code: 'BO',
    name: 'Bolivia',
    dialCode: '+591',
  },
  {
    code: 'BA',
    name: 'Bosnia and Herzegovina',
    dialCode: '+387',
  },
  {
    code: 'BW',
    name: 'Botswana',
    dialCode: '+267',
  },
  {
    code: 'BR',
    name: 'Brazil',
    dialCode: '+55',
  },
  {
    code: 'BN',
    name: 'Brunei',
    dialCode: '+673',
  },
  {
    code: 'BG',
    name: 'Bulgaria',
    dialCode: '+359',
  },
  {
    code: 'BF',
    name: 'Burkina Faso',
    dialCode: '+226',
  },
  {
    code: 'BI',
    name: 'Burundi',
    dialCode: '+257',
  },
  {
    code: 'KH',
    name: 'Cambodia',
    dialCode: '+855',
  },
  {
    code: 'CM',
    name: 'Cameroon',
    dialCode: '+237',
  },
  {
    code: 'CA',
    name: 'Canada',
    dialCode: '+1',
  },
  {
    code: 'CV',
    name: 'Cape Verde',
    dialCode: '+238',
  },
  {
    code: 'CF',
    name: 'Central African Republic',
    dialCode: '+236',
  },
  {
    code: 'TD',
    name: 'Chad',
    dialCode: '+235',
  },
  {
    code: 'CL',
    name: 'Chile',
    dialCode: '+56',
  },
  {
    code: 'CN',
    name: 'China',
    dialCode: '+86',
  },
  {
    code: 'CO',
    name: 'Colombia',
    dialCode: '+57',
  },
  {
    code: 'KM',
    name: 'Comoros',
    dialCode: '+269',
  },
  {
    code: 'CG',
    name: 'Congo',
    dialCode: '+242',
  },
  {
    code: 'CD',
    name: 'Democratic Republic of the Congo',
    dialCode: '+243',
  },
  {
    code: 'CR',
    name: 'Costa Rica',
    dialCode: '+506',
  },
  {
    code: 'CI',
    name: 'Côte d’Ivoire',
    dialCode: '+225',
  },
  {
    code: 'HR',
    name: 'Croatia',
    dialCode: '+385',
  },
  {
    code: 'CU',
    name: 'Cuba',
    dialCode: '+53',
  },
  {
    code: 'CY',
    name: 'Cyprus',
    dialCode: '+357',
  },
  {
    code: 'CZ',
    name: 'Czech Republic',
    dialCode: '+420',
  },
  {
    code: 'DK',
    name: 'Denmark',
    dialCode: '+45',
  },
  {
    code: 'DJ',
    name: 'Djibouti',
    dialCode: '+253',
  },
  {
    code: 'DM',
    name: 'Dominica',
    dialCode: '+1',
  },
  {
    code: 'DO',
    name: 'Dominican Republic',
    dialCode: '+1',
  },
  {
    code: 'EC',
    name: 'Ecuador',
    dialCode: '+593',
  },
  {
    code: 'EG',
    name: 'Egypt',
    dialCode: '+20',
  },
  {
    code: 'SV',
    name: 'El Salvador',
    dialCode: '+503',
  },
  {
    code: 'GQ',
    name: 'Equatorial Guinea',
    dialCode: '+240',
  },
  {
    code: 'ER',
    name: 'Eritrea',
    dialCode: '+291',
  },
  {
    code: 'EE',
    name: 'Estonia',
    dialCode: '+372',
  },
  {
    code: 'SZ',
    name: 'Eswatini',
    dialCode: '+268',
  },
  {
    code: 'ET',
    name: 'Ethiopia',
    dialCode: '+251',
  },
  {
    code: 'FJ',
    name: 'Fiji',
    dialCode: '+679',
  },
  {
    code: 'FI',
    name: 'Finland',
    dialCode: '+358',
  },
  {
    code: 'FR',
    name: 'France',
    dialCode: '+33',
  },
  {
    code: 'GA',
    name: 'Gabon',
    dialCode: '+241',
  },
  {
    code: 'GM',
    name: 'Gambia',
    dialCode: '+220',
  },
  {
    code: 'GE',
    name: 'Georgia',
    dialCode: '+995',
  },
  {
    code: 'DE',
    name: 'Germany',
    dialCode: '+49',
  },
  {
    code: 'GH',
    name: 'Ghana',
    dialCode: '+233',
  },
  {
    code: 'GR',
    name: 'Greece',
    dialCode: '+30',
  },
  {
    code: 'GD',
    name: 'Grenada',
    dialCode: '+1',
  },
  {
    code: 'GT',
    name: 'Guatemala',
    dialCode: '+502',
  },
  {
    code: 'GN',
    name: 'Guinea',
    dialCode: '+224',
  },
  {
    code: 'GW',
    name: 'Guinea-Bissau',
    dialCode: '+245',
  },
  {
    code: 'GY',
    name: 'Guyana',
    dialCode: '+592',
  },
  {
    code: 'HT',
    name: 'Haiti',
    dialCode: '+509',
  },
  {
    code: 'HN',
    name: 'Honduras',
    dialCode: '+504',
  },
  {
    code: 'HU',
    name: 'Hungary',
    dialCode: '+36',
  },
  {
    code: 'IS',
    name: 'Iceland',
    dialCode: '+354',
  },
  {
    code: 'IN',
    name: 'India',
    dialCode: '+91',
  },
  {
    code: 'ID',
    name: 'Indonesia',
    dialCode: '+62',
  },
  {
    code: 'IR',
    name: 'Iran',
    dialCode: '+98',
  },
  {
    code: 'IQ',
    name: 'Iraq',
    dialCode: '+964',
  },
  {
    code: 'IE',
    name: 'Ireland',
    dialCode: '+353',
  },
  {
    code: 'IL',
    name: 'Israel',
    dialCode: '+972',
  },
  {
    code: 'IT',
    name: 'Italy',
    dialCode: '+39',
  },
  {
    code: 'JM',
    name: 'Jamaica',
    dialCode: '+1',
  },
  {
    code: 'JP',
    name: 'Japan',
    dialCode: '+81',
  },
  {
    code: 'JO',
    name: 'Jordan',
    dialCode: '+962',
  },
  {
    code: 'KZ',
    name: 'Kazakhstan',
    dialCode: '+7',
  },
  {
    code: 'KE',
    name: 'Kenya',
    dialCode: '+254',
  },
  {
    code: 'KI',
    name: 'Kiribati',
    dialCode: '+686',
  },
  {
    code: 'KW',
    name: 'Kuwait',
    dialCode: '+965',
  },
  {
    code: 'KG',
    name: 'Kyrgyzstan',
    dialCode: '+996',
  },
  {
    code: 'LA',
    name: 'Laos',
    dialCode: '+856',
  },
  {
    code: 'LV',
    name: 'Latvia',
    dialCode: '+371',
  },
  {
    code: 'LB',
    name: 'Lebanon',
    dialCode: '+961',
  },
  {
    code: 'LS',
    name: 'Lesotho',
    dialCode: '+266',
  },
  {
    code: 'LR',
    name: 'Liberia',
    dialCode: '+231',
  },
  {
    code: 'LY',
    name: 'Libya',
    dialCode: '+218',
  },
  {
    code: 'LI',
    name: 'Liechtenstein',
    dialCode: '+423',
  },
  {
    code: 'LT',
    name: 'Lithuania',
    dialCode: '+370',
  },
  {
    code: 'LU',
    name: 'Luxembourg',
    dialCode: '+352',
  },
  {
    code: 'MG',
    name: 'Madagascar',
    dialCode: '+261',
  },
  {
    code: 'MW',
    name: 'Malawi',
    dialCode: '+265',
  },
  {
    code: 'MY',
    name: 'Malaysia',
    dialCode: '+60',
  },
  {
    code: 'MV',
    name: 'Maldives',
    dialCode: '+960',
  },
  {
    code: 'ML',
    name: 'Mali',
    dialCode: '+223',
  },
  {
    code: 'MT',
    name: 'Malta',
    dialCode: '+356',
  },
  {
    code: 'MR',
    name: 'Mauritania',
    dialCode: '+222',
  },
  {
    code: 'MU',
    name: 'Mauritius',
    dialCode: '+230',
  },
  {
    code: 'MX',
    name: 'Mexico',
    dialCode: '+52',
  },
  {
    code: 'MD',
    name: 'Moldova',
    dialCode: '+373',
  },
  {
    code: 'MC',
    name: 'Monaco',
    dialCode: '+377',
  },
  {
    code: 'MN',
    name: 'Mongolia',
    dialCode: '+976',
  },
  {
    code: 'ME',
    name: 'Montenegro',
    dialCode: '+382',
  },
  {
    code: 'MA',
    name: 'Morocco',
    dialCode: '+212',
  },
  {
    code: 'MZ',
    name: 'Mozambique',
    dialCode: '+258',
  },
  {
    code: 'MM',
    name: 'Myanmar',
    dialCode: '+95',
  },
  {
    code: 'NA',
    name: 'Namibia',
    dialCode: '+264',
  },
  {
    code: 'NP',
    name: 'Nepal',
    dialCode: '+977',
  },
  {
    code: 'NL',
    name: 'Netherlands',
    dialCode: '+31',
  },
  {
    code: 'NZ',
    name: 'New Zealand',
    dialCode: '+64',
  },
  {
    code: 'NI',
    name: 'Nicaragua',
    dialCode: '+505',
  },
  {
    code: 'NE',
    name: 'Niger',
    dialCode: '+227',
  },
  {
    code: 'NG',
    name: 'Nigeria',
    dialCode: '+234',
  },
  {
    code: 'MK',
    name: 'North Macedonia',
    dialCode: '+389',
  },
  {
    code: 'NO',
    name: 'Norway',
    dialCode: '+47',
  },
  {
    code: 'OM',
    name: 'Oman',
    dialCode: '+968',
  },
  {
    code: 'PK',
    name: 'Pakistan',
    dialCode: '+92',
  },
  {
    code: 'PA',
    name: 'Panama',
    dialCode: '+507',
  },
  {
    code: 'PG',
    name: 'Papua New Guinea',
    dialCode: '+675',
  },
  {
    code: 'PY',
    name: 'Paraguay',
    dialCode: '+595',
  },
  {
    code: 'PE',
    name: 'Peru',
    dialCode: '+51',
  },
  {
    code: 'PH',
    name: 'Philippines',
    dialCode: '+63',
  },
  {
    code: 'PL',
    name: 'Poland',
    dialCode: '+48',
  },
  {
    code: 'PT',
    name: 'Portugal',
    dialCode: '+351',
  },
  {
    code: 'QA',
    name: 'Qatar',
    dialCode: '+974',
  },
  {
    code: 'RO',
    name: 'Romania',
    dialCode: '+40',
  },
  {
    code: 'RW',
    name: 'Rwanda',
    dialCode: '+250',
  },
  {
    code: 'KN',
    name: 'Saint Kitts and Nevis',
    dialCode: '+1',
  },
  {
    code: 'LC',
    name: 'Saint Lucia',
    dialCode: '+1',
  },
  {
    code: 'VC',
    name: 'Saint Vincent and the Grenadines',
    dialCode: '+1',
  },
  {
    code: 'WS',
    name: 'Samoa',
    dialCode: '+685',
  },
  {
    code: 'SM',
    name: 'San Marino',
    dialCode: '+378',
  },
  {
    code: 'ST',
    name: 'São Tomé and Príncipe',
    dialCode: '+239',
  },
  {
    code: 'SA',
    name: 'Saudi Arabia',
    dialCode: '+966',
  },
  {
    code: 'SN',
    name: 'Senegal',
    dialCode: '+221',
  },
  {
    code: 'RS',
    name: 'Serbia',
    dialCode: '+381',
  },
  {
    code: 'SC',
    name: 'Seychelles',
    dialCode: '+248',
  },
  {
    code: 'SL',
    name: 'Sierra Leone',
    dialCode: '+232',
  },
  {
    code: 'SG',
    name: 'Singapore',
    dialCode: '+65',
  },
  {
    code: 'SK',
    name: 'Slovakia',
    dialCode: '+421',
  },
  {
    code: 'SI',
    name: 'Slovenia',
    dialCode: '+386',
  },
  {
    code: 'SB',
    name: 'Solomon Islands',
    dialCode: '+677',
  },
  {
    code: 'SO',
    name: 'Somalia',
    dialCode: '+252',
  },
  {
    code: 'ZA',
    name: 'South Africa',
    dialCode: '+27',
  },
  {
    code: 'KR',
    name: 'South Korea',
    dialCode: '+82',
  },
  {
    code: 'SS',
    name: 'South Sudan',
    dialCode: '+211',
  },
  {
    code: 'ES',
    name: 'Spain',
    dialCode: '+34',
  },
  {
    code: 'LK',
    name: 'Sri Lanka',
    dialCode: '+94',
  },
  {
    code: 'SD',
    name: 'Sudan',
    dialCode: '+249',
  },
  {
    code: 'SR',
    name: 'Suriname',
    dialCode: '+597',
  },
  {
    code: 'SE',
    name: 'Sweden',
    dialCode: '+46',
  },
  {
    code: 'CH',
    name: 'Switzerland',
    dialCode: '+41',
  },
  {
    code: 'SY',
    name: 'Syria',
    dialCode: '+963',
  },
  {
    code: 'TW',
    name: 'Taiwan',
    dialCode: '+886',
  },
  {
    code: 'TJ',
    name: 'Tajikistan',
    dialCode: '+992',
  },
  {
    code: 'TZ',
    name: 'Tanzania',
    dialCode: '+255',
  },
  {
    code: 'TH',
    name: 'Thailand',
    dialCode: '+66',
  },
  {
    code: 'TG',
    name: 'Togo',
    dialCode: '+228',
  },
  {
    code: 'TO',
    name: 'Tonga',
    dialCode: '+676',
  },
  {
    code: 'TT',
    name: 'Trinidad and Tobago',
    dialCode: '+1',
  },
  {
    code: 'TN',
    name: 'Tunisia',
    dialCode: '+216',
  },
  {
    code: 'TR',
    name: 'Türkiye',
    dialCode: '+90',
  },
  {
    code: 'TM',
    name: 'Turkmenistan',
    dialCode: '+993',
  },
  {
    code: 'UG',
    name: 'Uganda',
    dialCode: '+256',
  },
  {
    code: 'UA',
    name: 'Ukraine',
    dialCode: '+380',
  },
  {
    code: 'AE',
    name: 'United Arab Emirates',
    dialCode: '+971',
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
  {
    code: 'UY',
    name: 'Uruguay',
    dialCode: '+598',
  },
  {
    code: 'UZ',
    name: 'Uzbekistan',
    dialCode: '+998',
  },
  {
    code: 'VU',
    name: 'Vanuatu',
    dialCode: '+678',
  },
  {
    code: 'VA',
    name: 'Vatican City',
    dialCode: '+39',
  },
  {
    code: 'VE',
    name: 'Venezuela',
    dialCode: '+58',
  },
  {
    code: 'VN',
    name: 'Vietnam',
    dialCode: '+84',
  },
  {
    code: 'YE',
    name: 'Yemen',
    dialCode: '+967',
  },
  {
    code: 'ZM',
    name: 'Zambia',
    dialCode: '+260',
  },
  {
    code: 'ZW',
    name: 'Zimbabwe',
    dialCode: '+263',
  },
];

export default function PhoneSecurityPage() {
  const [step, setStep] =
    useState<PhoneStep>('phone');

  const [phoneNumber, setPhoneNumber] =
    useState('');

  const [countryCode, setCountryCode] =
    useState('NG');

  const [code, setCode] = useState('');

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] = useState('');

  const [successMessage, setSuccessMessage] =
    useState('');

  const [resendAvailableAt, setResendAvailableAt] =
    useState<number | null>(null);

  const [secondsRemaining, setSecondsRemaining] =
    useState(0);

  useEffect(() => {
    if (!resendAvailableAt) {
      setSecondsRemaining(0);
      return;
    }

    function updateCountdown() {
      const remaining = Math.max(
        0,
        Math.ceil(
          (resendAvailableAt - Date.now()) /
            1000,
        ),
      );

      setSecondsRemaining(remaining);

      if (remaining === 0) {
        setResendAvailableAt(null);
      }
    }

    updateCountdown();

    const interval = window.setInterval(
      updateCountdown,
      1000,
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [resendAvailableAt]);

  function clearMessages() {
    setError('');
    setSuccessMessage('');
  }

  async function requestPhoneVerification(
    event?: FormEvent<HTMLFormElement>,
  ) {
    event?.preventDefault();

    clearMessages();

    if (!phoneNumber.trim()) {
      setError(
        'Please enter your phone number.',
      );
      return;
    }

    setSubmitting(true);

    try {
      const data =
        await apiRequest<PhoneRequestResponse>(
          '/api/phone/add/',
          {
            method: 'POST',
            body: JSON.stringify({
              phone_number:
                phoneNumber.trim(),
              country_code: countryCode,
            }),
          },
        );

      setSuccessMessage(
        data.message ||
          'A verification code has been sent to your phone.',
      );

      setCode('');
      setStep('verify');

      setResendAvailableAt(
        Date.now() + 60_000,
      );
    } catch (err) {
      handleApiError(err);
    } finally {
      setSubmitting(false);
    }
  }

  async function verifyPhone(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    clearMessages();

    if (!code.trim()) {
      setError(
        'Please enter the verification code.',
      );
      return;
    }

    if (!/^\d{6}$/.test(code.trim())) {
      setError(
        'Your verification code must contain 6 digits.',
      );
      return;
    }

    setSubmitting(true);

    try {
      const data =
        await apiRequest<PhoneConfirmResponse>(
          '/api/phone/add/verify/',
          {
            method: 'POST',
            body: JSON.stringify({
              phone_number:
                phoneNumber.trim(),
              country_code: countryCode,
              code: code.trim(),
            }),
          },
        );

      setSuccessMessage(
        data.message ||
          'Your phone number has been verified successfully.',
      );

      setStep('success');
    } catch (err) {
      handleApiError(err);
    } finally {
      setSubmitting(false);
    }
  }

  async function resendCode() {
    if (
      submitting ||
      secondsRemaining > 0
    ) {
      return;
    }

    clearMessages();

    setSubmitting(true);

    try {
      const data =
        await apiRequest<PhoneRequestResponse>(
          '/api/phone/add/',
          {
            method: 'POST',
            body: JSON.stringify({
              phone_number:
                phoneNumber.trim(),
              country_code: countryCode,
            }),
          },
        );

      setSuccessMessage(
        data.message ||
          'A new verification code has been sent.',
      );

      setCode('');

      setResendAvailableAt(
        Date.now() + 60_000,
      );
    } catch (err) {
      handleApiError(err);
    } finally {
      setSubmitting(false);
    }
  }

  function handleApiError(err: unknown) {
    if (err instanceof ApiError) {
      const data = err.data;

      const phoneError =
        data?.phone_number;

      const codeError = data?.code;

      const detail = data?.detail;

      if (Array.isArray(phoneError)) {
        setError(
          phoneError.join(' '),
        );
        return;
      }

      if (
        typeof phoneError === 'string'
      ) {
        setError(phoneError);
        return;
      }

      if (Array.isArray(codeError)) {
        setError(
          codeError.join(' '),
        );
        return;
      }

      if (
        typeof codeError === 'string'
      ) {
        setError(codeError);
        return;
      }

      if (typeof detail === 'string') {
        setError(detail);
        return;
      }

      setError(err.message);
      return;
    }

    setError(
      'Something went wrong. Please try again.',
    );
  }

  function maskedPhone() {
    const normalized =
      phoneNumber.trim();

    if (normalized.length <= 4) {
      return normalized;
    }

    return `${normalized.slice(0, 4)}••••${normalized.slice(-2)}`;
  }

  return (
    <main className="min-h-screen bg-light-bg text-light-text dark:bg-dark-bg dark:text-dark-text">
      <HomeNav />

      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-12">
        <FadeIn>
          <div className="mb-8">
            <Link
              href="/settings/security"
              className="mb-5 inline-flex items-center gap-2 text-sm font-medium text-light-text-muted transition-colors hover:text-brand-teal dark:text-dark-text-muted dark:hover:text-brand-teal-light"
            >
              <span aria-hidden="true">
                ←
              </span>
              Back to Security
            </Link>

            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light">
                <PhoneIcon className="h-6 w-6" />
              </div>

              <div>
                <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                  Phone number
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-light-text-muted dark:text-dark-text-muted sm:text-base">
                  Add a verified phone number
                  to strengthen your
                  VibeNationHQ account security
                  and recovery options.
                </p>
              </div>
            </div>
          </div>
        </FadeIn>

        <FadeIn delay={0.05}>
          <section className="overflow-hidden rounded-2xl border border-light-border bg-light-surface shadow-sm dark:border-dark-border dark:bg-dark-surface">
            {step === 'phone' && (
              <form
                onSubmit={
                  requestPhoneVerification
                }
                className="px-5 py-6 sm:px-6 sm:py-7"
              >
                <div className="mb-6">
                  <h2 className="text-lg font-semibold">
                    Add your phone number
                  </h2>

                  <p className="mt-1 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    We&apos;ll send a 6-digit
                    verification code to
                    confirm that the number
                    belongs to you.
                  </p>
                </div>

                {error && (
                  <div
                    role="alert"
                    className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-300"
                  >
                    {error}
                  </div>
                )}

                {successMessage && (
                  <div
                    role="status"
                    className="mb-5 rounded-xl border border-brand-teal/25 bg-brand-teal/10 px-4 py-3 text-sm leading-6 text-light-text dark:text-dark-text"
                  >
                    {successMessage}
                  </div>
                )}

                <div className="space-y-5">
                  <div>
                    <label
                      htmlFor="country-code"
                      className="mb-2 block text-sm font-medium"
                    >
                      Country
                    </label>

                    <select
                      id="country-code"
                      value={countryCode}
                      onChange={(event) =>
                        setCountryCode(
                          event.target.value,
                        )
                      }
                      disabled={submitting}
                      className="w-full rounded-xl border border-light-border bg-light-surface px-4 py-3 text-sm text-light-text outline-none transition focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:focus:border-brand-teal-light"
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

                  <div>
                    <label
                      htmlFor="phone-number"
                      className="mb-2 block text-sm font-medium"
                    >
                      Phone number
                    </label>

                    <div className="relative">
                      <PhoneIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-light-text-soft dark:text-dark-text-soft" />

                      <input
                        id="phone-number"
                        name="phone_number"
                        type="tel"
                        inputMode="tel"
                        autoComplete="tel"
                        value={phoneNumber}
                        onChange={(event) =>
                          setPhoneNumber(
                            event.target.value,
                          )
                        }
                        disabled={submitting}
                        placeholder="801 234 5678"
                        className="w-full rounded-xl border border-light-border bg-light-surface py-3 pl-11 pr-4 text-sm text-light-text outline-none transition focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:placeholder:text-dark-text-soft dark:focus:border-brand-teal-light"
                      />
                    </div>

                    <p className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                      Enter your number without
                      the country code. We&apos;ll
                      validate and normalize it
                      automatically.
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex items-start gap-3 rounded-xl border border-light-border-soft bg-light-surface-soft px-4 py-3.5 dark:border-dark-border-soft dark:bg-dark-surface-soft">
                  <ShieldCheckIcon className="mt-0.5 h-4 w-4 shrink-0 text-light-text-soft dark:text-dark-text-soft" />

                  <p className="text-xs leading-5 text-light-text-muted dark:text-dark-text-muted">
                    Your phone number will only
                    be added to your account after
                    the verification code is
                    confirmed.
                  </p>
                </div>

                <div className="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                  <Link
                    href="/settings/security"
                    className="inline-flex min-h-11 items-center justify-center rounded-xl border border-light-border px-5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-soft dark:border-dark-border dark:text-dark-text dark:hover:bg-dark-surface-soft"
                  >
                    Cancel
                  </Link>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="inline-flex min-h-11 items-center justify-center rounded-xl bg-brand-teal px-5 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submitting
                      ? 'Sending code...'
                      : 'Send verification code'}
                  </button>
                </div>
              </form>
            )}

            {step === 'verify' && (
              <form
                onSubmit={verifyPhone}
                className="px-5 py-6 sm:px-6 sm:py-7"
              >
                <div className="mb-6">
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light">
                    <ShieldCheckIcon className="h-5 w-5" />
                  </div>

                  <h2 className="text-lg font-semibold">
                    Verify your phone number
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                    We&apos;ve sent a 6-digit
                    code to{' '}
                    <span className="font-semibold text-light-text dark:text-dark-text">
                      {maskedPhone()}
                    </span>
                    .
                  </p>
                </div>

                {error && (
                  <div
                    role="alert"
                    className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-300"
                  >
                    {error}
                  </div>
                )}

                {successMessage && (
                  <div
                    role="status"
                    className="mb-5 rounded-xl border border-brand-teal/25 bg-brand-teal/10 px-4 py-3 text-sm leading-6 text-light-text dark:text-dark-text"
                  >
                    {successMessage}
                  </div>
                )}

                <div>
                  <label
                    htmlFor="verification-code"
                    className="mb-2 block text-sm font-medium"
                  >
                    Verification code
                  </label>

                  <input
                    id="verification-code"
                    name="code"
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={6}
                    value={code}
                    onChange={(event) =>
                      setCode(
                        event.target.value
                          .replace(/\D/g, '')
                          .slice(0, 6),
                      )
                    }
                    disabled={submitting}
                    placeholder="000000"
                    className="w-full rounded-xl border border-light-border bg-light-surface px-4 py-4 text-center text-2xl font-bold tracking-[0.35em] text-light-text outline-none transition focus:border-brand-teal focus:ring-2 focus:ring-brand-teal/15 disabled:cursor-not-allowed disabled:opacity-60 dark:border-dark-border dark:bg-dark-surface-soft dark:text-dark-text dark:focus:border-brand-teal-light"
                  />

                  <p className="mt-2 text-xs leading-5 text-light-text-soft dark:text-dark-text-soft">
                    The code expires after 10
                    minutes.
                  </p>
                </div>

                <div className="mt-6 flex items-center justify-between gap-4">
                  <button
                    type="button"
                    onClick={resendCode}
                    disabled={
                      submitting ||
                      secondsRemaining > 0
                    }
                    className="text-sm font-semibold text-brand-teal transition-colors hover:text-brand-teal-dark disabled:cursor-not-allowed disabled:opacity-50 dark:text-brand-teal-light dark:hover:text-brand-teal"
                  >
                    {secondsRemaining > 0
                      ? `Resend code in ${secondsRemaining}s`
                      : 'Resend code'}
                  </button>

                  <button
                    type="submit"
                    disabled={
                      submitting ||
                      code.length !== 6
                    }
                    className="inline-flex min-h-11 items-center justify-center rounded-xl bg-brand-teal px-5 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submitting
                      ? 'Verifying...'
                      : 'Verify phone'}
                  </button>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    clearMessages();
                    setCode('');
                    setStep('phone');
                  }}
                  disabled={submitting}
                  className="mt-6 text-sm font-medium text-light-text-muted transition-colors hover:text-light-text disabled:cursor-not-allowed disabled:opacity-50 dark:text-dark-text-muted dark:hover:text-dark-text"
                >
                  Use a different number
                </button>
              </form>
            )}

            {step === 'success' && (
              <div className="px-5 py-8 text-center sm:px-6 sm:py-10">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-teal/10 text-brand-teal dark:bg-brand-teal/15 dark:text-brand-teal-light">
                  <CheckCircleIcon className="h-7 w-7" />
                </div>

                <h2 className="mt-5 text-xl font-bold tracking-tight">
                  Phone number verified
                </h2>

                <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-light-text-muted dark:text-dark-text-muted">
                  {successMessage ||
                    'Your phone number has been added and verified successfully.'}
                </p>

                <div className="mt-6 rounded-xl border border-light-border-soft bg-light-surface-soft px-4 py-3 text-sm font-semibold text-light-text dark:border-dark-border-soft dark:bg-dark-surface-soft dark:text-dark-text">
                  {maskedPhone()}
                </div>

                <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:justify-center">
                  <Link
                    href="/settings/security"
                    className="inline-flex min-h-11 items-center justify-center rounded-xl bg-brand-teal px-5 text-sm font-semibold text-white transition-colors hover:bg-brand-teal-dark"
                  >
                    Back to Security
                  </Link>

                  <Link
                    href="/account"
                    className="inline-flex min-h-11 items-center justify-center rounded-xl border border-light-border px-5 text-sm font-semibold text-light-text transition-colors hover:bg-light-surface-soft dark:border-dark-border dark:text-dark-text dark:hover:bg-dark-surface-soft"
                  >
                    View my account
                  </Link>
                </div>
              </div>
            )}
          </section>
        </FadeIn>
      </div>
    </main>
  );
}