@echo off
chcp 65001 >nul 2>&1

echo ========================================
echo  Questionary Arrow-Key Interface Test
echo ========================================
echo.

:: Find Python executable (same logic as launch.bat)
set "SCRIPT_DIR=%~dp0"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"

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

echo.
echo Testing questionary arrow-key navigation...
echo This will show you if the arrow-key menu will work.
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%main.py" --test-questionary

echo.
echo ========================================
echo Test completed. Now try launching the main application.
echo If the test worked, you should see arrow-key navigation.
echo If not, the application will use numbered menus instead.
echo ========================================
echo.
pause