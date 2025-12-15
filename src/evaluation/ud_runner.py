"""
UD Slovak SNK Benchmark - POS Tagging, Lemmatization, Dependency Parsing.
Implementation with checkpoint support for resumable execution.
Uses plain text responses with strong prompting (no structured outputs).
"""
import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import tracing_context
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from evaluation.ud_parser import Token, Sentence
from utils.llm import get_cost
from config.models import MODELS


# ============================================================================
# CONFIG
# ============================================================================

RESULTS_DIR = Path("data/results/ud_snk")
CHECKPOINT_DIR = Path("data/checkpoints/ud_snk")
BENCHMARK_PATH = Path("data/processed/ud_snk/benchmark.json")

SYSTEM = """Si expert na slovenský jazyk a syntax. 
DÔLEŽITÉ: Odpovedaj PRESNE podľa formátu v inštrukciách. Žiadne vysvetlenia, žiadny markdown, len požadovaný výstup."""


# ============================================================================
# PROMPTS (strong formatting instructions)
# ============================================================================

PROMPTS = {
    "pos": """Urči slovný druh (POS tag) pre KAŽDÉ slovo vo vete.

POVOLENÉ ZNAČKY: NOUN, VERB, ADJ, ADV, PRON, DET, ADP, AUX, CCONJ, SCONJ, PART, NUM, PROPN, INTJ, PUNCT, SYM, X

Veta: {text}

Slová ({count}):
{numbered}

FORMÁT ODPOVEDE: Napíš PRESNE {count} značiek, každú na nový riadok. Nič iné!

Príklad pre 3 slová:
NOUN
VERB
PUNCT""",

    "lemma": """Urči základný tvar (lemu) pre KAŽDÉ slovo vo vete.
Lema = slovníkový tvar (psov→pes, robím→robiť, krásnej→krásny, bol→byť).

Veta: {text}

Slová ({count}):
{numbered}

FORMÁT ODPOVEDE: Napíš PRESNE {count} lem, každú na nový riadok. Nič iné!

Príklad pre 3 slová:
dom
byť
.""",

    "dep": """Urči syntaktickú závislosť pre KAŽDÉ slovo vo vete.
HEAD = číslo slova, na ktorom závisí aktuálne slovo (0 = koreň vety)
DEPREL = typ vzťahu (root, nsubj, obj, obl, nmod, amod, advmod, det, case, punct, conj, cc, mark, cop, aux, ...)

Veta: {text}

Slová ({count}):
{numbered}

FORMÁT ODPOVEDE: Napíš PRESNE {count} riadkov vo formáte "HEAD,DEPREL". Nič iné!

Príklad pre 3 slová:
2,nsubj
0,root
2,punct"""
}


# ============================================================================
# RESPONSE PARSING
# ============================================================================

def parse_response(response_text: str, task: str, expected_count: int) -> List[str]:
    """Parse plain text response into list of predictions."""
    # Clean response
    text = response_text.strip()
    
    # Remove markdown code blocks if present
    text = re.sub(r'```[a-z]*\n?', '', text)
    text = re.sub(r'```', '', text)
    
    # Split by newlines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # For POS, also try comma/space separated if not enough lines
    if len(lines) < expected_count and task == "pos":
        # Try comma separated
        if ',' in text:
            lines = [t.strip() for t in text.split(',') if t.strip()]
        # Try space separated
        elif len(lines) == 1:
            lines = text.split()
    
    # For lemma, similar fallback
    if len(lines) < expected_count and task == "lemma":
        if ',' in text:
            lines = [t.strip() for t in text.split(',') if t.strip()]
    
    # For dep, ensure proper format HEAD,DEPREL
    if task == "dep":
        cleaned = []
        for line in lines:
            # Try to extract HEAD,DEPREL pattern
            match = re.search(r'(\d+)\s*[,:\s]\s*(\w+)', line)
            if match:
                cleaned.append(f"{match.group(1)},{match.group(2)}")
            else:
                cleaned.append(line)
        lines = cleaned
    
    return lines


# ============================================================================
# CHECKPOINT MANAGER
# ============================================================================

class UDCheckpointManager:
    """Manages checkpoint saving/loading for UD evaluation progress."""
    
    def __init__(self, model_name: str):
        self.model_short = model_name.split("/")[-1]
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path = CHECKPOINT_DIR / f"{self.model_short}.json"
    
    def load(self) -> Dict:
        """Load checkpoint if exists. Returns dict with completed results."""
        if not self.checkpoint_path.exists():
            return {"results": {}, "model_name": "", "timestamp": ""}
        
        try:
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load checkpoint: {e}")
            return {"results": {}, "model_name": "", "timestamp": ""}
    
    def save(self, results: Dict, model_name: str):
        """Save checkpoint with current results. Key format: 'task:sent_id'"""
        data = {
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }
        
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def delete(self):
        """Delete checkpoint after successful completion."""
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()


# ============================================================================
# DATA LOADING
# ============================================================================

def load_benchmark() -> list[Sentence]:
    """Load curated benchmark."""
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        data = json.load(f)
    
    sentences = []
    for s in data["sentences"]:
        tokens = [Token(t["id"], t["form"], t["lemma"], t["upos"], "_", "_", t["head"], t["deprel"], "_", "_") 
                  for t in s["tokens"]]
        sentences.append(Sentence(s["sent_id"], s["text"], tokens))
    return sentences


def get_gold(task: str, sentence: Sentence) -> list[str]:
    """Get gold labels for a sentence."""
    words = sentence.words
    if task == "pos":
        return [t.upos for t in words]
    elif task == "lemma":
        return [t.lemma for t in words]
    else:  # dep
        return [f"{t.head},{t.deprel}" for t in words]


# ============================================================================
# EVALUATION
# ============================================================================

async def evaluate_sentence(llm, task: str, sentence: Sentence) -> dict:
    """Evaluate single sentence, return accuracy and cost."""
    words = sentence.words
    gold = get_gold(task, sentence)
    expected_count = len(words)
    
    # Build prompt
    numbered = "\n".join(f"{i+1}. {w.form}" for i, w in enumerate(words))
    prompt = PROMPTS[task].format(
        text=sentence.text,
        numbered=numbered,
        count=expected_count
    )
    
    try:
        start = time.time()
        # Disable LangSmith tracing to prevent rate limit errors
        with tracing_context(enabled=False):
            result = await llm.ainvoke([SystemMessage(content=SYSTEM), HumanMessage(content=prompt)])

        latency = (time.time() - start) * 1000
        
        response_text = result.content if hasattr(result, 'content') else str(result)
        cost = get_cost(result)
        
        # Parse response
        preds = parse_response(response_text, task, expected_count)
        
        # Pad/trim to match gold length
        preds = (preds + [""] * expected_count)[:expected_count]
        correct = sum(1 for g, p in zip(gold, preds) if g == p)
        
        return {"correct": correct, "total": len(gold), "cost": cost, "latency": latency, "error": None}
    
    except Exception as e:
        return {"correct": 0, "total": len(gold), "cost": 0, "latency": 0, "error": str(e)[:100]}


async def run_benchmark(model_name: str, force: bool = False) -> dict:
    """Run full benchmark (POS, Lemma, DEP) with checkpoint support."""
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}. Use one from config/models.py")
    
    model_short = model_name.split("/")[-1]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / f"{model_short}.json"
    
    # Initialize checkpoint manager
    checkpoint = UDCheckpointManager(model_name)
    
    # Check if result already exists AND checkpoint doesn't exist (= completed cleanly)
    if result_path.exists() and not checkpoint.checkpoint_path.exists() and not force:
        print(f"⏩ Skipping {model_short} (already complete). Use --force to re-run.")
        with open(result_path, encoding="utf-8") as f:
            return json.load(f)
    
    # Load checkpoint if exists (resuming interrupted run)
    checkpoint_data = checkpoint.load()
    completed_results: Dict[str, dict] = checkpoint_data.get("results", {})
    
    if completed_results:
        print(f"   📂 Resuming from checkpoint: {len(completed_results)} items done")
    
    sentences = load_benchmark()
    llm = MODELS[model_name]  # Use LLM directly, no structured output wrapper
    sem = asyncio.Semaphore(16)
    
    # Build list of pending work: (task, sentence) combinations
    tasks = ["pos", "lemma", "dep"]
    all_work = [(task, s) for task in tasks for s in sentences]
    pending_work = [(t, s) for t, s in all_work if f"{t}:{s.sent_id}" not in completed_results]
    
    total_items = len(sentences) * 3
    done_items = total_items - len(pending_work)
    
    # Progress bar
    pbar = tqdm(total=total_items, initial=done_items, desc=model_short, leave=False)
    
    # Lock for thread-safe checkpoint saving
    checkpoint_lock = asyncio.Lock()
    
    async def eval_one(task: str, sentence: Sentence):
        key = f"{task}:{sentence.sent_id}"
        
        async with sem:
            result = await evaluate_sentence(llm, task, sentence)
        
        # Save to checkpoint immediately (thread-safe)
        async with checkpoint_lock:
            completed_results[key] = result
            checkpoint.save(completed_results, model_name)
        
        pbar.update(1)
        return key, result
    
    # Run all pending work concurrently
    if pending_work:
        await asyncio.gather(*[eval_one(t, s) for t, s in pending_work])
    
    pbar.close()
    
    # Aggregate results by task
    task_results = {}
    for task in tasks:
        task_items = [v for k, v in completed_results.items() if k.startswith(f"{task}:")]
        
        total_correct = sum(r["correct"] for r in task_items)
        total_tokens = sum(r["total"] for r in task_items)
        total_cost = sum(r["cost"] for r in task_items)
        latencies = [r["latency"] for r in task_items if r["latency"] > 0]
        errors = sum(1 for r in task_items if r["error"])
        first_error = next((r["error"] for r in task_items if r["error"]), None)
        
        task_results[task] = {
            "task": task,
            "accuracy": total_correct / total_tokens if total_tokens else 0,
            "correct": total_correct,
            "total": total_tokens,
            "cost_usd": total_cost,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "errors": errors,
            "first_error": first_error
        }
    
    total_cost = sum(r["cost_usd"] for r in task_results.values())
    total_errors = sum(r["errors"] for r in task_results.values())
    
    # Print results
    for task in tasks:
        r = task_results[task]
        if r["errors"] >= 5:
            err_short = r["first_error"][:150] if r["first_error"] else "Unknown"
            print(f"  ❌ {task.upper()}: Failed - {err_short}")
        else:
            print(f"  ✅ {task.upper()}: {r['accuracy']:.1%} | ${r['cost_usd']:.4f}")
    
    # Average accuracy across all tasks
    avg_accuracy = (task_results["pos"]["accuracy"] + task_results["lemma"]["accuracy"] + task_results["dep"]["accuracy"]) / 3
    
    output = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "total_sentences": len(sentences),
        "accuracy": avg_accuracy,
        "pos_accuracy": task_results["pos"]["accuracy"],
        "lemma_accuracy": task_results["lemma"]["accuracy"],
        "dep_accuracy": task_results["dep"]["accuracy"],
        "total_cost_usd": total_cost,
        "avg_latency_ms": sum(r["avg_latency_ms"] for r in task_results.values()) / 3,
        "error_count": total_errors,
        "tasks": task_results
    }
    
    # Don't save final result if all tasks failed
    all_failed = all(r["errors"] >= 5 for r in task_results.values())
    if all_failed:
        print(f"⚠️  Not saving - all tasks failed")
        return output
    
    # Save final result
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Delete checkpoint since we completed successfully
    checkpoint.delete()
    
    print(f"💾 {result_path} | Total: ${total_cost:.4f}")
    return output


if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "google/gemini-2.5-flash"
    asyncio.run(run_benchmark(model))
