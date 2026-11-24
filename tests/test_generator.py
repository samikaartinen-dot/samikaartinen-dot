"""Run: python -m pytest -q"""
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "generator"))

import yaml  # noqa: E402

import build  # noqa: E402
from themes import easter, flag_days, midsummer_day, themes_for  # noqa: E402
import workshop  # noqa: E402
from workshop import render  # noqa: E402


# ---------------------------------------------------------------- calendar
def test_easter_known_years():
    assert easter(2026) == date(2026, 4, 5)
    assert easter(2027) == date(2027, 3, 28)
    assert easter(2028) == date(2028, 4, 16)


def test_midsummer_is_saturday_20_to_26_june():
    for y in range(2024, 2035):
        d = midsummer_day(y)
        assert d.weekday() == 5 and 20 <= d.day <= 26 and d.month == 6


def test_mothers_and_fathers_day():
    fd = flag_days(2027)
    assert fd[date(2027, 5, 9)] in ("Äitienpäivä", "Eurooppa-päivä")   # both fall on 9.5.2027
    assert fd[date(2027, 11, 14)] == "Isänpäivä"


def test_independence_day_age():
    t = themes_for(date(2026, 12, 6), 12)
    assert t["flag"] == "Itsenäisyyspäivä"
    assert t["stool"] == ("cake", 109)
    assert "candles" in t["tags"]


def test_midsummer_eve_flag_from_18():
    eve = midsummer_day(2027).replace(day=midsummer_day(2027).day - 1)
    assert themes_for(eve, 17)["flag"] is None
    assert "Juhannus" in themes_for(eve, 18)["flag"]


def test_ordinary_day_has_no_theme():
    t = themes_for(date(2027, 3, 3), 12)
    assert t["flag"] is None and not t["tags"] and t["flap"] is None


# ---------------------------------------------------------------- build
def cfg():
    return yaml.safe_load((ROOT / "config.yml").read_text(encoding="utf-8"))


def test_offline_build_renders_valid_svg():
    data = build.build_data(cfg(), live=False, now=datetime(2026, 12, 24, 16))
    svg = render(data)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert "<script" not in svg            # image must stay script-free
    assert "JOULUKUU" in svg               # calendar page (split-flap letters are drawn one by one)


def test_config_languages_used_offline():
    data = build.build_data(cfg(), live=False, now=datetime(2026, 11, 24, 12))
    assert data["languages"][0][0] == "PY"
    assert data["lang_source"] == "my stack"


def test_visitor_counter_subtracts_own_fetches(monkeypatch):
    monkeypatch.setattr(build, "fetch_visitors", lambda c: 10)
    state = {"own_counter_fetches": 3}
    assert build.real_visitors({}, state) == 6     # 10 - (3 + this fetch)
    assert state["own_counter_fetches"] == 4


def test_trophy_auto_unlock():
    c = cfg()
    data = build.build_data(c, live=False, now=datetime(2026, 11, 24, 12))
    names = dict(data["trophies"])
    assert names["100 commits"] == (data["year_total"] >= 100)


def test_empty_languages_never_crash():
    data = build.build_data(cfg(), live=False, now=datetime(2026, 11, 24, 12))
    data["languages"] = []
    assert render(data).startswith("<svg")


def test_fetch_github_without_public_languages_keeps_config(monkeypatch):
    fake = {"data": {"user": {
        "contributionsCollection": {"contributionCalendar": {"weeks": [
            {"contributionDays": [{"date": "2026-11-24", "contributionCount": 3}]}]}},
        "repositories": {"nodes": [{"name": "samikaartinen-dot", "defaultBranchRef": None,
                                    "languages": {"edges": []}}]}}}}
    monkeypatch.setattr(build, "http_json", lambda *a, **k: fake)
    got = build.fetch_github("samikaartinen-dot", "x", date(2026, 11, 24))
    assert "languages" not in got and got["today_commits"] == 3


def test_hedgehog_routes_loop_back_home():
    for name in workshop.ROUTES:
        moves, _ = workshop.hedgehog_timeline(name)
        pts = moves["pos"].split('"')[1].split(";")
        assert pts[0] == pts[-1], name                      # seamless loop
        kts = [float(k) for k in moves["pos"].split('"')[3].split(";")]
        assert kts[0] == 0 and abs(kts[-1] - 1) < 1e-3 and kts == sorted(kts), name


def test_route_changes_with_build_and_skips_busy_stool():
    d = date(2026, 11, 24)
    picks = {workshop.pick_route(d, h) for h in range(0, 24, 2)}
    assert len(picks) >= 3                                   # not the same walk all day
    assert workshop.pick_route(d, 10) == workshop.pick_route(d, 10)   # stable within one build
    assert all(workshop.pick_route(d, h, stool_free=False) != "stool" for h in range(24))


def test_only_peek_route_uses_crate_clip(monkeypatch):
    for name in workshop.ROUTES:
        monkeypatch.setattr(workshop, "pick_route", lambda *a, _n=name, **k: _n)
        svg = workshop.render(dict(workshop.DEMO_DATA))
        assert f'data-route="{name}"' in svg
        assert ('clip-path="url(#cratehide)"' in svg) == (name == "peek")


def test_clock_shows_update_time():
    svg = render(dict(workshop.DEMO_DATA, hour=16, minute=37))
    assert "updated 16:37" in svg
    assert "updated" not in render(dict(workshop.DEMO_DATA, show_clock=False)).split("Helsinki")[1][:80]
