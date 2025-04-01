#!/bin/bash
# Run the Waffle Optimizer Dash Frontend

# Ensure we're in the dash_frontend directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Remove any existing virtual environment if it has issues
if [ -d "venv" ]; then
    if ! python3 -c "import dash" &> /dev/null; then
        echo "Issues with existing environment, recreating..."
        rm -rf venv
    fi
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Update core packages first - critical for Python 3.12
    pip install --upgrade pip
    pip install --upgrade setuptools wheel
    
    # Install packages one by one to better handle dependencies
    echo "Installing dependencies..."
    pip install numpy
    pip install pandas
    pip install matplotlib
    pip install networkx
    pip install plotly
    pip install dash
    pip install dash-bootstrap-components
    pip install ortools
else
    source venv/bin/activate
fi

# Verify dash is installed
if ! python3 -c "import dash" &> /dev/null; then
    echo "Error: Dash installation failed. Please try manually:"
    echo "cd $(pwd)"
    echo "python3 -m pip install dash dash-bootstrap-components"
    exit 1
fi

# Run the application
echo "Starting Dash application..."
python app.py 