"""
Test module for analyzing the impact of constraints on optimization results.

This module contains tests that systematically disable constraints to evaluate
their impact on the optimization model's objective value and solution feasibility.
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

class TestConstraintImpact(unittest.TestCase):
    """Test class for analyzing constraint impact on optimization results."""
    
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
        
        # Analyze cumulative demand and supply
        cls._analyze_cumulative_data()
        
        # Define test configurations
        cls.test_configurations = [
            {"name": "All Constraints", "disabled": []},
            {"name": "No Demand", "disabled": ["demand"]},
            {"name": "No Supply", "disabled": ["supply"]},
            {"name": "No Demand & No Supply", "disabled": ["demand", "supply"]}
        ]
    
    @classmethod
    def _analyze_cumulative_data(cls):
        """Analyze and display cumulative demand and supply data."""
        logger.info("\n=== Cumulative Demand and Supply Analysis ===")
        logger.info(f"{'Week':<10} {'Weekly Demand':<15} {'Cumulative Demand':<20} "
                   f"{'Weekly Supply':<15} {'Cumulative Supply':<20} {'Buffer %':<10}")
        logger.info("-" * 90)
        
        cumulative_demand = 0
        cumulative_supply = 0
        
        for week in sorted(cls.optimization_data['weeks']):
            # Calculate weekly demand
            weekly_demand = sum(
                cls.optimization_data['demand'].get((w, week), 0)
                for w in cls.optimization_data['waffle_types']
            )
            cumulative_demand += weekly_demand
            
            # Calculate weekly supply
            weekly_supply = sum(
                cls.optimization_data['supply'].get((p, week), 0)
                for p in cls.optimization_data['pan_types']
            )
            cumulative_supply += weekly_supply
            
            # Calculate buffer percentage
            buffer_percentage = (cumulative_supply / cumulative_demand * 100) if cumulative_demand > 0 else float('inf')
            
            logger.info(f"{week:<10} {weekly_demand:<15.2f} {cumulative_demand:<20.2f} "
                       f"{weekly_supply:<15.2f} {cumulative_supply:<20.2f} {buffer_percentage:<10.2f}%")
        
        # Add total row
        total_buffer = (cumulative_supply / cumulative_demand * 100) if cumulative_demand > 0 else float('inf')
        logger.info("-" * 90)
        logger.info(f"{'TOTAL':<10} {'-':<15} {cumulative_demand:<20.2f} "
                   f"{'-':<15} {cumulative_supply:<20.2f} {total_buffer:<10.2f}%")
    
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