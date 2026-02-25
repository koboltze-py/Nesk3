"""
Modell: Fahrzeugzustand (vehicle_states)
=========================================
Erfasst den Zustand eines Fahrzeugs zu einem bestimmten Zeitpunkt.

Tabelle: vehicle_states
-----------------------
Spalte          | Typ     | Beschreibung
----------------|---------|------------------------------------------
id              | INTEGER | Primärschlüssel (auto)
vehicle_name    | TEXT    | Fahrzeugname oder Kennzeichen
status          | TEXT    | einsatzbereit | defekt | in_reparatur | ausser_dienst
mileage         | REAL    | Kilometerstand (kann NULL sein)
fuel_level      | INTEGER | Kraftstoffstand in % (0–100, kann NULL sein)
notes           | TEXT    | Bemerkungen, Mängel (kann NULL sein)
recorded_at     | TEXT    | ISO-8601 Zeitstempel der Erfassung
recorded_by_id  | INTEGER | FK → users.id (kann NULL sein, z.B. kein Login)
created_at      | TEXT    | ISO-8601 Zeitstempel der DB-Eintragung

Gültige Status-Werte:
    'einsatzbereit'  – Fahrzeug ist vollständig einsatzbereit
    'defekt'         – Fahrzeug hat einen Defekt, eingeschränkt oder nicht nutzbar
    'in_reparatur'   – Fahrzeug befindet sich in der Werkstatt
    'ausser_dienst'  – Fahrzeug vorübergehend außer Dienst gestellt
"""

from datetime import datetime, timezone
from app import db

# Gültige Status-Werte (auch für externe Python-Programme)
VEHICLE_STATUS_VALUES = [
    "einsatzbereit",
    "defekt",
    "in_reparatur",
    "ausser_dienst",
]

VEHICLE_STATUS_LABELS = {
    "einsatzbereit": "Einsatzbereit",
    "defekt": "Defekt",
    "in_reparatur": "In Reparatur",
    "ausser_dienst": "Außer Dienst",
}

VEHICLE_STATUS_COLORS = {
    "einsatzbereit": "success",
    "defekt": "danger",
    "in_reparatur": "warning",
    "ausser_dienst": "secondary",
}


class VehicleState(db.Model):
    __tablename__ = "vehicle_states"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="einsatzbereit")
    mileage = db.Column(db.Float, nullable=True)
    fuel_level = db.Column(db.Integer, nullable=True)  # 0-100 %
    notes = db.Column(db.Text, nullable=True)
    recorded_at = db.Column(
        db.String(32),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )
    created_at = db.Column(
        db.String(32),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    # Fremdschlüssel zum Benutzer
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    recorded_by_user = db.relationship("User", back_populates="vehicle_states")

    def __repr__(self):
        return f"<VehicleState {self.vehicle_name} – {self.status}>"

    @property
    def status_label(self):
        return VEHICLE_STATUS_LABELS.get(self.status, self.status)

    @property
    def status_color(self):
        return VEHICLE_STATUS_COLORS.get(self.status, "secondary")
