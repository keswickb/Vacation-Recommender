import argparse, os
from ..config import APIConfig, UserPrefs
from .utils import save_json, haversine_km
from .flights_amadeus import search_flights, cheapest_price_usd
from .hotels_amadeus import avg_hotel_price_usd
from .weather_openweather import weather_suitability_score
from .places_yelp import activity_density
from ..features.engineer import build_feature_table
import pandas as pd

CITY_COORDS = {
    "JFK": (40.6413, -73.7781),
    "MIA": (25.7617, -80.1918),
    "LAX": (34.0522, -118.2437),
    "LIS": (38.7223, -9.1393),
    "BCN": (41.3874, 2.1686),
    "YYZ": (43.6532, -79.3832),
}

def estimate_travel_time_hours(origin_lat, origin_lon, dest_lat, dest_lon):
    dist_km = haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)
    return dist_km / 800.0 + 1.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--currency", default="USD")
    args = ap.parse_args()

    cfg = APIConfig()
    prefs = UserPrefs()

    origin = args.origin.upper()
    cand_codes = [c.strip().upper() for c in args.candidates.split(",") if c.strip()]

    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    origin_lat, origin_lon = CITY_COORDS.get(origin, CITY_COORDS["JFK"])

    rows = []
    for dest in cand_codes:
        dest_lat, dest_lon = CITY_COORDS.get(dest, (None, None))
        if dest_lat is None:
            print(f"[warn] Unknown coords for {dest}, skipping.")
            continue

        try:
            fjson = search_flights(cfg, origin, dest, args.start, args.end, currency=args.currency)
            save_json(fjson, f"data/raw/flights_{origin}_{dest}.json")
            flight_usd = cheapest_price_usd(fjson)
        except Exception as e:
            print(f"[err] Flights {origin}->{dest}: {e}")
            flight_usd = float("inf")

        try:
            avg_hotel = avg_hotel_price_usd(cfg, dest, args.start, args.end, currency=args.currency)
        except Exception as e:
            print(f"[err] Hotels {dest}: {e}")
            avg_hotel = float("inf")

        try:
            wscore = weather_suitability_score(cfg.openweather_api_key, dest_lat, dest_lon, prefs)
        except Exception as e:
            print(f"[err] Weather {dest}: {e}")
            wscore = 0.0

        try:
            ascore = activity_density(cfg.yelp_api_key, dest_lat, dest_lon, prefs.categories)
        except Exception as e:
            print(f"[err] Yelp {dest}: {e}")
            ascore = 0.0

        travel_time_h = estimate_travel_time_hours(origin_lat, origin_lon, dest_lat, dest_lon)
        total_cost = (0 if flight_usd == float("inf") else flight_usd) + (0 if avg_hotel == float("inf") else avg_hotel)

        rows.append({
            "origin": origin,
            "destination": dest,
            "start_date": args.start,
            "end_date": args.end,
            "currency": args.currency,
            "flight_cost_usd": None if flight_usd == float("inf") else flight_usd,
            "avg_hotel_usd": None if avg_hotel == float("inf") else avg_hotel,
            "total_cost_usd": None if total_cost == 0 else total_cost,
            "weather_score": wscore,
            "activity_score": ascore,
            "travel_time_hours": travel_time_h,
            "lat": dest_lat,
            "lon": dest_lon
        })

    feat = build_feature_table(rows)
    feat.to_csv("data/processed/candidates_features.csv", index=False)
    print("Saved: data/processed/candidates_features.csv")

if __name__ == "__main__":
    main()