from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
        "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
        "Rahu": "Ra", "Ketu": "Ke"}


def _font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def draw_north_indian(c: dict, size: int = 800) -> BytesIO:
    S, pad = size, 40
    img = Image.new("RGB", (S + 2 * pad, S + 2 * pad + 50), "white")
    d = ImageDraw.Draw(img)

    def P(x, y):  # unit coords 0..1 -> pixels
        return (pad + x * S, pad + y * S)

    A, B, C, D = P(0, 0), P(1, 0), P(1, 1), P(0, 1)
    T, R, Bm, L = P(.5, 0), P(1, .5), P(.5, 1), P(0, .5)
    O = P(.5, .5)
    p1, p2, p3, p4 = P(.25, .25), P(.75, .25), P(.75, .75), P(.25, .75)

    # house polygons, house 1..12, anticlockwise from top center
    houses = [
        [T, p1, O, p2],    # 1
        [A, T, p1],        # 2
        [A, p1, L],        # 3
        [L, p1, O, p4],    # 4
        [L, p4, D],        # 5
        [D, p4, Bm],       # 6
        [Bm, p4, O, p3],   # 7
        [Bm, p3, C],       # 8
        [C, p3, R],        # 9
        [R, p3, O, p2],    # 10
        [R, p2, B],        # 11
        [B, p2, T],        # 12
    ]

    # lines
    w = 3
    d.rectangle([A, C], outline="black", width=w)
    d.line([A, C], fill="black", width=w)
    d.line([B, D], fill="black", width=w)
    d.polygon([T, R, Bm, L], outline="black", width=w)

    # planets per house
    by_house = {h: [] for h in range(1, 13)}
    for name, g in c["grahas"].items():
        tag = ABBR[name] + ("(R)" if g["retro"] and name not in ("Rahu", "Ketu") else "")
        by_house[g["house"]].append(tag)
    by_house[1].insert(0, "Asc")

    lagna_idx = c["lagna"]["sign_idx"]
    f_sign, f_pl = _font(26), _font(30)

    for h, poly in enumerate(houses, start=1):
        cx = sum(x for x, _ in poly) / len(poly)
        cy = sum(y for _, y in poly) / len(poly)

        # sign number: nearest vertex to chart center, pulled toward centroid
        vx, vy = min(poly, key=lambda v: (v[0] - O[0]) ** 2 + (v[1] - O[1]) ** 2)
        lx, ly = vx + .3 * (cx - vx), vy + .3 * (cy - vy)
        sign_no = (lagna_idx + h - 1) % 12 + 1
        d.text((lx, ly), str(sign_no), font=f_sign, fill="#b00020", anchor="mm")

        # planets: centroid pushed slightly away from sign label
        px, py = cx + .15 * (cx - lx), cy + .15 * (cy - ly)
        items = by_house[h]
        gap = 34
        y0 = py - gap * (len(items) - 1) / 2
        for i, t in enumerate(items):
            d.text((px, y0 + i * gap), t, font=f_pl, fill="black", anchor="mm")

    d.text(((S + 2 * pad) / 2, S + 2 * pad + 20),
           f"Lahiri sidereal, whole sign, mean node. Lagna {c['lagna']['sign']}",
           font=_font(22), fill="#444", anchor="mm")

    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf