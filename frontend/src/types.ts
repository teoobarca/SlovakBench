export interface ModelResult {
    model: string;
    provider: string;
    overall: number;
    mcq?: number;
    short_text?: number;
    pos_accuracy?: number;
    lemma_accuracy?: number;
    dep_accuracy?: number;
    cost?: number;
    latency_ms?: number;
    error_count?: number;
    total_questions?: number;
}

export interface LeaderboardData {
    exam: Record<number, ModelResult[]>;
    pos: Record<number, ModelResult[]>;
    grammar: Record<number, ModelResult[]>;
}

export type TaskType = 'exam' | 'pos' | 'grammar';
export type SortField = 'overall' | 'mcq' | 'short_text' | 'cost' | 'latency_ms';
export type SortDirection = 'asc' | 'desc';

export interface TaskDescription {
    icon: string;
    title: string;
    description: string;
    link?: string;
}
