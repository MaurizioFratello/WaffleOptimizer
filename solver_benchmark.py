"""
Solver Benchmark Script for Waffle Production Optimization.

This script performs a comprehensive benchmark of all available solvers
with different constraint configurations and objective functions.
"""
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from tabulate import tabulate
from src.data.processor import DataProcessor
from src.solvers.solver_manager import SolverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SolverBenchmark:
    """Class to manage and run solver benchmarks."""
    
    def __init__(self):
        """Initialize the benchmark."""
        self.results = []
        self.solvers = ['ortools', 'pulp', 'cbc', 'glpk', 'scip', 'coin_cmd']
        self.objectives = ['minimize_cost', 'maximize_output']
        self.constraint_configs = self._generate_constraint_configs()
        
    def _generate_constraint_configs(self) -> List[Dict]:
        """Generate all constraint configurations to test."""
        configs = []
        
        # Base configurations
        base_configs = [
            # All constraints off
            {
                'demand': None,
                'supply': None,
                'allowed_combinations': None,
                'production_rate': None,
                'minimum_batch': None
            },
            # All constraints on with default config
            {
                'demand': {'equality': True},
                'supply': {'cumulative': True},
                'allowed_combinations': {},
                'production_rate': {'max_rate_change': 0.2},
                'minimum_batch': {'min_batch_size': 10}
            }
        ]
        
        # Special configurations for demand.equality and supply.cumulative
        special_configs = [
            {'demand': {'equality': True}, 'supply': {'cumulative': False}},
            {'demand': {'equality': True}, 'supply': {'cumulative': True}},
            {'demand': {'equality': False}, 'supply': {'cumulative': True}},
            {'demand': {'equality': False}, 'supply': {'cumulative': False}}
        ]
        
        # Combine all configurations
        configs.extend(base_configs)
        for special in special_configs:
            config = {
                'demand': special.get('demand', {'equality': True}),
                'supply': special.get('supply', {'cumulative': True}),
                'allowed_combinations': {},
                'production_rate': None,
                'minimum_batch': None
            }
            configs.append(config)
            
        return configs
    
    def _get_config_name(self, config: Dict) -> str:
        """Generate a human-readable name for a configuration."""
        if all(v is None for v in config.values()):
            return "All Constraints OFF"
        elif all(v is not None for v in config.values()):
            return "All Constraints ON"
        else:
            parts = []
            if config['demand']:
                parts.append(f"demand.equality={config['demand']['equality']}")
            if config['supply']:
                parts.append(f"supply.cumulative={config['supply']['cumulative']}")
            return ", ".join(parts)
    
    def _format_number(self, number: float) -> str:
        """Format a number with thousands separator and 2 decimal places."""
        return f"{number:,.2f}"
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to a readable string."""
        return f"{seconds:.1f}s"
    
    def run_benchmark(self, data: Dict, time_limit: int = 60) -> None:
        """Run the benchmark with the given data."""
        logger.info("Starting solver benchmark...")
        
        for solver in self.solvers:
            for objective in self.objectives:
                for config in self.constraint_configs:
                    config_name = self._get_config_name(config)
                    logger.info(f"Testing {solver} with {objective} and {config_name}")
                    
                    try:
                        result = self._test_configuration(
                            solver, objective, config, data, time_limit
                        )
                        self.results.append(result)
                    except Exception as e:
                        logger.error(f"Error testing {solver} with {config_name}: {str(e)}")
                        self.results.append({
                            'solver': solver,
                            'objective': objective,
                            'config': config_name,
                            'status': 'ERROR',
                            'error': str(e)
                        })
    
    def _test_configuration(self, solver: str, objective: str, config: Dict, 
                          data: Dict, time_limit: int) -> Dict:
        """Test a single configuration."""
        solver_manager = SolverManager()
        
        # Configure constraints
        for constraint_type, constraint_config in config.items():
            if constraint_config is None:
                solver_manager.set_constraint_enabled(constraint_type, False)
            else:
                solver_manager.set_constraint_enabled(constraint_type, True)
                solver_manager.set_constraint_configuration(constraint_type, constraint_config)
        
        # Create solver
        solver_instance = solver_manager.create_solver(
            solver_name=solver,
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
        status = solution_info.get('status', 'UNKNOWN')
        
        return {
            'solver': solver,
            'objective': objective,
            'config': self._get_config_name(config),
            'total_waffles': total_waffles,
            'total_cost': total_cost,
            'solve_time': end_time - start_time,
            'status': status
        }
    
    def print_results(self) -> None:
        """Print the benchmark results in a formatted table."""
        print("\n=== WAFFLE OPTIMIZATION BENCHMARK RESULTS ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Default Data Set\n")
        
        # Group results by objective
        for objective in self.objectives:
            print(f"[{objective.upper()} OBJECTIVE]")
            print("-" * 80)
            
            # Group by solver
            for solver in self.solvers:
                print(f"\nSolver: {solver}")
                print(" " * 37 + "Total Waffles    Total Cost    Time    Status")
                print("-" * 80)
                
                # Filter and sort results
                solver_results = [
                    r for r in self.results 
                    if r['solver'] == solver and r['objective'] == objective
                ]
                solver_results.sort(key=lambda x: x['config'])
                
                # Print results
                for result in solver_results:
                    if 'error' in result:
                        print(f"{result['config']:<35} {'ERROR':>15} {'ERROR':>12} {'ERROR':>8} {result['error']}")
                    else:
                        print(f"{result['config']:<35} "
                              f"{self._format_number(result['total_waffles']):>15} "
                              f"{self._format_number(result['total_cost']):>12} "
                              f"{self._format_time(result['solve_time']):>8} "
                              f"{result['status']}")
            
            print("\n")
        
        # Print summary
        self._print_summary()
        
        # Print solver performance comparison
        self._print_performance_comparison()
    
    def _print_summary(self) -> None:
        """Print a summary of the best results."""
        print("=== SUMMARY ===")
        
        # Best cost minimization
        cost_results = [r for r in self.results if r['objective'] == 'minimize_cost' and 'error' not in r]
        if cost_results:
            best_cost = min(cost_results, key=lambda x: x['total_cost'])
            print("Best cost minimization result:")
            print(f"  - Solver: {best_cost['solver']}")
            print(f"  - Configuration: {best_cost['config']}")
            print(f"  - Total Cost: ${self._format_number(best_cost['total_cost'])}")
            print(f"  - Total Waffles: {self._format_number(best_cost['total_waffles'])}")
        
        # Best output maximization
        output_results = [r for r in self.results if r['objective'] == 'maximize_output' and 'error' not in r]
        if output_results:
            best_output = max(output_results, key=lambda x: x['total_waffles'])
            print("\nBest output maximization result:")
            print(f"  - Solver: {best_output['solver']}")
            print(f"  - Configuration: {best_output['config']}")
            print(f"  - Total Waffles: {self._format_number(best_output['total_waffles'])}")
            print(f"  - Total Cost: ${self._format_number(best_output['total_cost'])}")
    
    def _print_performance_comparison(self) -> None:
        """Print solver performance comparison."""
        print("\n=== SOLVER PERFORMANCE COMPARISON ===")
        print("Average solve time:")
        
        # Calculate average solve time for each solver
        solver_times = {}
        for solver in self.solvers:
            solver_results = [r for r in self.results if r['solver'] == solver and 'error' not in r]
            if solver_results:
                avg_time = sum(r['solve_time'] for r in solver_results) / len(solver_results)
                solver_times[solver] = avg_time
        
        # Sort solvers by average time
        sorted_solvers = sorted(solver_times.items(), key=lambda x: x[1])
        
        # Print results
        for i, (solver, avg_time) in enumerate(sorted_solvers, 1):
            print(f"  {i}. {solver:<10} {self._format_time(avg_time)}")

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
    benchmark = SolverBenchmark()
    benchmark.run_benchmark(data)
    benchmark.print_results()

if __name__ == "__main__":
    main() 