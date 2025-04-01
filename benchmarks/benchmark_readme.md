# Waffle Production Optimization Solver Benchmarking

This document provides instructions and findings from benchmarking various open-source solvers for the Waffle Production Optimization problem.

## Available Solvers

The following solvers have been implemented and can be benchmarked:

1. **OR-Tools SCIP** (`ortools`): Google's OR-Tools library using the SCIP solver
2. **CBC** (`cbc`): COIN-OR Branch and Cut solver via PuLP
3. **GLPK** (`glpk`): GNU Linear Programming Kit via PuLP
4. **HiGHS** (`pulp_highs`): HiGHS solver via PuLP
5. **SCIP** (`scip`): SCIP solver via PuLP
6. **COIN-OR CMD** (`coin_cmd`): COIN-OR solver via command line
7. **COINMP DLL** (`coinmp_dll`): COIN-OR solver via DLL
8. **CHOCO** (`choco_cmd`): Constraint programming solver 
9. **MIPCL** (`mipcl_cmd`): Mixed Integer Programming solver

## How to Run Benchmarks

Run the benchmark script to compare the performance of different solvers:

```bash
python benchmark_solvers.py
```

The script will prompt you for:
- Data files to use
- Solvers to benchmark (comma-separated list, defaults to all available solvers)
- Objectives to test (minimize_cost, maximize_output)
- Time limits for each solver
- Whether to limit production to exactly meet demand for maximize_output objective

Simply pressing Enter at the solvers prompt will run benchmarks for all implemented solvers. Note that if a solver is not installed on your system, the script will display an error message and continue with the next solver.

The benchmark results will be exported to `benchmark_results.xlsx` and visualizations will be saved as:
- `benchmark_time_comparison.png`
- `benchmark_objective_comparison.png`

## Initial Benchmark Results

Initial benchmarking shows:

### Minimize Cost Objective (time limit: 120s)

| Solver   | Status  | Solve Time | Objective Value  | Notes                      |
|----------|---------|------------|------------------|----------------------------|
| OR-Tools | OPTIMAL | 0.71s      | 4,477,617,007.95 | Very fast and efficient    |
| CBC      | OPTIMAL | 1.09s      | 4,477,617,007.95 | Comparable performance     |

Both solvers found the optimal solution with similar objective values. OR-Tools with SCIP was slightly faster.

## How to Implement Additional Solvers

To implement a new solver:

1. Create a new implementation of the `SolverInterface` abstract class
2. Add the solver to the `SolverFactory` in `solver_interface.py`
3. Run the benchmark to compare with existing solvers

## Installing Additional Solvers

The project includes an installation script to help you install and check the availability of solvers:

```bash
python install_solvers.py
```

This script will:
1. Check if PuLP is installed
2. Display all available and unavailable solvers
3. Guide you through the installation process for additional solvers

Note that some solvers may require manual installation depending on your operating system.

## Notes on HiGHS Direct Implementation

We attempted to implement HiGHS directly (without PuLP), but ran into API compatibility issues. The HiGHS solver is still available through PuLP (`pulp_highs`), but its performance may vary depending on system availability. 