@echo off
setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

REM Check if first argument is "gui"
if "%1"=="gui" (
    echo [INFO] Starting Streamlit GUI...
    streamlit run "%ROOT_DIR%gui.py" ^
        --server.port 8501 ^
        --server.address 0.0.0.0 ^
        --browser.serverAddress localhost ^
        --browser.serverPort 8501
) else (
    echo [INFO] Using CLI entrypoint...
    python "%ROOT_DIR%main.py" %*
)

endlocal
