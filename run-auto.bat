@echo off
REM AIPut Windows Auto Start Script
REM This script detects virtual environment and starts the program

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo AIPut Windows Launcher
echo ========================================
echo.

REM Check virtual environment
if not exist "aiput-env\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo.
    echo Please run the following commands first:
    echo.
    echo CMD:
    echo   python -m venv aiput-env
    echo   aiput-env\Scripts\activate
    echo   pip install flask pyautogui pyperclip qrcode pillow pystray aiohttp python-dotenv
    echo.
    echo PowerShell:
    echo   python -m venv aiput-env
    echo   .\aiput-env\Scripts\Activate.ps1
    echo   pip install flask pyautogui pyperclip qrcode pillow pystray aiohttp python-dotenv
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call aiput-env\Scripts\activate.bat

REM Check if Python file exists
if not exist "src\remote_server.py" (
    echo Error: Cannot find src\remote_server.py
    pause
    exit /b 1
)

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Run program
echo ========================================
echo Starting AIPut (Windows)...
echo Default port: 37856
echo ========================================
echo.

REM Run main program
python src\remote_server.py

REM If program exits with error, pause to view error message
if errorlevel 1 (
    echo.
    echo Program exited abnormally, press any key to close...
    pause >nul
)
