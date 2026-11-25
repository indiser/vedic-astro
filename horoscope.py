import httpx
from datetime import date

_cache = {}

def get_horoscope(sign: str) -> dict | None:
    key = (sign.lower(), date.today().isoformat())
    if key in _cache:
        return _cache[key]
    try:
        r = httpx.get(
            f"https://horoscope-api-alpha.vercel.app/horoscope/{sign.lower()}",
            timeout=10,
        )
        r.raise_for_status()
    except httpx.HTTPError:
        return None
    _cache[key] = r.json()
    return _cache[key]