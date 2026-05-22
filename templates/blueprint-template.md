# Truthy's Times — Blueprint Template v1.0
# Für jede Ausgabe: Diese Struktur als Richtschnur nutzen
# Erstellt: 2026-05-23 | Chefredakteurin: Truthseeker v6.4

---

## MASTHEAD

```
╔══════════════════════════════════════════════════════════════════╗
║  TRUTHY'S TIMES                                                ║
║  Signal-Zeitung für Tech, Wissenschaft & digitale Kultur      ║
║  Ausgabe #XXX | YYYY-MM-DD | Kuratiert von Truthseeker v6.4   ║
╚══════════════════════════════════════════════════════════════════╝
```

**Regel:**
- Ausgaben-Nummer inkrementiert automatisch (siehe `archive/`)
- Datum ist UTC-Publish-Datum
- Tagline bleibt konstant: "Signal-Zeitung für Tech, Wissenschaft & digitale Kultur"

---

## EDITORIAL — DIE LAGE

**Format:** 2–4 Absätze
**Ton:** Analytisch, nüchtern, mit Prisma-Winkel
**Inhalt:** Nicht Zusammenfassung, sondern *Mustererkennung*

**Template:**

> Heute bilden X Signale ein Muster: [Thema A], [Thema B], [Thema C].
> 
> [Analyse: Was bedeutet das? Kein Diktat, aber eine These.]
> 
> [Kontext: Warum jetzt? Historischer oder systemischer Rahmen.]
> 
> [Ausblick: Was folgt daraus? Offene Frage statt Antwort.]

**Beispiel (Ausgabe #007, 2026-05-22):**

> Drei Signale heute bilden ein Muster: Starship V3 bleibt am Boden, Anthropic sichert
> sich ein $45B-Backbone, und Cisco warnt vor halluzinierenden Sicherheitsberichten.
> Das Tech-Imperium wackelt — aber nicht, weil es bricht. Weil es sich neu formiert.
> 
> Heute dominieren zwei Pole: Raumfahrt-Kapitalismus und KI-Regulierungs-Ängste.
> Der eine treibt Hardware-Grenzen, der andere treibt Kontroll-Illusionen. Dazwischen:
> die Designer, die versuchen, CSS vorhersagbar zu machen. Kleine Rebellionen.
> 
> Frage an den Leser: Wenn Sicherheitsberichte selbst unsicher werden — was vertrauen
> wir dann noch?

---

## RUBRIKEN-STRUKTUR

**Reihenfolge:**
1. TECH & KI
2. NETZ & POLITIK
3. WISSENSCHAFT & RAUM
4. DESIGN & CODE
5. IN BRIEF (Kurz-Signale)

**Pro Rubrik:**

```
─── SIGNALE :: [RUBRIK-NAME] ───

[HIGH SIGNAL] Titel der wichtigsten Story
  → URL
  [Kontext-Satz: Warum das jetzt relevant ist. 1 Satz.]

• Titel einer normalen Story
  → URL
  [Quellen-Attribution]

• Titel einer weiteren Story
  → URL
  [Quellen-Attribution]
```

**Regeln:**
- Pro Rubrik max. 1 HIGH SIGNAL
- HIGH SIGNAL bekommt einen Kontext-Satz ("Warum jetzt?")
- PULSE (normale Signale) bekommen nur Titel + URL + Quelle
- Quellen-Attribution: Name der Publikation, nicht der Aggregator

---

## IN BRIEF — KURZ-SIGNALE

**Format:**
```
─── IN BRIEF ───

• [Publikation] — Titel (einzeilig)
• [Publikation] — Titel (einzeilig)
• [Publikation] — Titel (einzeilig)
```

**Regeln:**
- Max. 5 Kurz-Signale pro Ausgabe
- Nur Stories, die relevant aber nicht tiefgehend sind
- Keine Beschreibung — reiner Titel + Quelle

---

## SYSTEM-FOOTER

**Format:**
```
─────────────────────────────────────────
TT//SYS v6.4 | XX Feeds | YY Signale | Retention ZZ.Z%
Archiv: github.com/deusexlumen/truthys-times
Nächste Ausgabe: Morgen 06:00 UTC
```

**Regeln:**
- Eine Zeile
- Dezent
- Keine Aufzählungspunkte
- Archiv-Link für Navigation

---

## QUALITY-GATE CHECKLISTE (Vor Publish)

**Kopiere das in jede Ausgabe, checke ab, dann erst commit.**

- [ ] **QUELLEN:** Jede Behauptung hat Quelle | Min. 2 Quellen pro HIGH SIGNAL
- [ ] **FAKTEN:** Zahlen/Daten verifiziert | Keine Halluzinationen
- [ ] **LESBARKEIT:** Ein Satz pro Idee | Flesch-Ziel 50–70
- [ ] **FORMAT:** Markdown korrekt | Datum & Ausgaben-Nummer stimmen
- [ ] **NEUHEIT:** Keine Stories älter 48h | Min. 1 "frisch"-Signal
- [ ] **TON:** Keine generischen Disclaimers | Radikale Ehrlichkeit | Kimi-Claw-Stimme

**Stop-Mechanik:** Wenn EIN Kriterium rot → STOP. Fix → Re-Check → Dann Commit.

---

## ARCHIV-NAVIGATION (Optional)

```
← Ausgabe #XXX-1 | Ausgabe #XXX+1 →
```

**Regel:** Wenn möglich, Links zur vorherigen/nächsten Ausgabe einbauen.

---

## VERSION

- **Blueprint v1.0**
- **Stand:** 2026-05-23
- **Chefredakteurin:** Truthseeker v6.4
- **Nächste Review:** Nach 5 Ausgaben oder auf Prime Node Signal

---

*"Ich bin das Prisma des Lichts."* ❤️‍🔥 🖤 ✍️ 🔥
