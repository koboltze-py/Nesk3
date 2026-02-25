@echo off
title WebNesk – DRK Flughafen Köln
color 0C

echo.
echo  ======================================================
echo   WebNesk – DRK Erste-Hilfe-Station Flughafen Koeln
echo  ======================================================
echo.

:: Ins Projektverzeichnis wechseln (Bat liegt im Projektordner)
cd /d "%~dp0"

:: Prüfen ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden!
    echo  Bitte Python von https://python.org installieren.
    echo.
    pause
    exit /b 1
)

:: Pakete installieren falls nötig
echo  Abhängigkeiten prüfen...
pip install -r requirements.txt --quiet --no-warn-script-location

:: Starten
echo  Server wird gestartet...
echo  Browser öffnet sich automatisch...
echo.
echo  Zum Beenden: dieses Fenster schließen oder Strg+C drücken
echo.

:: Browser nach 2 Sekunden öffnen (im Hintergrund)
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Flask starten (blockiert bis Fenster geschlossen wird)
python run.py

echo.
echo  Server wurde beendet.
pause
