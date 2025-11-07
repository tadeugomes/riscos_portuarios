@echo off
echo Setting up Virtual Environment for Port Risk Assessment
echo =====================================================

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error creating virtual environment. Please check Python installation.
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Error activating virtual environment.
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing project dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies.
    pause
    exit /b 1
)

echo.
echo Virtual environment setup complete!
echo.
echo To activate the environment in the future, run:
echo   venv\Scripts\activate
echo.
echo To run the data preview:
echo   python show_data_head.py
echo.
echo To start the dashboard:
echo   python app.py
echo.
echo Press any key to run the data preview now...
pause > nul

python show_data_head.py

pause
