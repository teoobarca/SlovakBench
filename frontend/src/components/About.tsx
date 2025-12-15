"use client";

import { useLanguage } from "@/contexts/LanguageContext";

export function About() {
    const { t } = useLanguage();

    return (
        <section id="about" className="py-20 px-6 bg-[var(--color-paper)]">
            <div className="max-w-6xl mx-auto">
                {/* Story Section */}
                <div className="mb-16 max-w-3xl">
                    <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">{t.about.label_story}</p>
                    <h2 className="font-[var(--font-display)] text-4xl font-semibold mb-6">{t.about.title_story}</h2>
                    <div className="space-y-4 text-[var(--color-muted)] leading-relaxed">
                        <p>{t.about.text_story_1}</p>
                        <p>{t.about.text_story_2}</p>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-16">
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">{t.about.label_about}</p>
                        <h2 className="font-[var(--font-display)] text-4xl font-semibold mb-6">{t.about.title_why}</h2>
                        <div className="space-y-4 text-[var(--color-muted)] leading-relaxed">
                            <p>
                                {t.about.text_why_1}
                            </p>
                            <p>
                                {t.about.text_why_2}
                            </p>
                        </div>
                    </div>
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">{t.about.label_tasks}</p>
                        <h2 className="font-[var(--font-display)] text-4xl font-semibold mb-6">{t.about.title_tasks}</h2>
                        <div className="space-y-4">
                            {/* Maturita - Active */}
                            <div className="flex gap-4 items-start">
                                <span className="text-2xl">📝</span>
                                <div>
                                    <h4 className="font-semibold">{t.about.task_exam.title}</h4>
                                    <p className="text-sm text-[var(--color-muted)]">
                                        {t.about.task_exam.desc}
                                    </p>
                                </div>
                            </div>
                            {/* POS Tagging - Active (no longer coming soon) */}
                            <div className="flex gap-4 items-start">
                                <span className="text-2xl">🏷️</span>
                                <div>
                                    <h4 className="font-semibold">
                                        {t.about.task_pos.title}
                                    </h4>
                                    <p className="text-sm text-[var(--color-muted)]">{t.about.task_pos.desc}</p>
                                </div>
                            </div>
                            {/* Grammar - Coming Soon */}
                            <div className="flex gap-4 items-start opacity-50">
                                <span className="text-2xl">✏️</span>
                                <div>
                                    <h4 className="font-semibold">
                                        {t.about.task_grammar.title}{" "}
                                        <span className="text-xs font-[var(--font-mono)] text-[var(--color-accent)]">{t.about.coming_soon}</span>
                                    </h4>
                                    <p className="text-sm text-[var(--color-muted)]">{t.about.task_grammar.desc}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
