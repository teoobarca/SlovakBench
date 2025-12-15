'use client';

import { useLanguage } from '@/contexts/LanguageContext';

export function LanguageSwitcher() {
    const { language, setLanguage } = useLanguage();

    const toggle = () => {
        setLanguage(language === 'sk' ? 'en' : 'sk');
    };

    return (
        <button
            onClick={toggle}
            className="flex items-center gap-1.5 font-[var(--font-mono)] text-xs font-medium bg-[var(--color-ink)]/5 rounded-full p-0.5 cursor-pointer transition-all hover:bg-[var(--color-ink)]/10"
            aria-label={language === 'sk' ? 'Switch to English' : 'Prepnúť do slovenčiny'}
        >
            {/* SK label */}
            <span className={`px-2 py-1 rounded-full transition-all ${language === 'sk'
                    ? 'bg-[var(--color-ink)] text-[var(--color-cream)]'
                    : 'text-[var(--color-muted)]'
                }`}>
                SK
            </span>
            {/* EN label */}
            <span className={`px-2 py-1 rounded-full transition-all ${language === 'en'
                    ? 'bg-[var(--color-ink)] text-[var(--color-cream)]'
                    : 'text-[var(--color-muted)]'
                }`}>
                EN
            </span>
        </button>
    );
}
