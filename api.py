from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_app
import os
from datetime import datetime

app = FastAPI(title="Financial Agent API")

_graph_app = build_app()

class AnalyzeRequest(BaseModel):
    ticker: str
    rag_enabled: bool = True

def save_report(ticker: str, report: str):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"outputs/{ticker}_report_{timestamp}.txt"
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
    except Exception as e:
        print(f"\nFailed to save report: {e}")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    result = _graph_app.invoke({
        "ticker": req.ticker.upper(),
        "rag_enabled": req.rag_enabled,
        "iterations": 0,
        "max_iterations": 8,
        "errors": [],
        "rag_context": None,
        "report": None,
    })
    
    report = result.get("report")
    if report:
        save_report(req.ticker.upper(), report)
        
    return {
        "ticker": req.ticker.upper(),
        "report": report,
        "errors": result.get("errors", []),
        "market": result.get("market", {}),
        "indicators": result.get("indicators", {}),
        "sentiment": result.get("sentiment", {}),
    }