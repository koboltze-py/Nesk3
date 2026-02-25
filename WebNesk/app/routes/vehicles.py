"""
Route: Fahrzeugzustände (vehicles)
====================================
Erstellen, anzeigen und verwalten von Fahrzeugzustandsberichten.
"""

from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.vehicle import VehicleState, VEHICLE_STATUS_VALUES, VEHICLE_STATUS_LABELS

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/fahrzeuge")


@vehicles_bp.route("/")
def list_vehicles():
    """Liste aller Fahrzeugzustände, neueste zuerst."""
    page = request.args.get("page", 1, type=int)
    query = VehicleState.query.order_by(VehicleState.recorded_at.desc())

    # Optionaler Filter nach Fahrzeug
    filter_name = request.args.get("fahrzeug", "").strip()
    if filter_name:
        query = query.filter(VehicleState.vehicle_name.ilike(f"%{filter_name}%"))

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template(
        "vehicles/list.html",
        vehicles=pagination.items,
        pagination=pagination,
        filter_name=filter_name,
    )


@vehicles_bp.route("/neu", methods=["GET", "POST"])
def new_vehicle():
    """Neuen Fahrzeugzustand erfassen."""
    if request.method == "POST":
        vehicle_name = request.form.get("vehicle_name", "").strip()
        status = request.form.get("status", "einsatzbereit")
        mileage_raw = request.form.get("mileage", "").strip()
        fuel_raw = request.form.get("fuel_level", "").strip()
        notes = request.form.get("notes", "").strip()
        recorded_at_raw = request.form.get("recorded_at", "").strip()

        # Validierung
        if not vehicle_name:
            flash("Fahrzeugname darf nicht leer sein.", "danger")
            return render_template("vehicles/form.html", status_values=VEHICLE_STATUS_VALUES, status_labels=VEHICLE_STATUS_LABELS)

        if status not in VEHICLE_STATUS_VALUES:
            flash("Ungültiger Status.", "danger")
            return render_template("vehicles/form.html", status_values=VEHICLE_STATUS_VALUES, status_labels=VEHICLE_STATUS_LABELS)

        mileage = float(mileage_raw) if mileage_raw else None
        fuel_level = int(fuel_raw) if fuel_raw else None

        if fuel_level is not None and not (0 <= fuel_level <= 100):
            flash("Kraftstoffstand muss zwischen 0 und 100 liegen.", "danger")
            return render_template("vehicles/form.html", status_values=VEHICLE_STATUS_VALUES, status_labels=VEHICLE_STATUS_LABELS)

        recorded_at = recorded_at_raw if recorded_at_raw else datetime.now(timezone.utc).isoformat()

        entry = VehicleState(
            vehicle_name=vehicle_name,
            status=status,
            mileage=mileage,
            fuel_level=fuel_level,
            notes=notes or None,
            recorded_at=recorded_at,
            recorded_by_id=None,
        )
        db.session.add(entry)
        db.session.commit()
        flash(f"Fahrzeugzustand für '{vehicle_name}' gespeichert.", "success")
        return redirect(url_for("vehicles.list_vehicles"))

    return render_template(
        "vehicles/form.html",
        status_values=VEHICLE_STATUS_VALUES,
        status_labels=VEHICLE_STATUS_LABELS,
        now=datetime.now().strftime("%Y-%m-%dT%H:%M"),
    )


@vehicles_bp.route("/<int:vehicle_id>")
def detail_vehicle(vehicle_id):
    """Detailansicht eines Fahrzeugzustands."""
    entry = db.get_or_404(VehicleState, vehicle_id)
    return render_template("vehicles/detail.html", entry=entry)


@vehicles_bp.route("/<int:vehicle_id>/loeschen", methods=["POST"])
def delete_vehicle(vehicle_id):
    """Fahrzeugzustand löschen."""
    entry = db.get_or_404(VehicleState, vehicle_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Eintrag gelöscht.", "info")
    return redirect(url_for("vehicles.list_vehicles"))
