@echo off
setlocal enabledelayedexpansion

REM RunwayML Batch Automation - Direct Python Launcher
REM This batch file launches the Python script directly (independent from .exe)

REM Set console properties for better display
title RunwayML Batch Automation
REM Note: mode command might fail on some systems, ignore errors
mode con cols=92 lines=40 2>nul

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ===============================================================================
    echo                           ERROR: Python Not Found
    echo ===============================================================================
    echo.
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.8 or later from https://www.python.org/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Clear screen for clean start
cls

REM Display startup banner
echo ===============================================================================
echo.
echo                   ╦═╗╦ ╦╔╗╔╦ ╦╔═╗╦ ╦╔╦╗╦     ╔╗ ╔═╗╔╦╗╔═╗╦ ╦
echo                   ╠╦╝║ ║║║║║║║╠═╣╚╦╝║║║║     ╠╩╗╠═╣ ║ ║  ╠═╣
echo                   ╩╚═╚═╝╝╚╝╚╩╝╩ ╩ ╩ ╩ ╩╩═╝   ╚═╝╩ ╩ ╩ ╚═╝╩ ╩
echo.
echo ===============================================================================
echo.
echo Starting RunwayML Batch Automation from Python source...
echo.

REM Check if src directory exists
if not exist "src\runway_automation_ui.py" (
    echo ERROR: Cannot find src\runway_automation_ui.py
    echo Please ensure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)

REM Check and install required packages if needed
echo Checking required packages...
python -c "import rich" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing rich library...
    pip install rich --quiet
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests library...
    pip install requests --quiet
)

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Pillow library...
    pip install Pillow --quiet
)

REM Clear screen before launching main application
cls

REM Launch the Python application with error capture
python "src\runway_automation_ui.py" 2>&1
set EXITCODE=%errorlevel%

REM Check if the script exited with an error
if %EXITCODE% neq 0 (
    echo.
    echo ===============================================================================
    echo APPLICATION ERROR - Exit Code: %EXITCODE%
    echo ===============================================================================
    echo.
    echo Check the logs\runway_automation.log file for details.
    echo Common issues:
    echo   - Missing API key in configuration
    echo   - Driver video not found
    echo   - Python import errors
    echo.
    echo Press any key to exit...
    pause >nul
)

endlocal