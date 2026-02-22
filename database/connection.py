"""
SQLite Datenbankverbindung
Verwaltet Verbindungen zur Nesk3 SQLite-Datenbank
"""
import sqlite3
from contextlib import contextmanager
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


def _row_factory(cursor, row):
    """Gibt Zeilen als dict zurück."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_connection() -> sqlite3.Connection:
    """Gibt eine neue SQLite-Verbindung zurück."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _row_factory
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def test_connection() -> tuple[bool, str]:
    """
    Testet die Datenbankverbindung.
    Gibt (True, Info) oder (False, Fehlermeldung) zurück.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT sqlite_version()")
        version = cur.fetchone()["sqlite_version()"]
        conn.close()
        return True, f"SQLite {version}  |  {DB_PATH}"
    except Exception as e:
        return False, str(e)


@contextmanager
def db_cursor(commit: bool = False):
    """
    Kontextmanager für DB-Cursor mit automatischem Commit/Rollback.

    Verwendung:
        with db_cursor(commit=True) as cur:
            cur.execute("INSERT ...")
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
