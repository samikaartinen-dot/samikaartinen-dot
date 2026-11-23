"""Build workshop.svg from config.yml + live data.

Usage:
    python generator/build.py              # live data (needs GITHUB_TOKEN env)
    python generator/build.py --offline    # demo data, no network (for testing the drawing)
    python generator/build.py --offline --date 2026-12-06 --hour 17   # preview a theme day

Status: drawing + config are tested. The live fetch functions (GitHub GraphQL,
Open-Meteo, komarev) are written but NOT yet tested against the real APIs –
see HANDOFF.md.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from workshop import DEMO_DATA, render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LANG_SHORT = {"Python": "PY", "JavaScript": "JS", "TypeScript": "TS", "C++": "C++", "C": "C",
              "HTML": "HTML", "CSS": "CSS", "Shell": "SH", "Jupyter Notebook": "IPYNB", "Arduino": "INO"}


# ------------------------------------------------------------------ HTTP helpers
def http_json(url, data=None, headers=None, timeout=20):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def http_text(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "sami-workshop"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# ------------------------------------------------------------------ GitHub
GQL = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 20, orderBy: {field: PUSHED_AT, direction: DESC},
                 ownerAffiliations: OWNER, privacy: PUBLIC) {
      nodes {
        name
        defaultBranchRef { target { ... on Commit { message } } }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}"""


def fetch_github(login, token, today):
    body = json.dumps({"query": GQL, "variables": {"login": login}}).encode()
    res = http_json("https://api.github.com/graphql", data=body,
                    headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    if "errors" in res:
        raise RuntimeError(res["errors"])
    user = res["data"]["user"]
    days = {}
    for w in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for dd in w["contributionDays"]:
            days[date.fromisoformat(dd["date"])] = dd["contributionCount"]

    def count(d):
        return days.get(d, 0)

    last64 = [count(today - timedelta(days=63 - i)) for i in range(64)]
    year_total = sum(v for d, v in days.items() if d.year == today.year and d <= today)
    week = sum(count(today - timedelta(days=i)) for i in range(7))
    # streak: consecutive days with contributions, ending today (or yesterday if today is still empty)
    streak, d = 0, today if count(today) > 0 else today - timedelta(days=1)
    while count(d) > 0:
        streak += 1
        d -= timedelta(days=1)
    since, d = 0, today
    while count(d) == 0 and since < 400:
        since += 1
        d -= timedelta(days=1)

    repos = [r for r in user["repositories"]["nodes"] if r["name"].lower() != login.lower()]
    sizes = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:4]
    total = sum(v for _, v in top) or 1
    languages = [(LANG_SHORT.get(k, k[:4].upper()), round(100 * v / total)) for k, v in top] or DEMO_DATA["languages"]
    latest = repos[0] if repos else None
    msg = ""
    if latest and latest.get("defaultBranchRef") and latest["defaultBranchRef"].get("target"):
        msg = (latest["defaultBranchRef"]["target"].get("message") or "").splitlines()[0]
    return {
        "contributions": last64, "year_total": year_total, "streak": streak,
        "today_commits": count(today), "week_commits": week, "days_since_commit": since,
        "languages": languages, "latest_repo": latest["name"] if latest else "",
        "last_commit": msg or "hello world",
    }


# ------------------------------------------------------------------ weather (Open-Meteo, no key)
def weather_kind(code):
    if code in (0, 1):
        return "clear"
    if code in (2, 3, 45, 48):
        return "cloudy"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    return "rain"


def fetch_weather(cfg):
    url = ("https://api.open-meteo.com/v1/forecast?"
           f"latitude={cfg['latitude']}&longitude={cfg['longitude']}"
           f"&current=temperature_2m,weather_code&timezone={cfg['timezone']}")
    cur = http_json(url)["current"]
    return {"city": cfg["city"], "temp": round(cur["temperature_2m"]), "kind": weather_kind(cur["weather_code"])}


# ------------------------------------------------------------------ visitors (experimental)
def fetch_visitors(cfg):
    if cfg.get("visitors", {}).get("source") != "komarev":
        return None
    svg = http_text(f"https://komarev.com/ghpvc/?username={cfg['github_user']}")
    nums = re.findall(r">\s*([\d,]+)\s*<", svg)
    return int(nums[-1].replace(",", "")) if nums else None


# ------------------------------------------------------------------ config -> data
def build_data(cfg, live, now):
    today = now.date()
    data = dict(DEMO_DATA)
    data.update({
        "name": cfg["name"], "tagline": cfg.get("tagline", ""), "date": today.isoformat(), "hour": now.hour,
        "now_building": cfg["now_building"], "learning": cfg["learning"],
        "projects": [(p["name"], int(p["percent"])) for p in cfg["projects"]],
        "todos": [(t["text"], t.get("color", "#ffd84a")) for t in cfg.get("todos", [])][:3],
        "flap_words": cfg.get("flap_words", DEMO_DATA["flap_words"]),
        "scoreboard": (cfg["scoreboard"]["home"], cfg["scoreboard"]["home_score"],
                       cfg["scoreboard"]["away"], cfg["scoreboard"]["away_score"]),
    })
    cd = cfg.get("countdown") or {}
    data["countdown"] = (cd["label"].upper(), cd["date"]) if cd.get("label") and cd.get("date") else None
    data["weather"] = {"city": cfg["city"], "temp": DEMO_DATA["weather"]["temp"], "kind": DEMO_DATA["weather"]["kind"]}

    if live:
        token = os.environ.get("GITHUB_TOKEN", "")
        for name, fn in [("github", lambda: fetch_github(cfg["github_user"], token, today)),
                         ("weather", lambda: {"weather": fetch_weather(cfg)}),
                         ("visitors", lambda: {"visitors": fetch_visitors(cfg)})]:
            try:
                got = fn()
                data.update({k: v for k, v in got.items() if v is not None})
            except Exception as e:  # never break the image because one source failed
                print(f"warning: {name} fetch failed: {e}", file=sys.stderr)

    trophies = []
    for t in cfg.get("trophies", [])[:6]:
        won = bool(t.get("unlocked", False))
        if "auto_commits" in t:
            won = data["year_total"] >= int(t["auto_commits"])
        trophies.append((t["name"], won))
    data["trophies"] = trophies
    data["show_clock"] = cfg.get("show_clock", True)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="use demo data, no network")
    ap.add_argument("--date", help="override date YYYY-MM-DD (theme preview)")
    ap.add_argument("--hour", type=int, help="override hour 0-23")
    ap.add_argument("--out", default=str(ROOT / "workshop.svg"))
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "config.yml").read_text(encoding="utf-8"))
    now = datetime.now(ZoneInfo(cfg.get("timezone", "Europe/Helsinki")))
    if args.date:
        d = date.fromisoformat(args.date)
        now = now.replace(year=d.year, month=d.month, day=d.day)
    if args.hour is not None:
        now = now.replace(hour=args.hour)
    data = build_data(cfg, live=not args.offline, now=now)
    Path(args.out).write_text(render(data), encoding="utf-8")
    print(f"wrote {args.out}  ({data['date']} {data['hour']:02d}:00)")


if __name__ == "__main__":
    main()
