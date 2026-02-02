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
source .venv/bin/activate
pip install -e .

# Frontend
cd ../../apps/web
npm install
```

## Run

```bash
# Terminal 1: backend
cd services/api
source .venv/bin/activate
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
- **Dataset upload fails**: Ensure the file is CSV/XLSX/JSON/Parquet and under 50 MB.

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
