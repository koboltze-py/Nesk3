"""
SQLite Datenbankverbindung
Verwaltet Verbindungen zur Nesk3 SQLite-Datenbank.
WAL-Modus für sicheres gleichzeitiges Lesen von mehreren PCs.
"""
import sqlite3
from contextlib import contextmanager
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


def _row_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Gibt jede Zeile als dict zurück (Spaltenname → Wert)."""
    cols = [c[0] for c in cursor.description]
    return dict(zip(cols, row))


def get_connection() -> sqlite3.Connection:
    """Gibt eine neue SQLite-Verbindung zurück (WAL-Modus, dict-Zeilen)."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = _row_factory
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA synchronous = NORMAL")
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
        row = cur.fetchone()
        version = row["sqlite_version()"] if row else "?"
        conn.close()
        return True, f"SQLite {version}  |  {DB_PATH}"
    except Exception as e:
        return False, str(e)


@contextmanager
def db_cursor(commit: bool = False):
    """
    Kontextmanager für DB-Cursor mit automatischem Commit/Rollback.
    Cursor liefert Zeilen als dict.

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
