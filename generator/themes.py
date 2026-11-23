"""Finnish calendar logic for the workshop: flag days and theme days."""
from datetime import date, timedelta

INDEPENDENCE_YEAR = 1917


def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, month, day)


def nth_weekday(y, month, weekday, n):
    """n-th given weekday (Mon=0..Sun=6) of a month."""
    d = date(y, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def last_weekday(y, month, weekday):
    d = date(y, month + 1, 1) - timedelta(days=1) if month < 12 else date(y, 12, 31)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def midsummer_day(y):
    """Saturday between 20 and 26 June."""
    d = date(y, 6, 20)
    return d + timedelta(days=(5 - d.weekday()) % 7)


def flag_days(y):
    """Official + customary flag days (Ministry of the Interior list)."""
    return {
        date(y, 2, 5): "Runebergin päivä",
        date(y, 2, 28): "Kalevalan päivä",
        date(y, 3, 19): "Minna Canthin päivä",
        date(y, 4, 9): "Suomen kielen päivä",
        date(y, 4, 27): "Veteraanipäivä",
        date(y, 5, 1): "Vappu",
        date(y, 5, 9): "Eurooppa-päivä",
        nth_weekday(y, 5, 6, 2): "Äitienpäivä",
        date(y, 5, 12): "Suomalaisuuden päivä",
        nth_weekday(y, 5, 6, 3): "Kaatuneitten muistopäivä",
        date(y, 6, 4): "Puolustusvoimain lippujuhla",
        midsummer_day(y): "Juhannus · Suomen lipun päivä",
        date(y, 7, 6): "Eino Leinon päivä",
        last_weekday(y, 8, 5): "Suomen luonnon päivä",
        date(y, 10, 1): "Miina Sillanpään päivä",
        date(y, 10, 10): "Aleksis Kiven päivä",
        date(y, 10, 24): "YK:n päivä",
        date(y, 11, 6): "Svenska dagen",
        nth_weekday(y, 11, 6, 2): "Isänpäivä",
        date(y, 11, 20): "Lapsen oikeuksien päivä",
        date(y, 12, 6): "Itsenäisyyspäivä",
        date(y, 12, 8): "Sibeliuksen päivä",
    }


def themes_for(d, hour):
    """Return a dict describing everything special about this day."""
    t = {"flag": None, "tags": set(), "flap": None, "hat": None, "stool": None, "monitor": None, "hud": None}
    y = d.year
    fd = flag_days(y)
    ms = midsummer_day(y)
    if d in fd:
        t["flag"] = fd[d]
    if d == ms - timedelta(days=1) and hour >= 18:      # flag goes up on Midsummer Eve 18:00
        t["flag"] = fd[ms]

    # --- Christmas season
    if d.month == 12:
        t["tags"].add("xmas_lights")
        t["hat"] = "santa"
        t["stool"] = "gingerbread"
    if (d.month == 12 and d.day >= 13) or (d.month == 1 and d.day <= 6):
        t["tags"].add("xmas_tree")
    if d.month == 12 and 24 <= d.day <= 26:
        t["tags"].add("presents")
        t["flap"] = ("HYVÄÄ", ["JOULUA", "GOD JUL", "SAMI"])

    # --- Independence Day
    if (d.month, d.day) == (12, 6):
        age = y - INDEPENDENCE_YEAR
        t["tags"] |= {"candles"}
        t["stool"] = ("cake", age)
        t["flap"] = ("ONNEA", ["SUOMI", f"{age} V", "SAMI"])
        t["hud"] = f"Suomi {age} v"

    # --- New Year (Dec 31 – Jan 1)
    if (d.month, d.day) in ((12, 31), (1, 1)):
        ny = y + 1 if d.month == 12 else y
        t["tags"].add("fireworks")
        t["hat"] = "party"
        t["stool"] = "tin"
        t["monitor"] = "tina: laiva=matka"
        t["flap"] = ("HYVÄÄ", ["UUTTA", "VUOTTA", str(ny)])

    # --- Runeberg
    if (d.month, d.day) == (2, 5):
        t["stool"] = "torte"

    # --- Easter: Palm Sunday .. Easter Monday
    e = easter(y)
    if e - timedelta(days=7) <= d <= e + timedelta(days=1):
        t["tags"].add("easter")
        t["hat"] = "witch"
        t["stool"] = "willow"
        t["flap"] = ("VIRVON", ["VARVON", "TUOREEKS", "TERVEEKS"])

    # --- Vappu (Apr 30 – May 1)
    if (d.month, d.day) in ((4, 30), (5, 1)):
        t["tags"] |= {"balloons", "streamers"}
        t["hat"] = "cap"
        t["stool"] = "champagne"
        t["flap"] = ("HAUSKAA", ["VAPPUA", "SKÅL!", "SAMI"])

    # --- Midsummer (eve + day)
    if d in (ms - timedelta(days=1), ms):
        t["tags"] |= {"birch", "bonfire", "mosquito"}
        t["hat"] = "flowers"
        t["stool"] = "sausage"
        t["flap"] = ("HYVÄÄ", ["JUSSIA!", "JUHANNUS", "SAMI"])
    return t
