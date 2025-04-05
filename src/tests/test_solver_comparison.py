"""
Test module to compare solver performance with different supply constraint configurations.
"""
import os
import logging
from typing import Dict, Any
from src.solvers.solver_manager import SolverManager
from src.data.processor import DataProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_test_data() -> Dict:
    """
    Load test data from the default Excel files.
    
    Returns:
        Dict: Dictionary containing optimization data
    """
    # Assuming data files are in a 'data' directory at the project root
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'input')
    
    processor = DataProcessor(debug_mode=True)
    processor.load_data(
        demand_file=os.path.join(data_dir, 'WaffleDemand.xlsx'),
        supply_file=os.path.join(data_dir, 'PanSupply.xlsx'),
        cost_file=os.path.join(data_dir, 'WaffleCostPerPan.xlsx'),
        wpp_file=os.path.join(data_dir, 'WafflesPerPan.xlsx'),
        combinations_file=os.path.join(data_dir, 'WafflePanCombinations.xlsx')
    )
    
    return processor.get_optimization_data()

def run_solver_comparison():
    """
    Run comparison test for all solvers with different supply constraint configurations.
    """
    # Available solvers
    solvers = ['ortools', 'cbc', 'glpk', 'scip', 'coin_cmd']
    
    # Supply constraint configurations to test
    configs = [
        {'cumulative': True},
        {'cumulative': False}
    ]
    
    # Load test data
    try:
        data = load_test_data()
    except Exception as e:
        logger.error(f"Failed to load test data: {str(e)}")
        return
    
    # Results storage
    results = []
    
    # Test each solver with each configuration
    for solver_name in solvers:
        for config in configs:
            try:
                # Create solver manager
                solver_manager = SolverManager()
                
                # Configure supply constraint
                solver_manager.set_constraint_configuration('supply', config)
                
                logger.info(f"\nTesting {solver_name} solver with supply.cumulative = {config['cumulative']}")
                
                # Create and configure solver
                solver = solver_manager.create_solver(solver_name)
                
                # Build and solve model
                solver.build_minimize_cost_model(data)
                solution_info = solver.solve_model()
                
                # Get detailed solution
                solution = solver.get_solution()
                
                # Store results
                result = {
                    'solver': solver_name,
                    'cumulative': config['cumulative'],
                    'status': solution_info['status'],
                    'solve_time': solution_info['solve_time'],
                    'objective_value': solution_info['objective_value'],
                    'non_zero_vars': len(solution['values']) if 'values' in solution else 0
                }
                results.append(result)
                
                # Log detailed results
                logger.info(f"Status: {result['status']}")
                logger.info(f"Solve time: {result['solve_time']:.3f} seconds")
                logger.info(f"Objective value: {result['objective_value']}")
                logger.info(f"Non-zero variables: {result['non_zero_vars']}")
                
            except Exception as e:
                logger.error(f"Error testing {solver_name} with cumulative={config['cumulative']}: {str(e)}")
                results.append({
                    'solver': solver_name,
                    'cumulative': config['cumulative'],
                    'status': 'ERROR',
                    'error': str(e)
                })
    
    # Print summary table
    logger.info("\n=== Summary Results ===")
    logger.info(f"{'Solver':<12} {'Cumulative':<10} {'Status':<12} {'Time (s)':<10} {'Objective':<15} {'Non-zero vars':<15}")
    logger.info("-" * 74)
    
    for result in results:
        status = result.get('status', 'N/A')
        time = f"{result.get('solve_time', 'N/A'):,.3f}" if 'solve_time' in result else 'N/A'
        obj = f"{result.get('objective_value', 'N/A'):,.2f}" if 'objective_value' in result else 'N/A'
        vars = str(result.get('non_zero_vars', 'N/A'))
        
        logger.info(f"{result['solver']:<12} {str(result['cumulative']):<10} {status:<12} {time:<10} {obj:<15} {vars:<15}")

if __name__ == '__main__':
    run_solver_comparison() 