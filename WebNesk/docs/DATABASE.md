# Datenbankdokumentation – WebNesk

> Diese Datei ist die **verbindliche Referenz** für alle Programme,
> die auf die SQLite-Datenbank `database/nesk.db` zugreifen.

---

## Allgemein

| Eigenschaft   | Wert |
|---------------|------|
| Format        | SQLite 3 |
| Dateipfad     | `database/nesk.db` (relativ zum Projektordner) |
| WAL-Modus     | **aktiviert** (`PRAGMA journal_mode=WAL`) |
| Fremdschlüssel| aktiviert (`PRAGMA foreign_keys=ON`) |
| Zeichensatz   | UTF-8 |
| Zeitstempel   | Alle Felder `created_at`, `recorded_at` werden als **ISO-8601-String** gespeichert (`2026-02-25T10:30:00+00:00`) |

---

## Paralleler Zugriff (Python-Programm)

Der WAL-Modus (Write-Ahead Logging) ist aktiviert.
Das bedeutet:

- **Ein Schreiber und beliebig viele Leser** können gleichzeitig auf die Datenbank zugreifen.
- Das externe Python-Programm kann die Datenbank jederzeit **lesen**, auch während die WebApp aktiv ist.
- Es gibt **keine Dateisperr-Konflikte** beim Lesen.

**Empfohlener Python-Zugriff:**

```python
import sqlite3

DB_PATH = r"C:\...\WebNesk\database\nesk.db"

con = sqlite3.connect(DB_PATH, timeout=30)
con.row_factory = sqlite3.Row  # Spaltenzugriff per Name
con.execute("PRAGMA journal_mode=WAL;")
con.execute("PRAGMA foreign_keys=ON;")

cursor = con.execute("SELECT * FROM vehicle_states ORDER BY recorded_at DESC")
for row in cursor:
    print(dict(row))

con.close()
```

---

## Tabelle: `users`

Benutzerkonten der WebApp.

| Spalte         | Typ     | Nullable | Beschreibung |
|----------------|---------|----------|--------------|
| `id`           | INTEGER | Nein     | Primärschlüssel (auto-increment) |
| `username`     | TEXT    | Nein     | Eindeutiger Benutzername |
| `password_hash`| TEXT    | Nein     | Werkzeug/bcrypt-Hash (nur für WebApp relevant) |
| `full_name`    | TEXT    | Nein     | Vollständiger Name |
| `role`         | TEXT    | Nein     | `'admin'` oder `'user'` |
| `created_at`   | TEXT    | Nein     | ISO-8601 Zeitstempel |

---

## Tabelle: `vehicle_states`

Fahrzeugzustände (jeder Eintrag = eine Erfassung).

| Spalte            | Typ     | Nullable | Beschreibung |
|-------------------|---------|----------|--------------|
| `id`              | INTEGER | Nein     | Primärschlüssel |
| `vehicle_name`    | TEXT    | Nein     | Fahrzeugname oder Kennzeichen |
| `status`          | TEXT    | Nein     | Siehe Status-Werte unten |
| `mileage`         | REAL    | Ja       | Kilometerstand (km) |
| `fuel_level`      | INTEGER | Ja       | Kraftstoffstand 0–100 (%) |
| `notes`           | TEXT    | Ja       | Bemerkungen / Mängel |
| `recorded_at`     | TEXT    | Nein     | ISO-8601 Zeitstempel der Erfassung |
| `created_at`      | TEXT    | Nein     | ISO-8601 Zeitstempel der DB-Eintragung |
| `recorded_by_id`  | INTEGER | Ja       | FK → `users.id` |

### Gültige `status`-Werte

| Wert             | Bedeutung |
|------------------|-----------|
| `einsatzbereit`  | Fahrzeug ist vollständig einsatzbereit |
| `defekt`         | Fahrzeug hat einen Defekt |
| `in_reparatur`   | Fahrzeug ist in der Werkstatt |
| `ausser_dienst`  | Fahrzeug vorübergehend außer Dienst |

---

## Tabelle: `shift_handovers`

Dokumentierte Schichtübergaben.

| Spalte           | Typ     | Nullable | Beschreibung |
|------------------|---------|----------|--------------|
| `id`             | INTEGER | Nein     | Primärschlüssel |
| `handover_from`  | TEXT    | Nein     | Name der übergebenden Person |
| `handover_to`    | TEXT    | Nein     | Name der übernehmenden Person |
| `shift_date`     | TEXT    | Nein     | Datum der Schicht (YYYY-MM-DD) |
| `shift_type`     | TEXT    | Nein     | Siehe Schichttypen unten |
| `incidents`      | TEXT    | Ja       | Besondere Vorkommnisse |
| `vehicle_status` | TEXT    | Ja       | Fahrzeugzustand bei Übergabe |
| `material_status`| TEXT    | Ja       | Materialstand / Verbrauch |
| `open_tasks`     | TEXT    | Ja       | Offene Aufgaben |
| `created_at`     | TEXT    | Nein     | ISO-8601 Zeitstempel |
| `created_by_id`  | INTEGER | Ja       | FK → `users.id` |

### Gültige `shift_type`-Werte

| Wert      | Bedeutung |
|-----------|-----------|
| `frueh`   | Frühschicht |
| `spaet`   | Spätschicht |
| `nacht`   | Nachtschicht |
| `sonstig` | Sonstige |

---

## Beispiel-Abfragen für externe Python-Programme

```python
import sqlite3

DB_PATH = r"C:\...\WebNesk\database\nesk.db"

with sqlite3.connect(DB_PATH, timeout=30) as con:
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")

    # Alle Fahrzeuge mit Status "defekt"
    defekte = con.execute(
        "SELECT * FROM vehicle_states WHERE status = 'defekt' ORDER BY recorded_at DESC"
    ).fetchall()

    # Schichtübergaben der letzten 7 Tage
    import datetime
    seit = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    uebergaben = con.execute(
        "SELECT * FROM shift_handovers WHERE shift_date >= ? ORDER BY shift_date DESC",
        (seit,)
    ).fetchall()

    # Letzter erfasster Zustand je Fahrzeug
    letzte = con.execute("""
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
```
