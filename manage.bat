@echo off
REM ============================================================================
REM OpenTalent Windows Management Script
REM ============================================================================

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "LOG_DIR=%SCRIPT_DIR%logs"
set "PID_FILE=%SCRIPT_DIR%.opentalent.pids.txt"
set "VENV_PATH=%SCRIPT_DIR%.venv"

REM Create log directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Command router
if "%1"=="" goto usage
if /i "%1"=="start" goto start
if /i "%1"=="stop" goto stop
if /i "%1"=="status" goto status
if /i "%1"=="restart" goto restart
goto usage

:start
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         OpenTalent - Starting Production Environment       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [*] Starting services...
echo.
echo Please use './manage.sh start' on Windows Subsystem for Linux
echo or run this from Git Bash for full functionality.
echo.
echo Alternative: Use start-demo.sh or manually start services:
echo   1. cd desktop-app ^&^& npm run dev
echo   2. cd services/desktop-integration-service ^&^& python app/main.py
echo.
goto end

:stop
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         OpenTalent - Stopping Services                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [*] Stopping Node.js processes...
taskkill /F /IM node.exe /T 2>nul
echo [*] Stopping Python processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM python3.exe /T 2>nul
echo.
echo [√] All services stopped
goto end

:status
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         OpenTalent - Service Status                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Checking active processes...
echo.
tasklist /FI "IMAGENAME eq node.exe" 2>nul | find "node.exe" >nul
if %ERRORLEVEL%==0 (
    echo [√] Node.js processes: RUNNING
) else (
    echo [X] Node.js processes: STOPPED
)
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if %ERRORLEVEL%==0 (
    echo [√] Python processes: RUNNING
) else (
    echo [X] Python processes: STOPPED
)
echo.
goto end

:restart
call :stop
timeout /t 3 /nobreak >nul
call :start
goto end

:usage
echo.
echo OpenTalent Management Script
echo.
echo Usage: manage.bat {start^|stop^|restart^|status}
echo.
echo Commands:
echo   start    - Start all OpenTalent services
echo   stop     - Stop all services
echo   restart  - Restart all services
echo   status   - Check service status
echo.
echo Note: For full functionality on Windows, use Git Bash or WSL
echo.
goto end

:end
endlocal
