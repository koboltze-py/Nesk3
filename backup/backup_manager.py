"""
Backup-Manager
Erstellt und verwaltet Datenbank-Backups als JSON
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BACKUP_DIR, BACKUP_MAX_KEEP, BASE_DIR


def _ensure_backup_dir() -> str:
    """Erstellt das Backup-Verzeichnis falls nicht vorhanden."""
    path = os.path.join(BASE_DIR, BACKUP_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def create_backup(typ: str = "manuell") -> str:
    """
    Erstellt ein vollständiges Backup aller Tabellen als JSON.
    Gibt den Dateipfad zurück.
    """
    # TODO: Implementierung folgt
    return ""


def list_backups() -> list[dict]:
    """Gibt eine Liste aller vorhandenen Backups zurück."""
    backup_dir = _ensure_backup_dir()
    backups = []
    for fname in sorted(os.listdir(backup_dir), reverse=True):
        if fname.endswith(".json"):
            fpath = os.path.join(backup_dir, fname)
            size  = os.path.getsize(fpath)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            backups.append({
                "dateiname":  fname,
                "pfad":       fpath,
                "groesse_kb": round(size / 1024, 1),
                "erstellt":   mtime.strftime("%d.%m.%Y %H:%M"),
            })
    return backups


def restore_backup(filepath: str) -> int:
    """
    Stellt ein Backup wieder her.
    Gibt die Anzahl der wiederhergestellten Datensätze zurück.
    """
    # TODO: Implementierung folgt
    return 0


def _cleanup_old_backups(backup_dir: str):
    """Löscht ältere Backups wenn MAX_KEEP überschritten."""
    files = sorted(
        [f for f in os.listdir(backup_dir) if f.endswith(".json")]
    )
    while len(files) > BACKUP_MAX_KEEP:
        os.remove(os.path.join(backup_dir, files.pop(0)))
