"""
Einstellungen-Widget
Anwendungseinstellungen verwalten (Ordner-Pfade etc.)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QMessageBox, QFileDialog, QGroupBox, QListWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from config import FIORI_BLUE, FIORI_TEXT


class EinstellungenWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Titel ──────────────────────────────────────────────────────
        title = QLabel("⚙️ Einstellungen")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {FIORI_TEXT};")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #ddd;")
        layout.addWidget(sep)

        # ── Gruppe: Dienstplan-Ordner ───────────────────────────────────
        grp = QGroupBox("📂 Dienstplan-Ordner")
        grp.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_layout = QVBoxLayout(grp)
        grp_layout.setSpacing(8)

        beschreibung = QLabel(
            "Ordner, der im Dienstplan-Tab als Dateibaum angezeigt wird.\n"
            "Alle .xlsx / .xls Dateien in diesem Ordner können direkt geladen werden."
        )
        beschreibung.setWordWrap(True)
        beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_layout.addWidget(beschreibung)

        ordner_row = QHBoxLayout()
        self._ordner_edit = QLineEdit()
        self._ordner_edit.setPlaceholderText("Pfad zum Dienstplan-Ordner …")
        self._ordner_edit.setMinimumHeight(32)
        ordner_row.addWidget(self._ordner_edit, 1)

        browse_btn = QPushButton("📂 Durchsuchen")
        browse_btn.setMinimumHeight(32)
        browse_btn.clicked.connect(self._browse_ordner)
        ordner_row.addWidget(browse_btn)

        grp_layout.addLayout(ordner_row)

        # Status-Anzeige für Pfad-Validierung
        self._pfad_status = QLabel("")
        self._pfad_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_layout.addWidget(self._pfad_status)

        self._ordner_edit.textChanged.connect(self._validate_path)

        layout.addWidget(grp)
        # ── Gruppe: Sonderaufgaben-Ordner ─────────────────────────────────
        grp_sa = QGroupBox("📝 Sonderaufgaben-Ordner")
        grp_sa.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_sa.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_sa_layout = QVBoxLayout(grp_sa)
        grp_sa_layout.setSpacing(8)

        sa_beschreibung = QLabel(
            "Ordner, der im Sonderaufgaben-Tab als Dateibaum angezeigt wird.\n"
            "Standardmäßig: 04_Tagesdienstpläne"
        )
        sa_beschreibung.setWordWrap(True)
        sa_beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_sa_layout.addWidget(sa_beschreibung)

        sa_row = QHBoxLayout()
        self._sa_ordner_edit = QLineEdit()
        self._sa_ordner_edit.setPlaceholderText("Pfad zum Sonderaufgaben-Ordner …")
        self._sa_ordner_edit.setMinimumHeight(32)
        sa_row.addWidget(self._sa_ordner_edit, 1)

        sa_browse_btn = QPushButton("📂 Durchsuchen")
        sa_browse_btn.setMinimumHeight(32)
        sa_browse_btn.clicked.connect(self._browse_sa_ordner)
        sa_row.addWidget(sa_browse_btn)

        grp_sa_layout.addLayout(sa_row)

        self._sa_pfad_status = QLabel("")
        self._sa_pfad_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_sa_layout.addWidget(self._sa_pfad_status)

        self._sa_ordner_edit.textChanged.connect(self._validate_sa_path)

        layout.addWidget(grp_sa)

        # ── Gruppe: AOCC Lagebericht-Datei ─────────────────────────────
        grp_aocc = QGroupBox("📣 AOCC Lagebericht-Datei")
        grp_aocc.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_aocc.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_aocc_layout = QVBoxLayout(grp_aocc)
        grp_aocc_layout.setSpacing(8)

        aocc_beschreibung = QLabel(
            "Pfad zur AOCC Lagebericht Excel-Datei (.xlsm).\n"
            "Wird im Tab '!Aufgaben Nacht > AOCC Lagebericht' geöffnet."
        )
        aocc_beschreibung.setWordWrap(True)
        aocc_beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_aocc_layout.addWidget(aocc_beschreibung)

        aocc_row = QHBoxLayout()
        self._aocc_edit = QLineEdit()
        self._aocc_edit.setPlaceholderText("Pfad zur AOCC Lagebericht.xlsm …")
        self._aocc_edit.setMinimumHeight(32)
        aocc_row.addWidget(self._aocc_edit, 1)

        aocc_browse_btn = QPushButton("📂 Durchsuchen")
        aocc_browse_btn.setMinimumHeight(32)
        aocc_browse_btn.clicked.connect(self._browse_aocc)
        aocc_row.addWidget(aocc_browse_btn)

        grp_aocc_layout.addLayout(aocc_row)

        self._aocc_status = QLabel("")
        self._aocc_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_aocc_layout.addWidget(self._aocc_status)

        self._aocc_edit.textChanged.connect(self._validate_aocc_path)

        layout.addWidget(grp_aocc)

        # ── Gruppe: Code 19 Datei ──────────────────────────────────────
        grp_c19 = QGroupBox("🚨 Code 19 Datei")
        grp_c19.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_c19.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_c19_layout = QVBoxLayout(grp_c19)
        grp_c19_layout.setSpacing(8)

        c19_beschreibung = QLabel(
            "Pfad zur Code-19-Excel-Datei (.xlsx).\n"
            "Wird im Tab '🚨 Code 19' geöffnet."
        )
        c19_beschreibung.setWordWrap(True)
        c19_beschreibung.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_c19_layout.addWidget(c19_beschreibung)

        c19_row = QHBoxLayout()
        self._c19_edit = QLineEdit()
        self._c19_edit.setPlaceholderText("Pfad zur Code 19.xlsx …")
        self._c19_edit.setMinimumHeight(32)
        c19_row.addWidget(self._c19_edit, 1)

        c19_browse_btn = QPushButton("📂 Durchsuchen")
        c19_browse_btn.setMinimumHeight(32)
        c19_browse_btn.clicked.connect(self._browse_c19)
        c19_row.addWidget(c19_browse_btn)

        grp_c19_layout.addLayout(c19_row)

        self._c19_status = QLabel("")
        self._c19_status.setStyleSheet("font-size: 10px; padding: 2px 0;")
        grp_c19_layout.addWidget(self._c19_status)

        self._c19_edit.textChanged.connect(self._validate_c19_path)

        layout.addWidget(grp_c19)

        # ── Gruppe: E-Mobby Fahrer ───────────────────────────────
        grp_emobby = QGroupBox("🛥 E-Mobby Fahrer")
        grp_emobby.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grp_emobby.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dce8f5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #0a5ba4;
            }
        """)
        grp_emobby_layout = QVBoxLayout(grp_emobby)
        grp_emobby_layout.setSpacing(8)

        emobby_desc = QLabel(
            "Namen der Mitarbeiter, die E-Mobby fahren dürfen.\n"
            "Beim Laden des Dienstplans werden diese automatisch erkannt."
        )
        emobby_desc.setWordWrap(True)
        emobby_desc.setStyleSheet("color: #555; font-size: 11px; font-weight: normal;")
        grp_emobby_layout.addWidget(emobby_desc)

        self._emobby_list = QListWidget()
        self._emobby_list.setFixedHeight(130)
        self._emobby_list.setStyleSheet(
            "border: 1px solid #c0c0c0; border-radius: 3px; "
            "font-size: 12px; background: white;"
        )
        grp_emobby_layout.addWidget(self._emobby_list)

        emobby_add_row = QHBoxLayout()
        self._emobby_input = QLineEdit()
        self._emobby_input.setPlaceholderText("Nachname eingeben …")
        self._emobby_input.setMinimumHeight(32)
        self._emobby_input.returnPressed.connect(self._add_emobby_entry)
        emobby_add_row.addWidget(self._emobby_input, 1)

        emobby_add_btn = QPushButton("+ Hinzufügen")
        emobby_add_btn.setMinimumHeight(32)
        emobby_add_btn.setStyleSheet(
            f"background-color: #107e3e; color: white; border: none; "
            f"border-radius: 3px; padding: 4px 12px; font-weight: bold;"
        )
        emobby_add_btn.clicked.connect(self._add_emobby_entry)
        emobby_add_row.addWidget(emobby_add_btn)

        emobby_remove_btn = QPushButton("🗑 Entfernen")
        emobby_remove_btn.setMinimumHeight(32)
        emobby_remove_btn.setStyleSheet(
            "background-color: #e0e0e0; color: #555; border: none; "
            "border-radius: 3px; padding: 4px 12px;"
        )
        emobby_remove_btn.clicked.connect(self._remove_emobby_entry)
        emobby_add_row.addWidget(emobby_remove_btn)
        grp_emobby_layout.addLayout(emobby_add_row)

        self._emobby_count_lbl = QLabel("")
        self._emobby_count_lbl.setStyleSheet("color: #555; font-size: 10px;")
        grp_emobby_layout.addWidget(self._emobby_count_lbl)

        layout.addWidget(grp_emobby)

        # ── Speichern-Button ───────────────────────────────────────────
        save_btn = QPushButton("💾 Einstellungen speichern")
        save_btn.setMinimumHeight(42)
        save_btn.setMaximumWidth(320)
        save_btn.setStyleSheet(
            f"background-color: {FIORI_BLUE}; color: white; font-size: 13px; "
            f"border-radius: 4px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

        layout.addStretch()

    # ------------------------------------------------------------------

    def _load_settings(self):
        try:
            from functions.settings_functions import get_setting
            self._ordner_edit.setText(get_setting('dienstplan_ordner'))
            self._sa_ordner_edit.setText(get_setting('sonderaufgaben_ordner'))
            self._aocc_edit.setText(get_setting('aocc_datei'))
            self._c19_edit.setText(get_setting('code19_datei'))
        except Exception:
            pass
        # E-Mobby Liste laden
        self._load_emobby_list()

    def _validate_path(self, text: str):
        if not text.strip():
            self._pfad_status.setText("")
            return
        if os.path.isdir(text.strip()):
            self._pfad_status.setText("✅ Ordner gefunden")
            self._pfad_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._pfad_status.setText("⚠️ Ordner nicht gefunden")
            self._pfad_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_ordner(self):
        current = self._ordner_edit.text().strip()
        start = current if os.path.isdir(current) else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(
            self, "Dienstplan-Ordner auswählen", start
        )
        if path:
            self._ordner_edit.setText(path)

    def _validate_sa_path(self, text: str):
        if not text.strip():
            self._sa_pfad_status.setText("")
            return
        if os.path.isdir(text.strip()):
            self._sa_pfad_status.setText("✅ Ordner gefunden")
            self._sa_pfad_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._sa_pfad_status.setText("⚠️ Ordner nicht gefunden")
            self._sa_pfad_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_sa_ordner(self):
        current = self._sa_ordner_edit.text().strip()
        start = current if os.path.isdir(current) else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(
            self, "Sonderaufgaben-Ordner auswählen", start
        )
        if path:
            self._sa_ordner_edit.setText(path)

    def _validate_aocc_path(self, text: str):
        if not text.strip():
            self._aocc_status.setText("")
            return
        if os.path.isfile(text.strip()):
            self._aocc_status.setText("✅ Datei gefunden")
            self._aocc_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._aocc_status.setText("⚠️ Datei nicht gefunden")
            self._aocc_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_aocc(self):
        current = self._aocc_edit.text().strip()
        start_dir = os.path.dirname(current) if os.path.isfile(current) else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "AOCC Lagebericht-Datei auswählen", start_dir,
            "Excel-Dateien (*.xlsx *.xlsm *.xls)"
        )
        if path:
            self._aocc_edit.setText(path)

    def _validate_c19_path(self, text: str):
        if not text.strip():
            self._c19_status.setText("")
            return
        if os.path.isfile(text.strip()):
            self._c19_status.setText("✅ Datei gefunden")
            self._c19_status.setStyleSheet("color: #107e3e; font-size: 10px; padding: 2px 0;")
        else:
            self._c19_status.setText("⚠️ Datei nicht gefunden")
            self._c19_status.setStyleSheet("color: #bb6600; font-size: 10px; padding: 2px 0;")

    def _browse_c19(self):
        current = self._c19_edit.text().strip()
        start_dir = os.path.dirname(current) if os.path.isfile(current) else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "Code-19-Datei auswählen", start_dir,
            "Excel-Dateien (*.xlsx *.xls)"
        )
        if path:
            self._c19_edit.setText(path)

    # ── E-Mobby Fahrer Verwaltung ────────────────────────────────

    def _load_emobby_list(self):
        try:
            from functions.emobby_functions import get_emobby_fahrer
            names = get_emobby_fahrer()
        except Exception:
            names = []
        self._emobby_list.clear()
        for n in names:
            self._emobby_list.addItem(n)
        self._emobby_count_lbl.setText(f"{len(names)} Fahrer in der Liste")

    def _add_emobby_entry(self):
        name = self._emobby_input.text().strip()
        if not name:
            return
        try:
            from functions.emobby_functions import add_emobby_fahrer
            added = add_emobby_fahrer(name)
            if added:
                self._emobby_input.clear()
                self._load_emobby_list()
            else:
                QMessageBox.information(self, "Bereits vorhanden",
                    f"'{name}' ist bereits in der Liste.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Hinzufügen:\n{e}")

    def _remove_emobby_entry(self):
        selected = self._emobby_list.currentItem()
        if not selected:
            QMessageBox.information(self, "Nichts ausgewählt",
                "Bitte zuerst einen Namen in der Liste auswählen.")
            return
        name = selected.text()
        antwort = QMessageBox.question(
            self, "Entfernen",
            f"'{name}' aus der E-Mobby-Liste entfernen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort != QMessageBox.StandardButton.Yes:
            return
        try:
            import json
            from functions.settings_functions import get_setting, set_setting
            db_raw = get_setting('emobby_fahrer', '')
            try:
                db_names = json.loads(db_raw) if db_raw else []
            except Exception:
                db_names = []
            if name in db_names:
                db_names.remove(name)
                set_setting('emobby_fahrer', json.dumps(db_names, ensure_ascii=False))
            self._load_emobby_list()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Entfernen:\n{e}")

    def _save(self):
        ordner = self._ordner_edit.text().strip()
        sa_ordner = self._sa_ordner_edit.text().strip()

        if ordner and not os.path.isdir(ordner):
            QMessageBox.warning(
                self, "Ungültiger Pfad",
                f"Dienstplan-Ordner existiert nicht:\n{ordner}\n\n"
                "Bitte einen gültigen Ordner auswählen."
            )
            return
        if sa_ordner and not os.path.isdir(sa_ordner):
            QMessageBox.warning(
                self, "Ungültiger Pfad",
                f"Sonderaufgaben-Ordner existiert nicht:\n{sa_ordner}\n\n"
                "Bitte einen gültigen Ordner auswählen."
            )
            return
        try:
            from functions.settings_functions import set_setting
            set_setting('dienstplan_ordner', ordner)
            set_setting('sonderaufgaben_ordner', sa_ordner)
            set_setting('aocc_datei', self._aocc_edit.text().strip())
            set_setting('code19_datei', self._c19_edit.text().strip())
            QMessageBox.information(
                self, "Gespeichert",
                "✅ Einstellungen wurden gespeichert.\n\n"
                "Die neuen Ordner werden beim nächsten Wechsel\n"
                "zum jeweiligen Tab angezeigt."
            )
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")
