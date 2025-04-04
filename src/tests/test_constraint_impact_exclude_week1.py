"""
Test module for analyzing the impact of constraints on optimization results,
excluding week 1 from both demand and supply data.
"""
import os
import sys
import time
import unittest
import logging
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.processor import DataProcessor
from solvers.solver_manager import SolverManager

# Set up logging
logger = logging.getLogger(__name__)

class TestConstraintImpactExcludeWeek1(unittest.TestCase):
    """Test class for analyzing constraint impact on optimization results, excluding week 1."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data and configuration."""
        logger.info("Setting up test environment...")
        
        # Define input file paths
        input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "input")
        cls.input_files = {
            'demand_file': os.path.join(input_dir, "WaffleDemand.xlsx"),
            'supply_file': os.path.join(input_dir, "PanSupply.xlsx"),
            'cost_file': os.path.join(input_dir, "WaffleCostPerPan.xlsx"),
            'wpp_file': os.path.join(input_dir, "WafflesPerPan.xlsx"),
            'combinations_file': os.path.join(input_dir, "WafflePanCombinations.xlsx")
        }
        
        # Validate input files exist
        for file_type, file_path in cls.input_files.items():
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found: {file_path}")
            logger.info(f"Found {file_type}: {os.path.basename(file_path)}")
        
        # Create data processor and load default data
        cls.data_processor = DataProcessor(debug_mode=True)
        logger.info("Loading default data...")
        cls.data_processor.load_data(**cls.input_files)
        
        # Get optimization data
        cls.optimization_data = cls.data_processor.get_optimization_data()
        
        # Log initial weeks
        logger.info(f"Initial weeks in data: {sorted(cls.optimization_data['weeks'])}")
        
        # Log initial demand weeks
        demand_weeks = sorted(set(week for _, week in cls.optimization_data['demand'].keys()))
        logger.info(f"Initial demand weeks: {demand_weeks}")
        
        # Log initial supply weeks
        supply_weeks = sorted(set(week for _, week in cls.optimization_data['supply'].keys()))
        logger.info(f"Initial supply weeks: {supply_weeks}")
        
        # Exclude week 1 from both demand and supply
        logger.info("Excluding week 1 from demand and supply data...")
        weeks = sorted(cls.optimization_data['weeks'])
        if 1 in weeks:
            weeks.remove(1)
            cls.optimization_data['weeks'] = weeks
            
            # Remove week 1 from demand
            demand = cls.optimization_data['demand']
            cls.optimization_data['demand'] = {k: v for k, v in demand.items() if k[1] != 1}
            
            # Remove week 1 from supply
            supply = cls.optimization_data['supply']
            cls.optimization_data['supply'] = {k: v for k, v in supply.items() if k[1] != 1}
        
        # Log final weeks
        logger.info(f"Final weeks in data: {sorted(cls.optimization_data['weeks'])}")
        
        # Log final demand weeks
        demand_weeks = sorted(set(week for _, week in cls.optimization_data['demand'].keys()))
        logger.info(f"Final demand weeks: {demand_weeks}")
        
        # Log final supply weeks
        supply_weeks = sorted(set(week for _, week in cls.optimization_data['supply'].keys()))
        logger.info(f"Final supply weeks: {supply_weeks}")
    
    def setUp(self):
        """Set up before each test."""
        self.solver_manager = SolverManager()
        
        # Disable all constraints by default
        for constraint_type in self.solver_manager.get_available_constraints():
            self.solver_manager.set_constraint_enabled(constraint_type, False)
        
        # Enable only Demand, Supply, and Allowed Combinations constraints
        self.solver_manager.set_constraint_enabled('demand', True)
        self.solver_manager.set_constraint_enabled('supply', True)
        self.solver_manager.set_constraint_enabled('allowed_combinations', True)
    
    def test_all_constraint_combinations(self):
        """Test all possible combinations of constraint settings."""
        logger.info("Starting comprehensive constraint settings analysis...")
        
        # Define all combinations to test
        settings_combinations = [
            {"demand_equality": True, "supply_cumulative": True},
            {"demand_equality": True, "supply_cumulative": False},
            {"demand_equality": False, "supply_cumulative": True},
            {"demand_equality": False, "supply_cumulative": False}
        ]
        
        results = []
        
        for settings in settings_combinations:
            logger.info(f"\nTesting combination: Demand equality={settings['demand_equality']}, "
                       f"Supply cumulative={settings['supply_cumulative']}")
            
            # Set constraint configurations
            self.solver_manager.set_constraint_configuration('demand', {'equality': settings['demand_equality']})
            self.solver_manager.set_constraint_configuration('supply', {'cumulative': settings['supply_cumulative']})
            
            # Create a solver with the configured constraints
            solver = self.solver_manager.create_solver("ortools", time_limit=60)
            
            # Build minimize cost model
            logger.info("  Building minimize cost model...")
            solver.build_minimize_cost_model(self.optimization_data)
            
            # Solve model
            logger.info("  Solving optimization model...")
            start_time = time.time()
            solution_info = solver.solve_model()
            solve_time = time.time() - start_time
            
            status = solution_info.get('status', 'UNKNOWN')
            objective_value = solution_info.get('objective_value', None)
            
            # Store results
            result = {
                "demand_equality": settings['demand_equality'],
                "supply_cumulative": settings['supply_cumulative'],
                "status": status,
                "objective_value": objective_value,
                "solve_time": solve_time
            }
            results.append(result)
            
            logger.info(f"  Status: {status}")
            logger.info(f"  Objective value: {objective_value}")
            logger.info(f"  Solve time: {solve_time:.4f} seconds")
        
        # Display results in tabular form
        logger.info("\n=== Comprehensive Results ===")
        logger.info(f"{'Demand Equality':<15} {'Supply Cumulative':<15} {'Status':<12} "
                   f"{'Objective Value':<20} {'Solve Time (s)':<15}")
        logger.info("-" * 77)
        
        for result in results:
            obj_value = result['objective_value']
            obj_str = f"{obj_value:.2f}" if obj_value is not None else "N/A"
            logger.info(f"{str(result['demand_equality']):<15} {str(result['supply_cumulative']):<15} "
                       f"{result['status']:<12} {obj_str:<20} {result['solve_time']:<15.4f}")

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main() 