"""
Example Usage of the Waffle Production Optimizer.

This script demonstrates how to use the waffle optimizer programmatically.
"""
import os
import sys
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.processor import DataProcessor
from src.data.validator import DataValidator
from src.solvers.base import SolverFactory
from src.utils.results_reporter import ResultsReporter

def minimize_cost_example():
    """Example of minimizing production cost."""
    print("=== Example: Minimize Production Cost ===\n")
    
    # Create data processor
    data_processor = DataProcessor(debug_mode=True)
    
    # Load data
    print("Loading data...")
    data_processor.load_data(
        demand_file="data/input/WaffleDemand.xlsx",
        supply_file="data/input/PanSupply.xlsx",
        cost_file="data/input/WaffleCostPerPan.xlsx",
        wpp_file="data/input/WafflesPerPan.xlsx",
        combinations_file="data/input/WafflePanCombinations.xlsx"
    )
    
    # Get optimization data
    optimization_data = data_processor.get_optimization_data()
    
    # Create data validator
    data_validator = DataValidator(debug_mode=True)
    
    # Check feasibility
    print("\nChecking data feasibility...")
    is_feasible, issues = data_validator.check_basic_feasibility(optimization_data)
    
    if not is_feasible:
        print("Data is not feasible. The following issues were found:")
        for issue in issues:
            print(f"- {issue}")
        return
    
    # Create solver (using CBC from PuLP)
    print("\nCreating CBC solver...")
    solver = SolverFactory.create_solver(
        solver_name="cbc",
        time_limit=60,
        optimality_gap=0.005
    )
    
    # Build minimize cost model
    print("Building minimize cost model...")
    solver.build_minimize_cost_model(optimization_data)
    
    # Solve model
    print("Solving optimization model...")
    start_time = time.time()
    solution_info = solver.solve_model()
    solve_time = time.time() - start_time
    
    # Check if solved successfully
    if not solution_info.get('is_feasible', False):
        print(f"Failed to find a feasible solution. Status: {solution_info.get('status', 'Unknown')}")
        return
    
    # Get solution
    solution = solver.get_solution()
    
    # Create results reporter
    results_reporter = ResultsReporter(debug_mode=True)
    
    # Print solution summary
    print(f"\nSolved in {solve_time:.2f} seconds")
    results_reporter.print_summary(solution)
    
    # Validate solution
    print("\nValidating solution...")
    validation = data_validator.validate_solution(optimization_data, solution)
    
    # Print detailed results
    results_reporter.print_detailed_results(optimization_data, solution, validation)
    
    # Create output directory if it doesn't exist
    os.makedirs("data/output", exist_ok=True)
    
    # Export solution to Excel
    output_file = "data/output/minimize_cost_solution.xlsx"
    print(f"\nExporting solution to {output_file}...")
    results_reporter.export_to_excel(optimization_data, solution, output_file)
    
    print("\nOptimization completed successfully.")

def maximize_output_example():
    """Example of maximizing waffle output."""
    print("=== Example: Maximize Waffle Output ===\n")
    
    # Create data processor
    data_processor = DataProcessor(debug_mode=True)
    
    # Load data
    print("Loading data...")
    data_processor.load_data(
        demand_file="data/input/WaffleDemand.xlsx",
        supply_file="data/input/PanSupply.xlsx",
        cost_file="data/input/WaffleCostPerPan.xlsx",
        wpp_file="data/input/WafflesPerPan.xlsx",
        combinations_file="data/input/WafflePanCombinations.xlsx"
    )
    
    # Get optimization data
    optimization_data = data_processor.get_optimization_data()
    
    # Create data validator
    data_validator = DataValidator(debug_mode=True)
    
    # Check feasibility
    print("\nChecking data feasibility...")
    is_feasible, issues = data_validator.check_basic_feasibility(optimization_data)
    
    if not is_feasible:
        print("Data is not feasible. The following issues were found:")
        for issue in issues:
            print(f"- {issue}")
        return
    
    # Create solver (using OR-Tools)
    print("\nCreating OR-Tools solver...")
    solver = SolverFactory.create_solver(
        solver_name="ortools",
        time_limit=60,
        optimality_gap=0.005
    )
    
    # Build maximize output model
    print("Building maximize output model...")
    solver.build_maximize_output_model(optimization_data)
    
    # Solve model
    print("Solving optimization model...")
    start_time = time.time()
    solution_info = solver.solve_model()
    solve_time = time.time() - start_time
    
    # Check if solved successfully
    if not solution_info.get('is_feasible', False):
        print(f"Failed to find a feasible solution. Status: {solution_info.get('status', 'Unknown')}")
        return
    
    # Get solution
    solution = solver.get_solution()
    
    # Create results reporter
    results_reporter = ResultsReporter(debug_mode=True)
    
    # Print solution summary
    print(f"\nSolved in {solve_time:.2f} seconds")
    results_reporter.print_summary(solution)
    
    # Validate solution
    print("\nValidating solution...")
    validation = data_validator.validate_solution(optimization_data, solution)
    
    # Print detailed results
    results_reporter.print_detailed_results(optimization_data, solution, validation)
    
    # Create output directory if it doesn't exist
    os.makedirs("data/output", exist_ok=True)
    
    # Export solution to Excel
    output_file = "data/output/maximize_output_solution.xlsx"
    print(f"\nExporting solution to {output_file}...")
    results_reporter.export_to_excel(optimization_data, solution, output_file)
    
    print("\nOptimization completed successfully.")

def compare_solvers_example():
    """Example of comparing different solvers."""
    print("=== Example: Compare Different Solvers ===\n")
    
    # Create data processor
    data_processor = DataProcessor()
    
    # Load data
    print("Loading data...")
    data_processor.load_data(
        demand_file="data/input/WaffleDemand.xlsx",
        supply_file="data/input/PanSupply.xlsx",
        cost_file="data/input/WaffleCostPerPan.xlsx",
        wpp_file="data/input/WafflesPerPan.xlsx",
        combinations_file="data/input/WafflePanCombinations.xlsx"
    )
    
    # Get optimization data
    optimization_data = data_processor.get_optimization_data()
    
    # Solvers to compare
    solvers = ["cbc", "glpk", "ortools", "scip", "coin_cmd"]
    
    # Compare solvers
    print("\nComparing solvers for minimize cost objective:")
    print(f"{'Solver':<12} {'Status':<15} {'Objective':<15} {'Time (s)':<10}")
    print("-" * 55)
    
    for solver_name in solvers:
        # Create solver
        solver = SolverFactory.create_solver(
            solver_name=solver_name,
            time_limit=10,  # Short time limit for comparison
            optimality_gap=0.01
        )
        
        # Build minimize cost model
        solver.build_minimize_cost_model(optimization_data)
        
        # Solve model
        start_time = time.time()
        solution_info = solver.solve_model()
        solve_time = time.time() - start_time
        
        # Get status and objective
        status = solution_info.get('status', 'Unknown')
        objective = solution_info.get('objective_value', 'N/A')
        if objective != 'N/A':
            objective = f"{objective:.2f}"
        
        print(f"{solver_name:<12} {status:<15} {objective:<15} {solve_time:<10.3f}")

if __name__ == "__main__":
    print("Waffle Production Optimizer Examples\n")
    
    while True:
        print("\nSelect an example to run:")
        print("1. Minimize Production Cost")
        print("2. Maximize Waffle Output")
        print("3. Compare Different Solvers")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-3): ")
        
        if choice == "1":
            minimize_cost_example()
        elif choice == "2":
            maximize_output_example()
        elif choice == "3":
            compare_solvers_example()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            
    print("\nThank you for using the Waffle Production Optimizer!") 