@echo off
REM ========================================================================
REM   RunwayML Batch Automation - Compile to EXE
REM ========================================================================

setlocal
echo.
echo ==================================================================
echo       RUNWAYML BATCH AUTOMATION - COMPILE TO EXE
echo ==================================================================
echo.

REM Check if PyInstaller is installed
echo Checking PyInstaller installation...
python -m pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install PyInstaller!
        echo Please install it manually with: pip install pyinstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully!
)

echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"

echo.
echo Starting compilation process...
echo This may take a few minutes...
echo.

REM Run PyInstaller with the spec file
pyinstaller runway_automation.spec --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==================================================================
    echo   ERROR: Compilation failed!
    echo ==================================================================
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==================================================================
echo   COMPILATION SUCCESSFUL!
echo ==================================================================
echo.
echo Executable location: dist\RunwayML_Batch_Automation.exe
echo.
echo The executable includes:
echo   - All Python dependencies
echo   - Assets folder (driver videos)
echo   - Config folder (settings)
echo.
echo You can now:
echo   1. Copy the exe to any Windows machine
echo   2. Run it without Python installed
echo   3. All settings will persist between launches
echo.
echo ==================================================================

REM Ask if user wants to test the executable
echo.
set /p TEST="Do you want to test the compiled executable now? (Y/N): "
if /i "%TEST%"=="Y" (
    echo.
    echo Starting the compiled executable...
    cd dist
    start RunwayML_Batch_Automation.exe
)

echo.
pause
endlocal