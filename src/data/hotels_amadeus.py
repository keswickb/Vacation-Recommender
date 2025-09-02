import requests
from ..config import APIConfig

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
HOTEL_OFFERS_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"

def get_access_token(cfg: APIConfig) -> str:
    data = {
        "grant_type": "client_credentials",
        "client_id": cfg.amadeus_client_id,
        "client_secret": cfg.amadeus_client_secret,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def avg_hotel_price_usd(cfg: APIConfig, city_code: str, check_in: str, check_out: str, currency: str="USD") -> float:
    token = get_access_token(cfg)
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "cityCode": city_code,
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": 1,
        "currencyCode": currency
    }
    r = requests.get(HOTEL_OFFERS_URL, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    prices = []
    for d in data.get("data", []):
        for o in d.get("offers", []):
            try:
                prices.append(float(o["price"]["total"]))
            except Exception:
                pass
    return sum(prices)/len(prices) if prices else float("inf")