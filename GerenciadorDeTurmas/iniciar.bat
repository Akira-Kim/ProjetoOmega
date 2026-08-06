@echo off
cd /d "%~dp0"
pythonw main.py
if errorlevel 1 pause