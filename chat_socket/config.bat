@echo off
chcp 65001 > nul
title Chat Socket Config

echo ================================================
echo Chat Socket Config - ngrok Settings
echo ================================================
echo.

:: ========================================
:: 1. Port number
:: ========================================
echo [1/4] Port number setup...
echo.
echo ================================================
echo Default port: 8765
echo (Press Enter to use default)
echo (Previous setting will NOT be preserved)
echo ================================================
echo.
set /p SERVER_PORT=Port number:
if "%SERVER_PORT%"=="" (
    set "SERVER_PORT=8765"
    echo [OK] Using default port: 8765
) else (
    echo [OK] Port: %SERVER_PORT%
)
echo.

:: ========================================
:: 2. ngrok authtoken
:: ========================================
echo [2/4] ngrok authtoken setup...
echo.
echo ================================================
echo 1. Go to https://dashboard.ngrok.com
echo 2. Copy 'Your Authtoken'
echo 3. Paste below
echo (Press Enter to skip if already configured)
echo ================================================
echo.
set /p NGROK_TOKEN=Authtoken:
if not "%NGROK_TOKEN%"=="" (
    ngrok config add-authtoken %NGROK_TOKEN%
    if errorlevel 1 (
        echo [Error] authtoken setup failed
        pause
        exit /b 1
    )
    echo [OK] authtoken configured
) else (
    echo [Skip] Keep existing config
)
echo.

:: ========================================
:: 3. Static domain (optional)
:: ========================================
echo [3/4] Static domain setup...
echo.
echo ================================================
echo Example: myapp.ngrok-free.app
echo (Press Enter to skip - will use random URL)
echo (Previous setting will NOT be preserved)
echo ================================================
echo.
set /p NGROK_DOMAIN=Static domain:
if "%NGROK_DOMAIN%"=="" (
    echo [Skip] Will use random URL
) else (
    echo [OK] Domain: %NGROK_DOMAIN%
)
echo.

:: ========================================
:: 4. Google OAuth (optional)
:: ========================================
echo [4/4] Google OAuth setup...
echo.
echo ================================================
echo Enter allowed Google email address
echo Example: user@gmail.com
echo (Press Enter to skip - public access)
echo (Previous setting will NOT be preserved)
echo ================================================
echo.
set /p OAUTH_EMAIL=Allowed email:
if "%OAUTH_EMAIL%"=="" (
    echo [Skip] Public access (no OAuth)
) else (
    echo [OK] OAuth email: %OAUTH_EMAIL%
)
echo.

:: ========================================
:: Generate run.bat
:: ========================================
echo [Info] Generating run.bat...

set "RUN_FILE=%~dp0run.bat"

> "%RUN_FILE%" echo @echo off
>> "%RUN_FILE%" echo echo ========================================
>> "%RUN_FILE%" echo echo Chat Socket Server Start
>> "%RUN_FILE%" echo echo ========================================
>> "%RUN_FILE%" echo echo.
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo REM Check aiohttp
>> "%RUN_FILE%" echo python -m pip show aiohttp ^> nul 2^>^&1
>> "%RUN_FILE%" echo if errorlevel 1 (
>> "%RUN_FILE%" echo     echo Installing aiohttp library...
>> "%RUN_FILE%" echo     python -m pip install aiohttp
>> "%RUN_FILE%" echo     echo.
>> "%RUN_FILE%" echo )
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo REM Change to parent directory for Claude CLI working directory
>> "%RUN_FILE%" echo cd /d "%%~dp0.."
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo :restart_loop
>> "%RUN_FILE%" echo echo Starting server...
>> "%RUN_FILE%" echo echo Access: http://localhost:%SERVER_PORT%
>> "%RUN_FILE%" echo echo Working directory: %%cd%%
>> "%RUN_FILE%" echo echo.
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo REM Open browser (only on first start)
>> "%RUN_FILE%" echo if not defined BROWSER_OPENED (
>> "%RUN_FILE%" echo     set BROWSER_OPENED=1
>> "%RUN_FILE%" echo     start http://localhost:%SERVER_PORT%
>> "%RUN_FILE%" echo )
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo python "chat_socket/server.py" --port %SERVER_PORT%
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo REM Exit code 100 = restart request
>> "%RUN_FILE%" echo if %%errorlevel%% == 100 (
>> "%RUN_FILE%" echo     echo.
>> "%RUN_FILE%" echo     echo ========================================
>> "%RUN_FILE%" echo     echo Restarting server... (applying changes)
>> "%RUN_FILE%" echo     echo ========================================
>> "%RUN_FILE%" echo     echo.
>> "%RUN_FILE%" echo     timeout /t 2 /nobreak ^> nul
>> "%RUN_FILE%" echo     goto restart_loop
>> "%RUN_FILE%" echo )
>> "%RUN_FILE%" echo.
>> "%RUN_FILE%" echo echo.
>> "%RUN_FILE%" echo echo Server stopped.
>> "%RUN_FILE%" echo pause

echo [OK] run.bat generated
echo.

:: ========================================
:: Generate run_ngrok.bat
:: ========================================
echo [Info] Generating run_ngrok.bat...

set "NGROK_FILE=%~dp0run_ngrok.bat"

:: Build ngrok command
set "NGROK_CMD=ngrok http %SERVER_PORT%"
set "PORT_DISPLAY=%SERVER_PORT%"
set "DOMAIN_DISPLAY=Random URL"
set "OAUTH_DISPLAY=Public"

if not "%NGROK_DOMAIN%"=="" (
    set "NGROK_CMD=%NGROK_CMD% --domain=%NGROK_DOMAIN%"
    set "DOMAIN_DISPLAY=https://%NGROK_DOMAIN%"
)

if not "%OAUTH_EMAIL%"=="" (
    set "NGROK_CMD=%NGROK_CMD% --oauth=google --oauth-allow-email=%OAUTH_EMAIL%"
    set "OAUTH_DISPLAY=%OAUTH_EMAIL%"
)

:: Write run_ngrok.bat line by line
> "%NGROK_FILE%" echo @echo off
>> "%NGROK_FILE%" echo title Chat Socket + ngrok
>> "%NGROK_FILE%" echo.
>> "%NGROK_FILE%" echo REM Store script directory before start command
>> "%NGROK_FILE%" echo set "SCRIPT_DIR=%%~dp0"
>> "%NGROK_FILE%" echo.
>> "%NGROK_FILE%" echo echo ================================================
>> "%NGROK_FILE%" echo echo Chat Socket + ngrok
>> "%NGROK_FILE%" echo echo ================================================
>> "%NGROK_FILE%" echo echo.
>> "%NGROK_FILE%" echo echo Port: %PORT_DISPLAY%
>> "%NGROK_FILE%" echo echo Domain: %DOMAIN_DISPLAY%
>> "%NGROK_FILE%" echo echo OAuth: %OAUTH_DISPLAY%
>> "%NGROK_FILE%" echo echo.
>> "%NGROK_FILE%" echo echo [1] Starting server (with restart loop)...
>> "%NGROK_FILE%" echo start "Chat Socket Server" /D "%%SCRIPT_DIR%%" cmd /k "run_server_loop.bat %SERVER_PORT%"
>> "%NGROK_FILE%" echo echo [Wait] 3 seconds...
>> "%NGROK_FILE%" echo timeout /t 3 /nobreak ^> nul
>> "%NGROK_FILE%" echo echo [2] Starting ngrok tunnel...
>> "%NGROK_FILE%" echo echo.
>> "%NGROK_FILE%" echo %NGROK_CMD%
>> "%NGROK_FILE%" echo echo.
>> "%NGROK_FILE%" echo echo ================================================
>> "%NGROK_FILE%" echo echo ngrok closed.
>> "%NGROK_FILE%" echo echo ================================================
>> "%NGROK_FILE%" echo pause

echo [OK] run_ngrok.bat generated
echo.

:: ========================================
:: Done
:: ========================================
echo ================================================
echo Configuration complete!
echo ================================================
echo.
echo Settings:
echo   Port:   %PORT_DISPLAY%
echo   Domain: %DOMAIN_DISPLAY%
echo   OAuth:  %OAUTH_DISPLAY%
echo.
echo How to run:
echo   run.bat        - Local server only
echo   run_ngrok.bat  - Server + ngrok tunnel
echo.
echo ================================================
echo.
echo Press any key to close...
pause > nul
