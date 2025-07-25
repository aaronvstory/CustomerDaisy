@echo off
title CustomerDaisy CLI - Create Distribution ZIP
chcp 65001 >nul 2>&1

echo ========================================
echo   CustomerDaisy CLI Export Packager
echo   Production-Ready Distribution
echo ========================================
echo.

set "CURRENT_DIR=%cd%"
set "PARENT_DIR=%cd%\.."
set "ZIP_NAME=CustomerDaisy_CLI_Production_%date:~10,4%%date:~4,2%%date:~7,2%.zip"

echo [INFO] Creating production ZIP package: %ZIP_NAME%
echo [INFO] This package contains everything needed for immediate deployment
echo.

cd /d "%PARENT_DIR%"

powershell -Command "Compress-Archive -Path 'export\*' -DestinationPath '%ZIP_NAME%' -CompressionLevel Optimal -Force"

if exist "%ZIP_NAME%" (
    echo [SUCCESS] Production package created: %ZIP_NAME%
    echo.
    echo 🎉 PRODUCTION-READY DISTRIBUTION
    echo ═══════════════════════════════════════
    echo ✅ Complete CLI application
    echo ✅ Pre-configured API keys (DaisySMS, MapQuest)
    echo ✅ 21 sample customer records  
    echo ✅ Automated setup/launch scripts
    echo ✅ Production notes and documentation
    echo ✅ All dependencies managed by UV
    echo.
    echo 🚀 DEPLOYMENT INSTRUCTIONS:
    echo 1. Extract ZIP on target Windows PC
    echo 2. Run setup.bat (installs dependencies)
    echo 3. Run launch.bat (starts application)
    echo 4. Done! Ready for immediate use
    echo.
    echo 📊 Package includes %date% %time%
    echo.
    echo File location: %PARENT_DIR%\%ZIP_NAME%
) else (
    echo [ERROR] Failed to create ZIP package.
    echo Please ensure PowerShell is available and try again.
)

echo.
pause
cd /d "%CURRENT_DIR%"