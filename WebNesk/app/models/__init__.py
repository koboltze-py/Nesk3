# app/models/__init__.py
# Wird beim Import der models automatisch geladen
from app.models.user import User
from app.models.vehicle import VehicleState
from app.models.shift import ShiftHandover

__all__ = ["User", "VehicleState", "ShiftHandover"]
