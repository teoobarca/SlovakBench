# skBench: Slovak LLM Benchmark

**skBench** is a reproducible pipeline for benchmarking Large Language Models (LLMs) in the Slovak language. The project focuses on three main tasks relevant to Slovak education and linguistics.

## 🎯 Project Goals
1.  **POS Tagging (Part-of-Speech):** Automatic determination of word classes using the Universal Dependencies (UD) corpus.
2.  **MCQ (Multiple Choice Questions):** Solving multiple-choice questions (A, B, C, D) extracted from official leaving exams and entrance tests.
3.  **Grammar Correction:** Correcting grammatical and spelling errors in Slovak text (both synthetic and real errors).

## 📂 Project Structure

This project is organized to clearly separate each step (from data acquisition to evaluation):

```text
skBench/
├── data/
│   ├── raw/          # Raw data (PDF tests, .conllu files) - DROP YOUR DATA HERE
│   ├── processed/    # Cleaned data in JSON/JSONL format ready for models
│   └── results/      # Model outputs and final metrics (scores)
├── src/
│   ├── ingestion/    # Scripts for data processing (PDF -> Text, Conllu -> JSON)
│   ├── evaluation/   # Logic for running models and evaluating responses
│   └── utils/        # Helper functions (logging, configs)
├── notebooks/        # Jupyter notebooks for data exploration and quick experiments
├── .env              # API keys (e.g., OPENROUTER_API_KEY)
├── pyproject.toml    # Project definition and dependencies (managed via uv)
└── uv.lock           # Locked package versions for reproducibility
```

## 🚀 Quick Start

### 1. Environment Setup
This project uses `uv` for package management, a super-fast alternative to pip/poetry.

```bash
# Install dependencies
uv sync
```

### 2. Configuration
Create a `.env` file (by copying `.env.example`) and add your API key:

```bash
cp .env.example .env
# Open .env and set OPENROUTER_API_KEY=...
```

### 3. Data
- **MCQ:** Upload PDF test files to `data/raw/mcq_pdfs/`.
- **POS:** Download the UD Slovak corpus and place `.conllu` files in `data/raw/ud_slovak/`.

### 4. Running
*(Instructions for running data processing and evaluation scripts will be added here once implemented)*

## 🛠 Technologies Used
- **Python 3.14+**
- **LangChain:** For orchestrating LLM calls.
- **OpenRouter:** For accessing various models via a unified API.
- **PyPDF:** For extracting text from PDFs.
- **Pandas/Datasets:** For data manipulation.
