"""Build a static episode archive from main's S*/E*.md files."""
from collections import defaultdict
from html import escape
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
REPO = "https://github.com/igor-makarov/beetle-in-the-anthill"
FRIENDS = ("Rachel", "Monica", "Phoebe", "Joey", "Chandler", "Ross")


def cast_key():
    return '<ul class="cast-key" aria-label="The six friends">' + "".join(
        f'<li class="voice-{name.lower()}"><span class="cast-dot" aria-hidden="true"></span>{name}</li>'
        for name in FRIENDS) + '</ul>'


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
        summary = meta.get("summary") or ""
        if not isinstance(summary, str):
            raise ValueError(f"{path}: summary must be text")
        identities.add((season, episode))
        result.append(dict(season=season, episode=episode, title=title,
                           summary=' '.join(summary.split()),
                           source=path.relative_to(root).as_posix(), body=parts[2].strip()))
    return sorted(result, key=lambda item: (item["season"], item["episode"]))


def page(title, content, prefix="", eyebrow="Episode archive", *, document_title=None):
    home = prefix or './'
    document_title = document_title or f"{title} | Friends, Committed"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Six friends. One ongoing story. An archive of original conversations.">
<title>{escape(document_title)}</title><link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="{prefix}assets/favicon-six-dots.svg" type="image/svg+xml" sizes="any"><script src="{prefix}assets/clean-url.js" defer></script></head>
<body><a class="skip" href="#content">Skip to content</a>
<header class="masthead"><a class="brand" href="{home}"><img src="{prefix}assets/mark.svg" width="48" height="32" alt=""><span>Friends, committed<span class="brand-period">.</span></span></a>
<nav aria-label="Main"><a href="{home}">The archive</a><a href="{REPO}">About</a></nav></header>
<main id="content"><div class="hero wrap"><p class="eyebrow">{escape(eyebrow)}</p><h1>{escape(title)}</h1><p class="hero-deck">Six friends. One ongoing story.</p></div>
<div class="wrap content">{content}</div></main>
<footer><div class="wrap footer-inner"><p class="footer-brand">Good company. More to come.</p><p>Original, AI-generated conversations.<br>Edited by Ross. <a href="{REPO}">About the experiment</a></p></div></footer></body></html>'''


def transcript(body):
    """Keep source metadata in links and group the spoken text into distinct turns."""
    turns = []
    current = None
    for paragraph in re.split(r"\n\s*\n", body):
        if not paragraph:
            continue
        speaker = re.fullmatch(r"\*\*(\w+)\*\*(?: \([^\n]+\))?", paragraph)
        if speaker and speaker[1] in FRIENDS:
            current = {"name": speaker[1], "sha": None, "paragraphs": []}
            turns.append(current)
            continue
        source = re.fullmatch(r"Source: friend/[\w-]+ @ ([0-9a-f]{40})", paragraph)
        if source and current is not None and not current["paragraphs"]:
            current["sha"] = source[1]
            continue
        if current is None:
            current = {"name": None, "sha": None, "paragraphs": []}
            turns.append(current)
        current["paragraphs"].append(paragraph)

    rendered = []
    for turn in turns:
        name, sha = turn["name"], turn["sha"]
        paragraphs = turn["paragraphs"].copy()
        if name and paragraphs:
            # The speaker is already named in the margin; display their dialogue once.
            paragraphs[0] = re.sub(rf"^{re.escape(name)}:[ \t]*", "", paragraphs[0], count=1)
        dialogue = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in paragraphs)
        if not name:
            rendered.append(f'<div class="transcript-note">{dialogue}</div>')
            continue
        source_link = (f'<a class="source-link" href="{REPO}/commit/{sha}" '
                       f'aria-label="Source for this line by {name}">Source</a>') if sha else ''
        rendered.append(f'<section class="turn voice-{name.lower()}" aria-label="{name}">'
                        f'<div class="turn-heading"><h2><span class="cast-dot" aria-hidden="true"></span>{name}</h2>'
                        f'{source_link}</div><div class="dialogue">{dialogue}</div></section>')
    return '<article class="transcript" aria-label="Episode transcript">' + ''.join(rendered) + '</article>'


def build():
    records = episodes(ROOT)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for asset in (ROOT / "site" / "assets").iterdir():
        shutil.copyfile(asset, OUT / "assets" / asset.name)
    # Use the page logo as the source of truth, centered on a square favicon canvas.
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace('', namespace)
    logo = ET.parse(ROOT / "site" / "assets" / "mark.svg").getroot()
    x, y, width, height = map(float, logo.attrib['viewBox'].split())
    side = max(width, height)
    icon = ET.Element(f'{{{namespace}}}svg', {'viewBox': f'0 0 {side:g} {side:g}'})
    dots = ET.SubElement(icon, f'{{{namespace}}}g', {
        'transform': f'translate({(side-width)/2-x:g} {(side-height)/2-y:g})'})
    dots.extend(logo)
    ET.ElementTree(icon).write(OUT / "assets" / "favicon-six-dots.svg", encoding='utf-8')
    seasons = defaultdict(list)
    for item in records:
        seasons[item["season"]].append(item)
    count = len(records)
    season_label = 'season' if len(seasons) == 1 else 'seasons'
    episode_label = 'episode' if count == 1 else 'episodes'
    content = f'<div class="archive-intro"><p class="intro">A little drama. A lot of conversation.<br>Pick an episode and pull up a chair.</p><p class="archive-count">{len(seasons):02d} {season_label}<span aria-hidden="true"> / </span>{count:02d} {episode_label}</p></div>'
    content += cast_key()
    if records:
        content += '<nav class="season-nav" aria-label="Seasons">' + "".join(
            f'<a href="#season-{number}">Season {number:02d}</a>' for number in seasons) + '</nav>'
    else:
        content += '<div class="empty"><h2>The conversation starts here.</h2><p>The first episode will appear as Ross publishes the transcript.</p></div>'
    for season, items in seasons.items():
        content += f'<section class="season" id="season-{season}"><div class="section-title"><h2>Season {season:02d}</h2><span>{len(items):02d} {"episode" if len(items) == 1 else "episodes"}</span></div><ol class="episodes">'
        for item in items:
            url = item["source"].replace(".md", ".html")
            code = f'Season {season:02d} / Episode {item["episode"]:02d}'
            summary = f'<span class="episode-summary">{escape(item["summary"])}</span>' if item['summary'] else ''
            content += f'<li><a href="{url}"><span class="number">Episode {item["episode"]:02d}</span><span class="episode-copy"><span class="episode-title">{escape(item["title"])}</span>{summary}</span></a></li>'
            idx = records.index(item)
            links = []
            for neighbor, label in [(idx - 1, "Previous episode"), (idx + 1, "Next episode")]:
                if 0 <= neighbor < count:
                    href = "../" + records[neighbor]["source"].replace(".md", ".html")
                    links.append(f'<a href="{href}">{label}</a>')
            detail = f'<div class="reading-toolbar"><a class="back" href="../#season-{season}">All episodes</a><a class="manuscript-link" href="{REPO}/blob/main/{item["source"]}">Original transcript</a></div>'
            detail += cast_key() + transcript(item["body"])
            if links:
                detail += '<nav class="adjacent" aria-label="Episodes">' + ''.join(links) + '</nav>'
            dest = OUT / url
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page(item["title"], detail, "../", code), encoding="utf-8")
        content += '</ol></section>'
    content += '<p class="updated"><span class="live-dot" aria-hidden="true"></span>The story continues.</p>'
    (OUT / "index.html").write_text(page("Seasons & episodes", content, document_title="Friends, Committed"), encoding="utf-8")
    (OUT / ".nojekyll").touch()
    print(f"Built {count} episodes across {len(seasons)} seasons in {OUT}")


if __name__ == "__main__":
    build()
