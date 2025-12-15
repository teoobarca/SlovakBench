"use client";

import { useState, useMemo, useEffect } from "react";
import Image from "next/image";
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    LabelList,
} from "recharts";
import type { LeaderboardData, TaskType, SortField, SortDirection, ModelResult } from "@/types";
import { useLanguage } from "@/contexts/LanguageContext";
import { TooltipHeader } from "./Tooltip";

// Provider logos and colors
const PROVIDER_LOGOS: Record<string, string> = {
    OpenAI: "/logos/openai.svg",
    Google: "/logos/google.svg",
    Anthropic: "/logos/anthropic.svg",
    Meta: "/logos/meta.svg",
    Mistral: "/logos/mistral.svg",
    DeepSeek: "/logos/deepseek.svg",
    Alibaba: "/logos/alibaba.svg",
    xAI: "/logos/xai.svg",
    Kimi: "/logos/kimi.svg",
    Qwen: "/logos/qwen.svg",
    Cohere: "/logos/cohere.svg",
    Databricks: "/logos/databricks.svg",
    TII: "/logos/tii.svg",
    Minimax: "/logos/minimax.svg",
    Microsoft: "/logos/microsoft.svg",
    AI21: "/logos/ai21.webp",
    zAI: "/logos/z-ai.svg",
};

const PROVIDER_COLORS: Record<string, string> = {
    OpenAI: "#10a37f",
    Google: "#4285f4",
    Anthropic: "#d97706",
    Meta: "#0668E1",
    Mistral: "#ff7000",
    DeepSeek: "#4f46e5",
    Alibaba: "#ff6a00",
    xAI: "#000000",
    Kimi: "#027AFF",
    Qwen: "#6366F1",
    Cohere: "#39594D",
    Databricks: "#FE321D",
    TII: "#6400FF",
    Minimax: "#FF6B35",
    Microsoft: "#00A4EF",
    AI21: "#000000",
    zAI: "#1d1d1f",
};



type ViewMode = "table" | "scatter";

interface LeaderboardProps {
    data: LeaderboardData;
}

export function Leaderboard({ data }: LeaderboardProps) {
    const { t } = useLanguage();
    const [currentTask, setCurrentTask] = useState<TaskType>("exam");
    // Sort years descending
    const availableYears = useMemo(() => {
        const years = Object.keys(data[currentTask] || {});
        return years.map(Number).sort((a, b) => b - a);
    }, [data, currentTask]);

    const [currentYear, setCurrentYear] = useState<number>(availableYears[0] || 2025);

    // Update year when task changes if current year not available
    useEffect(() => {
        const years = Object.keys(data[currentTask] || {}).map(Number).sort((a, b) => b - a);
        if (years.length > 0 && !years.includes(currentYear)) {
            setCurrentYear(years[0]);
        }
    }, [currentTask, data, currentYear]);

    const [currentProvider, setCurrentProvider] = useState<string>("all");
    const [viewMode, setViewMode] = useState<ViewMode>("table");
    const [sort, setSort] = useState<{ field: SortField | "pos_accuracy" | "lemma_accuracy" | "dep_accuracy"; direction: SortDirection }>({
        field: "overall",
        direction: "desc",
    });
    const [highlightedProviders, setHighlightedProviders] = useState<Set<string>>(new Set());
    const [hoveredProvider, setHoveredProvider] = useState<string | null>(null);
    const [isProvidersExpanded, setIsProvidersExpanded] = useState(false);

    const derivedProviders = useMemo(() => {
        const items = data[currentTask]?.[currentYear] || [];
        const uniqueProviders = Array.from(new Set(items.map(item => item.provider || "Unknown")));
        const prioritize = ["OpenAI", "Google", "Anthropic"];
        return ["all", ...uniqueProviders.sort((a, b) => {
            const idxA = prioritize.indexOf(a);
            const idxB = prioritize.indexOf(b);
            if (idxA !== -1 && idxB !== -1) return idxA - idxB;
            if (idxA !== -1) return -1;
            if (idxB !== -1) return 1;
            return a.localeCompare(b);
        })];
    }, [data, currentTask, currentYear]);

    const visibleProviders = useMemo(() => {
        const defaultVisible = derivedProviders.slice(0, 4);
        if (currentProvider !== "all" && !defaultVisible.includes(currentProvider)) {
            return [...defaultVisible, currentProvider];
        }
        return defaultVisible;
    }, [derivedProviders, currentProvider]);

    const hiddenProviders = useMemo(() => {
        return derivedProviders.filter(p => !visibleProviders.includes(p));
    }, [derivedProviders, visibleProviders]);

    const filteredAndSorted = useMemo(() => {
        let items = data[currentTask]?.[currentYear] || [];

        if (currentProvider !== "all") {
            items = items.filter((item) => item.provider === currentProvider);
        }

        return [...items].sort((a, b) => {
            // @ts-ignore - dynamic sort field
            const aVal = a[sort.field] || 0;
            // @ts-ignore
            const bVal = b[sort.field] || 0;
            return sort.direction === "desc" ? bVal - aVal : aVal - bVal;
        });
    }, [data, currentTask, currentYear, currentProvider, sort]);

    const handleSort = (field: SortField | "pos_accuracy" | "lemma_accuracy" | "dep_accuracy") => {
        setSort((prev) => ({
            field,
            direction: prev.field === field && prev.direction === "desc" ? "asc" : "desc",
        }));
    };

    const toggleProviderHighlight = (provider: string) => {
        setHighlightedProviders((prev) => {
            const next = new Set(prev);
            if (next.has(provider)) {
                next.delete(provider);
            } else {
                next.add(provider);
            }
            return next;
        });
    };

    const isProviderActive = (provider: string) => {
        if (highlightedProviders.size > 0) {
            return highlightedProviders.has(provider) || (hoveredProvider === provider);
        }
        if (hoveredProvider) {
            return provider === hoveredProvider;
        }
        return true;
    };

    const taskIcons: Record<TaskType, string> = {
        exam: "📝",
        pos: "🏷️",
        grammar: "✏️"
    };

    const taskDesc = {
        ...t.leaderboard.descriptions[currentTask],
        icon: taskIcons[currentTask],
        link: currentTask === "exam" ? "https://www.nucem.sk/" : undefined
    };

    // Prepare scatter data with smart label visibility
    const scatterData = useMemo(() => {
        const baseData = filteredAndSorted.map((item) => ({
            ...item,
            x: item.cost || 0,
            y: item.overall,
            color: PROVIDER_COLORS[item.provider] || "#6b7280",
        }));

        // Calculate which labels to show based on proximity
        // Sort by score (y) descending so higher-scoring models get priority for labels
        const sortedByScore = [...baseData].sort((a, b) => b.y - a.y);
        const labeledPoints: { x: number; y: number }[] = [];

        // Threshold for "too close" - in data units
        // These values are tuned based on typical chart dimensions
        const xThreshold = (Math.max(...baseData.map(d => d.x)) - Math.min(...baseData.map(d => d.x))) * 0.08 || 0.05;
        const yThreshold = 5; // 5% score difference

        const showLabelMap = new Map<string, boolean>();

        for (const point of sortedByScore) {
            const tooClose = labeledPoints.some(labeled =>
                Math.abs(point.x - labeled.x) < xThreshold &&
                Math.abs(point.y - labeled.y) < yThreshold
            );

            if (!tooClose) {
                showLabelMap.set(point.model, true);
                labeledPoints.push({ x: point.x, y: point.y });
            } else {
                showLabelMap.set(point.model, false);
            }
        }

        return baseData.map(item => ({
            ...item,
            showLabel: showLabelMap.get(item.model) ?? true,
        }));
    }, [filteredAndSorted]);

    return (
        <section id="leaderboard" className="py-12 md:py-20 px-4 md:px-6">
            <div className="max-w-6xl mx-auto">
                {/* Header with Task Tabs */}
                <div className="flex flex-col gap-4 md:gap-6 md:flex-row md:items-end justify-between mb-8 md:mb-12">
                    <div>
                        <p className="font-[var(--font-mono)] text-xs tracking-[0.3em] text-[var(--color-muted)] mb-2">{t.leaderboard.label}</p>
                        <h2 className="font-[var(--font-display)] text-3xl md:text-5xl font-semibold">{t.leaderboard.title}</h2>
                    </div>

                    <div className="flex gap-2 font-[var(--font-mono)] text-xs md:text-sm overflow-x-auto pb-2 md:pb-0">
                        {(["exam", "pos", "grammar"] as TaskType[]).map((task) => (
                            <button
                                key={task}
                                onClick={() => setCurrentTask(task)}
                                className={`px-3 md:px-4 py-2 rounded-full border border-[var(--color-ink)]/20 transition-all cursor-pointer whitespace-nowrap ${currentTask === task
                                    ? "bg-[var(--color-ink)] text-[var(--color-cream)]"
                                    : "hover:bg-[var(--color-ink)]/5"
                                    }`}
                            >
                                {task === "exam" ? t.leaderboard.tasks.exam : task === "pos" ? t.leaderboard.tasks.pos : t.leaderboard.tasks.grammar}
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
                                {taskDesc.desc}
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
                                {!taskDesc.link && currentTask === "grammar" && <span className="text-[var(--color-accent)] ml-1">{t.about.coming_soon}</span>}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Filters Row */}
                <div className="flex flex-wrap items-center gap-4 md:gap-6 mb-6">
                    {/* Year Selector - Only for Exam task */}
                    {currentTask !== "pos" && (
                        <div className="flex items-center gap-2 md:gap-3">
                            <span className="font-[var(--font-mono)] text-xs md:text-sm text-[var(--color-muted)]">{t.leaderboard.filters.year}:</span>
                            <div className="flex gap-1 md:gap-2">
                                {availableYears.length > 0 ? availableYears.map((year) => (
                                    <button
                                        key={year}
                                        onClick={() => setCurrentYear(year)}
                                        className={`px-2 md:px-3 py-1 md:py-1.5 rounded-lg font-[var(--font-mono)] text-xs md:text-sm transition-all cursor-pointer ${currentYear === year
                                            ? "bg-[var(--color-ink)] text-[var(--color-cream)]"
                                            : "border border-[var(--color-ink)]/20 hover:bg-[var(--color-ink)]/5"
                                            }`}
                                    >
                                        {year}
                                    </button>
                                )) : (
                                    <span className="text-sm text-[var(--color-muted)] italic">No data</span>
                                )}
                            </div>
                        </div>
                    )}

                    {/* View Toggle - moved here for mobile */}
                    <div className="flex items-center gap-1 ml-auto md:hidden">
                        <div className="flex gap-1 bg-[var(--color-paper)] rounded-lg p-0.5 border border-[var(--color-ink)]/10">
                            <button
                                onClick={() => setViewMode("table")}
                                className={`px-2 py-1 rounded-md font-[var(--font-mono)] text-xs transition-all cursor-pointer ${viewMode === "table" ? "bg-white shadow-sm" : "hover:bg-white/50"}`}
                            >
                                ☰
                            </button>
                            <button
                                onClick={() => setViewMode("scatter")}
                                className={`px-2 py-1 rounded-md font-[var(--font-mono)] text-xs transition-all cursor-pointer ${viewMode === "scatter" ? "bg-white shadow-sm" : "hover:bg-white/50"}`}
                            >
                                ⬡
                            </button>
                        </div>
                    </div>

                    {/* Provider Filter */}
                    <div className="flex items-start gap-3">
                        <span className="font-[var(--font-mono)] text-sm text-[var(--color-muted)] mt-2">{t.leaderboard.filters.provider}:</span>
                        <div className="flex gap-2 flex-wrap max-w-2xl relative transition-all">

                            {visibleProviders.map((provider) => (
                                <button
                                    key={provider}
                                    onClick={() => setCurrentProvider(provider)}
                                    className={`px-3 py-1.5 rounded-lg font-[var(--font-mono)] text-sm border border-[var(--color-ink)]/20 transition-all flex items-center gap-1.5 cursor-pointer ${currentProvider === provider
                                        ? "bg-[var(--color-ink)] text-[var(--color-cream)]"
                                        : "hover:bg-[var(--color-ink)]/5"
                                        }`}
                                >
                                    {provider !== "all" && PROVIDER_LOGOS[provider] && (
                                        <Image src={PROVIDER_LOGOS[provider]} alt={provider} width={14} height={14} className="opacity-70" />
                                    )}
                                    {provider === "all" ? t.leaderboard.filters.all_providers : provider}
                                </button>
                            ))}

                            {hiddenProviders.length > 0 && (
                                <div className="relative">
                                    <button
                                        onClick={() => setIsProvidersExpanded(!isProvidersExpanded)}
                                        className={`px-3 py-2 rounded-lg font-[var(--font-mono)] text-xs border border-[var(--color-ink)]/10 text-[var(--color-muted)] hover:bg-[var(--color-ink)]/5 cursor-pointer transition-colors flex items-center gap-1 ${isProvidersExpanded ? 'bg-[var(--color-ink)]/5' : 'bg-[var(--color-paper)]'}`}
                                    >
                                        +{hiddenProviders.length}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="12"
                                            height="12"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            className={`transition-transform duration-200 ${isProvidersExpanded ? 'rotate-180' : ''}`}
                                        >
                                            <path d="m6 9 6 6 6-6" />
                                        </svg>
                                    </button>

                                    {isProvidersExpanded && (
                                        <div className="absolute top-full left-0 mt-2 bg-[var(--color-paper)] border border-[var(--color-ink)]/10 rounded-lg shadow-lg p-2 z-50 flex flex-col gap-1 min-w-[140px]">
                                            {hiddenProviders.map((provider) => (
                                                <button
                                                    key={provider}
                                                    onClick={() => {
                                                        setCurrentProvider(provider);
                                                        setIsProvidersExpanded(false);
                                                    }}
                                                    className="w-full text-left px-3 py-2 rounded-md hover:bg-[var(--color-ink)]/5 font-[var(--font-mono)] text-sm flex items-center gap-2"
                                                >
                                                    {PROVIDER_LOGOS[provider] && (
                                                        <Image src={PROVIDER_LOGOS[provider]} alt={provider} width={14} height={14} className="opacity-70" />
                                                    )}
                                                    {provider}
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* View Toggle - desktop only (mobile version is in filters row) */}
                    <div className="hidden md:flex items-center gap-3 ml-auto">
                        <div className="flex gap-1 bg-[var(--color-paper)] rounded-lg p-1 border border-[var(--color-ink)]/10">
                            <button
                                onClick={() => setViewMode("table")}
                                className={`px-3 py-1.5 rounded-md font-[var(--font-mono)] text-sm transition-all cursor-pointer flex items-center gap-1.5 ${viewMode === "table" ? "bg-white shadow-sm" : "hover:bg-white/50"
                                    }`}
                            >
                                <span>☰</span> {t.leaderboard.table.view_table || "Table"}
                            </button>
                            <button
                                onClick={() => setViewMode("scatter")}
                                className={`px-3 py-1.5 rounded-md font-[var(--font-mono)] text-sm transition-all cursor-pointer flex items-center gap-1.5 ${viewMode === "scatter" ? "bg-white shadow-sm" : "hover:bg-white/50"
                                    }`}
                            >
                                <span>⬡</span> {t.leaderboard.table.view_scatter || "Scatter"}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Table View */}
                {viewMode === "table" && (
                    <div className="bg-white rounded-2xl border border-[var(--color-ink)]/10 overflow-hidden shadow-sm">
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[640px]">
                                <thead>
                                    <tr className="border-b-2 border-[var(--color-ink)]/10 text-left bg-[var(--color-paper)]/30">
                                        <th className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium w-10 md:w-16">
                                            {t.leaderboard.table.rank}
                                        </th>
                                        <th className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium">
                                            {t.leaderboard.table.model}
                                        </th>
                                        <TooltipHeader
                                            onClick={() => handleSort("overall")}
                                            tooltip={t.leaderboard.tooltips?.score}
                                            label={t.leaderboard.table.score}
                                            sortIndicator={
                                                <span className={`text-[10px] ml-1 ${sort.field === "overall" ? "opacity-100" : "opacity-50"}`}>
                                                    {sort.field === "overall" && sort.direction === "asc" ? "▲" : "▼"}
                                                </span>
                                            }
                                            className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                        />
                                        {currentTask === "exam" && (
                                            <>
                                                <TooltipHeader
                                                    onClick={() => handleSort("mcq")}
                                                    tooltip={t.leaderboard.tooltips?.mcq}
                                                    label={t.leaderboard.table.mcq}
                                                    sortIndicator={
                                                        <span className={`text-[10px] ml-1 ${sort.field === "mcq" ? "opacity-100" : "opacity-50"}`}>
                                                            {sort.field === "mcq" && sort.direction === "asc" ? "▲" : "▼"}
                                                        </span>
                                                    }
                                                    className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                                />
                                                <TooltipHeader
                                                    onClick={() => handleSort("short_text")}
                                                    tooltip={t.leaderboard.tooltips?.text}
                                                    label={t.leaderboard.table.text}
                                                    sortIndicator={
                                                        <span className={`text-[10px] ml-1 ${sort.field === "short_text" ? "opacity-100" : "opacity-50"}`}>
                                                            {sort.field === "short_text" && sort.direction === "asc" ? "▲" : "▼"}
                                                        </span>
                                                    }
                                                    className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                                />
                                            </>
                                        )}
                                        {currentTask === "pos" && (
                                            <>
                                                <TooltipHeader
                                                    onClick={() => handleSort("pos_accuracy")}
                                                    tooltip={t.leaderboard.tooltips?.pos}
                                                    label={t.leaderboard.table.pos}
                                                    sortIndicator={
                                                        <span className={`text-[10px] ml-1 ${sort.field === "pos_accuracy" ? "opacity-100" : "opacity-50"}`}>
                                                            {sort.field === "pos_accuracy" && sort.direction === "asc" ? "▲" : "▼"}
                                                        </span>
                                                    }
                                                    className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                                />
                                                <TooltipHeader
                                                    onClick={() => handleSort("lemma_accuracy")}
                                                    tooltip={t.leaderboard.tooltips?.lemma}
                                                    label={t.leaderboard.table.lemma}
                                                    sortIndicator={
                                                        <span className={`text-[10px] ml-1 ${sort.field === "lemma_accuracy" ? "opacity-100" : "opacity-50"}`}>
                                                            {sort.field === "lemma_accuracy" && sort.direction === "asc" ? "▲" : "▼"}
                                                        </span>
                                                    }
                                                    className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                                />
                                                <TooltipHeader
                                                    onClick={() => handleSort("dep_accuracy")}
                                                    tooltip={t.leaderboard.tooltips?.dep}
                                                    label={t.leaderboard.table.dep}
                                                    sortIndicator={
                                                        <span className={`text-[10px] ml-1 ${sort.field === "dep_accuracy" ? "opacity-100" : "opacity-50"}`}>
                                                            {sort.field === "dep_accuracy" && sort.direction === "asc" ? "▲" : "▼"}
                                                        </span>
                                                    }
                                                    className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                                />
                                            </>
                                        )}
                                        <TooltipHeader
                                            onClick={() => handleSort("latency_ms")}
                                            tooltip={t.leaderboard.tooltips?.latency}
                                            label={t.leaderboard.table.latency}
                                            sortIndicator={
                                                <span className={`text-[10px] ml-1 ${sort.field === "latency_ms" ? "opacity-100" : "opacity-50"}`}>
                                                    {sort.field === "latency_ms" && sort.direction === "asc" ? "▲" : "▼"}
                                                </span>
                                            }
                                            className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                        />
                                        <TooltipHeader
                                            onClick={() => handleSort("cost")}
                                            tooltip={t.leaderboard.tooltips?.cost}
                                            label={t.leaderboard.table.cost}
                                            sortIndicator={
                                                <span className={`text-[10px] ml-1 ${sort.field === "cost" ? "opacity-100" : "opacity-50"}`}>
                                                    {sort.field === "cost" && sort.direction === "asc" ? "▲" : "▼"}
                                                </span>
                                            }
                                            className="px-2 md:px-4 py-3 md:py-4 font-[var(--font-mono)] text-[10px] md:text-xs tracking-wider text-[var(--color-muted)] font-medium text-right cursor-pointer select-none hover:text-[var(--color-ink)]"
                                        />
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredAndSorted.length === 0 ? (
                                        <tr>
                                            <td colSpan={7} className="px-6 py-12 text-center text-[var(--color-muted)]">
                                                <p className="text-lg mb-2">{t.leaderboard.table.no_data}</p>
                                                <p className="text-sm">{t.leaderboard.table.no_data_desc}</p>
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredAndSorted.map((item, i) => {
                                            const rank = i + 1;
                                            const logo = PROVIDER_LOGOS[item.provider];

                                            return (
                                                <tr
                                                    key={item.model}
                                                    className={`
                                                    border-b border-[var(--color-ink)]/5 last:border-0 transition-colors
                                                    ${rank === 1 ? "bg-amber-50/50 hover:bg-amber-50" : "hover:bg-[var(--color-paper)]/50"}
                                                `}
                                                >
                                                    <td className="px-1 md:px-4 py-3 md:py-5 text-center w-8 md:w-12">
                                                        <span className={`font-[var(--font-mono)] text-base md:text-2xl font-bold ${rank === 1 ? "text-yellow-500" : rank === 2 ? "text-gray-400" : rank === 3 ? "text-amber-600" : "text-[var(--color-muted)]"}`}>
                                                            {rank}
                                                        </span>
                                                    </td>
                                                    <td className="px-2 md:px-4 py-3 md:py-5">
                                                        <div className="flex items-center gap-2 md:gap-3">
                                                            {logo && (
                                                                <Image src={logo} alt={item.provider} width={18} height={18} className="flex-shrink-0 md:w-[26px] md:h-[26px]" />
                                                            )}
                                                            <span className="font-[var(--font-mono)] text-xs md:text-base truncate max-w-[150px] md:max-w-none">{item.model}</span>
                                                            {(item.error_count ?? 0) > 0 && (
                                                                <span className="relative group ml-1">
                                                                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="currentColor" className="text-amber-500/80">
                                                                        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                                                                        <path d="M12 1.67c.955 0 1.845 .467 2.39 1.247l.105 .16l8.114 13.548a2.914 2.914 0 0 1 -2.307 4.363l-.195 .008h-16.225a2.914 2.914 0 0 1 -2.582 -4.2l.099 -.185l8.11 -13.538a2.914 2.914 0 0 1 2.491 -1.403zm.01 13.33l-.127 .007a1 1 0 0 0 0 1.986l.117 .007l.127 -.007a1 1 0 0 0 0 -1.986l-.117 -.007zm-.01 -7a1 1 0 0 0 -.993 .883l-.007 .117v4l.007 .117a1 1 0 0 0 1.986 0l.007 -.117v-4l-.007 -.117a1 1 0 0 0 -.993 -.883z" />
                                                                    </svg>

                                                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-[var(--color-ink)] text-[var(--color-cream)] text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none font-[var(--font-mono)]">
                                                                        {item.error_count}/{item.total_questions || 64} {t.leaderboard.table.failed_questions}
                                                                        <br />
                                                                        <span className="text-[var(--color-muted)]">API timeout or error</span>
                                                                        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[var(--color-ink)]"></div>
                                                                    </div>
                                                                </span>
                                                            )}
                                                        </div>
                                                    </td>
                                                    <td className="px-2 md:px-6 py-3 md:py-5 text-right">
                                                        <span className="font-[var(--font-mono)] font-semibold text-sm md:text-lg">{item.overall.toFixed(1)}</span>
                                                    </td>
                                                    {currentTask === "exam" && (
                                                        <>
                                                            <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                                {item.mcq?.toFixed(1) || "-"}
                                                            </td>
                                                            <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                                {item.short_text?.toFixed(1) || "-"}
                                                            </td>
                                                        </>
                                                    )}
                                                    {currentTask === "pos" && (
                                                        <>
                                                            <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                                {item.pos_accuracy !== undefined ? item.pos_accuracy.toFixed(1) : "-"}
                                                            </td>
                                                            <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                                {item.lemma_accuracy !== undefined ? item.lemma_accuracy.toFixed(1) : "-"}
                                                            </td>
                                                            <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                                {item.dep_accuracy !== undefined ? item.dep_accuracy.toFixed(1) : "-"}
                                                            </td>
                                                        </>
                                                    )}
                                                    <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                        {item.latency_ms ? `${(item.latency_ms / 1000).toFixed(1)}s` : "-"}
                                                    </td>
                                                    <td className="px-2 md:px-6 py-3 md:py-5 text-right font-[var(--font-mono)] text-xs md:text-base text-[var(--color-muted)]">
                                                        ${item.cost?.toFixed(2) || "-"}
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Scatter Plot View */}
                {viewMode === "scatter" && (
                    <div className="bg-white rounded-2xl border border-[var(--color-ink)]/10 overflow-hidden shadow-sm p-6">
                        <div className="mb-4 flex items-center justify-between">
                            <h3 className="font-[var(--font-mono)] text-sm text-[var(--color-muted)]">{t.leaderboard.scatter.score_vs_cost}</h3>
                            <div className="flex flex-wrap items-center gap-3 text-xs font-[var(--font-mono)]">
                                {Object.entries(PROVIDER_COLORS).map(([provider, color]) => (
                                    <button
                                        key={provider}
                                        onClick={() => toggleProviderHighlight(provider)}
                                        onMouseEnter={() => setHoveredProvider(provider)}
                                        onMouseLeave={() => setHoveredProvider(null)}
                                        className={`flex items-center gap-1.5 px-2 py-1 rounded-md transition-all cursor-pointer border ${highlightedProviders.has(provider)
                                            ? "bg-[var(--color-ink)]/5 border-[var(--color-ink)]/10"
                                            : "border-transparent hover:bg-[var(--color-ink)]/5"
                                            }`}
                                        style={{
                                            opacity: isProviderActive(provider) ? 1 : 0.4
                                        }}
                                    >
                                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                                        {provider}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <ResponsiveContainer width="100%" height={400}>
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis
                                    type="number"
                                    dataKey="x"
                                    name="Cost"
                                    unit="$"
                                    tick={{ fontSize: 12, fontFamily: "var(--font-mono)" }}
                                    tickFormatter={(v) => `$${v.toFixed(2)}`}
                                    label={{ value: t.leaderboard.scatter.x_axis, position: "bottom", offset: 0, fontSize: 12 }}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="y"
                                    name="Score"
                                    unit="%"
                                    domain={[0, 100]}
                                    tick={{ fontSize: 12, fontFamily: "var(--font-mono)" }}
                                    label={{ value: t.leaderboard.scatter.y_axis, angle: -90, position: "insideLeft", fontSize: 12 }}
                                />
                                <Tooltip
                                    content={({ active, payload }) => {
                                        if (!active || !payload?.length) return null;
                                        const d = payload[0].payload as ModelResult & { color: string };
                                        return (
                                            <div className="bg-white border border-[var(--color-ink)]/10 rounded-lg shadow-xl p-4 font-[var(--font-mono)] text-sm min-w-[200px]">
                                                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[var(--color-ink)]/5">
                                                    {PROVIDER_LOGOS[d.provider] && (
                                                        <Image
                                                            src={PROVIDER_LOGOS[d.provider]}
                                                            alt={d.provider}
                                                            width={20}
                                                            height={20}
                                                            className="rounded-sm"
                                                        />
                                                    )}
                                                    <span className="font-bold text-base">{d.model}</span>
                                                </div>
                                                <div className="space-y-1.5">
                                                    <div className="flex justify-between items-center">
                                                        <span className="text-[var(--color-muted)]">Score:</span>
                                                        <span className="font-bold text-lg">{d.overall.toFixed(1)}%</span>
                                                    </div>
                                                    {currentTask === "exam" && (
                                                        <>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-[var(--color-muted)]">MCQ:</span>
                                                                <span className="font-semibold">{d.mcq !== undefined ? d.mcq.toFixed(1) : "-"}%</span>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-[var(--color-muted)]">Text:</span>
                                                                <span className="font-semibold">{d.short_text !== undefined ? d.short_text.toFixed(1) : "-"}%</span>
                                                            </div>
                                                        </>
                                                    )}
                                                    {currentTask === "pos" && (
                                                        <>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-[var(--color-muted)]">POS:</span>
                                                                <span className="font-semibold">{d.pos_accuracy !== undefined ? d.pos_accuracy.toFixed(1) : "-"}%</span>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-[var(--color-muted)]">Lemma:</span>
                                                                <span className="font-semibold">{d.lemma_accuracy !== undefined ? d.lemma_accuracy.toFixed(1) : "-"}%</span>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-[var(--color-muted)]">Dep:</span>
                                                                <span className="font-semibold">{d.dep_accuracy !== undefined ? d.dep_accuracy.toFixed(1) : "-"}%</span>
                                                            </div>
                                                        </>
                                                    )}
                                                    <div className="flex justify-between items-center">
                                                        <span className="text-[var(--color-muted)]">Cost:</span>
                                                        <span className="font-semibold">${d.cost?.toFixed(2)}</span>
                                                    </div>
                                                    {d.latency_ms && (
                                                        <div className="flex justify-between items-center">
                                                            <span className="text-[var(--color-muted)]">Latency:</span>
                                                            <span className="font-semibold">{(d.latency_ms / 1000).toFixed(1)}s</span>
                                                        </div>
                                                    )}
                                                    <div className="text-xs text-[var(--color-muted)] mt-2 pt-2 border-t border-[var(--color-ink)]/5 text-right">
                                                        {d.provider}
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    }}
                                />
                                <Scatter
                                    data={scatterData}
                                    name="Models"
                                    isAnimationActive={false}
                                    shape={(props: any) => {
                                        const { cx, cy, fill, fillOpacity } = props;
                                        return <circle cx={cx} cy={cy} r={5} fill={fill} fillOpacity={fillOpacity} />;
                                    }}
                                    activeShape={(props: any) => {
                                        const { cx, cy, fill, fillOpacity } = props;
                                        return (
                                            <g>
                                                <circle cx={cx} cy={cy} r={8} fill="white" stroke={fill} strokeWidth={1} style={{ filter: 'drop-shadow(0px 2px 4px rgba(0,0,0,0.1))' }} />
                                                <circle cx={cx} cy={cy} r={6} fill={fill} fillOpacity={fillOpacity} />
                                            </g>
                                        );
                                    }}
                                >
                                    {scatterData.map((entry, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={entry.color}
                                            fillOpacity={isProviderActive(entry.provider) ? 1 : 0.15}
                                            strokeOpacity={isProviderActive(entry.provider) ? 1 : 0.15}
                                        />
                                    ))}
                                    <LabelList
                                        dataKey="model"
                                        position="right"
                                        offset={10}
                                        style={{
                                            fontSize: '10px',
                                            fontFamily: 'var(--font-mono)',
                                            pointerEvents: 'none',
                                            fontWeight: 500
                                        }}
                                        content={(props: any) => {
                                            const { x, y, value, index } = props;
                                            const entry = scatterData[index];

                                            // Guard against stale data during task switch
                                            if (!entry) return null;

                                            const isActive = isProviderActive(entry.provider);

                                            // Skip label if too close to other points
                                            if (!entry.showLabel) return null;

                                            return (
                                                <text
                                                    x={x}
                                                    y={y}
                                                    dx={15}
                                                    dy={8}
                                                    fill={entry.color}
                                                    fillOpacity={isActive ? 1 : 0.25}
                                                    fontSize={10}
                                                    fontFamily="var(--font-mono)"
                                                    fontWeight={600}
                                                    textAnchor="start"
                                                    style={{ pointerEvents: 'none' }}
                                                >
                                                    {value}
                                                </text>
                                            );
                                        }}
                                    />
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Table legend */}
                <div className="flex flex-wrap items-center gap-6 mt-4 text-sm text-[var(--color-muted)] font-[var(--font-mono)]">
                    <span>{t.leaderboard.filters.provider}:</span>
                    {Object.entries(PROVIDER_LOGOS).slice(0, 4).map(([provider, logo]) => (
                        <div key={provider} className="flex items-center gap-1.5">
                            <Image src={logo} alt={provider} width={14} height={14} />
                            {provider}
                        </div>
                    ))}
                    <span className="ml-auto">{t.leaderboard.last_updated}</span>
                </div>
            </div>
        </section>
    );
}
