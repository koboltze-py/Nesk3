"""
Übergabe-Protokoll – Datenbankfunktionen
CRUD-Operationen für Übergabeprotokolle (Tagdienst / Nachtdienst)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_cursor


# ── Erstellen ──────────────────────────────────────────────────────────────────

def erstelle_protokoll(
    datum:            str,
    schicht_typ:      str,   # 'tagdienst' | 'nachtdienst'
    beginn_zeit:      str  = "",
    ende_zeit:        str  = "",
    patienten_anzahl: int  = 0,
    personal:         str  = "",
    ereignisse:       str  = "",
    massnahmen:       str  = "",
    uebergabe_notiz:  str  = "",
    ersteller:        str  = "",
) -> int:
    """
    Legt ein neues Übergabeprotokoll an.
    Gibt die neue ID zurück.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO uebergabe_protokolle
                (datum, schicht_typ, beginn_zeit, ende_zeit,
                 patienten_anzahl, personal, ereignisse, massnahmen,
                 uebergabe_notiz, ersteller)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datum, schicht_typ, beginn_zeit, ende_zeit,
              patienten_anzahl, personal, ereignisse, massnahmen,
              uebergabe_notiz, ersteller))
        return cur.lastrowid


# ── Aktualisieren ──────────────────────────────────────────────────────────────

def aktualisiere_protokoll(
    protokoll_id:     int,
    beginn_zeit:      str  = "",
    ende_zeit:        str  = "",
    patienten_anzahl: int  = 0,
    personal:         str  = "",
    ereignisse:       str  = "",
    massnahmen:       str  = "",
    uebergabe_notiz:  str  = "",
    ersteller:        str  = "",
    abzeichner:       str  = "",
    status:           str  = "offen",
) -> bool:
    """Aktualisiert ein vorhandenes Protokoll. Gibt True bei Erfolg zurück."""
    with db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE uebergabe_protokolle
            SET beginn_zeit      = ?,
                ende_zeit        = ?,
                patienten_anzahl = ?,
                personal         = ?,
                ereignisse       = ?,
                massnahmen       = ?,
                uebergabe_notiz  = ?,
                ersteller        = ?,
                abzeichner       = ?,
                status           = ?
            WHERE id = ?
        """, (beginn_zeit, ende_zeit, patienten_anzahl, personal,
              ereignisse, massnahmen, uebergabe_notiz,
              ersteller, abzeichner, status, protokoll_id))
        return cur.rowcount > 0


# ── Laden ──────────────────────────────────────────────────────────────────────

def lade_protokolle(
    schicht_typ: str | None = None,
    limit:       int        = 60,
) -> list[dict]:
    """
    Gibt eine Liste von Protokollen zurück, neueste zuerst.
    Optional nach schicht_typ ('tagdienst' / 'nachtdienst') filtern.
    """
    with db_cursor() as cur:
        if schicht_typ:
            cur.execute("""
                SELECT * FROM uebergabe_protokolle
                WHERE schicht_typ = ?
                ORDER BY datum DESC, erstellt_am DESC
                LIMIT ?
            """, (schicht_typ, limit))
        else:
            cur.execute("""
                SELECT * FROM uebergabe_protokolle
                ORDER BY datum DESC, erstellt_am DESC
                LIMIT ?
            """, (limit,))
        return cur.fetchall() or []


def lade_protokoll_by_id(protokoll_id: int) -> dict | None:
    """Gibt ein einzelnes Protokoll anhand der ID zurück."""
    with db_cursor() as cur:
        cur.execute(
            "SELECT * FROM uebergabe_protokolle WHERE id = ?",
            (protokoll_id,)
        )
        return cur.fetchone()


# ── Löschen ───────────────────────────────────────────────────────────────────

def loesche_protokoll(protokoll_id: int) -> bool:
    """Löscht ein Protokoll dauerhaft. Gibt True bei Erfolg zurück."""
    with db_cursor(commit=True) as cur:
        cur.execute(
            "DELETE FROM uebergabe_protokolle WHERE id = ?",
            (protokoll_id,)
        )
        return cur.rowcount > 0


# ── Abschließen ───────────────────────────────────────────────────────────────

def schliesse_protokoll_ab(protokoll_id: int, abzeichner: str) -> bool:
    """Setzt Status auf 'abgeschlossen' und trägt den Abzeichner ein."""
    with db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE uebergabe_protokolle
            SET status = 'abgeschlossen', abzeichner = ?
            WHERE id = ?
        """, (abzeichner, protokoll_id))
        return cur.rowcount > 0


# ── Statistik ─────────────────────────────────────────────────────────────────

def protokoll_statistik() -> dict:
    """Gibt eine Übersicht über alle gespeicherten Protokolle zurück."""
    with db_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*)                                        AS gesamt,
                SUM(CASE WHEN schicht_typ='tagdienst'   THEN 1 ELSE 0 END) AS tag_ges,
                SUM(CASE WHEN schicht_typ='nachtdienst' THEN 1 ELSE 0 END) AS nacht_ges,
                SUM(CASE WHEN status='offen'           THEN 1 ELSE 0 END) AS offen,
                SUM(CASE WHEN status='abgeschlossen'   THEN 1 ELSE 0 END) AS abgeschlossen,
                SUM(COALESCE(patienten_anzahl, 0))              AS patienten_gesamt
            FROM uebergabe_protokolle
        """)
        return cur.fetchone() or {}
