# Eureka data pipeline

Builds `static/eureka/videos.json`, the library behind **eladozcohen.com/eureka/**.
The site itself is plain HTML/CSS/JS in `static/eureka/` (no build step); Hugo copies it as-is.

Python 3, standard library only. Run from this folder. Raw data goes to `data/` (git-ignored, ~300 MB).

| Stage | Command | What it does |
|---|---|---|
| 1 | `python harvest_hn.py comments` / `python harvest_hn.py stories` | Every HN comment and submission that links to a YouTube video, via the public Algolia HN API (time windows split adaptively because the API caps at 1000 hits) |
| 2 | `python aggregate.py` | One row per video: distinct recommenders, years, praise comments, thread. Writes `data/candidates.json` |
| 3a | `python oembed.py data/candidates_t1.json` | Title and channel via YouTube oEmbed (also flags deleted / non-embeddable videos) |
| 3b | `python curate.py --shortlist` | Cheap topic + channel filter on title/channel only, writes `data/shortlist.json` |
| 3c | `python enrich.py data/shortlist.json` | Length, views, date, description. Reads watch pages slowly (YouTube 429s fast crawlers). **Faster:** `set YT_API_KEY=...` first and it uses the official Data API, 50 videos per call |
| 4 | `python curate.py` | Final filter, topic / depth / format labels, score. Writes `static/eureka/videos.json` |

`curate.py --report` dumps `data/report.json` (kept + dropped, with reasons) for reviewing the filter.

## Taste lives in `curation.json`

* `block_channels` / `allow_channels`: prefix match on channel name (`=Name` for exact match). Allowed channels bypass the topic and length filters.
* `channel_topic`, `channel_default`, `channel_depth`: hand labels. Depth 1 = Spark (pop-sci, hidden by default), 2 = Explainer, 3 = Deep dive, 4 = Lecture / primary source.
* `block_ids`, `allow_ids`, `topic_override`, `depth_override`: per-video fixes.

To add a video the HN signal missed, put its id in `extra_ids`, then re-run `aggregate.py`, `oembed.py data/candidates.json`,
`curate.py --shortlist`, `enrich.py` and `curate.py`. Hand-picked videos skip the topic filter and rank high.

## Score

`sc` (0..1) = 50% log(distinct HN recommenders) + 14% years the video kept being recommended + 10% comments that explicitly praise it
+ 8% best submission points + 4% depth. The front end adds a locally computed taste profile on top (see `foryou()` in `app.js`).
