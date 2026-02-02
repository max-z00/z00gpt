# Security

## Sandbox decisions

- Only dataset files stored in `/data/{project_id}` are read by tools.
- `run_sql` only permits `SELECT` statements and blocks multi-statement input.
- Python execution is not exposed to the model; analysis uses DuckDB and pandas.

## Networking

- The app is local-first and does not make external network requests at runtime by default.
- The only outbound call is to a local LLM server (Ollama or llama.cpp).
- Optional Kaggle URL imports trigger outbound downloads when explicitly requested.

## Resource limits

- Dataset previews are capped at 50 rows.
- Queries return a preview capped at 200 rows.
- Profiling runs on the uploaded dataset and should be constrained to reasonable file sizes.
