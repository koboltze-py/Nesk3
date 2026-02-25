"""
WebNesk – Startdatei
=====================
Startet den Flask-Entwicklungsserver lokal.

Verwendung:
    python run.py

Die WebApp ist dann erreichbar unter: http://127.0.0.1:5000
"""

from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    sep = "=" * 54
    print(sep)
    print(f"  {Config.APP_NAME}")
    print(f"  URL    : http://{Config.HOST}:{Config.PORT}")
    print(f"  DB     : {Config.DATABASE_PATH}")
    print(f"  Login  : admin / drk2026")
    print(sep)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False,
    )
