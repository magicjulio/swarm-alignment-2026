import pandas as pd


def rollup(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.resample("W-MON", on="date").sum(numeric_only=True)
