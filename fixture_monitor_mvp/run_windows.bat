@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python was not found.
        echo Run setup_windows.bat first or configure Python in PyCharm.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=python"
)

echo Starting Smart Fixture Monitoring System...
echo Missing dependencies will be installed automatically into:
echo %PYTHON_EXE%
echo.
"%PYTHON_EXE%" start.py
if errorlevel 1 (
    echo.
    echo The application exited with an error.
    echo You can also run setup_windows.bat to rebuild the local environment.
    pause
    exit /b 1
)

exit /b 0
