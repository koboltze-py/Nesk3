# ============================================================
#  Nesk3 – Portables PostgreSQL: EINMALIGE EINRICHTUNG
#  Nur einmal auf dem Server-PC ausführen!
# ============================================================
#  Voraussetzung: PostgreSQL ZIP-Archiv von
#  https://www.enterprisedb.com/download-postgresql-binaries
#  herunterladen und nach %USERPROFILE%\nesk_postgres entpacken,
#  sodass %USERPROFILE%\nesk_postgres\bin\initdb.exe existiert.
#  KEIN ADMIN ERFORDERLICH!
# ============================================================

$PG_DIR     = "$env:USERPROFILE\nesk_postgres"              # Kein Admin nötig!
$PG_DATA    = "$env:USERPROFILE\nesk_postgres\data"         # Daten im Benutzerprofil
$PG_PORT    = 5432
$PG_USER    = "nesk3user"
$PG_PASS    = "nesk3pass"
$PG_DBNAME  = "nesk3"
$PG_BIN     = "$PG_DIR\bin"

# ── Pfad prüfen ──────────────────────────────────────────────────────────────
if (-not (Test-Path "$PG_BIN\initdb.exe")) {
    Write-Host ""
    Write-Host "FEHLER: initdb.exe nicht gefunden unter $PG_BIN" -ForegroundColor Red
    Write-Host "Bitte PostgreSQL ZIP entpacken nach: $PG_DIR" -ForegroundColor Yellow
    Write-Host "(d.h. es muss existieren: $PG_BIN\initdb.exe)" -ForegroundColor Yellow
    Write-Host "Download: https://www.enterprisedb.com/download-postgresql-binaries" -ForegroundColor Cyan
    Write-Host ""
    Pause
    exit 1
}

Write-Host ""
Write-Host "=== Nesk3 PostgreSQL Einrichtung ===" -ForegroundColor Cyan
Write-Host ""

# ── Data-Verzeichnis initialisieren ──────────────────────────────────────────
if (Test-Path "$PG_DATA\PG_VERSION") {
    Write-Host "[OK] Datenbank-Verzeichnis existiert bereits: $PG_DATA" -ForegroundColor Green
} else {
    Write-Host "Initialisiere Datenbank-Verzeichnis..." -ForegroundColor Yellow
    & "$PG_BIN\initdb.exe" -D $PG_DATA -U postgres -E UTF8 --locale=German_Germany.1252
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FEHLER bei initdb!" -ForegroundColor Red
        Pause
        exit 1
    }
    Write-Host "[OK] Datenbank initialisiert." -ForegroundColor Green
}

# ── Netzwerkzugriff konfigurieren (für alle 3 PCs im LAN) ───────────────────
$pgConf = "$PG_DATA\postgresql.conf"
(Get-Content $pgConf) -replace "#listen_addresses = 'localhost'", "listen_addresses = '*'" |
    Set-Content $pgConf
(Get-Content $pgConf) -replace "listen_addresses = 'localhost'", "listen_addresses = '*'" |
    Set-Content $pgConf

# pg_hba.conf – LAN-Zugriff erlauben
$hbaConf = "$PG_DATA\pg_hba.conf"
$hbaEintrag = "host    all             all             0.0.0.0/0               scram-sha-256"
if (-not (Select-String -Path $hbaConf -Pattern "0.0.0.0/0" -Quiet)) {
    Add-Content $hbaConf "`n$hbaEintrag"
    Write-Host "[OK] LAN-Zugriff in pg_hba.conf eingetragen." -ForegroundColor Green
}

# ── PostgreSQL starten ────────────────────────────────────────────────────────
Write-Host "Starte PostgreSQL..." -ForegroundColor Yellow
& "$PG_BIN\pg_ctl.exe" -D $PG_DATA -l "$PG_DATA\postgresql.log" start
Start-Sleep -Seconds 3

# ── Benutzer + Datenbank anlegen ──────────────────────────────────────────────
$env:PGPASSWORD = ""  # postgres hat noch kein Passwort nach initdb
Write-Host "Lege Benutzer '$PG_USER' und Datenbank '$PG_DBNAME' an..." -ForegroundColor Yellow

$sqlBenutzer = "CREATE USER $PG_USER WITH PASSWORD '$PG_PASS';"
$sqlDatenbank = "CREATE DATABASE $PG_DBNAME OWNER $PG_USER;"
$sqlRechte = "GRANT ALL PRIVILEGES ON DATABASE $PG_DBNAME TO $PG_USER;"

& "$PG_BIN\psql.exe" -U postgres -p $PG_PORT -c $sqlBenutzer 2>$null
& "$PG_BIN\psql.exe" -U postgres -p $PG_PORT -c $sqlDatenbank 2>$null
& "$PG_BIN\psql.exe" -U postgres -p $PG_PORT -c $sqlRechte 2>$null

Write-Host "[OK] Benutzer und Datenbank angelegt." -ForegroundColor Green

# ── PostgreSQL stoppen ────────────────────────────────────────────────────────
& "$PG_BIN\pg_ctl.exe" -D $PG_DATA stop
Write-Host ""
Write-Host "=== Einrichtung abgeschlossen! ===" -ForegroundColor Green
Write-Host "Starte die App ab jetzt immer über: start_nesk.ps1" -ForegroundColor Cyan
Write-Host ""

# IP-Adresse anzeigen
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" } | Select-Object -First 1).IPAddress
Write-Host "Server-IP für andere PCs: $ip" -ForegroundColor Yellow
Write-Host "In config.py eintragen: PG_HOST = `"$ip`"" -ForegroundColor Yellow
Write-Host ""
Pause
