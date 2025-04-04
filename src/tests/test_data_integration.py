"""
Test script for data integration with the constraint system.

This script verifies that the constraint configuration system integrates correctly
with the data processing pipeline.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import modules properly
sys.path.append(str(Path(__file__).parent.parent.parent))

import time
from typing import Dict, Any
from src.data import DataProcessor, ConstraintConfigManager
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

def test_constraint_config_manager():
    """Test the ConstraintConfigManager."""
    print("Testing ConstraintConfigManager...")
    
    # Create constraint configuration manager
    manager = ConstraintConfigManager(debug_mode=True)
    
    # Get available constraints
    constraints = manager.get_available_constraints()
    print(f"Available constraints: {len(constraints)}")
    for constraint in constraints:
        print(f"  - {constraint['name']}: {constraint['description']}")
        print(f"    Enabled: {constraint['enabled']}")
        print(f"    Config: {constraint['config']}")
    
    # Configure constraints
    print("\nConfiguring constraints...")
    manager.set_constraint_enabled('production_rate', True)
    manager.set_constraint_configuration('production_rate', {'max_rate_change': 0.3})
    manager.set_constraint_enabled('minimum_batch', True)
    manager.set_constraint_configuration('minimum_batch', {'min_batch_size': 5})
    
    # Get updated constraints
    constraints = manager.get_available_constraints()
    for constraint in constraints:
        if constraint['name'] in ['production_rate', 'minimum_batch']:
            print(f"  - {constraint['name']}: Enabled={constraint['enabled']}, Config={constraint['config']}")
    
    # Save configuration to a file
    config_file = 'test_constraints.json'
    print(f"\nSaving configuration to {config_file}...")
    if manager.save_configuration(config_file):
        print("  Configuration saved successfully.")
    
    # Reset configurations
    print("\nResetting configurations...")
    manager.set_constraint_enabled('production_rate', False)
    manager.reset_constraint_configuration('production_rate')
    manager.set_constraint_enabled('minimum_batch', False)
    manager.reset_constraint_configuration('minimum_batch')
    
    # Load configuration from file
    print(f"\nLoading configuration from {config_file}...")
    if manager.load_configuration(config_file):
        print("  Configuration loaded successfully.")
    
    # Get updated constraints
    constraints = manager.get_available_constraints()
    for constraint in constraints:
        if constraint['name'] in ['production_rate', 'minimum_batch']:
            print(f"  - {constraint['name']}: Enabled={constraint['enabled']}, Config={constraint['config']}")
    
    # Clean up the test file
    if os.path.exists(config_file):
        os.remove(config_file)
        print(f"  Removed test file: {config_file}")
    
    print("ConstraintConfigManager test completed.")

def test_data_processor_integration():
    """Test the integration of DataProcessor with the constraint system."""
    print("\nTesting DataProcessor integration with constraint system...")
    
    # Create data processor
    processor = DataProcessor(debug_mode=True)
    
    # Get constraint manager
    constraint_manager = processor.get_constraint_manager()
    print(f"Got constraint manager: {constraint_manager is not None}")
    
    # Configure constraints
    print("\nConfiguring constraints through DataProcessor...")
    constraint_manager.set_constraint_enabled('production_rate', True)
    constraint_manager.set_constraint_configuration('production_rate', {'max_rate_change': 0.25})
    
    # Create a solver with constraints
    print("\nCreating a solver with constraints...")
    solver = processor.create_solver_with_constraints('ortools')
    print(f"Solver created: {solver is not None}")
    
    # Check if the constraint is configured on the solver
    enabled_constraints = solver.get_all_constraints()
    print(f"Enabled constraints on solver: {list(enabled_constraints.keys())}")
    
    if 'production_rate' in enabled_constraints:
        print(f"Production rate constraint is configured on the solver.")
    
    print("DataProcessor integration test completed.")

def main():
    """Main function to run the tests."""
    print("=== Testing Data Integration with Constraint System ===")
    
    test_constraint_config_manager()
    test_data_processor_integration()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 