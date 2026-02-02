import pandas as pd

from app.profiling import profile_dataframe


def test_profile_dataframe_basic():
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "x", "y"]})
    profile = profile_dataframe(df)
    assert profile["row_count"] == 3
    assert profile["column_count"] == 2
    assert profile["columns"][0]["missing"] == 1
    assert profile["data_health"]["duplicates"] == 0
