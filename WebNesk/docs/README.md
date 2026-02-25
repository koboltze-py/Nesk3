# WebNesk – DRK Erste-Hilfe-Station Flughafen Köln/Bonn

Lokale WebApp zur Erfassung von **Fahrzeugzuständen** und **Schichtübergaben**.

---

## Variante A – Ohne Server (empfohlen)

**Datei:** `WebNesk_Lokal.html`

Einfach doppelklicken → öffnet sich im Browser.
Kein Python, kein Server, kein Setup notwendig.

- Daten werden im **Browser-Speicher (localStorage)** gesichert
- **Export als SQLite (.db)** → direkt mit Python lesbar
- **Export/Import als JSON** → zur Sicherung

**Standard-Login:** `admin` / `drk2026`

---

## Variante B – Mit Flask-Server (erweitert)

```powershell
# 1. Python-Pakete installieren (nur einmal nötig)
pip install -r requirements.txt

# 2. App starten
python run.py
```

Danach im Browser öffnen: **http://127.0.0.1:5000**

**Standard-Login:** `admin` / `drk2026` ← *nach dem ersten Start bitte ändern!*

---

## Ordnerstruktur

```
WebNesk/
├── app/
│   ├── __init__.py          Flask App-Factory
│   ├── models/
│   │   ├── user.py          Benutzermodell
│   │   ├── vehicle.py       Fahrzeugzustand-Modell
│   │   └── shift.py         Schichtübergabe-Modell
│   ├── routes/
│   │   ├── auth.py          Login / Logout
│   │   ├── dashboard.py     Startseite
│   │   ├── vehicles.py      Fahrzeugzustände
│   │   └── shifts.py        Schichtübergaben
│   ├── templates/           HTML-Vorlagen (Jinja2)
│   └── static/
│       ├── css/style.css    Eigenes CSS
│       └── js/main.js       Eigenes JavaScript
│
├── database/
│   ├── nesk.db              SQLite-Datenbank (wird automatisch erstellt)
│   └── schema.sql           Schema-Dokumentation (Referenz)
│
├── docs/
│   ├── README.md            Diese Datei
│   └── DATABASE.md          Datenbank-Dokumentation für externe Programme
│
├── functions/
│   └── helpers.py           Hilfsfunktionen (auch für externes Python-Programm nutzbar)
│
├── config.py                Konfiguration (Pfade, Schlüssel, Ports)
├── requirements.txt         Python-Abhängigkeiten
└── run.py                   Startdatei
```

---

## Daten mit Python lesen

### Aus JSON-Export (Variante A – lokale HTML-App)

```powershell
# Browser-Export (JSON) in SQLite konvertieren
python functions\lesen.py --json nesk_export.json --to-sqlite database\nesk.db

# Direkt aus JSON lesen und anzeigen
python functions\lesen.py --json nesk_export.json

# Nur Schichten der letzten 7 Tage
python functions\lesen.py --json nesk_export.json --days 7
```

### Direkt aus SQLite (Variante B – Flask-App oder konvertiert)

```powershell
python functions\lesen.py --db
```

### Im eigenen Python-Programm

```python
from functions.lesen import get_db_connection, read_latest_per_vehicle, read_shifts_from_db

con = get_db_connection()
fahrzeuge = read_latest_per_vehicle(con)
schichten = read_shifts_from_db(con, days=14)
con.close()
```

Vollständige Datenbankdokumentation: [docs/DATABASE.md](docs/DATABASE.md)

---

## Zugangsdaten ändern

Im laufenden Betrieb: In der SQLite-Datenbank mit einem DB-Browser
(z.B. [DB Browser for SQLite](https://sqlitebrowser.org/)) den Hash in der
`users`-Tabelle aktualisieren.

---

## Anforderungen

- Python 3.11 oder neuer
- Keine Internetverbindung zur Nutzung erforderlich (Bootstrap wird beim ersten
  Aufruf aus dem CDN geladen; für Offline-Betrieb kann Bootstrap lokal eingebunden werden)
