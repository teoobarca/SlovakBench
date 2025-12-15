"use client";

import { useLanguage } from "@/contexts/LanguageContext";

export function Footer() {
    const { t } = useLanguage();

    return (
        <footer className="py-16 px-6 border-t border-[var(--color-ink)]/10 bg-[var(--color-paper)]">
            <div className="max-w-6xl mx-auto">
                {/* Main footer content */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12">
                    {/* Brand */}
                    <div>
                        <p className="font-[var(--font-display)] text-2xl font-bold mb-3">
                            Slovak<span className="text-[var(--color-accent)]">Bench</span>
                        </p>
                        <p className="text-[var(--color-muted)] text-sm leading-relaxed">
                            {t.footer.desc}
                        </p>
                    </div>

                    {/* Links */}
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.2em] text-[var(--color-muted)] mb-4">
                            {t.footer.resources}
                        </p>
                        <div className="flex flex-col gap-2 font-[var(--font-mono)] text-sm">
                            <a
                                href="https://github.com/teoobarca/SlovakBench"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:text-[var(--color-accent)] transition-colors w-fit"
                            >
                                GitHub ↗
                            </a>
                            <a
                                href="https://www.nucem.sk/"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:text-[var(--color-accent)] transition-colors w-fit"
                            >
                                NÚCEM ↗
                            </a>
                        </div>
                    </div>

                    {/* Author */}
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.2em] text-[var(--color-muted)] mb-4">
                            {t.footer.author}
                        </p>
                        <p className="font-[var(--font-sans)] font-medium mb-2">Teodor Barča</p>
                        <div className="flex flex-col gap-1.5 font-[var(--font-mono)] text-sm">
                            <a
                                href="mailto:barca.teo@gmail.com"
                                className="text-[var(--color-muted)] hover:text-[var(--color-accent)] transition-colors w-fit"
                            >
                                barca.teo@gmail.com
                            </a>
                            <a
                                href="https://teodorbarca.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[var(--color-muted)] hover:text-[var(--color-accent)] transition-colors w-fit"
                            >
                                teodorbarca.com ↗
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="pt-8 border-t border-[var(--color-ink)]/10 flex flex-col md:flex-row items-center justify-between gap-4">
                    <p className="font-[var(--font-mono)] text-xs text-[var(--color-muted)]">
                        {t.footer.copyright}
                    </p>
                    <p className="font-[var(--font-mono)] text-xs text-[var(--color-muted)]">
                        {t.footer.source}
                    </p>
                </div>
            </div>
        </footer>
    );
}
