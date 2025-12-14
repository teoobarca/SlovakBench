"""Answer validation for exam benchmarks."""
import re
import unicodedata
from typing import List


def normalize(text: str, steps: List[str]) -> str:
    """Apply normalization steps: trim, casefold, collapse_ws, remove_punct, remove_diacritics, numeric_only, normalize_dashes."""
    for step in steps:
        if step == "trim":
            text = text.strip()
        elif step == "casefold":
            text = text.casefold()
        elif step == "collapse_ws":
            text = " ".join(text.split())
        elif step == "remove_punct":
            text = re.sub(r'[^\w\s]', '', text)
        elif step == "remove_diacritics":
            text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
        elif step == "numeric_only":
            text = "".join(c for c in text if c.isdigit())
        elif step == "normalize_dashes":
            # Convert all dash variants to simple hyphen-minus
            text = re.sub(r'[–—−‐‑]', '-', text)
    return text


def validate_mcq(answer: str, correct: str) -> bool:
    """Check if MCQ answer matches (A/B/C/D)."""
    return answer.strip().upper()[:1] == correct.upper()


def validate_short_text(answer: str, accepted: List[str], steps: List[str]) -> bool:
    """Check if answer matches any accepted form after normalization."""
    norm_answer = normalize(answer, steps)
    return norm_answer in [normalize(a, steps) for a in accepted]
