"use client";

import { useLanguage } from "@/contexts/LanguageContext";

export function About() {
    const { t } = useLanguage();

    return (
        <>
            {/* Story Section - full width, cream background matching hero */}
            <section className="py-16 px-6 bg-[var(--color-cream)]">
                <div className="max-w-4xl mx-auto text-center">
                    <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-3">{t.about.label_story}</p>
                    <h2 className="font-[var(--font-display)] text-4xl md:text-5xl font-semibold mb-8">{t.about.title_story}</h2>
                    <div className="space-y-4 text-lg text-[var(--color-muted)] leading-relaxed max-w-2xl mx-auto">
                        <p>{t.about.text_story_1}</p>
                        <p>{t.about.text_story_2}</p>
                    </div>
                </div>
            </section>

            {/* Tasks & Methodology Section - paper background for contrast */}
            <section id="about" className="py-16 px-6 bg-[var(--color-paper)]">
                <div className="max-w-6xl mx-auto">
                    <div className="grid md:grid-cols-2 gap-12 lg:gap-20">
                        {/* Tasks Column */}
                        <div>
                            <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">{t.about.label_tasks}</p>
                            <h2 className="font-[var(--font-display)] text-3xl font-semibold mb-6">{t.about.title_tasks}</h2>
                            <div className="space-y-5">
                                {/* Maturita - Active */}
                                <div className="flex gap-4 items-start p-4 rounded-xl bg-white/50 border border-[var(--color-ink)]/5">
                                    <span className="text-2xl">📝</span>
                                    <div>
                                        <h4 className="font-semibold mb-1">{t.about.task_exam.title}</h4>
                                        <p className="text-sm text-[var(--color-muted)]">
                                            {t.about.task_exam.desc}
                                        </p>
                                    </div>
                                </div>
                                {/* POS Tagging - Active */}
                                <div className="flex gap-4 items-start p-4 rounded-xl bg-white/50 border border-[var(--color-ink)]/5">
                                    <span className="text-2xl">🏷️</span>
                                    <div>
                                        <h4 className="font-semibold mb-1">{t.about.task_pos.title}</h4>
                                        <p className="text-sm text-[var(--color-muted)]">{t.about.task_pos.desc}</p>
                                    </div>
                                </div>
                                {/* Grammar - Coming Soon */}
                                <div className="flex gap-4 items-start p-4 rounded-xl bg-white/30 border border-[var(--color-ink)]/5 opacity-60">
                                    <span className="text-2xl">✏️</span>
                                    <div>
                                        <h4 className="font-semibold mb-1">
                                            {t.about.task_grammar.title}{" "}
                                            <span className="text-xs font-[var(--font-mono)] text-[var(--color-accent)]">{t.about.coming_soon}</span>
                                        </h4>
                                        <p className="text-sm text-[var(--color-muted)]">{t.about.task_grammar.desc}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Methodology Column */}
                        <div>
                            <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">{t.about.label_about}</p>
                            <h2 className="font-[var(--font-display)] text-3xl font-semibold mb-6">{t.about.title_why}</h2>
                            <div className="space-y-4 text-[var(--color-muted)] leading-relaxed">
                                <p>{t.about.text_why_1}</p>
                                <p>{t.about.text_why_2}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}
