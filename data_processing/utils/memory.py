"""Shrink DataFrames before writing them to disk."""

import pandas as pd


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to compact types.

    IDs become pandas strings instead of generic Python objects, and the
    millisecond timestamp (stored by Twitter as text) becomes a real datetime,
    which also makes time-based analysis possible.
    """
    df = df.copy()
    df["id"] = df["id"].astype("string")
    df["user_id"] = df["user_id"].astype("string")
    df["timestamp"] = pd.to_datetime(pd.to_numeric(df["timestamp"]), unit="ms")
    return df.reset_index(drop=True)
