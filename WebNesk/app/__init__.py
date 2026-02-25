"""
WebNesk – Flask App Factory
=============================
Erzeugt und konfiguriert die Flask-Anwendung.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# Globale Extensions (werden in create_app() mit der App verknüpft)
db = SQLAlchemy()


def _enable_wal_mode(dbapi_connection, connection_record):
    """
    Aktiviert WAL-Modus (Write-Ahead Logging) für SQLite.
    Ermöglicht konfliktfreien gleichzeitigen Lesezugriff
    durch externe Python-Programme.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


def create_app():
    """App-Factory: Erstellt und gibt die Flask-App zurück."""
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Extensions initialisieren
    db.init_app(app)

    # WAL-Modus bei jeder neuen SQLite-Verbindung aktivieren
    with app.app_context():
        from sqlalchemy.pool import Pool
        event.listen(Pool, "connect", _enable_wal_mode)

    # Modelle importieren & Tabellen erstellen
    with app.app_context():
        from app.models import user, vehicle, shift  # noqa: F401
        db.create_all()

    # Jinja2-Filter registrieren
    from functions.helpers import nl2br
    from markupsafe import Markup
    app.jinja_env.filters["nl2br"] = lambda v: Markup(nl2br(v))

    # Blueprints registrieren
    from app.routes.vehicles import vehicles_bp
    from app.routes.shifts import shifts_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(vehicles_bp)
    app.register_blueprint(shifts_bp)
    app.register_blueprint(dashboard_bp)

    return app


def _create_default_admin():
    """Erstellt einen Standard-Admin-User, falls noch keiner existiert."""
    from app.models.user import User
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("drk2026"),
            role="admin",
            full_name="Administrator",
        )
        db.session.add(admin)
        db.session.commit()
        print("[WebNesk] Standard-Admin erstellt: admin / drk2026")
