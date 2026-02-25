"""
Route: Dashboard
=================
Startseite nach dem Login.
"""

from flask import Blueprint, render_template
from app.models.vehicle import VehicleState
from app.models.shift import ShiftHandover

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/")


@dashboard_bp.route("/")
def index():
    # Letzte 5 Fahrzeugzustände und Schichtübergaben für die Übersicht
    recent_vehicles = (
        VehicleState.query.order_by(VehicleState.recorded_at.desc()).limit(5).all()
    )
    recent_shifts = (
        ShiftHandover.query.order_by(ShiftHandover.created_at.desc()).limit(5).all()
    )
    total_vehicles = VehicleState.query.count()
    total_shifts = ShiftHandover.query.count()

    return render_template(
        "dashboard/index.html",
        recent_vehicles=recent_vehicles,
        recent_shifts=recent_shifts,
        total_vehicles=total_vehicles,
        total_shifts=total_shifts,
    )
