@echo off
setlocal enabledelayedexpansion
title ARIS DockGlass Installer
color 0B

echo ========================================================
echo               ARIS DockGlass - Windows Installer
echo ========================================================
echo.
echo Installing ARIS DockGlass to your system...
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\ARIS-DockGlass"
set "EXE_NAME=ARIS-DockGlass.exe"
set "SOURCE_EXE=%~dp0dist\%EXE_NAME%"

if not exist "%SOURCE_EXE%" (
    if exist "%~dp0%EXE_NAME%" (
        set "SOURCE_EXE=%~dp0%EXE_NAME%"
    ) else (
        echo [ERROR] %EXE_NAME% not found!
        echo Please ensure %EXE_NAME% is in the same folder or in the dist/ folder.
        pause
        exit /b 1
    )
)

echo [1/4] Creating installation directory at:
echo       %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo.
echo [2/4] Copying application files...
copy /Y "%SOURCE_EXE%" "%INSTALL_DIR%\%EXE_NAME%" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy %EXE_NAME%. Make sure the app is not already running.
    pause
    exit /b 1
)

echo.
echo [3/4] Creating Start Menu and Desktop shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'ARIS DockGlass.lnk')); " ^
    "$s.TargetPath = '%INSTALL_DIR%\%EXE_NAME%'; " ^
    "$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
    "$s.Description = 'ARIS DockGlass - Transparent Taskbar and macOS-Style Dock'; " ^
    "$s.Save(); " ^
    "$startMenu = [System.IO.Path]::Combine([Environment]::GetFolderPath('StartMenu'), 'Programs'); " ^
    "$s2 = $ws.CreateShortcut([System.IO.Path]::Combine($startMenu, 'ARIS DockGlass.lnk')); " ^
    "$s2.TargetPath = '%INSTALL_DIR%\%EXE_NAME%'; " ^
    "$s2.WorkingDirectory = '%INSTALL_DIR%'; " ^
    "$s2.Description = 'ARIS DockGlass'; " ^
    "$s2.Save();"

echo.
echo [4/4] Creating Uninstaller...
(
echo @echo off
echo echo Uninstalling ARIS DockGlass...
echo taskkill /f /im %EXE_NAME% 2^>nul
echo timeout /t 1 ^>nul
echo del /f /q "%%USERPROFILE%%\Desktop\ARIS DockGlass.lnk" 2^>nul
echo del /f /q "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\ARIS DockGlass.lnk" 2^>nul
echo rmdir /s /q "%INSTALL_DIR%" 2^>nul
echo.
echo ARIS DockGlass has been successfully uninstalled.
echo pause
) > "%INSTALL_DIR%\Uninstall.bat"

echo.
echo ========================================================
echo        Installation Completed Successfully!
echo ========================================================
echo.
echo Desktop shortcut created: 'ARIS DockGlass'
echo Start menu shortcut added.
echo.
set /p LAUNCH="Do you want to launch ARIS DockGlass now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%INSTALL_DIR%\%EXE_NAME%"
)

echo.
echo Thank you for using ARIS DockGlass!
pause
