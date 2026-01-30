@echo off
title Claude Code Remote Access Installer

echo ========================================
echo   Claude Code Remote Access Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Python is already installed.
    python --version
    echo.
    echo Starting installer...
    python "%~dp0installer.py"
    echo.
    pause
    goto :eof
)

echo [!] Python is not installed.
echo.
echo The following will be done:
echo   - Install Python 3.12 via winget
echo   - Add Python to PATH automatically
echo.
choice /c YN /m "Install Python? (Y=Yes, N=No)"
if errorlevel 2 goto :cancel
if errorlevel 1 goto :install

:install
echo.
echo Installing Python. Please wait...
winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
echo.
echo [OK] Installation complete.
echo.
echo Starting installer in new terminal...
start cmd /c "cd /d %~dp0 && python installer.py && pause"
goto :eof

:cancel
echo.
echo Installation cancelled.
pause
goto :eof
