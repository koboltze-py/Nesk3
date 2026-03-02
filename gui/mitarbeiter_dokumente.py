"""
Mitarbeiter-Dokumente Widget
Öffnen, Bearbeiten und Erstellen von Mitarbeiter-Dokumenten
mit einheitlicher DRK-Kopf-/Fußzeile
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QMessageBox, QFrame, QScrollArea, QSizePolicy, QInputDialog,
    QFileDialog
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont, QColor, QIcon

from config import FIORI_BLUE, FIORI_TEXT, FIORI_WHITE, FIORI_BORDER

from functions.mitarbeiter_dokumente_functions import (
    KATEGORIEN, DOKUMENTE_BASIS, VORLAGE_PFAD,
    lade_dokumente_nach_kategorie,
    erstelle_dokument_aus_vorlage,
    oeffne_datei,
    loesche_dokument,
    umbenennen_dokument,
    sicherungsordner,
)


# ── Hilfsstile ────────────────────────────────────────────────────────────────
def _btn(text: str, color: str = FIORI_BLUE, hover: str = "#0057b8") -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(32)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {color}; color: white; border: none;
            border-radius: 4px; padding: 4px 14px; font-size: 12px;
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:disabled {{ background: #bbb; color: #888; }}
    """)
    return btn


def _btn_light(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(32)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton { background:#eee; color:#333; border:none;
            border-radius:4px; padding:4px 14px; font-size:12px; }
        QPushButton:hover { background:#ddd; }
        QPushButton:disabled { background:#f5f5f5; color:#bbb; }
    """)
    return btn


# ══════════════════════════════════════════════════════════════════════════════
#  Dialog: Neues Dokument erstellen
# ══════════════════════════════════════════════════════════════════════════════

class _NeuesDokumentDialog(QDialog):
    """Formulardialog zum Erstellen eines neuen Mitarbeiter-Dokuments."""

    def __init__(self, vorkategorie: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neues Dokument erstellen")
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        layout = QVBoxLayout(self)
        fl = QFormLayout()
        fl.setSpacing(8)

        # Kategorie
        self._kategorie = QComboBox()
        for kat in KATEGORIEN:
            self._kategorie.addItem(kat)
        if vorkategorie in KATEGORIEN:
            self._kategorie.setCurrentText(vorkategorie)
        fl.addRow("Kategorie:", self._kategorie)

        # Titel
        self._titel = QLineEdit()
        self._titel.setPlaceholderText("z.B. Stellungnahme zum Diensteinsatz")
        fl.addRow("Titel des Dokuments:", self._titel)

        # Mitarbeiter
        self._mitarbeiter = QLineEdit()
        self._mitarbeiter.setPlaceholderText("Vor- und Nachname")
        fl.addRow("Mitarbeiter:", self._mitarbeiter)

        # Datum
        self._datum = QDateEdit()
        self._datum.setCalendarPopup(True)
        self._datum.setDisplayFormat("dd.MM.yyyy")
        self._datum.setDate(QDate.currentDate())
        fl.addRow("Datum:", self._datum)

        layout.addLayout(fl)

        # Inhalt
        layout.addWidget(QLabel("Inhalt / Text des Dokuments:"))
        self._inhalt = QTextEdit()
        self._inhalt.setPlaceholderText(
            "Hier den vollständigen Text eingeben...\n\n"
            "Alle Absätze werden automatisch mit der DRK-Kopf-/Fußzeile formatiert."
        )
        self._inhalt.setMinimumHeight(180)
        self._inhalt.setStyleSheet(
            "QTextEdit { border:1px solid #ccc; border-radius:4px; "
            "padding:6px; font-size:13px; }"
        )
        layout.addWidget(self._inhalt)

        # Info-Box Vorlage
        vorlage_ok = os.path.isfile(VORLAGE_PFAD)
        info = QLabel(
            "✅ Kopf-/Fußzeile aus DRK-Vorlage wird übernommen."
            if vorlage_ok else
            "⚠ Vorlage nicht gefunden! Dokument ohne DRK-Kopf-/Fußzeile erstellt.\n"
            f"Erwartet: {VORLAGE_PFAD}"
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"background:{'#e8f5e9' if vorlage_ok else '#fff3e0'};"
            f"color:{'#256029' if vorlage_ok else '#7f5000'};"
            "border-radius:4px; padding:6px 10px; font-size:11px;"
        )
        layout.addWidget(info)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("📄 Erstellen")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_accept(self):
        if not self._titel.text().strip():
            QMessageBox.warning(self, "Pflichtfeld", "Bitte einen Titel eingeben.")
            return
        if not self._mitarbeiter.text().strip():
            QMessageBox.warning(self, "Pflichtfeld", "Bitte einen Mitarbeiternamen eingeben.")
            return
        self.accept()

    def get_data(self) -> dict:
        return dict(
            kategorie   = self._kategorie.currentText(),
            titel       = self._titel.text().strip(),
            mitarbeiter = self._mitarbeiter.text().strip(),
            datum       = self._datum.date().toString("dd.MM.yyyy"),
            inhalt      = self._inhalt.toPlainText(),
        )


# ══════════════════════════════════════════════════════════════════════════════
#  Dialog: Dokument bearbeiten (Text-Popup)
# ══════════════════════════════════════════════════════════════════════════════

class _DokumentBearbeitenDialog(QDialog):
    """
    Öffnet ein bestehendes .docx/.txt als editierbares Popup.
    Bei .docx werden die Absätze ausgelesen; bei .txt der Rohtext.
    Beim Speichern wird das Dokument neu über die Vorlage erstellt.
    """

    def __init__(self, eintrag: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Bearbeiten – {eintrag['name']}")
        self.setMinimumWidth(620)
        self.setMinimumHeight(520)
        self._eintrag = eintrag
        layout = QVBoxLayout(self)

        # Originalinhalt laden
        pfad = eintrag["pfad"]
        original = ""
        try:
            if pfad.lower().endswith(".docx"):
                from docx import Document as _Doc
                doc = _Doc(pfad)
                original = "\n".join(p.text for p in doc.paragraphs)
            elif pfad.lower().endswith(".txt"):
                with open(pfad, encoding="utf-8", errors="replace") as f:
                    original = f.read()
        except Exception as e:
            original = f"[Fehler beim Laden: {e}]"

        # Meta-Zeile
        meta = QLabel(f"📄  {eintrag['name']}   |   Zuletzt geändert: {eintrag['geaendert']}")
        meta.setStyleSheet("color:#555; font-size:11px; padding:2px 0 8px 0;")
        layout.addWidget(meta)

        # Textbereich
        self._editor = QTextEdit()
        self._editor.setPlainText(original)
        self._editor.setStyleSheet(
            "QTextEdit { border:1px solid #ccc; border-radius:4px; "
            "padding:8px; font-size:13px; }"
        )
        layout.addWidget(self._editor, 1)

        # Hinweis
        hint = QLabel(
            "ℹ️  Beim Übernehmen wird das Dokument mit diesem Text und der DRK-Vorlage neu erstellt."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "background:#e3f2fd; color:#154360; border-radius:4px; "
            "padding:6px 10px; font-size:11px;"
        )
        layout.addWidget(hint)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Save).setText("💾 Übernehmen & neu erstellen")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_inhalt(self) -> str:
        return self._editor.toPlainText()


# ══════════════════════════════════════════════════════════════════════════════
#  Haupt-Widget
# ══════════════════════════════════════════════════════════════════════════════

class MitarbeiterDokumenteWidget(QWidget):
    """
    Haupt-Widget für den Mitarbeiter-Dokumente-Bereich.
    Links: Kategorieliste
    Rechts: Dateiliste der gewählten Kategorie + Aktions-Buttons
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._akt_kategorie: str = KATEGORIEN[0]
        self._dokumente: dict[str, list[dict]] = {}
        self._build_ui()
        self.refresh()

    # ── UI aufbauen ───────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Titelleiste ────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(52)
        header.setStyleSheet(f"background:{FIORI_BLUE}; border:none;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        lbl = QLabel("👥  Mitarbeiter-Dokumente")
        lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl.setStyleSheet("color:white; background:transparent;")
        hl.addWidget(lbl)
        hl.addStretch()

        btn_ordner = QPushButton("📂 Ordner öffnen")
        btn_ordner.setFixedHeight(30)
        btn_ordner.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ordner.setToolTip("Mitarbeiterdokumente-Ordner im Explorer öffnen")
        btn_ordner.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.15);color:white;"
            "border:1px solid rgba(255,255,255,0.3);border-radius:4px;padding:4px 10px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.25);}"
        )
        btn_ordner.clicked.connect(self._ordner_oeffnen)
        hl.addWidget(btn_ordner)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedSize(30, 30)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setToolTip("Dateiliste aktualisieren")
        btn_refresh.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.15);color:white;"
            "border:1px solid rgba(255,255,255,0.3);border-radius:4px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.25);}"
        )
        btn_refresh.clicked.connect(self.refresh)
        hl.addWidget(btn_refresh)
        layout.addWidget(header)

        # ── Splitter (Links + Rechts) ──────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background:#ddd; width:1px; }")
        layout.addWidget(splitter, 1)

        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_hauptbereich())
        splitter.setSizes([220, 800])

    def _build_sidebar(self) -> QWidget:
        """Linke Spalte: Kategorie-Liste."""
        w = QWidget()
        w.setMinimumWidth(180)
        w.setMaximumWidth(280)
        w.setStyleSheet("background:#f0f2f5;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lbl = QLabel("  Kategorien")
        lbl.setFixedHeight(36)
        lbl.setStyleSheet(
            "background:#e0e4ea; color:#444; font-weight:bold; "
            "font-size:12px; padding-left:12px;"
        )
        layout.addWidget(lbl)

        self._kat_list = QListWidget()
        self._kat_list.setStyleSheet("""
            QListWidget {
                background:#f0f2f5;
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #e0e0e0;
                color: #333;
            }
            QListWidget::item:selected {
                background: #1565a8;
                color: white;
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background: #dce8f8;
            }
        """)
        for kat in KATEGORIEN:
            self._kat_list.addItem(f"📁  {kat}")
        self._kat_list.setCurrentRow(0)
        self._kat_list.currentRowChanged.connect(self._kategorie_gewaehlt)
        layout.addWidget(self._kat_list, 1)

        # Vorlage-Info
        vorlage_ok = os.path.isfile(VORLAGE_PFAD)
        status_lbl = QLabel(
            "  ✅ Vorlage gefunden" if vorlage_ok else "  ⚠ Vorlage fehlt"
        )
        status_lbl.setFixedHeight(28)
        status_lbl.setStyleSheet(
            f"background:{'#e8f5e9' if vorlage_ok else '#fff3e0'};"
            f"color:{'#2d6a2d' if vorlage_ok else '#7a5000'};"
            "font-size:10px; padding-left:10px;"
        )
        status_lbl.setToolTip(VORLAGE_PFAD)
        layout.addWidget(status_lbl)

        return w

    def _build_hauptbereich(self) -> QWidget:
        """Rechte Spalte: Dateiliste + Aktionsleiste."""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Aktions-Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._btn_neu = _btn("＋  Neues Dokument", FIORI_BLUE)
        self._btn_neu.setToolTip("Neues Dokument mit DRK-Kopf-/Fußzeile aus Vorlage erstellen")
        self._btn_neu.clicked.connect(lambda: self._neues_dokument())
        btn_row.addWidget(self._btn_neu)

        self._btn_oeffnen = _btn_light("📂  Öffnen")
        self._btn_oeffnen.setToolTip("Ausgewähltes Dokument mit Word / Standard-App öffnen")
        self._btn_oeffnen.setEnabled(False)
        self._btn_oeffnen.clicked.connect(self._dokument_oeffnen)
        btn_row.addWidget(self._btn_oeffnen)

        self._btn_bearbeiten = _btn_light("✏  Bearbeiten")
        self._btn_bearbeiten.setToolTip("Dokumentinhalt im Popup bearbeiten und neu speichern")
        self._btn_bearbeiten.setEnabled(False)
        self._btn_bearbeiten.clicked.connect(self._dokument_bearbeiten)
        btn_row.addWidget(self._btn_bearbeiten)

        self._btn_umbenennen = _btn_light("🔤  Umbenennen")
        self._btn_umbenennen.setToolTip("Datei umbenennen")
        self._btn_umbenennen.setEnabled(False)
        self._btn_umbenennen.clicked.connect(self._dokument_umbenennen)
        btn_row.addWidget(self._btn_umbenennen)

        self._btn_loeschen = _btn_light("🗑  Löschen")
        self._btn_loeschen.setToolTip("Ausgewähltes Dokument dauerhaft löschen")
        self._btn_loeschen.setEnabled(False)
        self._btn_loeschen.setStyleSheet(
            "QPushButton{background:#eee;color:#333;border:none;"
            "border-radius:4px;padding:4px 14px;font-size:12px;}"
            "QPushButton:hover{background:#ffcccc;color:#a00;}"
            "QPushButton:disabled{background:#f5f5f5;color:#bbb;}"
        )
        self._btn_loeschen.clicked.connect(self._dokument_loeschen)
        btn_row.addWidget(self._btn_loeschen)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Kategorie-Titel
        self._kat_label = QLabel()
        self._kat_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self._kat_label.setStyleSheet(f"color:{FIORI_TEXT}; padding:4px 0;")
        layout.addWidget(self._kat_label)

        # Tabelle
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Dateiname", "Zuletzt geändert", "Typ"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("QTableWidget{border:1px solid #ddd;font-size:12px;}")
        self._table.verticalHeader().setVisible(False)
        self._table.itemSelectionChanged.connect(self._auswahl_geaendert)
        self._table.itemDoubleClicked.connect(lambda _: self._dokument_oeffnen())
        layout.addWidget(self._table, 1)

        # Info-Box
        info = QLabel(
            "💡 <b>Doppelklick</b> öffnet ein Dokument direkt.  "
            "\"<b>Bearbeiten</b>\" ermöglicht Textänderungen im Popup – "
            "das Dokument wird anschließend mit der DRK-Vorlage neu erstellt."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background:#e3f2fd; color:#154360; border-radius:4px; "
            "padding:8px 12px; font-size:11px;"
        )
        layout.addWidget(info)

        return w

    # ── Refresh / Laden ───────────────────────────────────────────────────────

    def refresh(self):
        """Dateiliste neu laden."""
        sicherungsordner()
        self._dokumente = lade_dokumente_nach_kategorie()
        self._kat_liste_aktualisieren()
        self._zeige_kategorie(self._akt_kategorie)

    def _kat_liste_aktualisieren(self):
        """Sidebar: Anzahl der Dateien je Kategorie aktualisieren."""
        for row, kat in enumerate(KATEGORIEN):
            anzahl = len(self._dokumente.get(kat, []))
            item = self._kat_list.item(row)
            if item:
                item.setText(f"📁  {kat}  ({anzahl})")

    def _zeige_kategorie(self, kategorie: str):
        """Tabelle mit Dateien der gewählten Kategorie befüllen."""
        self._akt_kategorie = kategorie
        self._kat_label.setText(f"📁  {kategorie}")
        dateien = self._dokumente.get(kategorie, [])

        self._table.setRowCount(len(dateien))
        for row, d in enumerate(dateien):
            name_item = QTableWidgetItem(d["name"])
            ext = os.path.splitext(d["name"])[1].lower()
            icon_map = {".docx": "📝", ".doc": "📝", ".pdf": "📕", ".txt": "📄"}
            name_item.setIcon(QIcon())  # Kein Icon nötig – Text reicht
            self._table.setItem(row, 0, QTableWidgetItem(
                f"{icon_map.get(ext, '📄')}  {d['name']}"
            ))
            self._table.setItem(row, 1, QTableWidgetItem(d["geaendert"]))
            self._table.setItem(row, 2, QTableWidgetItem(ext.upper().lstrip(".")))

        self._auswahl_geaendert()

    # ── Ereignis-Handler ──────────────────────────────────────────────────────

    def _kategorie_gewaehlt(self, row: int):
        if 0 <= row < len(KATEGORIEN):
            self._zeige_kategorie(KATEGORIEN[row])

    def _auswahl_geaendert(self):
        hat_auswahl = self._table.currentRow() >= 0 and len(
            self._dokumente.get(self._akt_kategorie, [])
        ) > 0
        for btn in (self._btn_oeffnen, self._btn_bearbeiten,
                    self._btn_umbenennen, self._btn_loeschen):
            btn.setEnabled(hat_auswahl)

    def _aktueller_eintrag(self) -> dict | None:
        row = self._table.currentRow()
        dateien = self._dokumente.get(self._akt_kategorie, [])
        if 0 <= row < len(dateien):
            return dateien[row]
        return None

    # ── Aktionen ──────────────────────────────────────────────────────────────

    def _ordner_oeffnen(self):
        import subprocess
        subprocess.Popen(["explorer", DOKUMENTE_BASIS], shell=False)

    def _dokument_oeffnen(self):
        eintrag = self._aktueller_eintrag()
        if eintrag:
            oeffne_datei(eintrag["pfad"])

    def _dokument_bearbeiten(self):
        eintrag = self._aktueller_eintrag()
        if not eintrag:
            return
        pfad = eintrag["pfad"]
        ext = os.path.splitext(pfad)[1].lower()
        if ext not in (".docx", ".doc", ".txt"):
            QMessageBox.information(
                self, "Bearbeiten nicht möglich",
                f"Nur .docx und .txt können im Popup bearbeitet werden.\n"
                f"Bitte öffne die Datei direkt: {pfad}"
            )
            return
        dlg = _DokumentBearbeitenDialog(eintrag, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            neuer_inhalt = dlg.get_inhalt()
            try:
                # Alten Dateinamen behalten, mit neuem Inhalt neu erstellen
                alter_name = os.path.basename(pfad)
                # Kurzen Titel aus Dateinamen ableiten
                titel = os.path.splitext(alter_name)[0]
                neuer_pfad = erstelle_dokument_aus_vorlage(
                    kategorie=self._akt_kategorie,
                    titel=titel,
                    mitarbeiter="(Bearbeitung)",
                    datum=__import__("datetime").datetime.now().strftime("%d.%m.%Y"),
                    inhalt=neuer_inhalt,
                    dateiname=alter_name,
                )
                QMessageBox.information(
                    self, "Gespeichert",
                    f"Dokument wurde aktualisiert:\n{neuer_pfad}"
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Fehler beim Speichern", str(e))

    def _neues_dokument(self, vorkategorie: str = ""):
        dlg = _NeuesDokumentDialog(vorkategorie or self._akt_kategorie, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                pfad = erstelle_dokument_aus_vorlage(
                    kategorie=d["kategorie"],
                    titel=d["titel"],
                    mitarbeiter=d["mitarbeiter"],
                    datum=d["datum"],
                    inhalt=d["inhalt"],
                )
                self.refresh()
                # Zur richtigen Kategorie wechseln
                idx = KATEGORIEN.index(d["kategorie"]) if d["kategorie"] in KATEGORIEN else 0
                self._kat_list.setCurrentRow(idx)

                antwort = QMessageBox.question(
                    self, "Dokument erstellt",
                    f"Dokument wurde erfolgreich erstellt:\n{pfad}\n\nJetzt öffnen?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if antwort == QMessageBox.StandardButton.Yes:
                    oeffne_datei(pfad)
            except Exception as e:
                QMessageBox.critical(self, "Fehler beim Erstellen", str(e))

    def _dokument_loeschen(self):
        eintrag = self._aktueller_eintrag()
        if not eintrag:
            return
        antwort = QMessageBox.question(
            self, "Dokument löschen",
            f"Dokument wirklich dauerhaft löschen?\n\n📄 {eintrag['name']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort == QMessageBox.StandardButton.Yes:
            if loesche_dokument(eintrag["pfad"]):
                self.refresh()
            else:
                QMessageBox.warning(self, "Fehler", "Datei konnte nicht gelöscht werden.")

    def _dokument_umbenennen(self):
        eintrag = self._aktueller_eintrag()
        if not eintrag:
            return
        alter_name = eintrag["name"]
        neuer_name, ok = QInputDialog.getText(
            self, "Umbenennen", "Neuer Dateiname:",
            text=alter_name
        )
        if ok and neuer_name.strip() and neuer_name.strip() != alter_name:
            neuer_name = neuer_name.strip()
            if not any(neuer_name.lower().endswith(ext)
                       for ext in (".docx", ".doc", ".pdf", ".txt")):
                neuer_name += ".docx"
            try:
                umbenennen_dokument(eintrag["pfad"], neuer_name)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Fehler beim Umbenennen", str(e))
