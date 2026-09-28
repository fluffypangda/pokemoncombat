@echo off
chcp 65001 >nul
title 宝可梦传说 阿尔宙斯 · 洗翠攻略
set ROOT=%~dp0
cd /d "%ROOT%"

echo ==================================================
echo        宝可梦传说 阿尔宙斯 · 洗翠攻略
echo            一键启动本地服务器
echo ==================================================
echo.

rem 检查 Python
where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 未检测到 Python。
  echo 请先安装 Python 3 并勾选 "Add Python to PATH"：
  echo   https://www.python.org/downloads/
  pause
  exit /b 1
)

rem 检查 8000 端口是否已被占用（已在运行则直接开浏览器）
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>nul
if not errorlevel 1 (
  echo 检测到服务器已在运行，直接打开页面...
  echo.
  start "" "http://localhost:8000/index.html"
  echo  本机:  http://localhost:8000/index.html
  python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));print('  iPad:  http://'+s.getsockname()[0]+':8000/index.html')"
  echo.
  pause
  exit /b 0
)

echo 正在启动服务器（独立窗口）...
start "攻略服务器" cmd /k "cd /d ""%ROOT%"" && python -m http.server 8000 --bind 0.0.0.0"
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/index.html"
echo.
echo  本机:  http://localhost:8000/index.html
echo  iPad 同一 WiFi 下用 Safari 打开局域网地址:
python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));print('        http://'+s.getsockname()[0]+':8000/index.html')"
echo.
echo  提示: 服务器窗口标题为「攻略服务器」，关闭它即停止服务。
echo  关闭本窗口不影响服务器继续运行。
echo ==================================================
pause
