from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import pandas as pd
import io
import os

from classify import classify, classify_log

app = FastAPI(
    title="Log Classification API",
    description="Classifies log messages using a hybrid Regex → BERT → LLM pipeline.",
    version="1.0.0"
)

# Serve the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("static/index.html") as f:
        return f.read()


# ── Schemas ──────────────────────────────────────────────────────────────────

class LogEntry(BaseModel):
    source: str
    log_message: str

class ClassifyRequest(BaseModel):
    logs: List[LogEntry]

class ClassifyResponse(BaseModel):
    results: List[dict]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify_logs(request: ClassifyRequest):
    """Batch classify a list of log entries."""
    if not request.logs:
        raise HTTPException(status_code=400, detail="No logs provided.")
    pairs = [(e.source, e.log_message) for e in request.logs]
    labels = classify(pairs)
    results = [
        {"source": src, "log_message": msg, "label": label}
        for (src, msg), label in zip(pairs, labels)
    ]
    return {"results": results}


@app.post("/classify/single")
def classify_single(entry: LogEntry):
    """Classify a single log entry."""
    label = classify_log(entry.source, entry.log_message)
    return {"source": entry.source, "log_message": entry.log_message, "label": label}


@app.post("/classify/csv")
async def classify_csv_upload(file: UploadFile = File(...)):
    """Upload a CSV with [source, log_message] columns → download classified CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")
    if "source" not in df.columns or "log_message" not in df.columns:
        raise HTTPException(status_code=422, detail="CSV must have 'source' and 'log_message' columns.")
    df["label"] = classify(list(zip(df["source"], df["log_message"])))
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=classified_logs.csv"}
    )
