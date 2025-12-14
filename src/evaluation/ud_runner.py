"""
UD Slovak SNK Benchmark - POS Tagging, Lemmatization, Dependency Parsing.
Simple implementation with structured outputs.
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
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
BENCHMARK_PATH = Path("data/processed/ud_snk/benchmark.json")

SYSTEM = "Si expert na slovenský jazyk. Odpovedaj presne podľa inštrukcií."


# ============================================================================
# PROMPTS & RESPONSES
# ============================================================================

class POSResponse(BaseModel):
    tags: list[str] = Field(description="POS tag for each word")

class LemmaResponse(BaseModel):
    lemmas: list[str] = Field(description="Lemma for each word")

class DepResponse(BaseModel):
    deps: list[str] = Field(description="HEAD,DEPREL for each word")


PROMPTS = {
    "pos": """Urči slovný druh pre každé slovo.
Značky: NOUN, VERB, ADJ, ADV, PRON, DET, ADP, AUX, CCONJ, SCONJ, PART, NUM, PROPN, INTJ, PUNCT, SYM, X

Veta: {text}
Slová: {words}

Vráť presne {count} tagov.""",

    "lemma": """Urči základný tvar (lemu) pre každé slovo.
Lema = slovníkový tvar (psov→pes, robím→robiť, krásnej→krásny).

Veta: {text}
Slová: {words}

Vráť presne {count} lem.""",

    "dep": """Urči syntaktickú závislosť pre každé slovo.
Pre každé slovo vráť HEAD,DEPREL kde HEAD je číslo rodiča (0=koreň).

Veta: {text}
Slová: {numbered}

Vráť presne {count} párov HEAD,DEPREL."""
}

RESPONSE_CLASSES = {"pos": POSResponse, "lemma": LemmaResponse, "dep": DepResponse}


# ============================================================================
# DATA LOADING
# ============================================================================

def load_benchmark() -> list[Sentence]:
    """Load curated 32-sentence benchmark."""
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


def get_predictions(task: str, response) -> list[str]:
    """Extract predictions from structured response."""
    if task == "pos":
        return response.tags
    elif task == "lemma":
        return response.lemmas
    else:  # dep
        return response.deps


# ============================================================================
# EVALUATION
# ============================================================================

async def evaluate_sentence(llm, task: str, sentence: Sentence) -> dict:
    """Evaluate single sentence, return accuracy and cost."""
    words = sentence.words
    gold = get_gold(task, sentence)
    
    # Build prompt
    numbered = "\n".join(f"{i+1}. {w.form}" for i, w in enumerate(words))
    prompt = PROMPTS[task].format(
        text=sentence.text,
        words=", ".join(w.form for w in words),
        numbered=numbered,
        count=len(words)
    )
    
    try:
        start = time.time()
        result = await llm.ainvoke([SystemMessage(content=SYSTEM), HumanMessage(content=prompt)])
        latency = (time.time() - start) * 1000
        
        raw = result.get("raw")
        parsed = result.get("parsed")
        cost = get_cost(raw) if raw else 0.0
        
        if not parsed:
            return {"correct": 0, "total": len(gold), "cost": cost, "latency": latency, "error": "No parse"}
        
        preds = get_predictions(task, parsed)
        # Pad/trim to match gold length
        preds = (preds + [""] * len(gold))[:len(gold)]
        correct = sum(1 for g, p in zip(gold, preds) if g == p)
        
        return {"correct": correct, "total": len(gold), "cost": cost, "latency": latency, "error": None}
    
    except Exception as e:
        return {"correct": 0, "total": len(gold), "cost": 0, "latency": 0, "error": str(e)[:100]}


async def run_task(llm, task: str, sentences: list[Sentence], sem: asyncio.Semaphore) -> dict:
    """Run single task on all sentences with shared semaphore."""
    response_class = RESPONSE_CLASSES[task]
    llm_structured = llm.with_structured_output(response_class, include_raw=True)
    
    results = []
    errors = 0
    first_error = None
    
    async def eval_one(s):
        async with sem:
            return await evaluate_sentence(llm_structured, task, s)
    
    for coro in asyncio.as_completed([eval_one(s) for s in sentences]):
        r = await coro
        results.append(r)
        if r["error"]:
            errors += 1
            if not first_error:
                first_error = r["error"]
            if errors >= 5:
                break
    
    # Aggregate
    total_correct = sum(r["correct"] for r in results)
    total_tokens = sum(r["total"] for r in results)
    total_cost = sum(r["cost"] for r in results)
    latencies = [r["latency"] for r in results if r["latency"] > 0]
    
    return {
        "task": task,
        "accuracy": total_correct / total_tokens if total_tokens else 0,
        "correct": total_correct,
        "total": total_tokens,
        "cost_usd": total_cost,
        "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
        "errors": errors,
        "first_error": first_error
    }


async def run_benchmark(model_name: str) -> dict:
    """Run full benchmark (POS, Lemma, DEP) concurrently and save results."""
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}. Use one from config/models.py")
    
    sentences = load_benchmark()
    model_short = model_name.split("/")[-1]
    
    llm = MODELS[model_name]
    sem = asyncio.Semaphore(16)
    
    # Shared progress bar for all 30 requests (10 sentences x 3 tasks)
    pbar = tqdm(total=len(sentences) * 3, desc=model_short, leave=False)
    
    async def run_task_with_progress(task):
        r = await run_task(llm, task, sentences, sem)
        pbar.update(len(sentences))
        return r
    
    # Run all 3 tasks concurrently
    task_results = await asyncio.gather(
        run_task_with_progress("pos"),
        run_task_with_progress("lemma"),
        run_task_with_progress("dep")
    )
    pbar.close()
    
    results = {r["task"]: r for r in task_results}
    total_cost = sum(r["cost_usd"] for r in task_results)
    total_errors = sum(r["errors"] for r in task_results)
    
    # Print results
    for task in ["pos", "lemma", "dep"]:
        r = results[task]
        if r["errors"] >= 5:
            err_short = r["first_error"][:150] if r["first_error"] else "Unknown"
            print(f"  ❌ {task.upper()}: Failed - {err_short}")
        else:
            print(f"  ✅ {task.upper()}: {r['accuracy']:.1%} | ${r['cost_usd']:.4f}")
    
    # Average accuracy across all tasks
    avg_accuracy = (results["pos"]["accuracy"] + results["lemma"]["accuracy"] + results["dep"]["accuracy"]) / 3
    
    output = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "total_sentences": len(sentences),
        "accuracy": avg_accuracy,  # Average of all 3 tasks
        "pos_accuracy": results["pos"]["accuracy"],
        "lemma_accuracy": results["lemma"]["accuracy"],
        "dep_accuracy": results["dep"]["accuracy"],
        "total_cost_usd": total_cost,
        "avg_latency_ms": sum(r["avg_latency_ms"] for r in results.values()) / 3,
        "error_count": total_errors,
        "tasks": results
    }
    
    # Don't save if all tasks failed
    all_failed = all(r["errors"] >= 5 for r in results.values())
    if all_failed:
        print(f"⚠️  Not saving - all tasks failed")
        return output
    
    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{model_short}.json"
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 {path} | Total: ${total_cost:.4f}")
    return output


if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "google/gemini-2.5-flash"
    asyncio.run(run_benchmark(model))
