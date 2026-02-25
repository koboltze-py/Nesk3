# ============================================================
#  Nesk3 – Start-Script
#  Auf dem SERVER-PC: startet PostgreSQL + App
#  Auf CLIENT-PCs:   startet nur die App (verbindet zum Server)
# ============================================================

$PG_DIR   = "$env:USERPROFILE\nesk_postgres"
$PG_DATA  = "$env:USERPROFILE\nesk_postgres\data"
$PG_BIN   = "$PG_DIR\bin"
$PY       = "C:/Users/DRKairport/AppData/Local/Microsoft/WindowsApps/python3.13.exe"

# OneDrive-Pfad (automatisch vom eingeloggten Nutzer)
$OD = $env:OneDriveCommercial
if (-not $OD) { $OD = $env:OneDrive }
$APP_DIR = Join-Path $OD "Dateien von Erste-Hilfe-Station-Flughafen - DRK Köln e.V_ - !Gemeinsam.26\Nesk\Nesk3"

# ── Ist dies der Server-PC? (portable PG vorhanden?) ─────────────────────────
$istServer = Test-Path "$PG_BIN\pg_ctl.exe"

if ($istServer) {
    # Prüfen ob PostgreSQL schon läuft
    $pgLaeuft = & "$PG_BIN\pg_ctl.exe" -D $PG_DATA status 2>&1
    if ($pgLaeuft -notlike "*server is running*") {
        Write-Host "Starte PostgreSQL..." -ForegroundColor Yellow
        & "$PG_BIN\pg_ctl.exe" -D $PG_DATA -l "$PG_DATA\postgresql.log" start
        # Warten bis PostgreSQL bereit ist (max 15 Sekunden)
        $versuch = 0
        do {
            Start-Sleep -Seconds 1
            $versuch++
            $bereit = & "$PG_BIN\pg_isready.exe" -p 5432 2>&1
        } while ($bereit -notlike "*accepting connections*" -and $versuch -lt 15)

        if ($versuch -ge 15) {
            Write-Host "FEHLER: PostgreSQL konnte nicht gestartet werden!" -ForegroundColor Red
            Write-Host "Log: $PG_DATA\postgresql.log" -ForegroundColor Yellow
            Pause
            exit 1
        }
        Write-Host "[OK] PostgreSQL läuft." -ForegroundColor Green
    } else {
        Write-Host "[OK] PostgreSQL läuft bereits." -ForegroundColor Green
    }
}

# ── App starten ───────────────────────────────────────────────────────────────
if (-not (Test-Path $APP_DIR)) {
    Write-Host "FEHLER: App-Verzeichnis nicht gefunden:" -ForegroundColor Red
    Write-Host $APP_DIR -ForegroundColor Yellow
    Write-Host "OneDrive muss synchronisiert sein." -ForegroundColor Yellow
    Pause
    exit 1
}

Set-Location $APP_DIR
Write-Host "Starte Nesk3..." -ForegroundColor Cyan
& $PY main.py

# ── Nach App-Ende: PostgreSQL stoppen (nur auf Server-PC) ────────────────────
if ($istServer) {
    Write-Host "Stoppe PostgreSQL..." -ForegroundColor Yellow
    & "$PG_BIN\pg_ctl.exe" -D $PG_DATA stop
    Write-Host "[OK] PostgreSQL gestoppt." -ForegroundColor Green
}
