@echo off
echo ==========================================
echo    AI Football Prediction App Launcher
echo ==========================================
echo.

echo [1/2] Starting FastAPI Backend...
start "AI Football Backend" cmd /k "cd backend && call conda activate gozcu && python.exe main.py"

echo [2/2] Starting Next.js Frontend...
start "AI Football Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ------------------------------------------
echo Backend URL:  http://localhost:8000
echo Frontend URL: http://localhost:3000
echo ------------------------------------------
echo.
echo NOTE: Since Selenium is in visible mode, Chrome windows will pop up 
echo when the backend needs to scrape data from LiveScore.
echo Please do not close them while they are working.
echo.
echo Press any key to exit this launcher (servers will keep running in their windows).
pause > nul
