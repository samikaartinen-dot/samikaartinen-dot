"""Sami's Workshop – living GitHub profile scene.

render(data) -> SVG string. A daily GitHub Action will fill `data` with real
contributions, weather, date and time. DEMO_* dicts are sample data.
"""
import math
import random
from datetime import date
from xml.sax.saxutils import escape

from themes import themes_for

W, H = 1200, 680
S = 36                                   # px per iso unit
C30 = math.cos(math.radians(30))
CX, CY = S * C30, S * 0.5
OX, OY = 600, 264                        # back floor corner
FONT = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

WOOD = ("#d9b47a", "#b5874c", "#8c6434")
WOOD_L = ("#e8c48c", "#c79a5d", "#b5874c")
DARKWOOD = ("#6b4a2e", "#7a5534", "#5e4128")
METAL = ("#c3c8d8", "#9aa1b8", "#7d849b")
BLACK = ("#2b2f3d", "#22252f", "#1b1d25")
# rough Helsinki sunrise/sunset hours per month
DAYLIGHT = {1: (9, 15), 2: (8, 17), 3: (7, 18), 4: (6, 20), 5: (5, 22), 6: (4, 23),
            7: (4, 23), 8: (6, 21), 9: (7, 19), 10: (8, 17), 11: (8, 16), 12: (9, 15)}
LED_LEVELS = ["#1b2232", "#0e4429", "#006d32", "#26a641", "#39d353"]

DEMO_DATA = {
    "name": "Sami Kaartinen",
    "date": "2026-11-23",
    "hour": 22,
    "contributions": None,          # 64 daily counts, oldest first (None = demo)
    "year_total": 412,
    "streak": 12,
    "today_commits": 4,
    "week_commits": 9,
    "days_since_commit": 0,
    "languages": [("PY", 45), ("JS", 25), ("C++", 20), ("SVG", 10)],
    "weather": {"city": "Helsinki", "temp": -3, "kind": "snow"},
    "now_building": "MANEK V2",
    "learning": "Python",
    "last_commit": "feat: LED grid",
    "latest_repo": "manek-v2",
    "scoreboard": ("CODE", 7, "BUGS", 2),
    "todos": [("KiCad PCB", "#ffd84a"), ("firmware", "#ff8fb0"), ("README", "#8ef0a8")],
    "visitors": 1287,
    "countdown": None,              # (label, "YYYY-MM-DD") or None = Christmas Eve
    "projects": [("MANEK V2", 62), ("Liigamanageri", 40), ("Python MOOC", 35), ("GitHub profile", 80)],
    "flap_words": ["SAMI", "MAKER", "TEACHER", "AI DEV"],
    "trophies": [("First repo", True), ("100 commits", True), ("Profile", True),
                 ("MOOC Python", False), ("MANEK proto", False), ("First job", False)],
}

DEMO_DEC6 = dict(DEMO_DATA, date="2026-12-06", hour=17, today_commits=0, days_since_commit=4, latest_repo="liigamanageri",
                 weather={"city": "Helsinki", "temp": -8, "kind": "clear"},
                 trophies=[("First repo", True), ("100 commits", True), ("Profile", True),
                           ("MOOC Python", True), ("MANEK proto", False), ("First job", False)])


# ------------------------------------------------------------------ helpers
def iso(x, y, z=0.0):
    return OX + (x - y) * CX, OY + (x + y) * CY - z * S


def pts(points):
    return " ".join(f"{px:.1f},{py:.1f}" for px, py in points)


def poly(points, fill, extra=""):
    return f'<polygon points="{pts(points)}" fill="{fill}" {extra}/>'


def quad(a, b, c, d, fill, extra=""):
    return poly([iso(*a), iso(*b), iso(*c), iso(*d)], fill, extra)


def box(x, y, z, w, d, h, colors, extra=""):
    top, left, right = colors
    return "".join([
        quad((x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h), left, extra),
        quad((x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h), right, extra),
        quad((x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h), top, extra),
    ])


def line(p, q, color, width, extra=""):
    (x1, y1), (x2, y2) = iso(*p), iso(*q)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" {extra}/>'


def m_xplane(px, py):   # plane y=const, text along +x (right wall, monitor, +y faces)
    return f"matrix({C30:.4f} 0.5 0 1 {px:.1f} {py:.1f})"


def m_yplane(px, py):   # plane x=const, text along -y (left wall, +x faces)
    return f"matrix({C30:.4f} -0.5 0 1 {px:.1f} {py:.1f})"


def m_top(px, py):      # horizontal plane, text along +x
    return f"matrix({C30:.4f} 0.5 {-C30:.4f} 0.5 {px:.1f} {py:.1f})"


def level(n):
    return 0 if n <= 0 else 1 if n <= 2 else 2 if n <= 4 else 3 if n <= 7 else 4


def gear_path(r, teeth, depth=0.22):
    p = []
    for k in range(teeth * 4):
        ang = 2 * math.pi * k / (teeth * 4)
        rr = r if (k % 4) in (0, 1) else r * (1 - depth)
        p.append((rr * math.cos(ang), rr * math.sin(ang)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in p) + " Z"


FI_MONTHS = ["TAMMIKUU", "HELMIKUU", "MAALISKUU", "HUHTIKUU", "TOUKOKUU", "KESÄKUU",
             "HEINÄKUU", "ELOKUU", "SYYSKUU", "LOKAKUU", "MARRASKUU", "JOULUKUU"]


def motif_paths(repo):
    """Engraving motif (paths in px, centred at 0,0) chosen by the latest repo."""
    r = repo.lower()
    if "manek" in r or "hedgehog" in r or "siili" in r:          # hedgehog
        sp = []
        for k in range(15):
            ang = math.radians(180 + k * 12.85)
            rr = 15 if k % 2 == 0 else 20
            sp.append((rr * math.cos(ang), rr * 0.8 * math.sin(ang) + 4))
        body = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in sp)
        return [body + " L20 4 Q22 9 14 10 L-16 10 Z",
                "M14 2 Q22 0 25 5 Q22 9 15 8", "M-8 10 L-8 14 M6 10 L6 14", "M18 3 L18.5 3.5"]
    if "liiga" in r or "hockey" in r or "kiekko" in r:             # crossed sticks + puck
        return ["M-18 -16 L10 14 L17 14", "M18 -16 L-10 14 L-17 14",
                "M-7 16 a7 3 0 1 0 14 0 a7 3 0 1 0 -14 0"]
    return [gear_path(17, 10), "M-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0"]


def greeting(hour):
    if 5 <= hour < 10:
        return "HUOMENTA"
    if 10 <= hour < 17:
        return "PÄIVÄÄ"
    if 17 <= hour < 23:
        return "ILTAA"
    return "YÖVUORO"


# ------------------------------------------------------------------ scene
def render(data):
    d = date.fromisoformat(data["date"])
    hour = data["hour"]
    summer = d.month in (6, 7)
    rise, set_ = DAYLIGHT[d.month]
    night = not (rise <= hour < set_)
    white_night = summer and night
    th = themes_for(d, hour)
    sleeping = data["days_since_commit"] >= 3
    contrib = data["contributions"]
    if contrib is None:
        rnd0 = random.Random(42)
        contrib = [max(0, int(rnd0.gauss(3, 3))) if rnd0.random() > 0.25 else 0 for _ in range(64)]
    rnd = random.Random(7)
    out = []
    a = out.append

    sky_top, sky_bot = ("#070b24", "#24306b") if night else ("#5bb4ff", "#cfeaff")
    if white_night:
        sky_top, sky_bot = ("#3b5b9a", "#f5c9a0")
    a(f"""<defs>
  <radialGradient id="bg" cx="0.5" cy="0.45" r="0.75">
    <stop offset="0" stop-color="#1d2347"/><stop offset="1" stop-color="#090b1a"/>
  </radialGradient>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{sky_top}"/><stop offset="1" stop-color="{sky_bot}"/>
  </linearGradient>
  <radialGradient id="lampglow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ffcf7a" stop-opacity="0.45"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="sphere" cx="0.4" cy="0.35" r="0.7">
    <stop offset="0" stop-color="#ffe3a8"/><stop offset="0.6" stop-color="#e0a35a"/><stop offset="1" stop-color="#8c5a2a"/>
  </radialGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffe08a"/><stop offset="0.5" stop-color="#f2b930"/><stop offset="1" stop-color="#b9801a"/>
  </linearGradient>
  <linearGradient id="brass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#e9c27a"/><stop offset="1" stop-color="#9c6b2b"/>
  </linearGradient>
  <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="bigglow" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft"><feGaussianBlur stdDeviation="1.6"/></filter>
  <clipPath id="win"><polygon points="{pts([iso(1.3, 0, 2.9), iso(3.7, 0, 2.9), iso(3.7, 0, 5.3), iso(1.3, 0, 5.3)])}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="20" fill="url(#bg)"/>""")

    for _ in range(45):
        x, y = rnd.uniform(10, W - 10), rnd.uniform(10, H - 10)
        a(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(0.5, 1.4):.1f}" fill="#fff" opacity="0.4">'
          f'<animate attributeName="opacity" values="0.1;0.6;0.1" dur="{rnd.uniform(2, 6):.1f}s" repeatCount="indefinite"/></circle>')

    # ================================================= room shell
    a(box(0, 0, -0.45, 10, 10, 0.45, ("#3a2c22", "#6b4a2e", "#4f361f")))
    a(quad((0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0), "#5a4130"))
    for i in range(1, 10):
        a(line((i, 0, 0), (i, 10, 0), "#46321f", 1.4))
    a(quad((0, 0, 0), (0, 10, 0), (0, 10, 6.5), (0, 0, 6.5), "#2a3157"))
    a(quad((0, 0, 0), (10, 0, 0), (10, 0, 6.5), (0, 0, 6.5), "#20264a"))
    a(box(-0.3, 0, 0, 0.3, 10, 6.5, ("#3b4374", "#323a68", "#323a68")))
    a(box(0, -0.3, 0, 10, 0.3, 6.5, ("#3b4374", "#2a3157", "#2c3460")))
    a(quad((0, 0, 0), (0, 10, 0), (0, 10, 0.25), (0, 0, 0.25), "#3b2a1c"))
    a(quad((0, 0, 0), (10, 0, 0), (10, 0, 0.25), (0, 0, 0.25), "#33241a"))

    # ================================================= RIGHT WALL
    # --- window with weather
    a(quad((1.15, 0, 2.75), (3.85, 0, 2.75), (3.85, 0, 5.45), (1.15, 0, 5.45), "#b88a52"))
    a(quad((1.3, 0, 2.9), (3.7, 0, 2.9), (3.7, 0, 5.3), (1.3, 0, 5.3), "url(#sky)"))
    a('<g clip-path="url(#win)">')
    kind = data["weather"]["kind"]
    if night and not white_night:
        mx, my = iso(3.0, 0, 4.8)
        a(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="9" fill="#f4f1d0" filter="url(#glow)"/>'
          f'<circle cx="{mx + 4:.1f}" cy="{my - 3:.1f}" r="8" fill="#0d1333"/>')
        for _ in range(10):
            sx, sy = iso(rnd.uniform(1.4, 3.6), 0, rnd.uniform(3.6, 5.2))
            a(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="0.9" fill="#fff"/>')
    elif not white_night and kind in ("clear", "cloudy"):
        sx, sy = iso(3.0, 0, 4.7)
        a(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#ffd54a" filter="url(#glow)"/>')
    sil, hx = [iso(1.3, 0, 2.9)], 1.3
    while hx < 3.7:
        hgt = rnd.uniform(3.1, 3.8)
        sil += [iso(hx, 0, hgt), iso(min(hx + 0.35, 3.7), 0, hgt)]
        hx += 0.35
    sil += [iso(3.7, 0, 2.9)]
    a(poly(sil, "#0b0f26" if night else "#5d7396"))
    if night:  # lit windows in the skyline
        for _ in range(8):
            wx, wy = iso(rnd.uniform(1.4, 3.6), 0, rnd.uniform(3.0, 3.3))
            a(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="2" height="2" fill="#ffd98a" opacity="0.8"/>')
    if kind in ("snow", "rain"):
        for _ in range(26):
            x0, y0 = iso(rnd.uniform(1.3, 3.7), 0, 5.4)
            fall = 2.6 * S
            dur = rnd.uniform(2.5, 4.5) if kind == "snow" else rnd.uniform(0.7, 1.1)
            begin = rnd.uniform(0, dur)
            if kind == "snow":
                a(f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="1.5" fill="#fff" opacity="0.9">'
                  f'<animate attributeName="cy" values="{y0:.1f};{y0 + fall:.1f}" dur="{dur:.2f}s" begin="-{begin:.2f}s" repeatCount="indefinite"/></circle>')
            else:
                a(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0 - 2:.1f}" y2="{y0 + 7:.1f}" stroke="#9fc4ff" stroke-width="1" opacity="0.7">'
                  f'<animateTransform attributeName="transform" type="translate" values="0 0;-8 {fall:.1f}" dur="{dur:.2f}s" begin="-{begin:.2f}s" repeatCount="indefinite"/></line>')
    if "bonfire" in th["tags"]:   # juhannuskokko on the horizon
        bfx, bfy = iso(3.15, 0, 3.05)
        a(f'<g transform="translate({bfx:.1f} {bfy:.1f})"><ellipse rx="16" ry="7" fill="#ff8a2a" opacity="0.35" filter="url(#bigglow)"/>'
          f'<path d="M-7 0 Q-5 -12 0 -18 Q5 -12 7 0 Z" fill="#ff8a2a" filter="url(#glow)">'
          f'<animate attributeName="d" values="M-7 0 Q-5 -12 0 -18 Q5 -12 7 0 Z;M-7 0 Q-3 -14 1 -21 Q4 -10 7 0 Z;M-7 0 Q-5 -12 0 -18 Q5 -12 7 0 Z" dur="0.8s" repeatCount="indefinite"/></path>'
          f'<path d="M-4 0 Q-2 -7 0 -10 Q2 -7 4 0 Z" fill="#ffe08a"/></g>')
    if "fireworks" in th["tags"]:
        cols = ["#ff4d5e", "#ffc940", "#39d353", "#3fa9ff", "#d07bff"]
        for k in range(5):
            fx, fy = iso(rnd.uniform(1.6, 3.4), 0, rnd.uniform(4.2, 5.1))
            col = cols[k % 5]
            dur, beg = rnd.uniform(1.6, 2.4), rnd.uniform(0, 2)
            rays = "".join(f'<line x1="0" y1="0" x2="{12 * math.cos(math.radians(j * 30)):.1f}" y2="{12 * math.sin(math.radians(j * 30)):.1f}"/>' for j in range(12))
            a(f'<g transform="translate({fx:.1f} {fy:.1f})" stroke="{col}" stroke-width="1.4" stroke-linecap="round" opacity="0">'
              f'<animate attributeName="opacity" values="0;1;0" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
              f'<g><animateTransform attributeName="transform" type="scale" values="0.1;1.2" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>{rays}</g></g>')
    if th["flag"] and 8 <= hour < 22 or (th["flag"] and "Juhannus" in th["flag"]):
        fpx, fpy = iso(1.75, 0, 3.0)
        a(f'<g transform="{m_xplane(fpx, fpy)}">'
          f'<line x1="0" y1="0" x2="0" y2="-74" stroke="#e6e9f2" stroke-width="1.6"/><circle cx="0" cy="-75" r="1.8" fill="#ffd54a"/>'
          f'<g transform="translate(1 -72)"><animateTransform attributeName="transform" type="translate" values="1 -72;1 -72" dur="1s"/>'
          f'<path fill="#ffffff" d="M0 0 Q12 -3 24 0 Q36 3 44 0 L44 26 Q36 29 24 26 Q12 23 0 26 Z">'
          f'<animate attributeName="d" dur="1.6s" repeatCount="indefinite" values="M0 0 Q12 -3 24 0 Q36 3 44 0 L44 26 Q36 29 24 26 Q12 23 0 26 Z;'
          f'M0 0 Q12 3 24 0 Q36 -3 44 1 L44 27 Q36 23 24 26 Q12 29 0 26 Z;M0 0 Q12 -3 24 0 Q36 3 44 0 L44 26 Q36 29 24 26 Q12 23 0 26 Z"/></path>'
          f'<rect x="12" y="0" width="7" height="26" fill="#003580"/><rect x="0" y="9.5" width="44" height="7" fill="#003580"/>'
          f'</g></g>')
    a('</g>')
    a(line((2.5, 0, 2.9), (2.5, 0, 5.3), "#b88a52", 3))
    a(line((1.3, 0, 4.1), (3.7, 0, 4.1), "#b88a52", 3))
    a(box(1.05, 0, 2.62, 2.9, 0.35, 0.13, ("#d2a467", "#a87a44", "#8c6434")))
    if d.month in (12, 1, 2):  # snow on the sill
        a(box(1.1, 0.02, 2.75, 2.8, 0.3, 0.05, ("#f4f7ff", "#d7deef", "#c3cbe0")))
    if "xmas_lights" in th["tags"]:  # string lights around the window
        cols = ["#ff4d5e", "#ffc940", "#39d353", "#3fa9ff"]
        frame = [(1.15 + t * 2.7, 0, 5.45) for t in [i / 9 for i in range(10)]] + \
                [(3.85, 0, 5.45 - t * 2.7) for t in [i / 7 for i in range(1, 8)]] + \
                [(1.15, 0, 5.45 - t * 2.7) for t in [i / 7 for i in range(1, 8)]]
        for i, p in enumerate(frame):
            px, py = iso(*p)
            c1, c2 = cols[i % 4], cols[(i + 2) % 4]
            a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.6" fill="{c1}" filter="url(#glow)">'
              f'<animate attributeName="fill" values="{c1};{c2};{c1}" dur="2s" begin="{(i % 3) * 0.4:.1f}s" repeatCount="indefinite"/></circle>')
    if "candles" in th["tags"]:  # two candles on the sill
        for cx_ in (1.8, 3.2):
            a(box(cx_, 0.1, 2.75, 0.14, 0.14, 0.45, ("#fafafa", "#e7e9f2", "#d5d8e6")))
            fx, fy = iso(cx_ + 0.07, 0.17, 3.28)
            a(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="2.6" ry="5" fill="#ffcf5a" filter="url(#bigglow)">'
              f'<animate attributeName="ry" values="5;4;5.5;5" dur="0.9s" repeatCount="indefinite"/></ellipse>')

    if "birch" in th["tags"]:     # koivunoksat on both sides of the window
        for bxp in (0.95, 4.05):
            bx1, by1 = iso(bxp, 0.15, 2.7)
            leaves = "".join(f'<ellipse cx="{rnd.uniform(-9, 9):.1f}" cy="{-rnd.uniform(4, 70):.1f}" rx="3.4" ry="2.2" fill="{rnd.choice(["#5fbf4a", "#7fd65a", "#3f9e3a"])}" '
                             f'transform="rotate({rnd.uniform(-40, 40):.0f})"/>' for _ in range(34))
            a(f'<g transform="translate({bx1:.1f} {by1:.1f})"><path d="M0 0 L-2 -72 M0 -30 L-9 -52 M0 -42 L8 -62" stroke="#e8e4da" stroke-width="2"/>{leaves}'
              f'<animateTransform attributeName="transform" type="rotate" values="0 {bx1:.1f} {by1:.1f};1.5 {bx1:.1f} {by1:.1f};0 {bx1:.1f} {by1:.1f}" dur="4s" additive="sum" repeatCount="indefinite"/></g>')
    if "streamers" in th["tags"]:  # vappu serpentines along the walls
        cols = ["#ff4d5e", "#ffc940", "#3fa9ff", "#39d353", "#d07bff"]
        for k, col in enumerate(cols):
            zs = 6.1 - k * 0.12
            ptsl = [iso(0, yy_, zs - 0.25 * math.sin(yy_ * 2 + k)) for yy_ in [i * 0.5 for i in range(21)]]
            ptsr = [iso(xx_, 0, zs - 0.25 * math.sin(xx_ * 2 + k)) for xx_ in [i * 0.5 for i in range(21)]]
            for P in (ptsl, ptsr):
                a(f'<polyline points="{pts(P)}" fill="none" stroke="{col}" stroke-width="2" opacity="0.85"/>')

    # --- sign: now building / learning
    sx0, sx1 = 4.3, 7.55
    a(quad((sx0, 0, 3.55), (sx1, 0, 3.55), (sx1, 0, 5.5), (sx0, 0, 5.5), "#d9b47a"))
    a(quad((sx0 + 0.13, 0, 3.68), (sx1 - 0.13, 0, 3.68), (sx1 - 0.13, 0, 5.37), (sx0 + 0.13, 0, 5.37), "#12172e"))
    pct = dict(data["projects"]).get(data["now_building"], 0)
    for txt, z, size, col, fam in [("NOW BUILDING", 5.05, 8.5, "#8b95c9", MONO),
                                   (data["now_building"], 4.55, 15, "#ffc940", FONT),
                                   (f"{pct}%", 4.13, 9, "#ffc940", MONO),
                                   ("LEARNING " + data["learning"], 3.8, 8.5, "#39d353", MONO)]:
        px, py = iso(sx0 + (2.55 if txt.endswith("%") else 0.3), 0, z)
        a(f'<text transform="{m_xplane(px, py)}" font-family="{fam}" font-size="{size}" font-weight="700" '
          f'fill="{col}" letter-spacing="1">{escape(txt)}</text>')
    bar0, bar1 = sx0 + 0.3, sx0 + 2.4
    a(quad((bar0, 0, 4.15), (bar1, 0, 4.15), (bar1, 0, 4.3), (bar0, 0, 4.3), "#262c55"))
    bend = bar0 + (bar1 - bar0) * pct / 100
    a(quad((bar0, 0, 4.15), (bend, 0, 4.15), (bend, 0, 4.3), (bar0, 0, 4.3), "#ffc940", 'filter="url(#glow)"'))

    # --- trophy shelves
    trophies = data["trophies"]
    shelf_x0, shelf_w = 7.85, 1.95
    per_row = 3
    for row in range(2):
        z = 3.55 + row * 1.15
        a(box(shelf_x0, 0, z, shelf_w, 0.55, 0.09, ("#d2a467", "#a87a44", "#8c6434")))
        for k in range(per_row):
            idx = row * per_row + k
            if idx >= len(trophies):
                continue
            label, won = trophies[idx]
            px, py = iso(shelf_x0 + 0.33 + k * 0.62, 0.28, z + 0.09)
            fill = "url(#gold)" if won else "#2f3870"
            op = "1" if won else "0.55"
            flt = ' filter="url(#glow)"' if won else ""
            a(f'<g transform="translate({px:.1f} {py:.1f})" opacity="{op}"{flt}>'
              f'<rect x="-6" y="-4" width="12" height="4" fill="{"#6b4a2e" if won else "#262c55"}"/>'
              f'<rect x="-1.5" y="-10" width="3" height="6" fill="{fill}"/>'
              f'<path d="M-8 -24 L8 -24 L6 -14 Q0 -8 -6 -14 Z" fill="{fill}"/>'
              f'<path d="M-8 -22 Q-13 -20 -7 -15 M8 -22 Q13 -20 7 -15" fill="none" stroke="{fill}" stroke-width="1.6"/>'
              f'</g>')

    # ================================================= LEFT WALL
    # --- Liiga-style scoreboard (narrow)
    home, hs, away, as_ = data["scoreboard"]
    a(quad((0, 3.8, 3.95), (0, 2.25, 3.95), (0, 2.25, 5.45), (0, 3.8, 5.45), "#0d0f18"))
    a(quad((0, 3.72, 4.03), (0, 2.33, 4.03), (0, 2.33, 5.37), (0, 3.72, 5.37), "#151a2b"))
    px, py = iso(0, 3.02, 5.1)
    a(f'<text transform="{m_yplane(px, py)}" text-anchor="middle" font-family="{MONO}" font-size="7" fill="#8b95c9" letter-spacing="1">LIIGA·MGR</text>')
    for txt, yc, size, z in [(home, 3.4, 7, 4.2), (away, 2.64, 7, 4.2), (hs, 3.4, 18, 4.55), (as_, 2.64, 18, 4.55), ("–", 3.02, 14, 4.58)]:
        px, py = iso(0, yc, z)
        big = size > 8
        a(f'<text transform="{m_yplane(px, py)}" text-anchor="middle" font-family="{MONO}" font-size="{size}" '
          f'font-weight="700" fill="{"#ffb020" if big else "#c9d1ff"}"{" filter=" + chr(34) + "url(#glow)" + chr(34) if big else ""}>{escape(str(txt))}</text>')

    # --- wall calendar: today + countdown
    if data.get("countdown"):
        cd_label, cd_date = data["countdown"][0], date.fromisoformat(data["countdown"][1])
    else:
        cd_label = "JOULUUN"
        cd_date = date(d.year, 12, 24)
        if cd_date < d:
            cd_date = date(d.year + 1, 12, 24)
    days_left = (cd_date - d).days
    c0, c1 = 2.05, 0.55
    a(line((0, (c0 + c1) / 2, 5.62), (0, (c0 + c1) / 2, 5.38), "#8b95c9", 1.2))
    a(quad((0, c0, 3.95), (0, c1, 3.95), (0, c1, 5.4), (0, c0, 5.4), "#f3efe4"))
    a(quad((0, c0, 5.0), (0, c1, 5.0), (0, c1, 5.4), (0, c0, 5.4), "#d8343f"))
    for k in range(4):
        rx_, ry_ = iso(0, c0 - 0.22 - k * 0.33, 5.4)
        a(f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="1.6" fill="#555b77"/>')
    mid = (c0 + c1) / 2
    for txt, z, size, col, w8 in [(FI_MONTHS[d.month - 1], 5.11, 6.5, "#ffffff", 700), (str(d.day), 4.38, 24, "#1d2133", 800),
                                  ("JOULU" if days_left == 0 and not data.get("countdown") else f"{cd_label} {days_left} PV",
                                   4.05, 5.6, "#d8343f", 700)]:
        px, py = iso(0, mid, z)
        a(f'<text transform="{m_yplane(px, py)}" text-anchor="middle" font-family="{MONO if size < 20 else FONT}" '
          f'font-size="{size}" font-weight="{w8}" fill="{col}">{escape(txt)}</text>')

    # --- split-flap display: greeting + rotating words
    n_tiles, y_start, tw = 8, 9.35, 0.66
    a(quad((0, y_start + 0.12, 3.3), (0, y_start - n_tiles * tw - 0.12, 3.3),
           (0, y_start - n_tiles * tw - 0.12, 5.6), (0, y_start + 0.12, 5.6), "#0d0f18"))
    temp = data["weather"]["temp"]
    words2 = data["flap_words"] + [f"{temp:+d}°C", data["now_building"]]
    if th["flap"]:
        rows = [([th["flap"][0]], 4.55, 5.45), (th["flap"][1], 3.45, 4.35)]
    else:
        rows = [([greeting(hour)], 4.55, 5.45), (words2, 3.45, 4.35)]
    for words, z0, z1 in rows:
        for i in range(n_tiles):
            yb = y_start - i * tw
            a(quad((0, yb - 0.04, z0), (0, yb - tw + 0.04, z0), (0, yb - tw + 0.04, z1), (0, yb - 0.04, z1), "#1f2333"))
            a(line((0, yb - 0.04, (z0 + z1) / 2), (0, yb - tw + 0.04, (z0 + z1) / 2), "#000", 1.2))
        nw = len(words)
        for wi, word in enumerate(words):
            word = word.upper()[:n_tiles].center(n_tiles)
            g = []
            for i, ch in enumerate(word):
                if ch == " ":
                    continue
                px, py = iso(0, y_start - i * tw - tw / 2, z0 + 0.22)
                g.append(f'<text transform="{m_yplane(px, py)}" text-anchor="middle" font-family="{MONO}" '
                         f'font-size="20" font-weight="700" fill="#f3f0e6">{escape(ch)}</text>')
            if nw == 1:
                a("".join(g))
            else:
                vals = ";".join("1" if k == wi else "0" for k in range(nw))
                kt = ";".join(f"{k / nw:.3f}" for k in range(nw))
                a(f'<g opacity="{1 if wi == 0 else 0}"><animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
                  f'calcMode="discrete" dur="{nw * 2.5}s" repeatCount="indefinite"/>{"".join(g)}</g>')

    # --- shelf: sphere lamp + language boxes
    a(box(0, 3.5, 1.9, 0.9, 5.85, 0.12, ("#d2a467", "#a87a44", "#8c6434")))
    total = sum(v for _, v in data["languages"]) or 1
    yy, slots = 9.3, []
    for name, val in data["languages"]:
        w = max(0.85, 4.3 * val / total)
        slots.append((name, yy - w, w, 0.42 + 0.5 * val / total))
        yy -= w
    # sphere lamp (back end of shelf)
    lx, ly = iso(0.45, 4.15, 2.02 + 0.42)
    if night:
        a(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="26" fill="#ffb347" opacity="0.18" filter="url(#soft)"/>')
    a(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="14" fill="{"url(#sphere)" if night else "#c99c62"}"/>')
    for k in range(-3, 4):
        a(f'<ellipse cx="{lx:.1f}" cy="{ly + k * 3.6:.1f}" rx="{math.sqrt(max(0, 14 ** 2 - (k * 3.6) ** 2)):.1f}" ry="1.2" '
          f'fill="none" stroke="#6b4320" stroke-width="0.8" opacity="0.7"/>')
    a(f'<path d="M{lx - 4:.1f} {ly - 3:.1f} q4 -6 8 0 q1 4 -2 6 h-4 q-3 -2 -2 -6 z" fill="#3a2414" opacity="0.85"/>'
      f'<circle cx="{lx - 1.6:.1f}" cy="{ly - 1:.1f}" r="1.1" fill="{"#ffe3a8" if night else "#c99c62"}"/>'
      f'<circle cx="{lx + 1.6:.1f}" cy="{ly - 1:.1f}" r="1.1" fill="{"#ffe3a8" if night else "#c99c62"}"/>')
    a(f'<rect x="{lx - 5:.1f}" y="{ly + 12:.1f}" width="10" height="4" rx="1" fill="#6b4a2e"/>')
    for name, y0, w, h in reversed(slots):
        a(box(0.1, y0, 2.02, 0.7, w - 0.1, h, WOOD_L))
        px, py = iso(0.8, y0 + w / 2, 2.02 + h * 0.3)
        a(f'<text transform="{m_yplane(px, py)}" text-anchor="middle" font-family="{MONO}" font-size="11" '
          f'font-weight="700" fill="#4a2f16">{escape(name)}</text>')

    # --- hockey stick + puck (front of left wall)
    a(line((0.55, 9.75, 0.08), (0.08, 9.75, 3.0), "#1d1d22", 5, 'stroke-linecap="round"'))
    a(line((0.47, 9.75, 0.6), (0.4, 9.75, 1.0), "#f0f0f0", 5))
    a(line((0.12, 9.75, 2.65), (0.09, 9.75, 2.95), "#f0f0f0", 5, 'stroke-linecap="round"'))
    b1, b2 = iso(0.55, 9.75, 0.08), iso(1.25, 9.75, 0.06)
    a(f'<path d="M{b1[0]:.1f} {b1[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f} q4 2 2 5 L{b1[0] - 2:.1f} {b1[1] + 4:.1f} Z" fill="#1d1d22"/>')
    a(f'<line x1="{(b1[0] + b2[0]) / 2:.1f}" y1="{(b1[1] + b2[1]) / 2 + 1:.1f}" x2="{b2[0]:.1f}" y2="{b2[1] + 1:.1f}" stroke="#f0f0f0" stroke-width="2.5"/>')
    pk = iso(1.8, 9.2, 0)
    a(f'<ellipse cx="{pk[0]:.1f}" cy="{pk[1] + 2:.1f}" rx="7" ry="3.5" fill="#111"/><ellipse cx="{pk[0]:.1f}" cy="{pk[1]:.1f}" rx="7" ry="3.5" fill="#26262c"/>')

    # ================================================= FLOOR / BENCH
    if night:
        gx, gy = iso(3.0, 1.8, 2.3)
        a(f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="190" ry="110" fill="url(#lampglow)"/>')

    bx, by, bw, bd, bh = 0.7, 0.3, 5.2, 3.0, 2.1
    for lx_, ly_ in [(bx + 0.1, by + 0.1), (bx + bw - 0.35, by + 0.1)]:
        a(box(lx_, ly_, 0, 0.25, 0.25, bh, DARKWOOD))
    a(box(bx + 0.1, by + 0.15, 0.45, bw - 0.2, bd - 0.3, 0.08, ("#8c6434", "#7a5534", "#5e4128")))  # low shelf
    sheets = [(0.25, 0.3, 4.4, 2.3), (0.35, 0.35, 4.2, 2.2), (0.2, 0.25, 4.5, 2.4), (0.4, 0.3, 4.1, 2.3),
              (0.3, 0.4, 4.3, 2.1), (0.25, 0.3, 4.4, 2.3), (0.35, 0.35, 4.2, 2.25)]
    for i, (ox, oy, sw, sd) in enumerate(sheets):
        cols = ("#e8c48c", "#c79a5d", "#a5783f") if i % 2 == 0 else ("#dcb57b", "#b88a52", "#946a38")
        a(box(bx + ox, by + oy, 0.53 + i * 0.075, sw, sd, 0.075, cols))
    for lx_, ly_ in [(bx + 0.1, by + bd - 0.35), (bx + bw - 0.35, by + bd - 0.35)]:
        a(box(lx_, ly_, 0, 0.25, 0.25, bh, DARKWOOD))
    a(box(bx, by, bh, bw, bd, 0.22, ("#c99c62", "#a87a44", "#8c6434")))
    top = bh + 0.22
    tc_ = data["today_commits"]

    # MANEK board – 8x8 LEDs = last 64 days
    mx0, my0, ms, mh = 1.0, 0.45, 2.7, 0.42
    a(box(mx0, my0, top, ms, ms, mh, WOOD))
    a(quad((mx0 + 0.12, my0 + 0.12, top + mh), (mx0 + ms - 0.12, my0 + 0.12, top + mh),
           (mx0 + ms - 0.12, my0 + ms - 0.12, top + mh), (mx0 + 0.12, my0 + ms - 0.12, top + mh), "#0c1018"))
    cell = (ms - 0.3) / 8
    for k, n in enumerate(contrib[-64:]):
        r, c = divmod(k, 8)
        px, py = iso(mx0 + 0.15 + cell * (c + 0.5), my0 + 0.15 + cell * (r + 0.5), top + mh)
        lv = level(n)
        f = ' filter="url(#glow)"' if lv >= 2 else ""
        anim = '<animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/>' if k == 63 else ""
        a(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{cell * CX * 0.62:.1f}" ry="{cell * CY * 0.62:.1f}" fill="{LED_LEVELS[lv]}"{f}>{anim}</ellipse>')

    # monitor: last commit + today's count
    a(box(4.55, 1.05, top, 0.5, 0.35, 0.12, BLACK))
    a(box(4.75, 1.15, top + 0.12, 0.12, 0.12, 0.45, BLACK))
    a(box(3.85, 1.1, top + 0.55, 1.95, 0.18, 1.3, ("#2b2f3d", "#1f222c", "#16181f")))
    sy_ = 1.28
    a(quad((3.93, sy_, top + 0.63), (5.72, sy_, top + 0.63), (5.72, sy_, top + 1.77), (3.93, sy_, top + 1.77), "#0a0e1a"))
    tc = data["today_commits"]
    lines = [("$ git log -1", "#8b95c9"), (data["last_commit"][:14], "#39d353"),
             (th["monitor"] or (f"today: {tc}" + (" ⚡" if tc >= 5 else "")), "#ffc940"), ("$ _", "#8b95c9")]
    for i, (t, col) in enumerate(lines):
        px, py = iso(4.01, sy_, top + 1.55 - i * 0.25)
        el = f'<text transform="{m_xplane(px, py)}" font-family="{MONO}" font-size="7" fill="{col}">{escape(t)}'
        if i == 3:
            el += '<animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/>'
        a(el + "</text>")

    # post-it notes = current todos
    for (txt, col), (x0n, z0n, rot) in zip(data["todos"][:3], [(3.2, top + 1.6, -6), (5.72, top + 1.45, 5), (4.95, top + 2.3, -2)]):
        px, py = iso(x0n, 1.3, z0n)
        a(f'<g transform="{m_xplane(px, py)}"><g transform="rotate({rot})">'
          f'<rect x="1.5" y="1.5" width="30" height="22" fill="#000" opacity="0.25"/>'
          f'<rect width="30" height="22" fill="{col}"/><rect width="30" height="4" fill="#000" opacity="0.07"/>'
          f'<text x="15" y="13.5" text-anchor="middle" font-family="{FONT}" font-size="5.2" font-weight="700" fill="#3a2f1a">{escape(txt[:10])}</text>'
          f'</g></g>')

    # breadboard with Arduino Nano ESP32 + Nano R4
    bbx, bby = 3.9, 1.55
    a(box(bbx, bby, top, 1.15, 0.7, 0.07, ("#f1f1ec", "#d9d9d2", "#c8c8c0")))
    for r in range(5):
        for c in range(14):
            hx, hy = iso(bbx + 0.08 + c * 0.075, bby + 0.1 + r * 0.12, top + 0.07)
            a(f'<rect x="{hx - 0.6:.1f}" y="{hy - 0.4:.1f}" width="1.2" height="0.8" fill="#9a9a92"/>')
    for k, (lab, chipcol) in enumerate([("ESP32", "#c9ccd6"), ("R4", "#1a1a1a")]):
        nx_ = bbx + 0.12 + k * 0.52
        a(box(nx_, bby + 0.2, top + 0.07, 0.42, 0.2, 0.04, ("#00979c", "#00777b", "#006165")))
        a(box(nx_ + 0.12, bby + 0.24, top + 0.11, 0.18, 0.12, 0.04 if k else 0.06, (chipcol, "#8e919c" if not k else "#111", "#7a7d88" if not k else "#0b0b0b")))
        a(box(nx_ - 0.05, bby + 0.25, top + 0.11, 0.07, 0.1, 0.04, ("#d7dbe6", "#aab0c0", "#9097a8")))  # USB-C
        tx_, ty_ = iso(nx_ - 0.06 + k * 0.2, bby + 0.62, top + 0.075)
        a(f'<text transform="{m_top(tx_, ty_)}" font-family="{MONO}" font-size="6" font-weight="700" fill="#00777b">{lab}</text>')
        lx2, ly2 = iso(nx_ + 0.36, bby + 0.33, top + 0.12)
        a(f'<circle cx="{lx2:.1f}" cy="{ly2:.1f}" r="1.4" fill="{"#39d353" if k else "#ff9d2e"}" filter="url(#glow)">'
          f'<animate attributeName="opacity" values="1;0.2;1" dur="{0.8 + k * 0.5:.1f}s" repeatCount="indefinite"/></circle>')
    for (p1, p2, col) in [((4.05, 1.62), (4.6, 1.62), "#ff4d5e"), ((4.0, 1.7), (4.4, 1.7), "#3fa9ff"),
                          ((4.7, 1.65), (4.95, 2.12), "#ffc940")]:
        q1, q2 = iso(p1[0], p1[1], top + 0.08), iso(p2[0], p2[1], top + 0.08)
        mxp, myp = (q1[0] + q2[0]) / 2, min(q1[1], q2[1]) - 7
        a(f'<path d="M{q1[0]:.1f} {q1[1]:.1f} Q{mxp:.1f} {myp:.1f} {q2[0]:.1f} {q2[1]:.1f}" fill="none" stroke="{col}" stroke-width="1.4"/>')

    # soldering station (front-right corner)
    a(box(5.2, 1.5, top, 0.6, 0.55, 0.38, ("#3a3f52", "#c23b3b", "#9e2f2f")))
    dx_, dy_ = iso(5.27, 2.05, top + 0.3)
    a(f'<text transform="{m_xplane(dx_, dy_)}" font-family="{MONO}" font-size="7" font-weight="700" fill="#ffb020" '
      f'filter="url(#glow)">{"350°" if tc_ > 0 else "OFF"}</text>')
    a(box(5.3, 2.35, top, 0.45, 0.4, 0.05, ("#2b2f3d", "#22252f", "#1b1d25")))          # holder base
    a(box(5.6, 2.45, top + 0.05, 0.12, 0.2, 0.08, ("#f2d14a", "#d4b23a", "#b8992f")))  # sponge
    a(line((5.42, 2.55, top + 0.05), (5.42, 2.55, top + 0.42), "#9aa1b8", 3))           # spiral stand
    for k in range(4):
        a(line((5.36, 2.55, top + 0.12 + k * 0.08), (5.48, 2.55, top + 0.16 + k * 0.08), "#c3c8d8", 1.6))
    a(line((5.42, 2.55, top + 0.42), (5.95, 2.62, top + 0.72), "#1d1d22", 4.5, 'stroke-linecap="round"'))   # iron handle
    a(line((5.42, 2.55, top + 0.42), (5.33, 2.4, top + 0.3), "#c3c8d8", 2, 'stroke-linecap="round"'))   # tip
    cord0, cord1 = iso(5.95, 2.62, top + 0.72), iso(5.8, 1.85, top + 0.15)
    a(f'<path d="M{cord0[0]:.1f} {cord0[1]:.1f} C{cord0[0] + 16:.1f} {cord0[1] + 2:.1f} {cord1[0] + 18:.1f} {cord1[1] + 14:.1f} {cord1[0]:.1f} {cord1[1]:.1f}" '
      f'fill="none" stroke="#1d1d22" stroke-width="1.5"/>')
    if tc_ > 0:
        tipx, tipy = iso(5.33, 2.4, top + 0.3)
        a(f'<path d="M{tipx:.1f} {tipy - 2:.1f} q-3 -5 0 -10 q3 -5 0 -10" fill="none" stroke="#e6e9f2" stroke-width="1.3" opacity="0">'
          f'<animate attributeName="opacity" values="0;0.6;0" dur="2.2s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 2;0 -8" dur="2.2s" repeatCount="indefinite"/></path>')
    # solder spool
    spx, spy = iso(5.95, 2.2, top)
    a(f'<ellipse cx="{spx:.1f}" cy="{spy - 4:.1f}" rx="7" ry="4" fill="#9aa1b8"/>'
      f'<rect x="{spx - 7:.1f}" y="{spy - 10:.1f}" width="14" height="6" fill="#c3c8d8"/>'
      f'<ellipse cx="{spx:.1f}" cy="{spy - 10:.1f}" rx="7" ry="4" fill="#dfe3ee"/><ellipse cx="{spx:.1f}" cy="{spy - 10:.1f}" rx="2" ry="1.2" fill="#555"/>'
      f'<path d="M{spx + 6:.1f} {spy - 8:.1f} q8 2 10 8" fill="none" stroke="#c3c8d8" stroke-width="1"/>')

    # coffee mug – steam amount = today's commits
    mcx, mcy = iso(4.2, 2.85, top)
    a(f'<ellipse cx="{mcx:.1f}" cy="{mcy:.1f}" rx="8" ry="3.5" fill="#000" opacity="0.25"/>'
      f'<path d="M{mcx - 7:.1f} {mcy - 16:.1f} L{mcx - 7:.1f} {mcy - 1:.1f} Q{mcx:.1f} {mcy + 3:.1f} {mcx + 7:.1f} {mcy - 1:.1f} L{mcx + 7:.1f} {mcy - 16:.1f} Z" fill="#e8e3d8"/>'
      f'<path d="M{mcx + 7:.1f} {mcy - 13:.1f} q7 1 6 6 q-1 4 -6 3" fill="none" stroke="#e8e3d8" stroke-width="2.4"/>'
      f'<ellipse cx="{mcx:.1f}" cy="{mcy - 16:.1f}" rx="7" ry="3" fill="#4a2c17"/>'
      f'<path d="M{mcx - 7:.1f} {mcy - 9:.1f} L{mcx + 7:.1f} {mcy - 9:.1f}" stroke="#ff4d5e" stroke-width="2"/>')
    wisps = 0 if tc == 0 else 1 if tc <= 2 else 2 if tc <= 5 else 3
    for k in range(wisps):
        ox = (k - (wisps - 1) / 2) * 5
        a(f'<path d="M{mcx + ox:.1f} {mcy - 19:.1f} q-4 -6 0 -12 q4 -6 0 -12" fill="none" stroke="#ffffff" stroke-width="2" '
          f'stroke-linecap="round" opacity="0">'
          f'<animate attributeName="opacity" values="0;0.55;0" dur="2.6s" begin="{k * 0.8:.1f}s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 4;0 -8" dur="2.6s" begin="{k * 0.8:.1f}s" repeatCount="indefinite"/></path>')

    # multimeter – reads today's commits
    a(box(4.47, 2.38, top, 0.55, 0.68, 0.1, ("#f2c230", "#d4a520", "#b88d18")))
    a(quad((4.53, 2.44, top + 0.1), (4.96, 2.44, top + 0.1), (4.96, 2.66, top + 0.1), (4.53, 2.66, top + 0.1), "#1c2b22"))
    dx2, dy2 = iso(4.56, 2.63, top + 0.1)
    a(f'<text transform="{m_top(dx2, dy2)}" font-family="{MONO}" font-size="6.5" font-weight="700" fill="#9dff9d">{tc_:02d}.0</text>')
    kx, ky = iso(4.745, 2.86, top + 0.1)
    a(f'<ellipse cx="{kx:.1f}" cy="{ky:.1f}" rx="5" ry="2.8" fill="#2b2f3d"/><line x1="{kx:.1f}" y1="{ky:.1f}" x2="{kx + 3:.1f}" y2="{ky - 1.6:.1f}" stroke="#f2c230" stroke-width="1"/>')
    for col, (ex_, ey_) in [("#e0303c", (4.3, 3.25)), ("#1d1d22", (4.9, 3.28))]:
        j1, j2 = iso(4.6 if col != "#1d1d22" else 4.9, 3.0, top + 0.1), iso(ex_, ey_, top)
        a(f'<path d="M{j1[0]:.1f} {j1[1]:.1f} Q{(j1[0] + j2[0]) / 2:.1f} {j2[1] + 8:.1f} {j2[0]:.1f} {j2[1]:.1f}" fill="none" stroke="{col}" stroke-width="1.5"/>')

    # pendant lamp
    lp = iso(2.35, 1.8, top + 2.3)
    a(f'<line x1="{lp[0]:.1f}" y1="0" x2="{lp[0]:.1f}" y2="{lp[1] - 14:.1f}" stroke="#555b77" stroke-width="1.5"/>')
    a(f'<path d="M{lp[0] - 18:.1f} {lp[1] + 6:.1f} L{lp[0] - 7:.1f} {lp[1] - 14:.1f} L{lp[0] + 7:.1f} {lp[1] - 14:.1f} '
      f'L{lp[0] + 18:.1f} {lp[1] + 6:.1f} Z" fill="#3d4466"/>')
    a(f'<ellipse cx="{lp[0]:.1f}" cy="{lp[1] + 6:.1f}" rx="18" ry="4" fill="{"#ffd98a" if night else "#8a8fa8"}"'
      f'{" filter=" + chr(34) + "url(#glow)" + chr(34) if night else ""}/>')
    if night:
        bl, br = iso(1.0, 1.4, top), iso(3.7, 2.8, top)
        a(f'<polygon points="{lp[0] - 16:.1f},{lp[1] + 7:.1f} {lp[0] + 16:.1f},{lp[1] + 7:.1f} {br[0]:.1f},{br[1]:.1f} {bl[0]:.1f},{bl[1] + 20:.1f}" '
          f'fill="#ffd98a" opacity="0.07"/>')

    if "balloons" in th["tags"]:
        for k, (col, dxb, h_) in enumerate([("#ff4d5e", -26, 52), ("#3fa9ff", -6, 64), ("#ffc940", 16, 48)]):
            bxb, byb = lp[0] + dxb, lp[1] - h_
            a(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{2 - k:.0f} -4;0 0" dur="{3 + k * 0.6:.1f}s" repeatCount="indefinite"/>'
              f'<path d="M{lp[0]:.1f} {lp[1] - 12:.1f} Q{bxb - 4:.1f} {byb + 25:.1f} {bxb:.1f} {byb + 14:.1f}" fill="none" stroke="#c9d1ff" stroke-width="0.8"/>'
              f'<ellipse cx="{bxb:.1f}" cy="{byb:.1f}" rx="10" ry="13" fill="{col}"/>'
              f'<ellipse cx="{bxb - 3:.1f}" cy="{byb - 5:.1f}" rx="2.5" ry="4" fill="#fff" opacity="0.45"/>'
              f'<path d="M{bxb - 2:.1f} {byb + 13:.1f} l2 3 l2 -3 z" fill="{col}"/></g>')

    # ================================================= LASER
    tx, ty, tw_, td, tth = 6.3, 0.3, 3.4, 3.1, 1.9
    for lx_, ly_ in [(tx + 0.1, ty + 0.1), (tx + tw_ - 0.35, ty + 0.1), (tx + 0.1, ty + td - 0.35), (tx + tw_ - 0.35, ty + td - 0.35)]:
        a(box(lx_, ly_, 0, 0.25, 0.25, tth, ("#3d4258", "#353a4f", "#2b2f40")))
    a(box(tx, ty, tth, tw_, td, 0.18, ("#4a506b", "#3b4058", "#30344a")))
    lt = tth + 0.18
    a(box(tx + 0.3, ty + 0.35, lt, tw_ - 0.6, td - 0.7, 0.05, ("#e3c48f", "#c79a5d", "#b5874c")))
    mcx2, mcy2 = iso(tx + 1.15, ty + 1.2, lt + 0.05)
    a(f'<g transform="{m_top(mcx2, mcy2)}" fill="none" stroke="#5a3a1e" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">')
    for pth in motif_paths(data["latest_repo"]):
        a(f'<path d="{pth}" stroke-dasharray="260" stroke-dashoffset="260">'
          f'<animate attributeName="stroke-dashoffset" values="260;0;0;260" keyTimes="0;0.55;0.95;1" dur="7s" repeatCount="indefinite"/></path>')
    a('</g>')
    ex, ey = iso(tx + 0.75, ty + 2.15, lt + 0.05)
    a(f'<text transform="{m_top(ex, ey)}" font-family="{MONO}" font-size="13" font-weight="700" fill="#5a3a1e" opacity="0.85">'
      f'{escape(data["latest_repo"][:14])}</text>')
    a(box(tx + 0.15, ty + 0.15, lt, tw_ - 0.3, 0.2, 0.28, METAL))
    a(box(tx + 0.15, ty + td - 0.35, lt, tw_ - 0.3, 0.2, 0.28, METAL))
    gdx = [0, 1.9, 1.9, 0.4, 0]
    a('<g><animateTransform attributeName="transform" type="translate" dur="7s" repeatCount="indefinite" values="'
      + ";".join(f"{v * CX:.1f} {v * CY:.1f}" for v in gdx) + '"/>')
    gx0 = tx + 0.45
    a(box(gx0, ty + 0.15, lt + 0.28, 0.22, td - 0.3, 0.18, METAL))
    hdy = [0, 0, 1.6, 1.6, 0]
    a('<g><animateTransform attributeName="transform" type="translate" dur="7s" repeatCount="indefinite" values="'
      + ";".join(f"{-v * CX:.1f} {v * CY:.1f}" for v in hdy) + '"/>')
    hy0 = ty + 0.65
    bt, bb = iso(gx0 + 0.11, hy0 + 0.17, lt + 0.22), iso(gx0 + 0.11, hy0 + 0.17, lt + 0.05)
    a(f'<line x1="{bt[0]:.1f}" y1="{bt[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}" stroke="#ff3b3b" stroke-width="1.5" filter="url(#glow)"/>')
    a(f'<ellipse cx="{bb[0]:.1f}" cy="{bb[1]:.1f}" rx="4" ry="2.2" fill="#ff2a2a" filter="url(#bigglow)">'
      f'<animate attributeName="opacity" values="1;0.6;1" dur="0.3s" repeatCount="indefinite"/></ellipse>')
    a(box(gx0 - 0.05, hy0, lt + 0.22, 0.32, 0.34, 0.55, BLACK))
    a('</g></g>')

    # stack of cut pieces = week's commits
    n = max(1, min(14, data["week_commits"]))
    for i in range(n):
        a(box(8.0, 4.0, i * 0.1, 1.3, 1.0, 0.1, WOOD_L if i % 2 == 0 else ("#d9b47a", "#b88a52", "#a5783f")))
    sx_, sy2 = iso(8.65, 5.0, 0)
    a(f'<text x="{sx_ + 58:.1f}" y="{sy2 - 4:.1f}" font-family="{MONO}" font-size="10" fill="#c9b08a">{data["week_commits"]} commit{"" if data["week_commits"] == 1 else "s"}</text>'
      f'<text x="{sx_ + 58:.1f}" y="{sy2 + 8:.1f}" font-family="{MONO}" font-size="10" fill="#c9b08a">this week</text>')

    # stool
    for lx_, ly_ in [(2.6, 4.3), (3.4, 4.3), (2.6, 5.1), (3.4, 5.1)]:
        a(box(lx_, ly_, 0, 0.12, 0.12, 1.2, DARKWOOD))
    a(box(2.5, 4.2, 1.2, 1.15, 1.15, 0.15, ("#c99c62", "#a87a44", "#8c6434")))

    # ================================================= steampunk kinetic piece (front-left)
    a(box(1.0, 7.3, 0, 1.0, 1.0, 0.85, ("#3a2c22", "#4f3a2a", "#3d2c1f")))
    a(box(1.0, 7.3, 0.85, 1.0, 1.0, 0.08, ("#b88a52", "#8c6434", "#6f4d26")))
    for (gx_, gz, r, teeth, dur, dirn, fill) in [(1.35, 1.75, 24, 12, 9, 1, "url(#brass)"),
                                                (1.92, 2.12, 15, 8, 6, -1, "#c98a4a"),
                                                (1.9, 1.32, 11, 7, 4.4, -1, "#a86e35")]:
        px, py = iso(gx_, 7.8, gz)
        a(f'<g transform="{m_xplane(px, py)}"><g>'
          f'<animateTransform attributeName="transform" type="rotate" from="0" to="{360 * dirn}" dur="{dur}s" repeatCount="indefinite"/>'
          f'<path d="{gear_path(r, teeth)}" fill="{fill}" stroke="#5b3a18" stroke-width="0.8"/>'
          f'<circle r="{r * 0.35:.1f}" fill="#3a2414"/><circle r="{r * 0.15:.1f}" fill="#e9c27a"/></g></g>')
    a(line((1.35, 7.8, 0.93), (1.35, 7.8, 1.75), "#5b3a18", 3))
    # nixie visitor counter
    a(box(1.05, 8.0, 0.93, 0.9, 0.25, 0.14, ("#3a2414", "#5b3a18", "#4a2e14")))
    digits = f'{data["visitors"]:05d}'[-5:]
    for k, ch in enumerate(digits):
        nxp, nyp = iso(1.16 + k * 0.17, 8.12, 1.07)
        a(f'<rect x="{nxp - 3.6:.1f}" y="{nyp - 17:.1f}" width="7.2" height="17" rx="3.6" fill="#1b1410" stroke="#8a6a4a" stroke-width="0.6" opacity="0.95"/>'
          f'<text x="{nxp:.1f}" y="{nyp - 4:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#ff8a2a" filter="url(#glow)">{ch}</text>')
    lbx, lby = iso(1.1, 8.25, 0.96)
    a(f'<text transform="{m_xplane(lbx, lby)}" font-family="{MONO}" font-size="5" fill="#e9c27a" letter-spacing="1">VISITORS</text>')

    # steam puff from the piece
    vx, vy = iso(1.2, 7.8, 2.75)
    a(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="4" fill="#cfd6ea" opacity="0">'
      f'<animate attributeName="opacity" values="0;0.5;0" dur="3.4s" repeatCount="indefinite"/>'
      f'<animate attributeName="cy" values="{vy:.1f};{vy - 22:.1f}" dur="3.4s" repeatCount="indefinite"/>'
      f'<animate attributeName="r" values="3;9" dur="3.4s" repeatCount="indefinite"/></circle>')

    # ================================================= PCB cart: schematic + floating 3D boards
    cx0_, cy0_, cw_, cd_, ch_ = 7.55, 6.0, 1.9, 1.75, 1.15
    for lx_, ly_ in [(cx0_ + 0.05, cy0_ + 0.05), (cx0_ + cw_ - 0.15, cy0_ + 0.05),
                     (cx0_ + 0.05, cy0_ + cd_ - 0.15), (cx0_ + cw_ - 0.15, cy0_ + cd_ - 0.15)]:
        a(box(lx_, ly_, 0.08, 0.1, 0.1, ch_ - 0.08, ("#7d849b", "#6a7086", "#5a5f73")))
        wx_, wy_ = iso(lx_ + 0.05, ly_ + 0.05, 0.04)
        a(f'<circle cx="{wx_:.1f}" cy="{wy_:.1f}" r="3" fill="#1d1d22"/>')
    a(box(cx0_, cy0_, 0.25, cw_, cd_, 0.06, ("#9aa1b8", "#7d849b", "#6a7086")))
    # parts organiser on the lower shelf
    a(box(cx0_ + 0.15, cy0_ + 0.2, 0.31, cw_ - 0.3, 1.1, 0.5, ("#3fa9ff", "#2f86cc", "#256ba3")))
    for r in range(2):
        for c in range(4):
            x_ = cx0_ + 0.22 + c * 0.38
            a(quad((x_, cy0_ + 1.3, 0.37 + r * 0.22), (x_ + 0.32, cy0_ + 1.3, 0.37 + r * 0.22),
                   (x_ + 0.32, cy0_ + 1.3, 0.55 + r * 0.22), (x_, cy0_ + 1.3, 0.55 + r * 0.22), "#d6ecff", 'opacity="0.85"'))
    a(box(cx0_, cy0_, ch_, cw_, cd_, 0.08, ("#9aa1b8", "#7d849b", "#6a7086")))
    ct = ch_ + 0.08
    # blueprint schematic lying on top
    a(quad((cx0_ + 0.1, cy0_ + 0.1, ct), (cx0_ + cw_ - 0.1, cy0_ + 0.1, ct),
           (cx0_ + cw_ - 0.1, cy0_ + cd_ - 0.1, ct), (cx0_ + 0.1, cy0_ + cd_ - 0.1, ct), "#163a78"))
    spx0, spy0 = iso(cx0_ + 0.18, cy0_ + 0.18, ct)
    zz = "".join(f"l2 -3 l2 6 l2 -6 l2 6 l2 -3" for _ in range(1))
    schem = (
        '<rect x="2" y="2" width="56" height="51" fill="none" stroke="#9cc4ff" stroke-width="0.4" stroke-dasharray="1 1"/>'
        '<rect x="22" y="6" width="16" height="22" fill="none" stroke="#e6f0ff" stroke-width="0.9"/>'
        '<text x="30" y="16" text-anchor="middle" font-size="3.2" fill="#e6f0ff" font-family="monospace">NANO</text>'
        '<text x="30" y="20" text-anchor="middle" font-size="3.2" fill="#e6f0ff" font-family="monospace">ESP32</text>'
        + "".join(f'<path d="M6 {9 + k * 4} h4 {zz} h6" fill="none" stroke="#e6f0ff" stroke-width="0.6"/>' for k in range(5))
        + '<path d="M38 10 h6 M38 14 h10 M38 24 h6" stroke="#e6f0ff" stroke-width="0.6"/>'
        + "".join(f'<rect x="{6 + k * 7}" y="38" width="5" height="5" fill="none" stroke="#e6f0ff" stroke-width="0.6"/>'
                  f'<path d="M{11 + k * 7} 40.5 h2" stroke="#e6f0ff" stroke-width="0.6"/>' for k in range(6))
        + '<path d="M30 28 V34 H8 V38" fill="none" stroke="#e6f0ff" stroke-width="0.6"/>'
        '<circle cx="48" cy="14" r="2.5" fill="none" stroke="#e6f0ff" stroke-width="0.6"/>'
        '<text x="6" y="50" font-size="3" fill="#9cc4ff" font-family="monospace">MANEK V2 · SCH</text>')
    a(f'<g transform="{m_top(spx0, spy0)}">{schem}</g>')
    # hologram beam
    hb = [iso(cx0_ + 0.4, cy0_ + 0.4, ct), iso(cx0_ + cw_ - 0.4, cy0_ + 0.4, ct),
          iso(cx0_ + cw_ - 0.4, cy0_ + cd_ - 0.4, ct), iso(cx0_ + 0.4, cy0_ + cd_ - 0.4, ct)]
    a(f'<polygon points="{pts(hb)}" fill="#4fd1ff" opacity="0.12" filter="url(#soft)"/>')
    # floating exploded PCBs (KiCad 3D-viewer style)
    GREEN = ("#1f7a44", "#17603a", "#124e2f")
    a('<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="4.5s" repeatCount="indefinite"/>')
    # LED PCB
    lz = ct + 0.45
    a(box(cx0_ + 0.3, cy0_ + 0.25, lz, 1.3, 1.3, 0.05, GREEN))
    for r in range(8):
        for c in range(8):
            px, py = iso(cx0_ + 0.38 + c * 0.145, cy0_ + 0.33 + r * 0.145, lz + 0.05)
            a(f'<rect x="{px - 1.4:.1f}" y="{py - 0.9:.1f}" width="2.8" height="1.8" fill="#f2f2ea"/>')
    for hx_, hy_ in [(0.36, 0.31), (1.54, 0.31), (0.36, 1.49), (1.54, 1.49)]:
        px, py = iso(cx0_ + hx_, cy0_ + hy_, lz + 0.05)
        a(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="2.4" ry="1.4" fill="#d8b04a"/><ellipse cx="{px:.1f}" cy="{py:.1f}" rx="1.1" ry="0.7" fill="#0c1018"/>')
    # Command PCB (5 gold contacts)
    kz = ct + 1.05
    a(box(cx0_ + 0.2, cy0_ + 0.75, kz, 1.5, 0.32, 0.05, GREEN))
    for k in range(5):
        px, py = iso(cx0_ + 0.33 + k * 0.29, cy0_ + 0.91, kz + 0.05)
        a(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="3.2" ry="1.9" fill="#e8c45a"/>')
    # Controller PCB with Nano footprint
    cz = ct + 1.6
    a(box(cx0_ + 0.6, cy0_ + 0.6, cz, 0.7, 0.6, 0.05, GREEN))
    a(box(cx0_ + 0.72, cy0_ + 0.78, cz + 0.05, 0.46, 0.22, 0.05, ("#00979c", "#00777b", "#006165")))
    a('</g>')
    tgx, tgy = iso(cx0_ + cw_, cy0_ + cd_, 0)
    a(f'<text x="{tgx:.1f}" y="{tgy + 22:.1f}" text-anchor="middle" font-family="{MONO}" font-size="9" fill="#4fd1ff" opacity="0.85">KiCad 3D · MANEK PCBs</text>')

    # ================================================= theme items on the stool
    st = th["stool"]
    sx3, sy3 = iso(3.07, 4.77, 1.35)
    if isinstance(st, tuple) and st[0] == "cake":
        age = st[1]
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})">'
          f'<ellipse cx="0" cy="0" rx="20" ry="9" fill="#e8e3d8"/>'
          f'<rect x="-17" y="-16" width="34" height="16" fill="#fbfbf7"/><ellipse cx="0" cy="0" rx="17" ry="7.5" fill="#fbfbf7"/>'
          f'<rect x="-17" y="-9" width="34" height="3" fill="#003580"/>'
          f'<ellipse cx="0" cy="-16" rx="17" ry="7.5" fill="#ffffff"/>'
          + "".join(f'<circle cx="{12 * math.cos(math.radians(j * 40)):.1f}" cy="{-16 + 5.2 * math.sin(math.radians(j * 40)):.1f}" r="1.6" fill="#d8343f"/>' for j in range(9))
          + f'<text x="0" y="-19" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="800" fill="#003580">{age}</text>'
          + "".join(f'<rect x="{-8 + k * 7}" y="-38" width="2.4" height="9" fill="#9cc4ff"/>'
                    f'<ellipse cx="{-6.8 + k * 7:.1f}" cy="-41" rx="1.6" ry="3" fill="#ffcf5a" filter="url(#glow)">'
                    f'<animate attributeName="ry" values="3;2.4;3.4;3" dur="0.8s" begin="{k * 0.2:.1f}s" repeatCount="indefinite"/></ellipse>' for k in range(3))
          + '</g>')
    elif st == "champagne":
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})">'
          f'<ellipse cx="0" cy="1" rx="8" ry="3" fill="#000" opacity="0.3"/>'
          f'<path d="M-7 0 L-7 -24 Q-7 -32 -3 -36 L-3 -46 L3 -46 L3 -36 Q7 -32 7 -24 L7 0 Z" fill="#1f4d2b"/>'
          f'<rect x="-7" y="-20" width="14" height="10" fill="#f3e3b0"/><rect x="-3.2" y="-50" width="6.4" height="7" fill="#e8c45a"/>'
          f'<rect x="-2.4" y="-50" width="4.8" height="5" rx="1.5" fill="#c9a36a">'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;14 -60;14 -60;0 0" keyTimes="0;0.4;0.55;0.95;1" dur="4s" repeatCount="indefinite"/></rect>'
          + "".join(f'<circle cx="{rnd.uniform(-3, 3):.1f}" cy="-48" r="1.4" fill="#fff6c8" opacity="0">'
                    f'<animate attributeName="opacity" values="0;0;0.9;0" keyTimes="0;0.4;0.5;1" dur="4s" begin="{k * 0.07:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="cy" values="-48;-48;{-60 - k * 4};{-70 - k * 5}" keyTimes="0;0.4;0.6;1" dur="4s" repeatCount="indefinite"/></circle>' for k in range(7))
          + f'<path d="M14 0 L13 -14 Q18 -15 22 -14 L21 0 Z" fill="#ffffff" opacity="0.35"/><path d="M15 -3 L14.5 -10 L20.5 -10 L20 -3 Z" fill="#f6d36b" opacity="0.8"/>'
          + '</g>')
    elif st == "tin":
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})">'
          f'<ellipse cx="0" cy="0" rx="15" ry="6" fill="#5d6799"/><rect x="-15" y="-14" width="30" height="14" fill="#7d849b"/>'
          f'<ellipse cx="0" cy="-14" rx="15" ry="6" fill="#4fa3d1"/><ellipse cx="0" cy="-14" rx="11" ry="4" fill="#7fc3e8"/>'
          f'<path d="M-4 -16 q2 -4 5 -1 q3 -4 4 1 q-3 3 -9 0 z" fill="#c3c8d8" stroke="#9aa1b8" stroke-width="0.5"/>'
          f'<path d="M14 -20 L30 -34" stroke="#3a2414" stroke-width="2.5"/><ellipse cx="10" cy="-18" rx="5" ry="2.5" fill="#9aa1b8"/>'
          + "".join(f'<path d="M{-6 + k * 5} -20 q-2 -5 0 -9" stroke="#ffffff" stroke-width="1.2" fill="none" opacity="0">'
                    f'<animate attributeName="opacity" values="0;0.6;0" dur="2s" begin="{k * 0.5:.1f}s" repeatCount="indefinite"/></path>' for k in range(3))
          + '</g>')
    elif st == "torte":
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})">'
          f'<ellipse cx="0" cy="0" rx="16" ry="6" fill="#f3efe4"/>'
          f'<path d="M-8 -2 L-9 -16 L9 -16 L8 -2 Z" fill="#c98a4a"/><ellipse cx="0" cy="-16" rx="9" ry="3.5" fill="#f6f2ea"/>'
          f'<ellipse cx="0" cy="-17" rx="5" ry="2" fill="#c2213a"/></g>')
    elif st == "willow":
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})">'
          f'<path d="M-6 0 L-8 -16 L8 -16 L6 0 Z" fill="#ffc940"/>'
          + "".join(f'<path d="M0 -16 Q{dxw / 2:.1f} -40 {dxw:.1f} -58" stroke="#6b3e25" stroke-width="1.2" fill="none"/>'
                    + "".join(f'<ellipse cx="{dxw * t:.1f}" cy="{-16 - 42 * t:.1f}" rx="2" ry="1.4" fill="#e8e6e0"/>' for t in (0.35, 0.55, 0.75, 0.95))
                    for dxw in (-14, -4, 6, 15))
          + '<path d="M-12 -46 l3 2 l-3 2 z M8 -40 l3 2 l-3 2 z" fill="#ff8fb0"/>'
          + '</g>')
    elif st == "sausage":
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})">'
          f'<ellipse cx="0" cy="-2" rx="16" ry="7" fill="#f3efe4"/>'
          f'<rect x="-11" y="-8" width="22" height="7" rx="3.5" fill="#b3542e" transform="rotate(-8)"/>'
          f'<path d="M-8 -7 l3 2 M-2 -8 l3 2 M4 -9 l3 2" stroke="#6b2a14" stroke-width="1"/>'
          f'<path d="M-9 -9 Q0 -13 9 -11" stroke="#f2c230" stroke-width="1.6" fill="none"/></g>')
    elif st == "gingerbread":
        a(f'<g transform="translate({sx3:.1f} {sy3:.1f})"><ellipse cx="0" cy="-2" rx="16" ry="7" fill="#f3efe4"/>'
          + "".join(f'<path transform="translate({ox} {oy}) rotate({rot})" d="M0 -6 a2.4 2.4 0 1 1 0.1 0 M-1.8 -4 L-5 -1 L-2 -1 L-3 4 L-0.5 4 L0 1 L0.5 4 L3 4 L2 -1 L5 -1 L1.8 -4 Z" fill="#b5652e"/>'
                    for ox, oy, rot in [(-6, -3, -10), (6, -4, 12), (0, 0, 0)])
          + '</g>')

    # ================================================= floor theme items
    if "xmas_tree" in th["tags"]:
        tx3, ty3 = iso(3.2, 8.6, 0)
        a(f'<g transform="translate({tx3:.1f} {ty3:.1f})">'
          f'<ellipse cx="0" cy="0" rx="22" ry="9" fill="#000" opacity="0.25"/>'
          f'<rect x="-4" y="-10" width="8" height="10" fill="#6b4a2e"/>'
          f'<path d="M-24 -10 L0 -40 L24 -10 Z M-19 -30 L0 -58 L19 -30 Z M-13 -48 L0 -74 L13 -48 Z" fill="#1f6b3a"/>'
          f'<path d="M-24 -10 L0 -40 L0 -10 Z M-19 -30 L0 -58 L0 -30 Z M-13 -48 L0 -74 L0 -48 Z" fill="#2a8a4b"/>'
          + "".join(f'<circle cx="{x_}" cy="{y_}" r="2" fill="{c_}" filter="url(#glow)"><animate attributeName="opacity" values="1;0.3;1" dur="1.6s" begin="{i * 0.3:.1f}s" repeatCount="indefinite"/></circle>'
                    for i, (x_, y_, c_) in enumerate([(-14, -16, "#ff4d5e"), (8, -20, "#ffc940"), (-4, -34, "#3fa9ff"), (11, -38, "#ff4d5e"),
                                                      (-8, -50, "#ffc940"), (5, -56, "#39d353"), (-15, -28, "#d07bff"), (16, -14, "#3fa9ff")]))
          + '<path d="M0 -84 l2.5 6 l6 0.5 l-4.7 4 l1.5 6 l-5.3 -3.3 l-5.3 3.3 l1.5 -6 l-4.7 -4 l6 -0.5 z" fill="#ffd54a" filter="url(#glow)"/>'
          + '</g>')
    if "presents" in th["tags"]:
        for (gx3, gy3, w3, col, rib) in [(2.25, 9.0, 0.5, ("#e0303c", "#b8242f", "#961d26"), "#ffd54a"),
                                         (3.7, 9.1, 0.42, ("#3fa9ff", "#2f86cc", "#256ba3"), "#ffffff"),
                                         (2.9, 9.4, 0.36, ("#39d353", "#2aa63f", "#1f8030"), "#e0303c")]:
            a(box(gx3, gy3, 0, w3, w3, w3 * 0.8, col))
            a(line((gx3 + w3 / 2, gy3, w3 * 0.8), (gx3 + w3 / 2, gy3 + w3, w3 * 0.8), rib, 2))
            a(line((gx3, gy3 + w3 / 2, w3 * 0.8), (gx3 + w3, gy3 + w3 / 2, w3 * 0.8), rib, 2))
    if "easter" in th["tags"]:
        for (ex3, ey3, col) in [(5.2, 8.6, "#ffc940"), (6.1, 9.1, "#ff8fb0"), (3.1, 9.2, "#8ef0a8"), (8.6, 8.8, "#9cc4ff"), (4.2, 9.5, "#d07bff")]:
            px, py = iso(ex3, ey3, 0)
            a(f'<ellipse cx="{px:.1f}" cy="{py - 5:.1f}" rx="4.5" ry="6" fill="{col}"/>'
              f'<path d="M{px - 4.3:.1f} {py - 5:.1f} l2 -2 l2 2 l2 -2 l2 2" stroke="#ffffff" stroke-width="1" fill="none"/>')

    # ================================================= hats & Manek the hedgehog
    def hat_svg(kind, sgn, hx, hy):
        if kind == "santa":
            return (f'<path d="M{hx - 6:.1f} {hy:.1f} L{hx + 6:.1f} {hy:.1f} L{hx - sgn * 6:.1f} {hy - 14:.1f} Z" fill="#e0303c"/>'
                    f'<rect x="{hx - 7:.1f}" y="{hy - 1.5:.1f}" width="14" height="3" rx="1.5" fill="#fff"/>'
                    f'<circle cx="{hx - sgn * 6:.1f}" cy="{hy - 14:.1f}" r="2.4" fill="#fff"/>')
        if kind == "party":
            return (f'<path d="M{hx - 5:.1f} {hy:.1f} L{hx + 5:.1f} {hy:.1f} L{hx:.1f} {hy - 16:.1f} Z" fill="#d07bff"/>'
                    f'<path d="M{hx - 3.4:.1f} {hy - 5:.1f} L{hx + 3.4:.1f} {hy - 5:.1f} M{hx - 1.8:.1f} {hy - 10:.1f} L{hx + 1.8:.1f} {hy - 10:.1f}" stroke="#ffc940" stroke-width="1.5"/>'
                    f'<circle cx="{hx:.1f}" cy="{hy - 16:.1f}" r="2.2" fill="#ffc940"/>')
        if kind == "witch":
            return (f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="10" ry="2.4" fill="#1d1d22"/>'
                    f'<path d="M{hx - 5:.1f} {hy:.1f} L{hx + 5:.1f} {hy:.1f} L{hx + sgn * 2:.1f} {hy - 12:.1f} L{hx + sgn * 8:.1f} {hy - 16:.1f} Z" fill="#1d1d22"/>'
                    f'<rect x="{hx - 5:.1f}" y="{hy - 3:.1f}" width="10" height="2" fill="#d07bff"/>')
        if kind == "cap":   # Finnish student cap
            return (f'<ellipse cx="{hx + sgn * 3:.1f}" cy="{hy + 0.5:.1f}" rx="8" ry="2" fill="#111"/>'
                    f'<rect x="{hx - 6:.1f}" y="{hy - 5:.1f}" width="12" height="5" fill="#111"/>'
                    f'<path d="M{hx - 7:.1f} {hy - 5:.1f} Q{hx:.1f} {hy - 11:.1f} {hx + 7:.1f} {hy - 5:.1f} Z" fill="#ffffff"/>'
                    f'<path d="M{hx + sgn * 6:.1f} {hy - 6:.1f} q{sgn * 3:.1f} 4 {sgn * 1:.1f} 9" stroke="#111" stroke-width="1" fill="none"/>'
                    f'<circle cx="{hx:.1f}" cy="{hy - 4:.1f}" r="1.2" fill="#e8c45a"/>')
        if kind == "flowers":
            cols = ["#ffd54a", "#ff8fb0", "#ffffff", "#9cc4ff", "#ff4d5e"]
            return "".join(f'<circle cx="{hx + 8 * math.cos(math.radians(180 + j * 30)):.1f}" cy="{hy + 2.4 * math.sin(math.radians(180 + j * 30)):.1f}" r="2.2" fill="{cols[j % 5]}"/>'
                           for j in range(7))
        return ""

    def hedgehog(flip, carry=False, hat=None):
        sgn = -1 if flip else 1
        sp = []
        for k in range(9):
            ang = math.radians(200 + k * 17.5)
            sp.append((sgn * 15 * math.cos(ang), 15 * 0.7 * math.sin(ang)))
            ang2 = math.radians(200 + k * 17.5 + 8.75)
            sp.append((sgn * 21 * math.cos(ang2), 21 * 0.75 * math.sin(ang2)))
        spp = " ".join(f"{x:.1f},{y:.1f}" for x, y in sp)
        g = (f'<ellipse cx="0" cy="2" rx="17" ry="7" fill="#000" opacity="0.25"/>'
             f'<polygon points="{spp}" fill="#5b3a24"/>'
             f'<ellipse cx="0" cy="-5" rx="15" ry="9" fill="#6e4a2f"/>'
             f'<ellipse cx="{sgn * 13:.1f}" cy="-3" rx="8" ry="5.5" fill="#e2c39b"/>'
             f'<circle cx="{sgn * 20:.1f}" cy="-3" r="2" fill="#1a1a1a"/>'
             f'<circle cx="{sgn * 13:.1f}" cy="-6" r="1.6" fill="#1a1a1a"/>'
             f'<circle cx="{sgn * 5:.1f}" cy="1" r="2.2" fill="#3a2516"/><circle cx="{sgn * -7:.1f}" cy="1" r="2.2" fill="#3a2516"/>')
        if carry:
            g += f'<rect x="-11" y="-21" width="20" height="5" rx="1" fill="#e3c48f" stroke="#a5783f" stroke-width="0.6" transform="rotate({-8 * sgn})"/>'
        if hat:
            g += hat_svg(hat, sgn, sgn * 12, -9)
        return g

    hat = th["hat"]
    if sleeping:
        cx0, cy0 = 4.6, 6.6
        a(box(cx0, cy0, 0, 1.2, 1.0, 0.45, ("#3a2a1c", "#c79a5d", "#a5783f")))
        hx_, hy_ = iso(cx0 + 0.6, cy0 + 0.5, 0.45)
        a(f'<g transform="translate({hx_:.1f} {hy_ + 2:.1f}) scale(1.3)">'
          f'<ellipse cx="0" cy="-4" rx="13" ry="8" fill="#5b3a24"/>'
          + "".join(f'<path d="M{-12 + k * 4} -6 l2 -6 l2 6" fill="#4a2e1c"/>' for k in range(6))
          + f'<ellipse cx="9" cy="-1" rx="5" ry="3.5" fill="#e2c39b"/><path d="M8 -2 q2 1 4 0" stroke="#1a1a1a" stroke-width="1" fill="none"/>'
          + (hat_svg(hat, 1, 6, -10) if hat else "")
          + '</g>')
        for k, (dx_, sz) in enumerate([(14, 9), (22, 11), (31, 14)]):
            a(f'<text x="{hx_ + dx_:.1f}" y="{hy_ - 18 - k * 9:.1f}" font-family="{FONT}" font-size="{sz}" font-weight="700" fill="#c9d1ff" opacity="0">z'
              f'<animate attributeName="opacity" values="0;0.9;0" dur="3s" begin="{k * 0.6:.1f}s" repeatCount="indefinite"/></text>')
        anchor_x, anchor_y = hx_, hy_ - 10
    else:
        carry = data["today_commits"] >= 3
        p_a, p_b = iso(3.8, 7.6, 0), iso(6.9, 7.6, 0)
        dx, dy = p_b[0] - p_a[0], p_b[1] - p_a[1]
        walk = f'values="0 0;{dx:.1f} {dy:.1f};{dx:.1f} {dy:.1f};0 0;0 0" keyTimes="0;0.45;0.5;0.95;1"'
        a(f'<g transform="translate({p_a[0]:.1f} {p_a[1]:.1f})"><g>'
          f'<animateTransform attributeName="transform" type="translate" dur="12s" repeatCount="indefinite" {walk}/>'
          f'<g><animate attributeName="opacity" values="1;0;1" keyTimes="0;0.475;0.975" calcMode="discrete" dur="12s" repeatCount="indefinite"/>'
          f'<g transform="scale(1.45)">{hedgehog(False, carry, hat)}</g></g>'
          f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;0.475;0.975" calcMode="discrete" dur="12s" repeatCount="indefinite"/>'
          f'<g transform="scale(1.45)">{hedgehog(True, carry, hat)}</g></g>'
          + ('<g transform="translate(0 -40)"><circle r="1.6" fill="#1a1a1a">'
             '<animateMotion dur="2.2s" repeatCount="indefinite" path="M0 0 C 18 -10 26 8 8 12 C -14 16 -24 -6 0 0"/></circle>'
             f'<text x="16" y="-10" font-family="{MONO}" font-size="8" fill="#c9d1ff">bzz</text></g>' if "mosquito" in th["tags"] else "")
          + f'</g></g>')

    # ================================================= HUD
    w_ = data["weather"]
    icon = {"snow": "❄", "rain": "☂", "clear": "☀" if not night else "☾", "cloudy": "☁"}.get(w_["kind"], "•")
    a(f'<text x="44" y="64" font-family="{FONT}" font-size="30" font-weight="800" fill="#f3f0e6">{escape(data["name"])}</text>')
    a(f'<text x="46" y="92" font-family="{MONO}" font-size="14" fill="#8b95c9">{escape(data.get("tagline", "Teacher · Maker · Future AI developer"))}</text>')
    a(f'<text x="46" y="128" font-family="{MONO}" font-size="12" fill="#5d6799">'
      f'{escape(w_["city"])} {w_["temp"]:+d}°C {icon}  ·  {d.day}.{d.month}.{d.year}'
      f'{f" {hour:02d}:00" if data.get("show_clock", True) else ""}</text>')
    if th["flag"] or th["hud"]:
        label = " · ".join(x for x in [th["hud"], th["flag"]] if x)
        a(f'<g transform="translate(46 146)"><rect x="0" y="0" width="16" height="10" fill="#fff"/>'
          f'<rect x="4.5" y="0" width="3" height="10" fill="#003580"/><rect x="0" y="3.5" width="16" height="3" fill="#003580"/>'
          f'<text x="24" y="9" font-family="{MONO}" font-size="12" fill="#c9d1ff">{escape(label)}</text></g>')
    won = sum(1 for _, t in data["trophies"] if t)
    stats = [("CONTRIBUTIONS", str(data["year_total"]), "this year"),
             ("STREAK", f'{data["streak"]} d', "and counting"),
             ("TOP LANGUAGE", data["languages"][0][0], data.get("lang_source", "by bytes")),
             ("TROPHIES", f"{won}/{len(data['trophies'])}", "on the shelf")]
    for i, (lab, val, sub) in enumerate(stats):
        x0, y0 = 960, 40 + i * 66
        a(f'<rect x="{x0}" y="{y0}" width="200" height="56" rx="10" fill="#141a36" stroke="#2f3870"/>')
        a(f'<text x="{x0 + 14}" y="{y0 + 19}" font-family="{MONO}" font-size="10" fill="#8b95c9" letter-spacing="1">{lab}</text>')
        a(f'<text x="{x0 + 14}" y="{y0 + 44}" font-family="{FONT}" font-size="21" font-weight="800" fill="#f3f0e6">{escape(val)}</text>')
        a(f'<text x="{x0 + 186}" y="{y0 + 44}" text-anchor="end" font-family="{MONO}" font-size="10" fill="#5d6799">{sub}</text>')

    px0, py0 = 960, 312
    projs = data["projects"]
    a(f'<rect x="{px0}" y="{py0}" width="200" height="{34 + len(projs) * 30}" rx="10" fill="#141a36" stroke="#2f3870"/>')
    a(f'<text x="{px0 + 14}" y="{py0 + 21}" font-family="{MONO}" font-size="10" fill="#8b95c9" letter-spacing="1">PROJECTS</text>')
    for i, (pname, pc) in enumerate(projs):
        yb = py0 + 42 + i * 30
        col = "#39d353" if pc >= 75 else "#ffc940" if pc >= 40 else "#3fa9ff"
        a(f'<text x="{px0 + 14}" y="{yb}" font-family="{FONT}" font-size="11.5" font-weight="600" fill="#e6e8f5">{escape(pname)}</text>')
        a(f'<text x="{px0 + 186}" y="{yb}" text-anchor="end" font-family="{MONO}" font-size="11" font-weight="700" fill="{col}">{pc}%</text>')
        a(f'<rect x="{px0 + 14}" y="{yb + 6}" width="172" height="5" rx="2.5" fill="#262c55"/>')
        a(f'<rect x="{px0 + 14}" y="{yb + 6}" width="0" height="5" rx="2.5" fill="{col}">'
          f'<animate attributeName="width" values="0;{172 * pc / 100:.1f}" dur="1.6s" begin="{0.3 + i * 0.2:.1f}s" fill="freeze"/></rect>')

    lx0, ly0 = 44, 592
    a(f'<text x="{lx0}" y="{ly0}" font-family="{MONO}" font-size="11" fill="#8b95c9">MANEK board = my last 64 days on GitHub</text>')
    for i, col in enumerate(LED_LEVELS):
        a(f'<circle cx="{lx0 + 6 + i * 18}" cy="{ly0 + 18}" r="6" fill="{col}"/>')
    a(f'<text x="{lx0 + 100}" y="{ly0 + 22}" font-family="{MONO}" font-size="10" fill="#5d6799">less → more</text>')
    a(f'<text x="{lx0}" y="{ly0 + 44}" font-family="{MONO}" font-size="10" fill="#5d6799">☕ steam = today\'s commits · 🦔 sleeps when I do · nixie = visitors</text>')
    a(f'<text x="{W - 44}" y="{ly0 + 44}" text-anchor="end" font-family="{MONO}" font-size="10" fill="#5d6799">'
      f'auto-updated every 2 hours by a Python script</text>')

    body = "\n".join(out)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Sami\'s Workshop – living GitHub profile">\n{body}\n</svg>\n')


THEME_DEMOS = {
    "dec6": DEMO_DEC6,
    "xmas": dict(DEMO_DATA, date="2026-12-24", hour=16, weather={"city": "Helsinki", "temp": -6, "kind": "snow"}),
    "newyear": dict(DEMO_DATA, date="2026-12-31", hour=23, weather={"city": "Helsinki", "temp": -9, "kind": "clear"}),
    "easter": dict(DEMO_DATA, date="2027-03-28", hour=12, weather={"city": "Helsinki", "temp": 3, "kind": "cloudy"}),
    "vappu": dict(DEMO_DATA, date="2027-05-01", hour=13, weather={"city": "Helsinki", "temp": 12, "kind": "clear"}),
    "juhannus": dict(DEMO_DATA, date="2027-06-25", hour=23, weather={"city": "Helsinki", "temp": 16, "kind": "clear"}),
    "runeberg": dict(DEMO_DATA, date="2027-02-05", hour=11, weather={"city": "Helsinki", "temp": -4, "kind": "cloudy"}),
}


if __name__ == "__main__":
    import sys
    which = sys.argv[2] if len(sys.argv) > 2 else "demo"
    data = THEME_DEMOS.get(which, DEMO_DATA)
    out_path = sys.argv[1] if len(sys.argv) > 1 else "workshop.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render(data))
    print("wrote", out_path)
