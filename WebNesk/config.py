"""
WebNesk – Konfigurationsdatei
==============================
Alle Einstellungen für Flask und die SQLite-Datenbank.
"""

import os

# Absoluter Pfad zum Projektverzeichnis
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Pfad zur SQLite-Datenbank
DATABASE_PATH = os.path.join(BASE_DIR, "database", "nesk.db")


class Config:
    # ---------------------------------------------------------------
    # Flask / Sicherheit
    # ---------------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "drk-koeln-nesk-geheim-2026")

    # ---------------------------------------------------------------
    # SQLAlchemy
    # ---------------------------------------------------------------
    DATABASE_PATH = DATABASE_PATH
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLite-Optimierungen: WAL-Modus für konfliktfreien parallelen Zugriff
    # (auch durch das externe Python-Programm sicher lesbar)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30,
        }
    }

    # ---------------------------------------------------------------
    # Anwendungseinstellungen
    # ---------------------------------------------------------------
    APP_NAME = "WebNesk – DRK Flughafen Köln"
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 5000
