"""
Hilfe-Dialog
Erklärt alle Module und Funktionen der App visuell – mit Animationen.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QWidget, QTabWidget, QSizePolicy,
    QGridLayout, QGraphicsOpacityEffect, QProgressBar,
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QParallelAnimationGroup,
)
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor

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


# ── Animations-Hilfsfunktion ─────────────────────────────────────────────────
def _stagger_fade_slide(widgets: list[QWidget],
                        delay_step: int = 70,
                        duration: int = 380,
                        slide_px: int = 20):
    """Lässt Widgets gestaffelt von unten einfaden + einschieben."""
    for i, w in enumerate(widgets):
        eff = QGraphicsOpacityEffect(w)
        w.setGraphicsEffect(eff)
        eff.setOpacity(0.0)

        def _animate(wid=w, effect=eff):
            op_anim = QPropertyAnimation(effect, b"opacity", wid)
            op_anim.setDuration(duration)
            op_anim.setStartValue(0.0)
            op_anim.setEndValue(1.0)
            op_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            g = wid.geometry()
            start_geo = QRect(g.x(), g.y() + slide_px, g.width(), g.height())
            geo_anim = QPropertyAnimation(wid, b"geometry", wid)
            geo_anim.setDuration(duration)
            geo_anim.setStartValue(start_geo)
            geo_anim.setEndValue(g)
            geo_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            grp = QParallelAnimationGroup(wid)
            grp.addAnimation(op_anim)
            grp.addAnimation(geo_anim)
            grp.start()
            wid._anim_grp = grp  # Referenz halten

        QTimer.singleShot(i * delay_step, _animate)


# ── Pulsierendes Icon im Header ───────────────────────────────────────────────
class _PulseLabel(QLabel):
    """Label dessen Font-Größe leicht pulsiert (Breathing-Effekt)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._sizes = [36, 38, 40, 42, 40, 38]
        self._idx = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(600)

    def _tick(self):
        self._idx = (self._idx + 1) % len(self._sizes)
        self.setFont(QFont("Segoe UI Emoji", self._sizes[self._idx]))


# ── Animierter Laufbalken unter dem Header ────────────────────────────────────
class _RunningBanner(QFrame):
    """Schmaler Streifen mit wanderndem Farbverlauf."""
    def __init__(self, color: str = FIORI_BLUE, parent=None):
        super().__init__(parent)
        self._color = color
        self._pos = 0.0
        self.setFixedHeight(5)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)   # ~60 fps

    def _tick(self):
        self._pos = (self._pos + 2.5) % (self.width() + 160)
        self.update()

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#d0dcea"))
        grad = QLinearGradient(self._pos - 160, 0, self._pos, 0)
        grad.setColorAt(0.0, QColor(self._color + "00"))
        grad.setColorAt(0.5, QColor(self._color + "dd"))
        grad.setColorAt(1.0, QColor(self._color + "00"))
        p.fillRect(0, 0, w, h, grad)
        p.end()


# ── Modul-Karte ───────────────────────────────────────────────────────────────
class _ModuleCard(QFrame):
    def __init__(self, icon: str, title: str, color: str,
                 beschreibung: str, features: list[str], parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                border-top: none; border-right: none; border-bottom: none;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

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

        desc_lbl = QLabel(beschreibung)
        desc_lbl.setWordWrap(True)
        desc_lbl.setFont(QFont("Arial", 11))
        desc_lbl.setStyleSheet("color: #444; border: none;")
        lay.addWidget(desc_lbl)

        if features:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #eee;")
            lay.addWidget(sep)
            for f in features:
                fl = QLabel(f"  ✔  {f}")
                fl.setFont(QFont("Arial", 10))
                fl.setStyleSheet("color: #555; border: none;")
                lay.addWidget(fl)


# ── Workflow-Schritt-Karte ────────────────────────────────────────────────────
class _StepCard(QFrame):
    def __init__(self, num: str, ico: str, col: str,
                 title: str, desc: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background: white; border-radius: 10px; border: none; }"
        )
        rlay = QHBoxLayout(self)
        rlay.setContentsMargins(0, 0, 16, 0)
        rlay.setSpacing(0)

        badge = QLabel(num)
        badge.setFixedSize(58, 58)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {col}; color: white; border: none;
                border-top-left-radius: 10px; border-bottom-left-radius: 10px;
            }}
        """)
        rlay.addWidget(badge)

        i_lbl = QLabel(ico)
        i_lbl.setFixedSize(52, 58)
        i_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        i_lbl.setFont(QFont("Segoe UI Emoji", 20))
        i_lbl.setStyleSheet(f"background-color: {col}22; border: none;")
        rlay.addWidget(i_lbl)

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


# ── Tipp-Karte ────────────────────────────────────────────────────────────────
class _TipCard(QFrame):
    def __init__(self, icon: str, title: str, text: str,
                 color: str = "#0a73c4", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: white; border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        cl = QHBoxLayout(self)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(12)
        il = QLabel(icon)
        il.setFont(QFont("Segoe UI Emoji", 18))
        il.setStyleSheet("border: none;")
        il.setFixedWidth(34)
        tl = QVBoxLayout()
        tl.setSpacing(2)
        nl = QLabel(title)
        nl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        nl.setStyleSheet(f"color: {color}; border: none;")
        dl = QLabel(text)
        dl.setWordWrap(True)
        dl.setFont(QFont("Arial", 10))
        dl.setStyleSheet("color: #555; border: none;")
        tl.addWidget(nl)
        tl.addWidget(dl)
        cl.addWidget(il)
        cl.addLayout(tl, 1)


# ── Haupt-Dialog ─────────────────────────────────────────────────────────────
class HilfeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("❓ Hilfe – Nesk3 Bedienungsanleitung")
        self.resize(900, 700)
        self.setMinimumSize(720, 520)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self._tabs_animated: set[int] = set()
        self._tab_widgets: dict[int, list[QWidget]] = {}
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        self._banner = _RunningBanner(FIORI_BLUE)
        root.addWidget(self._banner)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #f5f6f7; }
            QTabBar::tab {
                padding: 10px 22px; font-size: 12px; font-family: Arial;
                background: #e8ecf0; color: #555;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected {
                background: #f5f6f7; color: #0a73c4;
                border-bottom: 3px solid #0a73c4; font-weight: bold;
            }
            QTabBar::tab:hover { background: #dde3ea; }
        """)

        self._tabs.addTab(self._tab_uebersicht(), "🏠  Übersicht")
        self._tabs.addTab(self._tab_module(),     "📦  Module")
        self._tabs.addTab(self._tab_workflow(),   "🔄  Workflow")
        self._tabs.addTab(self._tab_tipps(),      "💡  Tipps")
        self._tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self._tabs, 1)

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

    # ── Header mit Puls-Icon ──────────────────────────────────────────────────
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
        t2 = QLabel(
            f"Nesk3  ·  Version {APP_VERSION}  ·  "
            "DRK Erste-Hilfe-Station Flughafen Köln/Bonn"
        )
        t2.setFont(QFont("Arial", 10))
        t2.setStyleSheet("color: rgba(255,255,255,0.75); border: none;")
        left.addStretch()
        left.addWidget(t1)
        left.addWidget(t2)
        left.addStretch()

        self._pulse_icon = _PulseLabel("🏥")
        self._pulse_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pulse_icon.setStyleSheet("border: none; color: rgba(255,255,255,0.30);")

        lay.addLayout(left, 1)
        lay.addWidget(self._pulse_icon)
        return header

    # ── Tab 0: Übersicht ──────────────────────────────────────────────────────
    def _tab_uebersicht(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        intro = QLabel(
            "Nesk3 ist die digitale Verwaltungsapp der DRK Erste-Hilfe-Station "
            "am Flughafen Köln/Bonn.\n"
            "Sie fasst alle wichtigen Funktionen des Stationsbetriebs an einem Ort zusammen."
        )
        intro.setWordWrap(True)
        intro.setFont(QFont("Arial", 12))
        intro.setStyleSheet("color: #333;")
        root.addWidget(intro)
        root.addWidget(self._section_label("📌  Was kann die App?"))

        grid = QGridLayout()
        grid.setSpacing(12)
        items = [
            ("🏠", "Dashboard",       _COLORS["dashboard"],
             "Mitarbeiter, Schichten, DB-Status auf einen Blick."),
            ("☀️🌙", "Aufgaben",      _COLORS["aufgaben"],
             "Tages- & Nachtdienst-Aufgaben, Checklisten, Code-19-E-Mails."),
            ("📅", "Dienstplan",       _COLORS["dienstplan"],
             "Excel-Dienstpläne laden und als Word-Stärkemeldung exportieren."),
            ("📋", "Übergabe",          _COLORS["uebergabe"],
             "Schichtprotokolle anlegen, ausfüllen, per E-Mail weiterleiten."),
            ("🚗", "Fahrzeuge",         _COLORS["fahrzeuge"],
             "Status, Schäden, Reparaturaufträge, Wartungstermine."),
            ("🕐", "Code 19",           _COLORS["code19"],
             "Code-19-Protokoll führen, animierte Uhrzeigen-Anzeige."),
            ("🖨️", "Ma. Ausdrucke",    _COLORS["ausdrucke"],
             "Vordrucke öffnen oder drucken."),
            ("🤒", "Krankmeldungen",    _COLORS["krankmeldung"],
             "Krankmeldungsformulare je Mitarbeiter öffnen."),
            ("💾", "Backup",            _COLORS["backup"],
             "Datensicherung erstellen und wiederherstellen."),
            ("⚙️", "Einstellungen",     _COLORS["einstellung"],
             "Pfade, E-Mobby-Fahrer, Protokolle archivieren."),
        ]
        animatables: list[QWidget] = [intro]
        for i, (ico, name, col, desc) in enumerate(items):
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
            QLabel_name = QLabel(name)
            QLabel_name.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            QLabel_name.setStyleSheet(f"color: {col}; border: none;")
            QLabel_desc = QLabel(desc)
            QLabel_desc.setWordWrap(True)
            QLabel_desc.setFont(QFont("Arial", 10))
            QLabel_desc.setStyleSheet("color: #555; border: none;")
            tl.addWidget(QLabel_name)
            tl.addWidget(QLabel_desc)
            cl.addWidget(il)
            cl.addLayout(tl, 1)
            grid.addWidget(card, i // 2, i % 2)
            animatables.append(card)

        root.addLayout(grid)
        root.addStretch()
        self._tab_widgets[0] = animatables
        return self._scroll_wrap(w)

    # ── Tab 1: Module im Detail ───────────────────────────────────────────────
    def _tab_module(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        module_data: list[tuple] = [
            ("🏠", "Dashboard", _COLORS["dashboard"],
             "Die Startseite zeigt auf einen Blick die wichtigsten Kennzahlen.",
             ["Aktive Mitarbeiter und Gesamtanzahl",
              "Schichten heute und im laufenden Monat",
              "Datenbankstatus (verbunden / Fehler)",
              "Animiertes Flugzeug-Widget – zum Klicken 😄"]),
            ("☀️", "Aufgaben Tag", _COLORS["aufgaben"],
             "Verwaltet alle wiederkehrenden Aufgaben im Tagdienst.",
             ["Freier E-Mail-Entwurf mit Anhang + Umbenennung",
              "Schnell-Templates: Checklisten- und Checks-Mail",
              "Code-19-Monatsbericht per Excel → Outlook",
              "Signatur-Button: Mail mit persönlicher Outlook-Signatur"]),
            ("🌙", "Aufgaben Nacht", _COLORS["nacht"],
             "Spiegelseite für den Nachtdienst.",
             ["Gleiche Mail-Funktionen wie Tagdienst",
              "AOCC Lagebericht direkt öffnen",
              "Separate Code-19-Berichtsfunktion"]),
            ("📅", "Dienstplan", _COLORS["dienstplan"],
             "Lädt Excel-Dienstpläne und zeigt sie side-by-side.",
             ["Bis zu 4 Dienstpläne gleichzeitig offen",
              "Direktladen aus dem Dateibaum",
              "Word-Export: Stärkemeldung",
              "E-Mobby-Fahrer automatisch hervorgehoben"]),
            ("📋", "Übergabe", _COLORS["uebergabe"],
             "Erstellt und verwaltet Schichtprotokolle.",
             ["Neues Protokoll mit einem Klick",
              "Monatliche Übersicht mit Navigation",
              "Suche & Filterung nach Schichttyp",
              "Protokoll per E-Mail weiterleiten",
              "Schadenmeldungen im E-Mail-Dialog anhaken"]),
            ("🚗", "Fahrzeuge", _COLORS["fahrzeuge"],
             "Vollständige Fahrzeugverwaltung.",
             ["Fahrzeuge anlegen, bearbeiten, löschen",
              "Status-Verlauf mit Grund und Datum",
              "Schäden dokumentieren (Schwere, Behoben-Datum)",
              "Unfallbogen-Dialog und Reparaturauftrag-PDF",
              "Wartungs- und TÜV-Termine",
              "Globale Suche: Status, Schäden, Termine, Historie"]),
            ("🕐", "Code 19", _COLORS["code19"],
             "Protokolliert Code-19-Ereignisse.",
             ["Einträge mit Uhrzeit und Beschreibung",
              "Animierte Analoguhr zur Zeiterfassung",
              "Export / Weiterleitung per E-Mail"]),
            ("🖨️", "Ma. Ausdrucke", _COLORS["ausdrucke"],
             "Zeigt alle Vordrucke zum Öffnen oder Direktdruck.",
             ["Alle Dateien in Daten/Vordrucke",
              "'Öffnen' startet das zugehörige Programm",
              "'Drucken' sendet direkt an Standarddrucker"]),
            ("🤒", "Krankmeldungen", _COLORS["krankmeldung"],
             "Öffnet Krankmeldungsformulare je Mitarbeiter.",
             ["Automatische Unterordner-Erkennung",
              "Suche nach Mitarbeitername",
              "Öffnen und Drucken direkt"]),
            ("⚙️", "Einstellungen", _COLORS["einstellung"],
             "Zentrale Konfiguration und Datenverwaltung.",
             ["Ordner-Pfade konfigurieren",
              "E-Mobby-Fahrerliste pflegen",
              "Protokolle löschen / archivieren (passwortgeschützt)",
              "Archiv-Datenbank verwalten"]),
        ]
        cards: list[QWidget] = []
        for data in module_data:
            c = _ModuleCard(*data)
            root.addWidget(c)
            cards.append(c)
        root.addStretch()
        self._tab_widgets[1] = cards
        return self._scroll_wrap(w)

    # ── Tab 2: Workflow ───────────────────────────────────────────────────────
    def _tab_workflow(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        root.addWidget(self._section_label("🔄  Typischer Schichtablauf"))

        # Fortschrittsbalken – wird animiert wenn Tab aufgerufen
        self._wf_bar = QProgressBar()
        self._wf_bar.setRange(0, 100)
        self._wf_bar.setValue(0)
        self._wf_bar.setFixedHeight(8)
        self._wf_bar.setTextVisible(False)
        self._wf_bar.setStyleSheet(f"""
            QProgressBar {{
                background: #dde4ed; border-radius: 4px; border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {FIORI_BLUE}, stop:1 #27ae60
                );
                border-radius: 4px;
            }}
        """)
        root.addWidget(self._wf_bar)

        steps = [
            ("1", "🏠", "#0a73c4", "App starten → Dashboard",
             "Startet auf dem Dashboard. DB-Status und Schichtübersicht sofort sichtbar."),
            ("2", "📋", "#2980b9", "Übergabe-Protokoll anlegen",
             "Tab '📋 Übergabe' → '☀ Tagdienst' oder '🌙 Nachtdienst' → Protokoll wird angelegt."),
            ("3", "🚗", "#c0392b", "Fahrzeuge prüfen",
             "Tab '🚗 Fahrzeuge' → Status kontrollieren → Auffälligkeiten sofort als Schaden erfassen."),
            ("4", "☀️", "#e67e22", "Aufgaben abarbeiten",
             "Tages- oder Nachtdienst-Aufgaben abhaken. Code-19-Mail bei Bedarf direkt versenden."),
            ("5", "📅", "#27ae60", "Dienstplan laden (optional)",
             "Excel-Datei aus dem Dateibaum öffnen. Bei Bedarf als Word-Stärkemeldung exportieren."),
            ("6", "📋", "#2980b9", "Protokoll abschließen & weiterleiten",
             "Protokoll ausfüllen → 'E-Mail erstellen' → Schäden anhaken → Outlook-Entwurf öffnen."),
        ]
        step_cards: list[QWidget] = []
        for num, ico, col, title, desc in steps:
            card = _StepCard(num, ico, col, title, desc)
            root.addWidget(card)
            step_cards.append(card)

        root.addStretch()
        self._tab_widgets[2] = step_cards
        return self._scroll_wrap(w)

    # ── Tab 3: Tipps & Shortcuts ──────────────────────────────────────────────
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
             "In 'Fahrzeuge' und 'Übergabe' gibt es oben eine Suchleiste. Filter: Status, Schäden, Termine, Protokolldatum.",
             "#27ae60"),
            ("📧", "Outlook-Integration",
             "Alle E-Mail-Buttons erstellen einen fertigen Outlook-Entwurf. Mit dem Signatur-Button wird Ihre persönliche Signatur automatisch eingefügt.",
             "#2980b9"),
            ("💾", "Datenbank",
             "Alle Daten werden in einer lokalen SQLite-Datenbank gespeichert. Pfad im Dashboard-DB-Status sichtbar.",
             "#7f8c8d"),
            ("📦", "Archivieren statt Löschen",
             "In den Einstellungen können Sie Protokolle archivieren statt löschen. Archiv bleibt erhalten.",
             "#8e44ad"),
            ("🖨️", "Drucken",
             "In 'Ma. Ausdrucke' und 'Krankmeldungen' können Dateien direkt an den Drucker geschickt werden.",
             "#16a085"),
            ("🗂️", "Mehrere Dienstpläne",
             "Im Dienstplan-Tab können bis zu 4 Excel-Dateien gleichzeitig geöffnet und verglichen werden.",
             "#e67e22"),
            ("🔒", "Passwortschutz",
             "Löschen/Archivieren von Protokollen ist passwortgeschützt. Bitte bei der Stationsleitung erfragen.",
             "#e74c3c"),
        ]
        cards: list[QWidget] = []
        for ico, title, text, col in tipps:
            card = _TipCard(ico, title, text, col)
            root.addWidget(card)
            cards.append(card)

        root.addSpacing(8)
        ver_frm = QFrame()
        ver_frm.setStyleSheet(
            "QFrame { background: #e8ecf1; border-radius: 8px; border: none; }"
        )
        vl = QHBoxLayout(ver_frm)
        vl.setContentsMargins(16, 10, 16, 10)
        vc = QLabel("ℹ️")
        vc.setFont(QFont("Segoe UI Emoji", 14))
        vc.setStyleSheet("border: none;")
        vl.addWidget(vc)
        ver_txt = QLabel(
            f"<b>Nesk3 v{APP_VERSION}</b> · DRK Erste-Hilfe-Station Flughafen Köln/Bonn · "
            "Entwickelt mit Python 3.13 + PySide6"
        )
        ver_txt.setFont(QFont("Arial", 10))
        ver_txt.setStyleSheet("color: #555; border: none;")
        ver_txt.setWordWrap(True)
        vl.addWidget(ver_txt, 1)
        root.addWidget(ver_frm)
        cards.append(ver_frm)

        root.addStretch()
        self._tab_widgets[3] = cards
        return self._scroll_wrap(w)

    # ── Gemeinsame Helfer ─────────────────────────────────────────────────────
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

    # ── Progress-Animation Workflow ───────────────────────────────────────────
    def _animate_wf_bar(self):
        if not hasattr(self, "_wf_bar"):
            return
        self._wf_bar.setValue(0)
        self._wf_pval = 0

        def _tick():
            self._wf_pval = min(self._wf_pval + 2, 100)
            self._wf_bar.setValue(self._wf_pval)
            if self._wf_pval >= 100:
                self._wf_tick_timer.stop()

        self._wf_tick_timer = QTimer(self)
        self._wf_tick_timer.timeout.connect(_tick)
        self._wf_tick_timer.start(16)

    # ── Tab-Wechsel ───────────────────────────────────────────────────────────
    def _on_tab_changed(self, idx: int):
        if idx in self._tabs_animated:
            return
        self._tabs_animated.add(idx)
        widgets = self._tab_widgets.get(idx, [])
        if widgets:
            QTimer.singleShot(40, lambda: _stagger_fade_slide(widgets, delay_step=60))
        if idx == 2:
            QTimer.singleShot(220, self._animate_wf_bar)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, lambda: self._on_tab_changed(0))
