@echo off
chcp 65001 > nul
echo Starting WebGL Tea Consumer Simulation System...

REM Switch to current directory
cd /d %~dp0

REM Set WebSocket mode and output encoding
set WEB_MODE=True
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

REM Install required libraries
echo Checking required libraries...
pip install python-dotenv websockets -q

REM Start WebGL service
echo Starting simulation system...
python start_webgl_server.py

pause 