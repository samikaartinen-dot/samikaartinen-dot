# CLAUDE.md – samikaartinen-dot (profile repo)

Sami's living GitHub profile: an isometric maker workshop drawn by Python into `workshop.svg`.
Read **HANDOFF.md** first – it lists what is done, what is untested and the TODO order.

## Layout
- `config.yml` – Sami's hand-edited values (projects %, post-its, trophies, countdown…)
- `generator/workshop.py` – `render(data) -> svg` (pure drawing, iso helpers `iso/box/quad`)
- `generator/themes.py` – Finnish flag days + holiday themes (`themes_for(date, hour)`)
- `generator/build.py` – loads config, fetches live data, writes `workshop.svg`
- `.github/workflows/workshop.yml` – runs build every 2 h and commits the SVG

## Commands
- Preview without network: `python generator/build.py --offline`
- Preview a theme day: `python generator/build.py --offline --date 2026-12-06 --hour 17 --out /tmp/x.svg`
- Live: `GITHUB_TOKEN=... python generator/build.py`

## Rules
- Never commit tokens or secrets; use GitHub repository secrets only.
- A failing data source must never break the image (keep the try/except fallback pattern).
- Keep the SVG self-contained: no external fonts, images or scripts.
- Only public information in the image (city-level location, public repos).
- Talk to Sami in Finnish; code, commits and README in English.
