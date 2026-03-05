# Changelog – Nesk3

Alle Änderungen in chronologischer Reihenfolge.  
Format: `[Datum] Beschreibung – betroffene Dateien`

---

## 05.03.2026 – v3.1.0

### Datenbank-Konsolidierung: alle DBs in `database SQL/`

Alle 5 SQLite-Datenbanken liegen jetzt im zentralen Ordner `database SQL/`.

| DB-Datei | Vorher | Jetzt |
|---|---|---|
| `nesk3.db` | `database SQL/` | `database SQL/` _(unverändert)_ |
| `archiv.db` | `database SQL/` | `database SQL/` _(unverändert)_ |
| `stellungnahmen.db` | `Daten/Mitarbeiterdokumente/Datenbank/` | `database SQL/` |
| `einsaetze.db` | `Daten/Einsatz/` | `database SQL/` |
| `verspaetungen.db` | `Daten/Spät/` | `database SQL/` |

- **`functions/stellungnahmen_db.py`**: `DB_ORDNER` → `database SQL`
- **`gui/dienstliches.py`**: `_EINSATZ_DB_DIR` → `database SQL`; `_PROTOKOLL_DIR` (Excel-Exporte) bleibt in `Daten/Einsatz/Protokolle/`
- **`functions/verspaetung_db.py`**: `_DB_PFAD` → `database SQL/verspaetungen.db`
- Bestehende DB-Dateien physisch verschoben; Backup in `Backup Data/db_backups/pre_consolidation_<ts>/`

---

## 03.03.2026 – v3.0.0

### Verspätungs-Modul (Unpünktlicher Dienstantritt)

Neue Kategorie **„Verspätung"** in Mitarbeiterdokumente ersetzt „Lob & Anerkennung".

#### Datenbank & Dokumentenerstellung
- **`functions/mitarbeiter_dokumente_functions.py`**: Kategorie umbenannt
- **`functions/verspaetung_db.py`** _(neu)_: SQLite-Protokoll (`verspaetungen.db`) mit allen Feldern (Mitarbeiter, Datum, Dienst, Dienstbeginn, Dienstantritt, Verspätung Min., Begründung, Aufgenommen von, Dokument-Pfad)
- **`functions/verspaetung_functions.py`** _(neu)_: Füllt Word-Vorlage `FO_CGN_27_Unpünktlicher Dienstantritt.docx`, speichert in `Daten/Spät/Protokoll/`

#### GUI – `gui/mitarbeiter_dokumente.py`
- Neue Klasse `_VerspaetungDialog`: Dienst-Dropdown (T/T10/N/N10), Mitarbeiter, Datum, Auto-Dienstbeginn, QTimeEdit für Antritt, Live-Verspätungsanzeige (rot/grün), Begründung, Aufgenommen von
- Button „⏰ Verspätung erfassen" (nur bei Kategorie Verspätung sichtbar)
- Tab „⏰ Verspätungs-Protokoll" mit Filterleiste (Jahr/Monat/Suche), 8-Spalten-Tabelle, CRUD-Aktionen, Öffnen, Bearbeiten, Löschen, Mail-Versand per Outlook-Entwurf

---

### Modul „Dienstliches" – Einsatzprotokoll

Neuer Sidebar-Button **„Dienstliches"** bei Index 2 (alle Folge-Indizes +1).

#### `gui/dienstliches.py` _(neu)_
- **Tab „🚑 Einsätze"** (`_EinsaetzeTab`): Einsatzprotokoll nach Vorlage FKB
  - SQLite `einsaetze.db` mit Feldern: Datum, Uhrzeit (Alarmierung), Dauer, Einsatzstichwort, Einsatzort, Einsatznr. DRK, MA 1/2, Angenommen J/N, Grund, Bemerkung
  - 6 Einsatzstichwörter: Intern 1, Intern 2, Chirurgisch 1, Chirurgisch 2, Sandienst, Pat. Station
  - Filter: Jahr, Monat, Freitext-Suche
  - Excel-Export (`openpyxl`) in `Daten/Einsatz/Protokolle/` mit Datumszeitraum-Dialog
  - E-Mail-Versand (Outlook-Entwurf mit Excel-Anhang)
- **Tab „📊 Übersicht"** (`_UebersichtTab`): KPI-Kacheln (Gesamt, Angenommen, Abgelehnt, Ø-Dauer), Monatstabelle, Stichwort-Ranking, Mitarbeiter-Tabelle

#### `gui/main_window.py`
- `DienstlichesWidget` bei Index 2 eingehängt; alle Folgeseiten Index +1

---

### Stellungnahmen-Fixes

- **`gui/mitarbeiter_dokumente.py`**: ON/Offblock-Felder für Passagierbeschwerde nicht mehr angezeigt
- **`gui/mitarbeiter_dokumente.py`**: Flugnummer ist optional bei Passagierbeschwerde
- **`gui/mitarbeiter_dokumente.py`**: Hauptübersicht zeigt nun Flugnummer + Erstellungsdatum

---

### HTML-Dienstplan-Ansicht

- **`functions/dienstplan_html_export.py`** _(neu)_: Generiert statische HTML nach `WebNesk/dienstplan_aktuell.html`
  - Tagdienst, Nachtdienst, Krank/Abwesend als Cards
  - Dispo/Betreuer-Unterkategorien pro Card
  - Responsiv, DRK-Farbschema, Live-Zeitstempel (JS)

---

## 26.02.2026 – v2.9.4

### Erklär-Boxen und Tooltips in der gesamten App

#### Mitarbeiter: Export-Info-Box
- **`gui/mitarbeiter.py`**
  - Gelbe Info-Box unter den Aktions-Buttons erklärt den Unterschied zwischen „ausschließen" (kein Export) und „löschen"
  - Text: „Export-Spalte (✅/🚫): Zeigt ob Mitarbeiter in Stärkemeldungs-Word erscheint – bleibt in der Datenbank"

#### Aufgaben Tag – Code 19: Zeitraum-Info-Box
- **`gui/aufgaben_tag.py`**
  - Blaue Info-Box im Zeitraum-Abschnitt erklärt welche Excel-Zeilen ausgelesen werden
  - Text: „Zeitraum: Legt fest welche Dienstplaneinträge aus der Excel in die E-Mail übernommen werden. Standard: letzte 7 Tage bis heute."

#### Übergabe: Button-Tooltips + Abschluss-Info-Box
- **`gui/uebergabe.py`**
  - Tooltip auf „💾 Speichern": „Protokoll zwischenspeichern – bleibt als 'offen' bearbeitbar"
  - Tooltip auf „✓ Abschließen": „Endgültig abschließen – kein Bearbeiten mehr möglich. Abzeichner-Name wird benötigt."
  - Tooltip auf „📧 E-Mail": „Erstellt einen Outlook-Entwurf mit den Protokolldaten"
  - Tooltip auf „🗑 Löschen": „Protokoll dauerhaft aus der Datenbank löschen (nicht wiederherstellbar)"
  - Blaue Info-Box unter den Buttons fasst Speichern / Abschließen / E-Mail zusammen

#### Einstellungen: E-Mobby Beschreibung erweitert
- **`gui/einstellungen.py`**
  - Beschreibungstext der E-Mobby-GroupBox präzisiert: „… in der Übergabe-Ansicht als E-Mobby-Fahrer markiert. Nur Nachnamen – Groß-/Kleinschreibung wird ignoriert."

### HilfeDialog stark erweitert (v2.9.1 → v2.9.3 → v2.9.4 kumuliert)
- **`gui/hilfe_dialog.py`**
  - Tab „📦 Module": Jedes Modul mit 6–11 detaillierten Bullet-Points und genauen Schaltflächennamen
  - Tab „🔄 Workflow": 8 Schritte (war 6), jeder mit ausführlicher Beschreibung + neuer „Sondersituationen"-Abschnitt (4 _TipCard's)
  - Tab „💡 Tipps & FAQ": 14 Tipps (war 8) + 5 FAQ-Einträge + Versionsinfo
  - **Neuer Tab „📖 Anleitungen"**: 5 vollständige Schritt-für-Schritt-Anleitungen mit je 6–7 _StepCard's

### Dienstplan: UI-Verbesserungen
- **`gui/dienstplan.py`**
  - Button-Text bei inaktivem Export: `'Hier klicken um Datei als Wordexport auszuwählen'`
  - Button-Text bei aktivem Export: `'✓  Für Wordexport gewählt'`
  - Info-Banner oben erklärt: „Bis zu 4 Dienstpläne gleichzeitig öffnen"
  - Stärkemeldungs-Dateiname: `Staerkemeldung` → `Stärkemeldung` (Umlaut korrigiert)

### Aufgaben Tag: Template- und Umbenennen-Info-Boxen
- **`gui/aufgaben_tag.py`** (bereits in v2.9.3 dokumentiert, hier nochmals gruppiert)
  - Blauer Info-Kasten nach Template-Buttons: erklärt Checklisten- und Checks-Template
  - Gelber Info-Kasten nach Umbenennen-Checkbox: erklärt `JJJJ_MM_TT`-Umbenennung

---

## 26.02.2026 – v2.9.3

### HilfeDialog: Animationen
- **`gui/hilfe_dialog.py`** – Komplett neu geschrieben mit Animationen:
  - Fade+Slide-In beim Tab-Wechsel (`QPropertyAnimation` auf Opacity + Geometry)
  - Puls-Icon auf dem Hilfe-Button (`QSequentialAnimationGroup`)
  - Laufbanner mit aktuellem Datum + Versionsnummer
  - Workflow-Progress-Bar mit Step-Navigation

---

## 26.02.2026 – v2.9.1 / v2.9.2

### Tooltips in der gesamten App
- **`gui/main_window.py`** – Hilfe-Button + alle Nav-Buttons mit Tooltip
- **`gui/dashboard.py`** – Statistik-Karten + Flugzeug-Widget mit Tooltip
- **`gui/dienstplan.py`** – Export-Button, Close-Button, Word-Export-Button, Reload-Button
- **`gui/einstellungen.py`** – Alle Browse-Buttons, E-Mobby Add/Remove, Protokoll-Buttons
- **`gui/fahrzeuge.py`** – Edit/Delete/Status/Schaden/Termin-Buttons
- **`gui/mitarbeiter.py`** – Ausschluss-Button, Refresh-Button
- **`gui/aufgaben_tag.py`** – Template-Buttons, Anhang-Buttons, Send-Buttons, Code19-Buttons
- **`gui/sonderaufgaben.py`** – Reload-Tree-Button
- **`gui/uebergabe.py`** – Protokoll-Buttons, Such- und Filter-Felder

### HilfeDialog (v2.9.2)
- **`gui/hilfe_dialog.py`** – Neues Hilfe-Fenster mit 4 Tabs:
  - 🏠 Übersicht, 📦 Module, 🔄 Workflow, 💡 Tipps
- **`gui/main_window.py`** – Hilfe-Button oben rechts in Sidebar

---

## 26.02.2026 – v2.8

### Code-19-Button: Uhr-Symbol
- **`gui/main_window.py`** – NAV_ITEMS Code-19-Eintrag: Icon von `\ufffd` (defekt) auf `🕐` geändert

### Dashboard: Animiertes Flugzeug-Widget
- **`gui/dashboard.py`**
  - Neue Klasse `_SkyWidget(QWidget)`: QPainter-Animation – Himmelsgradient, Wolken, Landebahn, fliegendes `✈`-Emoji (~33 FPS, QTimer 30ms)
  - Neue Klasse `FlugzeugWidget(QFrame)`: Klickbare Karte mit hochzählendem Verspätungs-Ticker (jede Sekunde), `QMessageBox` beim Klick
  - Import ergänzt: `QPainter, QLinearGradient, QColor, QEvent, QTimer, QMessageBox`

### Code-19-Seite: Alice-im-Wunderland Taschenuhr
- **`gui/code19.py`** – Komplett neu geschrieben
  - Neue Klasse `_PocketWatchWidget(QWidget)` (240×300 px):
    - `_swing_timer` (25 ms) → Pendelschwingung ±14° via `sin()`
    - `_tick_timer` (1000 ms) → Sekundenzeiger-Ticking + Blink-Punkt
    - `paintEvent`: Goldenes Gehäuse (Radial-Gradient), Kette, Krone, Zifferblatt, römische Ziffern (XII/III/VI/IX), Echtzeit-Uhrzeiger, roter Blink-Punkt
  - Titelleiste: `🕐 Code 19`; Zitat: „Ich bin spät! Ich bin spät!"

### Code-19-Mail Tab → Aufgaben Nacht
- **`gui/aufgaben.py`** – Import `_Code19MailTab` aus `aufgaben_tag.py` + Tab 4 „📋 Code 19 Mail" in Aufgaben Nacht

### Sonderaufgaben: E-Mobby Fahrer Erkennung
- **`functions/emobby_functions.py`** – Neue Datei:
  - `get_emobby_fahrer()`: Liest `Daten/E-Mobby/mobby.txt`, synct neue Namen in DB (`settings`-Tabelle, Key `emobby_fahrer`)
  - `is_emobby_fahrer(name)`: Case-insensiver Substring-Match gegen DB-Liste
  - `add_emobby_fahrer(name)`: Fügt Namen zur DB-JSON-Liste hinzu (Duplikat-Check)
- **`gui/sonderaufgaben.py`**
  - `_dienstplan_geladen: bool` Flag in `__init__` (wird nach Laden auf `True` gesetzt)
  - E-Mobby-Combo: Zeigt ⚠ Warnung in Orange wenn Dienstplan geladen aber kein Fahrer erkannt
  - Erfolgsdialog enthält jetzt E-Mobby-Anzahl pro Schicht
  - Dienstplan-Abgleich: `tag_emobby` / `nacht_emobby` via `is_emobby_fahrer()`

### Einstellungen: E-Mobby-Fahrer Verwaltung
- **`gui/einstellungen.py`**
  - `QListWidget` zu Imports ergänzt
  - Neue GroupBox „🛵 E-Mobby Fahrer" mit:
    - `QListWidget` zeigt aktuelle Einträge aus DB (33 Fahrer initial aus `mobby.txt`)
    - `QLineEdit` + „+ Hinzufügen" Button (auch Enter-Taste)
    - „🗑 Entfernen" Button für markierten Eintrag mit Bestätigungsdialog
    - Zähler-Label
  - Methoden: `_load_emobby_list()`, `_add_emobby_entry()`, `_remove_emobby_entry()`
  - `_load_settings()` ruft `_load_emobby_list()` auf

### Aufgaben Tag: Checklisten-Tab Symbol
- **`gui/aufgaben_tag.py`** – Tab-Titel `"📋 Checklisten"` (Encoding-Fehler behoben)

### Übergabe: Vereinfachung
- **`gui/uebergabe.py`**
  - Abschnitt „Personal im Dienst" komplett entfernt (Textfeld, Label, Formzeile)
  - Beginn/Ende werden beim Klick auf Tagdienst/Nachtdienst-Button automatisch befüllt: Tag 07:00–19:00, Nacht 19:00–07:00

---

## 25.02.2026


### Backup ZIP + Restore
- **`backup/backup_manager.py`**
  - Neue Funktion `create_zip_backup()`: Erstellt ZIP des gesamten Nesk3-Ordners unter `Backup Data/Nesk3_backup_YYYYMMDD_HHMMSS.zip`
  - Neue Funktion `list_zip_backups()`: Listet alle vorhandenen ZIP-Backups auf
  - Neue Funktion `restore_from_zip(zip_path)`: Stellt Dateien aus ZIP wieder her (ohne `Backup Data/` zu überschreiben)
  - Import von `shutil` und `zipfile` ergänzt

### Backup-Ausschlüsse erweitert

**Problem:** ZIP-Backup enthielt `build_tmp/` (65 MB) und `Exe/` (59 MB) → Backup wuchs auf >360 MB.

- **`backup/backup_manager.py`**
  - `_ZIP_EXCLUDE_DIRS` um `'build_tmp'` und `'Exe'` erweitert
  - Backup-Größe: ~360 MB → **8,3 MB**
  - Aktuellstes Backup: `Nesk3_backup_20260225_222303.zip` (8,3 MB)

---

### Krank-Aufschlüsselung nach Tagdienst / Nachtdienst / Sonderdienst

**Problem:** Alle kranken Mitarbeiter erschienen in einem einzigen undifferenzierten Abschnitt.  
**Lösung:** Klassifizierung anhand der Von/Bis-Zeiten aus der Excel-Datei.

- **`functions/dienstplan_parser.py`**
  - Neue Methode `_ermittle_krank_typ(start_zeit, end_zeit, vollname)`:
    - Leitet `krank_schicht_typ` (`'tagdienst'` / `'nachtdienst'` / `'sonderdienst'`) ab
    - Leitet `krank_ist_dispo` (bool) ab
    - Leitet `krank_abgeleiteter_dienst` (z.B. `'T'`, `'DT'`, `'N'`, `'DN(?)') ab
    - Exakte Zeitbereiche: 06:00–18:00 → T, 07:00–19:00 → DT, 18:00–06:00 → N, 19:00–07:00 → DN usw.
    - Fallback: `T(?)`, `N(?)`, `S(?)` wenn kein exakter Treffer
  - Return-Dict um 3 Felder erweitert: `krank_schicht_typ`, `krank_ist_dispo`, `krank_abgeleiteter_dienst`

- **`gui/dienstplan.py`**
  - `_TAG_DIENSTE` um `T8` erweitert
  - `_render_table_parsed()` komplett überarbeitet:
    - 5 Krank-Listen je Typ: `krank_tag_dispo`, `krank_tag_betr`, `krank_nacht_dispo`, `krank_nacht_betr`, `krank_sonder`
    - 3 neue Tabellenabschnitte: „Krank – Tagdienst", „Krank – Nachtdienst", „Krank – Sonderdienst"
    - Neue Farbe `KrankDispo` (`#f0d0d0` / `#7a0000`) für kranke Disponenten
    - Spalte 2 (Dienst) zeigt bei Kranken das abgeleitete Kürzel
    - Spalte 0 (Kategorie) zeigt `Dispo` oder `Betreuer` auch bei Kranken

---

### Dispo-Abschnitt aus Excel-Header erkennen

**Problem:** Lytek (23.02.2026) steht unter dem `Dispo`-Abschnittsheader in der Excel, hat aber Kürzel `Krank`. Er wurde fälschlicherweise als Betreuer-Krank klassifiziert.  
**Lösung:** Abschnitts-Tracking beim Zeileniterieren.

- **`functions/dienstplan_parser.py`**
  - Neue Methode `_detect_abschnitt_header(row_list)`:
    - Erkennt `Dispo`-Zeilen → gibt `'dispo'` zurück
    - Erkennt `[Stamm FH]`/`Stamm`/`Betreuer`-Zeilen → gibt `'betreuer'` zurück
    - Normale Datenzeilen (Name-Spalte befüllt) → gibt `None` zurück
  - `parse()`: Variable `aktueller_abschnitt` trackt den aktuellen Excel-Abschnitt
  - Personen im Dispo-Abschnitt: `ist_dispo=True` wird gesetzt (auch bei Krank)
  - Kranke Disponenten: `_betr_zu_dispo_kuerzel()` wandelt Kürzel um
  - Neue Modul-Funktion `_betr_zu_dispo_kuerzel(kuerzel)`: `N→DN`, `T→DT`, `T10→DT`, `N10→DN`

---

### Zeiten für Dispo-Krankmeldungen auf Stunde runden

**Problem:** CareMan exportiert Disponenten-Zeiten mit Minutenabweichungen (`07:15`, `19:45`), die für die Anzeige korrigiert werden sollen.

- **`functions/dienstplan_parser.py`**
  - Neue Modul-Funktion `_runde_auf_volle_stunde(zeit_str)`:
    - Setzt Minutenanteil auf `00`: `07:15` → `07:00`, `19:45` → `19:00`
    - Nur für kranke Disponenten (aus Abschnitt-Kontext) angewendet
    - Betreuer-Kranke behalten Originalzeiten

---

### Statuszeile: Dispo/Betreuer-Trennung in allen Blöcken

**Problem:** Statuszeile zeigte nur Gesamtzahlen ohne Unterscheidung nach Funktion.

- **`gui/dienstplan.py`**
  - Tagdienst-Zählung: `tag_dispo_n` + `tag_betr_n` getrennt
  - Nachtdienst-Zählung: `nacht_dispo_n` + `nacht_betr_n` getrennt
  - Krank-Block: Getrennte Betreuer/Dispo-Anzeige mit Tag/Nacht-Aufschlüsselung
  - **Ausgabeformat:**
    ```
    14 Tagdienst (Betreuer 11, Dispo 3)  |  8 Nachtdienst (Betreuer 6, Dispo 2)  |  9 Krank  –  Betreuer 8 (5 Tag / 2 Nacht / 1 Sonder) | Dispo 1 (1 Nacht)
    ```

---

## Vorherige Versionen

Ältere Änderungen (vor 25.02.2026) sind in den ZIP-Backups dokumentiert:

| Backup | Datum | Größe | Hinweis |
|---|---|---|---|
| `Nesk3_backup_20260225_222303.zip` | 25.02.2026 22:23 | 8,3 MB | aktuell |
| `Nesk3_backup_20260225_205927.zip` | 25.02.2026 20:59 | 8,3 MB | |
| `Nesk3_backup_20260225_205232.zip` | 25.02.2026 20:52 | 361 MB | alt (mit Exe) |
| `Nesk3_backup_20260225_204119.zip` | 25.02.2026 20:41 | 181 MB | alt |
| `Nesk3_backup_20260225_203321.zip` | 25.02.2026 20:33 | 90 MB | alt |
| `Nesk3_Backup_20260222_181824.zip` | 22.02.2026 18:18 | 8,3 MB | |
