"""
Hilfe-Dialog
Erklärt alle Module und Funktionen der App visuell.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QWidget, QTabWidget, QSizePolicy,
    QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient

from config import FIORI_BLUE, FIORI_TEXT, APP_VERSION


# ── Farbpalette der Module ────────────────────────────────────────────────────
_COLORS = {
    "dashboard":    "#0a73c4",
    "aufgaben":     "#e67e22",
    "nacht":        "#8e44ad",
    "dienstplan":   "#27ae60",
    "uebergabe":    "#2980b9",
    "fahrzeuge":    "#c0392b",
    "code19":       "#e74c3c",
    "ausdrucke":    "#16a085",
    "krankmeldung": "#d35400",
    "backup":       "#7f8c8d",
    "einstellung":  "#2c3e50",
}


# ── Einfache Karte ────────────────────────────────────────────────────────────
class _ModuleCard(QFrame):
    """Visuelle Karte für ein App-Modul."""

    def __init__(self, icon: str, title: str, color: str,
                 beschreibung: str, features: list[str], parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                border-top: none;
                border-right: none;
                border-bottom: none;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        # Header
        header = QHBoxLayout()
        ico_lbl = QLabel(icon)
        ico_lbl.setFont(QFont("Segoe UI Emoji", 22))
        ico_lbl.setStyleSheet("border: none;")
        ico_lbl.setFixedWidth(44)
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {color}; border: none;")
        header.addWidget(ico_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        lay.addLayout(header)

        # Beschreibung
        desc_lbl = QLabel(beschreibung)
        desc_lbl.setWordWrap(True)
        desc_lbl.setFont(QFont("Arial", 11))
        desc_lbl.setStyleSheet("color: #444; border: none;")
        lay.addWidget(desc_lbl)

        # Features
        if features:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #eee;")
            lay.addWidget(sep)
            for f in features:
                f_lbl = QLabel(f"  ✔  {f}")
                f_lbl.setFont(QFont("Arial", 10))
                f_lbl.setStyleSheet("color: #555; border: none;")
                lay.addWidget(f_lbl)


# ── Kurztipp-Karte ────────────────────────────────────────────────────────────
class _TipCard(QFrame):
    """Kleiner Tipp-Hinweis."""
    def __init__(self, icon: str, text: str, color: str = "#0a73c4", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color}18;
                border-radius: 8px;
                border: 1px solid {color}44;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)
        ico = QLabel(icon)
        ico.setFont(QFont("Segoe UI Emoji", 18))
        ico.setStyleSheet("border: none;")
        ico.setFixedWidth(34)
        txt = QLabel(text)
        txt.setWordWrap(True)
        txt.setFont(QFont("Arial", 11))
        txt.setStyleSheet(f"color: {color}; border: none;")
        lay.addWidget(ico)
        lay.addWidget(txt, 1)


# ── Hilfe-Dialog ─────────────────────────────────────────────────────────────
class HilfeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("❓ Hilfe – Nesk3 Bedienungsanleitung")
        self.resize(880, 680)
        self.setMinimumSize(700, 500)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header-Banner
        root.addWidget(self._build_header())

        # Tab-Widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #f5f6f7; }
            QTabBar::tab {
                padding: 10px 20px; font-size: 12px; font-family: Arial;
                background: #e8ecf0; color: #555; border-radius: 0px;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected {
                background: #f5f6f7; color: #0a73c4;
                border-bottom: 3px solid #0a73c4; font-weight: bold;
            }
            QTabBar::tab:hover { background: #dde3ea; }
        """)
        tabs.addTab(self._tab_uebersicht(),   "🏠  Übersicht")
        tabs.addTab(self._tab_module(),       "📦  Module")
        tabs.addTab(self._tab_workflow(),     "🔄  Workflow")
        tabs.addTab(self._tab_tipps(),        "💡  Tipps & Shortcuts")
        root.addWidget(tabs, 1)

        # Schließen-Button
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(16, 10, 16, 14)
        btn_row.addStretch()
        close_btn = QPushButton("✕  Schließen")
        close_btn.setMinimumHeight(36)
        close_btn.setMinimumWidth(130)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {FIORI_BLUE}; color: white;
                border: none; border-radius: 4px;
                padding: 6px 20px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #0855a9; }}
        """)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet(f"background-color: {FIORI_BLUE};")
        lay = QHBoxLayout(header)
        lay.setContentsMargins(28, 0, 28, 0)

        left = QVBoxLayout()
        t1 = QLabel("❓ Hilfe & Bedienungsanleitung")
        t1.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        t1.setStyleSheet("color: white; border: none;")
        t2 = QLabel(f"Nesk3  ·  Version {APP_VERSION}  ·  DRK Erste-Hilfe-Station Flughafen Köln/Bonn")
        t2.setFont(QFont("Arial", 10))
        t2.setStyleSheet("color: rgba(255,255,255,0.75); border: none;")
        left.addStretch()
        left.addWidget(t1)
        left.addWidget(t2)
        left.addStretch()

        right = QLabel("🏥")
        right.setFont(QFont("Segoe UI Emoji", 40))
        right.setStyleSheet("border: none; color: rgba(255,255,255,0.3);")

        lay.addLayout(left, 1)
        lay.addWidget(right)
        return header

    # ── Tab 1: Übersicht ──────────────────────────────────────────────────────
    def _tab_uebersicht(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        intro = QLabel(
            "Nesk3 ist die digitale Verwaltungsapp der DRK Erste-Hilfe-Station am Flughafen Köln/Bonn.\n"
            "Sie fasst alle wichtigen Funktionen des Stationsbetriebs an einem Ort zusammen."
        )
        intro.setWordWrap(True)
        intro.setFont(QFont("Arial", 12))
        intro.setStyleSheet("color: #333;")
        root.addWidget(intro)

        root.addWidget(self._section_label("📌  Was kann die App?"))

        grid = QGridLayout()
        grid.setSpacing(12)

        cards = [
            ("🏠", "Dashboard",        _COLORS["dashboard"],
             "Schnellübersicht: aktive Mitarbeiter, Schichten heute/diesen Monat, DB-Status."),
            ("☀️🌙", "Aufgaben",        _COLORS["aufgaben"],
             "Tages- & Nachtdienst-Aufgaben, Checklisten und Code-19-E-Mails per Outlook."),
            ("📅", "Dienstplan",        _COLORS["dienstplan"],
             "Excel-Dienstpläne laden, anzeigen und als Word-Stärkemeldung exportieren."),
            ("📋", "Übergabe",          _COLORS["uebergabe"],
             "Schichtprotokolle anlegen, ausfüllen und per E-Mail weiterleiten."),
            ("🚗", "Fahrzeuge",         _COLORS["fahrzeuge"],
             "Fahrzeugstatus, Schäden dokumentieren, Reparaturaufträge, Wartungstermine."),
            ("🕐", "Code 19",           _COLORS["code19"],
             "Code-19-Protokoll führen, animierte Uhrzeigen-Anzeige verwalten."),
            ("🖨️", "Ma. Ausdrucke",    _COLORS["ausdrucke"],
             "Vordrucke direkt öffnen oder drucken (Ordner: Daten/Vordrucke)."),
            ("🤒", "Krankmeldungen",    _COLORS["krankmeldung"],
             "Krankmeldungsformulare je Mitarbeiter öffnen (Ordner: 03_Krankmeldungen)."),
            ("💾", "Backup",            _COLORS["backup"],
             "Datensicherung der Datenbank erstellen und wiederherstellen."),
            ("⚙️", "Einstellungen",     _COLORS["einstellung"],
             "Ordner-Pfade konfigurieren, E-Mobby-Fahrer verwalten, Protokolle archivieren."),
        ]

        for i, (ico, name, col, desc) in enumerate(cards):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white; border-radius: 8px;
                    border-left: 4px solid {col};
                }}
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(12, 10, 12, 10)
            cl.setSpacing(10)
            il = QLabel(ico)
            il.setFont(QFont("Segoe UI Emoji", 16))
            il.setStyleSheet("border: none;")
            il.setFixedWidth(32)
            tl = QVBoxLayout()
            nl = QLabel(name)
            nl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            nl.setStyleSheet(f"color: {col}; border: none;")
            dl = QLabel(desc)
            dl.setWordWrap(True)
            dl.setFont(QFont("Arial", 10))
            dl.setStyleSheet("color: #555; border: none;")
            tl.addWidget(nl)
            tl.addWidget(dl)
            cl.addWidget(il)
            cl.addLayout(tl, 1)
            grid.addWidget(card, i // 2, i % 2)

        root.addLayout(grid)
        root.addStretch()
        return self._scroll_wrap(w)

    # ── Tab 2: Module im Detail ───────────────────────────────────────────────
    def _tab_module(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        module = [
            _ModuleCard("🏠", "Dashboard", _COLORS["dashboard"],
                "Die Startseite zeigt auf einen Blick die wichtigsten Kennzahlen der Station.",
                ["Aktive Mitarbeiter und Gesamtanzahl",
                 "Schichten heute und im laufenden Monat",
                 "Datenbankstatus (verbunden / Fehler)",
                 "Animiertes Flugzeug-Widget – zum Klicken 😄"]),

            _ModuleCard("☀️", "Aufgaben Tag", _COLORS["aufgaben"],
                "Verwaltet alle wiederkehrenden Aufgaben im Tagdienst und ermöglicht E-Mail-Erstellung.",
                ["Freier E-Mail-Entwurf mit Anhang und Umbenennung",
                 "Schnell-Templates: Checklisten- und Checks-Mail",
                 "Code-19-Monatsbericht per Excel → Outlook",
                 "Signatur-Button: Mail mit persönlicher Outlook-Signatur"]),

            _ModuleCard("🌙", "Aufgaben Nacht", _COLORS["nacht"],
                "Spiegelseite für den Nachtdienst mit eigenem E-Mail-Tab und AOCC-Lagebericht.",
                ["Gleiche Mail-Funktionen wie Tagdienst",
                 "AOCC Lagebericht direkt öffnen",
                 "Separate Code-19-Berichts-Funktion für Nacht"]),

            _ModuleCard("📅", "Dienstplan", _COLORS["dienstplan"],
                "Lädt Excel-Dienstpläne aus dem konfigurierten Ordner und zeigt sie side-by-side.",
                ["Bis zu 4 Dienstpläne gleichzeitig offen",
                 "Direkt aus dem Dateibaum per Klick laden",
                 "Word-Export: Stärkemeldung für Hausverwaltung",
                 "E-Mobby-Fahrer werden automatisch hervorgehoben"]),

            _ModuleCard("📋", "Übergabe", _COLORS["uebergabe"],
                "Erstellt und verwaltet Schichtprotokolle für Tag- und Nachtdienst.",
                ["Neues Protokoll mit einem Klick anlegen",
                 "Monatliche Übersicht mit Navigation",
                 "Suche und Filterung nach Schichttyp",
                 "Protokoll per E-Mail (Outlook) weiterleiten",
                 "Schadenmeldungen direkt im E-Mail-Dialog anhaken"]),

            _ModuleCard("🚗", "Fahrzeuge", _COLORS["fahrzeuge"],
                "Vollständige Fahrzeugverwaltung mit Status, Schäden und Terminen.",
                ["Fahrzeuge anlegen, bearbeiten, löschen",
                 "Status-Verlauf mit Grund und Datum",
                 "Schäden dokumentieren (Schwere, Behoben-Datum)",
                 "Unfallbogen-Dialog und Reparaturauftrag-PDF öffnen",
                 "Wartungs- und TÜV-Termine mit Typisierung",
                 "Globale Suche über Status, Schäden, Termine, Historie"]),

            _ModuleCard("🕐", "Code 19", _COLORS["code19"],
                "Protokolliert Code-19-Ereignisse und zeigt eine animierte Uhr.",
                ["Einträge mit Uhrzeit und Beschreibung",
                 "Animierte Analoguhr zur Zeiterfassung",
                 "Export / Weiterleitung per E-Mail"]),

            _ModuleCard("🖨️", "Ma. Ausdrucke", _COLORS["ausdrucke"],
                "Zeigt alle Vordrucke im konfigurierten Ordner zum Öffnen oder Direktdruck.",
                ["Alle Dateien im Ordner Daten/Vordrucke",
                 "Button 'Öffnen' startet das zugehörige Programm",
                 "Button 'Drucken' sendet direkt an Standarddrucker",
                 "Suche nach Dateinamen"]),

            _ModuleCard("🤒", "Krankmeldungen", _COLORS["krankmeldung"],
                "Öffnet Krankmeldungsformulare je Mitarbeiter aus dem konfigurierten Ordner.",
                ["Automatische Unterordner-Erkennung",
                 "Suche nach Mitarbeitername",
                 "Öffnen und Drucken direkt aus dem Dialog"]),

            _ModuleCard("⚙️", "Einstellungen", _COLORS["einstellung"],
                "Zentrale Konfiguration der App-Pfade und Datenverwaltung.",
                ["Dienstplan-, Sonderaufgaben-, AOCC-, Code-19-Ordner konfigurieren",
                 "E-Mobby-Fahrerliste pflegen",
                 "Protokolle löschen oder archivieren (passwortgeschützt)",
                 "Archiv-Datenbank verwalten und Protokolle wiederherstellen"]),
        ]

        for card in module:
            root.addWidget(card)

        root.addStretch()
        return self._scroll_wrap(w)

    # ── Tab 3: Workflow ───────────────────────────────────────────────────────
    def _tab_workflow(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        root.addWidget(self._section_label("🔄  Typischer Schichtablauf"))

        steps = [
            ("1", "🏠", "#0a73c4",  "App starten → Dashboard",
             "Die App startet automatisch auf dem Dashboard. Status der Datenbank und Schichtübersicht werden angezeigt."),
            ("2", "📋", "#2980b9",  "Übergabe-Protokoll anlegen",
             "Im Tab '📋 Übergabe' auf '☀ Tagdienst' oder '🌙 Nachtdienst' klicken → Protokoll wird automatisch angelegt und geöffnet."),
            ("3", "🚗", "#c0392b",  "Fahrzeuge prüfen",
             "Im Tab '🚗 Fahrzeuge' Fahrzeugstatus kontrollieren. Auffälligkeiten direkt als Schaden erfassen."),
            ("4", "☀️", "#e67e22",  "Aufgaben abarbeiten",
             "Tages- oder Nachtdienst-Aufgaben im jeweiligen Tab abhaken. Code-19-Mail bei Bedarf direkt versenden."),
            ("5", "📅", "#27ae60",  "Dienstplan laden (optional)",
             "Im Tab '📅 Dienstplan' Excel-Datei aus dem Dateibaum per Klick öffnen. Stärkemeldung bei Bedarf als Word exportieren."),
            ("6", "📋", "#2980b9",  "Protokoll abschließen & weiterleiten",
             "Übergabe-Protokoll ausfüllen → 'E-Mail erstellen' → ggf. Schäden anhaken → Outlook-Entwurf wird geöffnet und kann versendet werden."),
        ]

        for num, ico, col, title, desc in steps:
            row_frame = QFrame()
            row_frame.setStyleSheet(
                "QFrame { background: white; border-radius: 10px; border: none; }"
            )
            rlay = QHBoxLayout(row_frame)
            rlay.setContentsMargins(0, 0, 16, 0)
            rlay.setSpacing(0)

            # Nummer-Badge
            badge = QLabel(num)
            badge.setFixedSize(56, 56)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {col};
                    color: white;
                    border-radius: 0px;
                    border-top-left-radius: 10px;
                    border-bottom-left-radius: 10px;
                    border: none;
                }}
            """)
            rlay.addWidget(badge)

            # Icon
            i_lbl = QLabel(ico)
            i_lbl.setFixedSize(52, 56)
            i_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            i_lbl.setFont(QFont("Segoe UI Emoji", 20))
            i_lbl.setStyleSheet(f"background-color: {col}22; border: none;")
            rlay.addWidget(i_lbl)

            # Text
            tlay = QVBoxLayout()
            tlay.setContentsMargins(14, 10, 0, 10)
            tlay.setSpacing(2)
            tit = QLabel(title)
            tit.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            tit.setStyleSheet(f"color: {col}; border: none;")
            dsc = QLabel(desc)
            dsc.setWordWrap(True)
            dsc.setFont(QFont("Arial", 10))
            dsc.setStyleSheet("color: #555; border: none;")
            tlay.addWidget(tit)
            tlay.addWidget(dsc)
            rlay.addLayout(tlay, 1)

            root.addWidget(row_frame)

        root.addStretch()
        return self._scroll_wrap(w)

    # ── Tab 4: Tipps & Shortcuts ──────────────────────────────────────────────
    def _tab_tipps(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        root.addWidget(self._section_label("💡  Nützliche Hinweise"))

        tipps = [
            ("🖱️", "Tooltips",
             "Fahren Sie mit der Maus über jeden Button oder jedes Feld – ein Tooltip erklärt die Funktion.",
             "#0a73c4"),
            ("🔍", "Globale Suche",
             "In 'Fahrzeuge' und 'Übergabe' gibt es oben eine Suchleiste. Sie können nach Kennzeichen, Status, Schäden, Terminen oder Protokolldatum filtern.",
             "#27ae60"),
            ("📧", "Outlook-Integration",
             "Alle E-Mail-Buttons erstellen einen fertigen Outlook-Entwurf. Sie müssen nur noch auf 'Senden' klicken. Mit dem Signatur-Button wird Ihre persönliche Outlook-Signatur automatisch eingefügt.",
             "#2980b9"),
            ("💾", "Datenbank",
             "Alle Daten (Fahrzeuge, Protokolle, Termine) werden in einer lokalen SQLite-Datenbank gespeichert. Der Pfad ist im Dashboard als DB-Status sichtbar.",
             "#7f8c8d"),
            ("📦", "Archivieren statt Löschen",
             "In den Einstellungen können Sie abgeschlossene Protokolle archivieren statt löschen. Sie bleiben in der Archiv-Datenbank erhalten und können jederzeit wiederhergestellt werden.",
             "#8e44ad"),
            ("🖨️", "Drucken",
             "In 'Ma. Ausdrucke' und 'Krankmeldungen' können Sie Dateien direkt an den Drucker schicken – ohne das Programm öffnen zu müssen.",
             "#16a085"),
            ("🗂️", "Mehrere Dienstpläne",
             "Im Dienstplan-Tab können Sie bis zu 4 Excel-Dateien gleichzeitig öffnen und nebeneinander vergleichen.",
             "#e67e22"),
            ("🔒", "Passwortschutz",
             "Das Löschen und Archivieren von Protokollen ist passwortgeschützt (Einstellungen). Bitte erfragen Sie das Passwort bei der Stationsleitung.",
             "#e74c3c"),
        ]

        for ico, title, text, col in tipps:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white; border-radius: 8px;
                    border-left: 4px solid {col};
                }}
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(12, 10, 12, 10)
            cl.setSpacing(12)
            il = QLabel(ico)
            il.setFont(QFont("Segoe UI Emoji", 18))
            il.setStyleSheet("border: none;")
            il.setFixedWidth(34)
            tl = QVBoxLayout()
            tl.setSpacing(2)
            nl = QLabel(title)
            nl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            nl.setStyleSheet(f"color: {col}; border: none;")
            tl.addWidget(nl)
            dl = QLabel(text)
            dl.setWordWrap(True)
            dl.setFont(QFont("Arial", 10))
            dl.setStyleSheet("color: #555; border: none;")
            tl.addWidget(dl)
            cl.addWidget(il)
            cl.addLayout(tl, 1)
            root.addWidget(card)

        # Versioninfo
        root.addSpacing(8)
        ver_frm = QFrame()
        ver_frm.setStyleSheet(
            "QFrame { background: #e8ecf1; border-radius: 8px; border: none; }"
        )
        vl = QHBoxLayout(ver_frm)
        vl.setContentsMargins(16, 10, 16, 10)
        vl.addWidget(QLabel("ℹ️"))
        ver_txt = QLabel(
            f"<b>Nesk3 v{APP_VERSION}</b> · DRK Erste-Hilfe-Station Flughafen Köln/Bonn · "
            "Entwickelt mit Python 3.13 + PySide6"
        )
        ver_txt.setFont(QFont("Arial", 10))
        ver_txt.setStyleSheet("color: #555; border: none;")
        ver_txt.setWordWrap(True)
        vl.addWidget(ver_txt, 1)
        root.addWidget(ver_frm)

        root.addStretch()
        return self._scroll_wrap(w)

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────
    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {FIORI_TEXT}; padding-bottom: 4px;")
        return lbl

    @staticmethod
    def _scroll_wrap(widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f5f6f7; }")
        scroll.setWidget(widget)
        return scroll
