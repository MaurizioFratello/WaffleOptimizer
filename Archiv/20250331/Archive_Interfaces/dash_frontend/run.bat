@echo off
REM Run the Waffle Optimizer Dash Frontend

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python could not be found. Please install Python.
    exit /b 1
)

REM Remove any existing virtual environment if it has issues
if exist venv (
    venv\Scripts\python -c "import dash" > nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Issues with existing environment, recreating...
        rmdir /s /q venv
    )
)

REM Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    
    REM Update core packages first - critical for Python 3.12
    python -m pip install --upgrade pip
    pip install --upgrade setuptools wheel
    
    REM Install packages one by one to better handle dependencies
    echo Installing dependencies...
    pip install numpy
    pip install pandas
    pip install matplotlib
    pip install networkx
    pip install plotly
    pip install dash
    pip install dash-bootstrap-components
    pip install ortools
) else (
    call venv\Scripts\activate
)

REM Verify dash is installed
python -c "import dash" > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Dash installation failed. Please try manually:
    echo cd %CD%
    echo python -m pip install dash dash-bootstrap-components
    exit /b 1
)

REM Run the application
echo Starting Dash application...
python app.py 