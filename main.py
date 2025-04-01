"""
Waffle Production Optimization Main Module.

This is the main entry point for the waffle production optimization application.
"""
import os
from src.data.processor import DataProcessor
from src.data.validator import DataValidator
from src.solvers.base import SolverFactory
from src.utils.results_reporter import ResultsReporter

def print_tabular(headers, data, widths=None):
    """
    Print data in a tabular format to the command line.
    
    Args:
        headers: List of column headers
        data: List of rows, where each row is a list of values
        widths: Optional list of column widths (auto-calculated if not provided)
    """
    if not widths:
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in data:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))
    
    # Print header row
    header_row = " | ".join(f"{h:{widths[i]}s}" for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print data rows
    for row in data:
        row_str = " | ".join(f"{str(val):{widths[i]}s}" for i, val in enumerate(row))
        print(row_str)

def get_user_config():
    """
    Get configuration from interactive command-line input.
    Uses default values when user presses Enter without input.
    """
    # Default values
    defaults = {
        'objective': 'cost',
        'demand': 'data/input/WaffleDemand.xlsx',
        'supply': 'data/input/PanSupply.xlsx',
        'cost': 'data/input/WaffleCostPerPan.xlsx',
        'wpp': 'data/input/WafflesPerPan.xlsx',
        'combinations': 'data/input/WafflePanCombinations.xlsx',
        'solver': 'ortools',
        'time_limit': 10,
        'gap': 0.005,
        'limit_to_demand': False,
        'debug': False,
        'output': 'data/output/waffle_solution.xlsx'
    }
    
    print("\n=== Waffle Production Optimizer Configuration ===\n")
    
    # Option to use all defaults
    print("Would you like to use all default values? [y/N]")
    use_defaults = input("> ").strip().lower().startswith('y')
    
    if use_defaults:
        print("\n=== Default Configuration Values ===")
        # Display default values in tabular form
        headers = ["Setting", "Default Value"]
        data = [
            ["Objective", defaults['objective']],
            ["Solver", defaults['solver']],
            ["Time limit", f"{defaults['time_limit']} seconds"],
            ["Optimality gap", defaults['gap']],
            ["Limit to demand", "No"],
            ["Debug mode", "Disabled"],
            ["Output file", defaults['output']],
            ["Demand file", defaults['demand']],
            ["Supply file", defaults['supply']],
            ["Cost file", defaults['cost']],
            ["Waffles per pan file", defaults['wpp']],
            ["Combinations file", defaults['combinations']]
        ]
        print_tabular(headers, data)
        
        confirm = input("\nProceed with these settings? [Y/n]\n> ").strip().lower()
        if confirm == 'n':
            print("Configuration cancelled. Exiting...")
            exit()
        
        return defaults.copy()
    
    # If not using all defaults, proceed with interactive configuration
    config = {}
    
    # Optimization objective
    print(f"Optimization objective [cost/output] (default: {defaults['objective']})")
    while True:
        objective = input("> ").strip().lower() or defaults['objective']
        if objective in ['cost', 'output']:
            config['objective'] = objective
            break
        print("Invalid input. Please enter 'cost' or 'output'.")
    
    # Data files
    print(f"\nData files (press Enter to use defaults):")
    config['demand'] = input(f"Demand file path (default: {defaults['demand']})\n> ").strip() or defaults['demand']
    config['supply'] = input(f"Supply file path (default: {defaults['supply']})\n> ").strip() or defaults['supply']
    config['cost'] = input(f"Cost file path (default: {defaults['cost']})\n> ").strip() or defaults['cost']
    config['wpp'] = input(f"Waffles per pan file path (default: {defaults['wpp']})\n> ").strip() or defaults['wpp']
    config['combinations'] = input(f"Combinations file path (default: {defaults['combinations']})\n> ").strip() or defaults['combinations']
    
    # Solver options
    print(f"\nSolver options:")
    
    # Solver
    print(f"Solver (default: {defaults['solver']})")
    print("Available options: ortools, cbc, glpk, pulp_highs, scip, coin_cmd")
    solver = input("> ").strip().lower() or defaults['solver']
    config['solver'] = solver
    
    # Time limit
    print(f"Time limit in seconds (default: {defaults['time_limit']})")
    while True:
        time_limit_str = input("> ").strip() or str(defaults['time_limit'])
        try:
            config['time_limit'] = int(time_limit_str)
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    
    # Optimality gap
    print(f"Optimality gap (default: {defaults['gap']})")
    while True:
        gap_str = input("> ").strip() or str(defaults['gap'])
        try:
            config['gap'] = float(gap_str)
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    # Model options
    print(f"\nModel options:")
    limit_to_demand = input("Limit production to demand? [y/N]\n> ").strip().lower()
    config['limit_to_demand'] = limit_to_demand.startswith('y')
    
    # Debug mode
    debug = input("Enable debug mode? [y/N]\n> ").strip().lower()
    config['debug'] = debug.startswith('y')
    
    # Output file
    print(f"\nOutput options:")
    config['output'] = input(f"Output file path (default: {defaults['output']})\n> ").strip() or defaults['output']
    
    # Confirm settings
    print("\n=== Configuration Summary ===")
    print(f"Objective: {config['objective']}")
    print(f"Solver: {config['solver']}")
    print(f"Time limit: {config['time_limit']} seconds")
    print(f"Optimality gap: {config['gap']}")
    print(f"Limit to demand: {'Yes' if config['limit_to_demand'] else 'No'}")
    print(f"Debug mode: {'Enabled' if config['debug'] else 'Disabled'}")
    print(f"Output file: {config['output']}")
    
    confirm = input("\nProceed with these settings? [Y/n]\n> ").strip().lower()
    if confirm == 'n':
        print("Configuration cancelled. Exiting...")
        exit()
        
    return config

def main():
    """Main function for waffle production optimization."""
    # Get configuration interactively
    config = get_user_config()
    
    # Create data processor
    data_processor = DataProcessor(debug_mode=config['debug'])
    
    # Load data
    print(f"\nLoading data from input files...")
    data_processor.load_data(
        demand_file=config['demand'],
        supply_file=config['supply'],
        cost_file=config['cost'],
        wpp_file=config['wpp'],
        combinations_file=config['combinations']
    )
    
    # Get optimization data
    optimization_data = data_processor.get_optimization_data()
    
    # Create data validator
    data_validator = DataValidator(debug_mode=config['debug'])
    
    # Check feasibility
    print("Checking data feasibility...")
    is_feasible, critical_issues, warnings = data_validator.check_basic_feasibility(optimization_data)
    
    # Print any warnings
    if warnings:
        print("\nWarnings (these won't affect optimization):")
        for warning in warnings:
            print(f"- {warning}")
    
    # Handle critical issues
    if not is_feasible:
        print("\nCritical issues found that prevent optimization:")
        for issue in critical_issues:
            print(f"- {issue}")
        return
    
    # Create solver
    print(f"\nCreating {config['solver']} solver...")
    solver = SolverFactory.create_solver(
        solver_name=config['solver'],
        time_limit=config['time_limit'],
        optimality_gap=config['gap']
    )
    
    # Build model based on objective
    if config['objective'].lower() == 'cost':
        print("Building minimize cost model...")
        solver.build_minimize_cost_model(optimization_data)
    else:
        print("Building maximize output model...")
        solver.build_maximize_output_model(optimization_data, limit_to_demand=config['limit_to_demand'])
    
    # Solve model
    print("Solving optimization model...")
    solution_info = solver.solve_model()
    
    # Check if solved successfully
    if not solution_info['is_feasible']:
        print(f"Failed to find a feasible solution. Status: {solution_info['status']}")
        return
    
    # Get solution
    solution = solver.get_solution()
    
    # Create results reporter
    results_reporter = ResultsReporter(debug_mode=config['debug'])
    
    # Print solution summary
    results_reporter.print_summary(solution)
    
    # Validate solution
    print("Validating solution...")
    validation = data_validator.validate_solution(optimization_data, solution)
    
    # Print detailed results
    if config['debug']:
        results_reporter.print_detailed_results(optimization_data, solution, validation)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(config['output']), exist_ok=True)
    
    # Export solution to Excel
    print(f"Exporting solution to {config['output']}...")
    results_reporter.export_to_excel(optimization_data, solution, config['output'])
    
    # Print tabular solution summary
    print("\n=== Optimization Results Summary ===")
    headers = ["Metric", "Value"]
    data = [
        ["Solver", solution_info['solver_name']],
        ["Status", solution_info['status']],
        ["Solution Time", f"{solution_info['solution_time']:.2f} seconds"],
    ]
    
    # Add metrics based on objective type
    if config['objective'].lower() == 'cost':
        data.append(["Objective", f"Minimize Cost"])
        if 'objective_value' in solution:
            data.append(["Total Cost", f"${solution['objective_value']:.2f}"])
    else:
        data.append(["Objective", f"Maximize Output"])
        if 'objective_value' in solution:
            data.append(["Total Output", f"{solution['objective_value']:.0f} waffles"])
    
    # Check for metrics in solution['metrics']
    if 'metrics' in solution:
        metrics = solution['metrics']
        if 'total_output' in metrics:
            data.append(["Total Waffles", f"{metrics['total_output']:,} waffles"])
        if 'average_cost_per_waffle' in metrics:
            data.append(["Avg Cost/Waffle", f"${metrics['average_cost_per_waffle']:.2f}"])
    
    # Add number of variables
    if 'num_variables' in solution:
        data.append(["Variables", f"{solution['num_variables']:,}"])
    
    print_tabular(headers, data)
    
    print("\nOptimization completed successfully.")

if __name__ == "__main__":
    main()
