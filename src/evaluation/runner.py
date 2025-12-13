"""
Evaluation runner for SlovakBench.
Orchestrates LLM evaluation on extracted exam questions.
"""
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import tracing_context
from tqdm import tqdm

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.llm import create_llm, get_cost, print_cost
from evaluation.answer_validator import validate_mcq, validate_short_text


@dataclass
class QuestionResult:
    """Result for a single question."""
    question_id: str
    task_type: str
    model_answer: str
    correct_answer: str
    is_correct: bool
    cost_usd: float = 0.0
    raw_response: str = ""


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
            "results": [
                {
                    "question_id": r.question_id,
                    "task_type": r.task_type,
                    "model_answer": r.model_answer,
                    "correct_answer": r.correct_answer,
                    "is_correct": r.is_correct,
                    "cost_usd": r.cost_usd,
                }
                for r in self.results
            ],
        }


class EvaluationRunner:
    """Run LLM evaluation on exam dataset."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
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
        """Evaluate a single question asynchronously."""
        prompt = self.build_prompt(q, contexts)
        
        try:
            response = await self.llm.ainvoke([system_msg, HumanMessage(content=prompt)])
            raw_response = response.content
            cost = get_cost(response)
        except Exception as e:
            print(f"Error on question {q['id']}: {e}")
            raw_response = ""
            cost = 0.0
        
        model_answer = self.parse_response(raw_response, q["task_type"])
        is_correct = self.validate_answer(q, model_answer)
        
        if q["task_type"] == "mcq":
            correct_answer = q["answer"].get("correct_option", "")
        else:
            correct_answer = ", ".join(q["answer"].get("accepted", [])[:3])
        
        return QuestionResult(
            question_id=q["id"],
            task_type=q["task_type"],
            model_answer=model_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            cost_usd=cost,
            raw_response=raw_response,
        )
    
    def run(self, dataset_path: str, concurrency: int = 32) -> EvaluationResult:
        """Execute evaluation on dataset with concurrent processing."""
        import asyncio
        
        data = self.load_dataset(dataset_path)
        contexts = data.get("contexts", [])
        questions = data.get("questions", [])
        
        system_msg = SystemMessage(content="Si expert na slovenský jazyk. Odpovedaj presne a stručne.")
        
        async def run_all():
            semaphore = asyncio.Semaphore(concurrency)
            pbar = tqdm(total=len(questions), desc=f"{self.model_name.split('/')[-1]}", leave=False)
            
            async def bounded_eval(q):
                async with semaphore:
                    with tracing_context(enabled=False):
                        result = await self._evaluate_question(q, contexts, system_msg)
                    pbar.update(1)
                    return result
            
            tasks = [bounded_eval(q) for q in questions]
            results = await asyncio.gather(*tasks)
            pbar.close()
            return results
        
        results = asyncio.run(run_all())
        
        # Compute stats
        mcq_correct = sum(1 for r in results if r.task_type == "mcq" and r.is_correct)
        mcq_total = sum(1 for r in results if r.task_type == "mcq")
        st_correct = sum(1 for r in results if r.task_type == "short_text" and r.is_correct)
        st_total = sum(1 for r in results if r.task_type == "short_text")
        
        total = len(results)
        correct = sum(1 for r in results if r.is_correct)
        total_cost = sum(r.cost_usd for r in results)
        
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
            results=results,
        )


def save_results(result: EvaluationResult, output_dir: str = "data/results") -> str:
    """Save evaluation results to JSON (overwrites previous for same model)."""
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
            print(f"[{r.question_id}] {status} Model: {r.model_answer} | Correct: {r.correct_answer}")
    else:
        print(f"Dataset not found: {dataset_path}")
