@echo off
echo Port Risk Assessment Analysis Tool
echo ==================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies. Please check your Python installation.
    pause
    exit /b 1
)

echo.
echo Step 2: Processing data and generating insights...
python generate_insights.py
if %errorlevel% neq 0 (
    echo Error processing data. Please check if questionario.xlsx exists.
    pause
    exit /b 1
)

echo.
echo Step 3: Starting web dashboard...
echo The dashboard will open at http://localhost:8050
echo Press Ctrl+C to stop the server.
echo.
python app.py

pause
