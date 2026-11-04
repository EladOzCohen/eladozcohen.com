"""Stage 2: collapse the raw HN harvest into one row per video with "how strongly and how
repeatedly did HN recommend it" signals.  data/hn_*.jsonl -> data/candidates.json
"""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import re

DATA = Path(__file__).parent / "data"
REC = re.compile(
    r"\b(recommend\w*|must[- ]watch|worth (?:a )?(?:watch|your time|the time)|excellent|fantastic|brilliant|"
    r"superb|gem|masterpiece|best (?:\w+ ){0,3}(?:explanation|lecture|talk|video|intro\w*|course)|"
    r"great (?:\w+ ){0,2}(?:explanation|lecture|talk|video|intro\w*|course|series|channel)|"
    r"good (?:explanation|lecture|talk|video|intro\w*)|explains? (?:it )?(?:really |very )?well|"
    r"changed (?:my|the way)|eye[- ]opening|mind[- ]blowing|watch this)\b", re.I)

vids = defaultdict(lambda: dict(n=0, authors=set(), stories=set(), years=set(), rec=0, titles=defaultdict(int),
                                snippets=[], sub_pts=0, sub_title=None, sub_comments=0, sub_id=None, sid_count=defaultdict(int), sid_title={}))


def year(t):
    return datetime.fromtimestamp(t, timezone.utc).year


for line in open(DATA / "hn_comments.jsonl", encoding="utf-8"):
    c = json.loads(line)
    isrec = bool(REC.search(c["x"]))
    for v in c["v"]:
        d = vids[v]
        d["n"] += 1
        d["authors"].add(c["a"])
        d["stories"].add(c["sid"])
        d["years"].add(year(c["t"]))
        d["rec"] += isrec
        if c["st"]:
            d["titles"][c["st"]] += 1
            d["sid_count"][c["sid"]] += 1
            d["sid_title"][c["sid"]] = c["st"]
        if isrec and len(d["snippets"]) < 3 and len(c["x"]) < 400:
            d["snippets"].append(c["x"])

for line in open(DATA / "hn_stories.jsonl", encoding="utf-8"):
    s = json.loads(line)
    d = vids[s["v"][0]]
    d["years"].add(year(s["t"]))
    if (s["p"] or 0) > d["sub_pts"]:
        d["sub_pts"], d["sub_title"], d["sub_comments"], d["sub_id"] = s["p"] or 0, s["title"], s["n"] or 0, s["id"]

rows = []
for v, d in vids.items():
    rows.append(dict(
        v=v, n=d["n"], au=len(d["authors"]), ns=len(d["stories"]),
        y0=min(d["years"]), y1=max(d["years"]), rec=d["rec"],
        pts=d["sub_pts"], sub=d["sub_title"], subc=d["sub_comments"],
        ctx=[t for t, _ in sorted(d["titles"].items(), key=lambda kv: -kv[1])[:4]],
        snip=d["snippets"],
        th=d["sub_id"] if d["sub_pts"] >= 100 else (max(d["sid_count"], key=d["sid_count"].get) if d["sid_count"] else d["sub_id"]),
        tt=d["sub_title"] if d["sub_pts"] >= 100 else (d["sid_title"].get(max(d["sid_count"], key=d["sid_count"].get)) if d["sid_count"] else d["sub_title"])))

keep = [r for r in rows if r["au"] >= 2 or r["pts"] >= 100]
have = {r["v"] for r in keep}
cur = json.load(open(Path(__file__).parent / "curation.json", encoding="utf-8"))
for v in cur.get("extra_ids", []):  # hand-picked videos the HN signal never surfaced
    if v not in have:
        keep.append(dict(v=v, n=0, au=0, ns=0, y0=2026, y1=2026, rec=0, pts=0, sub=None, subc=0, ctx=[], snip=[], th=None, tt=None, mine=True))
keep.sort(key=lambda r: (-r["au"], -r["pts"]))
json.dump(keep, open(DATA / "candidates.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"{len(rows)} distinct videos linked on HN; {len(keep)} candidates (>=2 distinct recommenders or >=100pt submission)")
for lo in (2, 3, 5, 10):
    print(f"  >= {lo} distinct authors:", sum(r["au"] >= lo for r in rows))
