# Checklisten & Drucksachen – Nesk3

> **Stand:** 22.02.2026 — v1.0  
> **Modul:** `gui/checklisten.py`  
> **Seite:** Navigation-Index 1 (Button „Checklisten")

---

## Was macht dieses Modul?

Das Checklisten-Modul zeigt alle Dateien aus dem Ordner

```
Daten/Drucksachen/
```

direkt im Hauptfenster an. Die Dateien können:

- **einzeln** geöffnet oder gedruckt werden
- **alle auf einmal** an den Standarddrucker gesendet werden

Der Ordner wird beim Klick auf den Navigations-Button automatisch gescannt.  
Unterordner werden als eigene Abschnitte dargestellt.

---

## Unterstützte Dateitypen

| Endung | Icon | Farbe |
|--------|------|-------|
| `.pdf` | 📄 | Rot |
| `.docx` / `.doc` | 📝 | Blau |
| `.xlsx` / `.xls` | 📊 | Grün |
| `.pptx` / `.ppt` | 📋 | Orange |
| `.png` / `.jpg` | 🖼️ | Lila |
| `.txt` | 📃 | Grau |
| Alle anderen | 📁 | Grau |

---

## Ordnerstruktur

```
Daten/
└── Drucksachen/
    ├── Datei1.pdf          ← erscheint unter „Drucksachen"
    ├── Datei2.docx
    ├── /Notfallkarten/     ← eigener Abschnitt „Notfallkarten"
    │   ├── Notfallkarte_A.pdf
    │   └── Notfallkarte_B.pdf
    └── /Formulare/         ← eigener Abschnitt „Formulare"
        └── Formular_X.docx
```

Unterordner, die leer sind, werden nicht angezeigt.

---

## UI-Aufbau

```
┌─────────────────────────────────────────────────────────────────┐
│  📋 Checklisten & Drucksachen    [🔄 Aktualisieren] [🖨 Alle]  │  ← Topbar
├─────────────────────────────────────────────────────────────────┤
│  ── Drucksachen  3 Dateien ─────────────────────────────────── │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 📄          │  │ 📝          │  │ 📊          │  ← Karten  │
│  │ PDF         │  │ DOCX        │  │ XLSX        │            │
│  │ Dateiname   │  │ Dateiname   │  │ Dateiname   │            │
│  │ 124 KB      │  │ 56 KB       │  │ 89 KB       │            │
│  │[Öff][Druck] │  │[Öff][Druck] │  │[Öff][Druck] │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ── Notfallkarten  2 Dateien ───────────────────────────────── │
│  ...                                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Klassen & Funktionen

### `ChecklistenWidget` (Hauptwidget)

| Methode | Beschreibung |
|---------|-------------|
| `refresh()` | Scannt `Daten/Drucksachen` neu und baut UI auf |
| `_print_single(filepath)` | Druckt eine Datei via `os.startfile(path, "print")` |
| `_print_all()` | Fragt nach Bestätigung, druckt alle Dateien |
| `_open_single(filepath)` | Öffnet Datei mit Standardprogramm |

### `FileCard` (Datei-Karte)

Einzelne Karte mit:
- Dateityp-Icon + farbigem Badge
- Dateiname (2 Zeilen max)
- Dateigröße
- Hover-Effekt (farbiger Rahmen)
- Buttons: **Öffnen** (Outline) + **Drucken** (Filled)

### `SectionHeader`

Zeigt Ordnername und Dateianzahl als horizontalen Trenner.

### `_FlowWidget` / `_FlowLayout`

Automatischer Karten-Umbruch bei schmaler Fenstergröße.

---

## Drucken – Technisch

```python
os.startfile(filepath, "print")
```

- Sendet Datei direkt an den **Windows-Standarddrucker**
- Für PDFs öffnet dies den Adobe Reader / Edge Print-Dialog
- Fallback: `os.startfile(filepath)` → Datei wird geöffnet

Voraussetzung: Windows mit konfiguriertem Standarddrucker.

---

## Neue Datei hinzufügen

1. Datei in `Daten/Drucksachen/` (oder Unterordner) ablegen
2. Auf **🔄 Aktualisieren** klicken (oder Seite neu laden)
3. Datei erscheint automatisch als Karte

---

## Versionshistorie

### v1.0 — 22.02.2026
- Erstimplementierung
- Karten-UI mit Flow-Layout
- Einzel- und Gesamt-Druck
- Unterordner als Abschnitte
- Topbar mit Aktualisieren + Alle-drucken Button
