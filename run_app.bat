@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==========================================
echo    AI Football Prediction - Launcher
echo ==========================================
echo.

rem ── 1. MongoDB ──────────────────────────────────────────────
echo [1/3] MongoDB yoxlanilir...
for /f "tokens=3" %%s in ('sc query MongoDB ^| findstr /C:"STATE"') do set MONGO_STATE=%%s
if /i "!MONGO_STATE!"=="RUNNING" (
    echo      MongoDB artiq isleyir.
) else (
    echo      MongoDB dayandir, basladilir...
    net start MongoDB >nul 2>&1
    timeout /t 4 /nobreak >nul
)

rem ── 2. Backend ──────────────────────────────────────────────
echo [2/3] FastAPI backend basladilir  (http://localhost:7999)...
if not exist "backend\venv\Scripts\python.exe" (
    echo      XATA: backend\venv yoxdur. Yuradis:
    echo             python -m venv backend\venv
    echo             backend\venv\Scripts\pip install -r backend\requirements.txt
    goto :fail
)
start "AI Football Backend" cmd /k "cd /d "%~dp0backend" && venv\Scripts\python.exe main.py"

rem ── Gogun uzerinde saglamlik yoxlamasi ──────────────────────
timeout /t 6 /nobreak >nul
echo      backend sorusu...
powershell -NoProfile -Command ^
  "try { $r = Invoke-RestMethod 'http://localhost:7999/api/health' -TimeoutSec 8; Write-Host ('      ' + $r.status + ' - ' + $r.message) } catch { Write-Host '      backend hele hazir deyil (normal, 5-10 saniyе davam eder)' }"

rem ── 3. Frontend ─────────────────────────────────────────────
echo [3/3] Next.js frontend basladilir  (http://localhost:3000)...
if not exist "frontend\node_modules" (
    echo      node_modules yoxdur. `npm install` calisdirilir...
    pushd frontend
    call npm.cmd install
    popd
)
start "AI Football Frontend" cmd /k "cd /d "%~dp0frontend" && npm.cmd run dev"

echo.
echo ------------------------------------------
echo  Frontend : http://localhost:3000     ^<-- BU LINKI AC
echo  Backend  : http://localhost:7999
echo  API docs : http://localhost:7999/docs
echo ------------------------------------------
echo.
echo  NOT: Selenium vizual rejimdadir - scraping zamaninda
echo  Chrome pencereleri acila bilər, qapatmayin.
echo.
echo  Bu pəncərəni ba��a bilərsiniz, serverlər öz pəncərələrində çalışmaqda davam edir.
echo.
pause > nul
exit /b 0

:fail
echo.
echo  Başlatma dayandırıldı - yuxarıdakı xataya baxın.
pause > nul
exit /b 1
