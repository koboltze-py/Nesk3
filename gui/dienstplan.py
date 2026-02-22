"""
Dienstplan-Widget
Schichten anzeigen, hinzufügen, bearbeiten, löschen
Excel-Import und Word-Export (Stärkemeldung)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QDateEdit, QTimeEdit, QTextEdit,
    QMessageBox, QFileDialog, QSpinBox, QFrame,
    QTreeView, QSplitter, QFileSystemModel,
    QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont, QColor

from config import FIORI_BLUE, FIORI_TEXT, FIORI_ERROR
from database.models import Dienstplan


class DienstplanDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten einer Schicht."""
    def __init__(self, schicht: Dienstplan = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schicht" + (" bearbeiten" if schicht else " hinzufügen"))
        self.setMinimumWidth(420)
        self.result_schicht: Dienstplan | None = None
        self._s = schicht or Dienstplan()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        # Mitarbeiter-Auswahl
        self._mitarbeiter_combo = QComboBox()
        self._ma_map: dict[str, int] = {}
        try:
            from functions.mitarbeiter_functions import get_alle_mitarbeiter
            for ma in get_alle_mitarbeiter(nur_aktive=True):
                label = f"{ma.vollname} ({ma.personalnummer})"
                self._mitarbeiter_combo.addItem(label)
                self._ma_map[label] = ma.id
                if ma.id == self._s.mitarbeiter_id:
                    self._mitarbeiter_combo.setCurrentText(label)
        except Exception:
            self._mitarbeiter_combo.addItem("(Kein Mitarbeiter verfügbar)")

        self._datum = QDateEdit()
        self._datum.setCalendarPopup(True)
        self._datum.setDisplayFormat("dd.MM.yyyy")
        if self._s.datum:
            self._datum.setDate(QDate(self._s.datum.year, self._s.datum.month, self._s.datum.day))
        else:
            self._datum.setDate(QDate.currentDate())

        self._start = QTimeEdit()
        self._start.setDisplayFormat("HH:mm")
        self._start.setTime(QTime(6, 0) if not self._s.start_uhrzeit
                            else QTime(self._s.start_uhrzeit.hour, self._s.start_uhrzeit.minute))

        self._end = QTimeEdit()
        self._end.setDisplayFormat("HH:mm")
        self._end.setTime(QTime(14, 0) if not self._s.end_uhrzeit
                          else QTime(self._s.end_uhrzeit.hour, self._s.end_uhrzeit.minute))

        self._position = QComboBox()
        try:
            from functions.mitarbeiter_functions import get_positionen
            self._position.addItems(get_positionen())
        except Exception:
            self._position.addItems(["Notfallsanitäter", "Rettungssanitäter"])
        if self._s.position:
            idx = self._position.findText(self._s.position)
            if idx >= 0:
                self._position.setCurrentIndex(idx)

        self._typ = QComboBox()
        self._typ.addItems(["regulär", "nacht", "bereitschaft"])
        self._typ.setCurrentText(self._s.schicht_typ)

        self._notizen = QTextEdit(self._s.notizen)
        self._notizen.setMaximumHeight(80)

        form.addRow("Mitarbeiter *:", self._mitarbeiter_combo)
        form.addRow("Datum *:",       self._datum)
        form.addRow("Von:",           self._start)
        form.addRow("Bis:",           self._end)
        form.addRow("Position:",      self._position)
        form.addRow("Schicht-Typ:",   self._typ)
        form.addRow("Notizen:",       self._notizen)
        layout.addLayout(form)

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
        selected_label = self._mitarbeiter_combo.currentText()
        ma_id = self._ma_map.get(selected_label)
        if not ma_id:
            QMessageBox.warning(self, "Fehler", "Bitte einen Mitarbeiter auswählen.")
            return

        from datetime import date, time
        qd = self._datum.date()
        qs = self._start.time()
        qe = self._end.time()

        self._s.mitarbeiter_id  = ma_id
        self._s.datum           = date(qd.year(), qd.month(), qd.day())
        self._s.start_uhrzeit   = time(qs.hour(), qs.minute())
        self._s.end_uhrzeit     = time(qe.hour(), qe.minute())
        self._s.position        = self._position.currentText()
        self._s.schicht_typ     = self._typ.currentText()
        self._s.notizen         = self._notizen.toPlainText().strip()

        self.result_schicht = self._s
        self.accept()


# Dienste die zum Standard gehören – Sonderdienste werden im Dialog angezeigt
_STANDARD_DIENSTE = frozenset({'N', 'N10', 'T', 'T10', 'DT', 'DT3', 'DN', 'DN3'})


class ExportDialog(QDialog):
    """Dialog für Word-Export: Zeitraum, PAX-Zahl, Ausgabepfad, Sonderdienst-Filter."""

    def __init__(self, parsed_data: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Word-Export – Stärkemeldung")
        self.setMinimumWidth(500)
        self.setMinimumHeight(460)
        self._parsed_data = parsed_data or {}
        self.result: dict | None = None
        self._checkboxen: list[tuple] = []   # (QCheckBox, vollname_lower)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form   = QFormLayout()
        form.setSpacing(10)

        today = QDate.currentDate()

        self._von = QDateEdit(today)
        self._von.setCalendarPopup(True)
        self._von.setDisplayFormat("dd.MM.yyyy")

        self._bis = QDateEdit(today)
        self._bis.setCalendarPopup(True)
        self._bis.setDisplayFormat("dd.MM.yyyy")

        self._pax = QSpinBox()
        self._pax.setRange(0, 99999)
        self._pax.setValue(0)

        self._pfad_lbl = QLabel("(noch kein Pfad gewählt)")
        self._pfad_lbl.setWordWrap(True)
        self._pfad_lbl.setStyleSheet("color: #555;")
        pfad_btn = QPushButton("📂 Speicherort wählen …")
        pfad_btn.clicked.connect(self._choose_path)
        self._ausgabe_pfad = ""

        form.addRow("Von:",       self._von)
        form.addRow("Bis:",       self._bis)
        form.addRow("PAX-Zahl:", self._pax)
        form.addRow("Datei:",    pfad_btn)
        form.addRow("",          self._pfad_lbl)
        layout.addLayout(form)

        # ── Sonderdienst-Abschnitt ─────────────────────────────────────
        sonder_personen = []
        for listen_key in ('betreuer', 'dispo'):
            for p in self._parsed_data.get(listen_key, []):
                dk = (p.get('dienst_kategorie') or '').upper()
                if dk not in _STANDARD_DIENSTE:
                    sonder_personen.append(p)

        if sonder_personen:
            sep1 = QFrame()
            sep1.setFrameShape(QFrame.Shape.HLine)
            sep1.setStyleSheet("color: #ddd;")
            layout.addWidget(sep1)

            sonder_lbl = QLabel(
                "⚠️  Mitarbeiter mit Sonderdiensten:\n"
                "   Haken setzen = vom Export ausschließen"
            )
            sonder_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            sonder_lbl.setStyleSheet("color: #555; padding: 2px 0;")
            layout.addWidget(sonder_lbl)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMaximumHeight(160)
            scroll.setStyleSheet(
                "QScrollArea { border: 1px solid #dce8f5; border-radius: 4px; }"
            )
            inner        = QWidget()
            inner_layout = QVBoxLayout(inner)
            inner_layout.setSpacing(3)
            inner_layout.setContentsMargins(8, 6, 8, 6)

            try:
                from functions.settings_functions import get_ausgeschlossene_namen
                settings_ausgeschlossen = set(get_ausgeschlossene_namen())
            except Exception:
                settings_ausgeschlossen = set()

            for p in sonder_personen:
                vollname_lower = p.get('vollname', '').lower()
                dienst         = p.get('dienst_kategorie', '') or '?'
                anzeige        = p.get('anzeigename', p.get('vollname', ''))
                cb = QCheckBox(f"  {anzeige}  [{dienst}]")
                cb.setFont(QFont("Arial", 10))
                # vorbelegen: ausschließen wenn bereits in Einstellungen
                cb.setChecked(vollname_lower in settings_ausgeschlossen)
                inner_layout.addWidget(cb)
                self._checkboxen.append((cb, vollname_lower))

            inner_layout.addStretch()
            scroll.setWidget(inner)
            layout.addWidget(scroll)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #ddd;")
        layout.addWidget(sep2)

        btn_row = QHBoxLayout()
        export_btn = QPushButton("📤 Exportieren")
        export_btn.setMinimumHeight(40)
        export_btn.setStyleSheet(
            f"background-color: {FIORI_BLUE}; color: white; font-size: 13px; border-radius: 4px;"
        )
        export_btn.clicked.connect(self._export)
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(export_btn)
        layout.addLayout(btn_row)

    def _choose_path(self):
        today_str = datetime.now().strftime("%d.%m.%Y")
        default   = os.path.join(os.path.expanduser("~"), "Desktop",
                                 f"Stärkemeldung {today_str}.docx")
        path, _ = QFileDialog.getSaveFileName(
            self, "Ausgabedatei wählen", default,
            "Word-Dokument (*.docx)"
        )
        if path:
            self._ausgabe_pfad = path
            self._pfad_lbl.setText(path)

    def _export(self):
        if not self._ausgabe_pfad:
            QMessageBox.warning(self, "Kein Pfad", "Bitte zuerst einen Speicherort wählen.")
            return
        qv = self._von.date()
        qb = self._bis.date()
        ausgeschlossene = {vn for cb, vn in self._checkboxen if cb.isChecked()}
        self.result = {
            'von_datum':               datetime(qv.year(), qv.month(), qv.day()),
            'bis_datum':               datetime(qb.year(), qb.month(), qb.day()),
            'pax_zahl':                self._pax.value(),
            'ausgabe_pfad':            self._ausgabe_pfad,
            'ausgeschlossene_vollnamen': ausgeschlossene,
        }
        self.accept()


class DienstplanWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parsed_data: dict | None  = None
        self._alle: list[Dienstplan]    = []
        self._fs_model: QFileSystemModel | None = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(8)

        # ── Titelzeile ─────────────────────────────────────────────────
        top = QHBoxLayout()
        title = QLabel("📅 Dienstplan")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {FIORI_TEXT};")
        top.addWidget(title)
        top.addStretch()

        word_btn = QPushButton("📤 Word exportieren")
        word_btn.setMinimumHeight(36)
        word_btn.setStyleSheet(
            f"background-color: {FIORI_BLUE}; color: white; "
            f"border-radius: 4px; padding: 0 12px;"
        )
        word_btn.clicked.connect(self._word_exportieren)
        top.addWidget(word_btn)

        reload_btn = QPushButton("🔄")
        reload_btn.setToolTip("Ordner-Ansicht neu laden")
        reload_btn.setMinimumHeight(36)
        reload_btn.clicked.connect(self.reload_tree)
        top.addWidget(reload_btn)

        outer.addLayout(top)

        # ── Status-Label ───────────────────────────────────────────────
        self._status_lbl = QLabel("Doppelklick auf eine Datei im Baum, um sie zu laden.")
        self._status_lbl.setFont(QFont("Arial", 10))
        self._status_lbl.setStyleSheet("color: #888; padding: 2px 0;")
        outer.addWidget(self._status_lbl)

        # ── Splitter: Dateibaum links | Tabelle rechts ─────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)

        # Linke Seite: Dateibaum
        tree_panel = QWidget()
        tree_panel.setMinimumWidth(180)
        tree_panel.setMaximumWidth(360)
        tree_layout = QVBoxLayout(tree_panel)
        tree_layout.setContentsMargins(0, 0, 6, 0)
        tree_layout.setSpacing(4)

        tree_header = QLabel("📂 Dienstpläne")
        tree_header.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        tree_header.setStyleSheet(f"color: {FIORI_TEXT}; padding: 4px 0;")
        tree_layout.addWidget(tree_header)

        self._tree = QTreeView()
        self._tree.setStyleSheet("""
            QTreeView {
                background-color: white;
                border: 1px solid #dce8f5;
                border-radius: 6px;
                font-size: 12px;
            }
            QTreeView::item {
                padding: 3px 2px;
            }
            QTreeView::item:selected {
                background-color: #dce8f5;
                color: #0a5ba4;
            }
            QTreeView::item:hover {
                background-color: #f0f4f8;
            }
        """)
        self._tree.setAnimated(True)
        self._tree.setSortingEnabled(True)
        self._tree.activated.connect(self._on_tree_activated)
        tree_layout.addWidget(self._tree, 1)

        self._ordner_lbl = QLabel("")
        self._ordner_lbl.setWordWrap(True)
        self._ordner_lbl.setStyleSheet("color: #aaa; font-size: 9px; padding: 2px;")
        tree_layout.addWidget(self._ordner_lbl)

        splitter.addWidget(tree_panel)

        # Rechte Seite: Tabelle
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(4)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            "Kategorie", "Name", "Dienst", "Von", "Bis"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("background-color: white; border-radius: 6px;")
        right_layout.addWidget(self._table, 1)

        self._row_count_lbl = QLabel("0 Einträge")
        self._row_count_lbl.setStyleSheet("color: #888;")
        right_layout.addWidget(
            self._row_count_lbl,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        splitter.addWidget(right_panel)
        splitter.setSizes([260, 900])
        outer.addWidget(splitter, 1)

        # Baum beim ersten Aufbau initialisieren
        self._setup_tree()

    # ------------------------------------------------------------------
    # Dateibaum
    # ------------------------------------------------------------------

    def _setup_tree(self):
        """Dateibaum für den konfigurierten Ordner aufbauen."""
        try:
            from functions.settings_functions import get_setting
            ordner = get_setting('dienstplan_ordner')
        except Exception:
            ordner = ''

        if not ordner or not os.path.isdir(ordner):
            self._ordner_lbl.setText(
                "⚠️ Kein gültiger Ordner konfiguriert.\n"
                "Bitte unter ➡ Einstellungen einen Ordner festlegen."
            )
            self._ordner_lbl.setStyleSheet("color: #bb6600; font-size: 10px; padding: 4px;")
            return

        self._fs_model = QFileSystemModel(self)
        self._fs_model.setNameFilters(['*.xlsx', '*.xls'])
        self._fs_model.setNameFilterDisables(False)
        root_idx = self._fs_model.setRootPath(ordner)

        self._tree.setModel(self._fs_model)
        self._tree.setRootIndex(root_idx)

        # Nur Name-Spalte anzeigen
        for col in range(1, 4):
            self._tree.hideColumn(col)
        self._tree.header().setVisible(False)

        self._ordner_lbl.setText(ordner)
        self._ordner_lbl.setStyleSheet("color: #aaa; font-size: 9px; padding: 2px;")

    def reload_tree(self):
        """Ordner-Konfiguration neu lesen und Baum neu aufbauen."""
        if self._fs_model is not None:
            self._tree.setModel(None)
            self._fs_model.deleteLater()
            self._fs_model = None
        self._ordner_lbl.setText("")
        self._setup_tree()

    def _on_tree_activated(self, index):
        """Eintrag im Baum aktiviert (Enter / Doppelklick)."""
        if self._fs_model is None:
            return
        path = self._fs_model.filePath(index)
        if os.path.isfile(path) and path.lower().endswith(('.xlsx', '.xls')):
            self._laden_excel_datei(path)

    # ------------------------------------------------------------------
    # Datenladen
    # ------------------------------------------------------------------

    def refresh(self):
        self._alle = []
        self._table.setRowCount(0)
        self._row_count_lbl.setText("0 Einträge")

    def _render_table_parsed(self, data: dict):
        """Tabelleninhalt aus geparsten Excel-Daten aufbauen."""
        alle_personen = (
            [('Dispo',     p) for p in data.get('dispo',    [])] +
            [('Betreuer',  p) for p in data.get('betreuer', [])] +
            [('Krank',     p) for p in data.get('kranke',   [])]
        )
        self._table.setRowCount(len(alle_personen))

        farben = {
            'Dispo':    QColor('#dce8f5'),
            'Betreuer': QColor('#ffffff'),
            'Krank':    QColor('#fce8e8'),
        }
        text_farben = {
            'Dispo':    QColor('#0a5ba4'),
            'Betreuer': QColor('#1a1a1a'),
            'Krank':    QColor('#bb0000'),
        }

        for row, (kategorie, p) in enumerate(alle_personen):
            vals = [
                kategorie,
                p.get('anzeigename', ''),
                p.get('dienst_kategorie', ''),
                p.get('start_zeit', '') or '',
                p.get('end_zeit',   '') or '',
            ]
            bg = farben.get(kategorie, QColor('#ffffff'))
            fg = text_farben.get(kategorie, QColor('#1a1a1a'))

            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setBackground(bg)
                item.setForeground(fg)
                self._table.setItem(row, col, item)

            if p.get('ist_bulmorfahrer'):
                for col in range(5):
                    self._table.item(row, col).setBackground(QColor('#fff3b0'))

        betreuer_n = len(data.get('betreuer', []))
        dispo_n    = len(data.get('dispo',    []))
        kranke_n   = len(data.get('kranke',   []))
        self._row_count_lbl.setText(
            f"{betreuer_n} Betreuer  |  {dispo_n} Dispo  |  {kranke_n} Krank"
        )

    # ------------------------------------------------------------------
    # Excel-Import
    # ------------------------------------------------------------------

    def _laden_excel_datei(self, path: str):
        """Excel-Datei einlesen und Tabelle befüllen."""
        self._status_lbl.setText("⏳ Datei wird eingelesen …")
        self._status_lbl.setStyleSheet("color: #555; padding: 2px 0;")
        self._status_lbl.repaint()

        try:
            from functions.dienstplan_parser import DienstplanParser
            result = DienstplanParser(path).parse()

            if not result['success']:
                QMessageBox.critical(
                    self, "Fehler beim Einlesen",
                    f"Die Datei konnte nicht geparst werden:\n\n{result['error']}"
                )
                self._status_lbl.setText("❌ Fehler beim Einlesen.")
                self._status_lbl.setStyleSheet("color: #bb0000; padding: 2px 0;")
                return

            self._parsed_data = result
            self._render_table_parsed(result)

            unbekannte = result.get('unbekannte_dienste', [])
            if unbekannte:
                QMessageBox.warning(
                    self, "Unbekannte Dienst-Kürzel",
                    "Folgende Dienst-Kürzel wurden nicht erkannt:\n"
                    + "\n".join(f"  • {d}" for d in sorted(unbekannte))
                    + "\n\nSie werden trotzdem angezeigt."
                )

            dateiname = os.path.basename(path)
            self._status_lbl.setText(
                f"✅ Geladen: {dateiname}  |  "
                f"{len(result['betreuer'])} Betreuer, "
                f"{len(result['dispo'])} Dispo, "
                f"{len(result['kranke'])} Krank"
            )
            self._status_lbl.setStyleSheet("color: #107e3e; padding: 2px 0;")

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Unerwarteter Fehler:\n{e}")
            self._status_lbl.setText(f"❌ {e}")
            self._status_lbl.setStyleSheet("color: #bb0000; padding: 2px 0;")

    # ------------------------------------------------------------------
    # Word-Export
    # ------------------------------------------------------------------

    def _word_exportieren(self):
        if not self._parsed_data:
            QMessageBox.information(
                self, "Kein Dienstplan",
                "Bitte zuerst eine Datei im Dateibaum auswählen (Doppelklick)."
            )
            return

        dlg = ExportDialog(parsed_data=self._parsed_data, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.result:
            return

        params = dlg.result
        try:
            from functions.staerkemeldung_export import StaerkemeldungExport
            exporter = StaerkemeldungExport(
                dienstplan_data          = self._parsed_data,
                ausgabe_pfad             = params['ausgabe_pfad'],
                von_datum                = params['von_datum'],
                bis_datum                = params['bis_datum'],
                pax_zahl                 = params['pax_zahl'],
                ausgeschlossene_vollnamen = params.get('ausgeschlossene_vollnamen', set()),
            )
            pfad, warnungen = exporter.export()

            if warnungen:
                QMessageBox.warning(
                    self, "Hinweise",
                    "Export abgeschlossen mit Hinweisen:\n\n" + "\n".join(warnungen)
                )

            QMessageBox.information(
                self, "Export erfolgreich",
                f"✅ Stärkemeldung gespeichert unter:\n{pfad}"
            )
            self._status_lbl.setText(f"✅ Word-Export: {os.path.basename(pfad)}")
            self._status_lbl.setStyleSheet("color: #107e3e; padding: 2px 0;")

        except Exception as e:
            QMessageBox.critical(self, "Fehler beim Export", f"Fehler:\n{e}")
            self._status_lbl.setText(f"❌ Export-Fehler: {e}")
            self._status_lbl.setStyleSheet("color: #bb0000; padding: 2px 0;")

    # ------------------------------------------------------------------
    # Stubs (DB-Anbindung folgt)
    # ------------------------------------------------------------------

    def _render_table(self, schichten: list[Dienstplan]):
        pass

    def _get_selected_id(self) -> int | None:
        return None

    def _add_schicht(self):
        pass

    def _edit_schicht(self):
        pass

    def _delete_schicht(self):
        pass
