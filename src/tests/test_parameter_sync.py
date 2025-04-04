"""
Test parameter synchronization between components.
"""
import sys
import logging
import os
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

from src.models.parameter_registry import ParameterRegistry
from src.models.parameter_model import ParameterModel
from src.models.data_model_service import DataModelService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ParameterModelTest(unittest.TestCase):
    """Test basic parameter model functionality."""
    
    def test_parameter_setting_getting(self):
        """Test parameter setting and getting."""
        model = ParameterModel()
        
        # Test setting and getting basic values
        model.set_parameter("test_int", 123)
        self.assertEqual(model.get_parameter("test_int"), 123)
        
        model.set_parameter("test_str", "hello")
        self.assertEqual(model.get_parameter("test_str"), "hello")
        
        model.set_parameter("test_bool", True)
        self.assertEqual(model.get_parameter("test_bool"), True)
        
        model.set_parameter("test_list", [1, 2, 3])
        self.assertEqual(model.get_parameter("test_list"), [1, 2, 3])
        
    def test_parameter_validation(self):
        """Test parameter validation."""
        model = ParameterModel()
        
        # Register a validator that only accepts positive values
        model.register_validator("validated", lambda x: x > 0)
        
        # Valid value should be accepted
        self.assertTrue(model.set_parameter("validated", 10))
        self.assertEqual(model.get_parameter("validated"), 10)
        
        # Invalid value should be rejected
        self.assertFalse(model.set_parameter("validated", -5))
        self.assertEqual(model.get_parameter("validated"), 10)  # Old value retained
    
    def test_parameter_locking(self):
        """Test parameter locking."""
        model = ParameterModel()
        
        # Set initial value
        model.set_parameter("locked", 42)
        self.assertEqual(model.get_parameter("locked"), 42)
        
        # Lock parameter
        model.lock_parameter("locked")
        
        # Attempt to change locked parameter
        self.assertFalse(model.set_parameter("locked", 100))
        self.assertEqual(model.get_parameter("locked"), 42)  # Value unchanged
        
        # Unlock parameter
        model.unlock_parameter("locked")
        
        # Now change should be allowed
        self.assertTrue(model.set_parameter("locked", 100))
        self.assertEqual(model.get_parameter("locked"), 100)
    
    def test_parameter_signals(self):
        """Test parameter change signals."""
        app = QApplication.instance() or QApplication(sys.argv)
        model = ParameterModel()
        
        # Track signal emissions
        signal_received = False
        signal_name = None
        signal_value = None
        
        def handle_parameter_changed(name, value):
            nonlocal signal_received, signal_name, signal_value
            signal_received = True
            signal_name = name
            signal_value = value
        
        # Connect signal
        model.parameter_changed.connect(handle_parameter_changed)
        
        # Change parameter
        model.set_parameter("signal_test", "test_value")
        
        # Process events to allow signal to be delivered
        app.processEvents()
        
        # Check signal was received correctly
        self.assertTrue(signal_received)
        self.assertEqual(signal_name, "signal_test")
        self.assertEqual(signal_value, "test_value")


class ParameterRegistryTest(unittest.TestCase):
    """Test parameter registry functionality."""
    
    def setUp(self):
        self.registry = ParameterRegistry.get_instance()
        # Reset the registry between tests
        self.registry.reset()
    
    def test_get_model(self):
        """Test getting models from registry."""
        # Get two different models
        model1 = self.registry.get_model("model1")
        model2 = self.registry.get_model("model2")
        
        # Should be different instances
        self.assertIsNot(model1, model2)
        
        # Getting same name should return same instance
        model1_again = self.registry.get_model("model1")
        self.assertIs(model1, model1_again)
    
    def test_parameter_isolation(self):
        """Test parameter isolation between models."""
        model1 = self.registry.get_model("model1")
        model2 = self.registry.get_model("model2")
        
        # Set parameters in different models
        model1.set_parameter("param1", "value1")
        model2.set_parameter("param2", "value2")
        
        # Verify parameter isolation
        self.assertEqual(model1.get_parameter("param1"), "value1")
        self.assertIsNone(model1.get_parameter("param2"))
        self.assertEqual(model2.get_parameter("param2"), "value2")
        self.assertIsNone(model2.get_parameter("param1"))


class DataModelServiceTest(unittest.TestCase):
    """Test data model service functionality."""
    
    def setUp(self):
        # Get or create app instance
        self.app = QApplication.instance() or QApplication(sys.argv)
        # Reset parameter registry
        ParameterRegistry.get_instance().reset()
        
        # Create data model service
        self.data_service = DataModelService(debug_mode=True)
        
        # Get parameter models
        self.registry = ParameterRegistry.get_instance()
        self.data_params = self.registry.get_model("data")
    
    def test_parameter_update(self):
        """Test updating parameters via data model service."""
        # Set file parameters
        file_paths = {
            "demand_file": "test_demand.xlsx",
            "supply_file": "test_supply.xlsx",
            "cost_file": "test_cost.xlsx",
            "wpp_file": "test_wpp.xlsx",
            "combinations_file": "test_combinations.xlsx"
        }
        
        # Set parameters
        for name, path in file_paths.items():
            self.data_params.set_parameter(name, path)
            
        # Verify parameters were set
        for name, path in file_paths.items():
            self.assertEqual(self.data_params.get_parameter(name), path)


def run_tests():
    """Run all tests."""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests() 