# Waffle Production Optimization Solver Benchmarking

This document provides instructions and findings from benchmarking various open-source solvers for the Waffle Production Optimization problem.

## Available Solvers

The following solvers have been implemented and can be benchmarked:

1. **OR-Tools SCIP** (`ortools`): Google's OR-Tools library using the SCIP solver
2. **CBC** (`cbc`): COIN-OR Branch and Cut solver via PuLP
3. **GLPK**: GNU Linear Programming Kit
4. **SCIP**: Solving Constraint Integer Programs
5. **COIN-OR CBC**: COIN-OR Branch and Cut
6. **COIN-OR CMD** (`coin_cmd`