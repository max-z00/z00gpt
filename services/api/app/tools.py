from __future__ import annotations

import re
from typing import Any

import duckdb
import pandas as pd

READ_ONLY_PATTERN = re.compile(r"^\s*select\s", re.IGNORECASE)


class QueryError(ValueError):
    pass


def validate_sql(query: str) -> None:
    if not READ_ONLY_PATTERN.match(query):
        raise QueryError("Only SELECT queries are allowed.")
    if ";" in query.strip().strip(";"):
        raise QueryError("Multiple statements are not allowed.")


def run_sql(df: pd.DataFrame, query: str, limit: int = 200) -> dict[str, Any]:
    validate_sql(query)
    conn = duckdb.connect(database=":memory:")
    conn.register("dataset", df)
    try:
        result = conn.execute(query).fetchdf()
    finally:
        conn.close()
    preview = result.head(limit)
    return {
        "columns": list(preview.columns),
        "rows": preview.fillna("").to_dict(orient="records"),
        "row_count": len(result),
    }


def summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    numeric = df.select_dtypes(include="number")
    summary = {}
    if not numeric.empty:
        summary = numeric.describe().to_dict()
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "numeric_summary": summary,
    }


def build_chart_spec(df: pd.DataFrame, x: str, y: str) -> dict[str, Any]:
    if x not in df.columns or y not in df.columns:
        raise QueryError("Columns not found for chart.")
    return {
        "type": "bar",
        "x": x,
        "y": y,
        "data": df[[x, y]].dropna().to_dict(orient="records"),
    }


def tool_result_payload(message: str, table: dict | None = None, chart: dict | None = None) -> dict:
    return {
        "message": message,
        "table": table,
        "chart": chart,
    }
