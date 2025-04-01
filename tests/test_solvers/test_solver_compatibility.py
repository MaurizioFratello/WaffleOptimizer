"""
Test solver compatibility with default configuration values.
"""
import unittest
import os
import sys
from src.solvers.base import SolverFactory
from src.data.processor import DataProcessor
from src.data.validator import DataValidator

class TestSolverCompatibility(unittest.TestCase):
    """Test class for checking solver compatibility with default values."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data and configuration."""
        # Default configuration
        cls.config = {
            'objective': 'cost',
            'demand': 'data/input/WaffleDemand.xlsx',
            'supply': 'data/input/PanSupply.xlsx',
            'cost': 'data/input/WaffleCostPerPan.xlsx',
            'wpp': 'data/input/WafflesPerPan.xlsx',
            'combinations': 'data/input/WafflePanCombinations.xlsx',
            'time_limit': 10,
            'gap': 0.005,
            'limit_to_demand': False,
            'debug': True
        }
        
        # Available solvers to test
        cls.solvers = [
            'ortools',
            'cbc',
            'glpk',
            'scip',
            'coin_cmd'
        ]
        
        # Load data once for all tests
        cls.data_processor = DataProcessor(debug_mode=True)
        cls.data_processor.load_data(
            demand_file=cls.config['demand'],
            supply_file=cls.config['supply'],
            cost_file=cls.config['cost'],
            wpp_file=cls.config['wpp'],
            combinations_file=cls.config['combinations']
        )
        cls.optimization_data = cls.data_processor.get_optimization_data()
        
        # Initialize validator
        cls.data_validator = DataValidator(debug_mode=True)
        
        # Check basic feasibility
        is_feasible, critical_issues, warnings = cls.data_validator.check_basic_feasibility(cls.optimization_data)
        if not is_feasible:
            raise RuntimeError(f"Test data is not feasible: {critical_issues}")

    def test_solver_compatibility(self):
        """Test each solver with default configuration."""
        results = []
        
        for solver_name in self.solvers:
            try:
                # Create solver
                solver = SolverFactory.create_solver(
                    solver_name=solver_name,
                    time_limit=self.config['time_limit'],
                    optimality_gap=self.config['gap']
                )
                
                # Build and solve model
                solver.build_minimize_cost_model(self.optimization_data)
                solution_info = solver.solve_model()
                
                # Check if solution is feasible
                self.assertTrue(solution_info['is_feasible'], 
                              f"Solver {solver_name} failed to find a feasible solution")
                
                # Get solution
                solution = solver.get_solution()
                
                # Validate solution
                validation = self.data_validator.validate_solution(
                    self.optimization_data, solution)
                
                # Record successful solver
                results.append({
                    'solver': solver_name,
                    'status': 'success',
                    'solution_time': solution_info['solution_time'],
                    'objective_value': solution.get('objective_value', None)
                })
                
            except Exception as e:
                # Record failed solver
                results.append({
                    'solver': solver_name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Print results
        print("\n=== Solver Compatibility Test Results ===")
        print("\nWorking Solvers:")
        for result in results:
            if result['status'] == 'success':
                print(f"- {result['solver']}:")
                print(f"  Solution time: {result['solution_time']:.2f} seconds")
                if result['objective_value'] is not None:
                    print(f"  Objective value: {result['objective_value']:.2f}")
        
        print("\nFailed Solvers:")
        for result in results:
            if result['status'] == 'failed':
                print(f"- {result['solver']}:")
                print(f"  Error: {result['error']}")
        
        # Assert that at least one solver works
        working_solvers = [r for r in results if r['status'] == 'success']
        self.assertTrue(len(working_solvers) > 0, 
                       "No solvers were able to solve the problem with default configuration")

if __name__ == '__main__':
    unittest.main() 