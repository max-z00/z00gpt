from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


@dataclass
class Project:
    id: str
    name: str
    created_at: str


@dataclass
class Dataset:
    id: str
    project_id: str
    filename: str
    path: str
    created_at: str
    profile_json: str


@dataclass
class Run:
    id: str
    project_id: str
    run_type: str
    request_json: str
    response_json: str
    created_at: str


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            profile_json TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            run_type TEXT NOT NULL,
            request_json TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        """
    )
    conn.commit()
    conn.close()


def _now() -> str:
    return datetime.utcnow().isoformat()


def create_project(project_id: str, name: str) -> Project:
    conn = _connect()
    created_at = _now()
    conn.execute(
        "INSERT INTO projects (id, name, created_at) VALUES (?, ?, ?)",
        (project_id, name, created_at),
    )
    conn.commit()
    conn.close()
    return Project(id=project_id, name=name, created_at=created_at)


def list_projects() -> list[Project]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    conn.close()
    return [Project(**dict(row)) for row in rows]


def get_project(project_id: str) -> Project | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return Project(**dict(row)) if row else None


def create_dataset(
    dataset_id: str,
    project_id: str,
    filename: str,
    path: str,
    profile: dict[str, Any],
) -> Dataset:
    conn = _connect()
    created_at = _now()
    profile_json = json.dumps(profile)
    conn.execute(
        """
        INSERT INTO datasets (id, project_id, filename, path, created_at, profile_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (dataset_id, project_id, filename, path, created_at, profile_json),
    )
    conn.commit()
    conn.close()
    return Dataset(
        id=dataset_id,
        project_id=project_id,
        filename=filename,
        path=path,
        created_at=created_at,
        profile_json=profile_json,
    )


def list_datasets(project_id: str) -> list[Dataset]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM datasets WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [Dataset(**dict(row)) for row in rows]


def get_dataset(dataset_id: str) -> Dataset | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    conn.close()
    return Dataset(**dict(row)) if row else None


def create_run(
    run_id: str,
    project_id: str,
    run_type: str,
    request_payload: dict[str, Any],
    response_payload: dict[str, Any],
) -> Run:
    conn = _connect()
    created_at = _now()
    conn.execute(
        """
        INSERT INTO runs (id, project_id, run_type, request_json, response_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            project_id,
            run_type,
            json.dumps(request_payload),
            json.dumps(response_payload),
            created_at,
        ),
    )
    conn.commit()
    conn.close()
    return Run(
        id=run_id,
        project_id=project_id,
        run_type=run_type,
        request_json=json.dumps(request_payload),
        response_json=json.dumps(response_payload),
        created_at=created_at,
    )


def list_runs(project_id: str) -> list[Run]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM runs WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [Run(**dict(row)) for row in rows]


def get_run(run_id: str) -> Run | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    return Run(**dict(row)) if row else None


def ensure_project_dir(project_id: str) -> Path:
    project_dir = DATA_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def write_uploaded_file(project_id: str, filename: str, content: bytes) -> Path:
    project_dir = ensure_project_dir(project_id)
    safe_name = os.path.basename(filename)
    path = project_dir / safe_name
    path.write_bytes(content)
    return path


def load_profile(profile_json: str) -> dict[str, Any]:
    return json.loads(profile_json)


def to_dicts(items: Iterable[Any]) -> list[dict[str, Any]]:
    return [dict(item.__dict__) for item in items]
