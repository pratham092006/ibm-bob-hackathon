@echo off
echo ========================================
echo    AXON Vercel Deployment Script
echo    Team Merge Conflicts
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed!
    echo Please install Git from: https://git-scm.com/
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Git status...
git status >nul 2>&1
if errorlevel 1 (
    echo [INFO] Initializing Git repository...
    git init
    echo       Done!
) else (
    echo       Git repository already initialized
)
echo.

echo [2/5] Adding files to Git...
git add index.html styles.css script.js vercel.json
git add LANDING_PAGE_README.md BUILD_EXECUTABLE.md VERCEL_DEPLOYMENT.md
git add README.md HOW_TO_RUN.md ARCHITECTURE.md
echo       Done!
echo.

echo [3/5] Committing changes...
git commit -m "Add landing page and Vercel deployment config"
if errorlevel 1 (
    echo       No changes to commit or already committed
) else (
    echo       Committed successfully!
)
echo.

echo [4/5] Checking remote repository...
git remote -v | findstr origin >nul
if errorlevel 1 (
    echo [INFO] Adding remote repository...
    set /p REPO_URL="Enter your GitHub repository URL: "
    git remote add origin %REPO_URL%
    echo       Remote added!
) else (
    echo       Remote already configured
)
echo.

echo [5/5] Pushing to GitHub...
echo.
echo Choose an option:
echo 1. Push to main branch
echo 2. Push to a new branch
echo 3. Skip push (manual push later)
echo.
set /p CHOICE="Enter choice (1-3): "

if "%CHOICE%"=="1" (
    echo.
    echo Pushing to main branch...
    git push -u origin main
    if errorlevel 1 (
        echo [WARNING] Push failed. You may need to pull first or force push.
        echo Try: git pull origin main --rebase
        echo Then: git push -u origin main
    ) else (
        echo       Pushed successfully!
    )
) else if "%CHOICE%"=="2" (
    set /p BRANCH="Enter branch name: "
    echo.
    echo Creating and pushing to branch: %BRANCH%
    git checkout -b %BRANCH%
    git push -u origin %BRANCH%
    echo       Pushed successfully!
) else (
    echo.
    echo Skipping push. You can push manually later with:
    echo   git push -u origin main
)

echo.
echo ========================================
echo    Next Steps
echo ========================================
echo.
echo 1. Go to https://vercel.com/dashboard
echo 2. Click "Add New..." -^> "Project"
echo 3. Import your GitHub repository
echo 4. Click "Deploy"
echo.
echo OR use Vercel CLI:
echo   npm install -g vercel
echo   vercel login
echo   vercel --prod
echo.
echo For detailed instructions, see VERCEL_DEPLOYMENT.md
echo.
echo ========================================
pause

@REM Made with Bob
