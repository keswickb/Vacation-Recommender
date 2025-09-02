import pandas as pd

def minmax(series: pd.Series) -> pd.Series:
    if series.nunique() <= 1:
        return pd.Series([0.0]*len(series), index=series.index)
    return (series - series.min()) / (series.max() - series.min())

def build_feature_table(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame.from_records(records)
    df["norm_total_cost"] = minmax(df["total_cost_usd"])
    df["norm_travel_time"] = minmax(df["travel_time_hours"])
    return df