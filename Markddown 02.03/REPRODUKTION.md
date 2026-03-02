# Nesk3 – Reproduktionsprotokoll

**Stand:** 02.03.2026 – v3.0.0  
**Ziel:** Vollständige Neuerstellung der Nesk3-Anwendung auf einem neuen System

---

## Voraussetzungen

| Komponente | Version | Hinweis |
|-----------|---------|---------|
| Python | 3.13+ | App ist auf 3.13 entwickelt |
| PySide6 | aktuell | GUI-Framework |
| openpyxl | aktuell | Excel-Lesen/Schreiben |
| python-docx | aktuell | Word-Export + Mitarbeiter-Dokumente |
| win32com (pywin32) | aktuell | Outlook-Integration (optional) |
| SQLite | 3.x | Eingebaut in Python |

```powershell
pip install PySide6 openpyxl python-docx pywin32
```

### Windows Long Path Limit
Falls PySide6 in einem `.venv` bei sehr langem Pfad nicht installiert werden kann:
1. Aktiviere „Long Path Support" in Windows (Gruppenrichtlinien oder Registry)
2. **Oder:** Nutze das System-Python direkt und trage in `.vscode/settings.json` ein:
   ```json
   {
     "python.defaultInterpreterPath": "C:/Users/.../python3.13.exe"
   }
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
│   ├── mitarbeiter_dokumente.py      ← NEU v3.0.0
│   ├── dienstplan.py
│   ├── aufgaben.py
│   ├── aufgaben_tag.py
│   ├── sonderaufgaben.py
│   ├── uebergabe.py
│   ├── fahrzeuge.py
│   ├── code19.py
│   ├── mitarbeiter.py
│   ├── einstellungen.py
│   ├── checklisten.py
│   ├── dokument_browser.py
│   └── hilfe_dialog.py
│
├── functions/
│   ├── __init__.py
│   ├── dienstplan_parser.py
│   ├── dienstplan_functions.py
│   ├── emobby_functions.py
│   ├── fahrzeug_functions.py
│   ├── mail_functions.py
│   ├── mitarbeiter_functions.py
│   ├── mitarbeiter_dokumente_functions.py  ← NEU v3.0.0
│   ├── settings_functions.py
│   ├── staerkemeldung_export.py
│   └── uebergabe_functions.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── models.py
│   └── migrations.py
│
├── backup/
│   └── backup_manager.py
│
└── Daten/
    ├── Mitarbeiter Vorlagen/
    │   └── Kopf und Fußzeile/
    │       └── Stärkemeldung 31.01.2026 bis 01.02.2026.docx
    └── Mitarbeiterdokumente/
        ├── Stellungnahmen/
        ├── Bescheinigungen/
        ├── Dienstanweisungen/
        ├── Abmahnungen/
        ├── Lob & Anerkennung/
        └── Sonstiges/
```

---

## 2. Datenbank initialisieren

Die Datenbank wird beim ersten Start automatisch erstellt und migriert.  
Tabellen werden in `database/migrations.py` über `run_migrations()` angelegt.

```python
from database.migrations import run_migrations
run_migrations()
```

Wichtige Tabellen:
- `mitarbeiter`
- `fahrzeuge`, `fahrzeug_status`, `fahrzeug_schaeden`, `fahrzeug_termine`
- `uebergabe_protokolle`
- `settings`

---

## 3. Mitarbeiter-Dokumente einrichten

### Vorlage bereitstellen
Die DRK-Kopf-/Fußzeile-Vorlage muss unter folgendem Pfad liegen:
```
Daten/Mitarbeiter Vorlagen/Kopf und Fußzeile/Stärkemeldung 31.01.2026 bis 01.02.2026.docx
```

Ohne diese Datei werden Dokumente ohne DRK-Kopf-/Fußzeile erstellt (Fallback: leeres Dokument).

### Ausgabe-Ordner
Werden beim ersten Start automatisch angelegt durch `sicherungsordner()` in  
`functions/mitarbeiter_dokumente_functions.py`.

---

## 4. Anwendung starten

```powershell
python main.py
```

Oder über die VS Code Task „Nesk3 starten":
```json
{
    "label": "Nesk3 starten",
    "type": "shell",
    "command": "python main.py"
}
```

---

## 5. Wichtige Konfigurationspfade (`config.py`)

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Nesk3-Ordner
DB_PATH  = os.path.join(BASE_DIR, "nesk3.db")
```

Alle Pfade (Dienstplan-Excel, Word-Export-Ziel etc.) werden in der DB-Tabelle `settings`  
als Key-Value-Paare gespeichert und können via Einstellungen-Tab geändert werden.

---

## 6. Betrieb im Schulungsmodus

Für Demos / Tests ohne echte Dienstplan-Excel:
1. Einstellungen → Dienstplan-Pfad auf eine Test-Excel zeigen
2. Mitarbeiter manuell anlegen über `STRG+N` in der Mitarbeiter-Ansicht
3. Fahrzeuge über die Fahrzeuge-Ansicht anlegen

---

## 7. Bekannte Probleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| PySide6 nicht installierbar | Windows Long Path | System-Python nutzen |
| Outlook-E-Mail nicht erstellt | pywin32 fehlt oder Outlook nicht gestartet | `pip install pywin32`, Outlook öffnen |
| Vorlage nicht gefunden | Datei verschoben | Pfad in `mitarbeiter_dokumente_functions.py` prüfen |
| python-docx fehlt | Nicht installiert | `pip install python-docx` |
| Dienstplan leer nach Laden | Falsches Excel-Format | CareMan-Export-Format prüfen |

---

## 8. Backup erstellen

Über die App (Backup-Tab) oder manuell:

```powershell
cd "Nesk3\"
python -c "
import os, zipfile
from datetime import datetime
BASE_DIR = os.getcwd()
BACKUP_DIR = os.path.join(BASE_DIR, 'Backup Data')
EXCLUDE = {'__pycache__', '.git', 'Backup Data', 'backup', 'build_tmp', 'Exe'}
os.makedirs(BACKUP_DIR, exist_ok=True)
stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
zip_path = os.path.join(BACKUP_DIR, f'Nesk3_backup_{stamp}.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for fname in files:
            full = os.path.join(root, fname)
            zf.write(full, os.path.relpath(full, BASE_DIR))
print('Backup:', zip_path)
"
```

Ergebnis: `Backup Data/Nesk3_backup_YYYYMMDD_HHMMSS.zip` (~8–10 MB)
