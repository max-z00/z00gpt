# LLM Data Analytics

Local-first data analyst copilot that profiles datasets, chats with a local LLM, and logs reproducible analysis runs.

## Prerequisites

- Node.js 18+
- Python 3.10+
- Ollama installed locally (recommended). Install from https://ollama.com and pull a model:

```bash
ollama pull llama3.1:8b
```

## Install

```bash
# Backend
cd services/api
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# On Windows PowerShell:
# .\\.venv\\Scripts\\Activate.ps1
pip install -e .

# Frontend
cd ../../apps/web
npm install
```

## Run

```bash
# Terminal 1: backend
cd services/api
source .venv/bin/activate  # macOS/Linux
# On Windows PowerShell:
# .\\.venv\\Scripts\\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: frontend
cd apps/web
npm run dev
```

Open `http://localhost:3000`.

## One-command startup (optional)

```bash
docker compose up --build
```

## Troubleshooting

- **Ollama not reachable**: Ensure the Ollama app is running and `ollama pull llama3.1:8b` has completed.
- **CORS errors**: Confirm the backend is running on `http://localhost:8000`.
- **Dataset upload fails**: Ensure the file is CSV/XLSX/JSON/Parquet and not blocked by local antivirus.

## Import datasets from URLs (including Kaggle)

You can paste direct dataset URLs (CSV/JSON/XLSX/Parquet) or Kaggle dataset links in the Project view.

For Kaggle datasets you must provide credentials:

```bash
setx KAGGLE_USERNAME "your_username"
setx KAGGLE_KEY "your_key"
```

Or enter them in the UI when importing a Kaggle URL.

## Large files

Uploads are streamed to disk and profiling samples large files (over 100 MB) to keep memory use stable.

## Tests

```bash
# Backend
cd services/api
pytest

# Frontend
cd apps/web
npm run test
```

## Repository structure

```
apps/web          # Next.js UI
services/api      # FastAPI backend
packages/shared   # Shared schemas
sample-data       # Tiny sample datasets
```
