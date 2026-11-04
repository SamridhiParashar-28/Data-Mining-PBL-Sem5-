@echo off
setlocal enabledelayedexpansion

title Employee Performance ^& Prediction Pipeline - Server

echo =====================================================================
echo    EMPLOYEE PERFORMANCE ^& PREDICTION PIPELINE (Data Mining PBL)
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
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [*] Found %%i

:: 2. Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [*] Creating Python virtual environment in .\venv ...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [WARNING] venv creation failed. Using system Python...
        goto :install_global
    )
    echo [*] Virtual environment created.
    call venv\Scripts\activate.bat
    goto :install_deps
) else (
    echo [*] Activating existing virtual environment...
    call venv\Scripts\activate.bat
)

:install_deps
echo [*] Installing/verifying dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have issues. Continuing...
)
goto :start

:install_global
echo [*] Installing dependencies to system Python...
python -m pip install --quiet -r requirements.txt

:start
echo.
echo =====================================================================
echo [*] Starting FastAPI + Uvicorn on http://127.0.0.1:8000
echo [*] FIRST STARTUP: Please wait 15-25 seconds while the ML pipeline
echo [*]                trains models on the synthetic HR dataset.
echo [*] The browser will open automatically once the server is ready.
echo [*] Press Ctrl+C to stop.
echo =====================================================================
echo.

:: 3. Create a small Python health-checker script that opens browser when ready
echo import urllib.request, time, subprocess, sys > "%TEMP%\wait_and_open.py"
echo url = "http://127.0.0.1:8000/" >> "%TEMP%\wait_and_open.py"
echo print("[Launcher] Waiting for server to become ready...") >> "%TEMP%\wait_and_open.py"
echo for i in range(60): >> "%TEMP%\wait_and_open.py"
echo     try: >> "%TEMP%\wait_and_open.py"
echo         urllib.request.urlopen(url, timeout=2) >> "%TEMP%\wait_and_open.py"
echo         print(f"[Launcher] Server ready after {i*3}s! Opening browser...") >> "%TEMP%\wait_and_open.py"
echo         import webbrowser >> "%TEMP%\wait_and_open.py"
echo         webbrowser.open(url) >> "%TEMP%\wait_and_open.py"
echo         sys.exit(0) >> "%TEMP%\wait_and_open.py"
echo     except: >> "%TEMP%\wait_and_open.py"
echo         time.sleep(3) >> "%TEMP%\wait_and_open.py"
echo print("[Launcher] Timeout: server did not respond in 3 minutes.") >> "%TEMP%\wait_and_open.py"

:: 4. Launch the health-checker as a background process
start /min "Browser Launcher" python "%TEMP%\wait_and_open.py"

:: 5. Run the FastAPI server in the foreground (keeps console open)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
