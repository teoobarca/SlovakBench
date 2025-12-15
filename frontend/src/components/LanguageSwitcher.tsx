'use client';

import { useLanguage } from '@/contexts/LanguageContext';

export function LanguageSwitcher() {
    const { language, setLanguage } = useLanguage();

    return (
        <div className="flex items-center gap-2 font-[var(--font-mono)] text-xs font-medium bg-[var(--color-ink)]/5 p-1 rounded-lg">
            <button
                onClick={() => setLanguage('en')}
                className={`px-2 py-1 rounded-md transition-all ${language === 'en'
                    ? 'bg-[var(--color-ink)] text-[var(--color-cream)] shadow-sm'
                    : 'text-[var(--color-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-ink)]/5'
                    }`}
                aria-label="Switch to English"
            >
                EN
            </button>
            <button
                onClick={() => setLanguage('sk')}
                className={`px-2 py-1 rounded-md transition-all ${language === 'sk'
                    ? 'bg-[var(--color-ink)] text-[var(--color-cream)] shadow-sm'
                    : 'text-[var(--color-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-ink)]/5'
                    }`}
                aria-label="Prepnúť do slovenčiny"
            >
                SK
            </button>
        </div>
    );
}
