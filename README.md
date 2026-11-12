# Seizure Watch

Free, no-API-key platform that reads open-source news every day, extracts illegal-seizure facts (drugs, precursors, CITES wildlife and timber, cultural heritage, arms, tobacco, stolen vehicles), scores risk indicators and publishes a dashboard, weekly bulletin and newsletter for law-enforcement analysts.

> Version 2. Same engine as version 1, rebuilt around a smaller repository, a faster site and one workflow.

**Live site:** https://glretief-ux.github.io/Seizure-watch-ver-2/

## The site

| Page | What it is |
|---|---|
| **Dashboard** | Filters, KPIs and six tabs: Overview (route map, alerts, trends), Leads (repeat links, production chain, watchlist, corridors), Analysis (concealment, cover load, what the data suggests), Events, News library, Method & coverage. |
| **Board** | Report-style view with country, route and commodity pages. |
| **Motion** | The last 30 days replayed day by day. |
| **Lite** | Light interactive map and charts read straight from `events.csv`. |
| **Bulletin / Newsletter** | One-page weekly bulletin and the illustrated weekly newsletter (PDF too). |
| **Reports** | Archive of earlier PDF reports. |

Byte, the help assistant, is on the dashboard (bottom right). It answers from the dashboard's own data and needs no server.

## Repository layout

```
.github/workflows/update.yml   the one workflow: collect > analyse > build > publish
config/config.yaml             searches, sources, risk points, thresholds (all tunable)
config/verifications.csv       optional analyst corrections (edit on GitHub)
swatch/                        the engine: collect, extract, analyse, report
web/                           site source: dashboard template, CSS, Board, Motion, Lite, shared top bar, vendored libraries
scripts/build_site.py          assembles site/ from web/ and the dashboard data
scripts/build_newsletter.py    weekly newsletter (HTML + PDF)
reports/                       archived PDF reports
templates/                     the open-source workbook template used for the Excel export
tests/                         135 tests
tools/byte/                    tools used to make the Byte mascot clip and widget
```

`site/` (the built website) and `data/` (the database) are not committed. The workflow publishes `site/` to GitHub Pages and keeps the database on a separate `data` branch that holds a single, overwritten commit. This keeps the repository small: version 1 grew to roughly 650 MB of history, mostly from committing the database every day.

## How it runs

Every day at 08:00 UTC (and on every push that changes site code) the **Update Seizure Watch** workflow:

1. restores the database from the `data` branch,
2. searches news (Google News editions, GDELT, official customs and police sites, RSS) in 20+ languages and reads the articles,
3. extracts facts, groups duplicate reports into one seizure, scores risk and builds alerts,
4. writes the dashboard, CSV, Excel and bulletin, builds the newsletter on Mondays,
5. saves the database and publishes the site.

Run it by hand under **Actions > Update Seizure Watch > Run workflow**. Use `days = 30` for the first run to back-fill.

### One-time setup
1. **Settings > Pages > Build and deployment > Source: GitHub Actions.**
2. Optional e-mail for the weekly bulletin: add secrets `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `BULLETIN_TO` (comma-separated), optionally `BULLETIN_FROM`.

## Run it yourself

```bash
pip install -r requirements.txt
python run.py --demo                 # offline demo with invented articles
python run.py --days 30              # real run with a 30-day back-fill
python run.py --reanalyse            # rebuild everything from the stored database
python scripts/build_site.py         # assemble site/ (open site/index.html through any static server)
python -m pytest tests
```

## Configure

Everything is in `config/config.yaml`: Google News editions and queries, GDELT queries, official sites, RSS feeds, risk points, caps and thresholds. The dashboard's "How risk is scored" box is generated from it, so it never drifts. The word lists for each language are in `swatch/lexicon.py` and `swatch/lang_more.py`. YAML reads a bare `no` as false, so Norwegian is written `"no"` (keep the quotes).

## What it flags

High-risk events (0-100 score from five capped dimensions: method, network, route, scale, commodity, so weight alone never decides), insider signals, new and surging corridors, repeat vessels and containers, precursor-to-drug production chains, and statistical spikes. Indicators are phrases in the article, never traits of a person or nationality; they justify a closer look and are not proof.

## Excel export

`seizure_watch.xlsx` opens on **Sheet1**, laid out like `templates/OPEN_source_template.xlsx` (38 columns, one row per seizure). Only facts the tool found are filled in. Replace the template to change the layout.

## Notes

- Only extracted facts and article links are stored, not article text.
- Extraction is rule-based. Treat output as leads to verify, not confirmed intelligence.
- Language coverage and blind spots are shown on the dashboard's Method & coverage tab.
- No third-party scripts are loaded except the optional GoatCounter view counter. Charts, maps and fonts are served from this site.
