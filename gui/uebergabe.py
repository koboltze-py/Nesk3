"""
Übergabe-Widget
Erstellt und verwaltet Tagdienst- und Nachtdienst-Übergabeprotokolle
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSplitter, QTextEdit, QLineEdit,
    QSpinBox, QComboBox, QFormLayout, QMessageBox, QSizePolicy,
    QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

from config import (
    FIORI_BLUE, FIORI_TEXT, FIORI_WHITE, FIORI_BORDER,
    FIORI_SUCCESS, FIORI_ERROR, FIORI_SIDEBAR_BG
)
from functions.uebergabe_functions import (
    erstelle_protokoll, aktualisiere_protokoll,
    lade_protokolle, lade_protokoll_by_id, loesche_protokoll,
    schliesse_protokoll_ab
)

# ── Farben ──────────────────────────────────────────────────────────────────
_TAG_COLOR    = "#e67e22"   # Orange für Tagdienst
_NACHT_COLOR  = "#2c3e50"   # Dunkelblau für Nachtdienst
_OFFEN_BG     = "#fff8e1"
_ABGES_BG     = "#e8f5e9"


class _ProtokolListItem(QFrame):
    """Kompaktes Listenelement für ein Protokoll in der Seitenleiste."""

    def __init__(self, protokoll: dict, parent=None):
        super().__init__(parent)
        self._id = protokoll["id"]
        self._setup(protokoll)

    def _setup(self, p: dict):
        typ     = p.get("schicht_typ", "tagdienst")
        datum   = p.get("datum", "")
        status  = p.get("status", "offen")
        erstell = p.get("ersteller", "–")

        # Datum lesbar formatieren
        try:
            d = datetime.strptime(datum, "%Y-%m-%d")
            datum_str = d.strftime("%d.%m.%Y")
        except Exception:
            datum_str = datum

        self._farbe  = _TAG_COLOR if typ == "tagdienst" else _NACHT_COLOR
        farbe  = self._farbe
        symbol = "☀" if typ == "tagdienst" else "🌙"
        label  = "Tagdienst" if typ == "tagdienst" else "Nachtdienst"
        self._bg_base = _OFFEN_BG if status == "offen" else _ABGES_BG

        self._apply_style(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(62)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)

        top = QHBoxLayout()
        typ_lbl = QLabel(f"{symbol} {label}")
        typ_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        typ_lbl.setStyleSheet(f"color: {farbe}; border: none;")

        stat_lbl = QLabel("✓ abgeschlossen" if status == "abgeschlossen" else "· offen")
        stat_lbl.setFont(QFont("Arial", 9))
        stat_lbl.setStyleSheet(
            f"color: {FIORI_SUCCESS}; border: none;"
            if status == "abgeschlossen"
            else "color: #999; border: none;"
        )
        top.addWidget(typ_lbl)
        top.addStretch()
        top.addWidget(stat_lbl)

        datum_lbl = QLabel(f"📅 {datum_str}  |  👤 {erstell}")
        datum_lbl.setFont(QFont("Arial", 9))
        datum_lbl.setStyleSheet("color: #555; border: none;")

        layout.addLayout(top)
        layout.addWidget(datum_lbl)

    def _apply_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: #cfe0f5;
                    border: 2px solid {self._farbe};
                    border-left: 6px solid {self._farbe};
                    border-radius: 4px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self._bg_base};
                    border: 1px solid #ddd;
                    border-left: 4px solid {self._farbe};
                    border-radius: 4px;
                }}
            """)

    def set_active(self, active: bool):
        self._apply_style(active)

    @property
    def protokoll_id(self) -> int:
        return self._id


class UebergabeWidget(QWidget):
    """Haupt-Widget für Tagdienst- und Nachtdienst-Übergabeprotokolle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._aktives_protokoll_id: int | None = None
        self._ist_neu = False
        self._aktueller_typ = "tagdienst"
        self._list_items: dict[int, "_ProtokolListItem"] = {}
        self._build_ui()
        self.refresh()

    # ── UI-Aufbau ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        root.addWidget(self._build_header())

        # Hauptbereich: Liste | Formular
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        splitter.addWidget(self._build_liste())
        splitter.addWidget(self._build_formular())
        splitter.setSizes([300, 700])

        root.addWidget(splitter, 1)

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setStyleSheet(f"background-color: {FIORI_SIDEBAR_BG};")
        header.setFixedHeight(64)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)

        title = QLabel("📋 Übergabeprotokolle")
        title.setFont(QFont("Arial", 17, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        layout.addStretch()

        # Neues Tagdienst-Protokoll
        btn_tag = QPushButton("☀  Neues Tagdienst-Protokoll")
        btn_tag.setFont(QFont("Arial", 11))
        btn_tag.setFixedHeight(40)
        btn_tag.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tag.setStyleSheet(f"""
            QPushButton {{
                background-color: {_TAG_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #e08010; }}
        """)
        btn_tag.clicked.connect(lambda: self._neues_protokoll("tagdienst"))

        # Neues Nachtdienst-Protokoll
        btn_nacht = QPushButton("🌙  Neues Nachtdienst-Protokoll")
        btn_nacht.setFont(QFont("Arial", 11))
        btn_nacht.setFixedHeight(40)
        btn_nacht.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nacht.setStyleSheet(f"""
            QPushButton {{
                background-color: {_NACHT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #3d566e; }}
        """)
        btn_nacht.clicked.connect(lambda: self._neues_protokoll("nachtdienst"))

        layout.addWidget(btn_tag)
        layout.addWidget(btn_nacht)
        return header

    def _build_liste(self) -> QWidget:
        container = QWidget()
        container.setMinimumWidth(260)
        container.setMaximumWidth(360)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Filter-Leiste
        filter_bar = QFrame()
        filter_bar.setStyleSheet("background-color: #f0f2f4; border-bottom: 1px solid #ddd;")
        filter_bar.setFixedHeight(44)
        fl = QHBoxLayout(filter_bar)
        fl.setContentsMargins(8, 4, 8, 4)

        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["Alle", "Tagdienst", "Nachtdienst"])
        self._filter_combo.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 3px; padding: 2px 6px;")
        self._filter_combo.currentIndexChanged.connect(self._lade_liste)
        fl.addWidget(QLabel("Anzeigen:"))
        fl.addWidget(self._filter_combo, 1)
        layout.addWidget(filter_bar)

        # Scrollbare Liste
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self._liste_container = QWidget()
        self._liste_layout = QVBoxLayout(self._liste_container)
        self._liste_layout.setContentsMargins(8, 8, 8, 8)
        self._liste_layout.setSpacing(4)
        self._liste_layout.addStretch()

        scroll.setWidget(self._liste_container)
        layout.addWidget(scroll, 1)
        return container

    def _build_formular(self) -> QWidget:
        self._form_container = QWidget()
        self._form_container.setStyleSheet("background-color: white;")
        outer = QVBoxLayout(self._form_container)
        outer.setContentsMargins(0, 0, 0, 0)

        # Formular-Header
        self._form_header = QFrame()
        self._form_header.setFixedHeight(50)
        self._form_header.setStyleSheet(f"background-color: #eef4fa; border-bottom: 1px solid {FIORI_BORDER};")
        fhl = QHBoxLayout(self._form_header)
        fhl.setContentsMargins(20, 0, 20, 0)
        self._form_titel = QLabel("Protokoll auswählen oder neu erstellen")
        self._form_titel.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self._form_titel.setStyleSheet(f"color: {FIORI_TEXT};")
        fhl.addWidget(self._form_titel)
        fhl.addStretch()
        outer.addWidget(self._form_header)

        # Formular-Scroll-Bereich
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        form_widget = QWidget()
        form_widget.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(form_widget)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # FormLayout für Felder
        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl.setSpacing(10)

        # Datum
        self._f_datum = QDateEdit()
        self._f_datum.setCalendarPopup(True)
        self._f_datum.setDate(QDate.currentDate())
        self._f_datum.setDisplayFormat("dd.MM.yyyy")
        self._f_datum.setStyleSheet(self._field_style())
        fl.addRow("Datum:", self._f_datum)

        # Beginn
        self._f_beginn = QLineEdit()
        self._f_beginn.setPlaceholderText("z.B. 07:00")
        self._f_beginn.setStyleSheet(self._field_style())
        fl.addRow("Beginn:", self._f_beginn)

        # Ende
        self._f_ende = QLineEdit()
        self._f_ende.setPlaceholderText("z.B. 19:00")
        self._f_ende.setStyleSheet(self._field_style())
        fl.addRow("Ende:", self._f_ende)

        # Patienten
        self._f_patienten = QSpinBox()
        self._f_patienten.setRange(0, 999)
        self._f_patienten.setStyleSheet(self._field_style())
        fl.addRow("Patienten:", self._f_patienten)

        # Ersteller
        self._f_ersteller = QLineEdit()
        self._f_ersteller.setPlaceholderText("Name Protokollersteller")
        self._f_ersteller.setStyleSheet(self._field_style())
        fl.addRow("Ersteller:", self._f_ersteller)

        # Abzeichner
        self._f_abzeichner = QLineEdit()
        self._f_abzeichner.setPlaceholderText("Name Abzeichner (bei Abschluss)")
        self._f_abzeichner.setStyleSheet(self._field_style())
        fl.addRow("Abzeichner:", self._f_abzeichner)

        layout.addLayout(fl)

        # Ereignisse / Vorfälle
        layout.addWidget(self._section_label("⚠ Ereignisse / Vorfälle"))
        self._f_ereignisse = QTextEdit()
        self._f_ereignisse.setPlaceholderText("Besondere Ereignisse, Vorfälle, Einsätze ...")
        self._f_ereignisse.setFixedHeight(110)
        self._f_ereignisse.setStyleSheet(self._textarea_style())
        layout.addWidget(self._f_ereignisse)

        # Maßnahmen / Behandlungen
        layout.addWidget(self._section_label("🩺 Maßnahmen / Behandlungen"))
        self._f_massnahmen = QTextEdit()
        self._f_massnahmen.setPlaceholderText("Durchgeführte Maßnahmen, Behandlungen ...")
        self._f_massnahmen.setFixedHeight(110)
        self._f_massnahmen.setStyleSheet(self._textarea_style())
        layout.addWidget(self._f_massnahmen)

        # Übergabe-Notiz
        layout.addWidget(self._section_label("📝 Übergabe-Notiz (für die Folgeschicht)"))
        self._f_notiz = QTextEdit()
        self._f_notiz.setPlaceholderText("Wichtige Informationen für die Folgeschicht ...")
        self._f_notiz.setFixedHeight(110)
        self._f_notiz.setStyleSheet(self._textarea_style())
        layout.addWidget(self._f_notiz)

        layout.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_speichern = QPushButton("💾  Speichern")
        self._btn_speichern.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self._btn_speichern.setFixedHeight(40)
        self._btn_speichern.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_speichern.setStyleSheet(f"""
            QPushButton {{
                background-color: {FIORI_BLUE};
                color: white; border: none;
                border-radius: 4px; padding: 4px 24px;
            }}
            QPushButton:hover {{ background-color: #0855a9; }}
            QPushButton:disabled {{ background-color: #ccc; color: #999; }}
        """)
        self._btn_speichern.clicked.connect(self._speichern)
        self._btn_speichern.setEnabled(False)

        self._btn_abschliessen = QPushButton("✓  Abschließen")
        self._btn_abschliessen.setFont(QFont("Arial", 11))
        self._btn_abschliessen.setFixedHeight(40)
        self._btn_abschliessen.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_abschliessen.setStyleSheet(f"""
            QPushButton {{
                background-color: {FIORI_SUCCESS};
                color: white; border: none;
                border-radius: 4px; padding: 4px 24px;
            }}
            QPushButton:hover {{ background-color: #0d6831; }}
            QPushButton:disabled {{ background-color: #ccc; color: #999; }}
        """)
        self._btn_abschliessen.clicked.connect(self._abschliessen)
        self._btn_abschliessen.setEnabled(False)

        self._btn_loeschen = QPushButton("🗑  Löschen")
        self._btn_loeschen.setFont(QFont("Arial", 11))
        self._btn_loeschen.setFixedHeight(40)
        self._btn_loeschen.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_loeschen.setStyleSheet(f"""
            QPushButton {{
                background-color: #e0e0e0;
                color: #555; border: none;
                border-radius: 4px; padding: 4px 18px;
            }}
            QPushButton:hover {{ background-color: #ffcccc; color: #a00; }}
            QPushButton:disabled {{ background-color: #eee; color: #bbb; }}
        """)
        self._btn_loeschen.clicked.connect(self._loeschen)
        self._btn_loeschen.setEnabled(False)

        btn_row.addWidget(self._btn_speichern)
        btn_row.addWidget(self._btn_abschliessen)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_loeschen)
        layout.addLayout(btn_row)
        layout.addStretch()

        scroll.setWidget(form_widget)
        outer.addWidget(scroll, 1)
        return self._form_container

    # ── Hilfsmethoden ──────────────────────────────────────────────────────────

    def _field_style(self) -> str:
        return (
            "border: 1px solid #ccc; border-radius: 3px; "
            "padding: 4px 8px; background: white; min-width: 240px;"
        )

    def _textarea_style(self) -> str:
        return (
            "border: 1px solid #ccc; border-radius: 3px; "
            "padding: 6px; background: white; font-size: 12px;"
        )

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl.setStyleSheet(
            f"color: {FIORI_TEXT}; border-bottom: 1px solid #e0e0e0; "
            f"padding-bottom: 4px; margin-top: 6px;"
        )
        return lbl

    # ── Liste laden ────────────────────────────────────────────────────────────

    def _lade_liste(self):
        # Alte Einträge entfernen (ohne den Stretch am Ende)
        while self._liste_layout.count() > 1:
            item = self._liste_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filter_idx = self._filter_combo.currentIndex()
        typ_filter = {0: None, 1: "tagdienst", 2: "nachtdienst"}.get(filter_idx)

        protokolle = lade_protokolle(schicht_typ=typ_filter, limit=80)

        self._list_items.clear()

        if not protokolle:
            lbl = QLabel("Keine Protokolle vorhanden")
            lbl.setStyleSheet("color: #999; padding: 16px; font-size: 12px; border: none;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._liste_layout.insertWidget(0, lbl)
            return

        for p in protokolle:
            item = _ProtokolListItem(p)
            pid = p["id"]
            self._list_items[pid] = item
            item.mousePressEvent = lambda e, i=pid: self._item_clicked(i)
            # Bereits aktives Item sofort hervorheben
            if pid == self._aktives_protokoll_id:
                item.set_active(True)
            self._liste_layout.insertWidget(
                self._liste_layout.count() - 1,  # vor dem Stretch
                item
            )

    # ── Item-Auswahl ────────────────────────────────────────────────────────────

    def _item_clicked(self, protokoll_id: int):
        """Item in der Liste anklicken: altes deaktivieren, neues aktivieren."""
        for pid, itm in self._list_items.items():
            itm.set_active(pid == protokoll_id)
        self._lade_protokoll_in_form(protokoll_id)

    # ── Formular befüllen ──────────────────────────────────────────────────────

    def _lade_protokoll_in_form(self, protokoll_id: int):
        p = lade_protokoll_by_id(protokoll_id)
        if not p:
            return

        self._aktives_protokoll_id = protokoll_id
        # Hervorhebung synchron halten
        for pid, itm in self._list_items.items():
            itm.set_active(pid == protokoll_id)
        self._ist_neu = False
        self._aktueller_typ = p.get("schicht_typ", "tagdienst")

        typ_label = "☀ Tagdienst" if self._aktueller_typ == "tagdienst" else "🌙 Nachtdienst"
        status = p.get("status", "offen")
        self._form_titel.setText(
            f"{typ_label}-Protokoll  –  ID #{protokoll_id}"
            + ("  [abgeschlossen]" if status == "abgeschlossen" else "")
        )
        farbe = _TAG_COLOR if self._aktueller_typ == "tagdienst" else _NACHT_COLOR
        self._form_header.setStyleSheet(
            f"background-color: {farbe}22; border-bottom: 1px solid {farbe};"
        )
        self._form_titel.setStyleSheet(f"color: {farbe};")

        # Felder setzen
        try:
            qd = QDate.fromString(p.get("datum", ""), "yyyy-MM-dd")
            if qd.isValid():
                self._f_datum.setDate(qd)
        except Exception:
            pass
        self._f_beginn.setText(p.get("beginn_zeit", ""))
        self._f_ende.setText(p.get("ende_zeit", ""))
        self._f_patienten.setValue(int(p.get("patienten_anzahl") or 0))
        self._f_ersteller.setText(p.get("ersteller", ""))
        self._f_abzeichner.setText(p.get("abzeichner", ""))
        self._f_ereignisse.setPlainText(p.get("ereignisse", ""))
        self._f_massnahmen.setPlainText(p.get("massnahmen", ""))
        self._f_notiz.setPlainText(p.get("uebergabe_notiz", ""))

        abges = (status == "abgeschlossen")
        self._btn_speichern.setEnabled(not abges)
        self._btn_abschliessen.setEnabled(not abges)
        self._btn_loeschen.setEnabled(True)

        for w in [self._f_datum, self._f_beginn, self._f_ende,
                  self._f_patienten, self._f_ersteller, self._f_abzeichner,
                  self._f_ereignisse, self._f_massnahmen, self._f_notiz]:
            w.setEnabled(not abges)

    def _neues_protokoll(self, typ: str):
        """Öffnet ein leeres Formular für ein neues Protokoll."""
        self._aktives_protokoll_id = None
        self._ist_neu = True
        self._aktueller_typ = typ

        farbe = _TAG_COLOR if typ == "tagdienst" else _NACHT_COLOR
        typ_label = "☀ Tagdienst" if typ == "tagdienst" else "🌙 Nachtdienst"
        self._form_titel.setText(f"Neues {typ_label}-Protokoll")
        self._form_header.setStyleSheet(
            f"background-color: {farbe}22; border-bottom: 1px solid {farbe};"
        )
        self._form_titel.setStyleSheet(f"color: {farbe};")

        # Felder leeren + Zeiten je nach Diensttyp vorbelegen
        self._f_datum.setDate(QDate.currentDate())
        if typ == "tagdienst":
            self._f_beginn.setText("07:00")
            self._f_ende.setText("19:00")
        else:
            self._f_beginn.setText("19:00")
            self._f_ende.setText("07:00")
        self._f_patienten.setValue(0)
        self._f_ersteller.setText("")
        self._f_abzeichner.setText("")
        self._f_ereignisse.clear()
        self._f_massnahmen.clear()
        self._f_notiz.clear()

        for w in [self._f_datum, self._f_beginn, self._f_ende,
                  self._f_patienten, self._f_ersteller, self._f_abzeichner,
                  self._f_ereignisse, self._f_massnahmen, self._f_notiz]:
            w.setEnabled(True)

        self._btn_speichern.setEnabled(True)
        self._btn_abschliessen.setEnabled(False)
        self._btn_loeschen.setEnabled(False)

    # ── Aktionen ───────────────────────────────────────────────────────────────

    def _speichern(self):
        datum_str = self._f_datum.date().toString("yyyy-MM-dd")

        kwargs = dict(
            beginn_zeit      = self._f_beginn.text().strip(),
            ende_zeit        = self._f_ende.text().strip(),
            patienten_anzahl = self._f_patienten.value(),
            ereignisse       = self._f_ereignisse.toPlainText().strip(),
            massnahmen       = self._f_massnahmen.toPlainText().strip(),
            uebergabe_notiz  = self._f_notiz.toPlainText().strip(),
            ersteller        = self._f_ersteller.text().strip(),
        )

        try:
            if self._ist_neu:
                new_id = erstelle_protokoll(
                    datum=datum_str,
                    schicht_typ=self._aktueller_typ,
                    **kwargs
                )
                self._aktives_protokoll_id = new_id
                self._ist_neu = False
                self._btn_abschliessen.setEnabled(True)
                self._btn_loeschen.setEnabled(True)
                QMessageBox.information(
                    self, "Gespeichert",
                    f"Protokoll #{new_id} wurde erfolgreich gespeichert."
                )
            else:
                aktualisiere_protokoll(
                    protokoll_id=self._aktives_protokoll_id,
                    abzeichner=self._f_abzeichner.text().strip(),
                    status="offen",
                    **kwargs
                )
                QMessageBox.information(
                    self, "Gespeichert",
                    f"Protokoll #{self._aktives_protokoll_id} wurde aktualisiert."
                )
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")
            return

        self._lade_liste()

    def _abschliessen(self):
        if self._aktives_protokoll_id is None:
            return
        abzeichner = self._f_abzeichner.text().strip()
        if not abzeichner:
            QMessageBox.warning(self, "Kein Abzeichner",
                                "Bitte trage einen Abzeichner ein, bevor du das Protokoll abschließt.")
            return

        antwort = QMessageBox.question(
            self, "Protokoll abschließen",
            f"Protokoll #{self._aktives_protokoll_id} als abgeschlossen markieren?\n\n"
            f"Abzeichner: {abzeichner}\n\nDanach ist das Protokoll schreibgeschützt.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort != QMessageBox.StandardButton.Yes:
            return

        # Zuerst aktuelle Änderungen speichern
        self._speichern()

        schliesse_protokoll_ab(self._aktives_protokoll_id, abzeichner)
        self._lade_protokoll_in_form(self._aktives_protokoll_id)
        self._lade_liste()

    def _loeschen(self):
        if self._aktives_protokoll_id is None:
            return
        antwort = QMessageBox.question(
            self, "Protokoll löschen",
            f"Protokoll #{self._aktives_protokoll_id} dauerhaft löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort != QMessageBox.StandardButton.Yes:
            return
        loesche_protokoll(self._aktives_protokoll_id)
        self._aktives_protokoll_id = None
        self._ist_neu = False
        self._form_titel.setText("Protokoll auswählen oder neu erstellen")
        self._form_header.setStyleSheet(
            f"background-color: #eef4fa; border-bottom: 1px solid {FIORI_BORDER};"
        )
        self._form_titel.setStyleSheet(f"color: {FIORI_TEXT};")
        self._btn_speichern.setEnabled(False)
        self._btn_abschliessen.setEnabled(False)
        self._btn_loeschen.setEnabled(False)
        self._lade_liste()

    # ── Refresh (von main_window aufgerufen) ───────────────────────────────────

    def refresh(self):
        self._lade_liste()
