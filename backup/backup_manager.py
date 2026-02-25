"""
Backup-Manager
Erstellt und verwaltet Datenbank-Backups als JSON.
Enthält außerdem Funktionen für ZIP-Backups und ZIP-Restore des gesamten Nesk3-Ordners.
"""
import os
import sys
import json
import shutil
import zipfile
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


# ---------------------------------------------------------------------------
# ZIP-Backup  /  ZIP-Restore  (gesamter Nesk3-Quellcode-Ordner)
# ---------------------------------------------------------------------------

_CODE_BACKUP_DIR = os.path.join(BASE_DIR, "Backup Data")

# Ordner/Muster die beim ZIP-Backup NICHT einbezogen werden sollen
_ZIP_EXCLUDE_DIRS  = {'__pycache__', '.git', 'Backup Data', 'build_tmp', 'Exe'}
_ZIP_EXCLUDE_EXTS  = {'.pyc', '.pyo'}


def create_zip_backup() -> str:
    """
    Erstellt ein vollständiges ZIP-Backup des Nesk3-Ordners (alle .py, .db, .ini, .json Dateien).
    Speichert das ZIP unter 'Backup Data/Nesk3_backup_<timestamp>.zip'.
    Gibt den vollständigen ZIP-Pfad zurück.
    """
    os.makedirs(_CODE_BACKUP_DIR, exist_ok=True)
    stamp    = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f"Nesk3_backup_{stamp}.zip"
    zip_path = os.path.join(_CODE_BACKUP_DIR, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Ausgeschlossene Ordner überspringen (in-place modifizieren)
            dirs[:] = [d for d in dirs if d not in _ZIP_EXCLUDE_DIRS]
            for fname in files:
                if os.path.splitext(fname)[1].lower() in _ZIP_EXCLUDE_EXTS:
                    continue
                full_path = os.path.join(root, fname)
                arcname   = os.path.relpath(full_path, BASE_DIR)
                zf.write(full_path, arcname)

    return zip_path


def list_zip_backups() -> list[dict]:
    """
    Gibt eine Liste aller ZIP-Backups im Backup-Data-Ordner zurück.
    Jedes Element: {'dateiname', 'pfad', 'groesse_kb', 'erstellt'}
    """
    if not os.path.isdir(_CODE_BACKUP_DIR):
        return []
    result = []
    for fname in sorted(os.listdir(_CODE_BACKUP_DIR), reverse=True):
        if fname.lower().endswith('.zip'):
            fpath = os.path.join(_CODE_BACKUP_DIR, fname)
            size  = os.path.getsize(fpath)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            result.append({
                'dateiname':  fname,
                'pfad':       fpath,
                'groesse_kb': round(size / 1024, 1),
                'erstellt':   mtime.strftime('%d.%m.%Y %H:%M'),
            })
    return result


def restore_from_zip(zip_path: str, ziel_ordner: str = None) -> dict:
    """
    Stellt einen Nesk3-Quellcode-Backup aus einer ZIP-Datei wieder her.

    Parameters
    ----------
    zip_path     : Vollständiger Pfad zur ZIP-Datei
    ziel_ordner  : Zielordner; Standard = BASE_DIR (= aktueller Nesk3-Ordner)

    Returns
    -------
    dict mit {'erfolg': bool, 'dateien': int, 'meldung': str}
    """
    if ziel_ordner is None:
        ziel_ordner = BASE_DIR

    if not os.path.isfile(zip_path):
        return {'erfolg': False, 'dateien': 0, 'meldung': f'ZIP nicht gefunden: {zip_path}'}

    if not zipfile.is_zipfile(zip_path):
        return {'erfolg': False, 'dateien': 0, 'meldung': 'Keine gültige ZIP-Datei.'}

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            namelist = zf.namelist()
            # Nur .py / .db / .ini / .json / .txt Dateien wiederherstellen; niemals Backup Data selbst
            restore_names = [
                n for n in namelist
                if not n.replace('\\', '/').startswith('Backup Data/')
                and os.path.splitext(n)[1].lower() not in _ZIP_EXCLUDE_EXTS
            ]
            for member in restore_names:
                target = os.path.join(ziel_ordner, member)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(member) as src, open(target, 'wb') as dst:
                    shutil.copyfileobj(src, dst)

        return {
            'erfolg':  True,
            'dateien': len(restore_names),
            'meldung': f'{len(restore_names)} Dateien aus {os.path.basename(zip_path)} wiederhergestellt.',
        }
    except Exception as e:
        return {'erfolg': False, 'dateien': 0, 'meldung': f'Fehler beim Wiederherstellen: {e}'}
