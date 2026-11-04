"""Stage 3a: cheap first pass - title + channel via YouTube oEmbed (no key, light endpoint).
HTTP 401 means the owner disabled embedding, 404 means deleted/private.  Resumable.

    python oembed.py data/candidates_t1.json    -> data/oembed.jsonl
"""
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DATA = Path(__file__).parent / "data"
lock = threading.Lock()


def one(v):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v}&format=json"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                j = json.load(r)
            return {"v": v, "code": 200, "title": j.get("title"), "ch": j.get("author_name"), "chu": j.get("author_url")}
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404):
                return {"v": v, "code": e.code}
            time.sleep(10 * (attempt + 1))
        except Exception:
            time.sleep(3 + attempt * 3)
    return {"v": v, "code": 0}


def main():
    src = Path(sys.argv[1])
    ids = [r["v"] for r in json.load(open(src, encoding="utf-8"))]
    out = DATA / "oembed.jsonl"
    done = {json.loads(l)["v"] for l in open(out, encoding="utf-8")} if out.exists() else set()
    todo = [v for v in ids if v not in done]
    print(len(todo), "to fetch", flush=True)
    f = open(out, "a", encoding="utf-8")
    n = 0

    def work(v):
        nonlocal n
        r = one(v)
        with lock:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
            if n % 500 == 0:
                f.flush()
                print(n, "/", len(todo), flush=True)

    with ThreadPoolExecutor(6) as ex:
        list(ex.map(work, todo))
    f.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
