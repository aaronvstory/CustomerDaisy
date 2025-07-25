@echo off
chcp 65001 >nul 2>&1

:: Simple variable setup
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%main.py"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "DATA_DIR=%SCRIPT_DIR%customer_data"

:: Change to script directory
cd /d "%SCRIPT_DIR%"

echo ========================================
echo  CustomerDaisy - Customer Creation System
echo ========================================
echo.

:: Create required directories
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%" >nul 2>&1
if not exist "logs" mkdir "logs" >nul 2>&1
if not exist "backups" mkdir "backups" >nul 2>&1

:: Check UV and sync dependencies first
echo [INFO] Checking dependencies...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] UV not found. Please run setup.bat first.
    pause
) else (
    echo [INFO] Syncing dependencies with UV...
    uv sync --quiet
    if errorlevel 1 (
        echo [WARNING] Failed to sync dependencies. Some features may not work.
    ) else (
        echo [INFO] Dependencies synchronized successfully.
    )
)

:: Find Python executable
set "PYTHON_EXE="
if exist "%VENV_PYTHON%" (
    set "PYTHON_EXE=%VENV_PYTHON%"
    echo [INFO] Using virtual environment python.
) else (
    for %%P in (py python) do (
        if not defined PYTHON_EXE (
            %%P --version >nul 2>&1
            if %errorlevel% equ 0 (
                set "PYTHON_EXE=%%P"
                echo [INFO] Using system python: %%P
            )
        )
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python not found. Please run setup.bat first.
    pause
    exit /b 1
)

:: Launch application
echo [INFO] Launching CustomerDaisy...
echo ========================================
echo.

"%PYTHON_EXE%" "%PYTHON_SCRIPT%" %*
set "EXIT_CODE=%errorlevel%"

echo.
echo ========================================
if %EXIT_CODE% equ 0 (
    echo      APPLICATION COMPLETED
) else (
    echo      APPLICATION ERROR (Code: %EXIT_CODE%)
)
echo ========================================
echo.
pause
exit /b %EXIT_CODE%