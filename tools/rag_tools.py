import os
import re
from config import CHROMA_PERSIST_DIR, RESEARCH_PDF_DIR

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

_COLLECTION = "research"

def clean_text(text: str) -> str:
    # Remove weird characters and excessive whitespace
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def ensure_vectorstore_built() -> dict:
    try:
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

        emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        vs = Chroma(
            collection_name=_COLLECTION,
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=emb,
        )
        existing = vs._collection.count()
        if existing and existing > 0:
            return {"ok": True, "data": {"status": "ready", "docs": existing}}

        if not os.path.isdir(RESEARCH_PDF_DIR):
            return {"ok": False, "error": f"PDF dir not found: {RESEARCH_PDF_DIR}", "data": {}}

        docs = []
        for filename in os.listdir(RESEARCH_PDF_DIR):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(RESEARCH_PDF_DIR, filename)
                loader = PyMuPDFLoader(filepath)
                file_docs = loader.load()
                for doc in file_docs:
                    doc.page_content = clean_text(doc.page_content)
                    doc.metadata['source'] = filename
                docs.extend(file_docs)

        if not docs:
            return {"ok": False, "error": f"No PDFs found in {RESEARCH_PDF_DIR}", "data": {}}

        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
        chunks = splitter.split_documents(docs)

        Chroma.from_documents(
            documents=chunks,
            embedding=emb,
            collection_name=_COLLECTION,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        return {"ok": True, "data": {"status": "built", "chunks": len(chunks)}}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": {}}

def retrieve_research_context(query: str, k: int = 6) -> dict:
    try:
        emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vs = Chroma(
            collection_name=_COLLECTION,
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=emb,
        )
        docs = vs.similarity_search(query, k=k)
        
        context_parts = []
        for i, d in enumerate(docs):
            source = d.metadata.get('source', 'Unknown')
            page = d.metadata.get('page', 'Unknown')
            context_parts.append(f"[{i+1}] Source: {source} (Page {page})\n{d.page_content}")
            
        context = "\n\n".join(context_parts)
        return {"ok": True, "data": context}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": ""}