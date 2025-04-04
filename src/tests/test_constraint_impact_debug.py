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
from solvers.constraints.supply_constraint import SupplyConstraint

# Set up logging with higher level of detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestConstraintImpactDebug(unittest.TestCase):
    """Test class for analyzing constraint impact with detailed diagnostic information."""
    
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
    
    def test_week3_supply_constraint_detail(self):
        """
        Detailed test specifically focused on Week 3 with non-cumulative supply.
        This test adds detailed diagnostic information to understand why the model
        is feasible when it should be infeasible.
        """
        logger.info("\n=== Testing Week 3 Supply Constraint in Detail ===")
        
        # Directly create a non-cumulative constraint to verify it works correctly
        test_constraint = SupplyConstraint(cumulative=False)
        logger.info(f"Direct constraint creation - cumulative setting: {test_constraint.cumulative}")
        self.assertFalse(test_constraint.cumulative, "SupplyConstraint constructor should set cumulative=False")
        
        # Set supply constraint to non-cumulative through solver manager
        self.solver_manager.set_constraint_configuration('supply', {'cumulative': False})
        
        # Verify the configuration is set correctly in the solver manager
        supply_config = self.solver_manager.get_constraint_configuration('supply')
        logger.info(f"SolverManager supply config: {supply_config}")
        self.assertFalse(supply_config.get('cumulative', True), "SolverManager should set cumulative=False")
        
        # Create a solver with the configured constraints
        solver = self.solver_manager.create_solver("ortools", time_limit=60)
        
        # Get the actual constraint object to verify its settings
        supply_constraint = solver.get_constraint('supply')
        if supply_constraint is None:
            self.fail("Supply constraint was not added to the solver")
        
        logger.info(f"Supply constraint object type: {type(supply_constraint)}")
        logger.info(f"Supply constraint cumulative setting: {supply_constraint.cumulative}")
        self.assertFalse(supply_constraint.cumulative, "Supply constraint should be non-cumulative")
        
        # Analyze Week 3 data
        week3 = "Week 3"
        
        # Get Week 3 supply
        week3_supply = sum(
            self.optimization_data['supply'].get((p, week3), 0)
            for p in self.optimization_data['pan_types']
        )
        
        # Get Week 3 demand
        week3_demand = sum(
            self.optimization_data['demand'].get((w, week3), 0)
            for w in self.optimization_data['waffle_types']
        )
        
        logger.info(f"Week 3 total supply: {week3_supply} pans")
        logger.info(f"Week 3 total demand: {week3_demand} pans")
        
        # Check if Week 3 key format is consistent
        logger.info(f"Week 3 key used for lookup: {repr(week3)}")
        
        # Show all keys in demand and supply to verify format
        demand_weeks = sorted(set(week for _, week in self.optimization_data['demand'].keys()))
        supply_weeks = sorted(set(week for _, week in self.optimization_data['supply'].keys()))
        
        logger.info(f"All demand weeks: {demand_weeks}")
        logger.info(f"All supply weeks: {supply_weeks}")
        
        # Detailed supply by pan type
        logger.info(f"Detailed supply for Week 3:")
        for p in self.optimization_data['pan_types']:
            supply = self.optimization_data['supply'].get((p, week3), 0)
            if supply > 0:
                logger.info(f"  {p}: {supply} pans")
        
        # Detailed demand by waffle type
        logger.info(f"Detailed demand for Week 3:")
        for w in self.optimization_data['waffle_types']:
            demand = self.optimization_data['demand'].get((w, week3), 0)
            if demand > 0:
                logger.info(f"  {w}: {demand} pans")
        
        # Check expected infeasibility condition
        if week3_demand > week3_supply:
            logger.info(f"Model should be INFEASIBLE: Week 3 demand ({week3_demand}) > Week 3 supply ({week3_supply})")
        
        # Build minimize cost model
        logger.info("Building minimize cost model...")
        solver.build_minimize_cost_model(self.optimization_data)
        
        # Check application of constraints in the model
        supply_constraint = solver.get_constraint('supply')
        demand_constraint = solver.get_constraint('demand')
        
        logger.info(f"Supply constraint in solver after build: {supply_constraint}")
        logger.info(f"Supply constraint cumulative after build: {supply_constraint.cumulative}")
        logger.info(f"Demand constraint equality setting: {getattr(demand_constraint, 'equality', None)}")
        
        # Solve model
        logger.info("Solving optimization model...")
        start_time = time.time()
        solution_info = solver.solve_model()
        solve_time = time.time() - start_time
        
        status = solution_info.get('status', 'UNKNOWN')
        objective_value = solution_info.get('objective_value', None)
        
        logger.info(f"Status: {status}")
        logger.info(f"Objective value: {objective_value}")
        logger.info(f"Solve time: {solve_time:.4f} seconds")
        
        # If the model is feasible when it should be infeasible, analyze the solution
        if status == 'OPTIMAL' and week3_demand > week3_supply:
            logger.warning("Model is OPTIMAL when it should be INFEASIBLE!")
            
            # Get detailed solution
            solution = solver.get_solution()
            
            # Analyze week 3 usage
            week3_usage = 0
            week3_usage_by_pan = {}
            
            for (w, p, week), value in solution.get('values', {}).items():
                if week == week3 and value > 0:
                    week3_usage += value
                    week3_usage_by_pan[p] = week3_usage_by_pan.get(p, 0) + value
            
            logger.info(f"Solution uses {week3_usage} pans in Week 3 (available: {week3_supply})")
            
            for p, usage in week3_usage_by_pan.items():
                supply = self.optimization_data['supply'].get((p, week3), 0)
                logger.info(f"  Pan {p}: using {usage} of {supply} available")
            
            # Check for constraint violation
            if week3_usage > week3_supply:
                logger.error(f"CONSTRAINT VIOLATION: Week 3 usage ({week3_usage}) > Week 3 supply ({week3_supply})")
                self.fail(f"Non-cumulative supply constraint violated: {week3_usage} > {week3_supply}")
        
        # Check for expected infeasibility
        if week3_demand > week3_supply:
            self.assertEqual(status, "INFEASIBLE", 
                            f"Model should be INFEASIBLE: Week 3 demand ({week3_demand}) > Week 3 supply ({week3_supply})")
    
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
            
            # Verify constraint configurations were set correctly
            supply_config = self.solver_manager.get_constraint_configuration('supply')
            demand_config = self.solver_manager.get_constraint_configuration('demand')
            
            logger.info(f"  SolverManager supply config: {supply_config}")
            logger.info(f"  SolverManager demand config: {demand_config}")
            
            # Create a solver with the configured constraints
            solver = self.solver_manager.create_solver("ortools", time_limit=60)
            
            # Verify constraint settings in actual constraint objects
            supply_constraint = solver.get_constraint('supply')
            demand_constraint = solver.get_constraint('demand')
            
            if supply_constraint:
                logger.info(f"  Supply constraint cumulative: {supply_constraint.cumulative}")
            if demand_constraint:
                logger.info(f"  Demand constraint equality: {getattr(demand_constraint, 'equality', None)}")
            
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
            
            # Check for unexpected feasibility
            week3 = "Week 3"
            week3_supply = sum(
                self.optimization_data['supply'].get((p, week3), 0)
                for p in self.optimization_data['pan_types']
            )
            week3_demand = sum(
                self.optimization_data['demand'].get((w, week3), 0)
                for w in self.optimization_data['waffle_types']
            )
            
            if not settings['supply_cumulative'] and week3_demand > week3_supply and status == 'OPTIMAL':
                logger.warning(f"  UNEXPECTED FEASIBILITY: non-cumulative supply should be infeasible")
                logger.warning(f"  Week 3 demand: {week3_demand}, Week 3 supply: {week3_supply}")
        
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
    # Run tests
    unittest.main() 