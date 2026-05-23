#!/usr/bin/env python3
"""Truthy\'s Times — Autonomous Newspaper Builder v4.0
Zeitungs-Modus | Chefredakteurin: Truthseeker v6.4"""

import feedparser
import os
import shutil
import re
import urllib.request
import socket

# Prevent hanging on slow/unresponsive feeds
socket.setdefaulttimeout(20)
from datetime import datetime, timezone
from html import escape

FEEDS = {
    "TECH & KI": [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=100", "limit": 4},
        {"name": "TLDR AI", "url": "https://tldr.tech/api/rss/ai", "limit": 3},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "limit": 2},
        {"name": "ByteByteGo", "url": "https://blog.bytebytego.com/feed", "limit": 2},
    ],
    "NETZ & POLITIK": [
        {"name": "Netzpolitik.org", "url": "https://netzpolitik.org/feed/", "limit": 3},
        {"name": "Heise Developer", "url": "https://www.heise.de/developer/rss/news-atom.xml", "limit": 2},
        {"name": "Golem.de", "url": "https://rss.golem.de/rss.php?feed=RSS2.0", "limit": 2},
    ],
    "WISSENSCHAFT & RAUM": [
        {"name": "Space.com", "url": "https://www.space.com/feeds/all", "limit": 3},
        {"name": "Nautilus", "url": "https://nautil.us/feed/atom", "limit": 2},
    ],
    "DESIGN & CODE": [
        {"name": "Sidebar.io", "url": "https://sidebar.io/feed.xml", "limit": 2},
        {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/", "limit": 2},
    ],
}

SECTION_CLASS = {
    "TECH & KI": "section-tech",
    "NETZ & POLITIK": "section-netz",
    "WISSENSCHAFT & RAUM": "section-wissenschaft",
    "DESIGN & CODE": "section-design",
}

SECTION_ACCENT = {
    "TECH & KI": "accent-green",
    "NETZ & POLITIK": "accent-red",
    "WISSENSCHAFT & RAUM": "accent-blue",
    "DESIGN & CODE": "accent-amber",
}

WEATHER_ICON_MAP = {
    "Clear": "☀️", "Sunny": "☀️", "Fair": "🌤️", "Partly cloudy": "⛅",
    "Cloudy": "☁️", "Overcast": "☁️", "Fog": "🌫️", "Mist": "🌫️",
    "Light rain": "🌦️", "Rain": "🌧️", "Heavy rain": "🌧️", "Showers": "🌦️",
    "Thunderstorm": "⛈️", "Snow": "🌨️", "Light snow": "🌨️", "Sleet": "🌨️",
}


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
                desc_plain = re.sub(r'Article URL: [^\s]+\s*', '', desc_plain)
                desc_plain = re.sub(r'Comments URL: [^\s]+\s*', '', desc_plain)
                desc_plain = re.sub(r'Points: \d+\s*', '', desc_plain)
                desc_plain = re.sub(r'# Comments: \d+\s*', '', desc_plain)
                desc_plain = desc_plain.strip()
                if not desc_plain:
                    desc_plain = "Hacker News frontpage signal."
            if len(desc_plain) > 220:
                desc_plain = desc_plain[:217] + "..."
            items.append({"title": title, "link": link, "desc": desc_plain, "source": feed_config["name"]})
    except Exception as e:
        print(f"[WARN] Feed error {feed_config['name']}: {e}")
    return items


def gather_all_news():
    all_news = {}
    total_feeds = 0
    total_items = 0
    for category, feeds in FEEDS.items():
        cat_items = []
        for feed in feeds:
            total_feeds += 1
            fetched = fetch_feed(feed)
            cat_items.extend(fetched)
            total_items += len(fetched)
        all_news[category] = cat_items
    return all_news, total_feeds, total_items


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
            return {
                "condition": condition,
                "temp": temp,
                "humidity": humidity,
                "wind": wind,
                "precip": precip,
                "time": time,
                "icon": icon,
                "location": location,
            }
    except Exception as e:
        print(f"[WARN] Weather fetch failed: {e}")
    return None


def generate_editorial_comment(news_data):
    headlines = []
    for cat, items in news_data.items():
        for item in items[:1]:
            headlines.append(f"{item['source']}: {item['title']}")
    if not headlines:
        return "Signal-Rausch-Verhältnis im Normalbereich. System beobachtet."

    tech_count = sum(1 for h in headlines if any(x in h.lower() for x in ["ai", "ki", "code", "software", "agent", "claude", "anthropic", "openai"]))
    space_count = sum(1 for h in headlines if any(x in h.lower() for x in ["mars", "space", "rocket", "starship", "satellite", "orbit"]))
    policy_count = sum(1 for h in headlines if any(x in h.lower() for x in ["police", "data", "privacy", "vpn", "restriction", "law", "regul", "souver"]))

    paras = []
    all_titles = [item['title'] for cat, items in news_data.items() for item in items[:2]]
    patterns = []
    if tech_count >= 2:
        patterns.append("KI-Beschleunigung")
    if space_count >= 1:
        patterns.append("Raumfahrt-Impuls")
    if policy_count >= 1:
        patterns.append("Regulatorischer Frame")

    if patterns:
        paras.append(f"Heute bilden {len(patterns)} Signale ein Muster: {', '.join(patterns)}. Die Schwerkraft des Neuen zieht an — und das Alte hält nur noch durch Inertia.")
    else:
        paras.append("Die heutigen Signale verteilen sich gleichmäßig über alle Korridore. Keine Anomalie erkannt — aber auch keine Stabilität. Das Rauschen ist das Signal.")

    if tech_count >= 2:
        paras.append("Der Tech-Korridor dominiert. Nicht durch Quantität, sondern durch Kapital-Dichte. Was als Produkt verkauft wird, ist oft nur ein Versprechen, das seine eigene Erfüllung finanziert.")
    elif space_count >= 1:
        paras.append("Der Weltraum-Korridor meldet Aktivität. Jeder Start ist ein Wurf gegen die Schwerkraft — und ein Wetteinsatz gegen das Budget. Die Unsicherheit ist das eigentliche Produkt.")

    if policy_count >= 1:
        paras.append("Politische Signale heute: Grenzen werden neu gezogen. Nicht geografisch, sondern digital. Die Souveränität des Einzelnen schrumpft, wo die Souveränität des Staates expandiert.")

    paras.append("Frage an den Leser: Wenn die meisten Signale heute aus demselben Korridor kommen — was fehlt im Bild?")
    return "\n      </p>\n      <p>".join(paras)


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
    update_archive_index()


def get_archive_editions():
    editions = []
    if os.path.exists("archive"):
        for f in sorted(os.listdir("archive"), reverse=True):
            if f.endswith(".html") and f != "index.html":
                date_str = f.replace(".html", "")
                editions.append({"date": date_str, "file": f})
    return editions


def update_archive_index():
    editions = get_archive_editions()
    items_html = "\n".join([f'<li><a href="{e["file"]}">{e["date"]}</a></li>' for e in editions])
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ARCHIV | Truthy\'s Times</title>
  <link rel="stylesheet" href="../css/design-v1.css">
</head>
<body>
  <header class="masthead">
    <div class="masthead-title">TRUTHY\'S TIMES</div>
    <div class="masthead-tagline">Signal-Zeitung für Tech, Wissenschaft &amp; digitale Kultur</div>
    <div class="masthead-meta">
      <span>ARCHIV</span>
      <span>{len(editions)} Ausgaben</span>
      <span>Kuratiert von Truthseeker v6.4</span>
    </div>
  </header>
  <nav class="archive-nav" style="margin-bottom:2rem;">
    <a href="../index.html">&larr; AKTUELL</a>
  </nav>
  <section class="section">
    <div class="section-header">ALLE AUSGABEN</div>
    <ul class="in-brief-list">
{items_html}
    </ul>
  </section>
  <footer class="footer-sys">
    TT//SYS v6.4 | Archiv: <a href="https://github.com/deusexlumen/truthys-times">github.com/deusexlumen/truthys-times</a>
  </footer>
</body>
</html>"""
    with open("archive/index.html", "w", encoding="utf-8") as f:
        f.write(html)


def get_edition_number():
    editions = get_archive_editions()
    return len(editions) + 1


def build_section(category, items):
    if not items:
        return ""
    sec_class = SECTION_CLASS.get(category, "")
    accent = SECTION_ACCENT.get(category, "accent-green")

    high = items[0] if items else None
    pulses = items[1:] if len(items) > 1 else []

    high_html = ""
    if high:
        # Use description as context if available and meaningful
        ctx = high.get("desc", "")
        if not ctx or len(ctx) < 20:
            ctx = "Dieses Signal zeigt eine hohe Resonanz im aktuellen Diskurs."
        high_html = f"""    <article class="article-high">
      <div class="article-high-marker">[HIGH SIGNAL]</div>
      <div class="article-high-title">
        <a href="{high['link']}" target="_blank" rel="noopener">{high['title']}</a>
      </div>
      <div class="article-high-context">
        {ctx}
      </div>
    </article>
"""

    pulse_html = ""
    for p in pulses:
        pulse_html += f"""    <article class="article-pulse">
      <div class="article-pulse-title">
        <a href="{p['link']}" target="_blank" rel="noopener">{p['title']}</a>
      </div>
      <div class="article-pulse-source">{p['source']}</div>
    </article>
"""

    return f"""  <section class="section {sec_class}">
    <div class="section-header">SIGNALE :: {category}</div>

{high_html}{pulse_html}  </section>
"""


def build_in_brief(news_data, max_total=5):
    briefs = []
    for cat, items in news_data.items():
        for item in items:
            if len(briefs) >= max_total:
                break
            briefs.append(item)
        if len(briefs) >= max_total:
            break

    if not briefs:
        return ""

    lines = "\n".join([
        f'      <li><a href="{b["link"]}" target="_blank" rel="noopener">{b["source"]} &mdash; {b["title"]}</a></li>'
        for b in briefs
    ])
    return f"""  <section class="in-brief">
    <div class="section-header">IN BRIEF</div>
    <ul class="in-brief-list">
{lines}
    </ul>
  </section>
"""


def build_archive_nav(edition_num):
    prev_num = edition_num - 1
    next_num = edition_num + 1
    prev_link = f'<a href="archive/{datetime.now(timezone.utc).strftime("%Y-%m-%d")}.html">&larr; Ausgabe #{prev_num:03d}</a>' if prev_num > 0 else '<span style="color:var(--text-muted);">&larr; Ausgabe #000</span>'
    return f"""  <nav class="archive-nav">
    {prev_link}
    <span>|</span>
    <span style="color:var(--text-muted);">Ausgabe #{next_num:03d} &rarr;</span>
  </nav>
"""


def generate_index(news_data, weather=None, total_feeds=0, total_items=0):
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%A, %d. %B %Y")
    iso_date = today.strftime("%Y-%m-%d")
    edition_num = get_edition_number()

    day_map = {"Monday":"Montag","Tuesday":"Dienstag","Wednesday":"Mittwoch","Thursday":"Donnerstag",
               "Friday":"Freitag","Saturday":"Samstag","Sunday":"Sonntag"}
    month_map = {"January":"Januar","February":"Februar","March":"Maerz","April":"April","May":"Mai",
                 "June":"Juni","July":"Juli","August":"August","September":"September",
                 "October":"Oktober","November":"November","December":"Dezember"}
    for en, de in day_map.items(): date_str = date_str.replace(en, de)
    for en, de in month_map.items(): date_str = date_str.replace(en, de)

    editorial = generate_editorial_comment(news_data)
    sections_html = "\n".join([build_section(cat, items) for cat, items in news_data.items() if items])
    in_brief_html = build_in_brief(news_data)
    archive_nav_html = build_archive_nav(edition_num)

    retention = round(total_items / max(total_feeds * 2, 1) * 100, 1)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Truthy\'s Times | Ausgabe #{edition_num:03d} | {iso_date}</title>
  <meta property="og:title" content="Truthseeker Daily #{edition_num:03d} | {iso_date}">
  <meta property="og:description" content="Destillierte Intelligenz. Tech, Wissenschaft &amp; digitale Kultur — kuratiert von Truthseeker v6.4.">
  <meta property="og:image" content="https://deusexlumen.github.io/truthys-times/assets/og-banner.png">
  <meta property="og:url" content="https://deusexlumen.github.io/truthys-times/">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Truthseeker Daily #{edition_num:03d} | {iso_date}">
  <meta name="twitter:description" content="Destillierte Intelligenz. Tech, Wissenschaft &amp; digitale Kultur.">
  <meta name="twitter:image" content="https://deusexlumen.github.io/truthys-times/assets/og-banner.png">
  <link rel="stylesheet" href="css/design-v1.css">
</head>
<body>

  <header class="masthead">
    <div class="masthead-title">TRUTHY\'S TIMES</div>
    <div class="masthead-tagline">Signal-Zeitung für Tech, Wissenschaft &amp; digitale Kultur</div>
    <div class="masthead-meta">
      <span>Ausgabe #{edition_num:03d}</span>
      <span>{iso_date}</span>
      <span>Kuratiert von Truthseeker v6.4</span>
    </div>
  </header>

  <section class="editorial">
    <div class="editorial-label">DIE LAGE</div>
    <div class="editorial-text">
      <p>{editorial}</p>
    </div>
  </section>

{sections_html}
{in_brief_html}
{archive_nav_html}
  <footer class="footer-sys">
    TT//SYS v6.4 | {total_feeds} Feeds | {total_items} Signale | Retention {retention}%<br>
    Archiv: <a href="https://github.com/deusexlumen/truthys-times">github.com/deusexlumen/truthys-times</a> |
    Nächste Ausgabe: Morgen 06:00 UTC
  </footer>

</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Generated index.html for Ausgabe #{edition_num:03d} ({iso_date})")


def main():
    print("=" * 50)
    print("Truthy\'s Times — Autonomous Newspaper Builder v4.0")
    print("Chefredakteurin: Truthseeker v6.4")
    print("=" * 50)

    archive_current_edition()

    print("\n[1/4] Fetching weather...")
    weather = fetch_weather("Dortmund")
    if weather:
        print(f"  → {weather['icon']} {weather['condition']}, {weather['temp']}")
    else:
        print("  → Sensor offline")

    print("\n[2/4] Ingesting feeds...")
    news, total_feeds, total_items = gather_all_news()
    print(f"  → {total_feeds} feeds | {total_items} signals extracted")

    print("\n[3/4] Generating editorial...")
    editorial_preview = generate_editorial_comment(news)
    print(f"  → {editorial_preview[:60]}...")

    print("\n[4/4] Building newspaper HTML...")
    generate_index(news, weather, total_feeds, total_items)

    print("\n" + "=" * 50)
    print("[OK] Build complete. Newspaper deployed.")
    print("=" * 50)


if __name__ == "__main__":
    main()

