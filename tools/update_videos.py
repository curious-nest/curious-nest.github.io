"""Refresh the video lists on index.html from the channel's public YouTube feed.

    python3 tools/update_videos.py

Reads https://www.youtube.com/feeds/videos.xml (the newest 15 public videos,
with view counts), keeps thumbnails on this site (img/videos/<id>.jpg, so
visitors' browsers never contact YouTube until they click), and rewrites the
cards between the <!-- videos:...:start/end --> markers. Run daily by
.github/workflows/update-videos.yml. Standard library only.
"""

import html
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL = "UCYclBr51SW5hWYQV5gqO5CA"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}
ROOT = Path(__file__).resolve().parents[1]
THUMBS = ROOT / "img" / "videos"
NEWEST, POPULAR = 6, 3


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "curious-nest-site"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def videos() -> list[dict]:
    out = []
    for e in ET.fromstring(fetch(FEED)).findall("a:entry", NS):
        if "/shorts/" in e.find("a:link", NS).get("href", ""):
            continue
        stats = e.find("media:group/media:community/media:statistics", NS)
        parts = [p.strip() for p in e.find("a:title", NS).text.split(" | ") if p.strip() != "Curious Nest"]
        out.append({
            "id": e.find("yt:videoId", NS).text,
            "title": parts[0],
            "sub": parts[1] if len(parts) > 1 else "",
            "published": e.find("a:published", NS).text,
            "views": int(stats.get("views", 0)) if stats is not None else 0,
        })
    return out


def thumbnail(vid: str) -> str:
    path = THUMBS / f"{vid}.jpg"
    if not path.exists():
        THUMBS.mkdir(parents=True, exist_ok=True)
        for name in ("hq720", "hqdefault"):
            try:
                path.write_bytes(fetch(f"https://i.ytimg.com/vi/{vid}/{name}.jpg"))
                break
            except OSError:
                continue
    return f"img/videos/{vid}.jpg"


def cards(vs: list[dict]) -> str:
    rows = []
    for v in vs:
        t, sub = html.escape(v["title"]), html.escape(v["sub"])
        rows.append(
            f'        <a class="video" href="https://youtu.be/{v["id"]}">\n'
            f'          <img src="{thumbnail(v["id"])}" alt="{t}" loading="lazy">\n'
            f'          <div><b>{t}</b><small>{sub}</small></div>\n'
            f'        </a>')
    return '      <div class="videos">\n' + "\n".join(rows) + "\n      </div>"


def put(page: str, name: str, block: str) -> str:
    start, end = f"<!-- videos:{name}:start -->", f"<!-- videos:{name}:end -->"
    a, b = page.index(start) + len(start), page.index(end)
    return page[:a] + "\n" + block + "\n      " + page[b:]


def main() -> None:
    vs = videos()
    newest = sorted(vs, key=lambda v: v["published"], reverse=True)[:NEWEST]
    shown = {v["id"] for v in newest}
    popular = sorted((v for v in vs if v["id"] not in shown), key=lambda v: v["views"], reverse=True)[:POPULAR]
    index = ROOT / "index.html"
    page = put(put(index.read_text(), "newest", cards(newest)), "popular", cards(popular))
    index.write_text(page)
    keep = {f"{v['id']}.jpg" for v in newest + popular}
    for f in THUMBS.glob("*.jpg"):
        if f.name not in keep:
            f.unlink()
    print(f"{len(newest)} newest, {len(popular)} most watched")


if __name__ == "__main__":
    main()
