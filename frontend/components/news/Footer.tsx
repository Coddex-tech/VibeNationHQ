'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { 
  FaFacebookF, 
  FaXTwitter, 
  FaInstagram, 
  FaWhatsapp, 
  FaTelegram, 
  FaArrowUp 
} from 'react-icons/fa6';

export default function Footer() {
  const [showTopBtn, setShowTopBtn] = useState(false);

  // Monitor scroll position to toggle the Back-To-Top button visibility
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 300) {
        setShowTopBtn(true);
      } else {
        setShowTopBtn(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  const footerLinks = [
    { name: 'About Us', href: '/about' },
    { name: 'Advertise With Us', href: '/advertise' },
    { name: 'Contact Us', href: '/contact' },
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Service', href: '/services' },
    { name: 'DMCA', href: '/dmca' },
  ];

  // Added brandHover classes for individual brand identity on hover
  const socialLinks = [
    { 
      icon: <FaFacebookF />, 
      href: 'https://facebook.com', 
      label: 'Facebook',
      brandHover: 'hover:bg-[#1877F2] hover:border-[#1877F2]' 
    },
    { 
      icon: <FaXTwitter />, 
      href: 'https://x.com', 
      label: 'X',
      brandHover: 'hover:bg-[#0f1419] hover:border-[#ffffff]' 
    },
    { 
      icon: <FaInstagram />, 
      href: 'https://instagram.com', 
      label: 'Instagram',
      brandHover: 'hover:bg-gradient-to-tr hover:from-[#f09433] hover:via-[#dc2743] hover:to-[#bc1888] hover:border-[#dc2743]' 
    },
    { 
      icon: <FaWhatsapp />, 
      href: 'https://whatsapp.com', 
      label: 'WhatsApp',
      brandHover: 'hover:bg-[#25D366] hover:border-[#25D366]' 
    },
    { 
      icon: <FaTelegram />, 
      href: 'https://telegram.org', 
      label: 'Telegram',
      brandHover: 'hover:bg-[#229ED9] hover:border-[#229ED9]' 
    },
  ];

  return (
    <footer className="w-full bg-[#032b2b] text-white pt-8 pb-10 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col space-y-6">
          
          {/* 1. LOGO */}
          <div className="flex-shrink-0">
            <Link href="/" className="inline-block">
              <Image
                src="/vibenation_nav_logo.png"
                alt="VibeNation HQ"
                width={180}
                height={50}
                className="h-10 w-auto object-contain"
              />
            </Link>
          </div>

          {/* 2. FOOTER NAVIGATION LINKS */}
          <nav className="flex flex-wrap gap-x-6 gap-y-2">
            {footerLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                className="text-base font-bold text-white hover:text-[#00a884] transition-colors duration-200"
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* 3. SOCIAL MEDIA CIRCULAR BUTTONS */}
          <div className="flex items-center space-x-3 pt-2">
            {socialLinks.map((social, index) => (
              <a
                key={index}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={social.label}
                className={`w-10 h-10 rounded-full border border-gray-600 bg-[#063a3a] flex items-center justify-center text-white transition-all duration-300 transform hover:-translate-y-1 ${social.brandHover}`}
              >
                {social.icon}
              </a>
            ))}
          </div>

          {/* 4. COPYRIGHT NOTICE */}
          <div className="pt-2 text-sm text-gray-300">
            © {new Date().getFullYear()} VibeNation. All rights reserved.
          </div>

        </div>
      </div>

      {/* 5. STICKY / FLOATING BACK TO TOP BUTTON */}
      <button
        onClick={scrollToTop}
        className={`fixed right-6 bottom-8 z-50 w-12 h-12 rounded-full bg-[#008080] hover:bg-[#00a884] text-white flex flex-col items-center justify-center text-xs font-bold shadow-2xl transition-all duration-300 hover:scale-110 ${
          showTopBtn ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-10 pointer-events-none'
        }`}
        aria-label="Back to Top"
      >
        <FaArrowUp className="text-sm mb-0.5" />
        <span>Top</span>
      </button>
    </footer>
  );
}