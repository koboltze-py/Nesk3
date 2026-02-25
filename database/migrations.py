"""
Datenbankmigrationen
Erstellt alle benötigten Tabellen beim ersten Start (SQLite)
"""
from .connection import get_connection


SQL_SCHEMA = """
PRAGMA foreign_keys = ON;

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

CREATE TABLE IF NOT EXISTS dienstplan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    mitarbeiter_id  INTEGER REFERENCES mitarbeiter(id) ON DELETE SET NULL,
    datum           TEXT NOT NULL,
    start_uhrzeit   TEXT NOT NULL,
    end_uhrzeit     TEXT NOT NULL,
    position        TEXT DEFAULT '',
    schicht_typ     TEXT DEFAULT 'regulaer'
                    CHECK (schicht_typ IN ('regulaer','nacht','bereitschaft')),
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

CREATE TABLE IF NOT EXISTS uebergabe_protokolle (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datum               TEXT NOT NULL,
    schicht_typ         TEXT NOT NULL
                        CHECK (schicht_typ IN ('tagdienst','nachtdienst')),
    beginn_zeit         TEXT DEFAULT '',
    ende_zeit           TEXT DEFAULT '',
    patienten_anzahl    INTEGER DEFAULT 0,
    personal            TEXT DEFAULT '',
    ereignisse          TEXT DEFAULT '',
    massnahmen          TEXT DEFAULT '',
    uebergabe_notiz     TEXT DEFAULT '',
    ersteller           TEXT DEFAULT '',
    abzeichner          TEXT DEFAULT '',
    status              TEXT DEFAULT 'offen'
                        CHECK (status IN ('offen','abgeschlossen')),
    erstellt_am         TEXT DEFAULT (datetime('now','localtime')),
    geaendert_am        TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS fahrzeuge (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    kennzeichen     TEXT NOT NULL UNIQUE,
    typ             TEXT DEFAULT '',
    marke           TEXT DEFAULT '',
    modell          TEXT DEFAULT '',
    baujahr         INTEGER,
    fahrgestellnr   TEXT DEFAULT '',
    tuev_datum      TEXT DEFAULT '',
    notizen         TEXT DEFAULT '',
    aktiv           INTEGER DEFAULT 1,
    erstellt_am     TEXT DEFAULT (datetime('now','localtime')),
    geaendert_am    TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS fahrzeug_status (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fahrzeug_id     INTEGER NOT NULL REFERENCES fahrzeuge(id) ON DELETE CASCADE,
    status          TEXT NOT NULL
                    CHECK (status IN ('fahrbereit','defekt','werkstatt','ausser_dienst','sonstiges')),
    von             TEXT NOT NULL,
    bis             TEXT DEFAULT '',
    grund           TEXT DEFAULT '',
    erstellt_am     TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS fahrzeug_schaeden (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fahrzeug_id     INTEGER NOT NULL REFERENCES fahrzeuge(id) ON DELETE CASCADE,
    datum           TEXT NOT NULL,
    beschreibung    TEXT NOT NULL,
    schwere         TEXT DEFAULT 'gering'
                    CHECK (schwere IN ('gering','mittel','schwer')),
    kommentar       TEXT DEFAULT '',
    behoben         INTEGER DEFAULT 0,
    behoben_am      TEXT DEFAULT '',
    erstellt_am     TEXT DEFAULT (datetime('now','localtime')),
    geaendert_am    TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS fahrzeug_termine (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fahrzeug_id     INTEGER NOT NULL REFERENCES fahrzeuge(id) ON DELETE CASCADE,
    datum           TEXT NOT NULL,
    uhrzeit         TEXT DEFAULT '',
    typ             TEXT DEFAULT 'sonstiges'
                    CHECK (typ IN ('tuev','inspektion','reparatur','hauptuntersuchung','sonstiges')),
    titel           TEXT NOT NULL,
    beschreibung    TEXT DEFAULT '',
    kommentar       TEXT DEFAULT '',
    erledigt        INTEGER DEFAULT 0,
    erstellt_am     TEXT DEFAULT (datetime('now','localtime')),
    geaendert_am    TEXT DEFAULT (datetime('now','localtime'))
);
"""

_default_ordner = (
    r'C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - '
    r'Kreisverband Koeln e.V\Dateien von Erste-Hilfe-Station-'
    r'Flughafen - DRK Koeln e.V_ - !Gemeinsam.26\04_Tagesdienstplaene'
)

_DEFAULT_ABTEILUNGEN = [
    ('Erste-Hilfe-Station', 'Flughafen Erste-Hilfe-Station'),
    ('Sanitaetsdienst',     'Allgemeiner Sanitaetsdienst'),
    ('Verwaltung',          'Administrative Aufgaben'),
]

_DEFAULT_POSITIONEN = [
    ('Rettungssanitaeter', 'RS'),
    ('Rettungsassistent',  'RA'),
    ('Notfallsanitaeter',  'NFS'),
    ('Sanitaetshelfer',    'SH'),
    ('Schichtleiter',      'SL'),
    ('Einsatzleiter',      'EL'),
]


def run_migrations():
    """Fuehrt alle Migrationen aus und erstellt die SQLite-Datenbank-Tabellen."""
    conn = get_connection()
    try:
        conn.executescript(SQL_SCHEMA)
        cur = conn.cursor()

        for name, beschreibung in _DEFAULT_ABTEILUNGEN:
            cur.execute(
                "INSERT OR IGNORE INTO abteilungen (name, beschreibung) VALUES (?, ?)",
                (name, beschreibung)
            )
        for name, kuerzel in _DEFAULT_POSITIONEN:
            cur.execute(
                "INSERT OR IGNORE INTO positionen (name, kuerzel) VALUES (?, ?)",
                (name, kuerzel)
            )
        cur.execute(
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