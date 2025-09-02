import requests

YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"

def activity_density(yelp_key: str, lat: float, lon: float, categories=("museums","hiking","beaches")) -> float:
    headers = {"Authorization": f"Bearer {yelp_key}"}
    total = 0
    for cat in categories:
        params = {"latitude": lat, "longitude": lon, "categories": cat, "limit": 50}
        r = requests.get(YELP_SEARCH_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        total += len(r.json().get("businesses", []))
    return min(1.0, total / 150.0)