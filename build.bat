@echo off
title Build ARIS DockGlass
color 0A

echo ========================================================
echo             Building ARIS DockGlass (.exe)
echo ========================================================
echo.

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Compiling application with PyInstaller...
pyinstaller --noconsole --onefile --name "ARIS-DockGlass" --clean main.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo                 Build Successful!
echo ========================================================
echo.
echo Standalone executable is ready at:
echo dist\ARIS-DockGlass.exe
echo.
echo You can run 'Install.bat' to install it to your system.
pause
