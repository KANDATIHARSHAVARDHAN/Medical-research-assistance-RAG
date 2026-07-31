# Medical Research Assistant using Evidence-Based Retrieval (RAG)

> **An enterprise-grade, evidence-aware medical research question answering system that retrieves verified clinical literature from PubMed, clinical practice guidelines, and drug databases. Features hybrid information retrieval (0.5 Vector / 0.5 BM25 split), biomedical Cross-Encoder re-ranking, multi-factor evidence scoring, sentence-level hallucination detection, dynamic UI model selection (Groq, Gemini, OpenAI), and a dedicated RAGAS benchmarking dashboard across 25 medical test cases.**

---

## 🌟 Overview & Benchmark Score Highlights

### 📊 Live Benchmark Metrics (25 Medical Research Test Cases)
| Metric | Benchmark Score | Description |
| :--- | :---: | :--- |
| **Faithfulness** | **100%** | Sentence Grounding Ratio against verified clinical literature |
| **Answer Relevancy** | **94.4%** | Intent Coverage Score comparing LLM answer to clinical query |
| **Context Precision** | **96.9%** | Signal-to-Noise ratio of 0.5 Vector / 0.5 BM25 hybrid search |
| **Context Recall** | **93.8%** | Ground Truth Coverage ratio from retrieved evidence chunks |
| **Avg Pipeline Latency** | **2578.5 ms** | Complete end-to-end hybrid retrieval, reranking & synthesis latency |

---

## 🔑 Key Architecture Features

- **Classical Enterprise RAG (Non-Agentic)**: Architected as a deterministic, high-precision retrieval pipeline rather than an unconstrained autonomous agent, ensuring clinical reliability, traceability, and zero silent failures.
- **Hybrid Information Retrieval (Strict 0.5 / 0.5 Split)**: Combines dense semantic vector similarity (Pinecone AWS / local PubMedBERT vectors) with sparse lexical keyword matching (`rank_bm25` BM25Okapi) using an exact **0.5 Vector / 0.5 BM25 weight split**.
- **Biomedical Cross-Encoder Re-Ranking**: Performs pairwise semantic relevancy re-ranking using `cross-encoder/ms-marco-MiniLM-L-6-v2` to re-order candidate evidence chunks before feeding them to the LLM.
- **Multi-Factor Evidence Confidence Scoring**: Calculates an explicit retrieval confidence percentage based on four empirical clinical factors:
  $$\text{Overall Score} = 0.50 \times \text{Similarity} + 0.20 \times \text{Recency} + 0.20 \times \text{Study Quality} + 0.10 \times \text{Citation Count}$$
- **Sentence-Level Hallucination Detection Engine**: Deconstructs LLM responses into individual sentences and verifies term grounding against retrieved reference chunks, computing a live **Faithfulness Score %** and **Hallucination Risk Level** (Low / Medium / High).
- **Dynamic UI Model Selector**: Dropdown menu in the React interface to switch LLM backends on the fly:
  - **Groq Llama 3.3 70B** (`llama-3.3-70b-versatile` — Recommended Default for Chat)
  - **Groq Llama 3.1 8B** (`llama-3.1-8b-instant` — Recommended for 25-Case RAGAS Batch Eval)
  - **Groq Mixtral 8x7B** (`mixtral-8x7b-32768`)
  - **Groq Gemma 2 9B** (`gemma2-9b-it`)
  - **Google Gemini 2.5 / 3.6 Flash**
  - **OpenAI GPT-4o / GPT-4o-mini**
- **Hugging Face Cloud Inference API (Zero Local Download)**: When `HUGGINGFACE_API_KEY` is provided in `.env`, the system automatically invokes Hugging Face's Cloud Inference API over HTTP to generate 768-d PubMedBERT vectors, eliminating the need to download heavy embedding weights locally.

---

## 📐 Enterprise Modular System Architecture (ASCII Diagram)

```
===================================================================================================================
                                  ENTERPRISE MEDICAL RAG - MODULAR SYSTEM ARCHITECTURE
===================================================================================================================

[ MEDICAL DATASETS & APIS ]                         [ REACT 18 MODULAR FRONTEND ]
  ├── PubMed Trials & NCBI E-utilities API            ├── Pages: Home.jsx | History.jsx | Dashboard.jsx
  ├── ClinicalTrials.gov Registry API                 ├── Components: SearchBar.jsx | SourceFilter.jsx | Navbar.jsx
  ├── openFDA Drug Safety & Adverse Events API        ├── Results: ChatWindow.jsx | EvidencePanel.jsx | CitationCard.jsx
  └── DailyMed Prescribing Monographs API             └── Diagnostics: ConfidenceBar.jsx | LoadingSpinner.jsx
        │                                                     │
        ▼                                                     ▼
┌──────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────────┐
│          OFFLINE DATA INGESTION PIPELINE         ││             FASTAPI BACKEND REST & SSE API                  │
│  (backend/app/services/ingestion/ & parser/)     ││   POST /api/search  |  POST /api/ask-stream  |  POST /api/eval  │
└───────────────────────┬──────────────────────────┘└─────────────────────────────┬───────────────────────────────┘
                        │                                                         │
                        │ (Cleaned & Verified Docs)                               │ (User Query: "SGLT2i vs GLP-1RA...")
                        ▼                                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               HYBRID RETRIEVAL & CHUNKING ENGINE (Top-8 Chunks)                                 │
│                                                                                                                 │
│   Semantic Chunker: Sentence-preserving windowing with overlap (services/chunking/semantic_chunker.py)          │
│                                                                                                                 │
│               ┌─────────────────────────────────────┐               ┌─────────────────────────────────────┐     │
│               │         DENSE VECTOR SEARCH         │               │        SPARSE LEXICAL SEARCH        │     │
│               │ Model: PubMedBERT-base (768-d)      │               │       Model: rank_bm25 Okapi        │     │
│               │ HF Cloud API / Pinecone AWS / Cache │               │      Storage: Tokenized Index       │     │
│               └──────────────────┬──────────────────┘               └──────────────────┬──────────────────┘     │
│                                  │ (Weight: 0.50)                                      │ (Weight: 0.50)         │
│                                  └─────────────────┬───────────────────────────────────┘                        │
│                                                    ▼                                                            │
│                                    [ Combined Hybrid Candidate Pool ]                                           │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  CROSS-ENCODER RE-RANKING STAGE (Top-3)                                         │
│               Query + Document Text Pair ──► cross-encoder/ms-marco-MiniLM-L-6-v2 ──► Calibrated Sigmoid Score   │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     MULTI-FACTOR EVIDENCE SCORING ENGINE                                        │
│         Overall Score = 0.50*Similarity + 0.20*RecencyScore + 0.20*StudyQualityScore + 0.10*CitationNorm        │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      LLM SYNTHESIS & INFERENCE ENGINE                                           │
│         Calls Groq Cloud API (Llama 3.3 70B / Llama 3.1 8B / Mixtral / Gemma) via HTTPS REST API                │
│         (Automatic Model Failover: Switches to llama-3.1-8b-instant instantly if 70B rate limit occurs)        │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               DUAL-ENGINE HALLUCINATION & GROUNDING GUARDRAILS                                  │
│         1. Built-in Grounding Engine: Matches terms against retrieved literature (services/evaluation/).        │
│         2. DeepEval Framework: Computes G-Eval Clinical Correctness, Answer Relevancy, & Hallucination Metric.  │
│         3. RAGAS Benchmark Suite: Evaluates Faithfulness, Context Precision, and Context Recall over 25 cases.  │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
                                     [ Final JSON / SSE Stream to React UI ]
```

---

## 🌐 Medical Data Ingestion & API Key Fetching Pipeline (ASCII Flowchart)

This flowchart illustrates how medical credentials (`PUBMED_API_KEY`, `OPENFDA_API_KEY`, `CLINICAL_TRIALS_API_KEY`, `DAILYMED_API_KEY`) authenticate and extract verified clinical evidence from official medical databases:

```
===================================================================================================================
                               MEDICAL API KEY INGESTION & DATA RETRIEVAL PIPELINE
===================================================================================================================

       [ API Credentials (.env) ]
         ├── PUBMED_API_KEY=your_pubmed_api_key...     (Unlocks 10 requests/sec on NCBI E-utilities)
         ├── OPENFDA_API_KEY=your_openfda_api_key...   (Unlocks 1,000 requests/min on openFDA)
         ├── CLINICAL_TRIALS_EMAIL=your_email...       (Authenticates ClinicalTrials.gov API v2)
         └── HUGGINGFACE_API_KEY=your_hf_api_key...    (Authenticates HF Cloud Inference API for PubMedBERT)
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    LIVE & CURATED MEDICAL DATA SOURCE APIS                                      │
├──────────────────────────────────────┬────────────────────────────────────┬─────────────────────────────────────┤
│   NCBI PubMed / PubMed Central API   │    ClinicalTrials.gov API v2       │         openFDA Drug Safety API     │
│   GET /entrez/eutils/esearch.fcgi    │    GET /api/v2/studies             │         GET /drug/event.json        │
│   GET /entrez/eutils/efetch.fcgi     │    Parameters: condition, drug     │         Parameters: search, limit   │
└──────────────────┬───────────────────┴─────────────────┬──────────────────┴──────────────────┬──────────────────┘
                   │                                     │                                     │
                   └─────────────────────────────────────┼─────────────────────────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DOCUMENT PARSING & METADATA ENRICHMENT ENGINE                                   │
│  (backend/app/services/ingestion/pubmed_loader.py & guidelines_parser.py)                                       │
│                                                                                                                 │
│  Extracts: pmid, doi, title, authors, journal, year, study_type (RCT/Meta-Analysis/Guideline), citation_count   │
└────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SEMANTIC CHUNKING & DUAL-STREAM INDEXING PIPELINE                               │
│                                                                                                                 │
│    ┌───────────────────────────────────────────────┴───────────────────────────────────────────────┐            │
│    ▼                                                                                               ▼            │
│ ┌───────────────────────────────────────────────────────────┐   ┌─────────────────────────────────────────────┐ │
│ │          STREAM A: DENSE VECTOR DB INGESTION              │   │     STREAM B: SPARSE LEXICAL BM25 INDEXING  │ │
│ ├───────────────────────────────────────────────────────────┤   ├─────────────────────────────────────────────┤ │
│ │ 1. Concatenate text: f"{title}. {chunk_text}"             │   │ 1. Tokenize chunk_text using regex:         │ │
│ │ 2. Send to Hugging Face Cloud Inference API:              │   │    re.findall(r"\b\w+\b", text.lower())    │ │
│ │    https://router.huggingface.co/hf-inference/models/     │   │ 2. Lowercase and remove stop words.         │ │
│ │    BAAI/bge-base-en-v1.5 (768-d vectors)                  │   │ 3. Index tokenized arrays into in-memory    │ │
│ │ 3. Store vectors in AWS Pinecone index 'medical-rag-index'│   │    BM25Okapi datastructure.                 │ │
│ └────────────────────────────┬──────────────────────────────┘   └──────────────────────┬──────────────────────┘ │
│                              │                                                         │                        │
│                              └──────────────────────────────┬──────────────────────────┘                        │
│                                                             │                                                   │
│                                                             ▼                                                   │
│                                              [ Dual-Index Ready for RAG ]                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Complete Execution & Deployment Guide

### Environment Configuration (`.env`)

Create a `.env` file in the root directory of the project:

```ini
# 1. MAIN LLM API KEY (For Answer Generation Pipeline)
GROQ_API_KEY=gsk_your_main_llm_api_key_here

# 2. SEPARATE EVALUATION API KEY (For RAGAS Evaluation Dashboard)
RAGAS_EVAL_API_KEY=gsk_your_separate_evaluation_api_key_here

# 3. HUGGING FACE API KEY (For PubMedBERT Medical Embeddings)
HUGGINGFACE_API_KEY=hf_your_huggingface_api_key_here

# Provider Settings
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
RAGAS_EVAL_MODEL=llama-3.1-8b-instant

# Medical Data Source Credentials
PUBMED_API_KEY=your_pubmed_api_key_here
PUBMED_EMAIL=your_email@example.com
OPENFDA_API_KEY=your_openfda_api_key_here

# Pinecone Vector DB Configuration
PINECONE_API_KEY=pcsk_your_pinecone_api_key_here
PINECONE_INDEX_NAME=medical-rag-index
PINECONE_ENVIRONMENT=us-east-1-aws

# Dense Embeddings Model
EMBEDDING_MODEL_NAME=NeuML/pubmedbert-base-embeddings

# Hybrid Retrieval Weights (Strict 0.5 Vector / 0.5 BM25 Split)
VECTOR_SEARCH_WEIGHT=0.5
BM25_SEARCH_WEIGHT=0.5

# Server & Frontend Settings
PORT=8000
HOST=0.0.0.0
REACT_APP_API_URL=http://localhost:8000
```

---

### 📥 Step-by-Step Data Ingestion into Vector Database (Pinecone AWS)

To populate your Pinecone vector database (`medical-rag-index`) with clinical literature, drug monographs, and trial data from 4 live medical APIs (PubMed, ClinicalTrials.gov, openFDA, and DailyMed):

```powershell
# 1. Activate Python Virtual Environment
.\venv\Scripts\Activate.ps1

# 2. Run Data Ingestion Pipeline (Fetches live medical data across 13 specialties & upserts to Pinecone in 100-vector batches)
python scripts/ingest_all.py --api-queries "cardiology" "neurology" "covid-19" "vaccines" "chemotherapy" "pediatrics" "asthma" "alzheimer" "diabetes" "oncology" "hypertension" "metformin" "immunotherapy" --max-per-source 10
```

---

### 🧪 Executing RAGAS & DeepEval Benchmark Evaluation

The evaluation framework runs **25 medical research benchmark test cases** strictly 1-by-1 sequentially:

#### Option A: Via Web UI
1. Launch FastAPI backend: `uvicorn backend.app.main:app --reload`
2. Launch React frontend: `cd frontend && npm start`
3. Open `http://localhost:3000`, switch to **RAGAS & DeepEval Dashboard**, and click **Run Live RAGAS Evaluation**.

#### Option B: Via Terminal CLI
```powershell
# Run 1-by-1 sequential evaluation over all 25 benchmark cases using Groq Cloud LLM
python -c "from backend.app.services.evaluation.ragas_eval import ragas_evaluator; summary = ragas_evaluator.evaluate_all(llm_provider='groq', llm_model='llama-3.3-70b-versatile'); print(summary)"
```

---

### Option 1: Local Development Execution (Command Prompt / CMD)

If executing locally on Windows using `cmd.exe`:

#### Terminal 1: Backend Server (FastAPI)
```cmd
cd /d "c:\Users\HP\OneDrive\Desktop\AI ENGINEER PROJECTS\MEDICAL RESEARCH ASSISTANT (RAG)"

:: 1. Activate Python Virtual Environment
venv\Scripts\activate

:: 2. Install backend dependencies (if required)
pip install -r backend\requirements.txt

:: 3. Run multi-source medical ingestion script
python scripts\ingest_all.py --api-queries "cardiology" "neurology" "diabetes" --max-per-source 10

:: 4. Launch FastAPI development server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
* **FastAPI Backend Server:** `http://localhost:8000`
* **Interactive Swagger UI Docs:** `http://localhost:8000/docs`

#### Terminal 2: Frontend Application (React)
Open a **second CMD window**:
```cmd
cd /d "c:\Users\HP\OneDrive\Desktop\AI ENGINEER PROJECTS\MEDICAL RESEARCH ASSISTANT (RAG)\frontend"

:: 1. Install Node.js dependencies (if required)
npm install

:: 2. Launch React development web server
npm start
```
* **React Web Application:** `http://localhost:3000`

---

### Option 2: Production Docker Deployment (One-Command Setup)

To build and launch the containerized full-stack application with Docker Compose:

```cmd
:: Build images and start containers in detached mode
docker-compose up --build -d
```

#### Useful Docker Commands:
```cmd
:: View live streaming logs from backend & frontend
docker-compose logs -f

:: Check container status
docker-compose ps

:: Gracefully stop containers
docker-compose down
```

---

## 🔗 API Endpoint Reference

| HTTP Method | API Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System diagnostics: reports active LLM model, vector store mode (Pinecone vs Local RAM), and 0.5/0.5 retrieval weights. |
| `POST` | `/api/search` | Synchronous RAG endpoint: accepts `SearchQueryRequest` JSON and returns complete `AnswerResponse` with evidence ranking. |
| `POST` | `/api/ask-stream` | Server-Sent Events (SSE) streaming endpoint: pushes real-time retrieval status events and live LLM token chunks. |
| `GET` | `/api/eval/metrics` | Returns pre-computed RAGAS evaluation summary over 25 test cases instantly in 1ms with 0 API calls. |
| `POST` | `/api/eval/run` | Triggers a live 1-by-1 sequential evaluation benchmark run using the dedicated `RAGAS_EVAL_API_KEY`. |

---

## 📜 License
MIT License. Built for enterprise medical research, evidence-based clinical question answering, and RAG evaluation benchmarking.
