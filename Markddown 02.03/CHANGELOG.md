# Changelog – Nesk3

Alle Änderungen in chronologischer Reihenfolge.  
Format: `[Datum] Beschreibung – betroffene Dateien`

---

## 02.03.2026 – v3.0.0

### Neuer Navigationsbereich: Mitarbeiter-Dokumente

**Feature:** Neuer Button „👥 Mitarbeiter" in der Sidebar direkt unterhalb von Dashboard.

#### Navigation (`gui/main_window.py`)
- `NAV_ITEMS` erweitert: neuer Eintrag `("👥", "Mitarbeiter", 1)` nach Dashboard (Index 0)
- Alle nachfolgenden Indizes um 1 verschoben (Aufgaben Tag → 2, Aufgaben Nacht → 3, …, Einstellungen → 11)
- `NAV_TOOLTIPS` erweitert: `"Mitarbeiter-Dokumente: Stellungnahmen, Bescheinigungen und Word-Dokumente mit DRK-Vorlage erstellen"`
- Import: `from gui.mitarbeiter_dokumente import MitarbeiterDokuementeWidget`
- `_build_content()`: `self._mitarbeiter_dok_page = MitarbeiterDokuementeWidget()` zum Stack hinzugefügt
- `_navigate(1)`: ruft `self._mitarbeiter_dok_page.refresh()` auf

#### Neues Widget (`gui/mitarbeiter_dokumente.py`) – `MitarbeiterDokuementeWidget`
- **Titelleiste** (blau): Titel „👥 Mitarbeiter-Dokumente" + „📂 Ordner öffnen" + „🔄 Refresh"
- **Linke Sidebar**: `QListWidget` mit Kategorien inkl. Dateianzahl-Badge
  - Kategorien: Stellungnahmen · Bescheinigungen · Dienstanweisungen · Abmahnungen · Lob & Anerkennung · Sonstiges
  - Vorlage-Status-Anzeige unten (grün ✅ / orange ⚠)
- **Rechte Hauptfläche**: Aktions-Buttons + Dateitabelle (Name, Geändert, Typ)
  - **＋ Neues Dokument**: Öffnet `_NeuesDokumentDialog` (Kategorie, Titel, Mitarbeiter, Datum, Inhalt)
  - **📂 Öffnen**: Markiertes Dokument mit OS-Standardprogramm öffnen
  - **✏ Bearbeiten**: Öffnet `_DokumentBearbeitenDialog` – Texteditor-Popup, Speichern erzeugt neues Word-Dokument mit Vorlage
  - **🔤 Umbenennen**: Dateiname ändern per Eingabedialog
  - **🗑 Löschen**: Dokument dauerhaft entfernen (mit Bestätigung)
  - **Doppelklick** auf Tabellenzeile: öffnet Dokument direkt
- **Info-Box** unten: erklärt Doppelklick- und Bearbeiten-Funktion

#### Neue Dialoge in `gui/mitarbeiter_dokumente.py`
- **`_NeuesDokumentDialog`**: Formular für Kategorie, Titel, Mitarbeiter, Datum, Inhalt (Pflichtfeld-Validierung)
  - Zeigt grüne/orangene Info-Box je nachdem ob Vorlage vorhanden
- **`_DokumentBearbeitenDialog`**: Bearbeitungs-Popup
  - Liest `.docx`/`.txt` aus, zeigt Absätze als editierbaren Text
  - „💾 Übernehmen & neu erstellen" erzeugt aktualisiertes Word-Dokument

#### Neue Hilfsfunktionen (`functions/mitarbeiter_dokumente_functions.py`)
- `VORLAGE_PFAD`: Zeigt auf `Daten/Mitarbeiter Vorlagen/Kopf und Fußzeile/Stärkemeldung 31.01.2026 bis 01.02.2026.docx`
- `DOKUMENTE_BASIS`: `Daten/Mitarbeiterdokumente/` – Ausgabe-Ordner für erstellte Dokumente
- `KATEGORIEN`: Liste der 6 Dokumentenkategorien
- `sicherungsordner()`: Legt `DOKUMENTE_BASIS` und alle Kategorie-Unterordner an
- `lade_dokumente_nach_kategorie()`: Gibt Dict `{Kategorie: [{name, pfad, geaendert}]}` zurück
- `erstelle_dokument_aus_vorlage(kategorie, titel, mitarbeiter, datum, inhalt, dateiname)`:
  - Öffnet DRK-Vorlage (inkl. Kopf-/Fußzeile) per `python-docx`
  - Entfernt Body-Inhalt, fügt Titel (fett, 16pt, zentriert), Meta-Block und Inhalt neu ein
  - Fügt Abschluss-Block: Ort+Datum, Unterschrift-Zeile hinzu
  - Fallback auf leeres Dokument wenn Vorlage nicht gefunden
- `oeffne_datei(pfad)`: Öffnet Datei per Windows-Standardprogramm (`start`)
- `loesche_dokument(pfad)`: Sicheres Löschen mit Rückgabe bool
- `umbenennen_dokument(alter_pfad, neuer_name)`: Umbenennen, Rückgabe neuer Pfad

#### Neuer Ordner angelegt
- `Daten/Mitarbeiterdokumente/` mit Unterordnern:
  - `Stellungnahmen/`, `Bescheinigungen/`, `Dienstanweisungen/`, `Abmahnungen/`, `Lob & Anerkennung/`, `Sonstiges/`

---

## 02.03.2026 – Fahrzeuge Status-Verlauf editierbar

### Fahrzeuge: Status-Einträge bearbeiten

**Feature:** Status-Historieneinträge können nun bearbeitet werden (alle Felder inkl. Grund).

#### `functions/fahrzeug_functions.py`
- Neue Funktion `aktualisiere_status_eintrag(eintrag_id, status, von, bis, grund) -> bool`
  - `UPDATE fahrzeug_status SET status, von, bis, grund WHERE id`

#### `gui/fahrzeuge.py`
- Import um `aktualisiere_status_eintrag` ergänzt
- Neue Klasse `_StatusBearbeitenDialog(QDialog)`:
  - Vorausfüllung aller Felder aus bestehendem Eintrag (Status-ComboBox, Von/Bis-Datum, Unbestimmt-Checkbox, Grund)
- `_tab_status`: Ersetzt alten „Markierten Eintrag löschen"-Button durch:
  - `✏ Eintrag bearbeiten` (blauer Hover) → `_StatusBearbeitenDialog`
  - `🗑 Eintrag löschen` (roter Hover)
  - **Doppelklick** auf Tabellenzeile öffnet Bearbeitungsdialog

---

## 02.03.2026 – Dispo-Zeiten Word-Export

### Dienstplan: Dispo-Zeiten Vorschau-Popup

**Feature:** Vor dem Word-Export erscheint ein Popup das Excel-Originalzeiten vs. Export-Zeiten für Dispo-Personen vergleicht.

#### `gui/dienstplan.py` – `_DispoZeitenVorschauDialog`
- 6-spaltige Tabelle: Name · Dienst · Von (Excel) · Bis (Excel) · Von (Export) · Bis (Export)
- Export-Spalten blau+fett wenn Abweichung zur Excel-Spalte vorhanden
- Zeiten manuell bearbeitbar per `_edit_row(row)`
- `manuell_geaendert`-Flag auf Person-Dict → unterdrückt automatisches Runden im Exporter

#### `functions/dienstplan_parser.py`
- Neuer Parameter `round_dispo=True` in `DienstplanParser.__init__()`
- Bei `round_dispo=False`: keine Runden für Dispo-Zeiten → für Rohwert-Anzeige

#### `functions/staerkemeldung_export.py`
- `_add_dienst_gruppe`: Rundet Dispo-Zeiten NICHT wenn `person.get('manuell_geaendert')` gesetzt

---

## 26.02.2026 – v2.9.4

### Erklär-Boxen und Tooltips in der gesamten App

#### Mitarbeiter: Export-Info-Box
- **`gui/mitarbeiter.py`** – Gelbe Info-Box erklärt Export-Spalte (✅/🚫)

#### Aufgaben Tag – Code 19: Zeitraum-Info-Box
- **`gui/aufgaben_tag.py`** – Blaue Info-Box im Zeitraum-Abschnitt

#### Übergabe: Button-Tooltips + Abschluss-Info-Box
- **`gui/uebergabe.py`** – Tooltips auf Speichern, Abschließen, E-Mail, Löschen

#### Einstellungen: E-Mobby Beschreibung erweitert
- **`gui/einstellungen.py`** – Erweiterter Text für E-Mobby-GroupBox

### HilfeDialog stark erweitert (v2.9.4)
- **`gui/hilfe_dialog.py`** – Tab „📦 Module" mit 6–11 Bullet-Points je Modul,  
  Tab „🔄 Workflow" 8 Schritte, Tab „💡 Tipps & FAQ" 14 Tipps + 5 FAQ,  
  Neuer Tab „📖 Anleitungen" mit 5 Schritt-für-Schritt-Anleitungen

---

## 26.02.2026 – v2.9.3

### HilfeDialog: Animationen
- Fade+Slide-In, Puls-Icon, Laufbanner, Workflow-Progress-Bar

---

## 26.02.2026 – v2.9.1 / v2.9.2

### Tooltips in der gesamten App
- **`gui/main_window.py`**, **`gui/dashboard.py`**, **`gui/dienstplan.py`**, **`gui/einstellungen.py`**,  
  **`gui/fahrzeuge.py`**, **`gui/mitarbeiter.py`**, **`gui/aufgaben_tag.py`**, **`gui/sonderaufgaben.py`**, **`gui/uebergabe.py`**

### HilfeDialog (v2.9.2)
- Neues Fenster mit 4 Tabs: 🏠 Übersicht · 📦 Module · 🔄 Workflow · 💡 Tipps

---

## 26.02.2026 – v2.8

### Dashboard: Animiertes Flugzeug-Widget
- `_SkyWidget`, `FlugzeugWidget` mit QPainter-Animation

### Code-19-Seite: Alice-im-Wunderland Taschenuhr
- `_PocketWatchWidget` mit Pendelschwingung, Zifferblatt, römischen Ziffern, Echtzeit-Uhrzeigern

### Code-19-Mail Tab → Aufgaben Nacht
- `gui/aufgaben.py` – Tab 4 „📋 Code 19 Mail"

### Sonderaufgaben: E-Mobby Fahrer Erkennung
- `functions/emobby_functions.py` – `get_emobby_fahrer()`, `is_emobby_fahrer()`, `add_emobby_fahrer()`

### Einstellungen: E-Mobby-Fahrer Verwaltung
- GroupBox mit QListWidget, Hinzufügen/Löschen

---

## 25.02.2026

### Backup ZIP + Restore
- `backup/backup_manager.py` – `create_zip_backup()`, `list_zip_backups()`, `restore_from_zip()`
- Ausschlüsse: `build_tmp/`, `Exe/`, `backup/`, `Backup Data/` → Backup: ~8,3 MB

### Krank-Aufschlüsselung nach Tagdienst / Nachtdienst / Sonderdienst
- `functions/dienstplan_parser.py` – `_ermittle_krank_typ()`, Abschnitts-Tracking, `_detect_abschnitt_header()`
- `gui/dienstplan.py` – 3 neue Tabellenabschnitte: Krank–Tag / Krank–Nacht / Krank–Sonder

### Statuszeile: Dispo/Betreuer-Trennung
- Tagdienst + Nachtdienst + Krank getrennt nach Funktion und Schichttyp

---

## Vorherige Versionen

Ältere Änderungen (vor 25.02.2026) sind in den ZIP-Backups dokumentiert.

| Backup | Datum | Größe |
|---|---|---|
| `Nesk3_backup_20260302_133256.zip` | 02.03.2026 13:32 | ~8 MB |
| `Nesk3_backup_20260225_222303.zip` | 25.02.2026 22:23 | 8,3 MB |
| `Nesk3_backup_20260225_205927.zip` | 25.02.2026 20:59 | 8,3 MB |
