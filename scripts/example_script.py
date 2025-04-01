"""
Example script demonstrating programmatic usage of the Waffle Optimizer.
"""
from main import WaffleOptimizer
import matplotlib.pyplot as plt
import os


def run_example(debug_mode: bool = False, use_increased_dataset: bool = False, use_4x_dataset: bool = False, use_8x_dataset: bool = False):
    """
    Run an example optimization.
    
    Args:
        debug_mode: If True, enables debug output. Defaults to False.
        use_increased_dataset: If True, uses the doubled dataset. Defaults to False.
        use_4x_dataset: If True, uses the 4x dataset. Defaults to False.
        use_8x_dataset: If True, uses the 8x dataset with randomness. Defaults to False.
    """
    # Initialize the optimizer
    optimizer = WaffleOptimizer(debug_mode=debug_mode)
    
    # Determine which dataset to use
    if use_8x_dataset:
        suffix = "_increased_8"
    elif use_4x_dataset:
        suffix = "_increased_4"
    elif use_increased_dataset:
        suffix = "_increased"
    else:
        suffix = ""
    
    # Load data
    optimizer.load_data(
        demand_file=f"WaffleDemand{suffix}.xlsx",
        supply_file=f"PanSupply{suffix}.xlsx",
        cost_file=f"WaffleCostPerPan{suffix}.xlsx",
        wpp_file=f"WafflesPerPan{suffix}.xlsx",
        combinations_file=f"WafflePanCombinations{suffix}.xlsx"
    )
    
    print("Starting optimization...")

    # Check feasibility
    feasibility_result = optimizer.check_feasibility()
    
    print("\n=== Feasibility Analysis ===")
    if feasibility_result['is_feasible']:
        print("The problem is likely FEASIBLE! The optimization can now be performed.")
    else:
        print("The problem is INFEASIBLE. Issues found:")
        for issue in feasibility_result['issues']:
            print(f"- {issue}")
        return
    
    # Solve for minimum cost
    print("\n=== Minimizing Production Cost ===")
    result_min_cost = optimizer.optimize(objective="minimize_cost", solver_name="ortools", limit_to_demand=True)
    
    # Store the complete solution for minimum cost
    if result_min_cost['status'] in ['OPTIMAL', 'FEASIBLE']:
        min_cost_solution = optimizer.solver.get_solution()
        # Export solution
        optimizer.export_solution("waffle_solution_min_cost.xlsx")
        print(f"Detailed results saved to waffle_solution_min_cost.xlsx")
    else:
        min_cost_solution = None
        print("No feasible solution found for minimizing cost.")
    
    # Solve for maximum output
    print("\n=== Maximizing Waffle Output ===")
    result_max_output = optimizer.optimize(objective="maximize_output", solver_name="ortools")
    
    # Store the complete solution for maximum output
    if result_max_output['status'] in ['OPTIMAL', 'FEASIBLE']:
        max_output_solution = optimizer.solver.get_solution()
        # Export solution
        optimizer.export_solution("waffle_solution_max_output.xlsx")
        print(f"Detailed results saved to waffle_solution_max_output.xlsx")
    else:
        max_output_solution = None
        print("No feasible solution found for maximizing output.")
    
    # Compare solutions if both are available
    if min_cost_solution and max_output_solution:
        print("\n=== Solution Comparison ===")
        
        # Get metrics from the stored solutions
        min_cost_total = min_cost_solution.get('total_cost', 0)
        min_cost_waffles = min_cost_solution.get('total_waffles', 0)
        max_output_waffles = max_output_solution.get('total_waffles', 0)
        max_output_total = max_output_solution.get('total_cost', 0)
        
        print(f"Minimum Cost Solution:")
        print(f"  - Total Cost: {min_cost_total:,.2f}")
        print(f"  - Total Waffles: {min_cost_waffles:,.0f}")
        
        print(f"Maximum Output Solution:")
        print(f"  - Total Cost: {max_output_total:,.2f}")
        print(f"  - Total Waffles: {max_output_waffles:,.0f}")
        
        # Calculate the trade-off
        cost_increase = max_output_total - min_cost_total
        output_increase = max_output_waffles - min_cost_waffles
        
        if cost_increase > 0 and output_increase > 0:
            cost_per_extra_waffle = cost_increase / output_increase
            print(f"\nTrade-off Analysis:")
            print(f"  - Extra cost for maximum output: {cost_increase:,.2f}")
            print(f"  - Additional waffles produced: {output_increase:,.0f}")
            print(f"  - Cost per additional waffle: {cost_per_extra_waffle:.4f}")
    
    print("\n=== Optimization Summary ===")
    print("The optimization has been completed successfully!")
    print("Key results:")
    print("1. The problem is feasible with the current data")
    print("2. Solutions have been saved to:")
    print("   - waffle_solution_min_cost.xlsx")
    print("   - waffle_solution_max_output.xlsx")
    print("3. You can use these Excel files to analyze the detailed production plan")


if __name__ == "__main__":
 
    # Run the example with the 8x dataset
    print("\nRunning optimization with 8x dataset...")
    run_example(debug_mode=False, use_increased_dataset=False, use_4x_dataset=False, use_8x_dataset=False)
