"""
WebNesk – Hilfsfunktionen
==========================
Wiederverwendbare Funktionen, die auch vom externen Python-Programm
importiert werden können.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Pfad zur Datenbankdatei (relativ zu diesem Skript auflösen)
_THIS_DIR = Path(__file__).parent
DB_PATH = _THIS_DIR.parent / "database" / "nesk.db"


def get_connection(path: str | Path = DB_PATH) -> sqlite3.Connection:
    """
    Gibt eine SQLite-Verbindung mit WAL-Modus zurück.
    Geeignet für den Lesezugriff durch externe Python-Programme.

    Beispiel:
        con = get_connection()
        rows = con.execute("SELECT * FROM vehicle_states").fetchall()
        con.close()
    """
    con = sqlite3.connect(str(path), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con


def get_latest_vehicle_states(con: sqlite3.Connection) -> list[dict]:
    """
    Gibt den jeweils letzten Fahrzeugzustand für jedes Fahrzeug zurück.

    Returns:
        Liste von dicts mit Fahrzeugdaten sortiert nach vehicle_name.
    """
    rows = con.execute("""
        SELECT v.*
        FROM vehicle_states v
        INNER JOIN (
            SELECT vehicle_name, MAX(recorded_at) AS max_ts
            FROM vehicle_states
            GROUP BY vehicle_name
        ) latest ON v.vehicle_name = latest.vehicle_name
                  AND v.recorded_at = latest.max_ts
        ORDER BY v.vehicle_name
    """).fetchall()
    return [dict(r) for r in rows]


def get_recent_shifts(con: sqlite3.Connection, days: int = 7) -> list[dict]:
    """
    Gibt Schichtübergaben der letzten `days` Tage zurück.

    Args:
        con:  SQLite-Verbindung
        days: Anzahl Tage rückwirkend (Standard: 7)

    Returns:
        Liste von dicts mit Schichtübergabe-Daten.
    """
    from datetime import date, timedelta
    since = (date.today() - timedelta(days=days)).isoformat()
    rows = con.execute(
        "SELECT * FROM shift_handovers WHERE shift_date >= ? ORDER BY shift_date DESC, created_at DESC",
        (since,),
    ).fetchall()
    return [dict(r) for r in rows]


def now_iso() -> str:
    """Gibt den aktuellen UTC-Zeitstempel als ISO-8601-String zurück."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------
# Jinja2-Filter (registriert in der Flask-App falls importiert)
# ---------------------------------------------------------------
def nl2br(value: str) -> str:
    """Wandelt Zeilenumbrüche in HTML <br>-Tags um."""
    if not value:
        return ""
    return value.replace("\n", "<br>\n")
