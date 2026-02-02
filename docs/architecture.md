# Architecture

## Request flow

1. User creates a project in the web app.
2. Uploads a dataset to `/projects/{id}/datasets`.
3. Backend stores the file locally in `/data/{project_id}` and profiles it.
4. Chat messages are sent to `/chat/stream` with dataset context.
5. The tool loop evaluates the model response and executes safe tools.

## Tool loop

- System prompt and developer prompt guide the model to output tool calls.
- The backend validates tool requests and executes:
  - `run_sql` (read-only) via DuckDB
  - `summarize_dataframe`
  - `plot` for chart specs
- Tool responses are streamed back to the client and logged as runs.

## Storage

- SQLite database in `data/app.db` stores projects, datasets, and runs.
- Dataset files are stored in `data/{project_id}/` and referenced by path.
