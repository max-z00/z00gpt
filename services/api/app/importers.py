from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path
from typing import Optional

import httpx

from . import db

KAGGLE_DATASET_RE = re.compile(r"kaggle\.com/datasets/([^/]+)/([^/?#]+)")


def parse_kaggle_url(url: str) -> Optional[str]:
    match = KAGGLE_DATASET_RE.search(url)
    if not match:
        return None
    owner, dataset = match.groups()
    return f"{owner}/{dataset}"


def import_dataset_from_kaggle(
    project_id: str,
    dataset_ref: str,
    filename: str | None,
    kaggle_username: str | None,
    kaggle_key: str | None,
) -> Path:
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError as exc:
        raise RuntimeError(
            "Kaggle support requires the 'kaggle' package. Install it in the API environment."
        ) from exc

    username = kaggle_username or os.getenv("KAGGLE_USERNAME")
    key = kaggle_key or os.getenv("KAGGLE_KEY")
    if not username or not key:
        raise RuntimeError(
            "Kaggle credentials are required. Provide kaggle_username/kaggle_key or set env vars."
        )

    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key

    api = KaggleApi()
    api.authenticate()

    project_dir = db.ensure_project_dir(project_id)
    api.dataset_download_files(dataset_ref, path=str(project_dir), quiet=True, force=True)

    zip_files = sorted(project_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not zip_files:
        raise RuntimeError("Failed to download Kaggle dataset archive.")
    download_path = zip_files[0]

    with zipfile.ZipFile(download_path, "r") as archive:
        archive.extractall(project_dir)

    if filename:
        candidate = project_dir / filename
        if candidate.exists():
            return candidate
        raise RuntimeError("Requested filename not found in Kaggle archive.")

    for ext in (".csv", ".parquet", ".xlsx", ".json"):
        for file in project_dir.glob(f"*{ext}"):
            return file

    raise RuntimeError("No supported dataset files found in Kaggle archive.")


async def import_dataset_from_url(
    project_id: str, url: str, filename: str | None
) -> Path:
    project_dir = db.ensure_project_dir(project_id)
    resolved_name = filename or url.split("/")[-1].split("?")[0]
    if not resolved_name:
        raise RuntimeError("Unable to infer filename from URL; please specify filename.")
    path = project_dir / resolved_name
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(path, "wb") as handle:
                async for chunk in response.aiter_bytes():
                    handle.write(chunk)
    return path
