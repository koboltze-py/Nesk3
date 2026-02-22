"""
Nesk3 – DRK Flughafen Köln
Mitarbeiter- und Dienstplanverwaltung
Einstiegspunkt der Anwendung
"""
import sys
import os
import traceback

# Projektverzeichnis in den Python-Pfad aufnehmen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Alle unbehandelten Exceptions im Terminal sichtbar machen
def _excepthook(exc_type, exc_value, exc_tb):
    print("\n=== UNBEHANDELTER FEHLER ===", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_tb)
    print("============================\n", file=sys.stderr)

sys.excepthook = _excepthook

import sqlite3
import shutil
import glob
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from gui.main_window import MainWindow


def _db_startup_backup():
    """Erstellt beim Programmstart ein SQLite-Backup der Datenbank.
    Behält die letzten 7 Backups; ältere werden gelöscht."""
    try:
        from config import DB_PATH
        if not os.path.exists(DB_PATH):
            return  # DB existiert noch nicht (Erststart)
        backup_dir = os.path.join(os.path.dirname(DB_PATH), "Backup Data", "db_backups")
        os.makedirs(backup_dir, exist_ok=True)
        datum = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"nesk3_{datum}.db")
        # SQLite-native Online-Backup (atomar, keine Lock-Probleme)
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_path)
        src.backup(dst)
        dst.close()
        src.close()
        # Nur die letzten 7 Backups behalten
        alle = sorted(glob.glob(os.path.join(backup_dir, "nesk3_*.db")))
        for alt in alle[:-7]:
            try:
                os.remove(alt)
            except Exception:
                pass
        print(f"[OK] DB-Backup erstellt: {os.path.basename(backup_path)}")
    except Exception as e:
        print(f"[WARNUNG] DB-Backup fehlgeschlagen: {e}")


def main():
    # High-DPI Unterstützung für Qt6 (PySide6)
    # QT_AUTO_SCREEN_SCALE_FACTOR ist nur Qt5 – in Qt6 ist High-DPI standardmäßig aktiv.
    # PassThrough gibt den echten Skalierungsfaktor (z.B. 1.25 bei 125%) direkt weiter
    # statt ihn auf ganze Zahlen zu runden → schärfere Darstellung auf allen Displays.
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Nesk3")
    app.setOrganizationName("DRK Flughafen Köln")
    app.setStyle("Fusion")

    # Globale Basisschrift: Segoe UI 10pt – die Windows-Systemschrift.
    # Alle Widgets ohne expliziten Font erben diese Größe und skalieren
    # damit korrekt mit der Windows-Anzeigenskalierung (100 %, 125 %, 150 % …).
    app.setFont(QFont("Segoe UI", 10))

    # DB-Backup vor Programmstart
    _db_startup_backup()

    # Datenbanktabellen beim ersten Start erstellen
    try:
        from database.migrations import run_migrations
        run_migrations()
    except Exception as e:
        print(f"[WARNUNG] Datenbankinitialisierung fehlgeschlagen: {e}")
        print("[INFO] Bitte Datenbankverbindung in config.py konfigurieren.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
