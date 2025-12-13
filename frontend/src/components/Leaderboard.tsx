"use client";

import { useState, useMemo } from "react";
import Image from "next/image";
import type { LeaderboardData, TaskType, SortField, SortDirection, TaskDescription } from "@/types";

const TASK_DESCRIPTIONS: Record<TaskType, TaskDescription> = {
    exam: {
        icon: "📝",
        title: "Slovak Maturita Exam",
        description: "Official Slovak high school graduation exam (Maturita) in Slovak Language and Literature. Includes MCQ and short-text answers covering grammar, literature, and comprehension.",
        link: "https://www.nucem.sk/",
    },
    pos: {
        icon: "🏷️",
        title: "Part-of-Speech Tagging",
        description: "Part-of-speech tagging evaluation on Slovak National Corpus data. Tests morphological analysis capabilities.",
    },
    grammar: {
        icon: "✏️",
        title: "Grammar Correction",
        description: "Detecting and correcting grammatical and spelling errors in Slovak text.",
    },
};

// Provider logos - SVGs in public/logos/
const PROVIDER_LOGOS: Record<string, string> = {
    OpenAI: "/logos/openai.svg",
    Google: "/logos/google.svg",
    Anthropic: "/logos/anthropic.svg",
    Meta: "/logos/meta.svg",
    Mistral: "/logos/mistral.svg",
    DeepSeek: "/logos/deepseek.svg",
    Alibaba: "/logos/alibaba.svg",
    xAI: "/logos/xai.svg",
};

const YEARS = [2025, 2024, 2023];
const PROVIDERS = ["all", "OpenAI", "Google", "Anthropic"] as const;

interface LeaderboardProps {
    data: LeaderboardData;
}

export function Leaderboard({ data }: LeaderboardProps) {
    const [currentTask, setCurrentTask] = useState<TaskType>("exam");
    const [currentYear, setCurrentYear] = useState(2025);
    const [currentProvider, setCurrentProvider] = useState<string>("all");
    const [sort, setSort] = useState<{ field: SortField; direction: SortDirection }>({
        field: "overall",
        direction: "desc",
    });

    const filteredAndSorted = useMemo(() => {
        let items = data[currentTask]?.[currentYear] || [];

        if (currentProvider !== "all") {
            items = items.filter((item) => item.provider === currentProvider);
        }

        return [...items].sort((a, b) => {
            const aVal = a[sort.field] || 0;
            const bVal = b[sort.field] || 0;
            return sort.direction === "desc" ? bVal - aVal : aVal - bVal;
        });
    }, [data, currentTask, currentYear, currentProvider, sort]);

    const handleSort = (field: SortField) => {
        setSort((prev) => ({
            field,
            direction: prev.field === field && prev.direction === "desc" ? "asc" : "desc",
        }));
    };

    const taskDesc = TASK_DESCRIPTIONS[currentTask];

    return (
        <section id="leaderboard" className="py-20 px-6">
            <div className="max-w-6xl mx-auto">
                {/* Header with Task Tabs */}
                <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">RESULTS</p>
                        <h2 className="font-[var(--font-display)] text-5xl font-semibold">Leaderboard</h2>
                    </div>

                    <div className="flex gap-2 font-[var(--font-mono)] text-sm">
                        {(["exam", "pos", "grammar"] as TaskType[]).map((task) => (
                            <button
                                key={task}
                                onClick={() => setCurrentTask(task)}
                                className={`px-4 py-2 rounded-full border border-[var(--color-ink)]/20 transition-all ${currentTask === task
                                    ? "bg-[var(--color-ink)] text-[var(--color-cream)]"
                                    : "hover:bg-[var(--color-ink)]/5"
                                    }`}
                            >
                                {task === "exam" ? "Maturita Exam" : task === "pos" ? "POS Tagging" : "Grammar"}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Task Description */}
                <div className="bg-[var(--color-paper)] rounded-2xl p-6 mb-8 border border-[var(--color-ink)]/5">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-[var(--color-ink)] text-[var(--color-cream)] rounded-xl flex items-center justify-center font-[var(--font-mono)] text-lg">
                            {taskDesc.icon}
                        </div>
                        <div>
                            <h3 className="font-[var(--font-sans)] font-semibold text-lg mb-1">{taskDesc.title}</h3>
                            <p className="text-[var(--color-muted)] text-sm leading-relaxed">
                                {taskDesc.description}
                                {taskDesc.link && (
                                    <a
                                        href={taskDesc.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-[var(--color-accent)] hover:underline ml-1"
                                    >
                                        NÚCEM ↗
                                    </a>
                                )}
                                {!taskDesc.link && <span className="text-[var(--color-accent)] ml-1">(Coming soon)</span>}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Filters Row */}
                <div className="flex flex-wrap items-center gap-6 mb-6">
                    {/* Year Selector */}
                    <div className="flex items-center gap-3">
                        <span className="font-[var(--font-mono)] text-sm text-[var(--color-muted)]">Year:</span>
                        <div className="flex gap-2">
                            {YEARS.map((year) => (
                                <button
                                    key={year}
                                    onClick={() => setCurrentYear(year)}
                                    className={`px-3 py-1.5 rounded-lg font-[var(--font-mono)] text-sm transition-all ${currentYear === year
                                        ? "bg-[var(--color-ink)] text-[var(--color-cream)]"
                                        : "border border-[var(--color-ink)]/20 hover:bg-[var(--color-ink)]/5"
                                        }`}
                                >
                                    {year}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Provider Filter */}
                    <div className="flex items-center gap-3">
                        <span className="font-[var(--font-mono)] text-sm text-[var(--color-muted)]">Provider:</span>
                        <div className="flex gap-2">
                            {PROVIDERS.map((provider) => (
                                <button
                                    key={provider}
                                    onClick={() => setCurrentProvider(provider)}
                                    className={`px-3 py-1.5 rounded-lg font-[var(--font-mono)] text-sm border border-[var(--color-ink)]/20 transition-all flex items-center gap-1.5 ${currentProvider === provider
                                        ? "bg-[var(--color-ink)] text-[var(--color-cream)]"
                                        : "hover:bg-[var(--color-ink)]/5"
                                        }`}
                                >
                                    {provider !== "all" && PROVIDER_LOGOS[provider] && (
                                        <Image src={PROVIDER_LOGOS[provider]} alt={provider} width={14} height={14} className="opacity-70" />
                                    )}
                                    {provider === "all" ? "All" : provider}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Table */}
                <div className="bg-white rounded-2xl border border-[var(--color-ink)]/10 overflow-hidden shadow-sm">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-[var(--color-ink)]/10 text-left">
                                <th className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium w-20">
                                    Rank
                                </th>
                                <th className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium">
                                    Model
                                </th>
                                <th
                                    onClick={() => handleSort("overall")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                >
                                    Score{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "overall" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "overall" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                                <th
                                    onClick={() => handleSort("mcq")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] hidden md:table-cell"
                                >
                                    MCQ{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "mcq" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "mcq" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                                <th
                                    onClick={() => handleSort("short_text")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] hidden md:table-cell"
                                >
                                    Text{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "short_text" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "short_text" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                                <th
                                    onClick={() => handleSort("cost")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] hidden lg:table-cell"
                                >
                                    Cost{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "cost" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "cost" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredAndSorted.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-[var(--color-muted)]">
                                        <p className="text-lg mb-2">No data available</p>
                                        <p className="text-sm">This task/year combination hasn&apos;t been evaluated yet.</p>
                                    </td>
                                </tr>
                            ) : (
                                filteredAndSorted.map((item, i) => {
                                    const rank = i + 1;
                                    const logo = PROVIDER_LOGOS[item.provider];

                                    return (
                                        <tr key={item.model} className="border-b border-[var(--color-ink)]/5 last:border-0 hover:bg-[var(--color-paper)]/50 transition-colors">
                                            {/* Rank - bigger, bolder */}
                                            <td className="px-6 py-5">
                                                <span className={`font-[var(--font-mono)] text-2xl font-bold ${rank === 1 ? "text-yellow-500" : rank === 2 ? "text-gray-400" : rank === 3 ? "text-amber-600" : "text-[var(--color-muted)]"
                                                    }`}>
                                                    {rank}
                                                </span>
                                            </td>
                                            {/* Model with logo */}
                                            <td className="px-6 py-5">
                                                <div className="flex items-center gap-3">
                                                    {logo && (
                                                        <Image
                                                            src={logo}
                                                            alt={item.provider}
                                                            width={20}
                                                            height={20}
                                                            className="flex-shrink-0"
                                                        />
                                                    )}
                                                    <span className="font-[var(--font-mono)] text-base">{item.model}</span>
                                                </div>
                                            </td>
                                            {/* Score */}
                                            <td className="px-6 py-5 text-right">
                                                <span className="font-[var(--font-mono)] font-semibold text-lg">
                                                    {item.overall.toFixed(1)}
                                                </span>
                                            </td>
                                            <td className="px-6 py-5 text-right font-[var(--font-mono)] hidden md:table-cell text-[var(--color-muted)]">
                                                {item.mcq?.toFixed(1) || "-"}
                                            </td>
                                            <td className="px-6 py-5 text-right font-[var(--font-mono)] hidden md:table-cell text-[var(--color-muted)]">
                                                {item.short_text?.toFixed(1) || "-"}
                                            </td>
                                            <td className="px-6 py-5 text-right font-[var(--font-mono)] text-[var(--color-muted)] hidden lg:table-cell">
                                                ${item.cost?.toFixed(4) || "-"}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Updated legend with logos */}
                <div className="flex flex-wrap items-center gap-6 mt-4 text-sm text-[var(--color-muted)] font-[var(--font-mono)]">
                    <span>Providers:</span>
                    {Object.entries(PROVIDER_LOGOS).map(([provider, logo]) => (
                        <div key={provider} className="flex items-center gap-1.5">
                            <Image src={logo} alt={provider} width={14} height={14} />
                            {provider}
                        </div>
                    ))}
                    <span className="ml-auto">Last updated: December 2025</span>
                </div>
            </div>
        </section>
    );
}
