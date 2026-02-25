"""
Modell: Benutzer (users)
=========================
Speichert Benutzerkonten mit verschlüsseltem Passwort.

Tabelle: users
--------------
Spalte          | Typ     | Beschreibung
----------------|---------|---------------------------
id              | INTEGER | Primärschlüssel (auto)
username        | TEXT    | Eindeutiger Benutzername
password_hash   | TEXT    | Bcrypt-Hash des Passworts
full_name       | TEXT    | Vollständiger Name
role            | TEXT    | 'admin' oder 'user'
created_at      | TEXT    | ISO-8601 Zeitstempel
"""

from datetime import datetime, timezone
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128), nullable=False, default="")
    role = db.Column(db.String(16), nullable=False, default="user")
    created_at = db.Column(
        db.String(32),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    # Beziehungen
    vehicle_states = db.relationship("VehicleState", back_populates="recorded_by_user", lazy="dynamic")
    shift_handovers = db.relationship("ShiftHandover", back_populates="created_by_user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_admin(self):
        return self.role == "admin"
