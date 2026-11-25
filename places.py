import time
from curl_cffi import requests
from timezonefinder import TimezoneFinder

_cache = {}
_last_call = 0.0
_tf = TimezoneFinder()

def search_place(query: str, country: str = "in") -> list[dict]:
    global _last_call
    key = (query.strip().lower(), country)
    if key in _cache:
        return _cache[key]

    wait = 1.0 - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)

    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "jsonv2", "limit": 5, "countrycodes": country},
        headers={"User-Agent": "vedic-astro-learning/0.1 (your.real.email@gmail.com)"},
        impersonate="chrome",
        timeout=10,
    )
    _last_call = time.time()
    r.raise_for_status()

    result = [
        {"name": x["display_name"], "lat": float(x["lat"]), "lon": float(x["lon"])}
        for x in r.json()
    ]
    _cache[key] = result
    return result

def tz_for(lat: float, lon: float) -> str:
    name = _tf.timezone_at(lat=lat, lng=lon)
    if not name:
        raise ValueError("no timezone found for these coordinates. ask user.")
    return name