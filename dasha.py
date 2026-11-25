# dasha.py
from datetime import datetime, timedelta, timezone

ORDER = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
         ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
TOTAL = 120
DAYS_PER_YEAR = 365.25
NAK = 360 / 27


def _plus(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * DAYS_PER_YEAR)


def _antardashas(lord_idx: int, start: datetime) -> list[dict]:
    maha_years = ORDER[lord_idx][1]
    out, t = [], start
    for k in range(9):
        name, yrs = ORDER[(lord_idx + k) % 9]
        length = maha_years * yrs / TOTAL
        end = _plus(t, length)
        out.append({"lord": name, "start": t, "end": end})
        t = end
    return out


def compute_dasha(moon_lon: float, birth_utc: datetime, as_of: datetime) -> dict:
    moon_lon %= 360
    nak_idx = int(moon_lon // NAK)
    first = nak_idx % 9
    elapsed = (moon_lon % NAK) / NAK
    first_years = ORDER[first][1]
    balance = first_years * (1 - elapsed)

    # first maha started BEFORE birth. rewind by elapsed part
    t = _plus(birth_utc, -first_years * elapsed)

    mahas = []
    for k in range(9):
        idx = (first + k) % 9
        name, yrs = ORDER[idx]
        end = _plus(t, yrs)
        mahas.append({"lord": name, "years": yrs, "start": t, "end": end, "idx": idx})
        t = end

    current = next((m for m in mahas if m["start"] <= as_of < m["end"]), None)
    antars, current_antar = [], None
    if current:
        antars = _antardashas(current["idx"], current["start"])
        current_antar = next((a for a in antars if a["start"] <= as_of < a["end"]), None)

    return {
        "birth_lord": ORDER[first][0],
        "balance_years": round(balance, 4),
        "year_days": DAYS_PER_YEAR,
        "mahadashas": mahas,
        "current_maha": current,
        "antardashas": antars,
        "current_antar": current_antar,
    }