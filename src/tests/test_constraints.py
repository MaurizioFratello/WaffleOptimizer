"""
Test script for the constraint system.

This script verifies that the constraint system works correctly with both solver implementations.
"""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import modules properly
sys.path.append(str(Path(__file__).parent.parent.parent))

import time
from typing import Dict, Any
from src.solvers import SolverManager
from src.solvers.constraints import (
    DemandConstraint,
    SupplyConstraint,
    AllowedCombinationsConstraint,
    ProductionRateConstraint,
    MinimumBatchConstraint,
)

def create_test_data() -> Dict[str, Any]:
    """Create a simple test dataset."""
    return {
        'waffle_types': ['Plain', 'Chocolate'],
        'pan_types': ['Standard', 'Premium'],
        'weeks': [1, 2, 3],
        'demand': {
            ('Plain', 1): 10,
            ('Plain', 2): 15,
            ('Plain', 3): 20,
            ('Chocolate', 1): 5,
            ('Chocolate', 2): 10,
            ('Chocolate', 3): 15,
        },
        'supply': {
            ('Standard', 1): 20,
            ('Standard', 2): 25,
            ('Standard', 3): 30,
            ('Premium', 1): 10,
            ('Premium', 2): 15,
            ('Premium', 3): 20,
        },
        'wpp': {
            'Plain': 100,
            'Chocolate': 80,
        },
        'cost': {
            ('Plain', 'Standard'): 0.5,
            ('Plain', 'Premium'): 0.7,
            ('Chocolate', 'Standard'): 0.6,
            ('Chocolate', 'Premium'): 0.8,
        },
        'allowed': {
            ('Plain', 'Standard'): True,
            ('Plain', 'Premium'): True,
            ('Chocolate', 'Standard'): True,
            ('Chocolate', 'Premium'): True,
        }
    }

def test_solver_with_constraints(solver_name: str, data: Dict[str, Any]) -> None:
    """Test a solver with various constraints."""
    # Create solver manager
    manager = SolverManager()
    
    # Set up constraints
    manager.set_constraint_enabled('demand', True)
    manager.set_constraint_enabled('supply', True)
    manager.set_constraint_enabled('allowed_combinations', True)
    
    # Enable production rate constraint with custom configuration
    manager.set_constraint_enabled('production_rate', True)
    manager.set_constraint_configuration('production_rate', {'max_rate_change': 0.3})
    
    # Enable minimum batch constraint
    manager.set_constraint_enabled('minimum_batch', True)
    manager.set_constraint_configuration('minimum_batch', {'min_batch_size': 5})
    
    # Create solver with constraints
    solver = manager.create_solver(solver_name)
    
    # Build and solve model
    print(f"\nTesting {solver_name} solver with constraints...")
    
    # Minimize cost model
    print("Building minimize cost model...")
    solver.build_minimize_cost_model(data)
    
    print("Solving model...")
    start_time = time.time()
    result = solver.solve_model()
    solve_time = time.time() - start_time
    
    print(f"Solution status: {result['status']}")
    print(f"Solve time: {solve_time:.4f} seconds")
    
    if result['status'] in ['OPTIMAL', 'FEASIBLE']:
        print(f"Objective value: {result['objective_value']}")
        solution = solver.get_solution()
        print(f"Number of variables with non-zero values: {len(solution['values'])}")
    else:
        print("No solution found.")
    
    # Test with different constraint configurations
    print("\nTesting with different constraint configurations...")
    
    # Disable production rate constraint
    manager.set_constraint_enabled('production_rate', False)
    
    # Create new solver with updated constraints
    solver = manager.create_solver(solver_name)
    
    # Build and solve model
    print("Building minimize cost model without production rate constraint...")
    solver.build_minimize_cost_model(data)
    
    print("Solving model...")
    start_time = time.time()
    result = solver.solve_model()
    solve_time = time.time() - start_time
    
    print(f"Solution status: {result['status']}")
    print(f"Solve time: {solve_time:.4f} seconds")
    
    if result['status'] in ['OPTIMAL', 'FEASIBLE']:
        print(f"Objective value: {result['objective_value']}")
        solution = solver.get_solution()
        print(f"Number of variables with non-zero values: {len(solution['values'])}")
    else:
        print("No solution found.")
    
def main():
    """Main function to run the tests."""
    print("=== Testing Constraint System ===")
    test_data = create_test_data()
    
    # Test OR-Tools solver
    test_solver_with_constraints('ortools', test_data)
    
    # Test PuLP solver
    test_solver_with_constraints('cbc', test_data)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 