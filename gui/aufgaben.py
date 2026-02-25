"""
Aufgaben-Widget
Kombiniert Checklisten (Drucksachen), Sonderaufgaben und AOCC Lagebericht.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.checklisten    import ChecklistenWidget
from gui.sonderaufgaben import SonderaufgabenWidget
from config import FIORI_BLUE, FIORI_TEXT
from functions.settings_functions import get_setting

_AOCC_DEFAULT = (
    r'C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - '
    r'Kreisverband Köln e.V\Dateien von Erste-Hilfe-Station-Flughafen - '
    r'DRK Köln e.V_ - !Gemeinsam.26\Nesk\Nesk3\Daten\AOCC\AOCC Lagebericht.xlsm'
)


class _AoccWidget(QWidget):
    """Einfacher Tab zum Öffnen des AOCC Lageberichts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        info = QLabel("📣 AOCC Lagebericht")
        info.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        info.setStyleSheet(f"color: {FIORI_TEXT};")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self._pfad_lbl = QLabel()
        self._pfad_lbl.setStyleSheet("color: #666; font-size: 11px;")
        self._pfad_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pfad_lbl.setWordWrap(True)
        layout.addWidget(self._pfad_lbl)

        self._status_lbl = QLabel()
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet("font-size: 11px;")
        layout.addWidget(self._status_lbl)

        btn = QPushButton("📄  AOCC Lagebericht öffnen")
        btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        btn.setFixedHeight(50)
        btn.setFixedWidth(340)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {FIORI_BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
            }}
            QPushButton:hover {{ background-color: #0855a9; }}
        """)
        btn.clicked.connect(self._open)
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)

        self._refresh()

    def _refresh(self):
        pfad = get_setting('aocc_datei', _AOCC_DEFAULT)
        self._pfad_lbl.setText(pfad)
        if os.path.isfile(pfad):
            self._status_lbl.setText("✅ Datei gefunden")
            self._status_lbl.setStyleSheet("color: #107e3e; font-size: 11px;")
        else:
            self._status_lbl.setText("⚠️ Datei nicht gefunden – Pfad in Einstellungen prüfen")
            self._status_lbl.setStyleSheet("color: #bb6600; font-size: 11px;")

    def _open(self):
        from PySide6.QtWidgets import QMessageBox
        pfad = get_setting('aocc_datei', _AOCC_DEFAULT)
        if not os.path.isfile(pfad):
            QMessageBox.warning(self, "Datei nicht gefunden",
                f"Die Datei wurde nicht gefunden:\n{pfad}\n\n"
                "Bitte den Pfad in den Einstellungen anpassen.")
            return
        try:
            os.startfile(pfad)
        except Exception as exc:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Öffnen:\n{exc}")


class AufgabenWidget(QWidget):
    """Kombinierte Seite: Tabs für Checklisten, Sonderaufgaben und AOCC."""

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Tab-Widget ─────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setDocumentMode(False)
        tabs.setFont(QFont("Segoe UI", 11))
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: #f5f6f7;
            }}
            QTabBar::tab {{
                background: #dce6f0;
                color: {FIORI_TEXT};
                padding: 10px 28px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
            }}
            QTabBar::tab:selected {{
                background: {FIORI_BLUE};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background: #b8cfe8;
            }}
        """)

        # Tab 1 – Checklisten
        self._checklisten = ChecklistenWidget()
        tabs.addTab(self._checklisten, "📋  Checklisten & Drucksachen")

        # Tab 2 – Sonderaufgaben
        self._sonderaufgaben = SonderaufgabenWidget()
        tabs.addTab(self._sonderaufgaben, "📝  Sonderaufgaben")

        # Tab 3 – AOCC Lagebericht
        self._aocc = _AoccWidget()
        tabs.addTab(self._aocc, "📣  AOCC Lagebericht")

        self._tabs = tabs
        root.addWidget(tabs, 1)

    # ── Navigation-Refresh ─────────────────────────────────────────────────
    def refresh(self):
        """Wird beim Tab-Wechsel in der Sidebar aufgerufen."""
        self._checklisten.refresh()
        self._aocc._refresh()
