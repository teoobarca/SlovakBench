"""
Metrics computation for skBench evaluation.
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass 
class MetricsSummary:
    """Summary metrics for evaluation."""
    total: int
    correct: int
    accuracy: float
    by_task_type: Dict[str, Dict[str, float]]
    
    def to_dict(self) -> Dict:
        return {
            "total": self.total,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "by_task_type": self.by_task_type,
        }


def compute_metrics(results: List[Dict[str, Any]]) -> MetricsSummary:
    """
    Compute accuracy metrics from evaluation results.
    
    Args:
        results: List of QuestionResult dicts with 'task_type' and 'is_correct' keys
    
    Returns:
        MetricsSummary with overall and per-task-type accuracy
    """
    if not results:
        return MetricsSummary(total=0, correct=0, accuracy=0.0, by_task_type={})
    
    total = len(results)
    correct = sum(1 for r in results if r.get("is_correct", False))
    
    # Group by task type
    by_type: Dict[str, Dict[str, int]] = {}
    for r in results:
        task_type = r.get("task_type", "unknown")
        if task_type not in by_type:
            by_type[task_type] = {"total": 0, "correct": 0}
        by_type[task_type]["total"] += 1
        if r.get("is_correct", False):
            by_type[task_type]["correct"] += 1
    
    # Compute per-type accuracy
    by_task_type = {}
    for task_type, counts in by_type.items():
        t, c = counts["total"], counts["correct"]
        by_task_type[task_type] = {
            "total": t,
            "correct": c,
            "accuracy": c / t if t > 0 else 0.0,
        }
    
    return MetricsSummary(
        total=total,
        correct=correct,
        accuracy=correct / total if total > 0 else 0.0,
        by_task_type=by_task_type,
    )


def format_metrics_report(summary: MetricsSummary, model_name: str = "") -> str:
    """Format metrics as a readable report string."""
    lines = []
    
    if model_name:
        lines.append(f"# Evaluation Report: {model_name}")
    else:
        lines.append("# Evaluation Report")
    
    lines.append("")
    lines.append(f"**Overall Accuracy**: {summary.accuracy:.1%} ({summary.correct}/{summary.total})")
    lines.append("")
    
    if summary.by_task_type:
        lines.append("## By Task Type")
        lines.append("")
        lines.append("| Task Type | Accuracy | Correct | Total |")
        lines.append("|-----------|----------|---------|-------|")
        for task_type, data in sorted(summary.by_task_type.items()):
            lines.append(
                f"| {task_type} | {data['accuracy']:.1%} | {data['correct']} | {data['total']} |"
            )
    
    return "\n".join(lines)
