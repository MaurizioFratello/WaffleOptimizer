# Project structure:
# waffle_optimizer/
# ├── __init__.py
# ├── data_processor.py      # Loading and validating data
# ├── model_formulator.py    # Creating optimization models
# ├── solver_interface.py    # Common interface for solvers
# ├── solver_ortools.py      # OR-Tools implementation
# ├── feasibility_check.py   # Checking data feasibility
# ├── results_reporter.py    # Visualizing and reporting results
# └── main.py                # Main interactive interface

# This structure separates concerns and will make it easier to add
# support for additional solvers in the future
