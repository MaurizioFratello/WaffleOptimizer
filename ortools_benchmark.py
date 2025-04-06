"""
OR-Tools Solver Benchmark Script for Waffle Production Optimization.

This script performs a focused benchmark of the OR-Tools solver
with different combinations of cumulative and equality parameters.
"""
import os
import time
import logging
from datetime import datetime
from typing import Dict, List
from tabulate import tabulate
from src.data.processor import DataProcessor
from src.solvers.solver_manager import SolverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ORToolsBenchmark:
    """Class to manage and run OR-Tools solver benchmarks."""
    
    def __init__(self):
        """Initialize the benchmark."""
        self.results = []
        self.configs = self._generate_configs()
        self.objectives = ['minimize_cost', 'maximize_output']
        
    def _generate_configs(self) -> List[Dict]:
        """Generate all constraint configurations to test."""
        configs = []
        
        # All combinations of cumulative and equality
        combinations = [
            {'cumulative': True, 'equality': True},
            {'cumulative': True, 'equality': False},
            {'cumulative': False, 'equality': True},
            {'cumulative': False, 'equality': False}
        ]
        
        for combo in combinations:
            config = {
                'demand': {'equality': combo['equality'], 'enabled': True},
                'supply': {'cumulative': combo['cumulative'], 'enabled': True},
                'allowed_combinations': {'enabled': True},
                'production_rate': {'enabled': False},
                'minimum_batch': {'enabled': False}
            }
            configs.append(config)
            
        return configs
    
    def _get_config_name(self, config: Dict, objective: str) -> str:
        """Generate a human-readable name for a configuration."""
        parts = []
        if config['demand'] and config['demand'].get('enabled', False):
            parts.append(f"equality={config['demand']['equality']}")
        if config['supply'] and config['supply'].get('enabled', False):
            parts.append(f"cumulative={config['supply']['cumulative']}")
        parts.append(f"obj={objective}")
        return ", ".join(parts)
    
    def _format_number(self, number: float) -> str:
        """Format a number with thousands separator and 2 decimal places."""
        if number is None:
            return "N/A"
        return f"{number:,.2f}"
    
    def run_benchmark(self, data: Dict, time_limit: int = 60) -> None:
        """Run the benchmark with the given data."""
        logger.info("Starting OR-Tools benchmark...")
        
        for objective in self.objectives:
            for config in self.configs:
                config_name = self._get_config_name(config, objective)
                logger.info(f"Testing configuration: {config_name}")
                
                try:
                    result = self._test_configuration(config, data, time_limit, objective)
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"Error testing configuration {config_name}: {str(e)}")
                    self.results.append({
                        'config': config_name,
                        'objective': objective,
                        'status': 'ERROR',
                        'error': str(e)
                    })
    
    def _test_configuration(self, config: Dict, data: Dict, time_limit: int, objective: str) -> Dict:
        """Test a single configuration."""
        solver_manager = SolverManager()
        
        # Configure constraints
        for constraint_type, constraint_config in config.items():
            # Set enabled status
            solver_manager.set_constraint_enabled(
                constraint_type, 
                constraint_config.get('enabled', False)
            )
            
            # If enabled, set configuration (excluding the 'enabled' flag)
            if constraint_config.get('enabled', False):
                config_copy = constraint_config.copy()
                config_copy.pop('enabled', None)
                if config_copy:  # Only set config if there are parameters
                    solver_manager.set_constraint_configuration(constraint_type, config_copy)
        
        # Create solver
        solver_instance = solver_manager.create_solver(
            solver_name='ortools',
            with_constraints=True,
            time_limit=time_limit
        )
        
        # Build and solve model
        start_time = time.time()
        if objective == 'minimize_cost':
            solver_instance.build_minimize_cost_model(data)
        else:
            solver_instance.build_maximize_output_model(data)
        solution_info = solver_instance.solve_model()
        end_time = time.time()
        
        # Get solution
        solution = solver_instance.get_solution() or {}
        
        # Extract metrics
        total_waffles = solution.get('total_waffles', 0)
        total_cost = solution.get('total_cost', 0)
        objective_value = solution_info.get('objective_value')
        status = solution_info.get('status', 'UNKNOWN')
        
        return {
            'config': self._get_config_name(config, objective),
            'objective': objective,
            'total_waffles': total_waffles,
            'total_cost': total_cost,
            'objective_value': objective_value,
            'solve_time': end_time - start_time,
            'status': status
        }
    
    def print_results(self) -> None:
        """Print the benchmark results in a formatted table."""
        print("\n=== OR-TOOLS SOLVER BENCHMARK RESULTS ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Default Data Set\n")
        
        # Print results for each objective
        for objective in self.objectives:
            print(f"\n[{objective.upper()}]")
            print("-" * 100)
            
            # Filter results for this objective
            objective_results = [r for r in self.results if r.get('objective') == objective]
            
            # Create table data
            table_data = []
            for result in objective_results:
                if 'error' in result:
                    table_data.append([
                        result['config'],
                        'ERROR',
                        'ERROR',
                        'ERROR',
                        'ERROR',
                        result['error']
                    ])
                else:
                    table_data.append([
                        result['config'],
                        self._format_number(result['total_waffles']),
                        self._format_number(result['total_cost']),
                        self._format_number(result['objective_value']),
                        f"{result['solve_time']:.1f}s",
                        result['status']
                    ])
            
            # Print table
            headers = ["Configuration", "Total Waffles", "Total Cost", "Objective Value", "Time", "Status"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print a summary of the results."""
        print("\n=== SUMMARY ===")
        
        for objective in self.objectives:
            print(f"\n[{objective.upper()}]")
            # Find best result for this objective
            valid_results = [
                r for r in self.results 
                if 'error' not in r and r['status'] == 'OPTIMAL' and r['objective'] == objective
            ]
            if valid_results:
                if objective == 'minimize_cost':
                    best_result = min(valid_results, key=lambda x: x['total_cost'])
                else:
                    best_result = max(valid_results, key=lambda x: x['total_waffles'])
                print("Best result:")
                print(f"  - Configuration: {best_result['config']}")
                print(f"  - Total Cost: ${self._format_number(best_result['total_cost'])}")
                print(f"  - Total Waffles: {self._format_number(best_result['total_waffles'])}")
                print(f"  - Objective Value: {self._format_number(best_result['objective_value'])}")
                print(f"  - Solve Time: {best_result['solve_time']:.1f}s")

def main():
    """Main function to run the benchmark."""
    # Load default data
    data_processor = DataProcessor(debug_mode=True)
    data_folder = "data/input"
    data_processor.load_data(
        demand_file=os.path.join(data_folder, "WaffleDemand.xlsx"),
        supply_file=os.path.join(data_folder, "PanSupply.xlsx"),
        cost_file=os.path.join(data_folder, "WaffleCostPerPan.xlsx"),
        wpp_file=os.path.join(data_folder, "WafflesPerPan.xlsx"),
        combinations_file=os.path.join(data_folder, "WafflePanCombinations.xlsx")
    )
    data = data_processor.get_optimization_data()
    
    # Run benchmark
    benchmark = ORToolsBenchmark()
    benchmark.run_benchmark(data)
    benchmark.print_results()

if __name__ == "__main__":
    main() 