@echo off
title Disconnect Equipment Bot
cd /d "%~dp0"
call .venv\Scripts\activate
start http://127.0.0.1:5000
python server.py
pause