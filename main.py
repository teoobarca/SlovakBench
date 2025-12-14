"""SlovakBench CLI - Slovak LLM Benchmark Pipeline."""
import typer
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

app = typer.Typer(help="SlovakBench - Slovak LLM Benchmark")

# Subcommand groups
evaluate_app = typer.Typer(help="Run LLM evaluations")
app.add_typer(evaluate_app, name="evaluate")

RAW_DIR = Path("data/raw/exam")
PROCESSED_DIR = Path("data/processed/exam")
RESULTS_DIR = Path("data/results/exam")
UD_RESULTS_DIR = Path("data/results/ud_snk")


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


@evaluate_app.command("exam")
def evaluate_exam(
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Year to evaluate"),
    all_years: bool = typer.Option(False, "--all", "-a", help="Evaluate all years"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Single model to evaluate"),
    force: bool = typer.Option(False, "--force", "-f", help="Re-run even if results exist"),
    list_datasets: bool = typer.Option(False, "--list", "-l", help="List available datasets"),
):
    """Run exam benchmark evaluation. Without --model, runs all models from config."""
    from src.evaluation.runner import EvaluationRunner, save_results
    from config.models import MODELS
    
    datasets = get_processed_datasets()
    
    if list_datasets:
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        
        # Datasets Info
        console.print(f"\n📚 [bold]Available Datasets (Years):[/bold] {', '.join(map(str, sorted(datasets.keys())))}")
        
        # Status Table
        table = Table(title=f"🤖 Model Evaluation Status ({len(MODELS)} configured)")
        table.add_column("Model Identifier", style="cyan")
        
        sorted_years = sorted(datasets.keys())
        for y in sorted_years:
            table.add_column(str(y), justify="center")
            
        for m in MODELS:
            model_short = m.split("/")[-1]
            row = [model_short]
            
            for y in sorted_years:
                output_path = RESULTS_DIR / str(y) / f"{model_short}.json"
                if output_path.exists():
                    row.append("✅")
                else:
                    row.append("[dim]⚪[/dim]")
            table.add_row(*row)
            
        console.print(table)
        console.print("[dim]Use --model [MODEL] --year [YEAR] to run specific evaluation[/dim]")
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
    if model:
        # Validate model is in config
        if model not in MODELS:
            typer.echo(f"❌ Unknown model: {model}")
            typer.echo(f"   Available models:")
            for m in MODELS:
                typer.echo(f"     {m}")
            raise typer.Exit(1)
        models_to_eval = [model]
    else:
        models_to_eval = MODELS
    
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
            saved_path = save_results(result, str(output_dir))
            
            answered = result.total_questions - result.error_count
            mcq = f"MCQ {result.mcq_accuracy:.0%}" if result.mcq_accuracy else ""
            st = f"Text {result.short_text_accuracy:.0%}" if result.short_text_accuracy else ""
            latency = f"⏱️ {result.avg_latency_ms:.0f}ms" if result.avg_latency_ms else ""
            
            if saved_path:
                typer.echo(f"   ✅ {result.accuracy:.1%} ({result.correct_count}/{answered}) | {mcq} | {st} | 💰${result.total_cost_usd:.4f} | {latency}")
            else:
                typer.echo(f"   ⚠️  Too many errors, result not saved")
                # Show sample error for debugging
                sample_errors = [r for r in result.results if r.error][:2]
                for err in sample_errors:
                    typer.echo(f"      → Q{err.question_id}: {err.error[:150]}...")
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
            try:
                with open(f) as fp:
                    data = json.load(fp)
            except json.JSONDecodeError:
                typer.echo(f"⚠️ Warning: Skipping corrupted file {f.name}")
                continue
            
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
                    try:
                        with open(f) as fp:
                            data = json.load(fp)
                    except json.JSONDecodeError:
                        typer.echo(f"⚠️ Warning: Skipping corrupted file {f.name}")
                        continue
                    model = data.get("model_name", "?").split("/")[-1]
                    model_stats[model]["years"].append(year_dir.name)
                    model_stats[model]["accs"].append(data.get("accuracy", 0))
                    if data.get("mcq_accuracy"):
                        model_stats[model]["mcq"].append(data["mcq_accuracy"])
                    if data.get("short_text_accuracy"):
                        model_stats[model]["st"].append(data["short_text_accuracy"])
                    model_stats[model]["cost"] += data.get("total_cost_usd", 0)
                    if data.get("avg_latency_ms"):
                        if "latency" not in model_stats[model]:
                            model_stats[model]["latency"] = []
                        model_stats[model]["latency"].append(data["avg_latency_ms"])
        
        if not model_stats:
            typer.echo("No results found. Run 'evaluate' first.")
            raise typer.Exit(1)
        
        table = Table(title="📊 SlovakBench - Model Comparison")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Years", justify="center")
        table.add_column("Avg Overall", justify="right", style="bold")
        table.add_column("Avg MCQ", justify="right")
        table.add_column("Avg Text", justify="right")
        table.add_column("Latency", justify="right", style="dim")
        table.add_column("Total Cost", justify="right", style="green")
        
        for model, stats in sorted(model_stats.items()):
            avg_acc = sum(stats["accs"]) / len(stats["accs"]) if stats["accs"] else 0
            avg_mcq = sum(stats["mcq"]) / len(stats["mcq"]) if stats["mcq"] else 0
            avg_st = sum(stats["st"]) / len(stats["st"]) if stats["st"] else 0
            avg_latency = sum(stats.get("latency", [])) / len(stats.get("latency", [1])) if stats.get("latency") else None
            years_str = ",".join(sorted(set(stats["years"])))
            
            table.add_row(
                model,
                years_str,
                f"{avg_acc:.1%}",
                f"{avg_mcq:.1%}" if stats["mcq"] else "-",
                f"{avg_st:.1%}" if stats["st"] else "-",
                f"{avg_latency:.0f}ms" if avg_latency else "-",
                f"${stats['cost']:.4f}"
            )
        
        console.print(table)
        typer.echo("\nUse --year YEAR to see year-specific results")


@app.command()
def export():
    """Export leaderboard data to frontend/public/leaderboard.json for frontend."""
    from collections import defaultdict
    
    OUTPUT_DIR = Path("frontend/public")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
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
        "mistral": "Mistral",
        "meta-llama": "Meta",
        "qwen": "Qwen",
        "deepseek": "DeepSeek",
        "moonshotai": "Kimi",
        "minimax": "Minimax",
        "cohere": "Cohere",
        "databricks": "Databricks",
        "tii": "TII",
        "microsoft": "Microsoft",
        "x-ai": "xAI",
        "z-ai": "zAI",
        "ai21": "AI21",
    }
    
    # Collect exam results
    exam_dir = RESULTS_DIR
    if exam_dir.exists():
        for year_dir in exam_dir.iterdir():
            if year_dir.is_dir():
                year = year_dir.name
                for f in year_dir.glob("*.json"):
                    try:
                        with open(f) as fp:
                            data = json.load(fp)
                    except json.JSONDecodeError:
                        print(f"⚠️ Warning: Skipping corrupted file {f.name}")
                        continue
                    
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
                        "latency_ms": round(data.get("avg_latency_ms", 0)) if data.get("avg_latency_ms") else None,
                        "error_count": data.get("error_count", 0),
                        "total_questions": data.get("total_questions", 64),
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
    
    output_path = OUTPUT_DIR / "leaderboard.json"
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


@app.command()
def analyze(
    year: int = typer.Option(..., "--year", "-y", help="Year to analyze"),
    question: Optional[str] = typer.Option(None, "--question", "-q", help="Specific question ID"),
    threshold: int = typer.Option(50, "--threshold", "-t", help="Min % of models that must fail to flag question"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Filter by model name (partial match)"),
):
    """Analyze failed questions across all models to identify dataset issues."""
    from rich.console import Console
    from rich.table import Table
    from collections import defaultdict
    
    console = Console()
    
    # Load dataset
    datasets = get_processed_datasets()
    if year not in datasets:
        typer.echo(f"❌ No dataset for year {year}")
        raise typer.Exit(1)
    
    with open(datasets[year]) as f:
        dataset = json.load(f)
    
    questions_by_id = {q["id"]: q for q in dataset["questions"]}
    
    # Load all results for this year
    year_dir = RESULTS_DIR / str(year)
    if not year_dir.exists():
        typer.echo(f"❌ No results for year {year}")
        raise typer.Exit(1)
    
    results_by_question = defaultdict(list)
    model_count = 0
    
    for f in year_dir.glob("*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
        except json.JSONDecodeError:
            continue
        
        model_name = data.get("model_name", "?").split("/")[-1]
        
        # Filter by model if requested
        if model and model.lower() not in model_name.lower():
            continue
            
        model_count += 1
        
        for r in data.get("results", []):
            if r.get("error"):
                continue  # Skip technical errors
            results_by_question[r["question_id"]].append({
                "model": model_name,
                "answer": r.get("model_answer", ""),
                "correct": r.get("is_correct", False),
            })
    
    if model_count == 0:
        typer.echo("❌ No valid result files found")
        raise typer.Exit(1)
    
    console.print(f"\n📊 [bold]Question Analysis: {year}[/bold] ({model_count} models)")
    console.print()
    
    # Filter to specific question if requested
    question_ids = [question] if question else sorted(results_by_question.keys())
    
    flagged = 0
    for qid in question_ids:
        if qid not in questions_by_id:
            continue
        
        q = questions_by_id[qid]
        results = results_by_question.get(qid, [])
        
        if not results:
            continue
        
        failed = [r for r in results if not r["correct"]]
        passed = [r for r in results if r["correct"]]
        fail_pct = len(failed) / len(results) * 100 if results else 0
        
        # Skip if below threshold (unless specific question requested)
        if not question and fail_pct < threshold:
            continue
        
        flagged += 1
        
        # Get expected answer
        if q["task_type"] == "mcq":
            expected = q["answer"].get("correct_option", "?")
            normalize_steps = None
        else:
            accepted = q["answer"].get("accepted", [])
            expected = ", ".join(accepted[:5]) + ("..." if len(accepted) > 5 else "")
            normalize_steps = q["answer"].get("normalize", [])
        
        # Print question header
        status = "❌" if fail_pct >= 80 else "⚠️" if fail_pct >= 50 else "🔍"
        console.print(f"{status} [bold]Q{qid}[/bold] [{q['task_type']}] - {len(failed)}/{len(results)} models failed ({fail_pct:.0f}%)")
        
        # Show question text (truncated)
        question_text = q.get("question", "")
        if len(question_text) > 200:
            question_text = question_text[:200] + "..."
        console.print(f"   [cyan]Q:[/cyan] {question_text}")
        
        # Show context if available (first 150 chars)
        if q.get("context_id"):
            ctx = next((c for c in dataset.get("contexts", []) if c["id"] == q["context_id"]), None)
            if ctx:
                ctx_text = ctx.get("text", "")[:150].replace("\n", " ")
                console.print(f"   [dim]Context ({q['context_id']}):[/dim] {ctx_text}...")
        
        console.print(f"   [dim]Expected:[/dim] {expected}")
        if normalize_steps:
            console.print(f"   [dim]Normalize:[/dim] {', '.join(normalize_steps)}")
        console.print("   " + "─" * 50)
        
        # Group answers
        answer_groups = defaultdict(list)
        for r in results:
            answer_groups[r["answer"]].append((r["model"], r["correct"]))
        
        # Sort by frequency
        for ans, models in sorted(answer_groups.items(), key=lambda x: -len(x[1])):
            is_correct = any(c for _, c in models)
            prefix = "[green]✅[/green]" if is_correct else "[red]❌[/red]"
            model_list = ", ".join(m for m, _ in models[:3])
            if len(models) > 3:
                model_list += f" +{len(models)-3} more"
            console.print(f"   {prefix} \"{ans}\" ({len(models)}): {model_list}")
        
        console.print()
    
    if flagged == 0:
        console.print(f"[green]✅ No questions flagged (threshold: {threshold}% failure rate)[/green]")
    else:
        console.print(f"[yellow]⚠️ {flagged} questions flagged for review[/yellow]")


@app.command()
def recalculate(
    year: int = typer.Option(..., "--year", "-y", help="Year to recalculate"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show changes without saving"),
):
    """Recalculate results from stored answers after dataset fixes."""
    from rich.console import Console
    from rich.table import Table
    from src.evaluation.answer_validator import normalize, validate_mcq, validate_short_text
    
    console = Console()
    
    # Load dataset
    datasets = get_processed_datasets()
    if year not in datasets:
        typer.echo(f"❌ No dataset for year {year}")
        raise typer.Exit(1)
    
    with open(datasets[year]) as f:
        dataset = json.load(f)
    
    questions_by_id = {q["id"]: q for q in dataset["questions"]}
    
    # Load and recalculate all results
    year_dir = RESULTS_DIR / str(year)
    if not year_dir.exists():
        typer.echo(f"❌ No results for year {year}")
        raise typer.Exit(1)
    
    table = Table(title=f"🔄 Recalculation: {year}")
    table.add_column("Model", style="cyan")
    table.add_column("Before", justify="right")
    table.add_column("After", justify="right")
    table.add_column("Δ", justify="right")
    
    updated_files = 0
    
    for f in sorted(year_dir.glob("*.json")):
        try:
            with open(f) as fp:
                data = json.load(fp)
        except json.JSONDecodeError:
            continue
            
        model_name = data.get("model_name", "?")
        results = data.get("results", [])
        original_count = len(results)
        
        # Calculate scores
        # ... logic reused ...
        
        updated_results = []
        changed = False
        
        for r in results:
            # Re-validate
            question_id = r["question_id"]
            if question_id not in questions_by_id:
                updated_results.append(r)
                continue
                
            q = questions_by_id[question_id]
            model_answer = r.get("model_answer", "")
            
            # Use validator
            if q["task_type"] == "mcq":
                correct_opt = q["answer"].get("correct_option", "")
                is_correct = validate_mcq(model_answer, correct_opt)
            else:
                accepted = q["answer"].get("accepted", [])
                steps = q["answer"].get("normalize", ["trim", "casefold"])
                is_correct = validate_short_text(model_answer, accepted, steps)
            
            if is_correct != r.get("is_correct"):
                r["is_correct"] = is_correct
                changed = True
            
            updated_results.append(r)
        
        # Calculate new accuracy
        new_correct = len([r for r in updated_results if r.get("is_correct")])
        new_pct = new_correct / original_count * 100 if original_count else 0
        
        # Helper to get old accuracy
        old_correct = len([r for r in data.get("results", []) if r.get("is_correct")])
        old_pct = old_correct / original_count * 100 if original_count else 0
        
        delta = new_pct - old_pct
        delta_str = f"[green]+{delta:.1f}%[/green]" if delta > 0 else f"[red]{delta:.1f}%[/red]" if delta < 0 else "[dim]0.0%[/dim]"
        
        table.add_row(
            model_name.split("/")[-1],
            f"{old_pct:.1f}%",
            f"{new_pct:.1f}%",
            delta_str
        )
        
        # Save if changed
        if changed and not dry_run:
            data["results"] = updated_results
            # Update aggregates
            if original_count > 0:
                data["correct_count"] = new_correct
                data["accuracy"] = new_correct / original_count
                data["total_questions"] = original_count
                
                # Recalc per-type
                mcq_results = [r for r in updated_results if r.get("task_type") == "mcq" and not r.get("error")]
                st_results = [r for r in updated_results if r.get("task_type") == "short_text" and not r.get("error")]
                
                if mcq_results:
                    data["mcq_accuracy"] = sum(1 for r in mcq_results if r.get("is_correct")) / len(mcq_results)
                if st_results:
                    data["short_text_accuracy"] = sum(1 for r in st_results if r.get("is_correct")) / len(st_results)

            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2, ensure_ascii=False)
            updated_files += 1
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run - no files updated[/yellow]")
    else:
        console.print(f"\n[green]✅ Updated {updated_files} result files[/green]")


@app.command()
def reevaluate(
    year: int = typer.Option(..., "--year", "-y", help="Year to re-evaluate"),
    question: str = typer.Option(..., "--question", "-q", help="Question ID to re-run (e.g. '32')"),
):
    """Re-run a specific question for ALL models by manipulating checkpoints."""
    from rich.console import Console
    from src.evaluation.runner import EvaluationRunner, CheckpointManager
    from datetime import datetime
    
    console = Console()
    
    # Load dataset
    datasets = get_processed_datasets()
    if year not in datasets:
        typer.echo(f"❌ No dataset for year {year}")
        raise typer.Exit(1)
        
    dataset_path = str(datasets[year])
    
    # Locate all results
    year_dir = RESULTS_DIR / str(year)
    if not year_dir.exists():
        typer.echo(f"❌ No results for year {year}")
        raise typer.Exit(1)
    
    results_files = list(year_dir.glob("*.json"))
    console.print(f"🔄 Re-evaluating Q{question} for {len(results_files)} models...")
    
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from tqdm import tqdm
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    diffs = []
    
    for f in tqdm(results_files, desc="Models", leave=True):
        try:
            with open(f) as fp:
                data = json.load(fp)
        except:
            continue
            
        model_name = data.get("model_name")
        if not model_name:
            continue
            
        short_name = model_name.split("/")[-1]
        
        current_results = data.get("results", [])
        
        # Find old answer for diff
        old_result = next((r for r in current_results if r["question_id"] == question), None)
        old_ans = old_result.get("model_answer", "") if old_result else "-"
        old_correct = old_result.get("is_correct", False) if old_result else False
        
        filtered_results = [r for r in current_results if r["question_id"] != question]
        
        # Create checkpoint
        ckpt = CheckpointManager(model_name, dataset_path)
        
        checkpoint_data = {
            "model_name": model_name,
            "dataset_path": dataset_path,
            "timestamp": datetime.now().isoformat(),
            "results": filtered_results
        }
        
        with open(ckpt.checkpoint_path, "w", encoding="utf-8") as fp:
            json.dump(checkpoint_data, fp, ensure_ascii=False, indent=2)
            
        # Run evaluation with suppressed output
        runner = EvaluationRunner(model_name=model_name)
        
        try:
            # Suppress tqdm and print output from runner
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                new_result = runner.run(dataset_path, resume=True)
            
            # Sort results by ID
            def get_id(r):
                try:
                    return int(r.question_id)
                except ValueError:
                    return 9999
            
            new_result.results.sort(key=get_id)
            
            # Save
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(new_result.to_dict(), fp, indent=2, ensure_ascii=False)
            
            # Find new answer
            new_r = next((r for r in new_result.results if r.question_id == question), None)
            new_ans = new_r.model_answer if new_r else "-"
            new_correct = new_r.is_correct if new_r else False
            
            diffs.append({
                "model": short_name,
                "old_ans": old_ans,
                "new_ans": new_ans,
                "old_correct": old_correct,
                "new_correct": new_correct,
                "changed": old_ans != new_ans or old_correct != new_correct
            })
            
        except Exception as e:
            diffs.append({
                "model": short_name,
                "old_ans": old_ans,
                "new_ans": f"ERROR: {e}",
                "old_correct": old_correct,
                "new_correct": False,
                "changed": True
            })
            if ckpt.checkpoint_path.exists():
                ckpt.checkpoint_path.unlink()
    
    # Show summary table
    table = Table(title=f"📋 Q{question} Changes", box=None, pad_edge=False)
    table.add_column("Model", style="cyan", max_width=25)
    table.add_column("Before", style="dim", max_width=20)
    table.add_column("After", max_width=20)
    table.add_column("", justify="center", width=8)
    
    changes_count = 0
    
    for d in sorted(diffs, key=lambda x: x["model"]):
        if not d["changed"]:
            continue
            
        changes_count += 1
        
        # Verdict with color
        if d["old_correct"] and not d["new_correct"]:
            verdict = "[red]✅→❌[/red]"   # Got worse
        elif not d["old_correct"] and d["new_correct"]:
            verdict = "[green]❌→✅[/green]"  # Got better
        elif d["new_correct"]:
            verdict = "[green]✅[/green]"
        else:
            verdict = "[red]❌[/red]"
        
        # Truncate answers
        old_ans = d['old_ans'][:18] + "…" if len(d['old_ans']) > 18 else d['old_ans']
        new_ans = d['new_ans'][:18] + "…" if len(d['new_ans']) > 18 else d['new_ans']
        
        table.add_row(d["model"], old_ans, new_ans, verdict)
    
    console.print()
    if changes_count > 0:
        console.print(table)
    else:
        console.print("[yellow]No changes in answers/correctness detected.[/yellow]")
        
    console.print(f"\n✅ Re-evaluation complete. Run [bold]analyze[/bold] to see full results.")


@app.command()
def retry(
    year: int = typer.Option(..., "--year", "-y", help="Year to retry errors for"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Specific model to retry (partial match)"),
    list_only: bool = typer.Option(False, "--list", "-l", help="Just show what would be retried"),
):
    """Retry only the ERRORED questions for models with partial failures."""
    from rich.table import Table
    from rich.console import Console
    from tqdm import tqdm
    import io
    from contextlib import redirect_stdout, redirect_stderr
    from src.evaluation.runner import CheckpointManager, EvaluationRunner
    
    console = Console()
    
    year_dir = RESULTS_DIR / str(year)
    if not year_dir.exists():
        typer.echo(f"❌ No results for year {year}")
        raise typer.Exit(1)
    
    dataset_path = f"data/processed/exam/{year}.json"
    
    # Find models with errors
    models_with_errors = []
    
    for f in year_dir.glob("*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
        except:
            continue
        
        model_name = data.get("model_name", "")
        error_count = data.get("error_count", 0)
        
        # Count errors from results if error_count not present
        if error_count == 0:
            error_count = sum(1 for r in data.get("results", []) if r.get("error"))
        
        if error_count > 0:
            # Filter by model if specified
            if model and model.lower() not in model_name.lower():
                continue
                
            errored_questions = [r["question_id"] for r in data.get("results", []) if r.get("error")]
            models_with_errors.append({
                "file": f,
                "model_name": model_name,
                "short_name": model_name.split("/")[-1],
                "error_count": error_count,
                "total": data.get("total_questions", 64),
                "errored_questions": errored_questions,
            })
    
    if not models_with_errors:
        console.print("[green]✅ No models with errors found![/green]")
        return
    
    # Show table
    table = Table(title=f"🔄 Models with Errors ({year})")
    table.add_column("Model", style="cyan")
    table.add_column("Errors", justify="right")
    table.add_column("Questions")
    
    for m in sorted(models_with_errors, key=lambda x: -x["error_count"]):
        qs = ", ".join(m["errored_questions"][:5])
        if len(m["errored_questions"]) > 5:
            qs += f" (+{len(m['errored_questions']) - 5} more)"
        table.add_row(
            m["short_name"],
            f"{m['error_count']}/{m['total']}",
            qs
        )
    
    console.print(table)
    
    if list_only:
        console.print("\n[dim]Use without --list to retry these.[/dim]")
        return
    
    console.print(f"\n🔄 Retrying {len(models_with_errors)} models...")
    
    # Track results for summary
    retry_results = []
    
    for m in tqdm(models_with_errors, desc="Retrying"):
        try:
            with open(m["file"]) as fp:
                data = json.load(fp)
        except:
            continue
        
        # Store before stats
        before_errors = m["error_count"]
        before_accuracy = data.get("accuracy", 0)
        
        # Keep only non-errored results
        good_results = [r for r in data.get("results", []) if not r.get("error")]
        
        # Create checkpoint with good results only
        ckpt = CheckpointManager(m["model_name"], dataset_path)
        
        checkpoint_data = {
            "model_name": m["model_name"],
            "dataset_path": dataset_path,
            "timestamp": datetime.now().isoformat(),
            "results": good_results
        }
        
        with open(ckpt.checkpoint_path, "w", encoding="utf-8") as fp:
            json.dump(checkpoint_data, fp, ensure_ascii=False, indent=2)
        
        # Run evaluation with suppressed output
        runner = EvaluationRunner(model_name=m["model_name"])
        
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                new_result = runner.run(dataset_path, resume=True)
            
            # Sort results by ID
            def get_id(r):
                try:
                    return int(r.question_id)
                except ValueError:
                    return 9999
            
            new_result.results.sort(key=get_id)
            
            # Save
            with open(m["file"], "w", encoding="utf-8") as fp:
                json.dump(new_result.to_dict(), fp, indent=2, ensure_ascii=False)
            
            # Track results
            after_errors = new_result.error_count
            after_accuracy = new_result.accuracy
            
            # Calculate cost of retried questions only
            retried_cost = sum(r.cost_usd for r in new_result.results 
                             if r.question_id in m["errored_questions"])
            
            retry_results.append({
                "model": m["short_name"],
                "before_errors": before_errors,
                "after_errors": after_errors,
                "before_accuracy": before_accuracy,
                "after_accuracy": after_accuracy,
                "fixed": before_errors - after_errors,
                "cost": retried_cost,
            })
                
        except Exception as e:
            console.print(f"[red]Failed {m['short_name']}: {e}[/red]")
            if ckpt.checkpoint_path.exists():
                ckpt.checkpoint_path.unlink()
    
    # Show summary
    if retry_results:
        summary = Table(title="📊 Retry Summary")
        summary.add_column("Model", style="cyan")
        summary.add_column("Errors", justify="center")
        summary.add_column("Fixed", justify="center")
        summary.add_column("Accuracy", justify="center")
        summary.add_column("Cost", justify="right")
        
        total_cost = 0
        for r in retry_results:
            errors_str = f"{r['before_errors']} → {r['after_errors']}"
            fixed_str = f"[green]+{r['fixed']}[/green]" if r['fixed'] > 0 else f"[yellow]{r['fixed']}[/yellow]"
            acc_before = f"{r['before_accuracy']:.1%}"
            acc_after = f"{r['after_accuracy']:.1%}"
            if r['after_accuracy'] > r['before_accuracy']:
                acc_str = f"{acc_before} → [green]{acc_after}[/green]"
            else:
                acc_str = f"{acc_before} → {acc_after}"
            
            cost_str = f"${r['cost']:.4f}"
            total_cost += r['cost']
            
            summary.add_row(r["model"], errors_str, fixed_str, acc_str, cost_str)
        
        console.print()
        console.print(summary)
        console.print(f"\n💰 Total retry cost: [bold]${total_cost:.4f}[/bold]")
    
    console.print(f"\n✅ Retry complete! Run [bold]export[/bold] to update frontend.")


# ============================================================================
# UD Slovak SNK Benchmark Commands
# ============================================================================

@evaluate_app.command("ud")
def evaluate_ud(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to evaluate (from config/models.py)"),
    report_only: bool = typer.Option(False, "--report", "-r", help="Show results only"),
):
    """Run UD Slovak SNK benchmark (POS, Lemma, DEP) on curated 32-sentence dataset."""
    import asyncio
    from rich.console import Console
    from rich.table import Table
    from config.models import MODELS
    
    console = Console()
    
    # Report mode
    if report_only:
        if not UD_RESULTS_DIR.exists():
            console.print("[red]❌ No UD results found[/red]")
            raise typer.Exit(1)
        
        table = Table(title="📊 UD Slovak SNK Results")
        table.add_column("Model", style="cyan")
        table.add_column("Avg", justify="right", style="bold")
        table.add_column("POS", justify="right")
        table.add_column("Lemma", justify="right")
        table.add_column("DEP", justify="right")
        table.add_column("Cost", justify="right", style="green")
        
        for f in sorted(UD_RESULTS_DIR.glob("*.json")):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                table.add_row(
                    data.get("model_name", "?").split("/")[-1],
                    f"{data.get('accuracy', 0):.1%}",
                    f"{data.get('pos_accuracy', 0):.1%}",
                    f"{data.get('lemma_accuracy', 0):.1%}",
                    f"{data.get('dep_accuracy', 0):.1%}",
                    f"${data.get('total_cost_usd', 0):.4f}",
                )
            except:
                pass
        
        console.print(table)
        raise typer.Exit(0)
    
    # Import runner
    from src.evaluation.ud_runner import run_benchmark
    
    # Get models to run
    if model:
        if model not in MODELS:
            console.print(f"[red]❌ Unknown model: {model}[/red]")
            console.print(f"[dim]Available: {', '.join(MODELS.keys())}[/dim]")
            raise typer.Exit(1)
        models_to_run = [model]
    else:
        models_to_run = list(MODELS.keys())
    
    console.print(f"\n{'='*60}")
    console.print(f"[bold]UD Slovak SNK Benchmark[/bold]")
    console.print(f"Models: {len(models_to_run)}")
    console.print(f"Tasks: POS, LEMMA, DEP")
    console.print(f"Dataset: Curated (32 sentences)")
    console.print(f"{'='*60}\n")
    
    for m in models_to_run:
        try:
            asyncio.run(run_benchmark(m))
        except Exception as e:
            console.print(f"[red]❌ {m}: {str(e)[:80]}[/red]")
        console.print()
    
    console.print("[green]✅ Done! Use --report to see all results.[/green]")


if __name__ == "__main__":
    app()
