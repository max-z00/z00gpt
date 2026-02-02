import pandas as pd
import pytest

from app.tools import QueryError, run_sql


def test_run_sql_select():
    df = pd.DataFrame({"category": ["A", "A", "B"], "value": [1, 2, 3]})
    result = run_sql(df, "SELECT category, AVG(value) AS avg_value FROM dataset GROUP BY category")
    assert result["row_count"] == 2
    assert "avg_value" in result["columns"]


def test_run_sql_rejects_non_select():
    df = pd.DataFrame({"x": [1]})
    with pytest.raises(QueryError):
        run_sql(df, "DELETE FROM dataset")
