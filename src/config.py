from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class APIConfig:
    amadeus_client_id: str = os.getenv("AMADEUS_CLIENT_ID", "")
    amadeus_client_secret: str = os.getenv("AMADEUS_CLIENT_SECRET", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    yelp_api_key: str = os.getenv("YELP_API_KEY", "")

@dataclass
class UserPrefs:
    target_temp_c: float = 24.0
    temp_tolerance: float = 6.0
    rain_tolerance_mm: float = 3.0
    categories: tuple = ("museums", "hiking", "beaches")

@dataclass
class Weights:
    w_cost: float = 0.35
    w_weather: float = 0.30
    w_activity: float = 0.20
    w_travel: float = 0.15