# Medical Research Assistant using Evidence-Based Retrieval (RAG)

> **An enterprise-grade, evidence-aware medical research question answering system that retrieves verified clinical literature from PubMed, clinical practice guidelines, and drug databases. Features hybrid information retrieval (0.5 Vector / 0.5 BM25 split), biomedical Cross-Encoder re-ranking, multi-factor evidence scoring, sentence-level hallucination detection, dynamic UI model selection (Groq, Gemini, OpenAI), and a dedicated RAGAS benchmarking dashboard across 25 medical test cases.**

---

## 🌟 Overview & Key Architecture Highlights

- **Classical Enterprise RAG (Non-Agentic)**: Architected specifically as a deterministic, high-precision retrieval pipeline rather than an unconstrained autonomous agent, ensuring clinical reliability, traceability, and zero silent failures.
- **Hybrid Information Retrieval (Strict 0.5 / 0.5 Split)**: Combines dense semantic vector similarity (Pinecone / local embedding vectors) with sparse lexical keyword matching (`rank_bm25` BM25Okapi) using an exact **0.5 Vector / 0.5 BM25 weight split**.
- **Biomedical Cross-Encoder Re-Ranking**: Performs pairwise semantic relevancy re-ranking using `cross-encoder/ms-marco-MiniLM-L-6-v2` to re-order candidate evidence chunks before feeding them to the LLM.
- **Multi-Factor Evidence Confidence Scoring**: Calculates an explicit retrieval confidence percentage based on four empirical clinical factors:
  $$\text{Overall Score} = 0.50 \times \text{Similarity} + 0.20 \times \text{Recency} + 0.20 \text{Study Quality} + 0.10 \times \text{Citation Count}$$
  *(Study Quality Weights: RCT = 1.0, Meta-Analysis / Systematic Review = 0.90, Clinical Guideline = 0.80, Cohort Study = 0.60, Case Report = 0.40)*
- **Sentence-Level Hallucination Detection Engine**: Deconstructs LLM responses into individual sentences and verifies term grounding against retrieved reference chunks, computing a live **Faithfulness Score %** and **Hallucination Risk Level** (Low / Medium / High).
- **Dynamic UI Model Selector**: Dropdown menu in the React interface to switch LLM backends on the fly:
  - **Groq Llama 3.3 70B** (`llama-3.3-70b-versatile` — Recommended Default)
  - **Groq Llama 3.1 8B** (`llama-3.1-8b-instant` — High Speed)
  - **Groq Mixtral 8x7B** (`mixtral-8x7b-32768`)
  - **Groq Gemma 2 9B** (`gemma2-9b-it`)
  - **Google Gemini 2.5 / 3.6 Flash**
  - **OpenAI GPT-4o / GPT-4o-mini**
- **Strictly Isolated API Key Architecture**: Employs two completely separate API keys in `.env`:
  1. `GROQ_API_KEY`: Used exclusively for real-time medical answer generation.
  2. `RAGAS_EVAL_API_KEY`: Used exclusively for running the 25-case RAGAS evaluation suite, preventing key exhaustion and cross-contamination.
- **Hugging Face Cloud Inference API (Zero Local Download)**: When `HUGGINGFACE_API_KEY` is provided in `.env`, the system automatically invokes Hugging Face's Cloud Inference API over HTTP to generate 768-d PubMedBERT vectors, eliminating the need to download heavy embedding weights locally (with automatic local fallback if offline).
- **Zero Re-Creation Embedding Reuse Engine**: Employs persistent disk caching (`datasets/embeddings_cache.json`) and deterministic MD5 document hashing (`hashlib.md5`). Once embeddings are computed or synced to AWS Pinecone/disk once, subsequent ingestions or server restarts instantly reuse existing vectors without re-calculating or wasting API calls.
- **RAGAS Evaluation Dashboard**: A comprehensive interactive benchmark view tracking **Faithfulness**, **Answer Relevancy**, **Context Precision**, **Context Recall**, and **Latency** across 25 curated medical test cases.

---

## 📐 Enterprise Modular System Architecture & Data Flow Diagram

The entire data flow—from offline corpus ingestion and parsing to hybrid search, Cross-Encoder reranking, confidence scoring, LLM synthesis, and dual-engine hallucination verification (DeepEval + RAGAS)—is structured into cleanly decoupled domain services under `backend/app/services/` and modular React components under `frontend/src/`:

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
│                               HYBRID RETRIEVAL & CHUNKING ENGINE (Top-20 Chunks)                                │
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
│                                  CROSS-ENCODER RE-RANKING STAGE (Top-5)                                         │
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
│         (Automatic Offline Fallback: Deterministic Clinical Synthesis Engine when offline or unauthenticated)  │
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

## 📥 Deep-Dive: How Data is Loaded from JSON Files & Indexed

A foundational component of this medical RAG architecture is its **deterministic corpus ingestion engine**. Instead of scraping unreliable web pages at query time, the system ingests pre-curated, peer-reviewed medical datasets stored as structured JSON files in the `datasets/` directory.

### 1. Structure of the Source JSON Datasets
The knowledge base consists of two distinct JSON corpora:
- `datasets/pubmed_sample.json`: Peer-reviewed clinical trials (CREDENCE, DAPA-CKD, PARADIGM-HF, KEYNOTE-189).
- `datasets/guidelines_sample.json`: Official clinical practice guidelines (2024 AHA/ACC Hypertension, IDSA Pneumonia, ADA Diabetes Standards of Care).

Each JSON file contains an array of structured objects formatted with strict clinical metadata:
```json
[
  {
    "pmid": "30990260",
    "doi": "10.1056/NEJMoa1811744",
    "title": "Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy (CREDENCE)",
    "authors": "Perkovic V, Jardine MJ, Neal B, et al.",
    "journal": "New England Journal of Medicine (NEJM)",
    "year": 2019,
    "study_type": "Randomized Controlled Trial (RCT)",
    "disease": "Diabetic Kidney Disease (DKD)",
    "drug": "Canagliflozin (SGLT2 inhibitor)",
    "source": "PubMed / Clinical Trials",
    "citation_count": 2450,
    "chunk_text": "In patients with type 2 diabetes and kidney disease, the risk of kidney failure and cardiovascular events was lower in the canagliflozin group than in the placebo group at a median follow-up of 2.62 years. The primary outcome occurred in 332 patients in the canagliflozin group (43.2 per 1000 patient-years) and 432 patients in the placebo group (61.2 per 1000 patient-years), representing a 30% relative risk reduction (HR 0.70; 95% CI, 0.59 to 0.82; P=0.00001)."
  }
]
```

### 2. Step-by-Step Data Loading & Dual-Stream Indexing Flow
When you run `python scripts/ingest_all.py` (or when the FastAPI server initializes via its startup hook), the data is extracted from the JSON files and fed into the retrieval engines through the following step-by-step pipeline:

```
===================================================================================================================
                                      JSON DATA LOADING & INDEXING PIPELINE
===================================================================================================================

[ Step 1: Disk I/O & Parsing ]
  ├── Read datasets/pubmed_sample.json ───┐
  └── Read datasets/guidelines_sample.json ┼──► Parse JSON Arrays via json.load(file)
                                                        │
                                                        ▼
[ Step 2: Document Object Construction ]
  └── Iterate over JSON items ──► Create Document(text=chunk_text, metadata={pmid, doi, title, authors, ...})
                                                        │
                                                        ▼
[ Step 3: Dual-Stream Parallel Indexing ]
  ┌─────────────────────────────────────────────────────┴─────────────────────────────────────────────────────┐
  ▼                                                                                                           ▼
┌───────────────────────────────────────────────────────────┐   ┌───────────────────────────────────────────────────────────┐
│           STREAM A: DENSE VECTOR DB INGESTION             │   │            STREAM B: SPARSE BM25 KEYWORD INDEXING         │
├───────────────────────────────────────────────────────────┤   ├───────────────────────────────────────────────────────────┤
│ 1. Concatenate: full_text = f"{title}. {chunk_text}"     │   │ 1. Extract raw chunk_text for every document.             │
│ 2. Send to SentenceTransformer('PubMedBERT').             │   │ 2. Apply Regex Tokenizer: re.findall(r"\b\w+\b", text).   │
│ 3. Generate 768-dimensional PyTorch embedding vector.     │   │ 3. Lowercase all tokens and strip punctuation.            │
│ 4. Store in Pinecone Cloud DB or Local RAM Matrix.        │   │ 4. Feed tokenized arrays into rank_bm25 (BM25Okapi).      │
└─────────────────────────────┬─────────────────────────────┘   └─────────────────────────────┬─────────────────────────────┘
                              │                                                               │
                              └─────────────────────────────┬─────────────────────────────────┘
                                                            │
                                                            ▼
                              [ Step 4: Hybrid Index Ready for 0.5 / 0.5 Search ]
```

#### Detailed Breakdown of the 4 Loading Steps:
1. **Disk I/O & Parsing**: Python's native `json.load()` opens each file in `datasets/`, decoding the UTF-8 text into Python lists of dictionaries.
2. **Document Object Construction**: Each dictionary is mapped into a LangChain-compatible `Document` object. The `chunk_text` becomes the primary `page_content`, while all bibliographic identifiers (`pmid`, `doi`, `title`, `authors`, `journal`, `year`, `study_type`, `citation_count`, `source`) are preserved inside the `metadata` dictionary.
3. **Dual-Stream Indexing**: The constructed documents are simultaneously dispatched to both retrieval indexes:
   - **Dense Vector Ingestion (Stream A)**: The document's title and body text are merged (`f"{title}. {chunk_text}"`) and checked against the **Zero Re-Creation Embedding Reuse Cache (`datasets/embeddings_cache.json`)** using a deterministic MD5 hash (`hashlib.md5`). If the vector is already pre-computed, it is instantly loaded from disk with zero re-calculation or API overhead! If it is a new document, `embedding_service.embed_documents()` calls **Hugging Face's Cloud Inference API over HTTP** (no local model downloading required) to generate the `[768]` float array and saves it to the cache. If Pinecone is configured (`PINECONE_ENVIRONMENT=us-east-1-aws`), `pinecone_index.upsert()` syncs the persistent vectors to the cloud; otherwise, they are held in high-speed local memory matrices.
   - **Lexical BM25 Ingestion (Stream B)**: Simultaneously, `bm25_store.index_documents()` extracts words using regex (`re.findall(r"\b\w+\b", text.lower())`), generating tokenized lists such as `["in", "patients", "with", "type", "2", "diabetes", ...]`. These arrays are indexed into an in-memory `BM25Okapi` data structure.
4. **Index Verification**: Once ingestion finishes, the script outputs exact index counts and cache hit statistics (e.g., `[EMBEDDING REUSE] Reused 10 existing pre-computed embeddings! (Zero re-creation needed)`), ensuring the system is ready for instant 0.5 Vector / 0.5 BM25 hybrid queries.

---

## 🚀 Execution & Deployment Commands

You can run and execute this project using either **Docker (recommended for production)** or **local Python/Node.js commands (recommended for development)**.

### Option 1: Production Docker Deployment (One-Command Setup)

The entire full-stack application (FastAPI backend + React frontend) is fully containerized. To build and launch the project in Docker:

```bash
# 1. Open your terminal in the project root folder
cd "MEDICAL RESEARCH ASSISTANT (RAG)"

# 2. Build the Docker images and launch the containers in background (detached mode)
docker-compose up --build -d
```

#### Accessing the Running Services:
- **React Frontend Web Application**: Open your browser to `http://localhost:3000`
- **FastAPI Interactive Swagger UI Docs**: Open your browser to `http://localhost:8000/docs`
- **System Health Diagnostics Endpoint**: Open your browser to `http://localhost:8000/health`

#### Useful Docker Management Commands:
```bash
# View live streaming console logs from both backend and frontend containers
docker-compose logs -f

# Check status of running containers
docker-compose ps

# Stop and gracefully shut down all Docker containers
docker-compose down
```

---

### Option 2: Local Development Execution (Without Docker)

If you wish to execute the code locally on your Windows host without Docker, you will need two open terminal windows:

#### Terminal 1: Start the FastAPI Backend Server
```bash
# 1. Navigate to the project root directory
cd "MEDICAL RESEARCH ASSISTANT (RAG)"

# 2. Install Python backend dependencies
pip install -r backend/requirements.txt

# 3. Feed & index the JSON datasets into the Vector and BM25 databases
python scripts/ingest_all.py

# 4. Start the FastAPI Uvicorn development server with live reload
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Start the React Frontend Server
Open a **second terminal window**:
```bash
# 1. Navigate into the frontend folder
cd "MEDICAL RESEARCH ASSISTANT (RAG)/frontend"

# 2. Install Node.js frontend dependencies
npm install

# 3. Launch the React development web server
npm start
```
The React UI will automatically open in your default browser at `http://localhost:3000`.

---

### Option 3: Automated Command-Line Verification Script

To verify that data loading from JSON, hybrid retrieval, Cross-Encoder reranking, confidence scoring, hallucination detection, and RAGAS evaluation are all working correctly from the terminal:

```bash
python scripts/test_pipeline.py
```
This command will execute an automated verification script that prints out the parsed JSON document counts, runs a sample clinical query, and outputs the generated medical markdown and confidence scores to the console.

---

## ⚙️ Environment Configuration (`.env`)

The project enforces strict separation of API keys to prevent evaluation scripts from exhausting production answer generation rate limits. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Ensure your `.env` contains the following configuration:
```ini
# Medical Research Assistant (RAG) - Active Environment Configuration

# ──────────────────────────────────────────────────────────────────
# 1. MAIN LLM API KEY (For Answer Generation Pipeline)
#    Used by: Groq Cloud API for query-time LLM answer synthesis.
#    Get your key at: https://console.groq.com/keys
# ──────────────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_your_main_llm_api_key_here

# ──────────────────────────────────────────────────────────────────
# 2. SEPARATE EVALUATION API KEY (For RAGAS Framework Benchmark)
#    This key is NEVER used for answer generation — only for the
#    25-question RAGAS evaluation benchmark dashboard.
#    Use a DIFFERENT Groq key or OpenAI key here.
# ──────────────────────────────────────────────────────────────────
RAGAS_EVAL_API_KEY=gsk_your_separate_evaluation_api_key_here

# ──────────────────────────────────────────────────────────────────
# 3. HUGGING FACE API KEY (For PubMedBERT Medical Embeddings & Models)
#    Used by Hugging Face API / Hub to authenticate and generate
#    biomedical embeddings without downloading large models locally.
#    Get your key/token at: https://huggingface.co/settings/tokens
# ──────────────────────────────────────────────────────────────────
HUGGINGFACE_API_KEY=hf_your_huggingface_api_key_here

# Provider Settings
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile

# ──────────────────────────────────────────────────────────────────
# 4. PINECONE VECTOR DATABASE CONFIGURATION
#    PINECONE_ENVIRONMENT: Specifies the cloud provider & region where your
#    Pinecone index is hosted (e.g., "gcp-starter" for free tier, "us-east-1-aws",
#    or "us-west1-gcp"). Required by Pinecone SDK to locate your index cluster.
#    Leave API key blank to operate in local in-memory vector fallback mode.
# ──────────────────────────────────────────────────────────────────
PINECONE_API_KEY=
PINECONE_INDEX_NAME=medical-rag-index
PINECONE_ENVIRONMENT=us-east-1-aws

# Dense Embeddings Model (Hugging Face PubMedBERT for biomedical RAG)
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

## 📊 Dual RAGAS & DeepEval Evaluation Benchmark Suite

The system includes an integrated evaluation benchmark suite (`backend/app/evaluation/ragas_benchmark_25.json`) containing **25 clinical test cases** with expert ground-truth answers, evaluated across two industry-leading frameworks:

### 1. RAGAS Framework Metrics
1. **Faithfulness**: Percentage of generated sentences supported by retrieved chunks.
2. **Answer Relevancy**: Semantic relevance of the answer to the user query.
3. **Context Precision**: Signal-to-noise ratio of top retrieved chunks.
4. **Context Recall**: Coverage of ground-truth concepts present in retrieved chunks.

### 2. DeepEval Framework (G-Eval & Hallucination Guardrails)
1. **G-Eval Clinical Correctness**: Evaluates accuracy against clinical trial evidence and contraindication guidelines.
2. **Hallucination Metric**: Evaluates risk of non-grounded claims or drug-drug interaction omissions.

### Triggering the Evaluation Suite
- **Via UI**: Go to the **"RAGAS & DeepEval Dashboard"** tab in the navbar and click **"Run Live Evaluation"**.
- **Via REST API**:
  ```bash
  curl -X POST "http://localhost:8000/api/eval/run" \
    -H "Content-Type: application/json" \
    -d '{"llm_model": "llama-3.3-70b-versatile"}'
  ```

---

## 🔗 API Endpoint Reference

| HTTP Method | API Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System diagnostics: reports active LLM model, vector store mode (Pinecone vs Local RAM), and 0.5/0.5 retrieval weights. |
| `POST` | `/api/search` | Synchronous RAG endpoint: accepts `SearchQueryRequest` JSON and returns complete `AnswerResponse` with evidence ranking. |
| `POST` | `/api/ask-stream` | Server-Sent Events (SSE) streaming endpoint: pushes real-time retrieval status events and live LLM token chunks. |
| `GET` | `/api/eval/metrics` | Retrieves cached summary benchmark metrics (Faithfulness, Relevancy, Precision, Recall) over the 25 test cases. |
| `POST` | `/api/eval/run` | Triggers a live evaluation benchmark run over test cases using the dedicated `RAGAS_EVAL_API_KEY`. |

---

## 📜 License
MIT License. Built for enterprise medical research, evidence-based clinical question answering, and RAG evaluation benchmarking.
