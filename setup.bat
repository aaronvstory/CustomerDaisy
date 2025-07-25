@echo off
title CustomerDaisy - Setup
chcp 65001 >nul 2>&1

REM Change to script directory
cd /d "%~dp0"

echo ========================================
echo    CustomerDaisy Setup
echo    DaisySMS Customer Creation System
echo ========================================
echo.

REM Check if UV is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] UV not found. Attempting to install...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    uv --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] UV installation failed. Please install it manually.
        pause
        exit /b 1
    )
)

echo [INFO] UV is available.
echo [INFO] Creating virtual environment and installing dependencies...
uv sync
if errorlevel 1 (
    echo [ERROR] Failed to set up project using uv sync.
    pause
    exit /b 1
)

echo.
echo [INFO] Creating required directories...
mkdir customer_data >nul 2>&1
mkdir logs >nul 2>&1
mkdir backups >nul 2>&1

echo.
echo [INFO] Testing DaisySMS connection...
python -c "from src.daisy_sms import DaisySMSManager; import configparser; config = configparser.ConfigParser(); config.read('config.ini'); manager = DaisySMSManager(dict(config.items('DAISYSMS'))); manager.test_api_connection()"

echo.
echo [OK] Setup complete! The CustomerDaisy system is ready.
echo To run the application, use the launch.bat script.
echo.
pause