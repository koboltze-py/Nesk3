"""
Datenbankmodelle (Datenklassen)
Spiegeln die PostgreSQL-Tabellenstruktur wider
"""
from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional


@dataclass
class Mitarbeiter:
    """Repräsentiert einen Mitarbeiter."""
    id:             Optional[int]  = None
    vorname:        str            = ""
    nachname:       str            = ""
    personalnummer: str            = ""
    position:       str            = ""
    abteilung:      str            = ""
    email:          str            = ""
    telefon:        str            = ""
    eintrittsdatum: Optional[date] = None
    status:         str            = "aktiv"      # aktiv | inaktiv | beurlaubt
    erstellt_am:    Optional[datetime] = None
    geaendert_am:   Optional[datetime] = None

    @property
    def vollname(self) -> str:
        return f"{self.vorname} {self.nachname}".strip()


@dataclass
class Dienstplan:
    """Repräsentiert einen Dienstplan-Eintrag (Schicht)."""
    id:                  Optional[int]  = None
    mitarbeiter_id:      Optional[int]  = None
    mitarbeiter_name:    str            = ""
    datum:               Optional[date] = None
    start_uhrzeit:       Optional[time] = None
    end_uhrzeit:         Optional[time] = None
    position:            str            = ""
    schicht_typ:         str            = "regulär"  # regulär | nacht | bereitschaft
    notizen:             str            = ""
    erstellt_am:         Optional[datetime] = None


@dataclass
class Abteilung:
    """Repräsentiert eine Abteilung/Gruppe."""
    id:          Optional[int] = None
    name:        str           = ""
    beschreibung: str          = ""


@dataclass
class Position:
    """Repräsentiert eine Stellenbezeichnung."""
    id:   Optional[int] = None
    name: str           = ""
    kuerzel: str        = ""
