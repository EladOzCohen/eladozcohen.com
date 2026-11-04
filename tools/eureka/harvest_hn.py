"""Stage 1: harvest every YouTube link ever posted on Hacker News (comments + submissions).

Uses the public Algolia HN API (no key). Algolia returns at most 1000 hits per query, so the
time range is split recursively until each window fits.

    python harvest_hn.py comments   -> data/hn_comments.jsonl
    python harvest_hn.py stories    -> data/hn_stories.jsonl
"""
import html
import json
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)

API = "https://hn.algolia.com/api/v1/search_by_date?"
START = 1167609600  # 2007-01-01
END = int(time.time())
VID = re.compile(
    r"(?:youtube(?:-nocookie)?\.com/(?:watch\?[^\"'\s<>]*?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
TAG = re.compile(r"<[^>]+>")
lock = threading.Lock()


def fetch(params, tries=6):
    url = API + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # network hiccup / 429
            time.sleep(2 + 3 * i)
    raise RuntimeError(f"giving up on {url}")


def windows(lo, hi, base, handle):
    """Fetch (lo, hi]; split in half while the window is saturated."""
    r = fetch({**base, "hitsPerPage": 1000,
               "numericFilters": base.get("numericFilters", "") + f"created_at_i>{lo},created_at_i<={hi}"})
    if r["nbHits"] > 950 and hi - lo > 120:
        mid = (lo + hi) // 2
        return windows(lo, mid, base, handle) + windows(mid, hi, base, handle)
    handle(r["hits"])
    return [r["nbHits"]]


def run(mode):
    if mode == "comments":
        out = DATA / "hn_comments.jsonl"
        bases = [dict(tags="comment", advancedSyntax="true", restrictSearchableAttributes="comment_text", query=q)
                 for q in ('"youtube.com/watch"', '"youtu.be"', '"youtube.com/embed"')]

        def keep(h):
            text = html.unescape(h.get("comment_text") or "")
            vids = list(dict.fromkeys(VID.findall(text)))
            if not vids:
                return None
            plain = html.unescape(TAG.sub(" ", text))
            plain = re.sub(r"https?://\S+", "<link>", plain)
            return {"id": h["objectID"], "t": h["created_at_i"], "a": h.get("author"),
                    "sid": h.get("story_id"), "st": h.get("story_title"), "v": vids,
                    "x": re.sub(r"\s+", " ", plain).strip()[:600]}
    else:
        out = DATA / "hn_stories.jsonl"
        bases = [dict(tags="story", advancedSyntax="true", restrictSearchableAttributes="url",
                      numericFilters="points>=15,", query=q)
                 for q in ('"youtube.com/watch"', '"youtu.be"')]

        def keep(h):
            vids = VID.findall(h.get("url") or "")
            if not vids:
                return None
            return {"id": h["objectID"], "t": h["created_at_i"], "v": vids[:1], "title": h.get("title"),
                    "p": h.get("points"), "n": h.get("num_comments")}

    seen = set()
    f = open(out, "w", encoding="utf-8")

    def handle(hits):
        with lock:
            for h in hits:
                if h["objectID"] in seen:
                    continue
                seen.add(h["objectID"])
                row = keep(h)
                if row:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()

    # seed windows: one per quarter, run in parallel
    step = 90 * 86400
    seeds = [(a, min(a + step, END)) for a in range(START, END, step)]
    for base in bases:
        with ThreadPoolExecutor(6) as ex:
            list(ex.map(lambda w: windows(w[0], w[1], base, handle), seeds))
        print(mode, base["query"], "done; unique so far", len(seen), flush=True)
    f.close()
    print("DONE", mode, len(seen), flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
