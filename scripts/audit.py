#!/usr/bin/env python3
"""Data-quality audit: finds places where one seizure may be counted as several, or a country looks wrong.
Usage: python scripts/audit.py [path/to/seizure_watch.db]"""
import re, sqlite3, sys, collections
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
from swatch import extract
from swatch import lexicon as L

db = sys.argv[1] if len(sys.argv) > 1 else "data/seizure_watch.db"
c = sqlite3.connect(db)
print("== 1. Headline names a different seizure country than the one stored")
bad = 0
for i, t, cur in c.execute("SELECT id, title, seizure_country FROM articles WHERE relevant=1 AND title IS NOT NULL"):
    a = extract._title_anchor(L.norm(t))
    if a and a[0] != cur:
        bad += 1
        if bad <= 8: print("  ", cur, "!=", a[0], "|", t[:90])
print("   total:", bad)
print("== 2. Vessels / containers with several events less than 14 days apart")
rows = c.execute("SELECT vessel, COUNT(DISTINCT event_id), MIN(COALESCE(published,fetched)), MAX(COALESCE(published,fetched)) "
                 "FROM articles WHERE relevant=1 AND vessel IS NOT NULL AND vessel<>'' GROUP BY vessel HAVING COUNT(DISTINCT event_id)>1").fetchall()
close = [r for r in rows if r[3][:10] and r[2][:10] and (__import__("datetime").date.fromisoformat(r[3][:10]) - __import__("datetime").date.fromisoformat(r[2][:10])).days <= 14]
print("   vessels with >1 event:", len(rows), "| all within 14 days:", len(close))
for r in close[:8]: print("  ", r)
print("== 3. Suspicious vessel names (one common word, or very short)")
names = collections.Counter(r[0] for r in c.execute("SELECT vessel FROM articles WHERE relevant=1 AND vessel<>'' AND vessel IS NOT NULL"))
sus = [(n, k) for n, k in names.items() if len(n) < 4 or n.lower() in {"brought", "shingle", "examination compound", "show", "the", "vessel", "ship"}]
print("  ", sus[:15])
print("== 4. Events whose articles disagree on country")
q = c.execute("SELECT event_id, COUNT(DISTINCT seizure_country) FROM articles WHERE relevant=1 AND event_id IS NOT NULL AND seizure_country IS NOT NULL GROUP BY event_id HAVING COUNT(DISTINCT seizure_country)>1").fetchall()
print("   events with mixed countries:", len(q))
