# Funktion: Dienstplan aus Excel einlesen → Word ausgeben

## Quelle / Vorlage

Diese Funktion wird aus **Nesk2** übernommen und für Nesk3 adaptiert.
Relevante Nesk2-Dateien:
- `Nesk2/Function/dienstplan_parser.py` → Excel-Parsing
- `Nesk2/Function/staerkemeldung_export.py` → Word-Export

---

## Excel-Format (Eingabe) — wie in Nesk2

Die Excel-Datei hat **keine feste Spaltenposition**. Der Parser sucht
die Header-Zeile **dynamisch** (durchsucht die ersten 20 Zeilen):

| Spaltenname | Inhalt | Beispiel |
|---|---|---|
| `NAME` | Nachname, Vorname | Müller, Max |
| `DIENST` | Dienst-Kürzel | T / N / NF / DT / DN … |
| `BEGINN` | Startzeit | 06:00 oder datetime |
| `ENDE` | Endzeit | 14:00 oder datetime |

**Hinweise:**
- Spaltenreihenfolge ist egal — Suche erfolgt über den Spaltennamen (case-insensitive)
- Leerzeilen und Zeilen ohne gültigen Namen werden übersprungen
- Namen im Format `"Nachname, Vorname"` oder `"Vorname Nachname"`
- Zeiten als `datetime`-Objekt, `time`-Objekt oder String `HH:MM` / `HHMM`

### Dienst-Kategorien (aus Nesk2 übernommen)

| Kategorie | Kürzel |
|---|---|
| Betreuer | T, T10, N, N10, NF, FB1, FB2, FB |
| Dispo | DT, DT3, DN, DN3, D |
| Krank | KRANK, K |

### Zellfarben (werden ausgelesen)

| Farbe | Bedeutung |
|---|---|
| Gelb (`FFFF00`) | Bulmorfahrer |
| Grau (`F5F5F5`) | Zebra-Zeile (kein Sonderstatus) |

---

## Geplante Klassen / Funktionssignaturen

```python
# functions/dienstplan_parser.py  (adaptiert aus Nesk2)

class DienstplanParser:
    """
    Liest eine Excel-Datei (.xlsx) und extrahiert Dienstplan-Daten.
    Findet die Header-Zeile (NAME, DIENST, BEGINN, ENDE) automatisch.
    """

    BETREUER_KATEGORIEN = ['T', 'T10', 'N', 'N10', 'NF', 'FB1', 'FB2', 'FB']
    DISPO_KATEGORIEN    = ['DT', 'DT3', 'DN', 'DN3', 'D']

    def __init__(self, excel_path: str):
        ...

    def parse(self) -> dict:
        """
        Returns:
            {
              'success': bool,
              'betreuer': list[dict],   # Betreuer-Schichten
              'dispo':    list[dict],   # Dispo-Schichten
              'kranke':   list[dict],   # Krankmeldungen
              'error':    str | None
            }
        """
        ...


# functions/staerkemeldung_export.py  (adaptiert aus Nesk2)

class StaerkemeldungExport:
    """
    Erstellt ein Word-Dokument aus geparsten Dienstplan-Daten.
    Struktur: DRK-Kopfzeile → Zeitraum → Disposition → Betreuer → PAX-Zahl → Fußzeile
    """

    def __init__(self, dienstplan_data: dict, ausgabe_pfad: str,
                 von_datum, bis_datum, pax_zahl: int = 0):
        ...

    def export(self) -> str:
        """Erstellt Word-Datei und gibt den Dateipfad zurück."""
        ...
```

---

## Ablauf im Detail

### Phase 1: Excel parsen (`DienstplanParser.parse`)

1. `openpyxl.load_workbook(excel_path, data_only=True)` — Formeln als Werte lesen
2. Erstes Arbeitsblatt (`workbook.active`)
3. **Header-Zeile finden** (`_find_columns`):
   - Zeilen 1–20 durchsuchen
   - Suche nach Zellen mit Wert `NAME`, `DIENST`, `BEGINN`, `ENDE` (case-insensitive)
   - Speichere Spalten-Indizes als `column_map`
4. **Jede Daten-Zeile verarbeiten** (`_parse_row`):
   - Name lesen → `_parse_name()` → `{vorname, nachname}`
   - Zellfarbe prüfen → Bulmorfahrer (gelb) erkennen
   - Dienst-Kürzel lesen → Betreuer / Dispo / Krank kategorisieren
   - Zeiten parsen → `_parse_time()` → `time`-Objekt oder `None`
   - Bei Dispo-Kategorie: Zeiten auf volle Stunde abrunden
5. **Doppelte Nachnamen** → Vorname-Initial anhängen (z.B. "Müller MA")
6. Rückgabe: `{success, betreuer, dispo, kranke, error}`

### Phase 2: Word exportieren (`StaerkemeldungExport.export`)

1. `Document()` erstellen
2. **DRK-Kopfzeile** (`_add_header`):
   - 1×2-Tabelle: Links DRK-Logo (`Daten/Email/Logo.jpg`), rechts Organisations-Text
   - Logo-Pfad relativ zum Projektordner: `Nesk3/Daten/Email/Logo.jpg`
   - Trennlinie unter der Kopfzeile
3. **DRK-Fußzeile** (`_add_footer`):
   - Text zentriert, 9pt, grau: `Telefon: +49 220340 – 2323  |  email: flughafen@drk-koeln.de  |  Stationsleitung: Lars Peters`
4. **Datumsbereich** als fetter Paragraph: `Zeitraum: DD.MM.YYYY bis DD.MM.YYYY`
5. **Disposition-Abschnitt**:
   - Überschrift „Disposition" (fett)
   - Kranke + Export-Ausschlüsse rausfiltern
   - Nach Startzeit sortieren
   - `_add_dienst_gruppe()` aufrufen
6. **Betreuer-Abschnitt**:
   - Überschrift „Behindertenbetreuer" (fett)
   - Gleicher Filter + Sortierung
   - `_add_dienst_gruppe()` aufrufen
7. **PAX-Zahl** zentriert, fett: `- 150 -`
8. `doc.save(ausgabe_pfad)`

### Person-Dict-Struktur (Rückgabe von `_parse_row`)

Jede Person wird als Dict zurückgegeben:

```python
{
    'vorname':          str,        # z.B. "Max"
    'nachname':         str,        # z.B. "Müller"
    'vollname':         str,        # z.B. "Max Müller"
    'anzeigename':      str,        # Nachname (ggf. mit Initial bei Duplikat)
    'dienst_kategorie': str | None, # z.B. "T", "DT3", "NF"
    'start_zeit':       str | None, # z.B. "06:00"
    'end_zeit':         str | None, # z.B. "14:00"
    'schicht_typ':      str | None, # siehe unten
    'ist_dispo':        bool,
    'ist_krank':        bool,
    'ist_bulmorfahrer': bool,       # gelbe Zellfarbe
    'zeilen_farbe':     str | None, # 'gray' oder None
    'dienst_farbe':     str | None, # 'yellow' oder None
    'dienst_farbe_hex': str | None, # z.B. "FFFFFF00"
}
```

### Schicht-Typ-Kategorisierung (`_ermittle_schichttyp`)

| `schicht_typ` | Startzeit | Endzeit |
|---|---|---|
| `tagdienst_vormittag` | 05:00 – 09:00 | 12:00 – 15:00 |
| `tagdienst_nachmittag` | 12:00 – 15:00 | 19:00 – 22:00 |
| `nachtdienst_frueh` | 19:00 – 22:00 | 01:00 – 04:00 |
| `nachtdienst_spaet` | 22:00 – 02:00 | 06:00 – 10:00 |
| `None` | Passt in keine Kategorie | — |

### Zeitgruppen-Ausgabe (`_add_dienst_gruppe`)

Mitarbeiter werden **nach Uhrzeit gruppiert** und dann in einem Paragraph mit
**Tabulator-Stop** bei 4,5 cm ausgegeben:

```
06:00 bis 14:00    Müller / Schmidt / Meier
14:00 bis 22:00    Weber / Hoffmann
```

- Tabulator-Stop: `w:pos = 2550` (Twips = 4,5 cm)
- Hanging-Indent: erste Zeile bei 0, Folgezeilen bei 4,5 cm (Zeilenumbruch bleibt eingerückt)
- Schriftgröße: 11 pt

---

## Benötigte Bibliotheken

```
openpyxl    # Excel lesen  (bereits in requirements.txt)
python-docx # Word schreiben (bereits in requirements.txt)
```

---

## Neue Dateien in Nesk3

| Datei | Inhalt |
|---|---|
| `functions/dienstplan_parser.py` | `DienstplanParser`-Klasse |
| `functions/staerkemeldung_export.py` | `StaerkemeldungExport`-Klasse |

---

## Geplante GUI-Anbindung (Dienstplan-Tab)

- Button **„📥 Dienstplan laden"** → `QFileDialog.getOpenFileName` → `.xlsx` → `DienstplanParser`
- Ergebnis wird in der Tabelle angezeigt (Betreuer + Dispo + Kranke)
- Button **„📤 Word exportieren"** → Datumsbereich + PAX-Eingabe → `StaerkemeldungExport` → `.docx`
- Statusmeldung: „✅ Gespeichert unter: C:\..."

---

## Offene Punkte / Anpassungen gegenüber Nesk2

- [ ] Nesk2 nutzt `tkinter.messagebox` für Warnungen → in Nesk3 durch `QMessageBox` ersetzen
- [ ] Nesk2 hat eine Datenbank für Dienst-Kategorien → in Nesk3 zunächst als Konstante
- [x] DRK-Logo-Pfad: `Daten/Email/Logo.jpg` (absoluter Pfad: `Nesk3\Daten\Email\Logo.jpg`) ✅
- [ ] PAX-Zahl: Wie wird sie eingegeben? (Eingabefeld im Dialog oder fester Wert)
- [ ] Sollen die geparsten Schichten direkt in die SQLite-DB übernommen werden?
