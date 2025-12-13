interface StatsStripProps {
    modelCount: number;
}

export function StatsStrip({ modelCount }: StatsStripProps) {
    return (
        <section className="border-y border-[var(--color-ink)]/10 py-8 px-6 animate-fade-up delay-3">
            <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
                <div>
                    <p className="font-[var(--font-mono)] text-4xl font-semibold">{modelCount}</p>
                    <p className="text-[var(--color-muted)] text-sm mt-1">Models Evaluated</p>
                </div>
                <div>
                    <p className="font-[var(--font-mono)] text-4xl font-semibold">3</p>
                    <p className="text-[var(--color-muted)] text-sm mt-1">Task Categories</p>
                </div>
                <div>
                    <p className="font-[var(--font-mono)] text-4xl font-semibold">192</p>
                    <p className="text-[var(--color-muted)] text-sm mt-1">Total Questions</p>
                </div>
                <div>
                    <p className="font-[var(--font-mono)] text-4xl font-semibold">2025</p>
                    <p className="text-[var(--color-muted)] text-sm mt-1">Latest Year</p>
                </div>
            </div>
        </section>
    );
}
