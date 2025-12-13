"""SlovakBench CLI - Slovak LLM Benchmark Pipeline."""
import typer
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

app = typer.Typer(help="SlovakBench - Slovak LLM Benchmark")

RAW_DIR = Path("data/raw/exam")
PROCESSED_DIR = Path("data/processed/exam")
RESULTS_DIR = Path("data/results/exam")


def get_available_years(source_dir: Path, prefix: str = "test_") -> list[int]:
    """Get available years from PDF files."""
    years = []
    for f in source_dir.glob(f"{prefix}*.pdf"):
        try:
            year = int(f.stem.split("_")[-1])
            years.append(year)
        except ValueError:
            pass
    return sorted(years)


def get_processed_datasets() -> dict[int, Path]:
    """Get available processed datasets by year."""
    datasets = {}
    for f in PROCESSED_DIR.glob("*.json"):
        try:
            # Extract year from filename like "2025.json" or "test_2025.json"
            year = int(f.stem.split("_")[-1]) if "_" in f.stem else int(f.stem)
            datasets[year] = f
        except ValueError:
            pass
    return datasets


@app.command()
def ingest(
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Specific year to ingest"),
    all_years: bool = typer.Option(False, "--all", "-a", help="Ingest all available years"),
    force: bool = typer.Option(False, "--force", "-f", help="Reprocess already processed years"),
    model: str = typer.Option("openai/gpt-5.2", "--model", "-m", help="Model for extraction"),
):
    """Extract exam questions from PDF files."""
    from src.ingestion.mcq_parser import extract_mcq_from_pdf
    
    available = get_available_years(RAW_DIR)
    processed = get_processed_datasets()
    
    if not available:
        typer.echo("❌ No PDF files found in data/raw/exam/")
        raise typer.Exit(1)
    
    # Show status when no args
    if not year and not all_years:
        typer.echo("📋 Years status:")
        for y in sorted(available):
            status = "✅ processed" if y in processed else "⏳ pending"
            typer.echo(f"  {y}: {status}")
        typer.echo("\nUse --year YEAR or --all to ingest (--force to reprocess)")
        raise typer.Exit(0)
    
    # Determine which years to process
    if all_years:
        years_to_process = available
    elif year:
        if year not in available:
            typer.echo(f"❌ Year {year} not found. Available: {available}")
            raise typer.Exit(1)
        years_to_process = [year]
    else:
        years_to_process = []
    
    # Filter out already processed unless --force
    if not force:
        pending = [y for y in years_to_process if y not in processed]
        skipped = len(years_to_process) - len(pending)
        if skipped > 0:
            typer.echo(f"⏭️  Skipping {skipped} already processed (use --force to reprocess)")
        years_to_process = pending
    
    if not years_to_process:
        typer.echo("✅ All years already processed")
        raise typer.Exit(0)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    for y in years_to_process:
        test_pdf = RAW_DIR / f"test_{y}.pdf"
        key_pdf = RAW_DIR / f"kluc_{y}.pdf"
        output = PROCESSED_DIR / f"{y}.json"
        
        if not test_pdf.exists() or not key_pdf.exists():
            typer.echo(f"⚠️  Missing files for {y}, skipping")
            continue
        
        typer.echo(f"\n📄 Extracting {y}...")
        extraction = extract_mcq_from_pdf(str(test_pdf), str(key_pdf), model)
        
        with open(output, "w", encoding="utf-8") as f:
            json.dump(extraction.model_dump(), f, ensure_ascii=False, indent=2)
        
        typer.echo(f"✅ Saved {len(extraction.questions)} questions to {output}")


@app.command()
def evaluate(
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Year to evaluate"),
    all_years: bool = typer.Option(False, "--all", "-a", help="Evaluate all years"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Single model to evaluate"),
    force: bool = typer.Option(False, "--force", "-f", help="Re-run even if results exist"),
    list_datasets: bool = typer.Option(False, "--list", "-l", help="List available datasets"),
):
    """Run LLM evaluation on datasets. Without --model, runs all models from config."""
    from src.evaluation.runner import EvaluationRunner, save_results
    from config.models import MODELS
    
    datasets = get_processed_datasets()
    
    if list_datasets:
        typer.echo("📋 Available datasets:")
        for y, path in sorted(datasets.items()):
            typer.echo(f"  {y}: {path}")
        typer.echo(f"\n🤖 Configured models: {len(MODELS)}")
        for m in MODELS:
            typer.echo(f"  {m}")
        raise typer.Exit(0)
    
    # Determine years
    if all_years:
        years_to_eval = sorted(datasets.keys())
    elif year:
        if year not in datasets:
            typer.echo(f"❌ Year {year} not found")
            raise typer.Exit(1)
        years_to_eval = [year]
    else:
        years_to_eval = sorted(datasets.keys())  # Default to all
    
    # Determine models
    models_to_eval = [model] if model else MODELS
    
    # Track what needs to be done
    tasks = []
    for y in years_to_eval:
        for m in models_to_eval:
            model_short = m.split("/")[-1]
            result_file = RESULTS_DIR / str(y) / f"{model_short}.json"
            if result_file.exists() and not force:
                continue
            tasks.append((y, m))
    
    if not tasks:
        typer.echo("✅ All evaluations already complete (use --force to re-run)")
        raise typer.Exit(0)
    
    typer.echo(f"📊 Running {len(tasks)} evaluations...")
    
    for y, m in tasks:
        dataset_path = datasets[y]
        model_short = m.split("/")[-1]
        typer.echo(f"\n🧪 {model_short} | {y}")
        
        try:
            runner = EvaluationRunner(m)
            result = runner.run(str(dataset_path))
            
            output_dir = RESULTS_DIR / str(y)
            save_results(result, str(output_dir))
            
            mcq = f"MCQ {result.mcq_accuracy:.0%}" if result.mcq_accuracy else ""
            st = f"Text {result.short_text_accuracy:.0%}" if result.short_text_accuracy else ""
            latency = f"⏱️ {result.avg_latency_ms:.0f}ms" if result.avg_latency_ms else ""
            typer.echo(f"   ✅ {result.accuracy:.1%} ({result.correct_count}/{result.total_questions}) | {mcq} | {st} | 💰${result.total_cost_usd:.4f} | {latency}")
        except Exception as e:
            typer.echo(f"   ❌ Error: {e}")


@app.command()
def report(
    results_path: Path = typer.Argument(None, help="Path to results JSON"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Show results for year"),
    compare: bool = typer.Option(False, "--compare", "-c", help="Compare all models for year"),
):
    """Generate metrics report from evaluation results."""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    if year:
        year_dir = RESULTS_DIR / str(year)
        if not year_dir.exists():
            typer.echo(f"❌ No results for year {year}")
            raise typer.Exit(1)
        results_files = sorted(year_dir.glob("*.json"))
        if not results_files:
            typer.echo(f"❌ No results found in {year_dir}")
            raise typer.Exit(1)
        
        # Build comparison table
        table = Table(title=f"📊 SlovakBench Results - {year}")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Overall", justify="right")
        table.add_column("MCQ", justify="right")
        table.add_column("Short Text", justify="right")
        table.add_column("Cost", justify="right", style="green")
        table.add_column("Timestamp", style="dim")
        
        for f in results_files:
            with open(f) as fp:
                data = json.load(fp)
            
            model = data.get("model_name", "?").split("/")[-1]
            acc = f"{data.get('accuracy', 0):.1%}"
            mcq = f"{data.get('mcq_accuracy', 0):.1%}" if data.get('mcq_accuracy') else "-"
            st = f"{data.get('short_text_accuracy', 0):.1%}" if data.get('short_text_accuracy') else "-"
            cost = f"${data.get('total_cost_usd', 0):.4f}"
            ts = data.get("timestamp", "?")[:16]
            
            table.add_row(model, acc, mcq, st, cost, ts)
        
        console.print(table)
    
    elif results_path and results_path.exists():
        with open(results_path) as f:
            data = json.load(f)
        
        from src.evaluation.metrics import compute_metrics, format_metrics_report
        results = data.get("results", [])
        summary = compute_metrics(results)
        report_text = format_metrics_report(summary, data.get("model_name", ""))
        typer.echo(report_text)
    
    else:
        # Show cross-year model comparison
        from collections import defaultdict
        
        model_stats = defaultdict(lambda: {"years": [], "accs": [], "mcq": [], "st": [], "cost": 0.0})
        
        for year_dir in sorted(RESULTS_DIR.iterdir()):
            if year_dir.is_dir():
                for f in year_dir.glob("*.json"):
                    with open(f) as fp:
                        data = json.load(fp)
                    model = data.get("model_name", "?").split("/")[-1]
                    model_stats[model]["years"].append(year_dir.name)
                    model_stats[model]["accs"].append(data.get("accuracy", 0))
                    if data.get("mcq_accuracy"):
                        model_stats[model]["mcq"].append(data["mcq_accuracy"])
                    if data.get("short_text_accuracy"):
                        model_stats[model]["st"].append(data["short_text_accuracy"])
                    model_stats[model]["cost"] += data.get("total_cost_usd", 0)
        
        if not model_stats:
            typer.echo("No results found. Run 'evaluate' first.")
            raise typer.Exit(1)
        
        table = Table(title="📊 SlovakBench - Model Comparison")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Years", justify="center")
        table.add_column("Avg Overall", justify="right", style="bold")
        table.add_column("Avg MCQ", justify="right")
        table.add_column("Avg Text", justify="right")
        table.add_column("Total Cost", justify="right", style="green")
        
        for model, stats in sorted(model_stats.items()):
            avg_acc = sum(stats["accs"]) / len(stats["accs"]) if stats["accs"] else 0
            avg_mcq = sum(stats["mcq"]) / len(stats["mcq"]) if stats["mcq"] else 0
            avg_st = sum(stats["st"]) / len(stats["st"]) if stats["st"] else 0
            years_str = ",".join(sorted(set(stats["years"])))
            
            table.add_row(
                model,
                years_str,
                f"{avg_acc:.1%}",
                f"{avg_mcq:.1%}" if stats["mcq"] else "-",
                f"{avg_st:.1%}" if stats["st"] else "-",
                f"${stats['cost']:.4f}"
            )
        
        console.print(table)
        typer.echo("\nUse --year YEAR to see year-specific results")


@app.command()
def export():
    """Export leaderboard data to public/leaderboard.json for frontend."""
    from collections import defaultdict
    
    PUBLIC_DIR = Path("public")
    PUBLIC_DIR.mkdir(exist_ok=True)
    
    # Structure: { task: { year: [ {model, provider, overall, mcq, short_text, cost} ] } }
    leaderboard = {
        "exam": defaultdict(list),
        "pos": defaultdict(list),
        "grammar": defaultdict(list),
    }
    
    # Provider display names (key is the slug before /)
    provider_names = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "mistralai": "Mistral",
        "meta-llama": "Meta",
        "qwen": "Alibaba",
        "deepseek": "DeepSeek",
    }
    
    # Collect exam results
    exam_dir = RESULTS_DIR
    if exam_dir.exists():
        for year_dir in exam_dir.iterdir():
            if year_dir.is_dir():
                year = year_dir.name
                for f in year_dir.glob("*.json"):
                    with open(f) as fp:
                        data = json.load(fp)
                    
                    full_name = data.get("model_name", "unknown/unknown")
                    provider_slug = full_name.split("/")[0]
                    model_raw = full_name.split("/")[-1]
                    # Strip suffixes like :free, :thinking for display
                    model = model_raw.split(":")[0]
                    
                    leaderboard["exam"][year].append({
                        "model": model,
                        "provider": provider_names.get(provider_slug, provider_slug.title()),
                        "overall": round(data.get("accuracy", 0) * 100, 1),
                        "mcq": round(data.get("mcq_accuracy", 0) * 100, 1) if data.get("mcq_accuracy") else None,
                        "short_text": round(data.get("short_text_accuracy", 0) * 100, 1) if data.get("short_text_accuracy") else None,
                        "cost": round(data.get("total_cost_usd", 0), 4),
                    })
    
    # Sort each year by overall score
    for task in leaderboard:
        for year in leaderboard[task]:
            leaderboard[task][year] = sorted(
                leaderboard[task][year], 
                key=lambda x: x["overall"], 
                reverse=True
            )
    
    # Convert defaultdict to regular dict for JSON
    output = {task: dict(years) for task, years in leaderboard.items()}
    
    output_path = PUBLIC_DIR / "leaderboard.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Count stats
    total_models = len(set(
        m["model"] 
        for task in output.values() 
        for year in task.values() 
        for m in year
    ))
    
    typer.echo(f"✅ Exported to {output_path}")
    typer.echo(f"   Models: {total_models}")
    typer.echo(f"   Tasks: {len([t for t in output.values() if any(y for y in t.values())])}")


if __name__ == "__main__":
    app()
