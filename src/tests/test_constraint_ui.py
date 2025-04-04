"""
Test script for constraint UI integration.

This script tests the constraint management UI components to verify they work correctly.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import modules properly
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from src.gui.widgets.constraint_manager import ConstraintManager, ConstraintConfigDialog
from src.gui.controllers.optimization_controller import OptimizationController
from src.data import ConstraintConfigManager

class TestMainWindow(QMainWindow):
    """Simple main window for testing the constraint manager widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Constraint Manager Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create optimization controller
        self.controller = OptimizationController()
        
        # Create constraint manager widget
        self.constraint_manager = ConstraintManager()
        self.constraint_manager.set_controller(self.controller)
        
        # Add widget to layout
        layout.addWidget(self.constraint_manager)
        
        # Set up a timer to load test data
        QTimer.singleShot(100, self.load_test_data)
    
    def load_test_data(self):
        """Load test data for the constraint manager."""
        # Create a dummy config
        config = {
            "demand": "data/input/WaffleDemand.xlsx",
            "supply": "data/input/PanSupply.xlsx",
            "cost": "data/input/WaffleCostPerPan.xlsx",
            "wpp": "data/input/WafflesPerPan.xlsx",
            "combinations": "data/input/WafflePanCombinations.xlsx",
            "debug": True
        }
        
        # Load the data
        self.controller.load_data(config)
        
        print("Data loaded, constraint manager should show available constraints.")
        print("Available constraints:")
        for constraint in self.controller.get_available_constraints():
            print(f"  - {constraint['name']}: {constraint['description']}")
            print(f"    Enabled: {constraint['enabled']}")
            print(f"    Config: {constraint['config']}")


def test_constraint_config_dialog():
    """Test the constraint configuration dialog."""
    app = QApplication(sys.argv)
    
    # Create a test constraint info
    constraint_info = {
        'name': 'test_constraint',
        'description': 'This is a test constraint for UI testing.',
        'schema': {
            'type': 'object',
            'properties': {
                'max_value': {
                    'type': 'number',
                    'title': 'Maximum Value',
                    'description': 'The maximum allowed value for this constraint',
                    'minimum': 0,
                    'maximum': 100
                },
                'enabled_feature': {
                    'type': 'boolean',
                    'title': 'Enable Feature',
                    'description': 'Whether to enable an additional feature'
                },
                'mode': {
                    'type': 'string',
                    'title': 'Operation Mode',
                    'description': 'The mode of operation',
                    'enum': ['simple', 'advanced', 'expert']
                }
            },
            'required': ['max_value']
        },
        'enabled': True,
        'config': {
            'max_value': 50,
            'enabled_feature': False,
            'mode': 'simple'
        }
    }
    
    # Create and show the dialog
    dialog = ConstraintConfigDialog(constraint_info)
    result = dialog.exec()
    
    if result:
        config = dialog.get_configuration()
        print("Dialog accepted with configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("Dialog cancelled")
    
    return app.exec()


def test_constraint_manager():
    """Test the constraint manager widget."""
    app = QApplication(sys.argv)
    
    window = TestMainWindow()
    window.show()
    
    return app.exec()


def main():
    """Main function to run the tests."""
    print("=== Testing Constraint UI Components ===")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dialog':
        print("Testing Constraint Config Dialog...")
        return test_constraint_config_dialog()
    else:
        print("Testing Constraint Manager Widget...")
        return test_constraint_manager()


if __name__ == "__main__":
    sys.exit(main()) 