"""MCQ Parser - Extracts exam questions from PDF using LLM."""
import json
import base64
import os
import sys
from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.llm import create_llm, get_cost, print_cost


# --- Pydantic Models ---

class Context(BaseModel):
    """Samostatná ukážka/pasáž s markdown formátovaním."""
    id: str = Field(description="Context ID, e.g. 'ukazka_1', 'text_a'")
    text: str = Field(description="Full text with markdown formatting: **bold**, _italic_, __underline__ for highlighting")


class MCQAnswer(BaseModel):
    """Answer for MCQ question."""
    correct_option: str = Field(description="The correct option letter: A, B, C, or D")


class ShortTextAnswer(BaseModel):
    """Answer for short_text question with accepted variants."""
    accepted: List[str] = Field(description="List of all acceptable answer forms")
    normalize: List[str] = Field(
        default=["trim", "casefold"],
        description="Normalization steps: trim, casefold, collapse_ws, remove_punct, remove_diacritics, numeric_only"
    )


class Question(BaseModel):
    """A single question extracted from the exam."""
    id: str = Field(description="Question ID (e.g., '01', '15')")
    task_type: Literal["mcq", "short_text"] = Field(description="mcq or short_text")
    context_id: Optional[str] = Field(default=None, description="Reference to context ID if question uses a passage")
    question: str = Field(description="The question text (without the context, just the question itself)")
    options: Optional[Dict[str, str]] = Field(default=None, description="For mcq: dict with keys A,B,C,D. For short_text: null")
    answer: Union[MCQAnswer, ShortTextAnswer] = Field(description="The correct answer")


class MCQExamExtraction(BaseModel):
    """Extracted exam with separated contexts and questions."""
    contexts: List[Context] = Field(default=[], description="All passages/excerpts referenced by questions")
    questions: List[Question] = Field(description="List of all extracted questions")


# --- Helper ---

def load_pdf_as_base64(pdf_path: str) -> str:
    """Load a PDF file and return its base64 encoding."""
    with open(pdf_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


# --- Extraction Functions ---

def extract_answers_from_key(
    test_pdf_path: str,
    key_pdf_path: str,
    model_name: str,
) -> str:
    """
    Step 1: Extract correct answers from key PDF matching the test code.
    Returns markdown with answers that will be passed to main extraction.
    """
    test_base64 = load_pdf_as_base64(test_pdf_path)
    key_base64 = load_pdf_as_base64(key_pdf_path)
    
    prompt = """Look at these two PDFs:
1. TEST PDF - find the test code (e.g., "Test 25 1403" or similar number in header/footer)
2. KEY PDF - contains answer key with multiple test versions in columns, plus Poznámky (notes)

Your task:
1. Find the test code from the TEST PDF
2. Find the matching column in the KEY PDF
3. Output the correct answers with notes in markdown format

Output format:
```
Test code: [test code]

## MCQ Answers (A/B/C/D)
01: A
02: B
...

## Short Text Answers
06: pás | Poznámka: Slovo musí byť vypísané pravopisne správne
07: chôdze | Poznámka: Uznať aj s adekvátnou predložkou
...
```

Include ALL questions. For short text:
- Copy all accepted variants separated by /
- Include the Poznámka (note) if present - it explains validation rules"""

    llm = create_llm(model_name, temperature=0.5)
    
    message = HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{test_base64}"}},
        {"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{key_base64}"}},
    ])
    
    response = llm.invoke([message])
    
    print(f"📋 Step 1: Extracted answers")
    print_cost(response)
    print(f"\n{response.content[:500]}...\n")
    
    return response.content


def extract_mcq_from_pdf(
    test_pdf_path: str,
    key_pdf_path: str,
    model_name: str,
) -> MCQExamExtraction:
    """
    Extract MCQ questions from a test PDF and pair with correct answers from key PDF.
    Uses two-step extraction: first extracts answers, then full questions.
    """
    # Step 1: Extract answers from key
    answers_markdown = extract_answers_from_key(test_pdf_path, key_pdf_path, model_name)
    
    # Step 2: Extract full questions with pre-extracted answers
    test_base64 = load_pdf_as_base64(test_pdf_path)

    prompt = f"""Extract all questions from the EXAM PDF.

I have already extracted the correct answers for you:
---
{answers_markdown}
---

## CONTEXTS
Extract all passages/excerpts into `contexts` array:
- `id`: unique identifier (e.g., "ukazka_1", "text_a")
- `text`: full passage text with PRESERVED FORMATTING:
  - **bold** for bold/tučné text
  - _italic_ for italic/kurzíva text  
  - __underline__ for underlined/podčiarknuté text
  - IMPORTANT: if words are highlighted in the PDF, mark them!

## QUESTIONS
- `id`: question number ("01", "02", ...)
- `context_id`: reference to context id, or null if standalone
- `question`: the question text itself
- `task_type`: "mcq" if has A/B/C/D options, "short_text" if written answer
- `options`: for mcq only: {{"A": "...", "B": "...", "C": "...", "D": "..."}}
- `answer`: use the pre-extracted answers above
  - For mcq: {{"correct_option": "A"}}
  - For short_text: {{"accepted": ["variant1", "variant2"], "normalize": ["trim", "casefold"]}}

Normalize options: trim, casefold, collapse_ws, remove_punct, remove_diacritics, numeric_only"""

    llm = create_llm(model_name)
    structured_llm = llm.with_structured_output(MCQExamExtraction, include_raw=True)
    
    message = HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{test_base64}"}},
    ])
    
    result = structured_llm.invoke([message])
    
    raw = result.get("raw")
    if raw:
        print_cost(raw, "Step 2")
    
    parsed = result.get("parsed")
    if parsed:
        print(f"  Contexts: {len(parsed.contexts)}, Questions: {len(parsed.questions)}")
        return parsed
    else:
        raise ValueError(f"Failed to parse response")


# --- Main ---

if __name__ == "__main__":
    MODEL = "openai/gpt-5.2"
    
    test_pdf_path = "data/raw/mcq/test_2025.pdf"
    key_pdf_path = "data/raw/mcq/kluc_2025.pdf"
    
    if os.path.exists(test_pdf_path) and os.path.exists(key_pdf_path):
        print(f"Extracting from {test_pdf_path} + {key_pdf_path}...")
        
        extraction = extract_mcq_from_pdf(test_pdf_path, key_pdf_path, MODEL)
        
        print(f"\n✓ Extracted {len(extraction.contexts)} contexts, {len(extraction.questions)} questions.")
        
        # Show first 3 contexts
        print("\n--- CONTEXTS ---")
        for ctx in extraction.contexts[:3]:
            preview = ctx.text[:100].replace('\n', ' ')
            print(f"  [{ctx.id}] {preview}...")
        
        # Show first 3 questions
        print("\n--- QUESTIONS ---")
        for q in extraction.questions[:3]:
            print(f"\n[{q.id}] ({q.task_type}) {q.question[:80]}...")
            if q.context_id:
                print(f"  Context: {q.context_id}")
            if hasattr(q.answer, 'correct_option'):
                print(f"  Answer: {q.answer.correct_option}")
            else:
                print(f"  Accepted: {q.answer.accepted}")
        
        # Save to processed
        os.makedirs("data/processed/mcq", exist_ok=True)
        output_path = "data/processed/mcq/debug_2025.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(extraction.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved to {output_path}")
    else:
        print(f"Missing files: {test_pdf_path} or {key_pdf_path}")
