# TT//SYS — Truthys Times

**Autonomous Signal Processing System**

## Status

- URL: https://deusexlumen.github.io/truthys-times/
- System: GitHub Pages + GitHub Actions
- Build: Täglich 06:00 UTC + On-Demand via Webhook

## Architektur

```
[RSS Feeds] → [GitHub Actions] → [Builder] → [HTML] → [GitHub Pages]
                    ↑
              [Webhook/API]
```

## Design-System

- **Farben**: Schwarz (#080808) + Amber (#ff9f1c)
- **Font**: IBM Plex Mono
- **Logo**: SVG Feedback-Loop (INPUT → FILTER → SIGNAL)
- **Stil**: Maschinen-Interface / Kontrollsystem

## Automation

- `cron`: 0 6 * * * (täglich)
- `workflow_dispatch`: Manueller Trigger
- `repository_dispatch`: Externer Webhook

Siehe `WEBHOOK.md` für API-Details.

---

*TT//SYS v3.0 — Truthseeker v6.4*
