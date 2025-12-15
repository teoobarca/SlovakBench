"use client";

import Image from "next/image";

import { useLanguage } from "@/contexts/LanguageContext";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function Navbar() {
    const { t } = useLanguage();

    return (
        <nav className="fixed top-0 left-0 right-0 bg-[var(--color-cream)]/90 backdrop-blur-sm z-50 border-b border-[var(--color-ink)]/5">
            <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                <a href="#" className="flex items-center gap-2 font-[var(--font-display)] text-2xl font-semibold">
                    <Image src="/logo.png" alt="SlovakBench Logo" width={40} height={40} className="rounded-md" />
                    <span>Slovak<span className="text-[var(--color-accent)]">Bench</span></span>
                </a>
                <div className="flex items-center gap-6 text-sm font-[var(--font-mono)]">
                    <a href="#leaderboard" className="hover:text-[var(--color-accent)] transition-colors hidden md:block">
                        {t.nav.leaderboard}
                    </a>
                    <a href="#about" className="hover:text-[var(--color-accent)] transition-colors hidden md:block">
                        {t.nav.about}
                    </a>
                    <a
                        href="https://github.com/teoobarca/SlovakBench"
                        className="hover:text-[var(--color-accent)] transition-colors hidden md:block"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {t.nav.github} ↗
                    </a>
                    <LanguageSwitcher />
                </div>
            </div>
        </nav>
    );
}
