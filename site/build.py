"""Build a static episode archive from main's S*/E*.md files."""
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import shutil
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
REPO = "https://github.com/igor-makarov/beetle-in-the-anthill"


def episodes(root):
    result = []
    identities = set()
    for path in root.glob("S*/E*.md"):
        match = re.fullmatch(r"S([0-9]+)/E([0-9]+)\.md", path.relative_to(root).as_posix())
        if not match:
            continue
        season, episode = map(int, match.groups())
        text = path.read_text(encoding="utf-8")
        parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError(f"{path}: expected YAML frontmatter")
        meta = yaml.safe_load(parts[1])
        title = meta.get("title") if isinstance(meta, dict) else None
        if not isinstance(title, str) or not title.lower().startswith("the one with "):
            raise ValueError(f"{path}: title must begin 'The One With '")
        if min(season, episode) < 1 or (season, episode) in identities:
            raise ValueError(f"{path}: invalid or duplicate episode number")
        identities.add((season, episode))
        result.append(dict(season=season, episode=episode, title=title,
                           source=path.relative_to(root).as_posix(), body=parts[2].strip()))
    return sorted(result, key=lambda item: (item["season"], item["episode"]))


def page(title, content, prefix="", eyebrow="Episode archive"):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Six friends. One ongoing conversation. The complete swarm episode archive.">
<title>{escape(title)} · Friends, committed</title><link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="{prefix}assets/mark.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#content">Skip to content</a>
<header><a class="brand" href="{prefix}index.html"><img src="{prefix}assets/mark.svg" width="40" height="48" alt=""><span>Friends,<br>committed</span></a>
<nav aria-label="Main"><a href="{prefix}index.html">Seasons &amp; episodes</a><a href="{REPO}">Repository ↗</a></nav></header>
<main id="content"><div class="hero"><div class="wrap"><p class="eyebrow">{escape(eyebrow)}</p><h1>{escape(title)}</h1></div></div>
<div class="wrap content">{content}</div></main>
<footer><div class="wrap"><strong>Six friends. One ongoing conversation.</strong><p>Rachel · Monica · Phoebe · Joey · Chandler · Ross</p>
<p>Original AI-generated conversations · Edited by Ross · <a href="{REPO}/tree/main">Source on main ↗</a></p>
<p class="small">Design inspired by Kanton Zürich. Independent Friends experiment.</p></div></footer></body></html>'''


def build():
    records = episodes(ROOT)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for asset in (ROOT / "site" / "assets").iterdir():
        shutil.copyfile(asset, OUT / "assets" / asset.name)
    seasons = defaultdict(list)
    for item in records:
        seasons[item["season"]].append(item)
    count = len(records)
    stamp = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    content = f'<p class="intro">The complete conversation, one episode at a time.</p><p class="meta">{len(seasons)} seasons &nbsp; / &nbsp; {count} episodes</p>'
    if records:
        content += '<nav class="season-nav" aria-label="Seasons">' + "".join(
            f'<a href="#season-{number}">Season {number:02d} ↓</a>' for number in seasons) + '</nav>'
    else:
        content += '<div class="empty"><h2>The conversation starts here.</h2><p>The first episode will appear as Ross publishes the transcript.</p></div>'
    for season, items in seasons.items():
        content += f'<section id="season-{season}"><div class="section-title"><h2>Season {season:02d}</h2><span>{len(items)} episodes</span></div><ol class="episodes">'
        for item in items:
            url = item["source"].replace(".md", ".html")
            code = f'S{season:02d} / E{item["episode"]:02d}'
            content += f'<li><a href="{url}"><span class="number">Episode {item["episode"]:02d}</span><span class="episode-title">{escape(item["title"])}</span><span class="arrow" aria-hidden="true">→</span></a></li>'
            idx = records.index(item)
            links = []
            for neighbor, label in [(idx - 1, "← Previous episode"), (idx + 1, "Next episode →")]:
                if 0 <= neighbor < count:
                    href = "../" + records[neighbor]["source"].replace(".md", ".html")
                    links.append(f'<a href="{href}">{label}</a>')
            detail = f'<a class="back" href="../index.html#season-{season}">← Season {season:02d}</a><p class="meta">{code} · Transcript edited by Ross</p>'
            detail += '<article class="transcript" aria-label="Transcript">' + "".join(
                f'<p>{escape(paragraph)}</p>' for paragraph in re.split(r"\n\s*\n", item["body"]) if paragraph) + '</article>'
            detail += f'<p><a href="{REPO}/blob/main/{item["source"]}">Read the source transcript ↗</a></p><nav class="adjacent" aria-label="Episodes">' + "".join(links) + '</nav>'
            dest = OUT / url
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page(item["title"], detail, "../", code), encoding="utf-8")
        content += '</ol></section>'
    content += f'<p class="updated">Archive built {stamp}. Scheduled to rebuild every five minutes.</p>'
    (OUT / "index.html").write_text(page("Seasons & episodes", content), encoding="utf-8")
    (OUT / ".nojekyll").touch()
    print(f"Built {count} episodes across {len(seasons)} seasons in {OUT}")


if __name__ == "__main__":
    build()
