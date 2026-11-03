@echo off
setlocal enabledelayedexpansion

title Employee Performance & Prediction Pipeline - Server

echo =====================================================================
echo    EMPLOYEE PERFORMANCE & PREDICTION PIPELINE (Data Mining PBL)
echo =====================================================================
echo.

:: 1. Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and add it to your PATH.
    pause
    exit /b 1
)

:: 2. Create virtual environment if it does not exist
if not exist "venv\Scripts\activate.bat" (
    echo [*] Creating Python virtual environment in .\venv ...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [*] Virtual environment created successfully.
)

:: 3. Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: 4. Install / Update dependencies
echo [*] Checking and installing dependencies from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies encountered an issue. Continuing to launch...
)

:: 5. Launch browser after a brief 2-second background timer
start /b cmd /c "timeout /t 2 >nul & start http://localhost:8000"

:: 6. Start FastAPI server with Uvicorn
echo.
echo =====================================================================
echo [*] Server starting on http://localhost:8000
echo [*] Press Ctrl+C in this console to stop the server.
echo =====================================================================
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause

