"""
Haupt-Fenster (MainWindow)
SAP Fiori-Design mit Sidebar-Navigation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

from config import (
    APP_NAME, APP_VERSION,
    FIORI_SIDEBAR_BG, FIORI_BLUE, FIORI_WHITE, FIORI_LIGHT_BLUE, FIORI_TEXT
)
from gui.dashboard    import DashboardWidget
from gui.mitarbeiter  import MitarbeiterWidget
from gui.dienstplan   import DienstplanWidget
from gui.einstellungen import EinstellungenWidget


NAV_ITEMS = [
    ("🏠", "Dashboard",    0),
    ("👥", "Mitarbeiter",  1),
    ("📅", "Dienstplan",   2),
    ("💾", "Backup",       3),
    ("⚙️",  "Einstellungen", 4),
]


class SidebarButton(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(f"  {icon}  {text}", parent)
        self.setCheckable(True)
        self.setMinimumHeight(48)
        self.setFont(QFont("Arial", 12))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(False)

    def _apply_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {FIORI_BLUE};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    text-align: left;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #cdd5e0;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: rgba(255,255,255,0.1);
                    color: white;
                }}
            """)

    def setActive(self, active: bool):
        self._apply_style(active)
        self.setChecked(active)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        self._nav_buttons: list[SidebarButton] = []
        self._build_ui()
        self._navigate(0)

    # ── UI aufbauen ────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_content(), 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"background-color: {FIORI_SIDEBAR_BG};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 0, 8, 16)
        layout.setSpacing(4)

        # Logo-Bereich
        logo_frame = QFrame()
        logo_frame.setFixedHeight(70)
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(8, 12, 8, 4)

        title_lbl = QLabel("NESK3")
        title_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: white;")
        logo_layout.addWidget(title_lbl)

        sub_lbl = QLabel("DRK Flughafen Köln")
        sub_lbl.setFont(QFont("Arial", 9))
        sub_lbl.setStyleSheet("color: #8fadc8;")
        logo_layout.addWidget(sub_lbl)

        layout.addWidget(logo_frame)

        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #4a6480;")
        layout.addWidget(line)
        layout.addSpacing(8)

        # Navigations-Buttons
        for icon, label, idx in NAV_ITEMS:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda _, i=idx: self._navigate(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Version unten
        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet("color: #4a6480; font-size: 10px; padding: 0 8px;")
        layout.addWidget(ver_lbl)

        return sidebar

    def _build_content(self) -> QWidget:
        frame = QWidget()
        frame.setStyleSheet(f"background-color: #f5f6f7;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()

        # Pages
        self._dashboard_page   = DashboardWidget()
        self._mitarbeiter_page = MitarbeiterWidget()
        self._dienstplan_page  = DienstplanWidget()
        self._backup_page      = self._placeholder_page("💾 Backup", "Backup-Verwaltung wird implementiert.")
        self._settings_page    = EinstellungenWidget()

        for page in [self._dashboard_page, self._mitarbeiter_page,
                     self._dienstplan_page, self._backup_page, self._settings_page]:
            self._stack.addWidget(page)

        layout.addWidget(self._stack)
        return frame

    def _placeholder_page(self, title: str, msg: str) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {FIORI_TEXT};")
        lbl_msg = QLabel(msg)
        lbl_msg.setFont(QFont("Arial", 13))
        lbl_msg.setStyleSheet("color: #999;")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_msg)
        return w

    # ── Navigation ─────────────────────────────────────────────────────────────
    def _navigate(self, index: int):
        for i, btn in enumerate(self._nav_buttons):
            btn.setActive(i == index)
        self._stack.setCurrentIndex(index)

        if index == 0:
            self._dashboard_page.refresh()
        elif index == 2:
            # Dateibaum neu laden (greift ggf. geänderte Einstellungen ab)
            self._dienstplan_page.reload_tree()
