"""
Route: Schichtübergaben (shifts)
==================================
Erstellen, anzeigen und verwalten von Schichtübergabeberichten.
"""

from datetime import datetime, timezone, date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models.shift import ShiftHandover, SHIFT_TYPE_VALUES, SHIFT_TYPE_LABELS

shifts_bp = Blueprint("shifts", __name__, url_prefix="/schichten")


@shifts_bp.route("/")
def list_shifts():
    """Liste aller Schichtübergaben, neueste zuerst."""
    page = request.args.get("page", 1, type=int)
    pagination = (
        ShiftHandover.query
        .order_by(ShiftHandover.shift_date.desc(), ShiftHandover.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template(
        "shifts/list.html",
        shifts=pagination.items,
        pagination=pagination,
    )


@shifts_bp.route("/neu", methods=["GET", "POST"])
def new_shift():
    """Neue Schichtübergabe erfassen."""
    if request.method == "POST":
        handover_from = request.form.get("handover_from", "").strip()
        handover_to = request.form.get("handover_to", "").strip()
        shift_date = request.form.get("shift_date", "").strip()
        shift_type = request.form.get("shift_type", "frueh")
        incidents = request.form.get("incidents", "").strip()
        vehicle_status = request.form.get("vehicle_status", "").strip()
        material_status = request.form.get("material_status", "").strip()
        open_tasks = request.form.get("open_tasks", "").strip()

        # Validierung
        errors = []
        if not handover_from:
            errors.append("Übergebende Person fehlt.")
        if not handover_to:
            errors.append("Übernehmende Person fehlt.")
        if not shift_date:
            errors.append("Datum fehlt.")
        if shift_type not in SHIFT_TYPE_VALUES:
            errors.append("Ungültiger Schichttyp.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "shifts/form.html",
                shift_type_values=SHIFT_TYPE_VALUES,
                shift_type_labels=SHIFT_TYPE_LABELS,
                today=date.today().isoformat(),
            )

        entry = ShiftHandover(
            handover_from=handover_from,
            handover_to=handover_to,
            shift_date=shift_date,
            shift_type=shift_type,
            incidents=incidents or None,
            vehicle_status=vehicle_status or None,
            material_status=material_status or None,
            open_tasks=open_tasks or None,
            created_by_id=None,
        )
        db.session.add(entry)
        db.session.commit()
        flash(f"Schichtübergabe vom {shift_date} gespeichert.", "success")
        return redirect(url_for("shifts.list_shifts"))

    return render_template(
        "shifts/form.html",
        shift_type_values=SHIFT_TYPE_VALUES,
        shift_type_labels=SHIFT_TYPE_LABELS,
        today=date.today().isoformat(),
    )


@shifts_bp.route("/<int:shift_id>")
def detail_shift(shift_id):
    """Detailansicht einer Schichtübergabe."""
    entry = db.get_or_404(ShiftHandover, shift_id)
    return render_template("shifts/detail.html", entry=entry)


@shifts_bp.route("/<int:shift_id>/loeschen", methods=["POST"])
def delete_shift(shift_id):
    """Schichtübergabe löschen."""
    entry = db.get_or_404(ShiftHandover, shift_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Schichtübergabe gelöscht.", "info")
    return redirect(url_for("shifts.list_shifts"))
