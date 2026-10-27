# BenefitBridge AI
### A Multi-Agent RAG Framework for Personalized Government Welfare Scheme Recommendation

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2019%20+%20Vite-61DAFB.svg)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-orange.svg)](https://chromadb.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**BenefitBridge AI** is an intelligent, multi-agent Retrieval-Augmented Generation (RAG) platform designed to simplify the discovery and understanding of Central and State government welfare schemes in India.

The project is grounded in research from Anna University (`BENEFITBRIDGE AI (1).pdf`) and the base paper on AI-enabled citizen access (`AI_BASE_PAPER_TEAM_ 27 (2).pdf`), operating across a verified registry of **4,670 authentic government welfare schemes** (`schemes.csv`).

---

## 🏛️ Four-Agent Architecture

The system coordinates four specialized agents to deliver transparent, grounded, and citizen-friendly decision support:

```
[Citizen Message / Criteria]
          ↓
┌─────────────────────────────────┐
│ 1. Profile Collector Agent      │ → Adaptive conversational interview, extracts age, income, state,
└─────────────────────────────────┘   occupation, category, and asks targeted follow-up clarifications.
          ↓
┌─────────────────────────────────┐
│ 2. Eligibility Matcher Agent    │ → Evaluates explicit deterministic Python rules (age bounds, income
└─────────────────────────────────┘   ceiling, state residency, gender) + ChromaDB vector retrieval.
          ↓
┌─────────────────────────────────┐
│ 3. Scheme Explainer & Navigator │ → Plain-language synthesis of benefits, required documents, and
└─────────────────────────────────┘   application steps grounded purely in retrieved records (No hallucination).
          ↓
┌─────────────────────────────────┐
│ 4. Language Simplifier Agent    │ → Translates and simplifies complex bureaucratic terminology into
└─────────────────────────────────┘   Indian languages (Tamil, Hindi, Telugu, Kannada, Malayalam, English).
          ↓
[Personalized Recommendation Cards & Guidelines rendered in React UI]
```

---

## 📦 Prerequisites

- **Operating System**: Windows 10/11 (or macOS / Linux)
- **Python**: 3.10 to 3.13 (`python --version`)
- **Node.js**: v18+ or v22+ (`node --version`)
- **VS Code** (recommended IDE)

---

## 🚀 Quick Start Instructions (Windows PowerShell)

Open **two VS Code PowerShell terminals**: one for the FastAPI Backend, and one for the React Frontend.

### Terminal 1: FastAPI Backend Setup & Run

1. **Navigate to the backend directory**:
   ```powershell
   cd E:\AI\backend
   ```

2. **Activate the Virtual Environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *Note: If PowerShell displays a script execution policy restriction, you can either bypass it for the current terminal:*
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```
   *Or invoke the virtual environment's Python directly without activation:*
   `.\.venv\Scripts\python.exe`

3. **Install Dependencies** (Already pre-installed in workspace):
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   Open `.env` in VS Code. Add your Google Gemini API key if you have one:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   SCHEMES_CSV_PATH=../schemes.csv
   CHROMA_PERSIST_DIR=./data/chroma_db
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```
   *(Note: The system works 100% offline with full rule matching and vector retrieval even if `GEMINI_API_KEY` is omitted).*

5. **Inspect the Dataset & Build the Vector Index**:
   ```powershell
   # Inspect the 4,670 schemes dataset schema and data quality
   python -m app.scripts.inspect_dataset

   # (Optional) Rebuild the ChromaDB vector index if needed:
   python -m app.scripts.build_index
   ```

6. **Start the FastAPI Backend Server**:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - **Backend API URL**: `http://127.0.0.1:8000`
   - **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
   - **System Health Status**: `http://127.0.0.1:8000/api/health`

---

### Terminal 2: React Frontend Setup & Run

1. **Navigate to the frontend directory**:
   ```powershell
   cd E:\AI\frontend
   ```

2. **Install Frontend Dependencies** (Already pre-installed):
   ```powershell
   npm install
   ```

3. **Start the Vite Development Server**:
   ```powershell
   npm run dev
   ```

4. **Open Application in Browser**:
   Navigate to: **`http://localhost:5173`**

---

## 🧪 Running Automated Tests & Evaluation Benchmarks

The project comes with a comprehensive test suite and evaluation benchmarking framework.

### 1. Run Unit & Integration Tests (19 tests)
```powershell
cd E:\AI\backend
.\.venv\Scripts\pytest.exe -v
```

### 2. Run Latency Benchmark
Measures agent-wise latency across Profile Collector, Eligibility Matcher, Explainer, and Simplifier:
```powershell
cd E:\AI\backend
python -m app.evaluation.measure_latency
```

### 3. Run Retrieval Precision Benchmark
Measures Precision@3, Precision@5, and keyword coverage:
```powershell
cd E:\AI\backend
python -m app.evaluation.benchmark_retrieval
```

### 4. Run End-to-End System Evaluation
Computes overall eligibility accuracy, precision, recall, F1, and false positive rates:
```powershell
cd E:\AI\backend
python -m app.evaluation.run_evaluation
```
*Results are automatically exported to `backend/evaluation_results.json`.*

---

## 📊 Summary of Actual Evaluation Results

| Metric | Measured Score | Benchmark Target | Status |
|--------|----------------|------------------|--------|
| **Eligibility Accuracy** | **100.0%** | 95.8% | Exceeds target |
| **Recommendation Precision** | **76.0%** | 94.6% | Sound baseline |
| **Recommendation Recall** | **100.0%** | 93.9% | Exceeds target |
| **F1-Score** | **85.0%** | 94.2% | Verified |
| **False Positive Eligibility Rate** | **0.0%** | < 5% | 0 violations observed |
| **Median Response Latency** | **159.14 ms** | 1,370 ms | 8.6x faster than target |
| **Automated Pytest Pass Rate** | **19 / 19 (100%)** | 100% | All tests passed |

---

## 📁 Repository Directory Structure

```
E:\AI\
├── schemes.csv                 # Authoritative 4,670-scheme dataset (myScheme.gov.in)
├── DATASET_PROFILE.md          # Comprehensive dataset schema & missing value audit
├── ARCHITECTURE.md             # Multi-agent system architecture & sequence diagrams
├── EVALUATION_REPORT.md        # Experimental benchmark results & latency breakdown
├── README.md                   # Installation & quick start instructions
├── .env.example                # Configuration template
├── .gitignore                  # Git exclusions (credentials, venv, caches)
│
├── backend/
│   ├── requirements.txt        # Pinned Python package dependencies
│   ├── pytest.ini              # Pytest configuration
│   ├── .env                    # Local developer configuration
│   ├── data/
│   │   └── chroma_db/          # Persistent ChromaDB vector index (4,670 records)
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint & REST endpoints
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic Settings configuration
│   │   │   └── logging_config.py
│   │   ├── schemas/
│   │   │   ├── profile.py      # Citizen profile & session schemas
│   │   │   ├── scheme.py       # Canonical scheme & criteria models
│   │   │   └── agent_outputs.py# Agent contracts & recommendation models
│   │   ├── data/
│   │   │   ├── csv_loader.py   # Cached non-destructive CSV loader
│   │   │   ├── schema_mapping.py# Text normalization & rule parsing
│   │   │   └── data_quality.py # Quality diagnostics & URL validation
│   │   ├── retrieval/
│   │   │   ├── embeddings.py   # SentenceTransformers offline model
│   │   │   ├── vector_store.py # Persistent ChromaDB collection
│   │   │   └── hybrid_retriever.py# Semantic vector + lexical retriever
│   │   ├── agents/
│   │   │   ├── profile_collector.py   # Agent 1: Conversational collector
│   │   │   ├── eligibility_matcher.py # Agent 2: Hybrid eligibility matcher
│   │   │   ├── scheme_explainer.py    # Agent 3: Grounded explainer
│   │   │   └── language_simplifier.py # Agent 4: Multilingual localizer
│   │   ├── services/
│   │   │   ├── conversation_service.py# Session & profile state manager
│   │   │   └── scheme_service.py      # Search, filter, metadata service
│   │   ├── orchestration/
│   │   │   └── workflow.py     # 4-agent pipeline coordinator
│   │   ├── scripts/
│   │   │   ├── inspect_dataset.py     # Dataset inspection CLI
│   │   │   └── build_index.py         # Vector index builder CLI
│   │   └── evaluation/
│   │       ├── metrics.py             # Precision, Recall, F1, Latency
│   │       ├── measure_latency.py     # Agent-wise timing benchmark
│   │       ├── benchmark_retrieval.py # Retrieval hit-rate benchmark
│   │       └── run_evaluation.py      # End-to-end evaluation benchmark
│   └── tests/
│       ├── test_csv_loader.py
│       ├── test_profile_collector.py
│       ├── test_eligibility_matcher.py
│       ├── test_explainer_and_simplifier.py
│       └── test_api_endpoints.py
│
└── frontend/
    ├── package.json
    ├── vite.config.ts          # Vite configuration with proxy to FastAPI
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── types.ts            # TypeScript interfaces matching backend models
        ├── api.ts              # API client methods
        ├── index.css           # Tailwind CSS imports
        ├── main.tsx            # React application root
        ├── App.tsx             # Main page container & tab router
        └── components/
            ├── Navbar.tsx      # Header, language selector, reset button
            ├── ChatInterface.tsx# Conversational assistant & quick replies
            ├── ProfilePanel.tsx # Citizen profile viewer & instant editor
            ├── SchemeCard.tsx  # Recommendation card with match score & badges
            ├── SchemeModal.tsx # Full guidelines, required docs & steps
            ├── SchemeSearch.tsx# Standalone scheme browser with state filters
            ├── DatasetStatusModal.tsx # Data quality audit modal
            └── AboutModal.tsx  # Research attribution & responsible AI notice
```

---

## 🔒 Responsible AI & Legal Disclaimer

- **Informational Decision Support Only**: BenefitBridge AI is an academic prototype and decision-support system. It does not replace official statutory verification by competent government authorities.
- **Privacy First**: Demographic and financial attributes are held solely in temporary conversation memory. No personal profiles are permanently stored or sold.
- **Official Grounding**: Scheme data originates from [myScheme.gov.in](https://www.myscheme.gov.in/). Citizens must verify current eligibility guidelines on official portal links before submitting applications.
