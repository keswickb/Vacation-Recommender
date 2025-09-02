import os, sys
import pandas as pd
import streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.config import APIConfig, UserPrefs, Weights
from src.data.collect import CITY_COORDS, estimate_travel_time_hours
from src.data.flights_amadeus import search_flights, cheapest_price_usd
from src.data.hotels_amadeus import avg_hotel_price_usd
from src.data.weather_openweather import weather_suitability_score
from src.data.places_yelp import activity_density
from src.features.engineer import build_feature_table
from src.models.recommender import score

st.set_page_config(page_title="Vacation Recommender", layout="wide")
st.title("🏝️ Vacation Recommendation & Cost Optimization")
st.caption("Live API data • Transparent scoring • Adjustable preferences")

cfg = APIConfig()
prefs = UserPrefs()

with st.sidebar:
    st.header("Inputs")
    origin = st.text_input("Origin IATA", value="JFK")
    trip_start = st.date_input("Start date")
    trip_end = st.date_input("End date")
    candidates = st.text_input("Candidate IATA (comma-separated)", value="MIA,LAX,LIS,BCN,YYZ")
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP"], index=0)

    st.divider()
    st.subheader("Preferences")
    prefs.target_temp_c = st.slider("Target temp (°C)", 10.0, 35.0, 24.0, 0.5)
    prefs.temp_tolerance = st.slider("Temp tolerance (±°C)", 2.0, 12.0, 6.0, 0.5)
    prefs.rain_tolerance_mm = st.slider("Rain tolerance (mm/3h avg)", 0.5, 10.0, 3.0, 0.5)
    categories = st.multiselect("Activity categories", ["museums","hiking","beaches","nightlife","shopping","parks"],
                                default=["museums","hiking","beaches"])

    st.divider()
    st.subheader("Weights")
    w = Weights(
        w_cost = st.slider("Weight: Cost", 0.0, 1.0, 0.35, 0.05),
        w_weather = st.slider("Weight: Weather", 0.0, 1.0, 0.30, 0.05),
        w_activity = st.slider("Weight: Activities", 0.0, 1.0, 0.20, 0.05),
        w_travel = st.slider("Weight: Travel time", 0.0, 1.0, 0.15, 0.05),
    )

def normalize_weights(w):
    total = max(1e-6, w.w_cost + w.w_weather + w.w_activity + w.w_travel)
    return Weights(
        w_cost = w.w_cost/total,
        w_weather = w.w_weather/total,
        w_activity = w.w_activity/total,
        w_travel = w.w_travel/total
    )

def run_pipeline(origin, start_str, end_str, candidates, currency, prefs, w, categories):
    origin = origin.upper()
    cand_codes = [c.strip().upper() for c in candidates.split(",") if c.strip()]
    origin_lat, origin_lon = CITY_COORDS.get(origin, CITY_COORDS["JFK"])

    rows = []
    for dest in cand_codes:
        dest_lat, dest_lon = CITY_COORDS.get(dest, (None, None))
        if dest_lat is None:
            continue
        # Flights
        try:
            fjson = search_flights(cfg, origin, dest, start_str, end_str, currency=currency)
            flight_usd = cheapest_price_usd(fjson)
        except Exception:
            flight_usd = float("inf")
        # Hotels
        try:
            avg_hotel = avg_hotel_price_usd(cfg, dest, start_str, end_str, currency=currency)
        except Exception:
            avg_hotel = float("inf")
        # Weather
        try:
            wscore = weather_suitability_score(cfg.openweather_api_key, dest_lat, dest_lon, prefs)
        except Exception:
            wscore = 0.0
        # Activities
        try:
            ascore = activity_density(cfg.yelp_api_key, dest_lat, dest_lon, tuple(categories))
        except Exception:
            ascore = 0.0

        travel_time_h = estimate_travel_time_hours(origin_lat, origin_lon, dest_lat, dest_lon)
        total_cost = (0 if flight_usd == float("inf") else flight_usd) + (0 if avg_hotel == float("inf") else avg_hotel)

        rows.append({
            "origin": origin,
            "destination": dest,
            "start_date": start_str,
            "end_date": end_str,
            "currency": currency,
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
    ranked = score(feat, normalize_weights(w))
    return ranked

col1, col2 = st.columns([1,2])
with col1:
    if st.button("Fetch live data and rank", type="primary"):
        if not (cfg.amadeus_client_id and cfg.amadeus_client_secret and cfg.openweather_api_key and cfg.yelp_api_key):
            st.error("Set your API keys in .env (Amadeus, OpenWeather, Yelp) and restart the app.")
        else:
            df = run_pipeline(origin, str(trip_start), str(trip_end), candidates, currency, prefs, w, categories)
            st.session_state["results_df"] = df

with col2:
    df = st.session_state.get("results_df")
    if df is not None:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download ranked CSV", data=csv, file_name="ranked_destinations.csv", mime="text/csv")
        try:
            import plotly.express as px
            fig = px.bar(df.head(10), x="destination", y="score",
                         hover_data=["total_cost_usd","weather_score","activity_score","travel_time_hours"])
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Install plotly for charts.")