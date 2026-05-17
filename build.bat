@echo off
echo ========================================
echo    AXON Executable Builder
echo    Team Merge Conflicts
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed!
    echo Please run: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo [1/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AXON.spec del AXON.spec
echo       Done!
echo.

echo [2/5] Checking dependencies...
python -c "import PyQt6, google.generativeai, PIL, pyautogui" 2>nul
if errorlevel 1 (
    echo [WARNING] Some dependencies might be missing!
    echo Please run: pip install -r requirements.txt
    echo.
)
echo       Done!
echo.

echo [3/5] Building AXON executable...
echo       This may take 2-5 minutes...
echo.

pyinstaller --name="AXON" ^
  --onefile ^
  --windowed ^
  --add-data="core;core" ^
  --add-data="executor;executor" ^
  --add-data="ui;ui" ^
  --add-data=".env.example;." ^
  --hidden-import=PyQt6 ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=google.generativeai ^
  --hidden-import=anthropic ^
  --hidden-import=PIL ^
  --hidden-import=pytesseract ^
  --hidden-import=pyautogui ^
  --hidden-import=keyboard ^
  --hidden-import=mss ^
  --exclude-module=matplotlib ^
  --exclude-module=scipy ^
  --exclude-module=pandas ^
  main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo [4/5] Verifying build...
if exist "dist\AXON.exe" (
    echo       Executable created successfully!
    for %%A in ("dist\AXON.exe") do echo       Size: %%~zA bytes
) else (
    echo [ERROR] Executable not found!
    pause
    exit /b 1
)
echo.

echo [5/5] Creating release package...
if not exist "AXON-Release" mkdir AXON-Release
copy "dist\AXON.exe" "AXON-Release\" >nul
copy "README.md" "AXON-Release\" >nul
copy "HOW_TO_RUN.md" "AXON-Release\" >nul
copy "BUILD_EXECUTABLE.md" "AXON-Release\" >nul
copy ".env.example" "AXON-Release\" >nul
if exist "LICENSE" copy "LICENSE" "AXON-Release\" >nul

REM Create quick start guide
echo AXON - Quick Start Guide > "AXON-Release\QUICK_START.txt"
echo ======================== >> "AXON-Release\QUICK_START.txt"
echo. >> "AXON-Release\QUICK_START.txt"
echo 1. Double-click AXON.exe to start >> "AXON-Release\QUICK_START.txt"
echo 2. Configure your API key in .env.example (rename to .env) >> "AXON-Release\QUICK_START.txt"
echo 3. Press Alt+G to open task dialog >> "AXON-Release\QUICK_START.txt"
echo 4. Press F12 for emergency stop >> "AXON-Release\QUICK_START.txt"
echo. >> "AXON-Release\QUICK_START.txt"
echo For detailed instructions, see HOW_TO_RUN.md >> "AXON-Release\QUICK_START.txt"
echo. >> "AXON-Release\QUICK_START.txt"
echo Built with IBM Bob - Team Merge Conflicts >> "AXON-Release\QUICK_START.txt"

echo       Release package created in AXON-Release\
echo.

echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Executable location: dist\AXON.exe
echo Release package: AXON-Release\
echo.
echo Next steps:
echo 1. Test the executable: dist\AXON.exe
echo 2. Distribute: AXON-Release\ folder
echo 3. Create ZIP: Right-click AXON-Release ^> Send to ^> Compressed folder
echo.
echo ========================================
pause

@REM Made with Bob
