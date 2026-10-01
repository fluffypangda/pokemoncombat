@echo off
title Hisui Guide - Local Server
set ROOT=%~dp0
cd /d "%ROOT%"

echo ==================================================
echo   Pokemon Legends: Arceus - Hisui Guide
echo   One-click local server launcher
echo ==================================================
echo.

rem Check Python
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found.
  echo Please install Python 3 and check "Add Python to PATH":
  echo   https://www.python.org/downloads/
  pause
  exit /b 1
)

rem Port 8000 already running? Then just open the browser.
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>nul
if not errorlevel 1 (
  echo Server already running, opening the page...
  echo.
  start "" "http://localhost:8000/index.html"
  echo   PC:    http://localhost:8000/index.html
  python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));print('   iPad:  http://'+s.getsockname()[0]+':8000/index.html')"
  echo.
  pause
  exit /b 0
)

echo Starting server in a separate window...
start "Hisui-Guide-Server" cmd /k "cd /d ""%ROOT%"" && python serve.py 8000"
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/index.html"
echo.
echo   PC:    http://localhost:8000/index.html
echo   iPad:  open the LAN address below in Safari (same Wi-Fi):
python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));print('        http://'+s.getsockname()[0]+':8000/index.html')"
echo.
echo   The server window is titled "Hisui-Guide-Server"; closing it stops the service.
echo   Closing this window does NOT stop the server.
echo ==================================================
pause
