# Dienstplan-Modul — vollständige technische Dokumentation

> **Stand:** 22.02.2026 — v2.4
> **Datei:** `gui/dienstplan.py`, `functions/dienstplan_parser.py`, `functions/staerkemeldung_export.py`  
> **Zweck:** Excel-Dienstpläne einlesen, in 4-Pane-Ansicht anzeigen und als Word-Stärkemeldung exportieren

---

## Inhaltsverzeichnis

1. [Architekturübersicht](#1-architekturübersicht)
2. [Excel-Format (Eingabe)](#2-excel-format-eingabe)
3. [DienstplanParser — Excel einlesen](#3-dienstplanparser--excel-einlesen)
4. [_DienstplanPane — Einzelne Anzeigeeinheit](#4-_dienstplanpane--einzelne-anzeigeeinheit)
5. [DienstplanWidget — Hauptcontainer](#5-dienstplanwidget--hauptcontainer)
6. [ExportDialog — Word-Export-Dialog](#6-exportdialog--word-export-dialog)
7. [StaerkemeldungExport — Word erzeugen](#7-staerkemeldungexport--word-erzeugen)
8. [Sonderfälle und Spezialregeln](#8-sonderfälle-und-spezialregeln)
9. [Farbkodierung in der Tabelle](#9-farbkodierung-in-der-tabelle)
10. [Changelog / Entwicklungshistorie](#10-changelog--entwicklungshistorie)
11. [Offene Punkte](#11-offene-punkte)

---

## 1. Architekturübersicht

```
DienstplanWidget (QWidget)
│
├── QTreeView  ← linke Seite: Dateibaum (04_Tagesdienstpläne)
│
└── QSplitter  ← rechte Seite: bis zu 4 Panes nebeneinander
    ├── _DienstplanPane [0]
    ├── _DienstplanPane [1]
    ├── _DienstplanPane [2]
    └── _DienstplanPane [3]
```

**Datenfluss:**
```
Excel-Datei (.xlsx)
    → DienstplanParser.parse()       → display_result (für Anzeige, MIT Ausschlüssen aufgelöst)
    → DienstplanParser.parse()       → export_result  (für Export, OHNE Ausschlüsse)
        → _DienstplanPane.load()
            → _render_table_parsed()   (Tabelle befüllen)
            → ExportDialog             (auf Knopfdruck)
                → StaerkemeldungExport.export()  → .docx
```

---

## 2. Excel-Format (Eingabe)

Die Excel-Datei hat **keine feste Spaltenposition**. Der Parser sucht
die Header-Zeile **dynamisch** innerhalb der ersten 20 Zeilen.

### Pflicht-Spalten

| Spaltenname | Inhalt | Beispiel |
|---|---|---|
| `NAME` | Nachname, Vorname | `Müller, Max` |
| `DIENST` | Dienst-Kürzel | `T`, `N`, `DT`, `KRANK` … |

### Optionale Spalten

| Spaltenname | Inhalt | Beispiel |
|---|---|---|
| `BEGINN` | Startzeit | `06:00`, `datetime`, `0600` |
| `ENDE` | Endzeit | `14:00`, `datetime`, `1400` |

### Namensformate (beide werden akzeptiert)

| Format | Beispiel | Ergebnis |
|---|---|---|
| `Nachname, Vorname` | `Müller, Max` | vorname=Max, nachname=Müller |
| `Vorname Nachname` | `Max Müller` | vorname=Max, nachname=Müller |
| Doppelname | `Müller-Schmidt, Anna` | wird als ein Nachname behandelt |

### Datumsformate im Dateinamen / in der Datei (akzeptiert)

Der Parser versucht das Datum aus mehreren Quellen zu extrahieren:

1. **Zellwert als `datetime`-Objekt** (openpyxl liefert das direkt)
2. **String-Muster im Zellinhalt** (erste gefundene Übereinstimmung):

| Muster | Beispiel | Intern gespeichert als |
|---|---|---|
| `DD.MM.YYYY` | `22.02.2026` | `22.02.2026` |
| `DD.MM.YY` | `22.02.26` | `22.02.2026` (2000+ angenommen) |
| `D.M.YYYY` | `5.2.2026` | `05.02.2026` |
| `D.M.YY` | `5.2.26` | `05.02.2026` |
| `DD/MM/YYYY` | `22/02/2026` | `22.02.2026` |
| `DD-MM-YYYY` | `22-02-2026` | `22.02.2026` |
| `YYYY-MM-DD` | `2026-02-22` | `22.02.2026` |
| `YYYYMMDD` | `20260222` | `22.02.2026` |
| `DD MM YYYY` | `22 02 2026` | `22.02.2026` |

> Alle erkannten Daten werden normalisiert auf **`DD.MM.YYYY`** gespeichert.  
> Zweistellige Jahreszahlen: `00`–`99` → `2000`–`2099`.

---

## 3. DienstplanParser — Excel einlesen

**Datei:** `functions/dienstplan_parser.py`

### Klassenattribute

```python
class DienstplanParser:
    BETREUER_KATEGORIEN = ['T', 'T10', 'N', 'N10', 'NF', 'FB1', 'FB2', 'FB']
    DISPO_KATEGORIEN    = ['DT', 'DT3', 'DN', 'DN3', 'D']
    STILLE_DIENSTE      = frozenset({'R', 'B1', 'B2'})   # ignoriert, keine Warnung
    AUSGESCHLOSSENE_VOLLNAMEN = frozenset({'lars peters'}) # fix ausgeschlossen im Export
```

### Konstruktor

```python
def __init__(self, excel_path: str, alle_anzeigen: bool = False):
```

- `alle_anzeigen=False` → Ausschlüsse werden angewendet (für Export)
- `alle_anzeigen=True` → alle Personen werden zurückgegeben (für Anzeige)

### `parse()` — Rückgabe-Dict

```python
{
    'success':            bool,
    'betreuer':           list[dict],   # Betreuer-Einträge
    'dispo':              list[dict],   # Dispo-Einträge
    'kranke':             list[dict],   # Krankmeldungen
    'error':              str | None,
    'unbekannte_dienste': list[str],    # Kürzel, die nicht erkannt wurden
    'datum':              str | None,   # z.B. "22.02.2026"
    'column_map':         dict,         # gefundene Spaltenindizes
    'excel_path':         str,          # absoluter Pfad
}
```

### Person-Dict-Struktur

```python
{
    'vorname':          str,        # "Max"
    'nachname':         str,        # "Müller"
    'vollname':         str,        # "Max Müller"
    'anzeigename':      str,        # Nachname (+ Initial bei Duplikat: "Müller MA")
    'dienst_kategorie': str | None, # "T", "DT3", "NF", …
    'start_zeit':       str | None, # "06:00"
    'end_zeit':         str | None, # "14:00"
    'schicht_typ':      str | None, # "tagdienst_vormittag" etc.
    'ist_dispo':        bool,
    'ist_krank':        bool,
    'ist_bulmorfahrer': bool,       # gelbe Zellfarbe
    'zeilen_farbe':     str | None, # 'gray' oder None
    'dienst_farbe':     str | None, # 'yellow' oder None
    'dienst_farbe_hex': str | None, # hex z.B. "FFFFFF00"
    'excel_row':        int | None, # 1-basierte Zeilennummer in der xlsx
}
```

### `_find_datum()` — Datum aus Datei ermitteln

Durchsucht alle Zeilen **oberhalb der Header-Zeile** auf Datumswerte:

```python
def _find_datum(self) -> Optional[str]:
    for row_idx in range(1, header_row):
        for cell in self.sheet[row_idx]:
            # 1. datetime-Objekt → direkt formatieren
            if isinstance(val, datetime):
                return val.strftime('%d.%m.%Y')
            # 2. String → Regex-Suche nach Datumsmustern
            if isinstance(val, str):
                # DD.MM.YYYY  /  D.M.YY  /  DD/MM/YYYY  /  YYYY-MM-DD  etc.
                ...
```

### `_parse_time()` — Zeitwert parsen

Akzeptiert `datetime`, `time`, und Strings:

| Eingabe | Beispiel | Ergebnis |
|---|---|---|
| `datetime` | openpyxl-Objekt | `"06:00"` |
| `time` | openpyxl-Objekt | `"06:00"` |
| String `HH:MM` | `"06:00"` | `"06:00"` |
| String `HHMM` | `"0600"` | `"06:00"` |

### `_ermittle_schichttyp()` — Schichtkategorie

| `schicht_typ` | Startzeit |
|---|---|
| `tagdienst_vormittag` | 05:00 – 11:59 |
| `tagdienst_nachmittag` | 12:00 – 18:59 |
| `nachtschicht_frueh` | 19:00 – 23:59 |
| `nachtschicht_spaet` | 00:00 – 04:59 |

### `_generate_display_names()` — Doppelte Nachnamen

Bei Namens-Duplikaten werden die ersten **zwei Vorname-Buchstaben** (Groß+Klein) angehängt:

```
Müller, Max   →  "Müller Ma"
Müller, Maria →  "Müller Ma" → Konflikt nur wenn beide gleich; Reihenfolge aus Excel
```

---

## 4. _DienstplanPane — Einzelne Anzeigeeinheit

**Klasse:** `_DienstplanPane(QWidget)` in `gui/dienstplan.py`

### Layout-Struktur

```
_DienstplanPane
│
├── Header-Leiste (blau, 28px)
│   ├── _export_radio  (Radiobutton "Für Export auswählen")
│   └── _title_lbl     (Dateiname nach dem Laden)
│
├── _datum_lbl         (Datum aus Excel, sichtbar wenn gefunden)
│
├── _table             (QTableWidget — Hauptansicht)
│
└── Footer-Leiste (grau)
    ├── _row_count_lbl  (Zählzeile: "3 Tagdienst | 1 Nachtdienst | 2 Krank")
    └── _status_lbl     (Info-/Fehlermeldungen)
```

### `load(path: str) → bool`

1. Prüft `_check_excel_locked(path)` — Excel-Sperre erkannt? → Fehlermeldung
2. Ruft `DienstplanParser(path, alle_anzeigen=True).parse()` → `display_result`
3. Ruft `DienstplanParser(path, alle_anzeigen=False).parse()` → `export_result`
4. Speichert beide Ergebnisse intern
5. Setzt `_title_lbl.setText(os.path.basename(path))`
6. Setzt `_datum_lbl` wenn Datum gefunden
7. Ruft `_render_table_parsed(display_result)` auf
8. Zeigt Warnung bei unbekannten Dienst-Kürzeln
9. Statuszeile: `"Geladen: 22.02.2026.xlsx"`

### `_render_table_parsed(data: dict)`

Baut die Tabelle auf. Spalten: `Kategorie | Name | Dienst | Von | Bis`

**Zeilengruppen (in dieser Reihenfolge):**

| Gruppe | Dienst-Kategorien | Trennzeile davor |
|---|---|---|
| Tagdienst | Kürzel in `_TAG_DIENSTE` | Nein (erste) |
| Nachtdienst | Kürzel in `_NACHT_DIENSTE` | Ja (gelb) |
| Sonstige | alle anderen Kürzel | Ja (hellgrün) |
| Krank | `KRANK`, `K` | Ja (rosa) |

**Kategorie-Erkennung:**

```python
STATIONSLEITUNG = {'lars peters'}   # lowercase-Vergleich

for kat, liste in (('Dispo', data['dispo']), ('Betreuer', data['betreuer'])):
    for p in liste:
        name_lower = p['anzeigename'].strip().lower()
        effekt_kat = 'Stationsleitung' if name_lower in STATIONSLEITUNG else kat
        ...
```

**Farben pro Kategorie:**

| Kategorie | Hintergrund | Textfarbe |
|---|---|---|
| `Dispo` | `#dce8f5` (hellblau) | `#0a5ba4` (dunkelblau) |
| `Betreuer` | `#ffffff` (weiß) | `#1a1a1a` (fast schwarz) |
| `Stationsleitung` | `#fff8e1` (zartes Gelb) | `#7a5000` (dunkelbraun) |
| `Krank` | `#fce8e8` (rosa) | `#bb0000` (dunkelrot) |

**Zählzeile (Footer):**

```python
teile = []
if tag_n:   teile.append(f'{tag_n} Tagdienst')
if nacht_n: teile.append(f'{nacht_n} Nachtdienst')
if sonst_n: teile.append(f'{sonst_n} Sonstige')
if krank_n: teile.append(f'{krank_n} Krank')
self._row_count_lbl.setText('  |  '.join(teile) or '0 Eintraege')
```

Beispielausgabe: `3 Tagdienst  |  1 Nachtdienst  |  2 Sonstige  |  1 Krank`

---

## 5. DienstplanWidget — Hauptcontainer

**Klasse:** `DienstplanWidget(QWidget)` in `gui/dienstplan.py`

### 4-Pane-Layout

- Bis zu **4 Dienstpläne nebeneinander** in einem `QSplitter`
- Panes werden erst bei Bedarf befüllt (leere Panes zeigen Platzhaltertext)
- **Export-Pane:** Ein Radiobutton pro Pane wählt aus, welcher Plan exportiert wird
  - Blauer Rahmen zeigt die aktive Export-Pane an
  - Index gespeichert in `self._export_pane_idx`

### Dateibaum (linke Seite)

- `QTreeView` + `QFileSystemModel`
- Stammordner: aus `config.py` → `DIENSTPLAN_DIR`
- Zeigt nur `.xlsx`-Dateien an
- Doppelklick → `_on_tree_activated()` → `pane.load(path)`
- Lädt in die **nächste freie Pane** (reihum, 0–3)

### Statische Methoden

```python
@staticmethod
def _check_excel_locked(path: str) -> None:
    """Prüft ob Excel die Datei geöffert hat (Lock-Datei ~$filename.xlsx).
    Wirft IOError wenn gesperrt."""

@staticmethod
def _backup_excel_save(path: str) -> None:
    """Kopiert die Excel-Datei in Backup Data/excel_saves/ mit Timestamp."""
```

### `_word_exportieren()`

```python
def _word_exportieren(self):
    pane = self._export_pane()          # aktive Export-Pane
    if pane.parsed_data is None:
        QMessageBox.information(...)    # kein Dienstplan geladen
        return
    dlg = ExportDialog(parsed_data=pane.parsed_data, parent=self)
    if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.result:
        return
    params = dlg.result
    exporter = StaerkemeldungExport(
        dienstplan_data           = pane.parsed_data,
        ausgabe_pfad              = params['ausgabe_pfad'],
        von_datum                 = params['von_datum'],
        bis_datum                 = params['bis_datum'],
        pax_zahl                  = params['pax_zahl'],
        ausgeschlossene_vollnamen = params['ausgeschlossene_vollnamen'],
    )
    pfad, warnungen = exporter.export()
    ...
```

> **Wichtig:** Es darf nur **eine** Definition dieser Methode in der Klasse existieren.
> Früher war ein Bug durch duplizierte alte Tab-Code-Methoden verursacht worden
> (alte Methode rief `self._active_pane()` auf, das nicht existiert).

---

## 6. ExportDialog — Word-Export-Dialog

**Klasse:** `ExportDialog(QDialog)` in `gui/dienstplan.py`  
Wird von `DienstplanWidget._word_exportieren()` geöffnet.

### Felder im Dialog

| Feld | Widget | Beschreibung |
|---|---|---|
| Von | `QDateEdit` | Startdatum des Zeitraums |
| Bis | `QDateEdit` | Enddatum des Zeitraums |
| PAX-Zahl | `QSpinBox` (0–99999) | Passagierzahl |
| Speicherort | `QPushButton` + Label | Dateipfad für .docx |
| Sonderdienste | `QScrollArea` + Checkboxen | Optionaler Ausschluss einzelner Personen |

### Standardpfad-Logik

```python
_STAERKEMELDUNG_DIR = r"C:\Users\DRKairport\OneDrive - ...\06_Stärkemeldung"

def _make_default_pfad(self) -> str:
    """Generiert Dateinamen aus Von-Bis-Datum."""
    von_str = "22.02.2026"
    bis_str = "28.02.2026"
    # Gleicher Tag:
    name = "Staerkemeldung 22.02.2026.docx"
    # Zeitraum:
    name = "Staerkemeldung 22.02.2026 - 28.02.2026.docx"
    return os.path.join(_STAERKEMELDUNG_DIR, name)
```

- Beim Öffnen des Dialogs wird **sofort** ein Standardpfad generiert und angezeigt
- Ändert sich das Von- oder Bis-Datum → Dateiname wird **automatisch aktualisiert**
- Solange kein manueller Pfad gewählt wurde (`_pfad_auto = True`)
- Nach manuellem „Speicherort wählen" → `_pfad_auto = False` → keine Auto-Updates mehr
- Wenn `_STAERKEMELDUNG_DIR` nicht existiert → Fallback auf `~/` (Home-Ordner)

### PAX-Zahl = 0 Warnung

Beim Klick auf „Exportieren" mit PAX = 0:

```python
ret = QMessageBox.warning(
    self, "PAX-Zahl ist 0",
    "Die PAX-Zahl ist aktuell 0.\n\n"
    "Bitte tragen Sie die Anzahl der Passagiere ein,\n"
    "oder klicken Sie auf 'Trotzdem exportieren'.",
    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Ignore,
    QMessageBox.StandardButton.Ok,          # Standard = OK (zurück)
)
if ret != QMessageBox.StandardButton.Ignore:
    self._pax.setFocus()
    self._pax.selectAll()    # Cursor direkt ins PAX-Feld
    return                   # Dialog bleibt offen
# bei Ignore → Export wird trotzdem ausgeführt
```

### Sonderdienst-Checkboxen

Personen mit unbekannten Dienst-Kürzeln (nicht in `BETREUER_KATEGORIEN` oder `DISPO_KATEGORIEN`) erscheinen 
als ankreuzbare Checkboxen:

- Vorbelegt anhand der Einstellungen (`get_ausgeschlossene_namen()`)
- Haken = Person **wird vom Export ausgeschlossen**
- Übergabe als `ausgeschlossene_vollnamen: set[str]` an `StaerkemeldungExport`

### Rückgabe (`dlg.result`)

```python
{
    'von_datum':                datetime,
    'bis_datum':                datetime,
    'pax_zahl':                 int,
    'ausgabe_pfad':             str,
    'ausgeschlossene_vollnamen': set[str],   # vollname.lower()
}
```

---

## 7. StaerkemeldungExport — Word erzeugen

**Datei:** `functions/staerkemeldung_export.py`

### Konstruktor

```python
def __init__(self,
             dienstplan_data:           dict,
             ausgabe_pfad:              str,
             von_datum:                 datetime,
             bis_datum:                 datetime,
             pax_zahl:                  int = 0,
             ausgeschlossene_vollnamen: set = None):
```

### `export() → tuple[str, list[str]]`

Gibt `(dateipfad, warnungen)` zurück.

**Dokumentstruktur:**

1. **DRK-Kopfzeile** (`_add_header`)
   - 1×2-Tabelle: Links DRK-Logo (`Daten/Email/Logo.jpg`), rechts Organisationstext
   - Logo-Pfad: relativ zu `BASE_DIR` → `Nesk3/Daten/Email/Logo.jpg`
   - Trennlinie nach der Kopfzeile

2. **DRK-Fußzeile** (`_add_footer`)
   - Zentriert, 9 pt, grau
   - Text: `Telefon: +49 220340 – 2323  |  email: flughafen@drk-koeln.de  |  Stationsleitung: Lars Peters`

3. **Datumszeile** (fett)
   - Einzel: `Zeitraum: 22.02.2026`
   - Bereich: `Zeitraum: 22.02.2026 bis 28.02.2026`

4. **Disposition-Abschnitt**
   - Überschrift „Disposition" (fett, 12 pt)
   - Kranke + ausgeschlossene Personen herausgefiltert
   - Sortiert nach Startzeit
   - `_add_dienst_gruppe()` aufrufen

5. **Betreuer-Abschnitt**
   - Überschrift „Behindertenbetreuer" (fett, 12 pt)
   - Gleicher Filter + Sortierung
   - `_add_dienst_gruppe()` aufrufen

6. **PAX-Zahl** (zentriert, fett, 12 pt)
   - Format: `- 150 -`

7. `doc.save(ausgabe_pfad)`

### `_add_dienst_gruppe()` — Zeitgruppen-Ausgabe

Mitarbeiter werden **nach Uhrzeit gruppiert**:

```
06:00 bis 14:00    Müller / Schmidt / Meier
14:00 bis 22:00    Weber / Hoffmann
```

- Tabulator-Stop: `w:pos = 2550` Twips (= 4,5 cm)
- Hanging-Indent: erste Zeile 0, Folgezeilen 4,5 cm
- Schriftgröße: 11 pt

---

## 8. Sonderfälle und Spezialregeln

### Stationsleitung — Lars Peters

Lars Peters ist **Stationsleitung**, kein Betreuer oder Dispo.

```python
STATIONSLEITUNG = {'lars peters'}   # in _render_table_parsed (dienstplan.py)
```

- Erkannt über `anzeigename.strip().lower() in STATIONSLEITUNG`
- Darstellung: zartes Gelb + dunkelbrauner Text (statt Betreuer-weiß)
- Erscheint in der **Anzeige-Tabelle** mit Kategorie `Stationsleitung`
- Im **Word-Export** wird er **nicht separat hervorgehoben**
  (da in `AUSGESCHLOSSENE_VOLLNAMEN` in `DienstplanParser`)
- Um weitere Personen als Stationsleitung zu kennzeichnen:
  `STATIONSLEITUNG = {'lars peters', 'max mustermann'}`

### Bulmorfahrer (gelbe Zellfarbe)

Personen deren Namens- oder Dienstzelle in Excel gelb gefärbt ist
(`FFFF??` mit Blauanteil ≤ `0x4F`) → `ist_bulmorfahrer = True`

- Wird im Person-Dict gespeichert
- Aktuell keine besondere Anzeige in Nesk3 (nur gespeichert für spätere Nutzung)

### KRANK-Erkennung

Dienst-Kürzel `KRANK` oder `K` → `ist_krank = True`

- Erscheinen in eigener Gruppe mit rosa Hintergrund (`#fce8e8`) + rotem Text (`#bb0000`)
- Werden **nicht** in den Betreuer/Dispo-Abschnitt der Word-Datei aufgenommen

### Excel-Sperre (Lock-Datei)

Wenn Excel die Datei geöffnet hat, existiert eine Lock-Datei `~$dateiname.xlsx`:

```python
lock = os.path.join(os.path.dirname(path), '~$' + os.path.basename(path))
if os.path.exists(lock):
    raise IOError(f"Datei ist in Excel geöffnet: {lock}")
```

### Doppelte Nachnamen

Bei mehreren Personen mit gleichem Nachnamen werden die ersten **zwei Vorname-Buchstaben** angehängt:
`Müller` → `Müller Ma` (für Max) und `Müller Me` (für Mena).

Bei Doppelnamen (enthält `-`) wird ebenfalls Initial angehängt.

---

## 9. Farbkodierung in der Tabelle

### Trennzeilen zwischen Gruppen

| Gruppe | Farbe | Hex | Text |
|---|---|---|---|
| Nachtdienst | Gelb | `#fff3cd` | `── Nachtdienst ──` |
| Sonstige | Hellgrün | `#e8f5e9` | `── Sonstige ──` |
| Krank | Rosa | `#fce8e8` | `── Krank ──` |

### Kategoriezeilen

| Kategorie | Hintergrund | Text | Schrift |
|---|---|---|---|
| `Dispo` | `#dce8f5` | `#0a5ba4` | normal |
| `Betreuer` | `#ffffff` | `#1a1a1a` | normal |
| `Stationsleitung` | `#fff8e1` | `#7a5000` | normal |
| `Krank` | `#fce8e8` | `#bb0000` | normal |

---

## 10. Changelog / Entwicklungshistorie

### v1.0 (Initial) — Grundfunktionen

- `DienstplanParser` aus Nesk2 nach Nesk3 portiert
- `StaerkemeldungExport` aus Nesk2 nach Nesk3 portiert
- Einfache Tab-basierte GUI in `DienstplanWidget`
- Button „Word exportieren" vorhanden

### v2.0 — 4-Pane-Layout + Encoding-Fixes (Session 2)

**Änderungen:**
- Tab-Layout durch **4-Pane-Splitter** ersetzt (bis zu 4 Dienstpläne nebeneinander)
- **119+ Mojibake-Fixes** in `dienstplan.py` (UTF-8-Encoding-Problem durch PowerShell `Set-Content`)
- Export-Pane-Auswahl per Radiobutton mit blauem Rahmen

### v2.1 — Stationsleitung + Zählzeile + Word-Export-Bug-Fix (Session 3)

**Probleme behoben:**

1. **Word-Export-Button** tat nichts → Root Cause: 236 Zeilen duplizierter alter Tab-Code am Dateiende,
   der die neuen Methoden durch gleichnamige alte Methoden überschrieb.
   Die alte `_word_exportieren` rief `self._active_pane()` auf (existiert nicht mehr).
   → Fix: Duplizierter Code mit `trim.py` entfernt (Zeile 1172 als Schnittlinie).

2. **Zählzeile** zeigte `N Betreuer | M Dispo | K Krank` → jetzt:
   `X Tagdienst | Y Nachtdienst | Z Sonstige | W Krank` (nur nicht-leere Kategorien)

3. **Lars Peters** wird als `Stationsleitung` (zartes Gelb) statt als `Betreuer` dargestellt.

4. **Garbled Status-Text** `âœ... Geladen:` → bereinigt zu `Geladen: dateiname.xlsx`

5. **Dateiname im Pane-Header** wird nach dem Laden angezeigt (`_title_lbl`)

### v2.2 — ExportDialog-Verbesserungen (Session 4)

**Neue Features:**

1. **Standardpfad mit Datum**: Dateiname wird automatisch aus Von-Bis generiert:
   - Gleicher Tag: `Staerkemeldung 22.02.2026.docx`
   - Zeitraum: `Staerkemeldung 22.02.2026 - 28.02.2026.docx`
   - Aktualisiert sich live wenn Datum geändert wird (solange kein manueller Pfad)

2. **Standardordner**: Dialog öffnet direkt im Ordner `06_Stärkemeldung`:
   ```
   C:\Users\DRKairport\OneDrive - ...\06_Stärkemeldung
   ```
   Fallback: Home-Ordner (`~/`) wenn Ordner nicht existiert.

3. **PAX = 0 Warnung**: Beim Export mit PAX-Zahl 0 erscheint Warnung mit zwei Optionen:
   - OK → Dialog bleibt offen, Fokus auf PAX-Feld
   - „Trotzdem exportieren" → Export wird ausgeführt

### v2.4 — Lars-Peters-Bug-Fix + DPI-Schrift-Fix (Session 6, 22.02.2026)

**Probleme behoben:**

1. **Lars Peters zeigte „Betreuer" statt „Stationsleitung"**
   - Root Cause: `_render_table_parsed()` verglich `p.get('anzeigename', '')` (= nur Nachname `'Peters'`)
     gegen `STATIONSLEITUNG = {'lars peters'}` → Match schlug immer fehl.
   - Fix: `anzeigename` → `vollname` (= `'Lars Peters'`), sodass der Vergleich korrekt greift.
   - Datei: `gui/dienstplan.py`, Funktion `_render_table_parsed()`.

2. **Schrift auf anderen PCs kaum lesbar (EXE)**
   - Root Cause 1: `QT_AUTO_SCREEN_SCALE_FACTOR = "1"` ist eine Qt5-Variable — in Qt6/PySide6 hat
     sie keine Wirkung. Qt6 aktiviert High-DPI-Skalierung automatisch, aber der Rundungs-Policy
     `Round` (Standard) kann bei 125 % oder 150 % Windows-Skalierung Fonts zu groß/klein machen.
   - Root Cause 2: Kein globaler App-Font gesetzt → Widgets erben die OS-Standardgröße, die
     je nach Windows-Version und DPI unterschiedlich ausfallen kann.
   - Fix in `main.py`:
     ```python
     # Vor QApplication:
     QApplication.setHighDpiScaleFactorRoundingPolicy(
         Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
     )
     # Nach QApplication(...):
     app.setFont(QFont("Segoe UI", 10))  # Windows-Systemschrift, 10 pt
     ```
   - `PassThrough` gibt den echten Faktor (z. B. 1,25 oder 1,5) direkt weiter statt ihn zu
     runden → gleichmäßige, scharfe Schrift auf 100 %, 125 %, 150 %, 175 % usw.
   - `Segoe UI 10pt` ist die Windows-Systemschrift und auf allen Windows-PCs vorhanden.

> **Hinweis EXE (PyInstaller):** Wenn die EXE auf einem PC mit anderer Windows-Skalierung
> weiterhin unscharf wirkt, fehlt ein DPI-Aware-Manifest in der EXE. Abhilfe beim nächsten
> build: `--manifest manifest.xml` mit `dpiAwareness = perMonitorV2` angeben.

---

### v2.3 — Erweiterte Datumsformat-Erkennung (Session 5)

**Problem:** Nur `DD.MM.YYYY` und `YYYY-MM-DD` wurden erkannt.

**Lösung:** `_find_datum()` in `DienstplanParser` wurde erweitert. Jetzt werden erkannt:
`DD.MM.YYYY`, `DD.MM.YY`, `D.M.YYYY`, `D.M.YY`, `DD/MM/YYYY`, `DD-MM-YYYY`,
`YYYY-MM-DD`, `YYYYMMDD`, `DD MM YYYY` — alle normalisiert auf `DD.MM.YYYY`.

---

## 11. Offene Punkte

- [ ] Sollen geparste Schichten direkt in die SQLite-Datenbank übernommen werden?
- [ ] Nesk2-Verhalten: Warnung bei komplett leerem Dienstplan (0 Einträge)?
- [ ] Stationsleitung-Liste konfigurierbar machen (aktuell nur `lars peters` hardcoded)
- [ ] Bulmorfahrer-Markierung in der Anzeige-Tabelle visualisieren (aktuell nur gespeichert)
- [ ] Mehrere Excel-Dateien für einen Zeitraum zusammenführen (Multi-Export)?
- [x] DRK-Logo-Pfad: `Daten/Email/Logo.jpg` relativ zu `BASE_DIR` ✅
- [x] PAX-Zahl: Eingabefeld im Export-Dialog ✅
- [x] Warnmeldung bei unbekannten Dienst-Kürzeln ✅
- [x] Excel-Lock-Erkennung (Datei in Excel geöffnet) ✅
- [x] Backup-Funktion bei Excel-Speicherung ✅
- [x] Lars Peters → Stationsleitung (vollname statt anzeigename) ✅
- [x] DPI-Skalierung: `PassThrough`-Policy + globaler `Segoe UI 10pt` Font ✅
- [ ] EXE: DPI-Aware-Manifest (`perMonitorV2`) für PyInstaller-Build ergänzen

---

## Abhängigkeiten

```
openpyxl    >= 3.0   # Excel lesen
python-docx >= 0.8   # Word schreiben
PySide6     >= 6.5   # GUI
```

---

## Datei-Referenzen

| Datei | Klasse / Inhalt |
|---|---|
| `gui/dienstplan.py` | `ExportDialog`, `_DienstplanPane`, `DienstplanWidget` |
| `functions/dienstplan_parser.py` | `DienstplanParser` |
| `functions/staerkemeldung_export.py` | `StaerkemeldungExport` |
| `functions/settings_functions.py` | `get_ausgeschlossene_namen()` |
| `config.py` | `BASE_DIR`, `DIENSTPLAN_DIR` |

