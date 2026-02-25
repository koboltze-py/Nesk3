-- =============================================================
-- WebNesk – SQLite Datenbankschema
-- =============================================================
-- Datei:    database/schema.sql
-- Zweck:    Referenz-Dokumentation des vollständigen DB-Schemas
--           (Die Tabellen werden automatisch von SQLAlchemy erstellt)
-- WAL-Modus: PRAGMA journal_mode=WAL  (aktiviert beim App-Start)
-- Erstellt: 2026
-- =============================================================

-- Fremdschlüssel aktivieren (wichtig für SQLite)
PRAGMA foreign_keys = ON;

-- WAL-Modus für konfliktfreien parallelen Lesezugriff aktivieren
PRAGMA journal_mode = WAL;

-- =============================================================
-- Tabelle: users
-- Zweck:   Benutzerkonten für den WebNesk-Login
-- =============================================================
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    full_name     TEXT    NOT NULL DEFAULT '',
    role          TEXT    NOT NULL DEFAULT 'user'
                          CHECK(role IN ('admin', 'user')),
    created_at    TEXT    NOT NULL   -- ISO-8601: 2026-02-25T10:30:00+00:00
);

-- =============================================================
-- Tabelle: vehicle_states
-- Zweck:   Erfasste Fahrzeugzustände (Fahrzeugbuch)
-- =============================================================
CREATE TABLE IF NOT EXISTS vehicle_states (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_name     TEXT    NOT NULL,        -- Fahrzeugname oder Kennzeichen
    status           TEXT    NOT NULL         -- Siehe STATUS-WERTE unten
                             CHECK(status IN (
                               'einsatzbereit',
                               'defekt',
                               'in_reparatur',
                               'ausser_dienst'
                             )),
    mileage          REAL,                    -- Kilometerstand (NULL = nicht angegeben)
    fuel_level       INTEGER                  -- Kraftstoff in % 0-100 (NULL = nicht angegeben)
                             CHECK(fuel_level IS NULL OR (fuel_level >= 0 AND fuel_level <= 100)),
    notes            TEXT,                    -- Bemerkungen / Mängel (NULL = keine)
    recorded_at      TEXT    NOT NULL,        -- ISO-8601 Zeitstempel der tatsächlichen Erfassung
    created_at       TEXT    NOT NULL,        -- ISO-8601 Zeitstempel der DB-Eintragung
    recorded_by_id   INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Index für schnelles Abfragen nach Fahrzeugname
CREATE INDEX IF NOT EXISTS idx_vehicle_states_name
    ON vehicle_states(vehicle_name);

-- Index für zeitbasierte Auswertungen
CREATE INDEX IF NOT EXISTS idx_vehicle_states_recorded_at
    ON vehicle_states(recorded_at);

-- =============================================================
-- Tabelle: shift_handovers
-- Zweck:   Dokumentation von Schichtübergaben
-- =============================================================
CREATE TABLE IF NOT EXISTS shift_handovers (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    handover_from    TEXT    NOT NULL,        -- Name der übergebenden Person
    handover_to      TEXT    NOT NULL,        -- Name der übernehmenden Person
    shift_date       TEXT    NOT NULL,        -- Datum der Schicht (YYYY-MM-DD)
    shift_type       TEXT    NOT NULL DEFAULT 'frueh'
                             CHECK(shift_type IN (
                               'frueh',       -- Frühschicht
                               'spaet',       -- Spätschicht
                               'nacht',       -- Nachtschicht
                               'sonstig'      -- Sonstige
                             )),
    incidents        TEXT,                    -- Besondere Vorkommnisse (NULL = keine)
    vehicle_status   TEXT,                    -- Fahrzeugzustand bei Übergabe (NULL = keine Angabe)
    material_status  TEXT,                    -- Materialstand / Verbrauch (NULL = keine Angabe)
    open_tasks       TEXT,                    -- Offene Aufgaben (NULL = keine)
    created_at       TEXT    NOT NULL,        -- ISO-8601 Zeitstempel der Eintragung
    created_by_id    INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Index für zeitbasierte Auswertungen
CREATE INDEX IF NOT EXISTS idx_shift_handovers_date
    ON shift_handovers(shift_date);
