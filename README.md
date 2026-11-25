<div align="center">

# ☽ Jyotish Observatory

**A precision Vedic astrology engine — Lahiri sidereal, whole-sign houses, mean node**

[![Python](https://img.shields.io/badge/Python-3.14%2B-gold?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-gold?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Swiss Ephemeris](https://img.shields.io/badge/Swiss%20Ephemeris-pysweph-blueviolet?style=flat-square)](https://pypi.org/project/pysweph/)
[![License](https://img.shields.io/badge/License-MIT-cyan?style=flat-square)](LICENSE)

</div>

---

## Overview

Jyotish Observatory is a full-stack Vedic astrology web application that computes a **Janma Kundali** (natal birth chart) from a date, time, and place of birth. It uses the Swiss Ephemeris for sub-arcsecond planetary accuracy, applies the **Lahiri ayanamsa** for sidereal correction, and renders a North Indian diamond chart as a downloadable PNG. Vimshottari Dasha periods and a live daily horoscope are also computed and displayed.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Flask App (main.py)                  │
│                                                             │
│   GET /          POST /search          POST /chart          │
│   form.html  →   pick.html         →   result.html          │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
  places.py          places.py         chart.py  ──► Swiss Ephemeris
  (Nominatim)        (tz_for)          dasha.py
                                       chart_png.py (Pillow)
                                       horoscope.py (httpx API)
```

**Request flow:**
1. User submits birth date, time, and place name on `form.html`
2. `/search` geocodes the place via Nominatim → user picks from up to 5 matches on `pick.html`
3. `/chart` resolves the timezone, converts local time to UTC, computes the full chart, dasha, and horoscope, then renders `result.html`

---

## Features

| Feature | Detail |
|---|---|
| **Sidereal Chart** | Lahiri ayanamsa via Swiss Ephemeris (`pysweph`) |
| **9 Grahas + Lagna** | Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu + Ascendant |
| **27 Nakshatras** | Ashwini → Revati, with pada (1–4) |
| **Whole-Sign Houses** | House number derived from sign offset from Lagna |
| **Retrograde Detection** | Speed < 0 for all planets; Rahu/Ketu always retrograde |
| **Vimshottari Dasha** | Full 120-year cycle, current Maha + Antardasha highlighted |
| **North Indian Chart PNG** | Pillow-rendered diamond layout, downloadable, night-invert toggle |
| **Geocoding** | Nominatim (OpenStreetMap) via `curl_cffi` with 1 s rate-limit |
| **Timezone Resolution** | `timezonefinder` from lat/lon, DST gap/fold detection |
| **Daily Horoscope** | Moon-sign horoscope fetched from external API, in-memory cached |

---

## Tech Stack

| Layer | Library |
|---|---|
| Web framework | `Flask 3.x` |
| Ephemeris | `pysweph` (Swiss Ephemeris MOSHIER mode, sidereal) |
| Chart rendering | `Pillow` |
| Geocoding | `curl_cffi` → Nominatim |
| Timezone | `timezonefinder`, `tzdata`, stdlib `zoneinfo` |
| HTTP client | `httpx` (horoscope API) |
| Runtime | Python 3.14+, `uv` package manager |

---

## Module Reference

### `chart.py` — Ephemeris Engine
Computes the full sidereal chart for a given UTC datetime and coordinates.

- `compute_chart(utc, lat, lon) → dict` — returns `lagna`, `grahas`, and `ayanamsa`
- Uses `swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED`
- Ketu is derived as `Rahu longitude + 180°`
- Each graha carries: `lon`, `sign`, `sign_idx`, `deg_in_sign`, `nakshatra`, `pada`, `house`, `retro`

### `dasha.py` — Vimshottari Dasha Calculator
Implements the classical 120-year Vimshottari cycle.

- `compute_dasha(moon_lon, birth_utc, as_of) → dict`
- Determines birth nakshatra lord and remaining balance from Moon's position within the nakshatra
- Computes all 9 Mahadashas and 9 Antardashas within the current Maha
- Returns `current_maha`, `current_antar`, `birth_lord`, `balance_years`

**Dasha order & years:**

| Lord | Years | Lord | Years | Lord | Years |
|------|-------|------|-------|------|-------|
| Ketu | 7 | Rahu | 18 | Mercury | 17 |
| Venus | 20 | Jupiter | 16 | — | — |
| Sun | 6 | Saturn | 19 | — | — |
| Moon | 10 | Mars | 7 | — | — |

### `places.py` — Geocoding & Timezone
- `search_place(query, country="in") → list[dict]` — queries Nominatim, returns up to 5 `{name, lat, lon}` results; 1 s rate-limit enforced; in-memory cached
- `tz_for(lat, lon) → str` — resolves IANA timezone string via `timezonefinder`

### `timeutil.py` — UTC Conversion
- `to_utc(date, time, tz_name) → datetime` — converts local time string to UTC; raises `TimeError` on DST gaps or ambiguous folds using `fold=0/1` disambiguation

### `chart_png.py` — North Indian Chart Renderer
- `draw_north_indian(c, size=800) → BytesIO` — renders the classic diamond-grid North Indian Kundali using Pillow
- 12 house polygons laid out from top-center anticlockwise
- Sign numbers in red, planet abbreviations in black, retrograde tagged `(R)`
- Returns a PNG byte stream (base64-encoded for inline HTML embedding)

### `horoscope.py` — Daily Horoscope
- `get_horoscope(sign) → dict | None` — fetches today's horoscope for the Moon sign from an external API; cached per sign per day

### `main.py` — Flask Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Birth data input form |
| `/search` | POST | Geocode place, show selection |
| `/chart` | POST | Compute and render full chart |

---

## Installation

**Prerequisites:** Python 3.14+, [`uv`](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/indiser/vedic-astro.git
cd vedic-astro

# Install dependencies
uv sync

# Run the development server
uv run python main.py
```

Open `http://127.0.0.1:5000` in your browser.

Alternatively with pip:

```bash
pip install -r requirements.txt
python main.py
```

---

## Usage

1. Enter a **birth date**, **local time** (24h), and **place name**
2. Select the correct location from the geocoded results
3. The chart page displays:
   - Telemetry strip: Lagna, Moon sign/nakshatra, timezone/UTC, Vimshottari birth lord, current Maha/Antardasha
   - North Indian Kundali PNG (downloadable, night-invert toggle)
   - Graha table with sign, degree, house, nakshatra, pada, retrograde status
   - Full Vimshottari Maha/Antardasha timeline with current period highlighted
   - Moon-sign daily horoscope (love, finance, career, health)

---

## Astrological Methodology

- **Ayanamsa:** Lahiri (Chitrapaksha) — the standard for Indian Jyotish
- **House system:** Whole-sign — each sign = one house, Lagna sign = house 1
- **Node calculation:** Mean node (not true/osculating)
- **Epoch:** Julian Day (UT) via `swe.julday`; all planetary positions in UT
- **Dasha year:** 365.25 days

---

## Project Structure

```
vedic-astro/
├── main.py           # Flask app & routes
├── chart.py          # Swiss Ephemeris chart computation
├── dasha.py          # Vimshottari dasha engine
├── places.py         # Geocoding + timezone resolution
├── timeutil.py       # Local → UTC conversion with DST handling
├── chart_png.py      # North Indian chart PNG renderer
├── horoscope.py      # Daily horoscope API client
├── templates/
│   ├── form.html     # Birth data input
│   ├── pick.html     # Place selection
│   └── result.html   # Full chart display
├── static/
│   ├── static.css    # Deep-space glassmorphism UI
│   └── static.js     # Starfield canvas, loaders, interactivity
├── pyproject.toml
└── requirements.txt
```

---

<div align="center">
<sub>☽ Lahiri Sidereal · Whole-Sign Houses · Mean Node · Vimshottari Dasha ☽</sub>
</div>
