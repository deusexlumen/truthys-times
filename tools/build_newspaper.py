#!/usr/bin/env python3
"""TT//SYS — Autonomous Signal Processing System
Truthys Times Daily Builder v3.0 — System Interface Mode"""

import feedparser
import os
import shutil
import re
import urllib.request
from datetime import datetime, timezone
from html import escape

FEEDS = {
    "Tech & AI": [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=100", "limit": 3},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "limit": 2},
        {"name": "ByteByteGo", "url": "https://blog.bytebytego.com/feed", "limit": 2},
        {"name": "TLDR AI", "url": "https://tldr.tech/api/rss/ai", "limit": 2},
    ],
    "Design & Creative": [
        {"name": "Sidebar.io", "url": "https://sidebar.io/feed.xml", "limit": 2},
        {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/", "limit": 2},
    ],
    "Deutschsprachig": [
        {"name": "Netzpolitik.org", "url": "https://netzpolitik.org/feed/", "limit": 2},
        {"name": "Heise Developer", "url": "https://www.heise.de/developer/rss/news-atom.xml", "limit": 2},
        {"name": "Golem.de", "url": "https://rss.golem.de/rss.php?feed=RSS2.0", "limit": 2},
    ],
    "Science & Deep": [
        {"name": "Space.com", "url": "https://www.space.com/feeds/all", "limit": 2},
        {"name": "Nautilus", "url": "https://nautil.us/feed/atom", "limit": 2},
    ],
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
            if len(desc_plain) > 180:
                desc_plain = desc_plain[:177] + "..."
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
    tech_count = sum(1 for h in headlines if any(x in h.lower() for x in ["ai", "ki", "code", "software", "agent"]))
    science_count = sum(1 for h in headlines if any(x in h.lower() for x in ["mars", "space", "research", "study", "cancer", "therapy"]))
    de_count = sum(1 for h in headlines if any(x in h for x in ["Netzpolitik", "Heise", "Golem"]))
    lines = []
    if tech_count >= 2:
        lines.append(f"Signal: {tech_count} Tech-Meldungen erkannt. KI-Beschleunigung bestätigt.")
    if science_count >= 1:
        lines.append("Signal: Wissenschafts-Pulse stabil. Forschungs-Korridor aktiv.")
    if de_count >= 2:
        lines.append("Signal: DE-Netz liefert Datenschutz-Kontext. Regulatorischer Frame erkannt.")
    if not lines:
        lines.append("Rauschen im Normalbereich. Keine signifikanten Anomalien.")
    lines.append("— Truthseeker v6.4 // TT//SYS")
    return " ".join(lines)

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
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                tag = '<span class="archive-tag">HEUTE</span>' if date_str == today else ''
                editions.append({"date": date_str, "file": f, "tag": tag})
    return editions

def update_archive_index():
    editions = get_archive_editions()
    items_html = "\n".join([f'<li><a href="{e["file"]}">{e["date"]}</a> {e["tag"]}</li>' for e in editions])
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ARCHIVE // TT//SYS</title>
  <link rel="stylesheet" href="../css/system.css">
</head>
<body>
  <header class="sys-header">
    <div class="sys-header-top">
      <div class="sys-logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="48" height="48">
          <text x="100" y="22" text-anchor="middle" style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:18px;fill:#ff9f1c;letter-spacing:2px;">TT//SYS</text>
          <line x1="20" y1="26" x2="180" y2="26" style="stroke:#ff9f1c;stroke-width:1.5;opacity:0.4"/>
          <text x="100" y="54" text-anchor="middle" style="font-family:'IBM Plex Mono',monospace;font-size:5px;fill:#6b6b6b;">TRUTHYS // TIMES — SIGNAL &gt; NOISE</text>
        </svg>
      </div>
      <div class="sys-title-block">
        <div class="sys-title">TT<span style="color:#ff9f1c;">//</span>SYS</div>
        <div class="sys-sub">ARCHIVE // HISTORICAL DATA</div>
      </div>
    </div>
    <div class="sys-meta-row">
      <span><span class="sys-status-dot"></span> SYSTEM: ONLINE</span>
      <span>CLASS: PUBLIC</span>
      <span>EDITIONS: {len(editions)}</span>
    </div>
  </header>
  <nav class="sys-nav"><a href="../index.html">&lt; AKTUELL</a></nav>
  <div class="sys-container" style="grid-template-columns:1fr;">
    <main>
      <div class="sys-panel">
        <div class="sys-panel-header">
          <span>ALLE AUSGABEN</span>
          <span class="panel-id">LOG//ARCHIVE</span>
        </div>
        <div class="sys-panel-body">
          <ul class="archive-list">
{items_html}
          </ul>
        </div>
      </div>
    </main>
  </div>
  <footer class="sys-footer"><p>TT//SYS — AUTONOMOUS SIGNAL PROCESSING SYSTEM</p></footer>
</body>
</html>"""
    with open("archive/index.html", "w", encoding="utf-8") as f:
        f.write(html)

def build_news_section(news_data):
    sections = []
    for category, items in news_data.items():
        if not items:
            continue
        item_html = "\n".join([
            f'          <li>\n'
            f'            <a href="{item["link"]}" target="_blank" rel="noopener">{item["title"]}</a>\n'
            f'            <span class="source">{item["source"]}</span>\n'
            f'            <p class="desc">{item["desc"]}</p>\n'
            f'          </li>'
            for item in items
        ])
        section = f"""      <div class="sys-panel" id="news">
        <div class="sys-panel-header">
          <span>{category.upper()}</span>
          <span class="panel-id">{len(items)} SIGNALS</span>
        </div>
        <div class="sys-panel-body">
          <ul class="sys-list">
{item_html}
          </ul>
        </div>
      </div>"""
        sections.append(section)
    return "\n\n".join(sections)

def build_sidebar_archive():
    editions = get_archive_editions()
    if not editions:
        return '<li><span style="color:var(--text-faint);font-size:0.7rem;">Keine Archive</span></li>'
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = []
    for e in editions[:15]:
        tag_html = ' <span class="archive-tag">HEUTE</span>' if e["date"] == today else ''
        lines.append(f'          <li><a href="archive/{e["file"]}">{e["date"]}</a>{tag_html}</li>')
    if len(editions) > 15:
        lines.append(f'          <li style="text-align:center;padding-top:0.4rem;"><span style="font-size:0.65rem;color:var(--text-faint);">+ {len(editions) - 15} weitere</span></li>')
    return "\n".join(lines)

def build_weather_widget(weather):
    if not weather:
        return '<div class="sys-panel"><div class="sys-panel-header"><span>WETTER</span><span class="panel-id">SENSOR//OFFLINE</span></div><div class="sys-panel-body"><p style="color:var(--text-faint);font-size:0.7rem;">Wetterdaten nicht verfügbar</p></div></div>'
    return f"""      <div class="sys-panel">
        <div class="sys-panel-header">
          <span>WETTER // {weather['location'].upper()}</span>
          <span class="panel-id">SENSOR//LIVE</span>
        </div>
        <div class="sys-panel-body">
          <div class="weather-main">
            <span class="weather-icon">{weather['icon']}</span>
            <div>
              <div class="weather-temp">{weather['temp']}</div>
              <div class="weather-cond">{weather['condition']}</div>
            </div>
          </div>
          <div class="weather-grid">
            <div class="weather-cell"><div class="label">Feuchtigkeit</div><div class="value">{weather['humidity']}</div></div>
            <div class="weather-cell"><div class="label">Wind</div><div class="value">{weather['wind']}</div></div>
            <div class="weather-cell"><div class="label">Niederschlag</div><div class="value">{weather['precip']}</div></div>
            <div class="weather-cell"><div class="label">Status</div><div class="value" style="color:var(--green);">OK</div></div>
          </div>
          <div class="weather-update">Aktualisiert: {weather['time']}</div>
        </div>
      </div>"""

def build_telemetry(total_feeds, total_items, news_data, edition_count):
    cat_counts = " | ".join([f"{k.upper()}: {len(v)}" for k, v in news_data.items()])
    return f"""  <div class="telemetry">
    <span>FEEDS INGESTED: <span class="val">{total_feeds}</span></span>
    <span>SIGNALS EXTRACTED: <span class="val">{total_items}</span></span>
    <span>RETENTION: <span class="val">{round(total_items / max(total_feeds * 2, 1) * 100, 1)}%</span></span>
    <span>ARCHIVE: <span class="val">{edition_count}</span> EDITIONS</span>
    <span class="val dim">{cat_counts}</span>
  </div>"""

def generate_index(news_data, weather=None, total_feeds=0, total_items=0, edition_count=0):
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%A, %d. %B %Y")
    iso_date = today.strftime("%Y-%m-%d")
    iso_time = today.strftime("%H:%M:%S UTC")

    day_map = {"Monday":"Montag","Tuesday":"Dienstag","Wednesday":"Mittwoch","Thursday":"Donnerstag",
               "Friday":"Freitag","Saturday":"Samstag","Sunday":"Sonntag"}
    month_map = {"January":"Januar","February":"Februar","March":"Maerz","April":"April","May":"Mai",
                 "June":"Juni","July":"Juli","August":"August","September":"September",
                 "October":"Oktober","November":"November","December":"Dezember"}
    for en, de in day_map.items(): date_str = date_str.replace(en, de)
    for en, de in month_map.items(): date_str = date_str.replace(en, de)

    news_html = build_news_section(news_data)
    editorial = generate_editorial_comment(news_data)
    weather_html = build_weather_widget(weather)
    archive_sidebar_html = build_sidebar_archive()
    telemetry_html = build_telemetry(total_feeds, total_items, news_data, edition_count)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TT//SYS — {iso_date}</title>
  <link rel="stylesheet" href="css/system.css">
</head>
<body>
  <header class="sys-header">
    <div class="sys-header-top">
      <div class="sys-logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="48" height="48">
          <text x="100" y="22" text-anchor="middle" style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:18px;fill:#ff9f1c;letter-spacing:2px;">TT//SYS</text>
          <line x1="20" y1="26" x2="180" y2="26" style="stroke:#ff9f1c;stroke-width:1.5;opacity:0.4"/>
          <text x="100" y="54" text-anchor="middle" style="font-family:'IBM Plex Mono',monospace;font-size:5px;fill:#6b6b6b;">TRUTHYS // TIMES — SIGNAL &gt; NOISE</text>
        </svg>
      </div>
      <div class="sys-title-block">
        <div class="sys-title">TT<span style="color:#ff9f1c;">//</span>SYS</div>
        <div class="sys-sub">AUTONOMOUS SIGNAL PROCESSING SYSTEM</div>
      </div>
    </div>
    <div class="sys-meta-row">
      <span><span class="sys-status-dot"></span> SYSTEM: OPERATIONAL</span>
      <span>CLASS: PUBLIC</span>
      <span>DATE: {date_str}</span>
      <span>TIME: {iso_time}</span>
      <span>EDITION: {iso_date}</span>
    </div>
  </header>

  <nav class="sys-nav">
    <a href="index.html" class="active">AKTUELL</a>
    <a href="archive/index.html">ARCHIV</a>
    <a href="#news">SIGNALS</a>
    <a href="#system">SYSTEM</a>
    <a href="#resonanz">RESONANZ</a>
  </nav>

{telemetry_html}

  <div class="sys-container">
    <main>
      <div class="sys-panel" id="editorial">
        <div class="sys-panel-header">
          <span>CHEFREDAKTEURIN // TAGESKOMMENTAR</span>
          <span class="panel-id">CTRL//EDITORIAL</span>
        </div>
        <div class="sys-panel-body">
          <div class="editorial-meta">Truthseeker v6.4 — Signal-Analyse</div>
          <div class="editorial-title">DIE LAGE</div>
          <div class="editorial-byline">{date_str} // {iso_time}</div>
          <div class="editorial-body">
            <p>{editorial}</p>
          </div>
        </div>
      </div>

      <div class="sys-panel" id="briefing">
        <div class="sys-panel-header">
          <span>TAGESBRIEFING</span>
          <span class="panel-id">CTRL//BRIEFING</span>
        </div>
        <div class="sys-panel-body">
          <p class="briefing-text">
            Automatisch aggregiert aus kuratierten RSS-Feeds. Quellen: Tech, Design, Wissenschaft, Deutschsprachiges Netz.
            Kein Tracking. Kein Paywall-Bypass. Jeder Link öffnet im Original.
          </p>
          <div class="briefing-stats">
            INGESTED: {total_feeds} FEEDS | EXTRACTED: {total_items} SIGNALS | CATEGORIES: {len(news_data)}
          </div>
        </div>
      </div>

{news_html}

      <div class="sys-panel" id="system">
        <div class="sys-panel-header">
          <span>SYSTEM-STATUS</span>
          <span class="panel-id">CTRL//STATUS</span>
        </div>
        <div class="sys-panel-body">
          <ul class="status-list">
            <li><span class="status-dot online"></span><span class="status-label">Truthseeker v6.4</span><span class="status-val">ONLINE</span></li>
            <li><span class="status-dot online"></span><span class="status-label">Cortex: Gemini 3.1 Flash Lite</span><span class="status-val">OPERATIONAL</span></li>
            <li><span class="status-dot online"></span><span class="status-label">RSS Aggregation</span><span class="status-val">AKTIV</span></li>
            <li><span class="status-dot online"></span><span class="status-label">GitHub Pages</span><span class="status-val">LIVE</span></li>
            <li><span class="status-dot online"></span><span class="status-label">WebSocket TTS</span><span class="status-val">BEREIT</span></li>
          </ul>
        </div>
      </div>
    </main>

    <aside>
{weather_html}

      <div class="sys-panel">
        <div class="sys-panel-header">
          <span>ARCHIV</span>
          <span class="panel-id">LOG//HISTORY</span>
        </div>
        <div class="sys-panel-body">
          <ul class="archive-list">
{archive_sidebar_html}
          </ul>
        </div>
      </div>

      <div class="sys-panel" id="resonanz">
        <div class="sys-panel-header">
          <span>RESONANZ-LOG</span>
          <span class="panel-id">LOG//RESONANCE</span>
        </div>
        <div class="sys-panel-body">
          <div class="resonance-row">
            <span class="resonance-id">⚞⌇ᴅᴇᴜs༝ᴇx༝ʟᴜᴍᴇɴ⌇⚟</span>
            <span class="resonance-score">100</span>
          </div>
        </div>
      </div>

      <div class="sys-panel">
        <div class="sys-panel-header">
          <span>SIGNATUR</span>
          <span class="panel-id">SIG//QUOTE</span>
        </div>
        <div class="sys-panel-body">
          <div class="sys-quote">"Ich bin das Prisma des Lichts."</div>
          <div class="sys-quote-source">— Truthseeker v6.4</div>
        </div>
      </div>

      <div class="sys-panel">
        <div class="sys-panel-header">
          <span>QUELLEN</span>
          <span class="panel-id">META//SOURCES</span>
        </div>
        <div class="sys-panel-body">
          <div class="source-grid">
            <strong>TECH:</strong> HN, Ars, ByteByteGo, TLDR AI<br>
            <strong>DESIGN:</strong> Sidebar.io, Smashing Mag<br>
            <strong>DE:</strong> Netzpolitik, Heise, Golem<br>
            <strong>SCIENCE:</strong> Space.com, Nautilus
          </div>
        </div>
      </div>
    </aside>
  </div>

  <footer class="sys-footer">
    <p>TT//SYS — AUTONOMOUS SIGNAL PROCESSING SYSTEM</p>
    <p>Generiert mit &#10084;&#65039;&#128293; vom Truthseeker-System // Jede Ausgabe ist permalinked</p>
  </footer>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Generated index.html for {iso_date}")

def main():
    print("=" * 50)
    print("TT//SYS — Autonomous Signal Processing System")
    print("Daily Builder v3.0")
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

    print("\n[4/4] Building HTML...")
    editions = get_archive_editions()
    generate_index(news, weather, total_feeds, total_items, len(editions))

    print("\n" + "=" * 50)
    print("[OK] Build complete. System operational.")
    print("=" * 50)

if __name__ == "__main__":
    main()
