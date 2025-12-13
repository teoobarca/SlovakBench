"use client";

import { useState, useMemo } from "react";
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

const PROVIDER_COLORS: Record<string, string> = {
    OpenAI: "bg-[var(--color-openai)]",
    Google: "bg-[var(--color-google)]",
    Anthropic: "bg-[var(--color-anthropic)]",
    Meta: "bg-[var(--color-meta)]",
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
                                    {provider !== "all" && <span className={`w-2 h-2 rounded-full ${PROVIDER_COLORS[provider]}`} />}
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
                                <th className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium">
                                    #
                                </th>
                                <th className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium">
                                    MODEL
                                </th>
                                <th
                                    onClick={() => handleSort("overall")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] tooltip"
                                    data-tooltip="Weighted average of MCQ and Short Text scores"
                                >
                                    OVERALL{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "overall" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "overall" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                                <th
                                    onClick={() => handleSort("mcq")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] hidden md:table-cell tooltip"
                                    data-tooltip="Multiple Choice Questions accuracy (40 questions)"
                                >
                                    MCQ{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "mcq" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "mcq" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                                <th
                                    onClick={() => handleSort("short_text")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] hidden md:table-cell tooltip"
                                    data-tooltip="Short answer questions accuracy (24 questions)"
                                >
                                    SHORT TEXT{" "}
                                    <span className={`text-[10px] ml-1 ${sort.field === "short_text" ? "opacity-100" : "opacity-50"}`}>
                                        {sort.field === "short_text" && sort.direction === "asc" ? "▲" : "▼"}
                                    </span>
                                </th>
                                <th
                                    onClick={() => handleSort("cost")}
                                    className="px-6 py-4 font-[var(--font-mono)] text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)] hidden lg:table-cell tooltip"
                                    data-tooltip="Estimated cost per full evaluation run"
                                >
                                    COST{" "}
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
                                    const medal = rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : null;
                                    const providerColor = PROVIDER_COLORS[item.provider] || "bg-[var(--color-muted)]";

                                    return (
                                        <tr key={item.model} className="border-b border-[var(--color-ink)]/5 last:border-0 transition-colors">
                                            <td
                                                className={`px-6 py-5 font-[var(--font-mono)] font-semibold ${rank === 1 ? "rank-1" : rank === 2 ? "rank-2" : rank === 3 ? "rank-3" : ""
                                                    }`}
                                            >
                                                {medal || rank}
                                            </td>
                                            <td className="px-6 py-5">
                                                <div className="flex items-center gap-3">
                                                    <div>
                                                        <div className="font-[var(--font-sans)] font-semibold text-base">{item.model}</div>
                                                        <div className="flex items-center gap-1.5 mt-1">
                                                            <span className={`w-2 h-2 rounded-full ${providerColor}`} />
                                                            <span className="text-sm text-[var(--color-muted)]">{item.provider}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-5 text-right">
                                                <div className="flex flex-col items-end gap-1">
                                                    <span className="font-[var(--font-mono)] font-semibold text-lg">{item.overall.toFixed(1)}%</span>
                                                    <div className="score-bar w-16">
                                                        <div className="score-bar-fill" style={{ width: `${item.overall}%` }} />
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-5 text-right font-[var(--font-mono)] hidden md:table-cell">
                                                {item.mcq?.toFixed(1) || "-"}%
                                            </td>
                                            <td className="px-6 py-5 text-right font-[var(--font-mono)] hidden md:table-cell">
                                                {item.short_text?.toFixed(1) || "-"}%
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

                {/* Table legend */}
                <div className="flex flex-wrap items-center gap-6 mt-4 text-sm text-[var(--color-muted)] font-[var(--font-mono)]">
                    <span>Providers:</span>
                    <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-openai)]" />
                        OpenAI
                    </div>
                    <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-google)]" />
                        Google
                    </div>
                    <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-anthropic)]" />
                        Anthropic
                    </div>
                    <span className="ml-auto">Last updated: December 2025</span>
                </div>
            </div>
        </section>
    );
}
