export function Footer() {
    return (
        <footer className="py-12 px-6 border-t border-[var(--color-ink)]/10">
            <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                <p className="font-[var(--font-display)] text-xl font-semibold">SlovakBench</p>
                <p className="font-[var(--font-mono)] text-sm text-[var(--color-muted)]">
                    Open source benchmark for Slovak LLM evaluation
                </p>
                <div className="flex gap-4 font-[var(--font-mono)] text-sm">
                    <a href="https://github.com/teoobarca/SlovakBench" className="hover:text-[var(--color-accent)] transition-colors">
                        GitHub
                    </a>
                    <a href="https://www.nucem.sk/" className="hover:text-[var(--color-accent)] transition-colors">
                        NÚCEM
                    </a>
                </div>
            </div>
        </footer>
    );
}
