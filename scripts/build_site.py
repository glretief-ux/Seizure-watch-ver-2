#!/usr/bin/env python3
"""Assemble the website in site/ after `python run.py` has written the dashboard, data.js, events.csv and bulletin.

  python scripts/build_site.py

Copies the static pages and shared assets from web/ and builds the data files of the Board and Motion pages
from the dashboard data. Nothing in site/ is committed: the workflow publishes it to GitHub Pages.
"""
import datetime as dt
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB, SITE = os.path.join(ROOT, "web"), os.path.join(ROOT, "site")


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def copytree(src, dst):
    shutil.copytree(src, dst, dirs_exist_ok=True)


def load_dashboard_data():
    s = open(os.path.join(SITE, "data.js"), encoding="utf-8").read()
    i = s.rindex(",geo:")
    return json.loads(s[len("window.__SW={data:"):i]), json.loads(s[i + 5:-2])


def build_board(D, geo):
    ev = []
    for e in D["events"]:
        ev.append({"i": e["id"], "d": e["date"], "it": e.get("drug_label") or e["drug"], "ca": e.get("category") or "Drug",
                   "c": e.get("country"), "p": e.get("place"), "o": e.get("origin"), "de": e.get("dest"), "t": e.get("transit"),
                   "co": e.get("conceal"), "tr": e.get("transport") if e.get("transport") != "Unknown" else None,
                   "kg": e.get("kg"), "u": e.get("units"), "ut": e.get("unit_type"), "n": e.get("n"),
                   "ti": (e.get("title_en") or e.get("title") or "")[:170], "ur": e.get("url"), "ou": (e.get("outlets") or "")[:60],
                   "ar": e.get("arrests")})
    out = {"asof": D["meta"]["asof"], "generated": D["meta"]["generated"], "first": D["meta"]["first_date"],
           "geo": dict(geo["c"]), "events": ev}
    dst = os.path.join(SITE, "board")
    copytree(os.path.join(WEB, "board"), dst)
    with open(os.path.join(dst, "data.js"), "w", encoding="utf-8") as f:
        f.write("window.OSD=" + json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=lambda x: None) + ";")
    return out


def build_motion(B):
    end = dt.date.fromisoformat(B["asof"][:10])
    days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]
    idx = {d: i for i, d in enumerate(days)}
    ev = []
    for e in B["events"]:
        i = idx.get((e.get("d") or "")[:10])
        if i is not None:
            ev.append([i, e["it"], e.get("c"), round(e["kg"], 1) if e.get("kg") else 0, e.get("ca") or "Drug"])
    ev.sort(key=lambda r: r[0])
    used = {r[2] for r in ev if r[2]}
    out = {"asof": B["asof"], "days": days, "geo": {k: v for k, v in B["geo"].items() if k in used}, "ev": ev}
    dst = os.path.join(SITE, "motion")
    copytree(os.path.join(WEB, "motion"), dst)
    with open(os.path.join(dst, "data.js"), "w", encoding="utf-8") as f:
        f.write("window.MOT=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";")


def build_reports_index():
    """reports/ holds the archived PDF reports; publish them with a simple index page."""
    src, dst = os.path.join(ROOT, "reports"), os.path.join(SITE, "reports")
    if not os.path.isdir(src):
        return
    copytree(src, dst)
    titles = {"weekly-bulletin": "Weekly bulletins", "weekly-routes": "Weekly route reports", "daily": "Daily bulletins"}
    body = ""
    for folder in ("weekly-bulletin", "weekly-routes", "daily"):
        d = os.path.join(dst, folder)
        if not os.path.isdir(d):
            continue
        files = sorted((f for f in os.listdir(d) if f.endswith(".pdf")), reverse=True)
        body += f"<section class='card'><h2>{titles[folder]}<span class='small'>{len(files)} PDF</span></h2><ul class='files'>"
        for f in files:
            label = f.replace("seizure-watch-", "").replace(".pdf", "")
            body += f"<li><a href='{html.escape(folder)}/{html.escape(f)}'>{html.escape(label)}</a></li>"
        body += "</ul></section>"
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seizure Watch - Reports</title><link rel="stylesheet" href="../shared/theme.css"><link rel="stylesheet" href="../dashboard.css"></head>
<body><script src="../shared/topbar.js" data-active="reports"></script>
<div class="wrap"><div class="hero"><div><h1>Reports</h1><div class="sub">Archive of the PDF reports. The current newsletter is under Newsletter.</div></div></div>
<div class="grid2">{body}</div></div>
</body></html>"""
    page = page.replace("</head>", "<style>.files{list-style:none;margin:0;padding:0;columns:2}.files li{padding:4px 0}.files a{text-decoration:none;color:var(--brand-2)}</style></head>")
    with open(os.path.join(dst, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


def add_topbar(name, active):
    """Give the generated bulletin / newsletter the same top bar (it hides itself when printing)."""
    import re
    p = os.path.join(SITE, name)
    if not os.path.exists(p):
        return
    h = open(p, encoding="utf-8").read()
    if "topbar.js" in h:
        return
    h = h.replace("</head>", '<link rel="stylesheet" href="shared/theme.css">\n</head>', 1)
    h = re.sub(r"(<body[^>]*>)", r'\1\n<script src="shared/topbar.js" data-active="%s"></script>' % active, h, count=1)
    open(p, "w", encoding="utf-8").write(h)


def main():
    os.makedirs(SITE, exist_ok=True)
    copytree(os.path.join(WEB, "shared"), os.path.join(SITE, "shared"))
    copy(os.path.join(WEB, "dashboard.css"), os.path.join(SITE, "dashboard.css"))
    copytree(os.path.join(WEB, "assets"), os.path.join(SITE, "assets"))
    copytree(os.path.join(WEB, "vendor"), os.path.join(SITE, "vendor"))
    copytree(os.path.join(WEB, "lite"), os.path.join(SITE, "lite"))
    copy(os.path.join(ROOT, "assets", "pccp", "pccp-logo-banner.jpg"), os.path.join(SITE, "assets", "pccp-logo-banner.jpg"))
    D, geo = load_dashboard_data()
    B = build_board(D, geo)
    build_motion(B)
    build_reports_index()
    add_topbar("bulletin.html", "bulletin")
    add_topbar("newsletter.html", "newsletter")
    open(os.path.join(SITE, ".nojekyll"), "w").close()
    print("site/ ready:", sum(len(f) for _, _, f in os.walk(SITE)), "files")


if __name__ == "__main__":
    main()
