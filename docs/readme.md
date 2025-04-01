# Waffle Production Optimizer

A Python tool for optimizing waffle production planning using open-source optimization solvers.

## Overview

This tool helps optimize waffle production by solving two key questions:

1. How to minimize overall production cost while meeting waffle demand
2. How to maximize waffle output for a given production schedule

The implementation uses a modular design with support for multiple optimization solvers, including PuLP (with various backends like CBC, GLPK) and Google OR-Tools.

## Features

- **Data Processing**: Load and validate input data from Excel files
- **Feasibility Checking**: Identify potential issues before optimization
- **Multiple Optimization Objectives**: Minimize cost or maximize output
- **Multiple Solvers**: Support for various optimization backends
- **Reporting**: Export detailed results to Excel for further analysis
- **Validation**: Verify solution feasibility and quality

## Requirements

- Python 3.7+
- Required packages (listed in requirements.txt):
  - numpy
  - pandas
  - openpyxl
  - pulp
  - matplotlib
  - ortools

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Project Structure

```
waffle_optimizer/
├── src/
│   ├── solvers/           # Solver implementations
│   │   ├── base.py        # Abstract base class and factory
│   │   ├── pulp_solver.py # PuLP-based solvers (CBC, GLPK, etc.)
│   │   └── ortools_solver.py  # Google OR-Tools implementation
│   ├── data/              # Data handling
│   │   ├── processor.py   # Data loading and processing
│   │   └── validator.py   # Data validation
│   └── utils/             # Utilities
│       └── results_reporter.py  # Results reporting and export
├── tests/                 # Test cases
├── benchmarks/            # Benchmarking tools and results
├── data/                  # Data files
│   ├── input/             # Input Excel files
│   └── output/            # Solution output files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── .gitignore             # Git ignore file
├── requirements.txt       # Python dependencies
└── main.py                # Main entry point
```

## Data Format

The optimizer requires five Excel files:

1. **WaffleDemand.xlsx**: Weekly demand for each waffle type (in pans)
2. **PanSupply.xlsx**: Weekly supply of each pan type
3. **WaffleCostPerPan.xlsx**: Cost per waffle for each waffle-pan combination
4. **WafflesPerPan.xlsx**: Number of waffles that can be produced in each pan type
5. **WafflePanCombinations.xlsx**: Allowed combinations of waffle types and pan types

## Usage

### Command Line

Run the main script with arguments to control the optimization:

```bash
python main.py --objective cost --solver cbc --time-limit 60 --output data/output/solution.xlsx
```

Available arguments:
- `--objective`: Choose between `cost` (minimize cost) or `output` (maximize output)
- `--solver`: Solver to use (`cbc`, `glpk`, `pulp_highs`, `ortools`, etc.)
- `--time-limit`: Time limit for optimization in seconds
- `--gap`: Optimality gap tolerance
- `--debug`: Enable debug output
- Data file paths can be specified with `--demand`, `--supply`, `--cost`, `--wpp`, `--combinations`

### Programmatic Usage

You can use the optimizer programmatically in your own scripts:

```python
from src.data.processor import DataProcessor
from src.data.validator import DataValidator
from src.solvers.base import SolverFactory
from src.utils.results_reporter import ResultsReporter

# Create data processor and load data
data_processor = DataProcessor()
data_processor.load_data(
    demand_file="data/input/WaffleDemand.xlsx",
    supply_file="data/input/PanSupply.xlsx",
    cost_file="data/input/WaffleCostPerPan.xlsx",
    wpp_file="data/input/WafflesPerPan.xlsx",
    combinations_file="data/input/WafflePanCombinations.xlsx"
)
optimization_data = data_processor.get_optimization_data()

# Check feasibility
validator = DataValidator()
is_feasible, issues = validator.check_basic_feasibility(optimization_data)

# Create and run solver
solver = SolverFactory.create_solver("cbc", time_limit=60, optimality_gap=0.005)
solver.build_minimize_cost_model(optimization_data)
solution_info = solver.solve_model()
solution = solver.get_solution()

# Report and export results
reporter = ResultsReporter()
reporter.print_summary(solution)
reporter.export_to_excel(optimization_data, solution, "data/output/solution.xlsx")
```

## Extending with Additional Solvers

The modular design makes it easy to add support for additional optimization solvers:

1. Create a new solver implementation that inherits from `SolverInterface` in `src/solvers/base.py`
2. Implement the required methods:
   - `build_minimize_cost_model`
   - `build_maximize_output_model`
   - `solve_model`
   - `get_solution`
3. Add the new solver to the `SolverFactory` in `src/solvers/base.py`

## Mathematical Formulation

### Decision Variables
- $X_{wpt}$: Number of pans of type $p$ used to cook waffle type $w$ in week $t$

### Objective Functions
1. **Minimize Cost**: $\min \sum_{w,p,t} C_{wp} \cdot N_w \cdot X_{wpt}$
2. **Maximize Output**: $\max \sum_{w,p,t} N_w \cdot X_{wpt}$

Where:
- $C_{wp}$ is the cost per waffle for waffle type $w$ and pan type $p$
- $N_w$ is the number of waffles per pan for waffle type $w$

### Constraints
1. Demand satisfaction: For each waffle type $w$ and week $t$, the number of pans used must meet or exceed demand.
2. Supply limitation: For each pan type $p$ and week $t$, the number of pans used cannot exceed supply.
3. Compatibility: Waffle type $w$ can only be cooked in pan type $p$ if allowed.
4. Non-negativity and integrality: $X_{wpt} \geq 0$ and integer.

## License

This project is open-source and available under the MIT License. 