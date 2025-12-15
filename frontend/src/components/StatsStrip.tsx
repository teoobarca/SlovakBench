"use client";

import { useLanguage } from "@/contexts/LanguageContext";

interface StatsStripProps {
    modelCount: number;
}

export function StatsStrip({ modelCount }: StatsStripProps) {
    const { t } = useLanguage();

    return (
        <section className="border-y border-[var(--color-ink)]/10 bg-[var(--color-paper)]/50 backdrop-blur-sm animate-fade-up delay-3">
            <div className="max-w-6xl mx-auto">
                <div className="grid grid-cols-2 md:grid-cols-4">
                    <div className="p-6 md:py-8 border-b md:border-b-0 border-r border-[var(--color-ink)]/10">
                        <p className="font-[var(--font-mono)] text-3xl md:text-4xl font-semibold tracking-tight">{modelCount}</p>
                        <p className="text-[var(--color-muted)] text-xs font-[var(--font-mono)] uppercase tracking-wider mt-2">{t.stats.models_evaluated}</p>
                    </div>
                    <div className="p-6 md:py-8 border-b md:border-b-0 md:border-r border-[var(--color-ink)]/10">
                        <p className="font-[var(--font-mono)] text-3xl md:text-4xl font-semibold tracking-tight">3</p>
                        <p className="text-[var(--color-muted)] text-xs font-[var(--font-mono)] uppercase tracking-wider mt-2">{t.stats.task_categories}</p>
                    </div>
                    <div className="p-6 md:py-8 border-r border-[var(--color-ink)]/10">
                        <p className="font-[var(--font-mono)] text-3xl md:text-4xl font-semibold tracking-tight">192</p>
                        <p className="text-[var(--color-muted)] text-xs font-[var(--font-mono)] uppercase tracking-wider mt-2">{t.stats.total_questions}</p>
                    </div>
                    <div className="p-6 md:py-8">
                        <p className="font-[var(--font-mono)] text-3xl md:text-4xl font-semibold tracking-tight">2025</p>
                        <p className="text-[var(--color-muted)] text-xs font-[var(--font-mono)] uppercase tracking-wider mt-2">{t.stats.latest_year}</p>
                    </div>
                </div>
            </div>
        </section>
    );
}
