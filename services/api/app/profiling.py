from __future__ import annotations

import pandas as pd
import pyarrow.parquet as pq

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json", ".parquet"}


def read_dataset(path: str, max_rows: int | None = None) -> pd.DataFrame:
    suffix = path.lower().rsplit(".", 1)
    ext = f".{suffix[1]}" if len(suffix) == 2 else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    if ext == ".csv":
        return pd.read_csv(path, nrows=max_rows)
    if ext == ".xlsx":
        return pd.read_excel(path, nrows=max_rows)
    if ext == ".json":
        return pd.read_json(path)
    if ext == ".parquet":
        table = pq.read_table(path)
        if max_rows is not None and table.num_rows > max_rows:
            table = table.slice(0, max_rows)
        return table.to_pandas()
    raise ValueError(f"Unsupported file type: {ext}")


def profile_dataframe(df: pd.DataFrame) -> dict:
    row_count = len(df)
    columns = []
    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        unique = int(series.nunique(dropna=True))
        top_values = (
            series.value_counts(dropna=True).head(5).to_dict()
            if series.dtype == "object"
            else series.dropna().astype(str).value_counts().head(5).to_dict()
        )
        stats = {}
        if pd.api.types.is_numeric_dtype(series):
            stats = {
                "min": float(series.min()) if not series.empty else None,
                "max": float(series.max()) if not series.empty else None,
                "mean": float(series.mean()) if not series.empty else None,
            }
        columns.append(
            {
                "name": col,
                "dtype": str(series.dtype),
                "missing": missing,
                "missing_pct": round(missing / row_count * 100, 2) if row_count else 0,
                "unique": unique,
                "unique_pct": round(unique / row_count * 100, 2) if row_count else 0,
                "top_values": top_values,
                "stats": stats,
            }
        )
    missing_total = sum(col["missing"] for col in columns)
    duplicates = int(df.duplicated().sum())
    return {
        "row_count": row_count,
        "column_count": len(df.columns),
        "columns": columns,
        "data_health": {
            "missing_total": missing_total,
            "missing_pct": round(missing_total / (row_count * max(len(df.columns), 1)) * 100, 2)
            if row_count
            else 0,
            "duplicates": duplicates,
            "duplicate_pct": round(duplicates / row_count * 100, 2) if row_count else 0,
        },
    }


def preview_dataframe(df: pd.DataFrame, limit: int = 50) -> dict:
    preview = df.head(limit)
    return {
        "columns": list(preview.columns),
        "rows": preview.fillna("").to_dict(orient="records"),
        "row_count": len(df),
    }
