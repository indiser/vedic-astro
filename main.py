import math
from datetime import datetime, timezone

from flask import Flask, render_template, request

from places import search_place, tz_for
from timeutil import to_utc
from chart import compute_chart
from dasha import compute_dasha

from flask import send_file
from chart_png import draw_north_indian
import base64

from horoscope import get_horoscope

app = Flask(__name__)

@app.get("/")
def form():
    return render_template("form.html", error=None)


@app.post("/search")
def search():
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    place = request.form.get("place", "").strip()
    if not (date and time and place):
        return render_template("form.html", error="fill all fields")
    try:
        matches = search_place(place)
    except Exception:
        return render_template("form.html", error="place lookup failed. try again.")
    if not matches:
        return render_template("form.html", error="no place found")
    return render_template("pick.html", matches=matches, date=date, time=time)


@app.post("/chart")
def chart():
    try:
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        date = request.form["date"]
        time = request.form["time"]
        if not (math.isfinite(lat) and math.isfinite(lon)):
            raise ValueError("bad coordinates")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("coordinates out of range")
        tz = tz_for(lat, lon)
        utc = to_utc(date, time, tz)
        c = compute_chart(utc, lat, lon)
        d = compute_dasha(
            c["grahas"]["Moon"]["lon"], utc, datetime.now(timezone.utc)
        )
        h = get_horoscope(c["grahas"]["Moon"]["sign"])
        png = base64.b64encode(draw_north_indian(c).getvalue()).decode()
    except (KeyError, ValueError) as e:
        return render_template("form.html", error=str(e))
    return render_template("result.html", c=c, d=d, tz=tz, utc=utc, png=png, h=h)


if __name__ == "__main__":
    app.run(debug=True)