import swisseph as swe
from datetime import datetime

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra",
         "Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"]

PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
           "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
           "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}

FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED


def _describe(lon: float) -> dict:
    lon %= 360
    sign = int(lon // 30)
    n = lon / (360 / 27)
    return {
        "lon": round(lon, 4),
        "sign": SIGNS[sign],
        "sign_idx": sign,
        "deg_in_sign": round(lon % 30, 4),
        "nakshatra": NAKSHATRAS[int(n)],
        "pada": int((n % 1) * 4) + 1,
    }


def compute_chart(utc: datetime, lat: float, lon: float) -> dict:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    jd = swe.julday(utc.year, utc.month, utc.day, hour)  # UT
    
    res = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
    ascmc = res[1]
    lagna = _describe(ascmc[0])

    grahas = {}
    for name, pid in PLANETS.items():
        res = swe.calc_ut(jd, pid, FLAGS)
        pos = res[0]
        d = _describe(pos[0])
        d["retro"] = True if name == "Rahu" else pos[3] < 0
        grahas[name] = d

    ketu = _describe(grahas["Rahu"]["lon"] + 180)
    ketu["retro"] = True
    grahas["Ketu"] = ketu

    for g in grahas.values():
        g["house"] = (g["sign_idx"] - lagna["sign_idx"]) % 12 + 1

    return {"ayanamsa": round(swe.get_ayanamsa_ut(jd), 4),
            "lagna": lagna, "grahas": grahas}
