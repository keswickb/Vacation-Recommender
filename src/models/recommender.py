import pandas as pd
from ..config import Weights

def score(df: pd.DataFrame, w: Weights) -> pd.DataFrame:
    out = df.copy()
    total = max(1e-6, w.w_cost + w.w_weather + w.w_activity + w.w_travel)
    wc, ww, wa, wt = w.w_cost/total, w.w_weather/total, w.w_activity/total, w.w_travel/total
    out["score"] = (
        wc * (1.0 - out["norm_total_cost"]) +
        ww * out["weather_score"] +
        wa * out["activity_score"] +
        wt * (1.0 - out["norm_travel_time"])
    )
    return out.sort_values("score", ascending=False)