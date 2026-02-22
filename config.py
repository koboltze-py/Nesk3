"""
Konfigurationsdatei für Nesk3
SQLite Datenbankverbindung und App-Einstellungen
"""
import os

# ─── SQLite Datenbankpfad ─────────────────────────────────────────────────────
# Die Datenbank liegt direkt im Projektordner (keine Installation nötig)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE_DIR, "nesk3.db")

# ─── Anwendungseinstellungen ──────────────────────────────────────────────────
APP_NAME    = "Nesk3 – DRK Flughafen Köln"
APP_VERSION = "1.0.0"
APP_LANG    = "de"

# ─── Backup-Einstellungen ─────────────────────────────────────────────────────
BACKUP_DIR      = "backup/exports"
BACKUP_MAX_KEEP = 30    # Maximale Anzahl gespeicherter Backups

# ─── JSON-Einstellungen ───────────────────────────────────────────────────────
JSON_DIR = "json"

# ─── SAP Fiori Design-Farben ─────────────────────────────────────────────────
FIORI_BLUE        = "#0a6ed1"
FIORI_LIGHT_BLUE  = "#eef4fa"
FIORI_TEXT        = "#32363a"
FIORI_BORDER      = "#d9d9d9"
FIORI_SUCCESS     = "#107e3e"
FIORI_WARNING     = "#e9730c"
FIORI_ERROR       = "#bb0000"
FIORI_WHITE       = "#ffffff"
FIORI_SIDEBAR_BG  = "#354a5e"
