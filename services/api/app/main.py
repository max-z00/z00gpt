from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, AsyncGenerator

import httpx
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from . import db
from .llm import DEVELOPER_PROMPT, FEW_SHOTS, SYSTEM_PROMPT, stream_ollama
from .profiling import preview_dataframe, profile_dataframe, read_dataset
from .tools import QueryError, build_chart_spec, run_sql, summarize_dataframe, tool_result_payload

app = FastAPI(title="LLM Data Analytics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatSettings(BaseModel):
    provider: str = "ollama"
    model: str = "llama3.1:8b"
    temperature: float = 0.2


class ChatRequest(BaseModel):
    project_id: str
    dataset_id: str | None = None
    messages: list[ChatMessage]
    settings: ChatSettings = Field(default_factory=ChatSettings)


@app.on_event("startup")
async def startup() -> None:
    db.init_db()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/projects")
async def list_projects() -> list[dict[str, Any]]:
    return db.to_dicts(db.list_projects())


@app.post("/projects")
async def create_project(payload: ProjectCreate) -> dict[str, Any]:
    project_id = str(uuid.uuid4())
    project = db.create_project(project_id, payload.name)
    return dict(project.__dict__)


@app.get("/projects/{project_id}")
async def get_project(project_id: str) -> dict[str, Any]:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return dict(project.__dict__)


@app.get("/projects/{project_id}/datasets")
async def list_datasets(project_id: str) -> list[dict[str, Any]]:
    datasets = db.list_datasets(project_id)
    return [
        {
            "id": dataset.id,
            "project_id": dataset.project_id,
            "filename": dataset.filename,
            "created_at": dataset.created_at,
            "profile": db.load_profile(dataset.profile_json),
        }
        for dataset in datasets
    ]


@app.post("/projects/{project_id}/datasets")
async def upload_dataset(project_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    content = await file.read()
    path = db.write_uploaded_file(project_id, file.filename, content)
    df = read_dataset(str(path))
    profile = profile_dataframe(df)
    dataset_id = str(uuid.uuid4())
    dataset = db.create_dataset(dataset_id, project_id, file.filename, str(path), profile)
    return {
        "id": dataset.id,
        "project_id": dataset.project_id,
        "filename": dataset.filename,
        "created_at": dataset.created_at,
        "profile": profile,
    }


@app.get("/datasets/{dataset_id}/profile")
async def get_dataset_profile(dataset_id: str) -> dict[str, Any]:
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db.load_profile(dataset.profile_json)


@app.get("/datasets/{dataset_id}/preview")
async def get_dataset_preview(dataset_id: str) -> dict[str, Any]:
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = read_dataset(dataset.path, max_rows=50)
    return preview_dataframe(df)


@app.get("/projects/{project_id}/runs")
async def list_runs(project_id: str) -> list[dict[str, Any]]:
    runs = db.list_runs(project_id)
    return [
        {
            "id": run.id,
            "project_id": run.project_id,
            "run_type": run.run_type,
            "created_at": run.created_at,
            "request": json.loads(run.request_json),
            "response": json.loads(run.response_json),
        }
        for run in runs
    ]


@app.get("/llm/test")
async def test_llm() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            response.raise_for_status()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@app.get("/runs/{run_id}/export")
async def export_run(run_id: str) -> dict[str, Any]:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    response = json.loads(run.response_json)
    markdown = "\n".join(
        [
            f"# Run {run.id}",
            "",
            f"**Type:** {run.run_type}",
            "",
            "## Answer",
            response.get("message", ""),
            "",
            "## Table",
            json.dumps(response.get("table"), indent=2),
            "",
            "## Chart",
            json.dumps(response.get("chart"), indent=2),
        ]
    )
    return {"markdown": markdown}


async def _tool_loop(request: ChatRequest) -> dict[str, Any]:
    dataset = None
    if request.dataset_id:
        dataset = db.get_dataset(request.dataset_id)
    if not dataset:
        return tool_result_payload(
            "Please upload and select a dataset before asking data questions.",
        )
    df = read_dataset(dataset.path)
    schema = {"columns": list(df.columns)}
    system_context = (
        f"Dataset schema: {schema}.\n"
        f"Profile summary: {db.load_profile(dataset.profile_json)}"
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": DEVELOPER_PROMPT},
        {"role": "system", "content": system_context},
    ]
    messages.extend(FEW_SHOTS)
    messages.extend([m.model_dump() for m in request.messages])

    model_text = ""
    try:
        async for token in stream_ollama(
            messages, request.settings.model, request.settings.temperature
        ):
            model_text += token
    except Exception:
        return tool_result_payload(
            "Ollama is not reachable. Please start Ollama and download the configured model.",
        )

    try:
        parsed = json.loads(model_text.strip())
    except json.JSONDecodeError:
        return tool_result_payload(
            "The model response could not be parsed. Try rephrasing your question.",
        )

    if parsed.get("type") == "tool":
        name = parsed.get("name")
        args = parsed.get("arguments") or {}
        try:
            if name == "run_sql":
                result = run_sql(df, args.get("query", ""))
                message = "Here is the result of the SQL query."
                chart = None
                if result["columns"]:
                    chart = build_chart_spec(
                        pd.DataFrame(result["rows"]), result["columns"][0], result["columns"][-1]
                    )
                return tool_result_payload(message, result, chart)
            if name == "summarize_dataframe":
                summary = summarize_dataframe(df)
                return tool_result_payload("Summary stats computed.", summary)
            if name == "plot":
                chart = build_chart_spec(df, args.get("x"), args.get("y"))
                return tool_result_payload("Chart spec generated.", None, chart)
        except QueryError as exc:
            return tool_result_payload(str(exc))
    if parsed.get("type") == "final":
        return tool_result_payload(
            parsed.get("message", ""), parsed.get("table"), parsed.get("chart")
        )
    return tool_result_payload("No actionable response from the model.")


@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest) -> EventSourceResponse:
    async def event_generator() -> AsyncGenerator[dict[str, str], None]:
        run_id = str(uuid.uuid4())
        yield {"event": "status", "data": json.dumps({"state": "thinking"})}
        response = await _tool_loop(payload)
        db.create_run(run_id, payload.project_id, "chat", payload.model_dump(), response)
        for token in response.get("message", "").split():
            yield {"event": "token", "data": json.dumps({"token": token + " "})}
            await asyncio.sleep(0.01)
        yield {"event": "final", "data": json.dumps({"run_id": run_id, **response})}

    return EventSourceResponse(event_generator())
