# Waffle Production Optimizer

A Python tool for optimizing waffle production planning using open-source optimization solvers.

## Overview

This tool helps optimize waffle production by solving two key questions:

1. How to minimize overall production cost while meeting waffle demand
2. How to maximize waffle output for a given production schedule

The implementation uses a modular design with support for multiple optimization solvers, starting with Google OR-Tools.

## Features

- **Data Processing**: Load and validate input data from Excel files
- **Feasibility Checking**: Identify potential issues before optimization
- **Multiple Optimization Objectives**: Minimize cost or maximize output
- **Interactive Interface**: Easy parameter adjustment and solver selection
- **Visualization**: Generate plots of production plans and resource usage
- **Reporting**: Export detailed results to Excel for further analysis

## Requirements

- Python 3.7+
- Required packages:
  - pandas
  - numpy
  - matplotlib
  - ortools

You can install the required packages using pip:

```bash
pip install pandas numpy matplotlib ortools
```

## Data Format

The optimizer requires five Excel files:

1. **WaffleDemand.xlsx**: Weekly demand for each waffle type (in pans)
2. **PanSupply.xlsx**: Weekly supply of each pan type
3. **WaffleCostPerPan.xlsx**: Cost per waffle for each waffle-pan combination
4. **WafflesPerPan.xlsx**: Number of waffles that can be produced in each pan type
5. **WafflePanCombinations.xlsx**: Allowed combinations of waffle types and pan types

## Usage

### Interactive Mode

Run the main script to start the interactive interface:

```bash
python main.py
```

The interface will guide you through:
1. Loading data files
2. Checking feasibility
3. Selecting optimization objectives and solvers
4. Visualizing results
5. Exporting solutions

### Programmatic Usage

You can also use the optimizer programmatically in your own scripts:

```python
from main import WaffleOptimizer

# Initialize the optimizer
optimizer = WaffleOptimizer()

# Load data
optimizer.load_data(
    demand_file="WaffleDemand.xlsx",
    supply_file="PanSupply.xlsx",
    cost_file="WaffleCostPerPan.xlsx",
    wpp_file="WafflesPerPan.xlsx",
    combinations_file="WafflePanCombinations.xlsx"
)

# Check feasibility
feasibility_result = optimizer.check_feasibility()

# Optimize for minimum cost
result = optimizer.optimize(objective="minimize_cost", solver_name="ortools")

# Visualize results
optimizer.visualize_results()

# Export solution
optimizer.export_solution("waffle_solution.xlsx")
```

See `example_script.py` for a more detailed example.

## Project Structure

```
waffle_optimizer/
├── __init__.py
├── data_processor.py      # Loading and validating data
├── model_formulator.py    # Creating optimization models
├── solver_interface.py    # Common interface for solvers
├── solver_ortools.py      # OR-Tools implementation
├── feasibility_check.py   # Checking data feasibility
├── results_reporter.py    # Visualizing and reporting results
└── main.py                # Main interactive interface
```

## Extending with Additional Solvers

The modular design makes it easy to add support for additional optimization solvers:

1. Create a new solver implementation that inherits from `SolverInterface`
2. Implement the required methods:
   - `build_minimize_cost_model`
   - `build_maximize_output_model`
   - `solve_model`
   - `get_solution`
3. Add the new solver to the `SolverFactory` in `solver_interface.py`

## Mathematical Formulation

### Decision Variables
- $X_{wpt}$: Number of pans of type $p$ used to cook waffle type $w$ in week $t$

### Objective Functions
1. **Minimize Cost**: $\min \sum_{w,p,t} C_{wp} \cdot N_p \cdot X_{wpt}$
2. **Maximize Output**: $\max \sum_{w,p,t} N_p \cdot X_{wpt}$

Where:
- $C_{wp}$ is the cost per waffle for waffle type $w$ and pan type $p$
- $N_p$ is the number of waffles per pan for pan type $p$

### Constraints
1. Demand satisfaction: For each waffle type $w$ and week $t$, the number of pans used must meet or exceed demand.
2. Supply limitation: For each pan type $p$ and week $t$, the number of pans used cannot exceed supply.
3. Compatibility: Waffle type $w$ can only be cooked in pan type $p$ if allowed.
4. Non-negativity and integrality: $X_{wpt} \geq 0$ and integer.

## License

This project is open-source and available under the MIT License.
