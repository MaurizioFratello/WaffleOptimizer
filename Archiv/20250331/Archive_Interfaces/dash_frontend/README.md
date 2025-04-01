# Waffle Optimizer Dash Frontend

A web-based frontend for the Waffle Production Optimization tool using Dash by Plotly.

## Overview

This is a minimum working example (MWE) that demonstrates how to create a web-based interface for the Waffle Optimizer using Dash. The frontend allows you to:

- Upload data files or use sample data
- Check feasibility
- Configure and run optimization
- View results with interactive charts
- Export results to Excel

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Start the application by running:
```
python app.py
```

This will launch the Dash server at http://127.0.0.1:8050/

## Structure

- `app.py`: Main Dash application with all the components and callbacks
- `requirements.txt`: Package requirements
- `README.md`: This documentation file

## Usage

1. **Data Upload Tab**: 
   - Load data using the sample files (currently uses the files from the parent directory)
   - In a full implementation, you could upload your own files

2. **Configuration Tab**:
   - Check feasibility of the optimization problem
   - Choose optimization objective (minimize cost or maximize output)
   - Set time limit and other parameters
   - Run the optimization

3. **Results Tab**:
   - View summary metrics and interactive charts
   - Explore detailed results in a table
   - Export solution to Excel

## Notes

This is a demonstration version with some simplified functionality:
- For demonstration purposes, the sample data is loaded from the parent directory
- Some visualizations show placeholder/mock data
- Full implementation would include proper state management between callbacks

## Integration with Existing Codebase

This implementation interfaces with the existing Waffle Optimizer codebase without modifying it, demonstrating how you can add a web interface to your existing tool. 