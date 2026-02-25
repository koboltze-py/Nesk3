"""
Einstellungs-Funktionen
Liest und schreibt Schlüssel-Wert-Paare aus der settings-Tabelle (SQLite).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_cursor

# Standardwerte, falls ein Schlüssel noch nicht in der DB steht
_DEFAULTS: dict[str, str] = {
    'dienstplan_ordner': (
        r'C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - '
        r'Kreisverband Köln e.V\Dateien von Erste-Hilfe-Station-'
        r'Flughafen - DRK Köln e.V_ - !Gemeinsam.26\04_Tagesdienstpläne'
    ),
    'sonderaufgaben_ordner': (
        r'C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - '
        r'Kreisverband Köln e.V\Dateien von Erste-Hilfe-Station-'
        r'Flughafen - DRK Köln e.V_ - !Gemeinsam.26\04_Tagesdienstpläne'
    ),
    'aocc_datei': (
        r'C:\Users\DRKairport\OneDrive - Deutsches Rotes Kreuz - '
        r'Kreisverband Köln e.V\Dateien von Erste-Hilfe-Station-Flughafen - '
        r'DRK Köln e.V_ - !Gemeinsam.26\Nesk\Nesk3\Daten\AOCC\AOCC Lagebericht.xlsm'
    ),
}


def get_setting(key: str, default: str = '') -> str:
    """
    Gibt den gespeicherten Wert für *key* zurück.
    Fällt auf _DEFAULTS oder *default* zurück, wenn der Schlüssel nicht existiert.
    """
    try:
        with db_cursor() as cur:
            cur.execute("SELECT wert FROM settings WHERE schluessel = ?", (key,))
            row = cur.fetchone()
            if row:
                return row['wert']
    except Exception:
        pass
    return _DEFAULTS.get(key, default)


def set_setting(key: str, value: str) -> bool:
    """
    Speichert *value* unter *key*.  Gibt True bei Erfolg zurück.
    """
    try:
        with db_cursor(commit=True) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO settings (schluessel, wert) VALUES (?, ?)",
                (key, value)
            )
        return True
    except Exception:
        return False


def get_alle_settings() -> dict[str, str]:
    """Gibt alle gespeicherten Einstellungen als dict zurück."""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT schluessel, wert FROM settings")
            return {row['schluessel']: row['wert'] for row in cur.fetchall()}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Ausschluss-Liste für Word-Export
# ---------------------------------------------------------------------------
import json as _json


def get_ausgeschlossene_namen() -> list[str]:
    """Gibt die persistierte Liste der ausgeschlossenen Vollnamen (lowercase) zurück."""
    raw = get_setting('export_ausgeschlossen', '[]')
    try:
        return _json.loads(raw)
    except Exception:
        return []


def set_ausgeschlossene_namen(namen: list[str]) -> bool:
    """Setzt die Ausschlussliste komplett neu."""
    try:
        bereinigt = list({n.lower().strip() for n in namen if n.strip()})
        return set_setting('export_ausgeschlossen', _json.dumps(bereinigt))
    except Exception:
        return False


def toggle_ausgeschlossener_name(vollname: str) -> bool:
    """
    Togglet einen Vollnamen in der Ausschlussliste.
    Rückgabe: True = jetzt ausgeschlossen, False = jetzt eingeschlossen.
    """
    key   = vollname.lower().strip()
    namen = get_ausgeschlossene_namen()
    if key in namen:
        namen.remove(key)
        set_ausgeschlossene_namen(namen)
        return False
    else:
        namen.append(key)
        set_ausgeschlossene_namen(namen)
        return True


def ist_ausgeschlossen(vollname: str) -> bool:
    """Prüft ob ein Vollname in der Ausschlussliste steht."""
    return vollname.lower().strip() in get_ausgeschlossene_namen()
