# TT//SYS — Webhook Integration

## Externer Webhook-Trigger

TT//SYS kann von externen Systemen via GitHub API getriggert werden.

### Methoden

**1. Repository Dispatch (Externe Webhooks)**

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/deusexlumen/truthys-times/dispatches \
  -d '{"event_type":"rss-update","client_payload":{"source":"webhook","reason":"new-signals"}}'
```

**2. Workflow Dispatch (Manuell / Dashboard)**

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/deusexlumen/truthys-times/actions/workflows/build.yml/dispatches \
  -d '{"ref":"main"}'
```

### Event-Typen

| Event Type | Zweck |
|------------|-------|
| `rebuild` | Vollständiger Rebuild |
| `rss-update` | Neue RSS-Signale erkannt |
| `webhook` | Generischer Webhook-Trigger |

### Token

Benötigt: `repo` scope (für private) oder `public_repo` (für public Repos).

Prime Node Token ist in `config/github.env` hinterlegt.

---

*TT//SYS — Autonomous Signal Processing System*
