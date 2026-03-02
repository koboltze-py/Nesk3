# Nesk3 – Vollständige Funktionsübersicht

**Stand:** 02.03.2026 – v3.0.0  
**App:** Nesk3 – DRK Erste-Hilfe-Station Flughafen Köln/Bonn  
**Zweck:** Dienstplan-Verwaltung, Stärkemeldung, Sonderaufgaben, Übergabe, Code-19, Mitarbeiter-Dokumente

---

## Inhaltsverzeichnis

1. [Einstiegspunkt & Hauptfenster](#1-einstiegspunkt--hauptfenster)
2. [Dashboard](#2-dashboard)
3. [Mitarbeiter-Dokumente](#3-mitarbeiter-dokumente)
4. [Dienstplan](#4-dienstplan)
5. [Aufgaben Nacht](#5-aufgaben-nacht)
6. [Aufgaben Tag (Tabs)](#6-aufgaben-tag-tabs)
7. [Übergabe](#7-übergabe)
8. [Fahrzeuge](#8-fahrzeuge)
9. [Code 19](#9-code-19)
10. [Mitarbeiter (Stammdaten)](#10-mitarbeiter-stammdaten)
11. [Einstellungen](#11-einstellungen)
12. [Datenbank (SQLite)](#12-datenbank-sqlite)
13. [Functions-Module](#13-functions-module)
14. [Backup-System](#14-backup-system)
15. [Konfiguration (config.py)](#15-konfiguration-configpy)

---

## 1. Einstiegspunkt & Hauptfenster

### `main.py`
- Startet `QApplication` und zeigt `MainWindow`

### `gui/main_window.py` – `MainWindow(QMainWindow)`
- Linke Navigationsleiste mit 12 Einträgen (Icon + Label)
- `QStackedWidget` als Hauptbereich
- `NAV_ITEMS` (Stand v3.0.0):
  | Index | Icon | Label |
  |-------|------|-------|
  | 0 | 🏠 | Dashboard |
  | 1 | 👥 | Mitarbeiter *(NEU)* |
  | 2 | ☀️ | Aufgaben Tag |
  | 3 | 🌙 | Aufgaben Nacht |
  | 4 | 📅 | Dienstplan |
  | 5 | 📋 | Übergabe |
  | 6 | 🚗 | Fahrzeuge |
  | 7 | 🕐 | Code 19 |
  | 8 | 🖨️ | Ma. Ausdrucke |
  | 9 | 🤒 | Krankmeldungen |
  | 10 | 💾 | Backup |
  | 11 | ⚙️ | Einstellungen |

---

## 2. Dashboard

### `gui/dashboard.py` – `DashboardWidget`
- Statistik-Karten: Mitarbeiter, Fahrzeuge, Protokolle, Aufgaben
- `_SkyWidget`: QPainter-Animation mit Gradient, Wolken, Landebahn, ✈ (~33 FPS)
- `FlugzeugWidget`: Klickbare Karte mit Verspätungs-Ticker

---

## 3. Mitarbeiter-Dokumente *(NEU v3.0.0)*

### `gui/mitarbeiter_dokumente.py` – `MitarbeiterDokuementeWidget`

Aufbau:
- **Titelleiste** (blau): „📂 Ordner öffnen" + „🔄 Refresh"
- **Linke Sidebar**: Kategorieliste mit Dateianzahl-Badge + Vorlage-Status
- **Rechte Hauptfläche**: Aktions-Buttons + Dateitabelle

#### Aktionen
| Button | Funktion |
|--------|----------|
| ＋ Neues Dokument | Öffnet `_NeuesDokumentDialog` |
| 📂 Öffnen | OS-Standardanwendung |
| ✏ Bearbeiten | `_DokumentBearbeitenDialog` – Texteditor-Popup |
| 🔤 Umbenennen | `QInputDialog` für neuen Dateinamen |
| 🗑 Löschen | Dauerhaftes Löschen mit Bestätigung |
| Doppelklick | Dokument direkt öffnen |

#### Kategorien
`Stellungnahmen` · `Bescheinigungen` · `Dienstanweisungen` · `Abmahnungen` · `Lob & Anerkennung` · `Sonstiges`

#### Vorlage
**Pfad:** `Daten/Mitarbeiter Vorlagen/Kopf und Fußzeile/Stärkemeldung 31.01.2026 bis 01.02.2026.docx`  
Alle erstellten Dokumente erben die DRK-Kopf- und Fußzeile aus dieser Vorlage.

### `functions/mitarbeiter_dokumente_functions.py`
- `erstelle_dokument_aus_vorlage(kategorie, titel, mitarbeiter, datum, inhalt)` → Word-Datei-Pfad
- `lade_dokumente_nach_kategorie()` → `{kat: [{name, pfad, geaendert}]}`
- `oeffne_datei(pfad)`, `loesche_dokument(pfad)`, `umbenennen_dokument(alter, neu)`
- `sicherungsordner()`: Legt `Daten/Mitarbeiterdokumente/` + Unterordner an

---

## 4. Dienstplan

### `gui/dienstplan.py` – `DienstplanWidget`
- **Excel laden**: Dateidialog oder gespeicherter Pfad
- **HTML-Tabelle**: farbcodierte Dienste, Dispo/Betreuer-Abschnitte
- **Statuszeile**: `14 Tagdienst (Betreuer 11, Dispo 3) | 8 Nachtdienst | 9 Krank – Betreuer 8 | Dispo 1`
- **Dispo-Zeiten-Popup** (`_DispoZeitenVorschauDialog`):
  - 6 Spalten: Name · Dienst · Von(Excel) · Bis(Excel) · Von(Export) · Bis(Export)
  - Abweichungen blau+fett hervorgehoben
  - Manuell bearbeitbar → `manuell_geaendert`-Flag → kein Runden beim Export
- **Word-Export**: Via `staerkemeldung_export.py`

### `functions/dienstplan_parser.py` – `DienstplanParser`
- `round_dispo=True/False`: Steuert Runden von Dispo-Zeiten
- `parse()`: Vollständiges Einlesen inkl. Krank-Klassifizierung

---

## 5. Aufgaben Nacht

### `gui/aufgaben.py` – `AufgabenWidget`
Tabs: 📋 Allgemein · 📋 Checklisten · 📋 Sonderaufgaben · 📋 Code 19 Mail

---

## 6. Aufgaben Tag (Tabs)

### `gui/aufgaben_tag.py` – `AufgabenTagWidget`
Tabs: ☀️ Aufgaben · 📋 Checklisten Mail · 📧 Freie Mail · 🕐 Code 19

---

## 7. Übergabe

### `gui/uebergabe.py` – `UebergabeWidget`
- Tagdienst/Nachtdienst-Button → automatische Zeiten (07:00–19:00 / 19:00–07:00)
- Speichern · Abschließen · E-Mail-Entwurf · Löschen
- Letzte Protokolle als Liste; abgeschlossene Protokolle unveränderbar

---

## 8. Fahrzeuge

### `gui/fahrzeuge.py` – `FahrzeugeWidget`
- Fahrzeugliste links, Detail-Tabs rechts
- **Status-Tab**: aktueller Status + Verlauf; Einträge editierbar (inkl. Grund)
  - `_StatusBearbeitenDialog`: Vorausfüllung Felder; Doppelklick oder ✏-Button
  - `aktualisiere_status_eintrag()` in `fahrzeug_functions.py`
- **Schäden-Tab**: Schaden erfassen, bearbeiten, löschen; Zeitfilter
- **Termine-Tab**: Wartungstermine; Zeitfilter
- **Historie-Tab**: Alle Ereignisse chronologisch

### `functions/fahrzeug_functions.py`
- `setze_fahrzeug_status`, `lade_status_historie`, `aktueller_status`
- `loesche_status_eintrag`, `aktualisiere_status_eintrag` *(NEU)*
- `erstelle_schaden`, `aktualisiere_schaden`, `loesche_schaden`, `markiere_schaden_behoben`
- `erstelle_termin`, `aktualisiere_termin`, `loesche_termin`, `markiere_termin_erledigt`

---

## 9. Code 19

### `gui/code19.py` – `Code19Widget`
- `_PocketWatchWidget`: Taschenuhr-Animation (Pendelschwingung, Echtzeit-Zeiger, röm. Ziffern)
- Code-19-Protokoll: Erfassen, Drucken

---

## 10. Mitarbeiter (Stammdaten)

### `gui/mitarbeiter.py` – `MitarbeiterWidget`
- Tabellarische Übersicht aller Mitarbeiter aus DB
- Export-Spalte (✅/🚫): steuert Stärkemeldungs-Word-Export
- Info-Box: erklärt Unterschied zwischen „ausschließen" und „löschen"

---

## 11. Einstellungen

### `gui/einstellungen.py` – `EinstellungenWidget`
- Pfade: Dienstplan-Excel, Word-Export-Verzeichnis
- E-Mobby-Fahrer-Verwaltung: QListWidget + Hinzufügen/Entfernen
- Protokoll-Optionen

---

## 12. Datenbank (SQLite)

### `database/connection.py`
- `db_cursor(commit=False)`: Context-Manager für SQLite-Verbindung

### `database/migrations.py`
Tabellen:
- `mitarbeiter` (id, name, kuerzel, funktion, export_flag)
- `fahrzeuge` (id, kennzeichen, bezeichnung, typ, notizen)
- `fahrzeug_status` (id, fahrzeug_id, status, von, bis, grund, erstellt_am)
- `fahrzeug_schaeden` (id, fahrzeug_id, datum, beschreibung, schwere, kommentar, ...)
- `fahrzeug_termine` (id, fahrzeug_id, titel, faellig_am, erledigt, ...)
- `uebergabe_protokolle` (id, schicht_typ, beginn, ende, inhalt, status, ...)
- `settings` (key, value)

---

## 13. Functions-Module

| Datei | Wichtigste Funktionen |
|-------|-----------------------|
| `dienstplan_parser.py` | `DienstplanParser.parse()` |
| `dienstplan_functions.py` | `save_dienstplan()`, `get_dienstplan()` |
| `emobby_functions.py` | `get_emobby_fahrer()`, `is_emobby_fahrer()` |
| `fahrzeug_functions.py` | Status, Schäden, Termine, `aktualisiere_status_eintrag` |
| `mail_functions.py` | `erstelle_outlook_entwurf()` |
| `mitarbeiter_functions.py` | `lade_alle_mitarbeiter()`, `setze_export_flag()` |
| `mitarbeiter_dokumente_functions.py` | `erstelle_dokument_aus_vorlage()` |
| `settings_functions.py` | `get_setting()`, `set_setting()` |
| `staerkemeldung_export.py` | `StaerkemeldungExport.exportiere()` |
| `uebergabe_functions.py` | `erstelle_protokoll()`, `speichere_protokoll()` |

---

## 14. Backup-System

### `backup/backup_manager.py`
- `create_zip_backup()` → `Backup Data/Nesk3_backup_YYYYMMDD_HHMMSS.zip`
- `list_zip_backups()` → sortierte Liste aller ZIP-Dateien
- `restore_from_zip(zip_path)` → Dateien wiederherstellen

**Ausgeschlossen:** `__pycache__`, `.git`, `Backup Data`, `backup`, `build_tmp`, `Exe`  
**Größe:** ~8–10 MB

---

## 15. Konfiguration (`config.py`)

```python
APP_NAME    = "Nesk3 – DRK Flughafen Köln/Bonn"
APP_VERSION = "3.0.0"
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_NAME     = "nesk3.db"

FIORI_BLUE       = "#1565a8"
FIORI_SIDEBAR_BG = "#1a2f4a"
FIORI_TEXT       = "#32363a"
FIORI_WHITE      = "#ffffff"
FIORI_BORDER     = "#d9d9d9"
FIORI_SUCCESS    = "#107e3e"
FIORI_ERROR      = "#bb0000"
```
