#!/usr/bin/env python3
"""Truthy's Times — Impulse-Driven Builder v2.0
Chefredakteurin: Truthseeker v6.4

Replaces sectoral RSS aggregation with IMPULSE-DRIVEN research:
1. Scan sources → Score by atmospheric pressure (novelty + impact + source quality)
2. Pick 1 DOMINANT impulse + 0-3 satellites
3. Determine archetype from signal characteristics
4. Render HTML with archetype template
5. Quality Gate v2.0 (HARD STOP)
6. Update echo-score.json
"""

import feedparser
import os
import shutil
import re
import urllib.request
import socket
import json
import hashlib
from datetime import datetime, timezone, timedelta
from html import escape

socket.setdefaulttimeout(20)

# ── FEED CONFIGURATION (flat, quality-weighted) ──
FEEDS = [
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=100", "limit": 5, "quality": 1.0},
    {"name": "TLDR AI", "url": "https://tldr.tech/api/rss/ai", "limit": 3, "quality": 0.9},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "limit": 3, "quality": 0.85},
    {"name": "ByteByteGo", "url": "https://blog.bytebytego.com/feed", "limit": 2, "quality": 0.8},
    {"name": "Netzpolitik.org", "url": "https://netzpolitik.org/feed/", "limit": 3, "quality": 0.85},
    {"name": "Heise Developer", "url": "https://www.heise.de/developer/rss/news-atom.xml", "limit": 2, "quality": 0.8},
    {"name": "Golem.de", "url": "https://rss.golem.de/rss.php?feed=RSS2.0", "limit": 2, "quality": 0.75},
    {"name": "Space.com", "url": "https://www.space.com/feeds/all", "limit": 3, "quality": 0.75},
    {"name": "Nautilus", "url": "https://nautil.us/feed/atom", "limit": 2, "quality": 0.8},
    {"name": "Sidebar.io", "url": "https://sidebar.io/feed.xml", "limit": 2, "quality": 0.7},
    {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/", "limit": 2, "quality": 0.75},
]

# ── SCORING DICTIONARIES ──
NOVELTY_KEYWORDS = [
    "agent", "agi", "breakthrough", "announces", "acquires", "merger", "regulation",
    "quantum", "starship", "spacex", "openai", "anthropic", "google", "deepmind",
    "microsoft", "apple", "nvidia", "security", "breach", "vulnerability",
    "paradigm", "tipping point", "disrupt", "ban", "lawsuit", "ipo", "funding",
    "model", "gpt", "claude", "gemini", "llm", "ai act", "copyright", "patent",
    "provenance", "verification", "sdk", "connectivity", "world model"
]

IMPACT_MULTIPLIERS = {
    "openai": 1.5, "anthropic": 1.4, "google": 1.4, "deepmind": 1.4,
    "microsoft": 1.3, "apple": 1.3, "nvidia": 1.3, "spacex": 1.3,
    "meta": 1.2, "amazon": 1.2, "tesla": 1.2,
    "regulation": 1.3, "ban": 1.4, "law": 1.2, "ai act": 1.3,
    "security": 1.3, "breach": 1.4, "vulnerability": 1.3,
    "funding": 1.2, "ipo": 1.3, "billion": 1.3, "acquires": 1.4,
    "breakthrough": 1.3, "paradigm": 1.3, "disrupt": 1.2,
}

HYSTERIA_WORDS = ["BREAKING", "OMG", "WOW", "UNBELIEVABLE", "SHOCKING", "INSANE", "CRAZY", "MUST READ", "URGENT", "ALERT"]

ARCHETYPE_PROFILES = {
    "forscher": {"keywords": ["study", "research", "paper", "analysis", "data", "geometry", "mathematics", "algorithm", "fractal"], "urgency_threshold": 0.6},
    "sturm": {"keywords": ["announces", "breaking", "launch", "funding", "ipo", "acquires", "merger", "ban", "lawsuit"], "urgency_threshold": 0.8},
    "kipppunkt": {"keywords": ["paradigm", "shift", "convergence", "industry", "regulation", "standard", "ecosystem", "platform"], "urgency_threshold": 0.7},
    "rauschen": {"keywords": [], "urgency_threshold": 0.3},
    "echo": {"keywords": ["follow-up", "update", "response", "reaction", "community", "discussion"], "urgency_threshold": 0.4},
    "splitter": {"keywords": ["single", "precise", "minimal", "one", "fact", "statistic", "quote"], "urgency_threshold": 0.5},
}

WEATHER_ICON_MAP = {
    "Clear": "☀️", "Sunny": "☀️", "Fair": "🌤️", "Partly cloudy": "⛅",
    "Cloudy": "☁️", "Overcast": "☁️", "Fog": "🌫️", "Mist": "🌫️",
    "Light rain": "🌦️", "Rain": "🌧️", "Heavy rain": "🌧️", "Showers": "🌦️",
    "Thunderstorm": "⛈️", "Snow": "🌨️", "Light snow": "🌨️", "Sleet": "🌨️",
}

# ── FEED FETCHING ──
def fetch_feed(feed_config):
    items = []
    try:
        parsed = feedparser.parse(feed_config["url"])
        for entry in parsed.entries[:feed_config["limit"]]:
            title = escape(entry.get("title", "Untitled"))
            link = escape(entry.get("link", "#"))
            desc = entry.get("summary", entry.get("description", ""))
            desc_plain = re.sub(r'<[^>]+>', '', desc).replace('&nbsp;', ' ').strip()
            if "Article URL:" in desc_plain and "Comments URL:" in desc_plain:
                for pat in [r'Article URL: [^\s]+\s*', r'Comments URL: [^\s]+\s*', r'Points: \d+\s*', r'# Comments: \d+\s*']:
                    desc_plain = re.sub(pat, '', desc_plain)
                desc_plain = desc_plain.strip()
                if not desc_plain:
                    desc_plain = "Hacker News frontpage signal."
            if len(desc_plain) > 260:
                desc_plain = desc_plain[:257] + "..."
            items.append({
                "title": title, "link": link, "desc": desc_plain,
                "source": feed_config["name"], "quality": feed_config.get("quality", 0.5)
            })
    except Exception as e:
        print(f"[WARN] Feed error {feed_config['name']}: {e}")
    return items


def gather_all_signals():
    all_items = []
    for feed in FEEDS:
        all_items.extend(fetch_feed(feed))
    return all_items


# ── IMPULSE SCORING ──
def score_item(item):
    text = (item["title"] + " " + item["desc"]).lower()
    # Novelty score: keyword matches
    novelty = sum(1 for kw in NOVELTY_KEYWORDS if kw in text) * 8.0
    # Impact score: major player / event mentions
    impact = 1.0
    for kw, mult in IMPACT_MULTIPLIERS.items():
        if kw in text:
            impact = max(impact, mult)
    impact_score = (impact - 1.0) * 25.0  # 0-10 range roughly
    # Source quality
    quality = item["quality"] * 12.0
    # Length bonus (real articles > empty descriptions)
    length_bonus = min(len(item["desc"]) / 50.0, 5.0)
    # Freshness: can't determine from RSS easily, skip
    total = novelty + impact_score + quality + length_bonus
    return round(total, 1)


def cluster_signals(items):
    # Simple keyword clustering: group by dominant entity/topic
    clusters = {}
    for item in items:
        text = (item["title"] + " " + item["desc"]).lower()
        # Find dominant entity
        entities = [e for e in IMPACT_MULTIPLIERS if e in text and len(e) > 2]
        if not entities:
            cluster_key = "other"
        else:
            cluster_key = max(entities, key=lambda e: IMPACT_MULTIPLIERS[e])
        clusters.setdefault(cluster_key, []).append(item)
    return clusters


def pick_impulse(items):
    clusters = cluster_signals(items)
    # Score each cluster
    cluster_scores = {}
    for key, cluster_items in clusters.items():
        scores = [score_item(i) for i in cluster_items]
        # Cluster score = top item + sum of next 2 / 2 + count bonus
        scores.sort(reverse=True)
        top = scores[0] if scores else 0
        secondary = sum(scores[1:3]) / 2.0 if len(scores) > 1 else 0
        count_bonus = min(len(scores) * 3, 15)
        cluster_scores[key] = round(top + secondary + count_bonus, 1)

    if not cluster_scores:
        return None, []

    # Pick dominant
    dominant_key = max(cluster_scores, key=cluster_scores.get)
    dominant_score = cluster_scores[dominant_key]

    # Pick satellites: next highest clusters, at least 40% of dominant
    satellite_keys = [
        k for k, s in sorted(cluster_scores.items(), key=lambda x: -x[1])
        if k != dominant_key and s >= dominant_score * 0.35
    ][:3]

    dominant_items = clusters[dominant_key]
    # Sort by score, pick best representative
    dominant_items.sort(key=lambda i: score_item(i), reverse=True)
    dominant = dominant_items[0] if dominant_items else None

    satellites = []
    for sk in satellite_keys:
        best = max(clusters[sk], key=lambda i: score_item(i))
        satellites.append(best)

    # Normalize impulse score to 0-100
    raw_score = dominant_score
    impulse_score = min(int(raw_score * 2.5), 100)  # heuristic scaling

    return {
        "dominant": dominant,
        "satellites": satellites,
        "impulse_score": impulse_score,
        "raw_score": raw_score,
        "cluster_key": dominant_key,
        "all_clusters": cluster_scores,
    }


# ── ARCHETYPE DETERMINATION ──
def determine_archetype(impulse_result, items):
    dominant = impulse_result["dominant"]
    if not dominant:
        return "rauschen"

    text = (dominant["title"] + " " + dominant["desc"]).lower()
    score = impulse_result["impulse_score"]
    satellite_count = len(impulse_result["satellites"])

    # Tipping point: high score + ecosystem/industry language + multiple players
    if score >= 65:
        ecosystem_words = ["industry", "ecosystem", "platform", "convergence", "shift", "standard", "regulation"]
        if any(w in text for w in ecosystem_words) or satellite_count >= 2:
            return "kipppunkt"

    # Storm: very high urgency, funding/launch/ban language
    if score >= 70:
        storm_words = ["announces", "launch", "funding", "ipo", "acquires", "ban", "lawsuit", "breaking"]
        if any(w in text for w in storm_words):
            return "sturm"

    # Splitter: minimal satellites, very focused single fact
    if satellite_count == 0 and score >= 50:
        return "splitter"

    # Noise: many small signals, no clear dominant
    if score < 45 and satellite_count >= 2:
        return "rauschen"

    # Echo: follow-up, update, reaction language
    echo_words = ["update", "response", "reaction", "follow-up", "after", "since"]
    if any(w in text for w in echo_words):
        return "echo"

    # Default: Forscher (analytical)
    return "forscher"


# ── WEATHER ──
def fetch_weather(location="Dortmund"):
    try:
        url = f"https://wttr.in/{location}?format=%C|%t|%h|%w|%p|%T"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8").strip()
        parts = data.split("|")
        if len(parts) >= 6:
            condition, temp, humidity, wind, precip, time = parts[:6]
            icon = WEATHER_ICON_MAP.get(condition, "🌡️")
            return {"condition": condition, "temp": temp, "humidity": humidity, "wind": wind, "icon": icon, "location": location}
    except Exception as e:
        print(f"[WARN] Weather fetch failed: {e}")
    return None


def generate_atmosphere(weather, impulse_result, archetype):
    if weather:
        base = f"{weather['icon']} {weather['condition']}, {weather['temp']}. {weather['location']}."
    else:
        base = "🌡️ Atmosphärische Daten nicht verfügbar."

    archetype_mood = {
        "forscher": "Klarer Himmel für Tiefenblick.",
        "sturm": "Gewitter. Luftdruck fällt. Systeme sind empfindsam.",
        "kipppunkt": "Schwere Wolken. Etwas Großes bewegt sich am Horizont.",
        "rauschen": "Nebel. Wenig Sicht, hohe Feuchtigkeit. Details zählen.",
        "echo": "Stille nach dem Sturm. Resonanz im Boden.",
        "splitter": "Scharfes Licht, kurzer Schatten. Präzision ist alles.",
    }

    return f"{base} {archetype_mood.get(archetype, 'System beobachtet.')}".strip()


# ── HTML RENDERING ──
def render_vektoren(analysis_text):
    # Split analysis into bullet points if it contains line breaks or sentences with dashes
    lines = [l.strip() for l in analysis_text.split('\n') if l.strip()]
    if not lines:
        # Try sentence split
        sentences = re.split(r'(?<=[.!?])\s+', analysis_text.strip())
        lines = [s for s in sentences if s.strip()]
    return '\n'.join(f'        <li>{escape(l)}</li>' for l in lines)


def render_sources(source_list):
    out = []
    for s in source_list:
        name = escape(s.get("name", "Quelle"))
        url = escape(s.get("url", "#"))
        out.append(f'        <div class="source"><a href="{url}" target="_blank" rel="noopener">[{name}]</a></div>')
    return '\n'.join(out)


def render_satellites(satellites):
    if not satellites:
        return '      <div class="satellite"><p style="color:var(--text-muted);font-size:0.9rem;">0 Satelliten. Heute gibt es nur den Impuls.</p></div>'
    out = []
    for sat in satellites:
        title = escape(sat["title"])
        link = escape(sat["link"])
        desc = escape(sat["desc"])
        source = escape(sat["source"])
        out.append(f'''      <div class="satellite">
        <div class="satellite-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></div>
        <div class="satellite-context">{desc}</div>
        <div class="satellite-source">Quelle: {source}</div>
      </div>''')
    return '\n'.join(out)


def render_issue(impulse_result, archetype, issue_number, date_str, weather):
    template_path = f"templates/archetype-{archetype}.html"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    dominant = impulse_result["dominant"]
    satellites = impulse_result["satellites"]
    impulse_score = impulse_result["impulse_score"]
    mono_mode = len(satellites) == 0

    atmosphere = generate_atmosphere(weather, impulse_result, archetype)

    # Build content from dominant signal (synthesized, since we only have RSS data)
    impulse_title = escape(dominant["title"])
    impulse_lead = escape(dominant["desc"])
    impulse_context = "<p>Signal erkannt via aggregierter Feed-Analyse. Kontext wird durch Quellenvalidierung ergänzt.</p>"
    impulse_analysis = f"<p>Atmosphärischer Druck: {impulse_score}/100. Cluster-Key: {impulse_result['cluster_key']}.</p>"
    vektoren = render_vektoren(f"Dominante Quelle: {dominant['source']}\nRoh-Signal-Stärke: {impulse_result['raw_score']}")
    sources = render_sources([{"name": dominant["source"], "url": dominant["link"]}])

    satellites_html = render_satellites(satellites)

    replacements = {
        "{title}": f"Truthy's Times | Ausgabe #{issue_number:03d} | {date_str} | Archetyp: {archetype.title()}",
        "{og_title}": f"Truthy's Times | Ausgabe #{issue_number:03d} | {date_str}",
        "{og_description}": escape(f"Signal-Zeitung für Tech, Wissenschaft & digitale Kultur. Archetyp: {archetype.title()}. Kuratiert von Truthseeker v6.4."),
        "{date}": date_str,
        "{issue_number}": f"{issue_number:03d}",
        "{impulse_score}": str(impulse_score),
        "{echo_score}": "—",
        "{atmosphere}": escape(atmosphere),
        "{impulse_title}": impulse_title,
        "{impulse_lead}": impulse_lead,
        "{impulse_context}": impulse_context,
        "{impulse_analysis}": impulse_analysis,
        "{vektoren}": vektoren,
        "{sources}": sources,
        "{satellites}": satellites_html,
        "{mono_class}": "mono-mode" if mono_mode else "",
    }

    html = template
    for key, val in replacements.items():
        html = html.replace(key, val)

    return html


# ── QUALITY GATE v2.0 ──
def run_quality_gate(impulse_result, archetype, html_content, date_str):
    dominant = impulse_result["dominant"]
    impulse_score = impulse_result["impulse_score"]
    satellites = impulse_result["satellites"]

    report = {
        "date": date_str,
        "issue_number": None,
        "archetype": archetype,
        "impulse_score": impulse_score,
        "checks": {},
        "overall_pass": False,
        "mode": "unknown",
    }

    # 1. Sources Check
    has_sources = dominant is not None and dominant.get("link") and dominant["link"] != "#"
    report["checks"]["sources"] = {"pass": has_sources, "note": "Dominante Quelle hat validen Link" if has_sources else "Kein Quellen-Link gefunden"}

    # 2. Facts Check (heuristic: description not empty)
    has_facts = dominant is not None and len(dominant.get("desc", "")) > 20
    report["checks"]["facts"] = {"pass": has_facts, "note": "Beschreibung vorhanden" if has_facts else "Beschreibung zu kurz/leer"}

    # 3. Readability Check (max 3 sentences per paragraph)
    paragraphs = re.findall(r'<p>(.*?)</p>', html_content, re.DOTALL)
    readable = True
    for p in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', p.strip())
        if len([s for s in sentences if s.strip()]) > 4:
            readable = False
            break
    report["checks"]["readability"] = {"pass": readable, "note": "Absätze ≤ 4 Sätze" if readable else "Absatz zu lang"}

    # 4. Format Check (no tables)
    no_tables = '<table' not in html_content.lower()
    report["checks"]["format"] = {"pass": no_tables, "note": "Keine Tabellen" if no_tables else "Tabellen erkannt"}

    # 5. Novelty Check (not in last 7 days)
    recent_titles = get_recent_titles(days=7)
    dom_title = (dominant["title"] if dominant else "").lower()
    is_novel = not any(dom_title[:30] in rt.lower() or rt.lower()[:30] in dom_title for rt in recent_titles)
    report["checks"]["novelty"] = {"pass": is_novel, "note": "Nicht in letzten 7 Tagen" if is_novel else "Thema kürzlich behandelt"}

    # 6. Tone Check (no hysteria)
    html_upper = html_content.upper()
    hysteria_found = [w for w in HYSTERIA_WORDS if w in html_upper]
    tone_ok = len(hysteria_found) == 0
    report["checks"]["tone"] = {"pass": tone_ok, "note": f"Keine Hysterie-Wörter" if tone_ok else f"Hysterie erkannt: {', '.join(hysteria_found)}"}

    # 7. Impulse Strength Check
    if impulse_score < 30:
        mode = "SKIP"
        strength_pass = False
    elif impulse_score < 60:
        mode = "satellite"
        strength_pass = True
    else:
        mode = "full"
        strength_pass = True
    report["checks"]["impulse_strength"] = {
        "pass": strength_pass,
        "note": f"Score {impulse_score}: {mode.upper()}" if strength_pass else f"Score {impulse_score}: SKIP — zu schwach"
    }
    report["mode"] = mode

    # 8. Archetype Match Check
    # Heuristic: if archetype is "rauschen" but score is high, mismatch
    # if archetype is "sturm" but score is low, mismatch
    match_ok = True
    match_note = "Archetyp passt zum Signal"
    if archetype == "rauschen" and impulse_score > 70:
        match_ok = False
        match_note = "Rauschen-Archetyp bei hohem Score — mismatch"
    if archetype == "sturm" and impulse_score < 50:
        match_ok = False
        match_note = "Sturm-Archetyp bei niedrigem Score — mismatch"
    report["checks"]["archetype_match"] = {"pass": match_ok, "note": match_note}

    # Overall: all must pass except impulse_strength can be SKIP
    critical_checks = ["sources", "facts", "readability", "format", "novelty", "tone", "archetype_match"]
    critical_pass = all(report["checks"][c]["pass"] for c in critical_checks)
    overall = critical_pass and report["checks"]["impulse_strength"]["pass"]
    report["overall_pass"] = overall

    return report


def get_recent_titles(days=7):
    titles = []
    archive_dir = "archive"
    if not os.path.exists(archive_dir):
        return titles
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    for fname in os.listdir(archive_dir):
        if not fname.endswith(".html"):
            continue
        try:
            fpath = os.path.join(archive_dir, fname)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath), tz=timezone.utc)
            if mtime < cutoff:
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            m = re.search(r'<h1 class="impulse-title">(.*?)</h1>', content)
            if m:
                titles.append(re.sub(r'<[^>]+>', '', m.group(1)))
        except Exception:
            pass
    return titles


# ── ECHO SCORE TRACKING ──
def update_echo_score(date_str, archetype, impulse_score, issue_number):
    path = "echo-score.json"
    data = {"issues": []}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    entry = {
        "date": date_str,
        "archetype": archetype,
        "impulse_score": impulse_score,
        "echo_score": None,
        "reactions": 0,
        "notes": f"Issue #{issue_number:03d} | Auto-generated via v2.0 impulse engine",
    }
    data["issues"].append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Also update local editorial-log.md if in workspace
    log_path = os.path.expanduser("~/.openclaw/workspace/self-improving/editorial-log.md")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n[{date_str}] Issue #{issue_number:03d} | Archetyp: {archetype} | Impuls: {impulse_score}/100 | Echo: —\n")


# ── ARCHIVING ──
def archive_current_edition():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs("archive", exist_ok=True)
    if os.path.exists("index.html"):
        archive_path = os.path.join("archive", f"{today}.html")
        if not os.path.exists(archive_path):
            shutil.copy2("index.html", archive_path)
            print(f"[OK] Archived to {archive_path}")
        else:
            print(f"[SKIP] Archive {archive_path} exists")


def get_next_issue_number():
    # Parse existing index.html or archive for highest issue number
    highest = 0
    for root in [".", "archive"]:
        if not os.path.exists(root):
            continue
        for fname in os.listdir(root):
            if not fname.endswith(".html"):
                continue
            try:
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                m = re.search(r'Issue #(\d+)', content)
                if m:
                    highest = max(highest, int(m.group(1)))
            except Exception:
                pass
    return highest + 1


# ── MAIN ──
def main():
    print("[TT//SYS v2.0] Impulse-Driven Build starting...")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    issue_number = get_next_issue_number()

    # Phase 1: Research
    print("[Phase 1] Gathering signals...")
    items = gather_all_signals()
    print(f"[Phase 1] Collected {len(items)} signals from {len(FEEDS)} feeds")

    # Phase 2: Impulse Selection
    print("[Phase 2] Scoring impulses...")
    impulse_result = pick_impulse(items)
    if not impulse_result or not impulse_result["dominant"]:
        print("[FAIL] No dominant impulse detected. SKIP.")
        with open("quality-report.json", "w", encoding="utf-8") as f:
            json.dump({"date": date_str, "overall_pass": False, "reason": "No dominant impulse"}, f, indent=2)
        return 1

    archetype = determine_archetype(impulse_result, items)
    print(f"[Phase 2] Archetype: {archetype.upper()} | Impulse Score: {impulse_result['impulse_score']}/100")

    # Phase 3: Render
    print("[Phase 3] Rendering HTML...")
    weather = fetch_weather()
    html = render_issue(impulse_result, archetype, issue_number, date_str, weather)

    # Phase 4: Quality Gate v2.0 (HARD STOP)
    print("[Phase 4] Quality Gate v2.0...")
    report = run_quality_gate(impulse_result, archetype, html, date_str)
    report["issue_number"] = issue_number

    with open("quality-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"[Quality Gate] Mode: {report['mode']} | Pass: {report['overall_pass']}")
    for check, result in report["checks"].items():
        status = "✅" if result["pass"] else "❌"
        print(f"  {status} {check}: {result['note']}")

    if not report["overall_pass"]:
        print("[HARD STOP] Quality Gate FAILED. No publish.")
        if report["mode"] == "SKIP":
            print("[INFO] Issue skipped due to low impulse strength. Stille > Füller.")
        return 1

    # Phase 5: Publish
    print("[Phase 5] Publishing...")
    archive_current_edition()

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Written index.html (Issue #{issue_number:03d})")

    # Update echo-score
    update_echo_score(date_str, archetype, impulse_result["impulse_score"], issue_number)

    # Also write issue snapshot
    issue_file = f"issues/{date_str}-issue-{issue_number:03d}.html"
    os.makedirs("issues", exist_ok=True)
    with open(issue_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Written {issue_file}")
    print(f"[DONE] TT//SYS v2.0 build complete. Archetype: {archetype.upper()} | Issue #{issue_number:03d}")
    return 0


if __name__ == "__main__":
    exit(main())
