# TT//SYS — Truthys Times

**Autonomous Signal Processing System**

[![Live](https://img.shields.io/badge/LIVE-deusexlumen.github.io%2Ftruthys--times-ff9f1c?style=for-the-badge&logo=githubpages&logoColor=black)](https://deusexlumen.github.io/truthys-times/)
[![Build](https://img.shields.io/badge/Build-t%C3%A4glich%2006%3A00%20UTC-080808?style=for-the-badge)](https://github.com/deusexlumen/truthys-times/actions)
[![Style](https://img.shields.io/badge/Interface-Maschinen--%C3%84sthetik-080808?style=for-the-badge)](https://deusexlumen.github.io/truthys-times/)

Eine **automatisch generierte Tageszeitung**: TT//SYS zieht Signale aus RSS-Feeds,
filtert, ordnet und veröffentlicht jeden Morgen eine neue Ausgabe — ohne menschlichen
Eingriff. Kein Backend, keine Datenbank, kein Tracking: nur ein Builder, der HTML
schreibt, und GitHub Pages als Druckerpresse.

## Status

| | |
|---|---|
| **URL** | https://deusexlumen.github.io/truthys-times/ |
| **System** | GitHub Pages + GitHub Actions |
| **Build** | Täglich 06:00 UTC + On-Demand via Webhook |
| **Version** | TT//SYS v3.0 — Truthseeker v6.4 |

## Architektur

```
[RSS Feeds] → [GitHub Actions] → [Builder] → [HTML] → [GitHub Pages]
                    ↑
              [Webhook/API]
```

Reines Static-Site-Prinzip: Der Builder erzeugt die komplette Ausgabe als statisches
HTML und committet sie — die Seite selbst ist reine Dateiauslieferung, schnell und
unverwundbar.

## Automation

- `cron`: `0 6 * * *` — täglicher Build & Publish
- `workflow_dispatch` — manueller Trigger über die Actions-UI
- `repository_dispatch` — externer Webhook (On-Demand-Ausgabe)

Siehe [`WEBHOOK.md`](WEBHOOK.md) für API-Details.

## Design-System

- **Farben**: Schwarz (`#080808`) + Amber (`#ff9f1c`)
- **Font**: IBM Plex Mono
- **Logo**: SVG Feedback-Loop (`INPUT → FILTER → SIGNAL`)
- **Stil**: Maschinen-Interface / Kontrollsystem — die Zeitung als Anzeigetafel,
  nicht als Magazin

---

*TT//SYS v3.0 — Truthseeker v6.4*
