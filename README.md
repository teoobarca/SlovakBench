# SlovakBench 🇸🇰

**A Robust Evaluation Pipeline for Large Language Models on Slovak Language Tasks**

SlovakBench is an open-source framework designed to rigorously evaluate the capabilities of Large Language Models (LLMs) in the Slovak language. Unlike generic multi-lingual benchmarks, SlovakBench focuses on culturally and linguistically specific tasks, ranging from high school graduation exams to low-level linguistic analysis.

![SlovakBench Leaderboard](https://via.placeholder.com/1200x600?text=SlovakBench+Dashboard) 
*(Replace with actual screenshot if available)*

## 🎯 Benchmark Tasks

| Task | ID | Description | Status |
|------|----|-------------|--------|
| **Maturita Exam** | `exam` | Official Slovak high school graduation exam (Maturita) in Slovak Language and Literature. Includes extensive **MCQ** (comprehension, grammar, literature) and **Short Text** generation. | ✅ Active |
| **Universal Dependencies** | `ud` | Low-level linguistic evaluation on the Slovak National Corpus (SNK). Tests **POS Tagging** (Part-of-Speech), **Lemmatization** (base forms), and **Dependency Parsing** (syntax). | ✅ Active |
| **Grammar Correction** | `grammar` | Detecting and correcting grammatical, spelling, and stylistic errors in native Slovak text. | 🚧 Planned |

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** (fast Python package manager)
- **Node.js 18+** (for Frontend)
- **OpenRouter API Key** (for accessing models)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SlovakBench.git
cd SlovakBench

# Install dependencies
uv sync
```

### 2. Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```env
OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Run the Pipeline

```bash
# 1. Ingest Data (parse PDF exams)
uv run python main.py ingest --all

# 2. Run Evaluation (Exam & POS)
uv run python main.py evaluate exam
uv run python main.py evaluate ud

# 3. View Report
uv run python main.py report

# 4. Start Leaderboard UI
uv run python main.py export  # Generates frontend data
cd frontend
npm install
npm run dev
```

## 🛠️ CLI Reference

 The core logic is handled by `main.py`. Here are the available commands:

### 📥 Data Ingestion
Parses raw PDF files from `data/raw/exam` into structured JSON datasets.
```bash
main.py ingest --year 2025        # Process specific year
main.py ingest --all              # Process all years
main.py ingest --force            # Re-process existing files
```

### 🧪 Benchmarking
Runs evaluation for configured models.
```bash
# Maturita Exam
main.py evaluate exam --year 2025 # Specific year
main.py evaluate exam --all       # All years
main.py evaluate exam -m openai/gpt-4o  # Specific model

# Universal Dependencies (POS/Lemma/Syntax)
main.py evaluate ud               # Run all models on UD dataset
main.py evaluate ud --report      # Show UD specific report table
```

### 📊 Analysis & Reporting
Tools to inspect results and debug failures.
```bash
# General Report
main.py report                    # Show comparison table for all models
main.py report --year 2025        # Detailed report for a specific year

# Deep Dive Analysis
main.py analyze --year 2025       # Analyze failed questions (identifies hard questions)
main.py analyze --model gpt-4     # Filter analysis by model

# Re-evaluation & Retries
main.py retry --year 2025         # Retry ONLY failed questions (saves $$)
main.py reevaluate --year 2025 -q 12  # Re-run a specific question ID for all models
```

### 🌐 Frontend Export
Prepares data for the Next.js web application.
```bash
main.py export                    # Exports to frontend/public/leaderboard.json
```

## 📁 Project Structure

```
SlovakBench/
├── config/
│   └── models.py          # LLM configuration (add new models here)
├── data/
│   ├── raw/               # Original PDFs (test_YYYY.pdf)
│   ├── processed/         # Extracted JSON datasets
│   └── results/           # Evaluation logs and results
├── frontend/              # Next.js Leaderboard App
├── src/
│   ├── ingestion/         # PDF parsing logic using specialized prompts
│   ├── evaluation/        # Evaluation runners (Exam & UD)
│   └── utils/             # LLM client wrappers and helpers
└── main.py                # Central CLI entry point
```

## ⚙️ adding New Models

To evaluate a new model, simply add it to `config/models.py`:

```python
MODELS = {
    # ...
    "provider/model-name": create_llm("provider/model-name"),
}
```
SlovakBench uses **OpenRouter** standard, so any model supported by OpenRouter can be added instantly.

## 📖 Methodology

### Maturita Exam
- **Source**: National Institute for Certified Educational Measurements (NÚCEM).
- **Metric**: Accuracy (Exact Match for MCQ, Semantic Match for Text).
- **Process**: We extract questions from official PDFs, keeping context (articles/poems) attached to relevant questions. Models are prompted to solve the test zero-shot or few-shot.

### Universal Dependencies (UD)
- **Source**: Slovak National Corpus (SNK).
- **Metric**: Token-level accuracy for POS tags, Lemmas, and Dependency relations.
- **Process**: A curated subset of complex sentences is presented to the model. The model must produce CoNLL-U style usage tags which are then parsed and compared to gold labels.

## 📄 License

This project is open-source under the MIT License.
Data from NÚCEM and SNK retains their original licensing/copyrights.
