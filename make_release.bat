@echo off
setlocal enabledelayedexpansion

:: Error trap - ensure pause on any exit
if "%~1"=="__MAIN__" goto :main
cmd /c "%~f0" __MAIN__ %*
pause
exit /b

:main

:: make_release.bat version
set SCRIPT_VERSION=1.3

echo ========================================
echo   Chat Socket Release Package Builder
echo   (script v%SCRIPT_VERSION%)
echo ========================================
echo.

:: Get version from git tag
for /f "tokens=*" %%i in ('git describe --tags --abbrev^=0 2^>nul') do set GIT_TAG=%%i

:: Use default if no tag found
if not defined GIT_TAG (
    echo [WARN] No git tag found.
    set VERSION=0.0.0
) else (
    set VERSION=!GIT_TAG:v=!
    echo [OK] Git tag: !GIT_TAG!
)

:: Output folder settings
set RELEASE_DIR=release
set ZIP_NAME=chat_socket_v%VERSION%.zip

:: Create release folder
if not exist %RELEASE_DIR% mkdir %RELEASE_DIR%

:: Delete existing ZIP file
if exist %RELEASE_DIR%\%ZIP_NAME% del %RELEASE_DIR%\%ZIP_NAME%

:: Create temp folder
set TEMP_DIR=%RELEASE_DIR%\temp_chat_socket
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%
mkdir %TEMP_DIR%

echo.
echo [WORK] Copying chat_socket files...

:: Copy core files
copy chat_socket\server.py %TEMP_DIR%\ >nul
copy chat_socket\index.html %TEMP_DIR%\ >nul
copy chat_socket\service-worker.js %TEMP_DIR%\ >nul
copy chat_socket\manifest.json %TEMP_DIR%\ >nul
copy chat_socket\requirements.txt %TEMP_DIR%\ >nul

:: Copy run scripts
copy chat_socket\install.bat %TEMP_DIR%\ >nul
copy chat_socket\config.bat %TEMP_DIR%\ >nul
copy chat_socket\run.bat %TEMP_DIR%\ >nul
copy chat_socket\run_server_loop.bat %TEMP_DIR%\ >nul

:: Copy README
if exist chat_socket\README.md (
    copy chat_socket\README.md %TEMP_DIR%\ >nul
) else (
    copy README.md %TEMP_DIR%\ >nul
)

:: Copy docs folder
mkdir %TEMP_DIR%\docs
xcopy chat_socket\docs\*.* %TEMP_DIR%\docs\ /s /q >nul

:: Copy icons folder
mkdir %TEMP_DIR%\icons
xcopy chat_socket\icons\*.* %TEMP_DIR%\icons\ /s /q >nul

:: Delete excluded files
if exist %TEMP_DIR%\nul del %TEMP_DIR%\nul 2>nul
if exist %TEMP_DIR%\icons\generate_icons.py del %TEMP_DIR%\icons\generate_icons.py 2>nul

echo [OK] Files copied.

:: Create ZIP file
echo.
echo [WORK] Creating ZIP file...
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%RELEASE_DIR%\%ZIP_NAME%' -Force"

:: Delete temp folder
rmdir /s /q %TEMP_DIR%

:: Check result
if exist %RELEASE_DIR%\%ZIP_NAME% (
    echo [OK] ZIP file created.
    echo.
    echo ========================================
    echo   Release Package Complete!
    echo ========================================
    echo.
    echo   File: %RELEASE_DIR%\%ZIP_NAME%
    echo   Version: v%VERSION%
    for %%A in (%RELEASE_DIR%\%ZIP_NAME%) do set SIZE=%%~zA
    set /a SIZE_KB=!SIZE!/1024
    echo   Size: !SIZE_KB! KB
    echo.
    echo   v%VERSION% released successfully!
    echo.
) else (
    echo [ERROR] ZIP file creation failed.
    echo.
    exit /b 1
)

:: ========================================
:: GitHub Release Upload
:: ========================================
echo.
set /p UPLOAD="Upload to GitHub release? (y/n): "
if /i "!UPLOAD!" neq "y" (
    echo [SKIP] GitHub upload skipped.
    echo.
    exit /b 0
)

:: Check gh CLI
where gh >nul 2>nul
if errorlevel 1 (
    echo [ERROR] GitHub CLI (gh) not found.
    echo         Install: winget install GitHub.cli
    echo.
    exit /b 1
)

:: Check gh auth status
gh auth status >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Not logged in to GitHub CLI.
    echo         Run: gh auth login
    echo.
    exit /b 1
)

echo.
echo [INFO] Target version: v%VERSION%

:: Create local tag if not exists
git tag -l v%VERSION% | findstr /c:"v%VERSION%" >nul 2>nul
if errorlevel 1 (
    echo [WORK] Creating local tag v%VERSION%...
    git tag v%VERSION%
    if errorlevel 1 (
        echo [ERROR] Failed to create tag.
        exit /b 1
    )
)

:: Push tag to remote
echo [WORK] Pushing tag to remote...
git push origin v%VERSION% 2>nul
if errorlevel 1 (
    echo [INFO] Tag already exists on remote or push failed, continuing...
)

:: Check if release exists and handle accordingly
echo [WORK] Checking existing release...
gh release view v%VERSION% >nul 2>nul
if errorlevel 1 (
    echo [INFO] No existing release found. Creating new release...
) else (
    echo [INFO] Release v%VERSION% already exists.
    set /p OVERWRITE="Delete and recreate? (y/n): "
    if /i "!OVERWRITE!" neq "y" (
        echo [SKIP] Upload cancelled.
        exit /b 0
    )
    echo [WORK] Deleting existing release...
    gh release delete v%VERSION% --yes
    if errorlevel 1 (
        echo [ERROR] Failed to delete existing release.
        exit /b 1
    )
    echo [OK] Existing release deleted.
)

:: Create new release with ZIP file
echo [WORK] Creating GitHub release v%VERSION%...
gh release create v%VERSION% "%RELEASE_DIR%\%ZIP_NAME%" --title "Chat Socket v%VERSION%" --generate-notes
if errorlevel 1 (
    echo [ERROR] Failed to create release.
    exit /b 1
)

echo.
echo ========================================
echo   GitHub Release Complete!
echo ========================================
echo.
echo   Version: v%VERSION%
echo.
for /f "tokens=*" %%u in ('gh release view v%VERSION% --json url -q .url 2^>nul') do echo   URL: %%u
echo.
