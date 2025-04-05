import os
import time
import pandas as pd
import numpy as np
import logging
from tabulate import tabulate
from src.data.processor import DataProcessor
from src.solvers.solver_manager import SolverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_default_data(shortage_penalty=10000):
    """
    Load the default dataset from the standard input files.
    
    Args:
        shortage_penalty: Cost penalty for not satisfying demand (per waffle)
    """
    # Default file paths
    data_folder = "data/input"
    demand_file = os.path.join(data_folder, "WaffleDemand.xlsx")
    supply_file = os.path.join(data_folder, "PanSupply.xlsx")
    cost_file = os.path.join(data_folder, "WaffleCostPerPan.xlsx")
    wpp_file = os.path.join(data_folder, "WafflesPerPan.xlsx")
    combinations_file = os.path.join(data_folder, "WafflePanCombinations.xlsx")
    
    # Create data processor and load data
    data_processor = DataProcessor(debug_mode=True)  # Enable debug mode
    data_processor.load_data(
        demand_file=demand_file,
        supply_file=supply_file,
        cost_file=cost_file,
        wpp_file=wpp_file,
        combinations_file=combinations_file
    )
    
    # Get optimization data
    data = data_processor.get_optimization_data()
    
    # Add shortage penalty
    data['shortage_penalty'] = shortage_penalty
    
    # Print summary of the data
    print("\nData Summary:")
    print(f"Waffle Types: {len(data['waffle_types'])}")
    print(f"Pan Types: {len(data['pan_types'])}")
    print(f"Weeks: {len(data['weeks'])}")
    print(f"Demand Entries: {len(data['demand'])}")
    print(f"Supply Entries: {len(data['supply'])}")
    print(f"Cost Entries: {len(data['cost'])}")
    print(f"Allowed Combinations: {len(data['allowed'])}")
    print(f"Shortage Penalty: {shortage_penalty}")
    
    # Calculate total demand
    total_demand = sum(data['demand'].values())
    print(f"Total Demand: {total_demand} waffles")
    
    # Calculate average cost per waffle
    all_costs = []
    for (waffle, pan), cost in data['cost'].items():
        wpp = data['wpp'].get(waffle, 0)
        if wpp > 0:
            cost_per_waffle = cost / wpp
            all_costs.append(cost_per_waffle)
    
    avg_cost = sum(all_costs) / len(all_costs) if all_costs else 0
    print(f"Average Cost Per Waffle: {avg_cost:.4f}")
    print(f"Shortage Penalty / Avg Cost Ratio: {shortage_penalty / avg_cost:.2f}")
    
    # Sample data entries
    print("\nSample Data:")
    if data['demand']:
        key, value = next(iter(data['demand'].items()))
        print(f"Sample Demand: {key} = {value}")
    if data['cost']:
        key, value = next(iter(data['cost'].items()))
        print(f"Sample Cost: {key} = {value}")
    if data['supply']:
        key, value = next(iter(data['supply'].items()))
        print(f"Sample Supply: {key} = {value}")
    if data['wpp']:
        key, value = next(iter(data['wpp'].items()))
        print(f"Sample WPP: {key} = {value}")
    
    return data

def analyze_solution(solver_name, config_name, objective_type, solution, optimization_data):
    """
    Analyze the optimization solution in detail.
    
    Args:
        solver_name: Name of the solver
        config_name: Configuration name for display
        objective_type: Type of objective function ('minimize_cost' or 'maximize_output')
        solution: Solution dictionary
        optimization_data: Original optimization data
    """
    # Basic solution info
    print(f"\nDetailed Analysis for {solver_name} ({config_name}, {objective_type}):")
    
    # Check if solution exists
    if not solution:
        print("  No solution data available.")
        return
    
    # Analyze objective value
    objective = solution.get('objective_value', 0)
    print(f"  Objective Value: {objective:,.2f}")
    
    # Production values could be in either 'production' or 'values' field
    # The 'values' field is the primary location for ortools and pulp solvers
    production = solution.get('production', {})
    if not production and 'values' in solution:
        production = solution.get('values', {})
    
    if not production:
        print("  No production data available in solution.")
        
        # Additional diagnostics
        print("  Solution keys:", ", ".join(solution.keys()))
        for key in solution:
            if isinstance(solution[key], dict) and len(solution[key]) < 10:
                print(f"  Contents of {key}: {solution[key]}")
        return
    
    # Analyze production
    total_production = sum(production.values())
    print(f"  Total Production: {total_production:,}")
    
    # Count non-zero production entries
    non_zero_production = sum(1 for v in production.values() if v > 0)
    print(f"  Non-zero Production Entries: {non_zero_production}")
    
    # Calculate total waffles produced
    total_waffles = 0
    for (waffle, pan, week), amount in production.items():
        wpp = optimization_data['wpp'].get(waffle, 0)
        total_waffles += amount * wpp
    print(f"  Total Waffles Produced: {total_waffles:,}")
    
    # Calculate demand satisfaction
    total_demand = sum(optimization_data['demand'].values())
    demand_satisfaction = min(total_waffles / total_demand * 100 if total_demand > 0 else 0, 100)
    print(f"  Demand Satisfaction: {demand_satisfaction:.2f}%")
    
    # Calculate average cost per waffle
    if total_waffles > 0:
        avg_cost = objective / total_waffles if objective_type == 'minimize_cost' else objective
        print(f"  Average Cost Per Waffle: {avg_cost:.4f}")
    
    # Show some sample production if any
    if non_zero_production > 0:
        print("  Sample Production (waffle, pan, week) = amount:")
        count = 0
        for key, value in production.items():
            if value > 0 and count < 5:
                print(f"    * {key} = {value}")
                count += 1

def test_solver_with_config(solver_name, config_name, constraint_config, optimization_data, objective_type='minimize_cost', limit_to_demand=False, time_limit=60, gap=0.01):
    """
    Test a solver with a specific constraint configuration and objective function.
    
    Args:
        solver_name: Name of the solver to test
        config_name: Display name of the configuration
        constraint_config: Dictionary of constraint configurations
        optimization_data: Dictionary containing optimization data
        objective_type: Type of objective function ('minimize_cost' or 'maximize_output')
        limit_to_demand: Whether to limit production to demand (for maximize_output only)
        time_limit: Time limit in seconds
        gap: Optimality gap
        
    Returns:
        dict: Results of the optimization
    """
    obj_desc = "minimize cost" if objective_type == 'minimize_cost' else "maximize output"
    logger.info(f"Testing solver '{solver_name}' with configuration '{config_name}' and objective: {obj_desc}")
    
    # Create solver manager
    solver_manager = SolverManager()
    
    # Enable and configure constraints
    for constraint_type, config in constraint_config.items():
        if config is None:
            # If config is None, disable the constraint
            solver_manager.set_constraint_enabled(constraint_type, False)
        else:
            # Enable and configure the constraint
            solver_manager.set_constraint_enabled(constraint_type, True)
            solver_manager.set_constraint_configuration(constraint_type, config)
    
    # Print the enabled constraints
    constraints = solver_manager._enabled_constraints
    print(f"\nEnabled Constraints for {solver_name} ({config_name}, {obj_desc}):")
    for constraint_type, enabled in constraints.items():
        if enabled:
            config = solver_manager.get_constraint_configuration(constraint_type)
            print(f"  - {constraint_type}: {config}")
    
    # Create solver with constraints
    solver = solver_manager.create_solver(
        solver_name=solver_name,
        with_constraints=True,
        time_limit=time_limit,
        optimality_gap=gap
    )
    
    # Build and solve the model
    start_time = time.time()
    if objective_type == 'minimize_cost':
        solver.build_minimize_cost_model(optimization_data)
    else:  # maximize_output
        solver.build_maximize_output_model(optimization_data, limit_to_demand=limit_to_demand)
    
    solution_info = solver.solve_model()
    end_time = time.time()
    
    # Get the solution and extract metrics
    solution = solver.get_solution() or {}
    
    # Check solution status
    is_feasible = False
    status = "Unknown"
    total_cost = float('inf')
    production_total = 0
    waffles_total = 0
    
    if solution_info is not None:
        # Different solvers might use different keys for feasibility
        is_feasible = solution_info.get('is_feasible', False)
        if not is_feasible and solution_info.get('status', '').lower() in ['optimal', 'feasible']:
            is_feasible = True
            
        status = solution_info.get('status', 'Unknown')
    
    # If we have a solution with an objective value, it must be feasible
    if solution and 'objective_value' in solution:
        is_feasible = True
        total_cost = solution.get('objective_value')
        
        # Calculate total production - check both 'production' and 'values' fields
        production = solution.get('production', {})
        if not production and 'values' in solution:
            production = solution.get('values', {})
            
        production_total = sum(production.values())
        
        # Calculate total waffles produced
        for (waffle, pan, week), amount in production.items():
            wpp = optimization_data['wpp'].get(waffle, 0)
            waffles_total += amount * wpp
        
        # Analyze the solution
        analyze_solution(solver_name, config_name, objective_type, solution, optimization_data)
    elif solution_info and solution_info.get('status', '').lower() != 'infeasible':
        # If the solution exists but has no objective_value, try to analyze it anyway
        print(f"\nSolution info without objective value for {solver_name} ({config_name}, {obj_desc}):")
        print(f"  Status: {status}")
        print(f"  Solution keys: {list(solution.keys())}")
        print(f"  Solution info keys: {list(solution_info.keys())}")
    
    # Return results
    return {
        'solver': solver_name,
        'config': config_name,
        'objective': objective_type,
        'is_feasible': is_feasible,
        'status': status,
        'total_cost': total_cost,
        'solve_time': end_time - start_time,
        'production_total': production_total,
        'waffles_total': waffles_total
    }

def main():
    """Main function to test solvers with different constraint configurations, penalty levels and objective functions."""
    # Available solvers - just use one for faster testing
    solver_name = 'ortools'
    
    # Test multiple shortage penalty levels
    penalty_levels = [100, 10000]  # Reduced to just two for faster testing
    
    # Results storage for all tests
    all_results = []
    
    for penalty in penalty_levels:
        print(f"\n{'='*50}")
        print(f" TESTING WITH SHORTAGE PENALTY = {penalty}")
        print(f"{'='*50}")
        
        # Load data with current penalty
        optimization_data = load_default_data(shortage_penalty=penalty)
        
        # Define constraint configurations to test
        configs = [
            # Test all 4 combinations of demand equality and supply cumulative
            {
                'name': f'DE_True_SC_True_P{penalty}',
                'desc': f'Demand Equality=True, Supply Cumulative=True (P={penalty})',
                'constraints': {
                    'demand': {'equality': True},
                    'supply': {'cumulative': True},
                    'allowed_combinations': {}
                }
            },
            {
                'name': f'DE_True_SC_False_P{penalty}',
                'desc': f'Demand Equality=True, Supply Cumulative=False (P={penalty})',
                'constraints': {
                    'demand': {'equality': True},
                    'supply': {'cumulative': False},
                    'allowed_combinations': {}
                }
            },
            {
                'name': f'DE_False_SC_True_P{penalty}',
                'desc': f'Demand Equality=False, Supply Cumulative=True (P={penalty})',
                'constraints': {
                    'demand': {'equality': False},
                    'supply': {'cumulative': True},
                    'allowed_combinations': {}
                }
            },
            {
                'name': f'DE_False_SC_False_P{penalty}',
                'desc': f'Demand Equality=False, Supply Cumulative=False (P={penalty})',
                'constraints': {
                    'demand': {'equality': False},
                    'supply': {'cumulative': False},
                    'allowed_combinations': {}
                }
            }
        ]
        
        # Results for current penalty level
        results = []
        
        # Test each configuration with both objective functions
        for config in configs:
            # Test with minimize cost objective
            try:
                result = test_solver_with_config(
                    solver_name=solver_name,
                    config_name=config['desc'],
                    constraint_config=config['constraints'],
                    optimization_data=optimization_data,
                    objective_type='minimize_cost'
                )
                result['short_name'] = config['name']  # Add short name for plotting
                results.append(result)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Error testing '{config['desc']}' with minimize_cost: {str(e)}")
                result = {
                    'solver': solver_name,
                    'config': config['desc'],
                    'objective': 'minimize_cost',
                    'short_name': config['name'],
                    'is_feasible': False,
                    'status': f"Error: {str(e)}",
                    'total_cost': float('inf'),
                    'solve_time': 0,
                    'production_total': 0,
                    'waffles_total': 0
                }
                results.append(result)
                all_results.append(result)
                
            # Test with maximize output objective (only one configuration needed)
            try:
                result = test_solver_with_config(
                    solver_name=solver_name,
                    config_name=config['desc'],
                    constraint_config=config['constraints'],
                    optimization_data=optimization_data,
                    objective_type='maximize_output',
                    limit_to_demand=False
                )
                result['short_name'] = config['name']  # Add short name for plotting
                results.append(result)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Error testing '{config['desc']}' with maximize_output: {str(e)}")
                result = {
                    'solver': solver_name,
                    'config': config['desc'],
                    'objective': 'maximize_output',
                    'short_name': config['name'],
                    'is_feasible': False,
                    'status': f"Error: {str(e)}",
                    'total_cost': float('inf'),
                    'solve_time': 0,
                    'production_total': 0,
                    'waffles_total': 0
                }
                results.append(result)
                all_results.append(result)
    
    # Format and display all results
    table_data = []
    headers = ["Configuration", "Objective", "Feasible", "Status", "Cost/Objective", "Waffles", "Time (s)"]
    
    for result in all_results:
        row = [
            result['config'],
            "Min Cost" if result['objective'] == 'minimize_cost' else "Max Output",
            "Yes" if result['is_feasible'] else "No",
            result['status'],
            f"{result['total_cost']:,.2f}" if result['total_cost'] != float('inf') else "N/A",
            f"{result.get('waffles_total', 0):,}",
            f"{result['solve_time']:.2f}"
        ]
        table_data.append(row)
    
    # Sort results: first by penalty, then by configuration, then by objective
    def get_penalty(row):
        match = re.search(r'P=(\d+)', row[0])
        return int(match.group(1)) if match else 0
        
    table_data.sort(key=lambda x: (get_penalty(x), x[0], x[1]))
    
    # Print results table
    print("\nSolver Comparison Results:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Create summarized table with focus on key metrics
    summary_data = []
    summary_headers = ["Configuration", "Waffles (Min Cost)", "Cost", "Waffles (Max Out)", "Obj Value"]
    
    # Group results by configuration to create summary rows
    config_groups = {}
    for result in all_results:
        config_key = result['config']
        if config_key not in config_groups:
            config_groups[config_key] = {'config': config_key}
            
        if result['objective'] == 'minimize_cost' and result['is_feasible']:
            config_groups[config_key]['min_cost_waffles'] = result.get('waffles_total', 0)
            config_groups[config_key]['min_cost_cost'] = result['total_cost']
            
        elif result['objective'] == 'maximize_output' and result['is_feasible']:
            config_groups[config_key]['max_out_waffles'] = result.get('waffles_total', 0)
            config_groups[config_key]['max_out_obj'] = result['total_cost']
    
    # Create summary rows
    for config, data in config_groups.items():
        row = [
            config,
            f"{data.get('min_cost_waffles', 0):,}",
            f"{data.get('min_cost_cost', float('inf')):,.2f}" if data.get('min_cost_cost', float('inf')) != float('inf') else "N/A",
            f"{data.get('max_out_waffles', 0):,}",
            f"{data.get('max_out_obj', 0):,.2f}" if 'max_out_obj' in data else "N/A"
        ]
        summary_data.append(row)
    
    # Sort by configuration
    summary_data.sort(key=lambda x: x[0])
    
    print("\nSummary of Results (Comparing Both Objective Functions):")
    print(tabulate(summary_data, headers=summary_headers, tablefmt="grid"))
    
    # Find and print best configurations
    min_cost_results = [r for r in all_results if r['objective'] == 'minimize_cost' and r['is_feasible'] and r.get('waffles_total', 0) > 0]
    max_output_results = [r for r in all_results if r['objective'] == 'maximize_output' and r['is_feasible'] and r.get('waffles_total', 0) > 0]
    
    print("\nConclusion:")
    if min_cost_results:
        best_min_cost = min(min_cost_results, key=lambda x: x['total_cost'])
        print(f"Best minimize cost configuration: {best_min_cost['config']}")
        print(f"  - Cost: {best_min_cost['total_cost']:,.2f}")
        print(f"  - Waffles Produced: {best_min_cost.get('waffles_total', 0):,}")
    else:
        print("No feasible configurations with non-zero production for cost minimization.")
        
    if max_output_results:
        best_max_output = max(max_output_results, key=lambda x: x.get('waffles_total', 0))
        print(f"Best maximize output configuration: {best_max_output['config']}")
        print(f"  - Objective Value: {best_max_output['total_cost']:,.2f}")
        print(f"  - Waffles Produced: {best_max_output.get('waffles_total', 0):,}")
    else:
        print("No feasible configurations with non-zero production for output maximization.")
        
    # Print additional diagnostic information about the model
    print("\nModel Diagnostics:")
    print(f"Total Demand: {sum(optimization_data['demand'].values()):,} waffles")
    print(f"Total Supply (when cumulative=True): {sum(optimization_data['supply'].values())} pans")
    
    # Calculate possible production capacity
    total_capacity = 0
    for (waffle, pan) in optimization_data['allowed']:
        wpp = optimization_data['wpp'].get(waffle, 0)
        for week, supply in [(w, s) for (p, w), s in optimization_data['supply'].items() if p == pan]:
            total_capacity += supply * wpp
    
    print(f"Theoretical Maximum Production Capacity: {total_capacity:,} waffles")
    print(f"Ratio of Capacity to Demand: {total_capacity / sum(optimization_data['demand'].values()):.2f}")

if __name__ == "__main__":
    import re
    main() 