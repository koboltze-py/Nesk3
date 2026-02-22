"""
Mitarbeiter-Widget
Mitarbeiter anzeigen, hinzufügen, bearbeiten, löschen
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QComboBox, QDateEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

from config import FIORI_BLUE, FIORI_TEXT, FIORI_ERROR
from database.models import Mitarbeiter


class MitarbeiterDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten eines Mitarbeiters."""
    def __init__(self, mitarbeiter: Mitarbeiter = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mitarbeiter" + (" bearbeiten" if mitarbeiter else " hinzufügen"))
        self.setMinimumWidth(420)
        self.result_ma: Mitarbeiter | None = None
        self._ma = mitarbeiter or Mitarbeiter()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        self._vorname    = QLineEdit(self._ma.vorname)
        self._nachname   = QLineEdit(self._ma.nachname)
        self._persnr     = QLineEdit(self._ma.personalnummer)
        self._email      = QLineEdit(self._ma.email)
        self._telefon    = QLineEdit(self._ma.telefon)

        self._position   = QComboBox()
        self._abteilung  = QComboBox()
        self._status     = QComboBox()
        self._status.addItems(["aktiv", "inaktiv", "beurlaubt"])
        self._status.setCurrentText(self._ma.status)

        self._eintrittsdatum = QDateEdit()
        self._eintrittsdatum.setCalendarPopup(True)
        self._eintrittsdatum.setDisplayFormat("dd.MM.yyyy")
        if self._ma.eintrittsdatum:
            self._eintrittsdatum.setDate(QDate(
                self._ma.eintrittsdatum.year,
                self._ma.eintrittsdatum.month,
                self._ma.eintrittsdatum.day
            ))
        else:
            self._eintrittsdatum.setDate(QDate.currentDate())

        # Positionen & Abteilungen aus DB laden
        try:
            from functions.mitarbeiter_functions import get_positionen, get_abteilungen
            for p in get_positionen():
                self._position.addItem(p)
            for a in get_abteilungen():
                self._abteilung.addItem(a)
        except Exception:
            self._position.addItems(["Notfallsanitäter", "Rettungssanitäter", "Sanitätshelfer"])
            self._abteilung.addItems(["Erste-Hilfe-Station", "Sanitätsdienst"])

        if self._ma.position:
            idx = self._position.findText(self._ma.position)
            if idx >= 0:
                self._position.setCurrentIndex(idx)
        if self._ma.abteilung:
            idx = self._abteilung.findText(self._ma.abteilung)
            if idx >= 0:
                self._abteilung.setCurrentIndex(idx)

        form.addRow("Vorname *:",       self._vorname)
        form.addRow("Nachname *:",      self._nachname)
        form.addRow("Personalnummer:",  self._persnr)
        form.addRow("Position:",        self._position)
        form.addRow("Abteilung:",       self._abteilung)
        form.addRow("E-Mail:",          self._email)
        form.addRow("Telefon:",         self._telefon)
        form.addRow("Eintrittsdatum:",  self._eintrittsdatum)
        form.addRow("Status:",          self._status)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Speichern")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet(f"background-color: {FIORI_BLUE}; color: white; font-size: 13px; border-radius: 4px;")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _save(self):
        if not self._vorname.text().strip() or not self._nachname.text().strip():
            QMessageBox.warning(self, "Pflichtfelder", "Vor- und Nachname sind Pflichtfelder.")
            return

        qd = self._eintrittsdatum.date()
        from datetime import date
        eintritt = date(qd.year(), qd.month(), qd.day())

        self._ma.vorname        = self._vorname.text().strip()
        self._ma.nachname       = self._nachname.text().strip()
        self._ma.personalnummer = self._persnr.text().strip()
        self._ma.position       = self._position.currentText()
        self._ma.abteilung      = self._abteilung.currentText()
        self._ma.email          = self._email.text().strip()
        self._ma.telefon        = self._telefon.text().strip()
        self._ma.eintrittsdatum = eintritt
        self._ma.status         = self._status.currentText()

        self.result_ma = self._ma
        self.accept()


class MitarbeiterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Titel + Aktionsleiste
        top = QHBoxLayout()
        title = QLabel("👥 Mitarbeiter")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {FIORI_TEXT};")
        top.addWidget(title)
        top.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍 Suchen...")
        self._search.setMinimumWidth(220)
        self._search.setMinimumHeight(36)
        self._search.textChanged.connect(self._search_changed)
        top.addWidget(self._search)

        add_btn = QPushButton("➕ Hinzufügen")
        add_btn.setMinimumHeight(36)
        add_btn.setStyleSheet(f"background-color: {FIORI_BLUE}; color: white; border-radius: 4px; padding: 0 12px;")
        add_btn.clicked.connect(self._add_mitarbeiter)
        top.addWidget(add_btn)

        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Aktualisieren")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.clicked.connect(self.refresh)
        top.addWidget(refresh_btn)

        layout.addLayout(top)

        # Tabelle
        self._table = QTableWidget()
        self._table.setColumnCount(9)
        self._table.setHorizontalHeaderLabels([
            "ID", "Vorname", "Nachname", "Personalnr.", "Position", "Abteilung", "Status", "Eintritt", "Export"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.doubleClicked.connect(self._edit_mitarbeiter)
        self._table.setStyleSheet("background-color: white; border-radius: 6px;")
        layout.addWidget(self._table)

        # Aktions-Buttons
        btn_row = QHBoxLayout()
        edit_btn = QPushButton("✏️ Bearbeiten")
        edit_btn.clicked.connect(self._edit_mitarbeiter)
        del_btn  = QPushButton("🗑️ Löschen")
        del_btn.setStyleSheet(f"color: {FIORI_ERROR};")
        del_btn.clicked.connect(self._delete_mitarbeiter)
        self._ausschluss_btn = QPushButton("🚫 Ausschließen")
        self._ausschluss_btn.setToolTip("Ausgewählten Mitarbeiter vom Word-Export ausschließen / einschließen")
        self._ausschluss_btn.clicked.connect(self._toggle_ausschluss)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        btn_row.addWidget(self._ausschluss_btn)
        btn_row.addStretch()
        self._row_count_lbl = QLabel("0 Einträge")
        self._row_count_lbl.setStyleSheet("color: #888;")
        btn_row.addWidget(self._row_count_lbl)
        layout.addLayout(btn_row)

    def refresh(self):
        """Lädt alle Mitarbeiter aus der DB."""
        # TODO: Implementierung folgt
        self._alle: list[Mitarbeiter] = []
        self._render_table(self._alle)

    def _render_table(self, mitarbeiter: list[Mitarbeiter]):
        try:
            from functions.settings_functions import get_ausgeschlossene_namen
            ausgeschlossen_set = set(get_ausgeschlossene_namen())
        except Exception:
            ausgeschlossen_set = set()

        self._table.setRowCount(len(mitarbeiter))
        for row, m in enumerate(mitarbeiter):
            vollname_low = f"{m.vorname} {m.nachname}".lower().strip()
            ist_ausgeschlossen = vollname_low in ausgeschlossen_set
            export_symbol = "🚫 Nein" if ist_ausgeschlossen else "✅ Ja"

            vals = [
                str(m.id or ""),
                m.vorname,
                m.nachname,
                m.personalnummer,
                m.position,
                m.abteilung,
                m.status,
                str(m.eintrittsdatum or ""),
                export_symbol,
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if col == 6:  # Status
                    if val == "aktiv":
                        item.setForeground(Qt.GlobalColor.darkGreen)
                    elif val == "inaktiv":
                        item.setForeground(Qt.GlobalColor.darkRed)
                if ist_ausgeschlossen:
                    item.setBackground(QColor('#fce8e8'))
                    item.setForeground(QColor('#bb0000'))
                self._table.setItem(row, col, item)
        self._row_count_lbl.setText(f"{len(mitarbeiter)} Einträge")

    def _search_changed(self, text: str):
        # TODO: Implementierung folgt
        pass

    def _get_vollname_selected(self) -> str | None:
        """Gibt 'Vorname Nachname' der ausgewählten Zeile zurück."""
        row = self._table.currentRow()
        if row < 0:
            return None
        vorname  = (self._table.item(row, 1) or QTableWidgetItem('')).text()
        nachname = (self._table.item(row, 2) or QTableWidgetItem('')).text()
        return f"{vorname} {nachname}".strip() or None

    def _toggle_ausschluss(self):
        """Schaltet den Ausschluss-Status des ausgewählten Mitarbeiters um."""
        vollname = self._get_vollname_selected()
        if not vollname:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Kein Mitarbeiter", "Bitte zunächst eine Zeile auswählen.")
            return
        try:
            from functions.settings_functions import toggle_ausgeschlossener_name
            jetzt_ausgeschlossen = toggle_ausgeschlossener_name(vollname)
            status = '🚫 ausgeschlossen' if jetzt_ausgeschlossen else '✅ eingeschlossen'
            self._ausschluss_btn.setText(
                "✅ Einschließen" if jetzt_ausgeschlossen else "🚫 Ausschließen"
            )
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Export-Status geändert",
                f"{vollname} ist jetzt {status} vom Word-Export."
            )
            self._render_table(self._alle)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Fehler", str(e))

    def _get_selected_id(self) -> int | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return int(item.text()) if item and item.text() else None

    def _add_mitarbeiter(self):
        # TODO: Implementierung folgt
        pass

    def _edit_mitarbeiter(self):
        # TODO: Implementierung folgt
        pass

    def _delete_mitarbeiter(self):
        # TODO: Implementierung folgt
        pass
