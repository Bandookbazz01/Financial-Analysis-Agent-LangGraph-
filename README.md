# Financial Analysis Agent (LangGraph) — Full Project Guide

## 1) Project Purpose (Why this exists)
This project is an **autonomous financial analysis agent**.  
Given a stock ticker (example: `AAPL`), the system automatically:
- pulls current market/fundamental data,
- calculates technical indicators (RSI, MACD, VWAP),
- searches recent news,
- runs sentiment analysis using FinBERT,
- optionally reads your private research documents (RAG),
- generates a structured investment report.

### The problem it solves
Normally, to analyze a stock you must manually:
- open a finance site, collect price/PE/market cap,
- open charts and compute indicators,
- search news in multiple tabs,
- mentally summarize sentiment,
- read PDFs/research notes,
- write a report.

This project automates that end-to-end workflow so you can:
- save time,
- standardize reports into one format,
- avoid missing key data,
- run the same analysis repeatedly for different tickers.

> Note: This is **not financial advice**. It is a research automation tool.

---

## 2) What the system produces (Output)
A final report with these sections:

1. Executive Summary  
2. Market Data Analysis  
3. News & Sentiment  
4. Risk Assessment  
5. RAG Insights  
6. Gaps & Limitations  

The report always includes a timestamp and lists missing data in **Gaps & Limitations**.

---

## 3) Architecture Overview (Workflow)
This system is a **multi-agent state machine** built using **LangGraph**.

### Key idea: Shared State
All nodes (agents) read and write to a shared dictionary-like state:
- `ticker`
- `market`
- `indicators`
- `news`
- `sentiment`
- `rag_context`
- `errors`
- `report`
- `iterations / max_iterations`

### Supervisor Pattern
A **Supervisor** node decides what to run next (routing):
- If market data missing → Market Data Agent
- If news/sentiment missing → Sentiment Agent
- If RAG enabled + no rag_context → RAG Agent
- Otherwise → Synthesis Node

---

## 4) Agents and What They Do

### 4.1 Supervisor Agent (`agents/supervisor.py`)
**Purpose:** Orchestrates the system.  
**Input:** current `state`  
**Output:** sets `state["next_agent"]` based on missing data.  
**Safety:** prevents infinite loops with `max_iterations`.

### 4.2 Market Data Agent (`agents/market_data.py`)
**Purpose:** Get market data + compute technical indicators.  
- Uses `yfinance` to fetch stock info
- Uses `pandas-ta` for RSI/MACD/VWAP  
Writes to:
- `state["market"]`
- `state["indicators"]`

### 4.3 Sentiment Agent (`agents/sentiment.py`)
**Purpose:** Pull news + score sentiment.  
- Uses Tavily search to fetch recent headlines
- Uses FinBERT to classify sentiment for each item  
Writes to:
- `state["news"]`
- `state["sentiment"]`

### 4.4 RAG / Quant Agent (`agents/rag_quant.py`)
**Purpose:** Use your private documents.  
- Reads documents from: `data/research_pdfs/`
- Builds/uses a local Chroma vector store: `vector_store/`
- Retrieves top-k relevant chunks and writes to `state["rag_context"]`

> RAG is optional. If no documents exist, report includes that in gaps.

### 4.5 Synthesis Node (`agents/synthesizer.py`)
**Purpose:** Generate the final report.  
In **free mode**, it builds a structured report using a template + collected signals.

---

## 5) Data Sources + Tools

### 5.1 yfinance + Finnhub (market + fundamentals)
- `yfinance` fetches historical price and calculates technicals.
- `Finnhub` is used for real-time price quotes and basic fundamentals.
- Both work together to provide a robust data set.

### 5.2 pandas-ta (indicators)
- RSI(14): overbought/oversold signal
- MACD: momentum/trend indicator
- VWAP: intraday price reference

### 5.3 Finnhub (news search)
- requires `FINNHUB_API_KEY`
- returns recent company news headlines and URLs.

### 5.4 FinBERT (sentiment)
- local model, free
- classifies finance text as positive/neutral/negative
- first run downloads weights (slow), later runs are faster

### 5.5 Chroma + SentenceTransformers embeddings + PyMuPDF (RAG)
- local embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- clean text extraction using `PyMuPDF`
- no OpenAI credits needed
- stores embeddings on disk for reuse

### 5.6 Groq + Gemini (Synthesis)
- uses Groq (Llama 3.3 70B) for fast and free report generation.
- fallback to Gemini 2.5 Flash if Groq is unavailable.

---

## 6) Project Files (What is where)
```
financial_agent/
  main.py               # CLI entrypoint
  api.py                # FastAPI service
  graph.py              # LangGraph wiring
  config.py             # env config (keys, folders)
  schemas.py            # state schema
  prompts.py            # synthesis prompt template (if needed)
  agents/               # nodes
  tools/               # pure helper functions
  data/research_pdfs/   # your documents (PDF/TXT/DOCX)
  vector_store/         # chroma database files
```

---

## 7) Setup (Windows + VS Code + PowerShell)

### 7.1 Create and activate venv
```powershell
cd D:\financial_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 7.2 Install packages
```powershell
pip install -r requirements.txt
```

### 7.3 Add keys (.env)
Create `D:\financial_agent\.env`:
```bash
GROQ_API_KEY=your_groq_key
FINNHUB_API_KEY=your_finnhub_key
GOOGLE_API_KEY=your_gemini_key

CHROMA_PERSIST_DIR=vector_store
RESEARCH_PDF_DIR=data/research_pdfs
```

> Get `GROQ_API_KEY` from groq.com, `FINNHUB_API_KEY` from finnhub.io, and `GOOGLE_API_KEY` from Google AI Studio. All have generous free tiers.

---

## 8) How to Run

### 8.1 CLI (recommended first)
Without RAG:
```powershell
python .\main.py AAPL --no-rag
```

With RAG:
```powershell
python .\main.py AAPL
```

### 8.2 Add documents for RAG
Put files here:
- `data/research_pdfs/`

Examples:
- `aapl_note.txt`
- `industry_report.docx`
- `aapl-20250927.pdf`

### 8.3 FastAPI
Start server:
```powershell
uvicorn api:app --reload --port 8000
```

Open docs:
- http://127.0.0.1:8000/docs

POST `/analyze` body:
```json
{ "ticker": "AAPL", "rag_enabled": true }
```

---

## 9) Where to see output
### CLI:
- printed in the terminal
- automatically saved to `outputs/<TICKER>_report_<timestamp>.txt`

### API:
- response JSON includes `report`
- automatically saved to `outputs/` folder.

---

## 10) Troubleshooting

### 10.1 “pypdf package not found”
Fix:
```powershell
pip install pypdf
```

### 10.2 FinBERT downloads are slow
Normal on first run. Later it uses cache.

### 10.3 PDF cannot be read
Some PDFs are scanned images or encrypted.
Workaround:
- convert to TXT (copy/paste text) and store as `.txt`
- or OCR the PDF before using RAG

### 10.4 Tavily missing
If `TAVILY_API_KEY` missing, news will fail and appear in “Gaps & Limitations”.

---

## 11) Convert this guide to PDF on Windows

### Method A (best in VS Code): “Markdown PDF” extension
1) Install extension: **Markdown PDF** (by yzane)
2) Open `PROJECT_GUIDE.md`
3) Press `Ctrl+Shift+P` → type: **Markdown PDF: Export (pdf)**
4) It will create `PROJECT_GUIDE.pdf`

### Method B: use Pandoc (if installed)
```powershell
pandoc .\PROJECT_GUIDE.md -o .\PROJECT_GUIDE.pdf
```

---

## 12) Future Improvements (Optional)
- add volatility (std dev of returns), drawdown, ATR
- caching of yfinance + news responses
- better recommendation scoring
- local LLM for narrative synthesis (optional)
