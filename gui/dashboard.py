"""
Dashboard-Widget
Zeigt Statistiken und Übersichten
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import FIORI_BLUE, FIORI_TEXT, FIORI_WHITE, FIORI_SUCCESS, FIORI_WARNING


class StatCard(QFrame):
    """Eine Statistik-Karte im SAP Fiori-Stil."""
    def __init__(self, title: str, value: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        top = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 11))
        title_lbl.setStyleSheet("color: #666; border: none;")
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Arial", 20))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        top.addWidget(title_lbl)
        top.addStretch()
        top.addWidget(icon_lbl)
        layout.addLayout(top)

        self._value_lbl = QLabel(value)
        self._value_lbl.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self._value_lbl.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(self._value_lbl)

    def set_value(self, value: str):
        self._value_lbl.setText(value)


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Titel
        title = QLabel("🏠 Dashboard")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {FIORI_TEXT};")
        layout.addWidget(title)

        subtitle = QLabel("Willkommen bei Nesk3 – DRK Flughafen Köln")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)

        # Statistik-Karten
        self._card_aktive  = StatCard("Aktive Mitarbeiter",     "–", "👥", FIORI_BLUE)
        self._card_gesamt  = StatCard("Mitarbeiter gesamt",     "–", "🗂️",  "#555")
        self._card_heute   = StatCard("Schichten heute",        "–", "📅", FIORI_SUCCESS)
        self._card_monat   = StatCard("Schichten diesen Monat", "–", "📊", FIORI_WARNING)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.addWidget(self._card_aktive, 0, 0)
        grid.addWidget(self._card_gesamt, 0, 1)
        grid.addWidget(self._card_heute,  1, 0)
        grid.addWidget(self._card_monat,  1, 1)
        layout.addLayout(grid)

        # DB-Statusanzeige
        self._db_status_lbl = QLabel("🔄 Datenbankverbindung wird geprüft...")
        self._db_status_lbl.setFont(QFont("Arial", 11))
        self._db_status_lbl.setStyleSheet(
            "background-color: white; border-radius: 6px; padding: 10px 14px;"
        )
        layout.addWidget(self._db_status_lbl)

        layout.addStretch()

    def refresh(self):
        """Aktualisiert alle Dashboard-Daten."""
        # Datenbankverbindung testen
        try:
            from database.connection import test_connection
            ok, info = test_connection()
            if ok:
                self._db_status_lbl.setText(f"✅ Datenbank verbunden  |  {info[:60]}")
                self._db_status_lbl.setStyleSheet(
                    "background-color: #e8f5e8; border-radius: 6px; "
                    "border-left: 4px solid #107e3e; padding: 10px 14px; color: #107e3e;"
                )
            else:
                self._db_status_lbl.setText(f"❌ Keine Datenbankverbindung: {info[:80]}")
                self._db_status_lbl.setStyleSheet(
                    "background-color: #fce8e8; border-radius: 6px; "
                    "border-left: 4px solid #bb0000; padding: 10px 14px; color: #bb0000;"
                )
        except Exception as e:
            self._db_status_lbl.setText(f"❌ Fehler: {e}")

        # TODO: Statistiken laden (Implementierung folgt)
