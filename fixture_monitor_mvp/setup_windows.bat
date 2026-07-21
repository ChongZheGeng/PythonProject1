@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found in PATH.
    echo Please install Python 3.10 or 3.11, or configure the interpreter in PyCharm.
    pause
    exit /b 1
)

echo [2/3] Creating local virtual environment...
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Existing .venv detected; reusing it.
)

echo [3/3] Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo Setup completed successfully.
echo Run run_windows.bat to start the application.
pause
exit /b 0

:fail
echo.
echo Dependency installation failed. Check the network and Python installation.
pause
exit /b 1
