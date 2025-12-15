"use client";

import { useLanguage } from "@/contexts/LanguageContext";

export function Hero() {
    const { t } = useLanguage();

    return (
        <header className="pt-32 pb-20 px-6">
            <div className="max-w-6xl mx-auto">
                <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-4 animate-fade-up">
                    {t.hero.label}
                </p>
                <h1 className="font-[var(--font-display)] text-7xl md:text-8xl lg:text-9xl leading-[0.9] mb-8 animate-fade-up delay-1 font-bold">
                    {t.hero.title_start}<span className="text-[var(--color-accent)]">{t.hero.title_end}</span>
                </h1>
                <p className="font-[var(--font-sans)] text-xl md:text-2xl text-[var(--color-muted)] max-w-2xl leading-relaxed animate-fade-up delay-2">
                    {t.hero.description}
                </p>
            </div>
        </header>
    );
}
