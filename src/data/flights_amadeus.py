import requests
from typing import Dict, Any
from ..config import APIConfig

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
FLIGHTS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

def get_access_token(cfg: APIConfig) -> str:
    data = {
        "grant_type": "client_credentials",
        "client_id": cfg.amadeus_client_id,
        "client_secret": cfg.amadeus_client_secret,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def search_flights(cfg: APIConfig, origin: str, destination: str, depart_date: str, return_date: str, currency: str="USD") -> Dict[str, Any]:
    token = get_access_token(cfg)
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": depart_date,
        "returnDate": return_date,
        "adults": 1,
        "currencyCode": currency,
        "max": 20
    }
    r = requests.get(FLIGHTS_URL, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def cheapest_price_usd(flight_offers: Dict[str, Any]) -> float:
    prices = []
    for offer in flight_offers.get("data", []):
        try:
            prices.append(float(offer["price"]["grandTotal"]))
        except Exception:
            pass
    return min(prices) if prices else float("inf")