"""
Benchmarking Script for Waffle Production Optimization Solvers.

This script compares the performance of different solvers on the waffle optimization problem.
"""
import time
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any

from data_processor import DataProcessor
from solver_interface import SolverFactory

def run_benchmark(
    demand_file: str, 
    supply_file: str, 
    cost_file: str, 
    wpp_file: str, 
    combinations_file: str,
    solvers: List[str] = ['ortools', 'highs'],
    objectives: List[str] = ['minimize_cost', 'maximize_output'],
    time_limits: List[int] = [30, 60, 120],
    limit_to_demand: bool = False
) -> Dict:
    """
    Run benchmarks for the specified solvers, objectives, and time limits.
    
    Args:
        demand_file: Path to waffle demand Excel file
        supply_file: Path to pan supply Excel file
        cost_file: Path to waffle cost Excel file
        wpp_file: Path to waffles per pan Excel file
        combinations_file: Path to allowed combinations Excel file
        solvers: List of solver names to benchmark
        objectives: List of objective functions to test
        time_limits: List of time limits (in seconds) to test
        limit_to_demand: Whether to limit production to exactly meet demand when maximizing output
        
    Returns:
        Dict: Dictionary containing benchmark results
    """
    print(f"Loading data from:")
    print(f"  - Demand: {demand_file}")
    print(f"  - Supply: {supply_file}")
    print(f"  - Cost: {cost_file}")
    print(f"  - WPP: {wpp_file}")
    print(f"  - Combinations: {combinations_file}")
    
    # Load data
    data_processor = DataProcessor(debug_mode=False)
    data_processor.load_data(demand_file, supply_file, cost_file, wpp_file, combinations_file)
    data = data_processor.get_optimization_data()
    
    # Store benchmark results
    results = []
    
    # Run benchmarks
    for solver_name in solvers:
        for objective in objectives:
            for time_limit in time_limits:
                print(f"\nRunning benchmark: {solver_name}, {objective}, time limit: {time_limit}s")
                
                try:
                    # Create solver
                    solver = SolverFactory.create_solver(solver_name, time_limit=time_limit, optimality_gap=0.005)
                    
                    # Build model
                    start_build_time = time.time()
                    if objective == 'minimize_cost':
                        solver.build_minimize_cost_model(data)
                    else:  # maximize_output
                        solver.build_maximize_output_model(data, limit_to_demand=limit_to_demand)
                    build_time = time.time() - start_build_time
                    
                    # Solve model
                    solve_result = solver.solve_model()
                    
                    # Get solution if available
                    solution = None
                    if solve_result['status'] in ['OPTIMAL', 'FEASIBLE', 'TIME_LIMIT']:
                        try:
                            solution = solver.get_solution()
                        except Exception as e:
                            print(f"  Error getting solution: {e}")
                    
                    # Store result
                    result = {
                        'solver': solver_name,
                        'objective': objective,
                        'time_limit': time_limit,
                        'status': solve_result['status'],
                        'build_time': build_time,
                        'solve_time': solve_result['wall_time'],
                        'total_time': build_time + solve_result['wall_time'],
                        'objective_value': solve_result.get('objective_value'),
                        'gap': solve_result.get('gap'),
                        'nodes': solve_result.get('nodes')
                    }
                    
                    if solution:
                        result['total_waffles'] = solution.get('total_waffles')
                        result['total_cost'] = solution.get('total_cost')
                    
                    results.append(result)
                    
                    # Print basic result
                    print(f"  Status: {solve_result['status']}")
                    print(f"  Build time: {build_time:.2f}s")
                    print(f"  Solve time: {solve_result['wall_time']:.2f}s")
                    print(f"  Total time: {(build_time + solve_result['wall_time']):.2f}s")
                    if solve_result.get('objective_value') is not None:
                        print(f"  Objective value: {solve_result['objective_value']:.2f}")
                    if solve_result.get('gap') is not None:
                        print(f"  Gap: {solve_result['gap']:.2f}%")
                except Exception as e:
                    print(f"  Error with solver {solver_name}: {e}")
                    print(f"  Skipping to next solver...")
    
    return results

def export_results(results: List[Dict], output_file: str = 'benchmark_results.xlsx') -> None:
    """
    Export benchmark results to an Excel file.
    
    Args:
        results: List of benchmark result dictionaries
        output_file: Path to output Excel file
    """
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
    print(f"\nBenchmark results exported to {output_file}")

def visualize_results(results: List[Dict]) -> None:
    """
    Visualize benchmark results.
    
    Args:
        results: List of benchmark result dictionaries
    """
    df = pd.DataFrame(results)
    
    # Set up figures
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    # Prepare data for plotting
    for objective in df['objective'].unique():
        obj_data = df[df['objective'] == objective]
        
        # Group by solver and time limit
        pivot = obj_data.pivot_table(
            index='time_limit', 
            columns='solver', 
            values='total_time', 
            aggfunc='mean'
        )
        
        # Plot solve time comparison
        pivot.plot(kind='bar', ax=ax1)
        
        # Plot objective value comparison (if objective values are available)
        if 'objective_value' in obj_data.columns:
            pivot2 = obj_data.pivot_table(
                index='time_limit', 
                columns='solver', 
                values='objective_value', 
                aggfunc='mean'
            )
            pivot2.plot(kind='bar', ax=ax2)
    
    # Configure plots
    ax1.set_title('Solver Performance Comparison: Total Time')
    ax1.set_xlabel('Time Limit (s)')
    ax1.set_ylabel('Total Time (s)')
    
    ax2.set_title('Solver Performance Comparison: Objective Value')
    ax2.set_xlabel('Time Limit (s)')
    ax2.set_ylabel('Objective Value')
    
    plt.tight_layout()
    
    # Save figures
    fig1.savefig('benchmark_time_comparison.png')
    fig2.savefig('benchmark_objective_comparison.png')
    
    print("Benchmark visualizations saved to:")
    print("  - benchmark_time_comparison.png")
    print("  - benchmark_objective_comparison.png")
    
    plt.show()

def main():
    """Main function for the benchmarking script."""
    print("=== Waffle Production Optimization Solver Benchmark ===")
    
    # Input files
    demand_file = input("Enter path to waffle demand file (default: WaffleDemand_increased_8.xlsx): ")
    demand_file = "WaffleDemand_increased_8.xlsx" if not demand_file or demand_file.lower() == 'default' else demand_file
    
    supply_file = input("Enter path to pan supply file (default: PanSupply_increased_8.xlsx): ")
    supply_file = "PanSupply_increased_8.xlsx" if not supply_file or supply_file.lower() == 'default' else supply_file
    
    cost_file = input("Enter path to waffle cost file (default: WaffleCostPerPan_increased_8.xlsx): ")
    cost_file = "WaffleCostPerPan_increased_8.xlsx" if not cost_file or cost_file.lower() == 'default' else cost_file
    
    wpp_file = input("Enter path to waffles per pan file (default: WafflesPerPan_increased_8.xlsx): ")
    wpp_file = "WafflesPerPan_increased_8.xlsx" if not wpp_file or wpp_file.lower() == 'default' else wpp_file
    
    combinations_file = input("Enter path to allowed combinations file (default: WafflePanCombinations_increased_8.xlsx): ")
    combinations_file = "WafflePanCombinations_increased_8.xlsx" if not combinations_file or combinations_file.lower() == 'default' else combinations_file
    
    # Benchmark parameters
    print("\nSelect solvers to benchmark (comma-separated):")
    all_solvers = ["ortools", "cbc", "glpk", "scip", "coin_cmd", "pulp_highs"]
    solvers_input = input(f"Solvers (default: all): ")
    solvers = all_solvers if not solvers_input or solvers_input.lower() == 'all' else [s.strip() for s in solvers_input.split(',')]
    
    print("\nSelect objectives to benchmark (comma-separated):")
    objectives_input = input("Objectives (default: minimize_cost,maximize_output): ")
    objectives = ["minimize_cost", "maximize_output"] if not objectives_input else [o.strip() for o in objectives_input.split(',')]
    
    print("\nSelect time limits in seconds (comma-separated):")
    time_limits_input = input("Time limits (default: 30,60,120): ")
    time_limits = [30, 60, 120] if not time_limits_input else [int(t.strip()) for t in time_limits_input.split(',')]
    
    limit_to_demand = input("\nLimit production to exactly meet demand when maximizing output? (y/n, default: n): ").lower() == 'y'
    
    # Run benchmarks
    results = run_benchmark(
        demand_file=demand_file,
        supply_file=supply_file,
        cost_file=cost_file,
        wpp_file=wpp_file,
        combinations_file=combinations_file,
        solvers=solvers,
        objectives=objectives,
        time_limits=time_limits,
        limit_to_demand=limit_to_demand
    )
    
    # Check if we have any results
    if results:
        # Export results
        export_results(results)
        
        # Check if we have enough solvers with successful runs to visualize
        successful_solvers = set(result['solver'] for result in results)
        if len(successful_solvers) >= 2:
            # Visualize results if user wants to
            visualize = input("\nVisualize benchmark results? (y/n, default: y): ").lower() != 'n'
            if visualize:
                try:
                    visualize_results(results)
                except Exception as e:
                    print(f"Error visualizing results: {e}")
                    print("This might happen if solvers had incompatible results or different objective values.")
        else:
            print("\nNot enough successful solvers to create visualization. Need at least 2 solvers with results.")
            if successful_solvers:
                print(f"Only {', '.join(successful_solvers)} had successful runs.")
    else:
        print("\nNo benchmark results to export or visualize. All solvers failed.")
        # Create empty export with headers
        empty_results = [{
            'solver': '',
            'objective': '',
            'time_limit': 0,
            'status': 'FAILED',
            'build_time': 0,
            'solve_time': 0,
            'total_time': 0,
            'objective_value': None,
            'gap': None,
            'nodes': None,
            'total_waffles': None,
            'total_cost': None
        }]
        export_results(empty_results)

if __name__ == "__main__":
    main() 