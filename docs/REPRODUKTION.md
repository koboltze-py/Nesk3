# Nesk3 – Reproduktionsprotokoll

**Stand:** 26.02.2026  
**Ziel:** Vollständige Neuerstellung der Nesk3-Anwendung auf einem neuen System

---

## Voraussetzungen

| Komponente | Version | Hinweis |
|-----------|---------|---------|
| Python | 3.13+ | App ist auf 3.13 entwickelt |
| PySide6 | aktuell | GUI-Framework |
| openpyxl | aktuell | Excel-Lesen/Schreiben |
| python-docx | aktuell | Word-Export |
| win32com (pywin32) | aktuell | Outlook-Integration (optional) |
| SQLite | 3.x | Eingebaut in Python |

```powershell
pip install PySide6 openpyxl python-docx pywin32
```

---

## 1. Projektstruktur anlegen

```
Nesk3/
├── main.py
├── config.py
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── dashboard.py
│   ├── dienstplan.py
│   ├── aufgaben.py
│   ├── aufgaben_tag.py
│   ├── sonderaufgaben.py
│   ├── uebergabe.py
│   ├── fahrzeuge.py
│   ├── code19.py
│   ├── mitarbeiter.py
│   ├── einstellungen.py
│   └── checklisten.py
│
├── functions/
│   ├── __init__.py
│   ├── dienstplan_parser.py
│   ├── dienstplan_functions.py
│   ├── emobby_functions.py
│   ├── fahrzeug_functions.py
│   ├── mail_functions.py
│   ├── mitarbeiter_functions.py
│   ├── settings_functions.py
│   ├── staerkemeldung_export.py
│   └── uebergabe_functions.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── migrations.py
│   └── models.py
│
├── backup/
│   ├── __init__.py
│   └── backup_manager.py
│
├── Daten/
│   └── E-Mobby/
│       └── mobby.txt         ← E-Mobby-Fahrerliste (ein Name pro Zeile)
│
├── database SQL/
│   └── nesk3.db              ← wird automatisch erstellt
│
└── docs/
    ├── FUNKTIONEN.md
    └── REPRODUKTION.md
```

---

## 2. Datenbank-Setup

Die Datenbank wird beim ersten Start automatisch angelegt via `database/migrations.py`.

### `database/connection.py`
```python
import sqlite3
from pathlib import Path
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
```

### `database/migrations.py`
Erstellt beim App-Start alle benötigten Tabellen:
```python
from database.connection import get_connection

def run_migrations():
    conn = get_connection()
    c = conn.cursor()
    # Tabellen anlegen (CREATE TABLE IF NOT EXISTS)
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS mitarbeiter (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, funktion TEXT, qualifikationen TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS fahrzeuge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, zuletzt_geaendert TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS uebergabe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typ TEXT, beginn TEXT, ende TEXT,
        besonderheiten TEXT, erstellt_am TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS dienstplan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT, name TEXT, kuerzel TEXT,
        von TEXT, bis TEXT, ist_dispo INTEGER
    )""")
    conn.commit()
    conn.close()
```

---

## 3. Konfiguration (`config.py`)

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DB_PATH  = BASE_DIR / "database SQL" / "nesk3.db"
SHARED_DIR = BASE_DIR.parent.parent  # OneDrive-Stammordner
```

---

## 4. Einstiegspunkt (`main.py`)

```python
import sys
from PySide6.QtWidgets import QApplication
from database.migrations import run_migrations
from gui.main_window import MainWindow

def main():
    run_migrations()
    app = QApplication(sys.argv)
    app.setApplicationName("Nesk3")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

## 5. Hauptfenster (`gui/main_window.py`)

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtGui import QFont

NAV_ITEMS = [
    ("🏠", "Dashboard",      0),
    ("📅", "Dienstplan",     1),
    ("📋", "Aufgaben Nacht", 2),
    ("📋", "Aufgaben Tag",   3),
    ("🔧", "Sonderaufgaben", 4),
    ("📝", "Übergabe",       5),
    ("🚗", "Fahrzeuge",      6),
    ("🕐", "Code 19",        7),
    ("👥", "Mitarbeiter",    8),
    ("⚙️",  "Einstellungen",  9),
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Linke Navigation
        nav = QWidget()
        nav.setFixedWidth(160)
        nav_layout = QVBoxLayout(nav)
        # ... Buttons aus NAV_ITEMS ...

        # Rechter Stack
        self._stack = QStackedWidget()
        # ... Widgets hinzufügen ...

        layout.addWidget(nav)
        layout.addWidget(self._stack)
```

---

## 6. Section: E-Mobby Fahrer

### `functions/emobby_functions.py` aufbauen

```python
import json
from pathlib import Path
from config import BASE_DIR

_TXT_PATH     = Path(BASE_DIR) / "Daten" / "E-Mobby" / "mobby.txt"
_SETTINGS_KEY = "emobby_fahrer"

def _names_from_txt() -> list[str]:
    if not _TXT_PATH.exists():
        return []
    names = []
    for line in _TXT_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names

def get_emobby_fahrer() -> list[str]:
    """Merged TXT + DB, synct neue TXT-Einträge → DB."""
    from functions.settings_functions import get_setting, set_setting
    txt_names = _names_from_txt()
    db_raw = get_setting(_SETTINGS_KEY, "")
    try:
        db_names = json.loads(db_raw) if db_raw else []
    except Exception:
        db_names = []
    # Neue TXT-Namen in DB eintragen
    changed = False
    for n in txt_names:
        if n not in db_names:
            db_names.append(n)
            changed = True
    if changed:
        set_setting(_SETTINGS_KEY, json.dumps(db_names, ensure_ascii=False))
    return db_names

def is_emobby_fahrer(name: str) -> bool:
    """Case-insensitiver Substring-Match."""
    fahrer = get_emobby_fahrer()
    name_lower = name.lower()
    return any(f.lower() in name_lower or name_lower in f.lower() for f in fahrer)

def add_emobby_fahrer(name: str) -> bool:
    """Fügt Namen zur DB-Liste hinzu. Returns False wenn bereits vorhanden."""
    from functions.settings_functions import get_setting, set_setting
    db_raw = get_setting(_SETTINGS_KEY, "")
    try:
        db_names = json.loads(db_raw) if db_raw else []
    except Exception:
        db_names = []
    if name in db_names:
        return False
    db_names.append(name)
    set_setting(_SETTINGS_KEY, json.dumps(db_names, ensure_ascii=False))
    return True
```

### `Daten/E-Mobby/mobby.txt` – Format
```
# Kommentarzeilen werden ignoriert (beginnen mit #)
Bouladhne
Ormaba
Dobrani
... (ein Nachname pro Zeile)
```

---

## 7. Dienstplan-Parser – Aufbau

### `functions/dienstplan_parser.py` – Grundstruktur

```python
import openpyxl
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Mitarbeiter:
    name: str
    kuerzel: str
    von: str
    bis: str
    ist_dispo: bool = False
    ist_krank: bool = False
    krank_schicht_typ: str = ""      # tagdienst / nachtdienst / sonderdienst
    krank_abgeleiteter_dienst: str = ""

class DienstplanParser:
    def parse(self, xlsx_path: str) -> list[Mitarbeiter]:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        result = []
        aktueller_abschnitt = "betreuer"  # dispo / betreuer

        for row in ws.iter_rows(values_only=True):
            abschnitt = self._detect_abschnitt_header(list(row))
            if abschnitt:
                aktueller_abschnitt = abschnitt
                continue
            # Name-Spalte auslesen, Dienst, Zeiten...
            # ...
        return result

    def _detect_abschnitt_header(self, row_list) -> Optional[str]:
        for cell in row_list:
            if cell and "dispo" in str(cell).lower():
                return "dispo"
            if cell and any(w in str(cell).lower() for w in ["stamm", "betreuer"]):
                return "betreuer"
        return None
```

---

## 8. E-Mobby in Sonderaufgaben

### Combo-Logik in `_add_aufgabe_row()`

```python
def _add_aufgabe_row(self, grid, name, row, nur_bulmor=False):
    is_emobby = (name == "E-mobby Check")

    for schicht in ("tag", "nacht"):
        is_tag = (schicht == "tag")
        if nur_bulmor:
            mitarbeiter = self._tag_bulmor if is_tag else self._nacht_bulmor
        elif is_emobby:
            mitarbeiter = self._tag_emobby if is_tag else self._nacht_emobby
        else:
            mitarbeiter = self._tag_mitarbeiter if is_tag else self._nacht_mitarbeiter

        combo = QComboBox()
        if mitarbeiter:
            combo.addItems(["— bitte wählen —"] + mitarbeiter)
        elif is_emobby and self._dienstplan_geladen:
            combo.addItems(["⚠ Kein E-Mobby-Fahrer auf dieser Schicht – bitte prüfen!"])
            combo.setStyleSheet("QComboBox { color: #cc6600; font-weight: bold; }")
        else:
            combo.addItems(["— Dienstplan laden —"])
```

---

## 9. Übergabe: Automatisches Zeitbefüllen

```python
def _neues_protokoll(self, typ: str):
    # typ = "tagdienst" oder "nachtdienst"
    if typ == "tagdienst":
        self._f_beginn.setText("07:00")
        self._f_ende.setText("19:00")
    else:
        self._f_beginn.setText("19:00")
        self._f_ende.setText("07:00")
    # Felder freischalten, Formular leeren...
```

---

## 10. Code-19 Taschenuhr (`_PocketWatchWidget`)

```python
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen, QFont
import datetime

class _PocketWatchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 300)
        self._swing_t   = 0.0
        self._swing_angle = 0.0
        self._blink_on  = True

        self._swing_timer = QTimer(self)
        self._swing_timer.timeout.connect(self._swing_step)
        self._swing_timer.start(25)   # ~40 FPS

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)  # jede Sekunde

    def _swing_step(self):
        self._swing_t += 0.07
        self._swing_angle = 14.0 * math.sin(self._swing_t)
        self.update()

    def _tick(self):
        self._blink_on = not self._blink_on
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Pivot oben-mitte
        p.translate(120, 40)
        p.rotate(self._swing_angle)
        p.translate(-120, -40)
        # Uhr-Zentrum
        cx, cy = 120, 170
        # Gehäuse zeichnen (Radial-Gradient Gold)
        grad = QRadialGradient(cx, cy, 90)
        grad.setColorAt(0, QColor("#FFD700"))
        grad.setColorAt(1, QColor("#8B6914"))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - 85, cy - 85, 170, 170)
        # Zifferblatt, Zeiger, röm. Ziffern...
        now = datetime.datetime.now()
        # ...
        p.end()
```

---

## 11. Einstellungen: E-Mobby GroupBox

```python
from PySide6.QtWidgets import QGroupBox, QListWidget, QLineEdit, QPushButton

grp_emobby = QGroupBox("🛵 E-Mobby Fahrer")
self._emobby_list  = QListWidget()
self._emobby_input = QLineEdit()
self._emobby_input.setPlaceholderText("Nachname eingeben …")
self._emobby_input.returnPressed.connect(self._add_emobby_entry)

btn_add = QPushButton("+ Hinzufügen")
btn_add.clicked.connect(self._add_emobby_entry)

btn_rem = QPushButton("🗑 Entfernen")
btn_rem.clicked.connect(self._remove_emobby_entry)

def _load_emobby_list(self):
    from functions.emobby_functions import get_emobby_fahrer
    self._emobby_list.clear()
    for n in get_emobby_fahrer():
        self._emobby_list.addItem(n)

def _add_emobby_entry(self):
    name = self._emobby_input.text().strip()
    if not name:
        return
    from functions.emobby_functions import add_emobby_fahrer
    if add_emobby_fahrer(name):
        self._emobby_input.clear()
        self._load_emobby_list()

def _remove_emobby_entry(self):
    selected = self._emobby_list.currentItem()
    if not selected:
        return
    import json
    from functions.settings_functions import get_setting, set_setting
    db_names = json.loads(get_setting("emobby_fahrer", "[]"))
    db_names.remove(selected.text())
    set_setting("emobby_fahrer", json.dumps(db_names, ensure_ascii=False))
    self._load_emobby_list()
```

---

## 12. App starten

```powershell
cd "...\Nesk\Nesk3"
python3.13 main.py
```

### Erste Inbetriebnahme Checkliste
- [ ] Python 3.13+ installiert
- [ ] `pip install PySide6 openpyxl python-docx pywin32`
- [ ] `Daten/E-Mobby/mobby.txt` mit Fahrernamen befüllt
- [ ] App starten → DB wird automatisch erstellt
- [ ] Einstellungen öffnen → Pfade zu Dienstplan-Excel, Sonderaufgaben, AOCC, Code-19 eintragen
- [ ] Dienstplan laden → ersten Dienstplan importieren
