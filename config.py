import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "vector_store")
RESEARCH_PDF_DIR = os.getenv("RESEARCH_PDF_DIR", "data/research_pdfs")