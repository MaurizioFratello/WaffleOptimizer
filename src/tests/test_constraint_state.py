"""
Test script for verifying constraint state management in the solver system.
"""
import sys
import os
from pathlib import Path
import logging
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.solvers.solver_manager import SolverManager
from src.solvers.constraints import (
    DemandConstraint,
    SupplyConstraint,
    AllowedCombinationsConstraint,
    ProductionRateConstraint,
    MinimumBatchConstraint,
)

def create_test_data() -> Dict[str, Any]:
    """Create test data for the optimization model."""
    return {
        'waffle_types': ['W1', 'W2'],
        'pan_types': ['P1', 'P2'],
        'weeks': ['Week1', 'Week2'],
        'demand': {
            ('W1', 'Week1'): 100,
            ('W1', 'Week2'): 150,
            ('W2', 'Week1'): 200,
            ('W2', 'Week2'): 250
        },
        'supply': {
            ('P1', 'Week1'): 50,
            ('P1', 'Week2'): 60,
            ('P2', 'Week1'): 70,
            ('P2', 'Week2'): 80
        },
        'allowed': {
            ('W1', 'P1'): True,
            ('W1', 'P2'): True,
            ('W2', 'P1'): True,
            ('W2', 'P2'): True
        },
        'wpp': {
            'W1': 10,
            'W2': 15
        },
        'cost': {
            ('W1', 'P1'): 1.0,
            ('W1', 'P2'): 1.2,
            ('W2', 'P1'): 1.5,
            ('W2', 'P2'): 1.8
        }
    }

def test_constraint_state_changes():
    """Test that constraint state changes are properly reflected in the solver."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Create solver manager
    solver_manager = SolverManager()
    
    # Create test data
    data = create_test_data()
    
    # Test 1: Default constraints enabled
    logger.info("Test 1: Default constraints enabled")
    solver = solver_manager.create_solver('ortools')
    solver.build_minimize_cost_model(data)
    solver.apply_constraints()
    constraints = solver.get_all_constraints()
    # By default, only demand, supply, and allowed_combinations are enabled
    assert len(constraints) == 3, "Expected 3 constraints by default"
    assert 'demand' in constraints, "Demand constraint should be present"
    assert 'supply' in constraints, "Supply constraint should be present"
    assert 'allowed_combinations' in constraints, "Allowed combinations constraint should be present"
    
    # Test 2: Disable demand constraint
    logger.info("Test 2: Disable demand constraint")
    solver_manager.set_constraint_enabled('demand', False)
    solver = solver_manager.create_solver('ortools')
    solver.build_minimize_cost_model(data)
    solver.apply_constraints()
    constraints = solver.get_all_constraints()
    assert len(constraints) == 2, "Expected 2 constraints after disabling demand"
    assert 'demand' not in constraints, "Demand constraint should not be present"
    assert 'supply' in constraints, "Supply constraint should be present"
    assert 'allowed_combinations' in constraints, "Allowed combinations constraint should be present"
    
    # Test 3: Re-enable demand constraint
    logger.info("Test 3: Re-enable demand constraint")
    solver_manager.set_constraint_enabled('demand', True)
    solver = solver_manager.create_solver('ortools')
    solver.build_minimize_cost_model(data)
    solver.apply_constraints()
    constraints = solver.get_all_constraints()
    assert len(constraints) == 3, "Expected 3 constraints after re-enabling demand"
    assert 'demand' in constraints, "Demand constraint should be present"
    assert 'supply' in constraints, "Supply constraint should be present"
    assert 'allowed_combinations' in constraints, "Allowed combinations constraint should be present"
    
    # Test 4: Enable additional constraints
    logger.info("Test 4: Enable additional constraints")
    solver_manager.set_constraint_enabled('production_rate', True)
    solver_manager.set_constraint_enabled('minimum_batch', True)
    solver = solver_manager.create_solver('ortools')
    solver.build_minimize_cost_model(data)
    solver.apply_constraints()
    constraints = solver.get_all_constraints()
    assert len(constraints) == 5, "Expected 5 constraints after enabling all"
    assert 'demand' in constraints, "Demand constraint should be present"
    assert 'supply' in constraints, "Supply constraint should be present"
    assert 'allowed_combinations' in constraints, "Allowed combinations constraint should be present"
    assert 'production_rate' in constraints, "Production rate constraint should be present"
    assert 'minimum_batch' in constraints, "Minimum batch constraint should be present"
    
    logger.info("All constraint state tests passed successfully")

def main():
    """Run the constraint state tests."""
    try:
        test_constraint_state_changes()
        print("All tests completed successfully")
    except Exception as e:
        print(f"Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 