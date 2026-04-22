import sys
import os
from datetime import datetime
from graph import build_app

def save_report(ticker: str, report: str):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"outputs/{ticker}_report_{timestamp}.txt"
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport successfully saved to {filepath}")
    except Exception as e:
        print(f"\nFailed to save report: {e}")

def run(ticker: str, rag_enabled: bool = True):
    app = build_app()
    result = app.invoke({
        "ticker": ticker.upper(),
        "rag_enabled": rag_enabled,
        "iterations": 0,
        "max_iterations": 8,
        "errors": [],
        "rag_context": None,
        "report": None,
    })
    report = result.get("report", "No report generated.")
    print(report)
    if result.get("errors"):
        print("\n---\nErrors:")
        for e in result["errors"]:
            print("-", e)
            
    if report and report != "No report generated.":
        save_report(ticker.upper(), report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <TICKER> [--no-rag]")
        sys.exit(1)

    ticker = sys.argv[1]
    rag_enabled = "--no-rag" not in sys.argv[2:]
    run(ticker, rag_enabled=rag_enabled)