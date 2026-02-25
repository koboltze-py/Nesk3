"""Prüft und setzt das Admin-Passwort in der Datenbank zurück."""
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
DB = BASE / "database" / "nesk.db"

print(f"Datenbank: {DB}")
if not DB.exists():
    print("FEHLER: Datenbank nicht gefunden!")
    sys.exit(1)

con = sqlite3.connect(str(DB))
con.row_factory = sqlite3.Row

rows = con.execute("SELECT id, username, password_hash, role FROM users").fetchall()
print(f"\nAktuell {len(rows)} Benutzer in der DB:")
for r in rows:
    h = r['password_hash']
    print(f"  id={r['id']}  username={r['username']}  role={r['role']}  hash={h[:30]}...")

# Passwort "drk2026" mit werkzeug hashen und neu setzen
from werkzeug.security import generate_password_hash, check_password_hash

new_hash = generate_password_hash("drk2026")
print(f"\nNeuer Hash für 'drk2026': {new_hash[:30]}...")

# Prüfen ob admin existiert
admin = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
if admin:
    con.execute("UPDATE users SET password_hash=? WHERE username='admin'", (new_hash,))
    print("Admin-Passwort auf 'drk2026' zurückgesetzt.")
else:
    con.execute(
        "INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?,?,?,?,?)",
        ("admin", new_hash, "Administrator", "admin", "2026-02-25T00:00:00+00:00")
    )
    print("Admin-Benutzer neu angelegt.")

con.commit()

# Verifikation
check = con.execute("SELECT password_hash FROM users WHERE username='admin'").fetchone()
ok = check_password_hash(check['password_hash'], "drk2026")
print(f"\nVerifikation Login admin/drk2026: {'OK ✓' if ok else 'FEHLER ✗'}")
con.close()
