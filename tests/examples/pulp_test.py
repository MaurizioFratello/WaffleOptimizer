"""
Test script for PuLP-based solvers.
"""
from data_processor import DataProcessor
from solver_interface import SolverFactory

# Load data
print("Loading data...")
data_processor = DataProcessor(debug_mode=False)
data_processor.load_data(
    "WaffleDemand_increased_8.xlsx",
    "PanSupply_increased_8.xlsx",
    "WaffleCostPerPan_increased_8.xlsx",
    "WafflesPerPan_increased_8.xlsx",
    "WafflePanCombinations_increased_8.xlsx"
)
data = data_processor.get_optimization_data()

# Test various PuLP solvers
solvers_to_test = ['cbc', 'pulp_highs']

for solver_name in solvers_to_test:
    print(f"\n\nTesting {solver_name.upper()} solver...")
    
    # Create solver
    solver = SolverFactory.create_solver(solver_name, time_limit=60, optimality_gap=0.005)
    
    print("Building minimize_cost model...")
    solver.build_minimize_cost_model(data)
    
    print("Solving model...")
    result = solver.solve_model()
    
    print(f"\nSolution status: {result['status']}")
    print(f"Wall time: {result['wall_time']:.2f} seconds")
    
    if result['status'] in ['OPTIMAL', 'FEASIBLE', 'TIME_LIMIT']:
        try:
            solution = solver.get_solution()
            print(f"Objective value: {solution['objective_value']:.2f}")
            print(f"Total waffles: {solution['total_waffles']}")
            print(f"Total cost: {solution['total_cost']:.2f}")
            print(f"Number of variables with non-zero values: {len(solution['solution_values'])}")
        except Exception as e:
            print(f"Error getting solution: {e}")
    else:
        print("No feasible solution found.") 