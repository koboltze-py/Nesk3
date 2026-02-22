"""
Nesk3 – DRK Flughafen Köln
Mitarbeiter- und Dienstplanverwaltung
Einstiegspunkt der Anwendung
"""
import sys
import os

# Projektverzeichnis in den Python-Pfad aufnehmen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow


def main():
    # High-DPI Unterstützung
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Nesk3")
    app.setOrganizationName("DRK Flughafen Köln")
    app.setStyle("Fusion")

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
