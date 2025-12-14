"""
Evaluation runner for SlovakBench.
Orchestrates LLM evaluation on extracted exam questions.

Features:
- Async concurrent processing with semaphore
- Per-question timeout (prevents hanging)
- Checkpoint saving (resume after interruption)
- Graceful error handling
"""
import asyncio
import time
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import tracing_context
from tqdm import tqdm

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.llm import create_llm, get_cost
from evaluation.answer_validator import validate_mcq, validate_short_text

# Configuration
DEFAULT_TIMEOUT = 300  # 5 minutes per question
MAX_ERROR_RATE = 0.20  # Don't save if > 20% errors
CHECKPOINT_DIR = Path("data/checkpoints")


@dataclass
class QuestionResult:
    """Result for a single question."""
    question_id: str
    task_type: str
    model_answer: str
    correct_answer: str
    is_correct: bool
    cost_usd: float = 0.0
    latency_ms: float = 0.0  # Response time in milliseconds
    raw_response: str = ""
    error: Optional[str] = None


@dataclass
class EvaluationResult:
    """Complete evaluation result."""
    model_name: str
    dataset_path: str
    timestamp: str
    total_questions: int
    correct_count: int
    accuracy: float
    total_cost_usd: float = 0.0
    mcq_accuracy: Optional[float] = None
    short_text_accuracy: Optional[float] = None
    avg_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    error_count: int = 0
    results: List[QuestionResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "model_name": self.model_name,
            "dataset_path": self.dataset_path,
            "timestamp": self.timestamp,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "accuracy": self.accuracy,
            "total_cost_usd": self.total_cost_usd,
            "mcq_accuracy": self.mcq_accuracy,
            "short_text_accuracy": self.short_text_accuracy,
            "avg_latency_ms": self.avg_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "error_count": self.error_count,
            "results": [
                {
                    "question_id": r.question_id,
                    "task_type": r.task_type,
                    "model_answer": r.model_answer,
                    "correct_answer": r.correct_answer,
                    "is_correct": r.is_correct,
                    "cost_usd": r.cost_usd,
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


class CheckpointManager:
    """Manages checkpoint saving/loading for evaluation progress."""
    
    def __init__(self, model_name: str, dataset_path: str):
        self.model_short = model_name.split("/")[-1]
        self.dataset_name = Path(dataset_path).stem
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path = CHECKPOINT_DIR / f"{self.model_short}_{self.dataset_name}.json"
    
    def load(self) -> Dict[str, QuestionResult]:
        """Load checkpoint if exists. Returns dict of question_id -> result."""
        if not self.checkpoint_path.exists():
            return {}
        
        try:
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            results = {}
            for r in data.get("results", []):
                results[r["question_id"]] = QuestionResult(
                    question_id=r["question_id"],
                    task_type=r["task_type"],
                    model_answer=r["model_answer"],
                    correct_answer=r["correct_answer"],
                    is_correct=r["is_correct"],
                    cost_usd=r.get("cost_usd", 0.0),
                    latency_ms=r.get("latency_ms", 0.0),
                    raw_response=r.get("raw_response", ""),
                    error=r.get("error"),
                )
            return results
        except Exception as e:
            print(f"⚠️  Could not load checkpoint: {e}")
            return {}
    
    def save(self, results: List[QuestionResult], model_name: str, dataset_path: str):
        """Save checkpoint with current results."""
        data = {
            "model_name": model_name,
            "dataset_path": dataset_path,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "question_id": r.question_id,
                    "task_type": r.task_type,
                    "model_answer": r.model_answer,
                    "correct_answer": r.correct_answer,
                    "is_correct": r.is_correct,
                    "cost_usd": r.cost_usd,
                    "latency_ms": r.latency_ms,
                    "raw_response": r.raw_response,
                    "error": r.error,
                }
                for r in results
            ],
        }
        
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def delete(self):
        """Delete checkpoint after successful completion."""
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()


class EvaluationRunner:
    """Run LLM evaluation on exam dataset."""
    
    def __init__(self, model_name: str, timeout: int = DEFAULT_TIMEOUT):
        self.model_name = model_name
        self.timeout = timeout
        self.llm = create_llm(model_name=model_name)
    
    def load_dataset(self, dataset_path: str) -> Dict:
        """Load processed exam JSON."""
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def build_prompt(self, question: Dict, contexts: List[Dict]) -> str:
        """Build prompt for a single question."""
        # Find relevant context if referenced
        context_text = ""
        if question.get("context_id"):
            for ctx in contexts:
                if ctx["id"] == question["context_id"]:
                    context_text = f"### Kontext\n{ctx['text']}\n\n"
                    break
        
        # Build question text
        q_text = question["question"]
        
        if question["task_type"] == "mcq":
            options = question["options"]
            options_text = "\n".join(f"{k}) {v}" for k, v in options.items())
            prompt = f"""{context_text}### Otázka
{q_text}

### Možnosti
{options_text}

Odpovedz IBA písmenom správnej odpovede (A, B, C alebo D). Nič viac."""
        else:
            prompt = f"""{context_text}### Otázka
{q_text}

DÔLEŽITÉ: Odpoveď je automaticky hodnotená systémom, ktorý porovnáva presne slová.
- Napíš len jedno slovo alebo niekoľko slov
- BEZ vysvetlení, BEZ zátvoriek, BEZ dodatkov
- Presne to čo sa pýta, nič viac

Príklad: "epiteton" (nie "epiteton (básnický prívlastok)")"""
        
        return prompt
    
    def parse_response(self, response: str, task_type: str) -> str:
        """Extract answer from model response."""
        response = response.strip()
        
        if task_type == "mcq":
            # Extract letter A/B/C/D
            for char in response.upper():
                if char in "ABCD":
                    return char
            return response[:1].upper() if response else ""
        else:
            # Short text - return as-is (will be normalized during validation)
            return response
    
    def validate_answer(self, question: Dict, model_answer: str) -> bool:
        """Check if model answer is correct."""
        answer = question["answer"]
        
        if question["task_type"] == "mcq":
            correct = answer.get("correct_option", "")
            return validate_mcq(model_answer, correct)
        else:
            accepted = answer.get("accepted", [])
            steps = answer.get("normalize", ["trim", "casefold"])
            return validate_short_text(model_answer, accepted, steps)
    
    async def _evaluate_question(self, q: Dict, contexts: List[Dict], system_msg) -> QuestionResult:
        """Evaluate a single question with timeout."""
        prompt = self.build_prompt(q, contexts)
        
        # Determine correct answer for logging
        if q["task_type"] == "mcq":
            correct_answer = q["answer"].get("correct_option", "")
        else:
            correct_answer = ", ".join(q["answer"].get("accepted", [])[:3])
        
        cost = 0.0
        
        # Simple retry loop
        max_retries = 3
        
        for attempt in range(max_retries + 1):
            start_time = time.perf_counter()
            try:
                # Apply timeout to the LLM call
                response = await asyncio.wait_for(
                    self.llm.ainvoke([system_msg, HumanMessage(content=prompt)]),
                    timeout=self.timeout
                )
                latency_ms = (time.perf_counter() - start_time) * 1000
                raw_response = response.content
                cost = get_cost(response)
                error = None
                break  # Success
                
            except asyncio.TimeoutError:
                latency_ms = (time.perf_counter() - start_time) * 1000
                raw_response = ""
                error = f"Timeout after {self.timeout}s"
                break
                
            except Exception as e:
                err_str = str(e) or type(e).__name__
                err_type = type(e).__name__
                
                # Check for rate limits or server errors
                is_retryable = "429" in err_str or "500" in err_str or "503" in err_str or "rate limit" in err_str.lower()
                
                if is_retryable and attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                # Build informative error message
                latency_ms = (time.perf_counter() - start_time) * 1000
                raw_response = ""
                
                # Extract useful info from error + keep some raw for debugging
                raw_snippet = err_str[:250] if len(err_str) > 250 else err_str
                
                if "429" in err_str:
                    error = f"{err_type}: Rate limit (429) | {raw_snippet}"
                elif "500" in err_str or "502" in err_str or "503" in err_str:
                    error = f"{err_type}: Server error (5xx) | {raw_snippet}"
                elif "Connection" in err_str or "connection" in err_str:
                    error = f"{err_type}: Connection failed | {raw_snippet}"
                elif "timeout" in err_str.lower():
                    error = f"{err_type}: Timed out | {raw_snippet}"
                else:
                    error = f"{err_type}: {err_str[:250]}"
                
                break
        
        model_answer = self.parse_response(raw_response, q["task_type"])
        is_correct = self.validate_answer(q, model_answer) if not error else False
        
        return QuestionResult(
            question_id=q["id"],
            task_type=q["task_type"],
            model_answer=model_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            cost_usd=cost,
            latency_ms=latency_ms,
            raw_response=raw_response,
            error=error,
        )
    
    def run(self, dataset_path: str, concurrency: int = 32, resume: bool = True) -> EvaluationResult:
        """Execute evaluation on dataset with concurrent processing and checkpointing."""
        import asyncio
        
        data = self.load_dataset(dataset_path)
        contexts = data.get("contexts", [])
        questions = data.get("questions", [])
        
        # Initialize checkpoint manager
        checkpoint = CheckpointManager(self.model_name, dataset_path)
        
        # Load existing progress if resuming
        completed_results: Dict[str, QuestionResult] = {}
        if resume:
            completed_results = checkpoint.load()
            if completed_results:
                print(f"   📂 Resuming from checkpoint: {len(completed_results)}/{len(questions)} done")
        
        # Filter out already completed questions
        pending_questions = [q for q in questions if q["id"] not in completed_results]
        
        system_msg = SystemMessage(content="Si expert na slovenský jazyk. Odpovedaj presne a stručne.")
        
        # Results list (will include both resumed and new)
        all_results: List[QuestionResult] = list(completed_results.values())
        
        async def run_all():
            nonlocal all_results
            
            if not pending_questions:
                return
            
            semaphore = asyncio.Semaphore(concurrency)
            pbar = tqdm(
                total=len(questions),
                initial=len(completed_results),
                desc=f"{self.model_name.split('/')[-1]}",
                leave=False
            )
            
            # Lock for thread-safe checkpoint saving
            checkpoint_lock = asyncio.Lock()
            
            async def bounded_eval(q):
                async with semaphore:
                    with tracing_context(enabled=False):
                        result = await self._evaluate_question(q, contexts, system_msg)
                    
                    # Add result and save checkpoint (thread-safe)
                    async with checkpoint_lock:
                        all_results.append(result)
                        # Save checkpoint every question for safety
                        checkpoint.save(all_results, self.model_name, dataset_path)
                    
                    pbar.update(1)
                    return result
            
            tasks = [bounded_eval(q) for q in pending_questions]
            await asyncio.gather(*tasks)
            pbar.close()
        
        asyncio.run(run_all())
        
        # Compute stats
        mcq_correct = sum(1 for r in all_results if r.task_type == "mcq" and r.is_correct)
        mcq_total = sum(1 for r in all_results if r.task_type == "mcq")
        st_correct = sum(1 for r in all_results if r.task_type == "short_text" and r.is_correct)
        st_total = sum(1 for r in all_results if r.task_type == "short_text")
        
        total = len(all_results)
        correct = sum(1 for r in all_results if r.is_correct)
        total_cost = sum(r.cost_usd for r in all_results)
        
        # Compute latency stats
        latencies = [r.latency_ms for r in all_results if r.latency_ms > 0]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            sorted_latencies = sorted(latencies)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p95_latency = sorted_latencies[min(p95_idx, len(sorted_latencies) - 1)]
        else:
            avg_latency = None
            p95_latency = None
        
        # Count errors/timeouts
        errors = sum(1 for r in all_results if r.error)
        if errors > 0:
            print(f"   ⚠️  {errors} questions had errors/timeouts")
        
        # Delete checkpoint on success
        checkpoint.delete()
        
        return EvaluationResult(
            model_name=self.model_name,
            dataset_path=dataset_path,
            timestamp=datetime.now().isoformat(),
            total_questions=total,
            correct_count=correct,
            accuracy=correct / total if total > 0 else 0.0,
            total_cost_usd=total_cost,
            mcq_accuracy=mcq_correct / mcq_total if mcq_total > 0 else None,
            short_text_accuracy=st_correct / st_total if st_total > 0 else None,
            avg_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            error_count=errors,
            results=all_results,
        )


def save_results(result: EvaluationResult, output_dir: str = "data/results") -> Optional[str]:
    """Save evaluation results to JSON. Returns None if too many errors."""
    # Guard: don't save if error rate > MAX_ERROR_RATE
    if result.total_questions > 0:
        error_rate = result.error_count / result.total_questions
        if error_rate > MAX_ERROR_RATE:
            print(f"   ❌ Skipping save: {result.error_count}/{result.total_questions} errors ({error_rate:.0%} > {MAX_ERROR_RATE:.0%} threshold)")
            return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Filename is just model name - overwrites previous result
    model_short = result.model_name.split("/")[-1]
    filename = f"{model_short}.json"
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    
    return output_path


if __name__ == "__main__":
    # Quick test
    dataset_path = "data/processed/mcq/debug_2025.json"
    model_name = "google/gemini-2.5-flash-lite-preview-09-2025"
    
    if os.path.exists(dataset_path):
        runner = EvaluationRunner(model_name=model_name)
        result = runner.run(dataset_path)
        
        print(f"\n{'='*50}")
        print(f"Model: {result.model_name}")
        print(f"Total: {result.total_questions} questions")
        print(f"Correct: {result.correct_count}")
        print(f"Accuracy: {result.accuracy:.1%}")
        if result.mcq_accuracy is not None:
            print(f"MCQ Accuracy: {result.mcq_accuracy:.1%}")
        if result.short_text_accuracy is not None:
            print(f"Short Text Accuracy: {result.short_text_accuracy:.1%}")
        
        # Save results
        output_path = save_results(result)
        print(f"\n✓ Results saved to {output_path}")
        
        # Show first 5 results
        print(f"\n--- Sample Results ---")
        for r in result.results[:5]:
            status = "✓" if r.is_correct else "✗"
            err = f" [{r.error}]" if r.error else ""
            print(f"[{r.question_id}] {status} Model: {r.model_answer} | Correct: {r.correct_answer}{err}")
    else:
        print(f"Dataset not found: {dataset_path}")
