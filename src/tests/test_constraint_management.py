"""
Additional test cases for constraint management system.

This module implements additional test cases for the constraint management system,
including configuration persistence, invalid configuration handling, and edge cases.
"""
import sys
import os
import json
import tempfile
from pathlib import Path
import logging
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.solvers.solver_manager import SolverManager
from src.data.constraint_config import ConstraintConfigManager
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
            # Increasing supply to make the model feasible
            ('P1', 'Week1'): 300,
            ('P1', 'Week2'): 350,
            ('P2', 'Week1'): 300,
            ('P2', 'Week2'): 350
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
        'wpp_pan': {
            ('W1', 'P1'): 10,
            ('W1', 'P2'): 12,
            ('W2', 'P1'): 15,
            ('W2', 'P2'): 18
        },
        'cost': {
            ('W1', 'P1'): 1.0,
            ('W1', 'P2'): 1.2,
            ('W2', 'P1'): 1.5,
            ('W2', 'P2'): 1.8
        }
    }

def test_configuration_persistence():
    """Test that constraint configurations are properly persisted and loaded."""
    logger = logging.getLogger(__name__)
    logger.info("Testing configuration persistence...")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        config_file = temp_file.name
    
    try:
        # Create constraint config manager
        manager = ConstraintConfigManager(debug_mode=True)
        
        # Configure some constraints
        manager.set_constraint_enabled('production_rate', True)
        manager.set_constraint_configuration('production_rate', {'max_rate_change': 0.3})
        manager.set_constraint_enabled('minimum_batch', True)
        manager.set_constraint_configuration('minimum_batch', {'min_batch_size': 5})
        
        # Save configuration
        assert manager.save_configuration(config_file), "Failed to save configuration"
        
        # Create new manager and load configuration
        new_manager = ConstraintConfigManager(debug_mode=True)
        assert new_manager.load_configuration(config_file), "Failed to load configuration"
        
        # Verify loaded configuration
        constraints = new_manager.get_available_constraints()
        for constraint in constraints:
            if constraint['name'] == 'production_rate':
                assert constraint['enabled'], "Production rate constraint should be enabled"
                assert 'max_rate_change' in constraint['config'], "max_rate_change should be in config"
                # Check that the value is within valid range (0-1)
                assert 0 <= constraint['config']['max_rate_change'] <= 1, "max_rate_change should be between 0 and 1"
            elif constraint['name'] == 'minimum_batch':
                assert constraint['enabled'], "Minimum batch constraint should be enabled"
                assert 'min_batch_size' in constraint['config'], "min_batch_size should be in config"
                # Check that the value is a positive integer
                assert isinstance(constraint['config']['min_batch_size'], int), "min_batch_size should be an integer"
                assert constraint['config']['min_batch_size'] > 0, "min_batch_size should be positive"
        
        logger.info("Configuration persistence test passed")
    
    finally:
        # Clean up
        if os.path.exists(config_file):
            os.remove(config_file)

def test_invalid_configurations():
    """Test handling of invalid constraint configurations."""
    logger = logging.getLogger(__name__)
    logger.info("Testing invalid configuration handling...")
    
    # Create constraint config manager
    manager = ConstraintConfigManager(debug_mode=True)
    
    # Test 1: Invalid constraint name
    try:
        manager.set_constraint_enabled('invalid_constraint', True)
        assert False, "Should have raised ValueError for invalid constraint name"
    except ValueError:
        pass
    
    # Test 2: Invalid configuration values
    try:
        manager.set_constraint_configuration('production_rate', {'max_rate_change': -0.5})
        assert False, "Should have raised ValueError for negative max_rate_change"
    except ValueError:
        pass
    
    try:
        manager.set_constraint_configuration('minimum_batch', {'min_batch_size': 0})
        assert False, "Should have raised ValueError for non-positive min_batch_size"
    except ValueError:
        pass
    
    # Test 3: Empty configuration (should use default values)
    try:
        manager.set_constraint_configuration('production_rate', {})
        # Should not raise an error since all parameters are optional with defaults
    except ValueError:
        assert False, "Should not have raised ValueError for empty configuration with defaults"
    
    logger.info("Invalid configuration test passed")

def test_edge_cases():
    """Test edge cases in constraint management."""
    logger = logging.getLogger(__name__)
    logger.info("Testing edge cases...")
    
    # Create constraint config manager
    manager = ConstraintConfigManager(debug_mode=True)
    
    # Test 1: Empty configuration (should be valid for optional parameters)
    empty_config = {}
    assert manager.validate_constraint_configuration('production_rate', empty_config) is True, \
        "Empty configuration should be valid when parameters are optional"
    
    # Test 2: Maximum allowed values
    max_config = {
        'max_rate_change': 1.0
    }
    assert manager.validate_constraint_configuration('production_rate', max_config) is True, \
        "Maximum values should be valid"
    
    # Test 3: Multiple constraint changes
    manager.set_constraint_enabled('production_rate', True)
    manager.set_constraint_enabled('minimum_batch', True)
    manager.set_constraint_enabled('demand', False)
    manager.set_constraint_enabled('supply', False)
    manager.set_constraint_enabled('allowed_combinations', False)
    
    constraints = manager.get_available_constraints()
    enabled_count = sum(1 for c in constraints if c['enabled'])
    assert enabled_count == 2, "Should have exactly 2 enabled constraints"
    
    # Test 4: Reset configuration
    manager.reset_constraint_configuration('production_rate')
    constraints = manager.get_available_constraints()
    for constraint in constraints:
        if constraint['name'] == 'production_rate':
            assert not constraint['enabled'], "Constraint should be disabled after reset"
            assert constraint['config'] == {}, "Configuration should be empty after reset"
    
    logger.info("Edge case tests passed")

def test_solver_integration():
    """Test integration with solver system."""
    logger = logging.getLogger(__name__)
    logger.info("Testing solver integration...")
    
    # Create solver manager and test data
    solver_manager = SolverManager()
    data = create_test_data()
    
    # Disable all constraints initially
    for constraint_type in solver_manager.get_available_constraints():
        solver_manager.set_constraint_enabled(constraint_type, False)
    
    # Test 1: No constraints
    solver = solver_manager.create_solver('ortools')
    solver.build_minimize_cost_model(data)
    solver.apply_constraints()
    constraints = solver.get_all_constraints()
    assert len(constraints) == 0, "Should have no constraints initially"
    
    # Test 2: All constraints enabled
    solver_manager.set_constraint_enabled('demand', True)
    solver_manager.set_constraint_enabled('supply', True)
    solver_manager.set_constraint_enabled('allowed_combinations', True)
    solver_manager.set_constraint_enabled('production_rate', True)
    solver_manager.set_constraint_enabled('minimum_batch', True)
    
    solver = solver_manager.create_solver('ortools')
    solver.build_minimize_cost_model(data)
    solver.apply_constraints()
    constraints = solver.get_all_constraints()
    assert len(constraints) == 5, "Should have all constraints enabled"
    
    # Test 3: Solve with constraints
    result = solver.solve_model()
    assert result['status'] in ['OPTIMAL', 'FEASIBLE'], "Model should be solvable with constraints"
    
    logger.info("Solver integration tests passed")

def main():
    """Run all constraint management tests."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting constraint management tests...")
        
        test_configuration_persistence()
        test_invalid_configurations()
        test_edge_cases()
        test_solver_integration()
        
        logger.info("All constraint management tests completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 