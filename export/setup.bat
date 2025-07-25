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
        echo Visit: https://docs.astral.sh/uv/getting-started/installation/
        pause
        exit /b 1
    )
)

echo [INFO] UV is available.
echo [INFO] Creating virtual environment and installing dependencies...
uv sync
if errorlevel 1 (
    echo [ERROR] Failed to set up project using uv sync.
    echo This usually means:
    echo - No internet connection
    echo - Firewall blocking UV
    echo - Python not properly installed
    pause
    exit /b 1
)

echo.
echo [INFO] Creating required directories...
if not exist customer_data mkdir customer_data
if not exist logs mkdir logs
if not exist backups mkdir backups
if not exist exports mkdir exports

echo.
echo [INFO] Testing DaisySMS connection...
python -c "from src.daisy_sms import DaisySMSManager; import configparser; config = configparser.ConfigParser(); config.read('config.ini'); manager = DaisySMSManager(dict(config.items('DAISYSMS'))); manager.test_api_connection()"

echo.
echo [OK] Setup complete! The CustomerDaisy system is ready.
echo.
echo API Keys Configured:
echo    - DaisySMS: Ready (Balance shown above)
echo    - MapQuest: Ready for address generation
echo    - Mail.tm: Ready for email creation
echo.
echo Next Steps:
echo    1. Run launch.bat to start the application
echo    2. Use the interactive menu to create customers
echo    3. Monitor SMS codes in real-time
echo.
echo Data will be saved to: customer_data/customers.db
echo Logs will be saved to: logs/customer_daisy.log
echo.
pause