@echo off
REM Windows Batch Script to Copy Frontend Files
REM Run this from the Backend folder

echo ========================================
echo  Copying Frontend Files for Admin Portal
echo ========================================
echo.

REM Set source and destination directories
set SOURCE=%~dp0frontend_files
set DEST=%~dp0..\Frontend\src\views

echo Source: %SOURCE%
echo Destination: %DEST%
echo.

REM Copy AdminView files
echo [1/3] Copying AdminView.jsx...
copy /Y "%SOURCE%\AdminView.jsx" "%DEST%\AdminView.jsx"
if %ERRORLEVEL% EQU 0 (
    echo ✓ AdminView.jsx copied successfully
) else (
    echo ✗ Failed to copy AdminView.jsx
)
echo.

echo [2/3] Copying AdminView.css...
copy /Y "%SOURCE%\AdminView.css" "%DEST%\AdminView.css"
if %ERRORLEVEL% EQU 0 (
    echo ✓ AdminView.css copied successfully
) else (
    echo ✗ Failed to copy AdminView.css
)
echo.

echo [3/3] Copying HomeView.jsx...
copy /Y "%SOURCE%\HomeView.jsx" "%DEST%\HomeView.jsx"
if %ERRORLEVEL% EQU 0 (
    echo ✓ HomeView.jsx copied successfully
) else (
    echo ✗ Failed to copy HomeView.jsx
)
echo.

echo ========================================
echo  Copy Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update Frontend/.env with: VITE_API_URL=http://localhost:5000
echo 2. Make sure App.jsx has the /admin route
echo 3. Create an admin user in your database
echo 4. Run the backend: python flask_app.py
echo 5. Run the frontend: npm run dev
echo.
echo See FRONTEND_UPDATE_STEPS.md for detailed instructions
echo.
pause
