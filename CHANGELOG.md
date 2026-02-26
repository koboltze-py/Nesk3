# Changelog – Nesk3

Alle Änderungen in chronologischer Reihenfolge.  
Format: `[Datum] Beschreibung – betroffene Dateien`

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
