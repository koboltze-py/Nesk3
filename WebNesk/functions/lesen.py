"""
WebNesk – Python-Leseprogramm
==============================
Liest Daten aus dem JSON-Export der lokalen WebApp ODER
direkt aus der SQLite-Datenbank (nesk.db).

Verwendung:
    python lesen.py                      # zeigt alle Daten aus JSON
    python lesen.py --db                 # direkt aus SQLite lesen
    python lesen.py --json nesk_export.json --to-sqlite nesk.db
                                         # JSON → SQLite konvertieren
"""

import json
import sqlite3
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta


# ================================================================
# Pfade
# ================================================================
BASE_DIR  = Path(__file__).parent
JSON_PATH = BASE_DIR / "nesk_export.json"   # Standard-Exportdatei
DB_PATH   = BASE_DIR / "database" / "nesk.db"


# ================================================================
# SQLite-Verbindung (WAL-Modus, konfliktfrei lesbar)
# ================================================================
def get_db_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Öffnet die SQLite-Datenbank im WAL-Modus.
    Kann gleichzeitig mit der laufenden WebApp (Flask oder lokal) genutzt werden.
    """
    con = sqlite3.connect(str(path), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con


# ================================================================
# JSON → SQLite konvertieren
# ================================================================
def json_to_sqlite(json_path: Path, db_path: Path) -> None:
    """
    Konvertiert den JSON-Export der lokalen WebApp in eine SQLite-Datenbank.
    Die erzeugte Datei hat dasselbe Schema wie die Flask-WebApp-Datenbank.

    Tabellen: users, vehicle_states, shift_handovers
    """
    print(f"Lese JSON von: {json_path}")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Schreibe SQLite nach: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    # Schema
    cur.executescript("""
        PRAGMA foreign_keys=ON;
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL DEFAULT '',
            full_name     TEXT    NOT NULL DEFAULT '',
            role          TEXT    NOT NULL DEFAULT 'user',
            created_at    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vehicle_states (
            id              INTEGER PRIMARY KEY,
            vehicle_name    TEXT    NOT NULL,
            status          TEXT    NOT NULL,
            mileage         REAL,
            fuel_level      INTEGER,
            notes           TEXT,
            recorded_at     TEXT    NOT NULL,
            created_at      TEXT    NOT NULL,
            recorded_by_id  INTEGER REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS shift_handovers (
            id               INTEGER PRIMARY KEY,
            handover_from    TEXT    NOT NULL,
            handover_to      TEXT    NOT NULL,
            shift_date       TEXT    NOT NULL,
            shift_type       TEXT    NOT NULL DEFAULT 'frueh',
            incidents        TEXT,
            vehicle_status   TEXT,
            material_status  TEXT,
            open_tasks       TEXT,
            created_at       TEXT    NOT NULL,
            created_by_id    INTEGER REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_vehicle_name ON vehicle_states(vehicle_name);
        CREATE INDEX IF NOT EXISTS idx_vehicle_date ON vehicle_states(recorded_at);
        CREATE INDEX IF NOT EXISTS idx_shift_date   ON shift_handovers(shift_date);
    """)

    # Benutzer
    for u in data.get("users", []):
        cur.execute(
            "INSERT OR REPLACE INTO users(id,username,password_hash,full_name,role,created_at) VALUES(?,?,?,?,?,?)",
            (u["id"], u["username"], "", u.get("full_name", ""), u.get("role", "user"), u.get("created_at", ""))
        )

    # Fahrzeugzustände
    for v in data.get("vehicles", []):
        cur.execute(
            "INSERT OR REPLACE INTO vehicle_states(id,vehicle_name,status,mileage,fuel_level,notes,recorded_at,created_at,recorded_by_id) VALUES(?,?,?,?,?,?,?,?,?)",
            (v["id"], v["vehicle_name"], v["status"], v.get("mileage"), v.get("fuel_level"),
             v.get("notes"), v["recorded_at"], v["created_at"], None)
        )

    # Schichtübergaben
    for s in data.get("shifts", []):
        cur.execute(
            "INSERT OR REPLACE INTO shift_handovers(id,handover_from,handover_to,shift_date,shift_type,incidents,vehicle_status,material_status,open_tasks,created_at,created_by_id) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (s["id"], s["handover_from"], s["handover_to"], s["shift_date"], s.get("shift_type", "frueh"),
             s.get("incidents"), s.get("vehicle_status"), s.get("material_status"),
             s.get("open_tasks"), s["created_at"], None)
        )

    con.commit()
    con.close()
    print(f"  → {len(data.get('vehicles', []))} Fahrzeugzustände")
    print(f"  → {len(data.get('shifts', []))}   Schichtübergaben")
    print("Konvertierung abgeschlossen.")


# ================================================================
# Hilfsfunktionen zum Lesen
# ================================================================

def read_vehicles_from_db(con: sqlite3.Connection) -> list[dict]:
    """Alle Fahrzeugzustände aus SQLite lesen."""
    rows = con.execute("SELECT * FROM vehicle_states ORDER BY recorded_at DESC").fetchall()
    return [dict(r) for r in rows]


def read_latest_per_vehicle(con: sqlite3.Connection) -> list[dict]:
    """Letzter Zustand je Fahrzeug."""
    rows = con.execute("""
        SELECT v.*
        FROM vehicle_states v
        INNER JOIN (
            SELECT vehicle_name, MAX(recorded_at) AS max_ts
            FROM vehicle_states GROUP BY vehicle_name
        ) latest ON v.vehicle_name = latest.vehicle_name
               AND v.recorded_at   = latest.max_ts
        ORDER BY v.vehicle_name
    """).fetchall()
    return [dict(r) for r in rows]


def read_shifts_from_db(con: sqlite3.Connection, days: int = None) -> list[dict]:
    """Schichtübergaben aus SQLite lesen, optional gefiltert nach letzten N Tagen."""
    if days:
        since = (date.today() - timedelta(days=days)).isoformat()
        rows = con.execute(
            "SELECT * FROM shift_handovers WHERE shift_date >= ? ORDER BY shift_date DESC",
            (since,)
        ).fetchall()
    else:
        rows = con.execute("SELECT * FROM shift_handovers ORDER BY shift_date DESC").fetchall()
    return [dict(r) for r in rows]


def read_vehicles_from_json(json_path: Path = JSON_PATH) -> list[dict]:
    """Fahrzeugzustände direkt aus JSON-Export lesen (ohne SQLite)."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f).get("vehicles", [])


def read_shifts_from_json(json_path: Path = JSON_PATH) -> list[dict]:
    """Schichtübergaben direkt aus JSON-Export lesen."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f).get("shifts", [])


# ================================================================
# CLI
# ================================================================
def main():
    parser = argparse.ArgumentParser(description="WebNesk Daten lesen / konvertieren")
    parser.add_argument("--db",        action="store_true", help="Aus SQLite-Datenbank lesen")
    parser.add_argument("--json",      type=str,            help="Pfad zur JSON-Exportdatei")
    parser.add_argument("--to-sqlite", type=str,            help="JSON nach SQLite konvertieren (Pfad zur .db-Datei)")
    parser.add_argument("--days",      type=int,            help="Nur Schichten der letzten N Tage anzeigen")
    args = parser.parse_args()

    json_path = Path(args.json) if args.json else JSON_PATH

    # JSON → SQLite konvertieren
    if args.to_sqlite:
        json_to_sqlite(json_path, Path(args.to_sqlite))
        return

    # Aus SQLite lesen
    if args.db:
        if not DB_PATH.exists():
            print(f"Datenbank nicht gefunden: {DB_PATH}")
            print("Tipp: Erst aus dem Browser exportieren oder Flask-WebApp einmal starten.")
            sys.exit(1)
        con = get_db_connection()
        vehicles = read_latest_per_vehicle(con)
        shifts   = read_shifts_from_db(con, days=args.days)
        con.close()

    # Aus JSON lesen (Standard)
    else:
        if not json_path.exists():
            print(f"JSON-Exportdatei nicht gefunden: {json_path}")
            print("Tipp: In der WebApp unter ☰ → Daten exportieren → Als JSON exportieren.")
            sys.exit(1)
        vehicles = sorted(read_vehicles_from_json(json_path), key=lambda x: x["recorded_at"], reverse=True)
        shifts   = sorted(read_shifts_from_json(json_path), key=lambda x: x["shift_date"], reverse=True)
        if args.days:
            since = (date.today() - timedelta(days=args.days)).isoformat()
            shifts = [s for s in shifts if s["shift_date"] >= since]

    # Ausgabe
    STATUS_LABELS = {
        "einsatzbereit": "Einsatzbereit",
        "defekt":        "DEFEKT!",
        "in_reparatur":  "In Reparatur",
        "ausser_dienst": "Außer Dienst",
    }

    print("\n" + "="*60)
    print("  FAHRZEUGZUSTÄNDE (letzter je Fahrzeug)")
    print("="*60)
    if not vehicles:
        print("  Keine Einträge.")
    for v in vehicles:
        status = STATUS_LABELS.get(v.get("status", ""), v.get("status", "–"))
        km = f"{v['mileage']:.0f} km" if v.get("mileage") is not None else "–"
        fuel = f"{v['fuel_level']}%" if v.get("fuel_level") is not None else "–"
        print(f"  {v['vehicle_name']:<20} | {status:<16} | {km:>10} | Kraftstoff: {fuel}")

    print("\n" + "="*60)
    print(f"  SCHICHTÜBERGABEN {'(letzten ' + str(args.days) + ' Tage)' if args.days else '(alle)'}")
    print("="*60)
    if not shifts:
        print("  Keine Einträge.")
    for s in shifts:
        print(f"  {s['shift_date']}  {s['handover_from']:<20} → {s['handover_to']}")
        if s.get("incidents"):
            print(f"    Vorkommnisse: {s['incidents'][:80]}")
    print()


if __name__ == "__main__":
    main()
