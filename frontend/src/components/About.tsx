export function About() {
    return (
        <section id="about" className="py-20 px-6 bg-[var(--color-paper)]">
            <div className="max-w-6xl mx-auto">
                <div className="grid md:grid-cols-2 gap-16">
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">ABOUT</p>
                        <h2 className="font-[var(--font-display)] text-4xl font-semibold mb-6">Why SlovakBench?</h2>
                        <div className="space-y-4 text-[var(--color-muted)] leading-relaxed">
                            <p>
                                Most LLM benchmarks focus on English, leaving low-resource languages underrepresented. SlovakBench
                                provides rigorous evaluation for Slovak language capabilities.
                            </p>
                            <p>
                                We use real-world tasks: official Maturita exams from NÚCEM, part-of-speech tagging from linguistic
                                corpora, and grammar correction from native texts.
                            </p>
                        </div>
                    </div>
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">TASKS</p>
                        <h2 className="font-[var(--font-display)] text-4xl font-semibold mb-6">Benchmark Tasks</h2>
                        <div className="space-y-4">
                            <div className="flex gap-4 items-start">
                                <span className="text-2xl">📝</span>
                                <div>
                                    <h4 className="font-semibold">Maturita Exam</h4>
                                    <p className="text-sm text-[var(--color-muted)]">
                                        Slovak high school graduation exam with MCQ and open-ended questions.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-4 items-start opacity-50">
                                <span className="text-2xl">🏷️</span>
                                <div>
                                    <h4 className="font-semibold">
                                        POS Tagging <span className="text-xs font-[var(--font-mono)] text-[var(--color-accent)]">(coming soon)</span>
                                    </h4>
                                    <p className="text-sm text-[var(--color-muted)]">Part-of-speech tagging on Slovak National Corpus data.</p>
                                </div>
                            </div>
                            <div className="flex gap-4 items-start opacity-50">
                                <span className="text-2xl">✏️</span>
                                <div>
                                    <h4 className="font-semibold">
                                        Grammar Correction{" "}
                                        <span className="text-xs font-[var(--font-mono)] text-[var(--color-accent)]">(coming soon)</span>
                                    </h4>
                                    <p className="text-sm text-[var(--color-muted)]">Detecting and correcting grammatical errors in Slovak text.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
