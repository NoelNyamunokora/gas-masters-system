@echo off
echo ========================================
echo   Gas Masters System - Local Server
echo ========================================
echo.
echo Starting server...
echo.
echo Your PC can access at: http://localhost:5000
echo.
echo Other computers on your network can access at:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    echo http://%%a:5000
)
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python app.py
pause
