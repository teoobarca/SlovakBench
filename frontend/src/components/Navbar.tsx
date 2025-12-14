export function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 bg-[var(--color-cream)]/90 backdrop-blur-sm z-50 border-b border-[var(--color-ink)]/5">
            <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                <a href="#" className="font-[var(--font-display)] text-2xl font-semibold">
                    SlovakBench
                </a>
                <div className="flex items-center gap-6 text-sm font-[var(--font-mono)]">
                    <a href="#leaderboard" className="hover:text-[var(--color-accent)] transition-colors">
                        Leaderboard
                    </a>
                    <a href="#about" className="hover:text-[var(--color-accent)] transition-colors">
                        About
                    </a>
                    <a
                        href="https://github.com/teoobarca/SlovakBench"
                        className="hover:text-[var(--color-accent)] transition-colors"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        GitHub ↗
                    </a>
                </div>
            </div>
        </nav>
    );
}
