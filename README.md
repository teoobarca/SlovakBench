# SlovakBench

**Benchmarking LLMs on Slovak Language Tasks**

A reproducible evaluation pipeline for testing Large Language Models on Slovak. Uses real-world data from official Maturita exams and linguistic corpora.

## 🎯 Tasks

| Task | Description | Status |
|------|-------------|--------|
| **Maturita Exam** | Slovak high school graduation exam (MCQ + short text) | ✅ Active |
| **POS Tagging** | Part-of-speech tagging on Slovak National Corpus | 🔜 Coming |
| **Grammar Correction** | Detecting and correcting Slovak text errors | 🔜 Coming |

## 🚀 Quick Start

```bash
# Install
uv sync

# Configure
cp .env.example .env
# Set OPENROUTER_API_KEY in .env

# Ingest exam data
uv run python main.py ingest --all

# Evaluate all models
uv run python main.py evaluate

# View results
uv run python main.py report

# Export for frontend
uv run python main.py export
```

## 📊 Latest Results (Maturita 2025)

| Model | Overall | MCQ | Short Text | Cost |
|-------|---------|-----|------------|------|
| gpt-5.2 | **92.2%** | 95.0% | 87.5% | $0.17 |
| gemini-2.5-pro | **92.2%** | 97.5% | 83.3% | $0.77 |
| gemini-2.5-flash | 81.2% | 97.5% | 54.2% | $0.01 |
| gpt-4o | 78.1% | 87.5% | 62.5% | $0.09 |
| claude-sonnet-4 | 75.0% | 90.0% | 50.0% | $0.13 |
| gpt-4o-mini | 65.6% | 82.5% | 37.5% | $0.01 |

## 📁 Structure

```
SlovakBench/
├── data/
│   ├── raw/exam/          # PDF test files (test_YYYY.pdf, kluc_YYYY.pdf)
│   ├── processed/exam/    # Extracted JSON datasets
│   └── results/exam/      # Evaluation results per year
├── config/
│   └── models.py          # Models to evaluate
├── public/
│   ├── index.html         # Leaderboard frontend
│   └── leaderboard.json   # Exported results
├── src/
│   ├── ingestion/         # PDF → JSON extraction
│   ├── evaluation/        # LLM evaluation runner
│   └── utils/             # LLM client, helpers
└── main.py                # CLI entry point
```

## 🔧 CLI Commands

```bash
# Ingest PDF exams
main.py ingest                    # Show status
main.py ingest --year 2025        # Process specific year
main.py ingest --all              # Process all years
main.py ingest --force            # Reprocess existing

# Evaluate models
main.py evaluate                  # Run all configured models
main.py evaluate --year 2025      # Specific year only
main.py evaluate -m openai/gpt-4o # Single model
main.py evaluate --force          # Re-run completed
main.py evaluate --list           # Show available datasets/models

# Reports
main.py report                    # Cross-model comparison
main.py report --year 2025        # Year-specific results

# Frontend
main.py export                    # Generate public/leaderboard.json
```

## ⚙️ Configuration

**Models** (`config/models.py`):
```python
MODELS = [
    "openai/gpt-5.2",
    "anthropic/claude-sonnet-4",
    "google/gemini-2.5-pro",
    # Add more...
]
```

**Environment** (`.env`):
```
OPENROUTER_API_KEY=sk-or-...
```

## 📖 Data Sources

- **Maturita Exams**: [NÚCEM](https://www.nucem.sk/) - National Institute for Certified Educational Measurements
- Official Slovak high school graduation exams in Slovak Language and Literature

## 🛠 Tech Stack

- **Python 3.11+** with `uv` package manager
- **LangChain** for LLM orchestration
- **OpenRouter** API for model access
- **Tailwind CSS** for frontend
