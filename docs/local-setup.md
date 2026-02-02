# Local setup

## Ollama

1. Install Ollama from https://ollama.com.
2. Pull a model:

```bash
ollama pull llama3.1:8b
```

## Backend

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# On Windows PowerShell:
# .\\.venv\\Scripts\\Activate.ps1
pip install -e .
uvicorn app.main:app --reload
```

## Frontend

```bash
cd apps/web
npm install
npm run dev
```

## Kaggle credentials (optional)

Kaggle downloads require API credentials.

Windows PowerShell:

```powershell
[Environment]::SetEnvironmentVariable("KAGGLE_USERNAME", "your_username", "User")
[Environment]::SetEnvironmentVariable("KAGGLE_KEY", "your_key", "User")
```

macOS/Linux:

```bash
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_key"
```
