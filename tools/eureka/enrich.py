"""Stage 3b: attach YouTube metadata (title, channel, length, views, date, description, embeddable?)
to every shortlisted video.  Resumable; strongest HN recommendations first.

Two modes:
  * default - read the public watch page, slowly and politely (no key; YouTube rate-limits fast crawlers)
  * YT_API_KEY=... set in the environment - use the official YouTube Data API v3 (50 videos per call, instant)

    python enrich.py data/shortlist.json [--limit N]    -> data/meta.jsonl
"""
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DATA = Path(__file__).parent / "data"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
       "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
MARK = "ytInitialPlayerResponse = "
lock = threading.Lock()
cool_until = 0.0
dec = json.JSONDecoder()


def player_response(v):
    req = urllib.request.Request(f"https://www.youtube.com/watch?v={v}", headers=HDR)
    buf = ""
    with urllib.request.urlopen(req, timeout=40) as r:
        while True:
            chunk = r.read(131072)
            if not chunk:
                break
            buf += chunk.decode("utf-8", "replace")
            i = buf.find(MARK)
            if i >= 0:
                try:
                    return dec.raw_decode(buf[i + len(MARK):])[0]
                except ValueError:
                    pass  # not fully read yet
    return None


def from_page(v):
    global cool_until
    for attempt in range(30):
        wait = cool_until - time.time()
        if wait > 0:
            time.sleep(wait)
        try:
            pr = player_response(v)
            break
        except Exception as e:
            if "429" in str(e):
                cool_until = max(cool_until, time.time() + 120)
                print("429 - cooling down 2 min", flush=True)
            else:
                time.sleep(2 + attempt)
    else:
        return None  # leave unwritten so a later run retries
    if not pr:
        return {"v": v, "status": "NOPAGE"}
    ps = pr.get("playabilityStatus", {})
    vd = pr.get("videoDetails", {})
    mf = pr.get("microformat", {}).get("playerMicroformatRenderer", {})
    time.sleep(1.2)
    return {
        "v": v, "status": ps.get("status"), "embed": bool(ps.get("playableInEmbed", True)),
        "title": vd.get("title"), "ch": vd.get("author"), "chid": vd.get("channelId"),
        "len": int(vd.get("lengthSeconds") or 0), "views": int(vd.get("viewCount") or 0),
        "date": (mf.get("publishDate") or "")[:10], "cat": mf.get("category"),
        "live": bool(vd.get("isLiveContent")), "desc": (vd.get("shortDescription") or "")[:700],
    }


ISO = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
CATS = {"1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music", "15": "Pets & Animals", "17": "Sports", "19": "Travel & Events",
        "20": "Gaming", "22": "People & Blogs", "23": "Comedy", "24": "Entertainment", "25": "News & Politics", "26": "Howto & Style",
        "27": "Education", "28": "Science & Technology", "29": "Nonprofits & Activism"}


def from_api(ids, key):
    url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(
        {"part": "snippet,contentDetails,statistics,status", "id": ",".join(ids), "key": key, "maxResults": 50})
    with urllib.request.urlopen(url, timeout=40) as r:
        items = {i["id"]: i for i in json.load(r)["items"]}
    out = []
    for v in ids:
        i = items.get(v)
        if not i:
            out.append({"v": v, "status": "GONE"}); continue
        h, m, s = (int(x or 0) for x in ISO.match(i["contentDetails"]["duration"]).groups())
        sn = i["snippet"]
        out.append({"v": v, "status": "OK", "embed": bool(i["status"].get("embeddable")), "title": sn["title"], "ch": sn["channelTitle"],
                    "chid": sn["channelId"], "len": h * 3600 + m * 60 + s, "views": int(i["statistics"].get("viewCount", 0)),
                    "date": sn["publishedAt"][:10], "cat": CATS.get(sn.get("categoryId")), "live": sn.get("liveBroadcastContent") != "none",
                    "desc": sn.get("description", "")[:700]})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = Path(args[0]) if args else DATA / "shortlist.json"
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    rows = json.load(open(src, encoding="utf-8"))
    rows.sort(key=lambda r: (-r["au"], -r["pts"]))
    ids = [r["v"] for r in rows]
    out = DATA / "meta.jsonl"
    done = set()
    if out.exists():
        done = {json.loads(l)["v"] for l in open(out, encoding="utf-8") if l.strip()}
    todo = [v for v in ids if v not in done][:limit]
    print(f"{len(todo)} to fetch ({len(done)} cached)", flush=True)
    f = open(out, "a", encoding="utf-8")
    key = os.environ.get("YT_API_KEY")
    if key:
        for i in range(0, len(todo), 50):
            for m in from_api(todo[i:i + 50], key):
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
            f.flush()
            print(min(i + 50, len(todo)), "/", len(todo), flush=True)
        print("DONE", flush=True)
        return
    n = 0

    def work(v):
        nonlocal n
        m = from_page(v)
        if m is None:
            return
        with lock:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            if n % 50 == 0:
                print(n, "/", len(todo), flush=True)

    with ThreadPoolExecutor(2) as ex:
        list(ex.map(work, todo))
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
