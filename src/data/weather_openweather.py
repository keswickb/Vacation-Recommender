import requests
from ..config import UserPrefs

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def kelvin_to_c(k: float) -> float:
    return k - 273.15

def weather_suitability_score(api_key: str, lat: float, lon: float, prefs: UserPrefs) -> float:
    params = {"lat": lat, "lon": lon, "appid": api_key}
    r = requests.get(FORECAST_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    temps_c, rains = [], []
    for it in data.get("list", []):
        temps_c.append(kelvin_to_c(it.get("main", {}).get("temp", 293.15)))
        rains.append(it.get("rain", {}).get("3h", 0.0))
    if not temps_c:
        return 0.0
    avg_temp = sum(temps_c)/len(temps_c)
    avg_rain = sum(rains)/len(rains) if rains else 0.0
    temp_penalty = min(1.0, abs(avg_temp - prefs.target_temp_c) / max(1.0, prefs.temp_tolerance))
    rain_penalty = min(1.0, avg_rain / max(0.1, prefs.rain_tolerance_mm))
    score = max(0.0, 1.0 - 0.6*temp_penalty - 0.4*rain_penalty)
    return score