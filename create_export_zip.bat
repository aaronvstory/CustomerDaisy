@echo off
title CustomerDaisy - Create Export ZIP
chcp 65001 >nul 2>&1

echo ========================================
echo   CustomerDaisy Export Packager
echo ========================================
echo.

set "EXPORT_DIR=export"
set "ZIP_NAME=CustomerDaisy_CLI_Export_%date:~10,4%%date:~4,2%%date:~7,2%.zip"

if not exist "%EXPORT_DIR%" (
    echo [ERROR] Export directory not found. Please ensure 'export' folder exists.
    pause
    exit /b 1
)

echo [INFO] Creating ZIP package: %ZIP_NAME%
echo [INFO] This may take a moment...
echo.

powershell -Command "Compress-Archive -Path '%EXPORT_DIR%\*' -DestinationPath '%ZIP_NAME%' -CompressionLevel Optimal -Force"

if exist "%ZIP_NAME%" (
    echo [SUCCESS] Export package created: %ZIP_NAME%
    echo.
    echo This ZIP file contains everything needed to run CustomerDaisy CLI
    echo on any Windows PC. Simply extract and run setup.bat.
    echo.
    echo Package contents:
    echo - Complete CLI application
    echo - Pre-configured API keys
    echo - Automated setup scripts
    echo - Sample database
    echo - Full documentation
) else (
    echo [ERROR] Failed to create ZIP package.
    echo Please ensure PowerShell is available and try again.
)

echo.
pause