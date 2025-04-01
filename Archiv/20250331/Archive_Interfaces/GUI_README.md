# Waffle Production Optimizer GUI

A graphical user interface for the Waffle Production Optimization tool that allows you to configure and run optimization problems, visualize feasibility checks, and view solution results.

## Features

- **Data Upload**: Load waffle demand, pan supply, cost, waffles per pan, and allowed combinations data from Excel files
- **Feasibility Check**: Visualize feasibility checks with a network graph and detailed analysis
- **Optimization Configuration**: Select objective (minimize cost or maximize output) and set constraints
- **Solution Visualization**: View optimization results with charts and tables
- **Data Export**: Export solutions to Excel

## Installation

1. Ensure you have Python 3.8+ installed
2. Install required packages:
   ```
   pip install PyQt6 matplotlib networkx pandas
   ```
3. Clone or download this repository

## Running the Application

Start the application by running:

```
python waffle_gui.py
```

## Usage Instructions

### Configuration Tab

1. **Data Files**:
   - Use the default Excel files or browse to select your own
   - Click "Load Data" to process the files
   
2. **Model Configuration**:
   - Choose optimization objective (Minimize Cost or Maximize Output)
   - Set demand handling option
   - Select solver
   
3. **Feasibility Check**:
   - Click "Check Feasibility" to analyze if the problem is feasible
   - View supply-demand network visualization and feasibility details
   - If feasible, click "Run Optimization" to solve

### Solution Tab

The solution tab will display the results after optimization:

1. **Solution Summary**: Overview of the optimization results
2. **Production Allocation**: Chart showing production quantities
3. **Pan Utilization**: Chart showing pan usage
4. **Cost Analysis**: Cost distribution by waffle type
5. **Detailed Results**: Table with detailed assignment data

You can export the solution to Excel by clicking "Export Solution to Excel".

## File Structure

- **waffle_gui.py**: Main entry point
- **gui/**: GUI components
  - **main_window.py**: Main application window
  - **config_tab.py**: Configuration tab
  - **solution_tab.py**: Solution tab
  - **widgets/**: Custom widgets
    - **data_upload.py**: Data file upload widget
    - **feasibility_view.py**: Feasibility visualization widget
    - **solution_view.py**: Solution visualization widget
- **core/**: Core business logic
  - **data_processor.py**: Data loading and processing
  - **feasibility_check.py**: Feasibility analysis
  - **solver_interface.py**: Solver interface
  - **solver_ortools.py**: OR-Tools implementation

## Troubleshooting

- **Missing dependencies**: Make sure all required packages are installed
- **File access errors**: Ensure Excel files are not open in another application
- **GUI display issues**: Try adjusting your system's display scaling settings 