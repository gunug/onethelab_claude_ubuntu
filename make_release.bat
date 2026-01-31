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

:: Create temp folder with chat_socket subfolder
set TEMP_DIR=%RELEASE_DIR%\temp_release
set TARGET_DIR=%TEMP_DIR%\chat_socket
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%
mkdir %TARGET_DIR%

echo.
echo [WORK] Copying chat_socket files...

:: Copy core files
copy chat_socket\server.py %TARGET_DIR%\ >nul
copy chat_socket\index.html %TARGET_DIR%\ >nul
copy chat_socket\service-worker.js %TARGET_DIR%\ >nul
copy chat_socket\manifest.json %TARGET_DIR%\ >nul
copy chat_socket\requirements.txt %TARGET_DIR%\ >nul

:: Copy run scripts
copy chat_socket\install.bat %TARGET_DIR%\ >nul
copy chat_socket\config.bat %TARGET_DIR%\ >nul
copy chat_socket\run.bat %TARGET_DIR%\ >nul
copy chat_socket\run_server_loop.bat %TARGET_DIR%\ >nul

:: Copy README
if exist chat_socket\README.md (
    copy chat_socket\README.md %TARGET_DIR%\ >nul
) else (
    copy README.md %TARGET_DIR%\ >nul
)

:: Copy docs folder
mkdir %TARGET_DIR%\docs
xcopy chat_socket\docs\*.* %TARGET_DIR%\docs\ /s /q >nul

:: Copy icons folder
mkdir %TARGET_DIR%\icons
xcopy chat_socket\icons\*.* %TARGET_DIR%\icons\ /s /q >nul

:: Delete excluded files
if exist %TARGET_DIR%\nul del %TARGET_DIR%\nul 2>nul
if exist %TARGET_DIR%\icons\generate_icons.py del %TARGET_DIR%\icons\generate_icons.py 2>nul

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
    echo.
) else (
    echo [ERROR] ZIP file creation failed.
    echo.
    exit /b 1
)

:: ========================================
:: GitHub Release Guide
:: ========================================
echo ----------------------------------------
echo   To upload to GitHub:
echo ----------------------------------------
echo.
echo   1. Commit and push changes:
echo      git add . ^&^& git commit -m "v%VERSION% release"
echo      git push origin master
echo.
echo   2. Create and push tag:
echo      git tag v%VERSION%
echo      git push origin v%VERSION%
echo.
echo   3. Create GitHub release:
echo      gh release create v%VERSION% "%RELEASE_DIR%\%ZIP_NAME%" --title "Chat Socket v%VERSION%" --generate-notes
echo.
echo ----------------------------------------
echo.
