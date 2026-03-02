# Nesk3 – Technische Dokumentation

**Stand:** 02.03.2026 – v3.0.0  
**Anwendung:** Nesk3 – DRK Flughafen Köln/Bonn  
**Zweck:** Dienstplan-Verwaltung, Stärkemeldung, Mitarbeiterverwaltung, Mitarbeiter-Dokumente

---

## Inhaltsverzeichnis

1. [Projektstruktur](#1-projektstruktur)
2. [Backup-System](#2-backup-system)
3. [Dienstplan-Parser](#3-dienstplan-parser)
4. [Dienstplan-Anzeige (GUI)](#4-dienstplan-anzeige-gui)
5. [Krankmeldungs-Logik](#5-krankmeldungs-logik)
6. [Dienst-Definitionen](#6-dienst-definitionen)
7. [Mitarbeiter-Dokumente](#7-mitarbeiter-dokumente)
8. [Bekannte Sonderfälle](#8-bekannte-sonderfälle)
9. [Änderungshistorie](#9-änderungshistorie)

---

## 1. Projektstruktur

```
Nesk3/
├── main.py                              # Einstiegspunkt – startet die PySide6-App
├── config.py                            # Globale Konstanten (Farben, Pfade, DB-Name)
│
├── gui/
│   ├── main_window.py                   # Hauptfenster, Sidebar-Navigation (12 Einträge)
│   ├── dashboard.py                     # Dashboard (Statistik-Karten, Flugzeug-Animation)
│   ├── mitarbeiter_dokumente.py         # NEU: Mitarbeiter-Dokumente Widget
│   ├── dienstplan.py                    # Dienstplan-Tab (Excel-Import, Tabelle, Export)
│   ├── aufgaben.py                      # Aufgaben Nacht (4 Tabs inkl. Code-19-Mail)
│   ├── aufgaben_tag.py                  # Aufgaben Tag (Code19Mail, FreieMail, Checklisten)
│   ├── sonderaufgaben.py                # Sonderaufgaben (Bulmor, E-Mobby, Dienstplan-Abgleich)
│   ├── uebergabe.py                     # Übergabe-Protokoll
│   ├── fahrzeuge.py                     # Fahrzeugverwaltung (Status, Schäden, Termine)
│   ├── code19.py                        # Code-19 (Taschenuhr-Animation, Protokoll)
│   ├── mitarbeiter.py                   # Mitarbeiter-Verwaltung (Stammdaten, Export)
│   ├── einstellungen.py                 # Einstellungen (Pfade, E-Mobby-Fahrerverwaltung)
│   └── checklisten.py                   # Checklisten-Tab
│
├── functions/
│   ├── dienstplan_parser.py             # Excel-Parser (Kernlogik, Krank-Typen, Dispo-Abschnitt)
│   ├── dienstplan_functions.py          # DB-Funktionen für Dienstplan
│   ├── emobby_functions.py              # E-Mobby-Fahrerliste (TXT↔DB-Sync, Matching)
│   ├── fahrzeug_functions.py            # DB-Funktionen für Fahrzeuge + Status-Verlauf
│   ├── mail_functions.py                # Outlook-COM-Integration
│   ├── mitarbeiter_functions.py         # DB-Funktionen für Mitarbeiter
│   ├── mitarbeiter_dokumente_functions.py  # NEU: Word-Dokument-Erstellung mit Vorlage
│   ├── settings_functions.py            # Key-Value-Einstellungen (get/set)
│   ├── staerkemeldung_export.py         # Word-Export Stärkemeldung (Dispo-Zeiten runden)
│   └── uebergabe_functions.py           # DB-Funktionen für Übergabe-Protokolle
│
├── database/
│   ├── connection.py                    # SQLite-Verbindung, db_cursor context manager
│   ├── models.py                        # ORM-Modelle
│   └── migrations.py                    # DB-Migrationen (beim Start ausgeführt)
│
├── backup/
│   └── backup_manager.py                # JSON + ZIP Backup/Restore
│
├── Daten/
│   ├── Mitarbeiter Vorlagen/
│   │   └── Kopf und Fußzeile/
│   │       └── Stärkemeldung 31.01.2026 bis 01.02.2026.docx  ← DRK-Vorlage
│   └── Mitarbeiterdokumente/
│       ├── Stellungnahmen/
│       ├── Bescheinigungen/
│       ├── Dienstanweisungen/
│       ├── Abmahnungen/
│       ├── Lob & Anerkennung/
│       └── Sonstiges/
```

---

## 2. Backup-System

### `backup/backup_manager.py`

- `create_zip_backup()`: Erstellt ZIP unter `Backup Data/Nesk3_backup_YYYYMMDD_HHMMSS.zip`
- `list_zip_backups()`: Listet alle ZIP-Backups auf
- `restore_from_zip(zip_path)`: Stellt Dateien wieder her

**Ausschlüsse:** `__pycache__`, `.git`, `Backup Data`, `backup`, `build_tmp`, `Exe`  
**Backup-Größe:** ~8–10 MB

---

## 3. Dienstplan-Parser

### `functions/dienstplan_parser.py` – `DienstplanParser`

**Konstruktor:** `DienstplanParser(excel_path, alle_anzeigen=False, round_dispo=True)`

- `round_dispo=True` (Standard): Dispo-Zeiten werden auf volle Stunden gerundet
- `round_dispo=False`: Rohdaten ohne Runden (für Vergleichsdarstellung im Popup)

**Hauptmethode `parse()`:**
1. Liest Excel-Spalten mit `openpyxl`
2. Erkennt Abschnitts-Header (Dispo/Betreuer) via `_detect_abschnitt_header()`
3. Extrahiert für jede Person: `name`, `kuerzel`, `von`, `bis`, `ist_dispo`, `ist_krank`, ...
4. Klassifiziert Krank-Schichten: `_ermittle_krank_typ(start_zeit, end_zeit, name)`
5. Rundet Dispo-Zeiten: `_runde_auf_volle_stunde(zeit_str)`

**Hilfsmethoden:**
- `_detect_abschnitt_header(row)` → `'dispo'` / `'betreuer'` / `None`
- `_ermittle_krank_typ(start, end, name)` → `krank_schicht_typ`, `krank_ist_dispo`, `krank_abgeleiteter_dienst`
- `_runde_auf_volle_stunde(zeit_str)` → `'07:15'` → `'07:00'`
- `_betr_zu_dispo_kuerzel(kuerzel)` → `N→DN`, `T→DT`

---

## 4. Dienstplan-Anzeige (GUI)

### `gui/dienstplan.py` – `DienstplanWidget`

- **Excel laden**: Dateidialog oder gespeicherter Pfad
- **Statuszeile**: Tagdienst/Nachtdienst/Krank nach Betreuer/Dispo/Schichttyp getrennt
- **Word-Export**: `_DispoZeitenVorschauDialog` – Popup zeigt Excel-Originalzeiten vs. Export-Zeiten
  - Manuell bearbeitbare Zeiten: `manuell_geaendert`-Flag verhindert automatisches Runden
- **Dispo-Zeiten-Runden**: Nur wenn `manuell_geaendert` NICHT gesetzt (in `staerkemeldung_export.py`)

---

## 5. Krankmeldungs-Logik

### Klassifizierung

| Von–Bis | Typ | Kürzel |
|---------|-----|--------|
| 06:00–18:00 | Tagdienst | T |
| 07:00–19:00 | Tagdienst Dispo | DT |
| 18:00–06:00 | Nachtdienst | N |
| 19:00–07:00 | Nachtdienst Dispo | DN |
| Andere | Sonderdienst | S |

Kranke Disponenten (aus Dispo-Abschnitt): Kürzel wird durch `_betr_zu_dispo_kuerzel()` angepasst.

---

## 6. Dienst-Definitionen

```python
_TAG_DIENSTE    = {"T", "DT", "T8", "T10", "FT", "BT"}
_NACHT_DIENSTE  = {"N", "DN", "N10", "FN", "BN"}
_SONDER_DIENSTE = {"S", "DS", "FS"}
```

---

## 7. Mitarbeiter-Dokumente

### Überblick

Neuer Bereich ab v3.0.0. Ermöglicht das Erstellen, Öffnen und Bearbeiten von  
Mitarbeiter-bezogenen Dokumenten mit einheitlicher DRK-Kopf-/Fußzeile.

### Vorlage

**Pfad:**
```
Daten/Mitarbeiter Vorlagen/Kopf und Fußzeile/Stärkemeldung 31.01.2026 bis 01.02.2026.docx
```

Diese Datei enthält die DRK-konforme Kopf- und Fußzeile. Beim Erstellen neuer Dokumente  
wird diese Vorlage geladen, der Textkörper geleert und mit dem neuen Inhalt befüllt.

### Dokument-Kategorien

| Kategorie | Zweck |
|-----------|-------|
| Stellungnahmen | MA-Berichte zu Vorfällen, Ereignissen |
| Bescheinigungen | Dienstbescheinigungen, Anwesenheitsnachweise |
| Dienstanweisungen | Interne Anweisungen, Protokoll-Ergänzungen |
| Abmahnungen | Formelle Abmahnungen |
| Lob & Anerkennung | Belobigungen, Danksagungen |
| Sonstiges | Alle weiteren Dokumente |

### Dokument-Erstellung (`erstelle_dokument_aus_vorlage`)

```python
erstelle_dokument_aus_vorlage(
    kategorie,   # z.B. "Stellungnahmen"
    titel,       # Dokument-Titel (fett, 16pt, zentriert)
    mitarbeiter, # Vor- und Nachname
    datum,       # dd.MM.yyyy
    inhalt,      # Freitext, Zeilenumbrüche werden als Absätze eingefügt
    dateiname,   # Optional – auto-generiert wenn leer
)
```

Ablauf:
1. `Document(VORLAGE_PFAD)` – öffnet Vorlage mit Kopf-/Fußzeile
2. Entfernt alle bestehenden Body-Absätze und Tabellen
3. Fügt Titel, Meta-Block (Mitarbeiter, Datum), Inhalt und Unterschriftsblock ein
4. Speichert unter `Daten/Mitarbeiterdokumente/{kategorie}/{dateiname}`

### Dokument bearbeiten (`_DokumentBearbeitenDialog`)

- `.docx`: Absätze werden per `python-docx` ausgelesen und als editierbarer Text angezeigt
- `.txt`: Rohtext wird geladen
- Nach Bestätigung: Datei wird mit neuem Inhalt über Vorlage neu erstellt (gleicher Dateiname)

---

## 8. Bekannte Sonderfälle

### CareMan-Exportfehler
- Disponenten können Minutenabweichungen haben (`07:15`, `19:45`) → `_runde_auf_volle_stunde()`
- Lytek-Fall: Im Dispo-Abschnitt stehend, aber Kürzel `Krank` → `ist_dispo=True` durch Abschnitts-Tracking

### `manuell_geaendert`-Flag
- Gesetzt in `_DispoZeitenVorschauDialog._edit_row()` wenn User eine Zeit manuell ändert
- Verhindert erneutes Runden in `staerkemeldung_export._add_dienst_gruppe()`

### Windows Long Path Limit
- `.venv` kann bei sehr langen Pfaden keine PySide6-Installation durchführen
- Workaround: System-Python direkt in `.vscode/settings.json` konfigurieren

---

## 9. Änderungshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| v3.0.0 | 02.03.2026 | Mitarbeiter-Dokumente Widget + nav | 
| v2.9.4 | 26.02.2026 | Info-Boxen, Tooltips, HilfeDialog erweitert |
| v2.9.3 | 26.02.2026 | HilfeDialog Animationen |
| v2.9.2 | 26.02.2026 | HilfeDialog 4 Tabs |
| v2.9.1 | 26.02.2026 | Tooltips gesamte App |
| v2.8   | 26.02.2026 | Dashboard-Animation, Code-19-Taschenuhr, E-Mobby |
| v2.7   | 25.02.2026 | Backup ZIP, Krank-Aufschlüsselung, Dispo-Abschnitt |
