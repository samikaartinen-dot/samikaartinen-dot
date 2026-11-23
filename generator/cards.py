"""Isometric project cards for the README (cards/<slug>.svg).

Each card: a small animated iso illustration, title, two text lines and a progress
bar whose percentage comes from config.yml -> projects.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 420, 210
C30 = math.cos(math.radians(30))
FONT = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"


class Iso:
    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y, z=0.0):
        return self.ox + (x - y) * self.s * C30, self.oy + (x + y) * self.s * 0.5 - z * self.s

    def poly(self, points, fill, extra=""):
        pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in (self.p(*q) for q in points))
        return f'<polygon points="{pts}" fill="{fill}" {extra}/>'

    def box(self, x, y, z, w, d, h, top, left, right):
        return "".join([
            self.poly([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], left),
            self.poly([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], right),
            self.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], top),
        ])


# ------------------------------------------------------------------ illustrations
def art_manek(iso):
    out = [iso.box(0, 0, 0, 4, 4, 0.7, "#d9b47a", "#b5874c", "#8c6434"),
           iso.poly([(0.2, 0.2, 0.7), (3.8, 0.2, 0.7), (3.8, 3.8, 0.7), (0.2, 3.8, 0.7)], "#0c1018")]
    cell = 3.4 / 8
    cols = "#1b2232;#39d353;#26a641;#1b2232"
    for r in range(8):
        for c in range(8):
            px, py = iso.p(0.3 + cell * (c + 0.5), 0.3 + cell * (r + 0.5), 0.7)
            out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{cell * iso.s * C30 * 0.6:.1f}" ry="{cell * iso.s * 0.3:.1f}" fill="#1b2232">'
                       f'<animate attributeName="fill" values="{cols}" dur="2.4s" begin="{(r + c) * 0.1:.1f}s" repeatCount="indefinite"/></ellipse>')
    # command blocks in front
    shades = {"#ff4d5e": ("#c93a48", "#a32f3a"), "#ffc940": ("#d6a72f", "#b38a22"), "#3fa9ff": ("#2f86cc", "#256ba3"),
              "#39d353": ("#2aa63f", "#1f8030"), "#d07bff": ("#a660d0", "#8a4caf")}
    for k, col in enumerate(shades):
        out.append(iso.box(0.3 + k * 0.72, 4.3, 0, 0.55, 0.55, 0.45, col, *shades[col]))
    return "".join(out)


def art_liiga(iso):
    out = [iso.box(0, 0, 0, 5.2, 3.0, 0.3, "#eef3fb", "#c9d1e6", "#aeb8d3"),
           iso.poly([(0.15, 0.15, 0.3), (5.05, 0.15, 0.3), (5.05, 2.85, 0.3), (0.15, 2.85, 0.3)], "#f7fbff")]
    for x, col in [(2.6, "#e0303c"), (1.75, "#3f7fd6"), (3.45, "#3f7fd6")]:
        a, b = iso.p(x, 0.15, 0.3), iso.p(x, 2.85, 0.3)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="2"/>')
    cx, cy = iso.p(2.6, 1.5, 0.3)
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{0.5 * iso.s * C30 * 1.4:.1f}" ry="{0.5 * iso.s * 0.7:.1f}" fill="none" stroke="#3f7fd6" stroke-width="1.4"/>')
    for gx in (0.45, 4.75):
        out.append(iso.box(gx - 0.12, 1.25, 0.3, 0.24, 0.5, 0.35, "#e0303c", "#b8242f", "#961d26"))
    # moving puck
    a, b, c = iso.p(1.0, 2.2, 0.32), iso.p(3.8, 0.9, 0.32), iso.p(4.5, 1.5, 0.32)
    out.append(f'<g><ellipse rx="4" ry="2" fill="#111"/>'
               f'<animateMotion dur="3s" repeatCount="indefinite" path="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} L{c[0]:.1f} {c[1]:.1f} L{a[0]:.1f} {a[1]:.1f}"/></g>')
    # two little players (sticks)
    for (x, y, col) in [(1.5, 1.0, "#ffc940"), (3.6, 2.1, "#3fa9ff")]:
        px, py = iso.p(x, y, 0.3)
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="5" ry="2.5" fill="#00000033"/>'
                   f'<rect x="{px - 3:.1f}" y="{py - 16:.1f}" width="6" height="14" rx="2.5" fill="{col}"/>'
                   f'<circle cx="{px:.1f}" cy="{py - 19:.1f}" r="3.2" fill="{col}"/>'
                   f'<path d="M{px + 3:.1f} {py - 8:.1f} L{px + 9:.1f} {py:.1f} l4 0" stroke="#1d1d22" stroke-width="1.6" fill="none"/>')
    return "".join(out)


def art_python(iso):
    out = [iso.box(0.3, 0.2, 0, 3.0, 1.6, 0.15, "#3a3f52", "#2b2f3d", "#22252f"),
           iso.box(1.5, 0.7, 0.15, 0.5, 0.4, 0.5, "#2b2f3d", "#22252f", "#1b1d25"),
           iso.box(0.4, 0.8, 0.6, 2.8, 0.15, 1.8, "#2b2f3d", "#1f222c", "#16181f"),
           iso.poly([(0.5, 0.95, 0.7), (3.1, 0.95, 0.7), (3.1, 0.95, 2.3), (0.5, 0.95, 2.3)], "#0a0e1a")]
    lines = [(">>> import ai", "#8b95c9"), (">>> sami.learn()", "#ffc940"), ("level up ▲", "#39d353")]
    for i, (t, col) in enumerate(lines):
        px, py = iso.p(0.6, 0.95, 2.0 - i * 0.42)
        out.append(f'<text transform="matrix({C30:.4f} 0.5 0 1 {px:.1f} {py:.1f})" font-family="{MONO}" font-size="6.5" fill="{col}">{escape(t)}</text>')
    # python-coloured blocks stacking up
    for k, (x, y, z, col) in enumerate([(3.6, 1.8, 0, "#3776ab"), (4.3, 1.8, 0, "#ffd43b"), (3.95, 1.8, 0.6, "#3776ab")]):
        dark = "#2b5d87" if col == "#3776ab" else "#d6b12f"
        darker = "#204a6b" if col == "#3776ab" else "#b8961f"
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.9;1" dur="4s" begin="{k * 0.5:.1f}s" repeatCount="indefinite"/>'
                   + iso.box(x, y, z, 0.6, 0.6, 0.6, col, dark, darker) + '</g>')
    return "".join(out)


ARTS = {"manek": art_manek, "liiga": art_liiga, "python": art_python}
ART_ORIGIN = {"manek": (108, 64, 24), "liiga": (100, 66, 20), "python": (96, 74, 24)}


def render_card(card, pct):
    accent = card.get("accent", "#39d353")
    iso = Iso(*ART_ORIGIN.get(card.get("art", ""), (110, 70, 24)))
    art = ARTS.get(card.get("art", ""), lambda i: "")(iso)
    bar_w = 190 * max(0, min(100, pct)) / 100
    tags = card.get("tags", [])
    tag_svg, tx = "", 210
    for t in tags[:3]:
        w = 14 + len(t) * 6.4
        tag_svg += (f'<rect x="{tx}" y="160" width="{w:.0f}" height="20" rx="10" fill="none" stroke="{accent}" stroke-opacity="0.6"/>'
                    f'<text x="{tx + w / 2:.1f}" y="174" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{accent}">{escape(t)}</text>')
        tx += w + 6
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(card['title'])} – {pct}% done">
<defs><radialGradient id="bg" cx="0.25" cy="0.4" r="0.9"><stop offset="0" stop-color="#1d2347"/><stop offset="1" stop-color="#0b0e20"/></radialGradient></defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="url(#bg)" stroke="#2f3870"/>
{art}
<text x="210" y="44" font-family="{FONT}" font-size="22" font-weight="800" fill="#f3f0e6">{escape(card['title'])}</text>
<text x="210" y="70" font-family="{MONO}" font-size="10.5" fill="#a8b3d6">{escape(card.get('line1', ''))}</text>
<text x="210" y="87" font-family="{MONO}" font-size="10.5" fill="#a8b3d6">{escape(card.get('line2', ''))}</text>
<text x="210" y="122" font-family="{MONO}" font-size="10" fill="#8b95c9" letter-spacing="1">PROGRESS</text>
<text x="400" y="122" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="700" fill="{accent}">{pct}%</text>
<rect x="210" y="130" width="190" height="7" rx="3.5" fill="#262c55"/>
<rect x="210" y="130" width="0" height="7" rx="3.5" fill="{accent}"><animate attributeName="width" values="0;{bar_w:.1f}" dur="1.4s" fill="freeze"/></rect>
{tag_svg}
</svg>
"""


def build_cards(cfg, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    pcts = {p["name"]: int(p["percent"]) for p in cfg.get("projects", [])}
    written = []
    for card in cfg.get("cards", []):
        pct = int(card.get("percent", pcts.get(card.get("project", card["title"]), 0)))
        path = out_dir / f"{card['slug']}.svg"
        path.write_text(render_card(card, pct), encoding="utf-8")
        written.append(path)
    return written
