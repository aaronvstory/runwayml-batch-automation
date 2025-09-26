@echo off
echo ==================================================================
echo     FINAL COMPILATION - RunwayML Batch Automation v2.0.1
echo ==================================================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

REM Check if icon exists
if not exist "assets\runway_icon.ico" (
    echo ERROR: Icon file not found at assets\runway_icon.ico
    pause
    exit /b 1
)

REM Compile with icon
echo Starting final compilation with custom icon...
echo.

pyinstaller --noconfirm ^
    --onefile ^
    --console ^
    --name="RunwayML_Batch_Automation" ^
    --icon="assets\runway_icon.ico" ^
    --add-data="assets;assets" ^
    --add-data="config;config" ^
    --hidden-import=tkinter ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=selenium ^
    --hidden-import=selenium.webdriver ^
    src\runway_automation_ui.py

echo.
if exist "dist\RunwayML_Batch_Automation.exe" (
    echo ==================================================================
    echo   COMPILATION SUCCESSFUL!
    echo ==================================================================
    echo.

    REM Show exe details
    echo Executable details:
    cmd /c dir dist\*.exe | findstr exe

    REM Kill any running instances
    taskkill /F /IM RunwayML_Batch_Automation.exe 2>nul

    REM Copy to distribution
    echo.
    echo Copying to distribution folder...
    copy /Y "dist\RunwayML_Batch_Automation.exe" "distribution\RunwayML_Batch_Automation.exe"

    echo.
    echo ✓ Executable compiled and copied to distribution
    echo ✓ Custom icon embedded
    echo.
) else (
    echo ==================================================================
    echo   COMPILATION FAILED!
    echo ==================================================================
)

pause