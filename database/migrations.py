"""
Datenbankmigrationen
Erstellt alle benötigten Tabellen beim ersten Start (SQLite)
"""
from .connection import get_connection


SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS abteilungen (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    beschreibung    TEXT DEFAULT '',
    erstellt_am     TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS positionen (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    kuerzel         TEXT DEFAULT '',
    erstellt_am     TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS mitarbeiter (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vorname         TEXT NOT NULL,
    nachname        TEXT NOT NULL,
    personalnummer  TEXT UNIQUE,
    position        TEXT DEFAULT '',
    abteilung       TEXT DEFAULT '',
    email           TEXT DEFAULT '',
    telefon         TEXT DEFAULT '',
    eintrittsdatum  TEXT,
    status          TEXT DEFAULT 'aktiv'
                    CHECK (status IN ('aktiv','inaktiv','beurlaubt')),
    erstellt_am     TEXT DEFAULT (datetime('now','localtime')),
    geaendert_am    TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TRIGGER IF NOT EXISTS trg_mitarbeiter_geaendert_am
AFTER UPDATE ON mitarbeiter
FOR EACH ROW
BEGIN
    UPDATE mitarbeiter SET geaendert_am = datetime('now','localtime')
    WHERE id = OLD.id;
END;

CREATE TABLE IF NOT EXISTS dienstplan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    mitarbeiter_id  INTEGER REFERENCES mitarbeiter(id) ON DELETE SET NULL,
    datum           TEXT NOT NULL,
    start_uhrzeit   TEXT NOT NULL,
    end_uhrzeit     TEXT NOT NULL,
    position        TEXT DEFAULT '',
    schicht_typ     TEXT DEFAULT 'regulär'
                    CHECK (schicht_typ IN ('regulär','nacht','bereitschaft')),
    notizen         TEXT DEFAULT '',
    erstellt_am     TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS backup_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    dateiname       TEXT NOT NULL,
    typ             TEXT DEFAULT 'manuell',
    erstellt_am     TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS settings (
    schluessel  TEXT PRIMARY KEY,
    wert        TEXT NOT NULL DEFAULT ''
);
"""


def run_migrations():
    """Führt alle Migrationen aus und erstellt die SQLite-Datenbank."""
    conn = get_connection()
    try:
        conn.executescript(SQL_SCHEMA)
        conn.execute(
            "INSERT OR IGNORE INTO abteilungen (name, beschreibung) VALUES "
            "('Erste-Hilfe-Station','Flughafen Erste-Hilfe-Station'),"
            "('Sanitätsdienst','Allgemeiner Sanitätsdienst'),"
            "('Verwaltung','Administrative Aufgaben')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO positionen (name, kuerzel) VALUES "
            "('Rettungssanitäter','RS'),('Rettungsassistent','RA'),"
            "('Notfallsanitäter','NFS'),('Sanitätshelfer','SH'),"
            "('Schichtleiter','SL'),('Einsatzleiter','EL')"
        )
        # Default-Einstellungen
        _default_ordner = (
            r'C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - '
            r'Kreisverband Köln e.V\Dateien von Erste-Hilfe-Station-'
            r'Flughafen - DRK Köln e.V_ - !Gemeinsam.26\04_Tagesdienstpläne'
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings (schluessel, wert) VALUES (?, ?)",
            ('dienstplan_ordner', _default_ordner)
        )
        conn.commit()
        print("[OK] Datenbank bereit.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
