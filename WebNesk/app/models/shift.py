"""
Modell: Schichtübergabe (shift_handovers)
==========================================
Dokumentiert eine vollständige Schichtübergabe.

Tabelle: shift_handovers
------------------------
Spalte           | Typ     | Beschreibung
-----------------|---------|------------------------------------------
id               | INTEGER | Primärschlüssel (auto)
handover_from    | TEXT    | Name der übergebenden Person
handover_to      | TEXT    | Name der übernehmenden Person
shift_date       | TEXT    | Datum der Schicht (ISO-8601: YYYY-MM-DD)
shift_type       | TEXT    | frueh | spaet | nacht | sonstig
incidents        | TEXT    | Besondere Vorkommnisse (kann NULL sein)
vehicle_status   | TEXT    | Fahrzeugzustand bei Übergabe (kann NULL sein)
material_status  | TEXT    | Materialstand / Verbrauch (kann NULL sein)
open_tasks       | TEXT    | Offene Aufgaben (kann NULL sein)
created_at       | TEXT    | ISO-8601 Zeitstempel der Eintragung
created_by_id    | INTEGER | FK → users.id (kann NULL sein)

Gültige Schichttypen (shift_type):
    'frueh'    – Frühschicht
    'spaet'    – Spätschicht
    'nacht'    – Nachtschicht
    'sonstig'  – Sonstige / individuell
"""

from datetime import datetime, timezone
from app import db

SHIFT_TYPE_VALUES = ["frueh", "spaet", "nacht", "sonstig"]
SHIFT_TYPE_LABELS = {
    "frueh": "Frühschicht",
    "spaet": "Spätschicht",
    "nacht": "Nachtschicht",
    "sonstig": "Sonstige",
}


class ShiftHandover(db.Model):
    __tablename__ = "shift_handovers"

    id = db.Column(db.Integer, primary_key=True)
    handover_from = db.Column(db.String(128), nullable=False)
    handover_to = db.Column(db.String(128), nullable=False)
    shift_date = db.Column(db.String(10), nullable=False)   # YYYY-MM-DD
    shift_type = db.Column(db.String(16), nullable=False, default="frueh")
    incidents = db.Column(db.Text, nullable=True)
    vehicle_status = db.Column(db.Text, nullable=True)
    material_status = db.Column(db.Text, nullable=True)
    open_tasks = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.String(32),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    # Fremdschlüssel zum Benutzer
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by_user = db.relationship("User", back_populates="shift_handovers")

    def __repr__(self):
        return f"<ShiftHandover {self.shift_date} {self.handover_from} → {self.handover_to}>"

    @property
    def shift_type_label(self):
        return SHIFT_TYPE_LABELS.get(self.shift_type, self.shift_type)
