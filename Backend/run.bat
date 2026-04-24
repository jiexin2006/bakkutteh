@echo off
REM Windows batch file to run AI Financial Intelligence Advisor

echo Checking Python installation...
python --version >nul 2>&1

if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

echo Starting AI Financial Intelligence Advisor...
python main.py

if errorlevel 1 (
    echo Error occurred while running the application
    pause
)
