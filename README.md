# Log Classification System

A hybrid ML pipeline that automatically classifies server/application log messages using a 3-tier fallback strategy: **Regex → BERT → LLM**. Served via a FastAPI backend with a lightweight web UI.

---

## Architecture

```
Incoming Log (source, message)
         │
         ▼
  ┌─────────────────────────────┐
  │  Is source "rare"?          │
  │  (seen < N times in train)  │
  └────────┬──────┬─────────────┘
           │ YES  │ NO
           ▼      ▼
         LLM    Regex match?
        (Groq)  ─────┬──────
                 YES  │  NO
                      ▼
                    BERT classifier
                 (all-MiniLM-L6-v2
                  + sklearn model)
```

### Classification Labels
| Label | Description |
|---|---|
| User Action | Login, logout, account creation |
| System Notification | Backups, uploads, reboots, updates |
| HTTP Error | 4xx/5xx API responses |
| Security Alert | Blocked IPs, login failures, escalation |
| Workflow Error | Process failures, escalation errors |
| Deprecation Warning | Module retirement notices |

---

## Project Structure

```
Log-Classification-System/
├── main.py                  # FastAPI app (all API endpoints)
├── classify.py              # Routing logic (which processor to use)
├── processor_regex.py       # Tier 1: Pattern matching
├── processor_bert.py        # Tier 2: Sentence transformer + sklearn
├── processor_llm.py         # Tier 3: Groq LLM (rare sources)
├── static/
│   └── index.html           # Web UI
├── models/
│   └── log_classifier_model.joblib   # Trained classifier
├── training/
│   ├── rare_sources.npy     # Sources routed to LLM
│   ├── dataset/
│   │   └── synthetic_logs.csv
│   └── training.ipynb       # Model training notebook
├── evaluation/
│   ├── logs.csv             # Test input
│   └── classified_logs.csv  # Test output
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml              # One-click Render deployment
└── .env.example
```

---

## Quick Start

### 1. Clone & set up environment

```bash
git clone <your-repo-url>
cd Log-Classification-System

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 3. Run the server

```bash
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** for the web UI, or **http://localhost:8000/docs** for the interactive API docs.

---

## API Reference

### `POST /classify/single`
Classify one log entry.

```bash
curl -X POST http://localhost:8000/classify/single \
  -H "Content-Type: application/json" \
  -d '{"source": "ModernCRM", "log_message": "IP 192.168.1.1 blocked due to potential attack"}'
```

**Response:**
```json
{
  "source": "ModernCRM",
  "log_message": "IP 192.168.1.1 blocked due to potential attack",
  "label": "Security Alert"
}
```

### `POST /classify`
Classify a batch of logs.

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      {"source": "BillingSystem", "log_message": "User User12345 logged in."},
      {"source": "LegacyCRM", "log_message": "Invoice generation aborted for order ID 8910."}
    ]
  }'
```

### `POST /classify/csv`
Upload a CSV → download classified CSV.

```bash
curl -X POST http://localhost:8000/classify/csv \
  -F "file=@evaluation/logs.csv" \
  --output classified.csv
```

CSV must have `source` and `log_message` columns.

---

## Deploy to Render (Free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo — Render detects `render.yaml` automatically
4. Add environment variable: `GROQ_API_KEY=your_key_here`
5. Click **Deploy** — your API will be live at `https://your-app.onrender.com`

---

## Deploy with Docker

```bash
docker compose up --build
```

The service will be available at `http://localhost:8000`.

---

## Training Your Own Model

Open `training/training.ipynb` in Jupyter. The notebook:
- Loads `training/dataset/synthetic_logs.csv`
- Generates sentence embeddings with `all-MiniLM-L6-v2`
- Trains a scikit-learn classifier
- Saves the model to `models/log_classifier_model.joblib`
- Identifies rare sources and saves them to `training/rare_sources.npy`

---

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Tier 1 Classifier | Python `re` (regex) |
| Tier 2 Classifier | Sentence Transformers + scikit-learn |
| Tier 3 Classifier | Groq API (Llama 3.3 70B) |
| Embeddings Model | `all-MiniLM-L6-v2` |
| Frontend | Vanilla HTML/CSS/JS |
| Containerisation | Docker + Docker Compose |

---

## License

MIT
