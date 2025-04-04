"""
Data Model Service Module.

Provides a service for data processing and synchronization with parameter models.
"""
import logging
import os
from PyQt6.QtCore import QObject, pyqtSignal
from src.data.processor import DataProcessor
from .parameter_registry import ParameterRegistry

logger = logging.getLogger(__name__)

class DataModelService(QObject):
    """
    Service for managing data processing and parameter synchronization.
    """
    data_loaded = pyqtSignal()  # Emitted when data is successfully loaded
    data_error = pyqtSignal(str)  # Emitted when data loading fails
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the data model service.
        
        Args:
            debug_mode: Whether to enable debug output
        """
        super().__init__()
        self.debug_mode = debug_mode
        self.data_processor = DataProcessor(debug_mode=debug_mode)
        self.param_registry = ParameterRegistry.get_instance()
        self.data_params = self.param_registry.get_model("data")
        self.optimization_params = self.param_registry.get_model("optimization")
        
        # Connect to parameter changes
        self.data_params.parameter_changed.connect(self._on_parameter_changed)
        
        logger.debug("Initialized data model service")
    
    def _on_parameter_changed(self, name, value):
        """
        React to data parameter changes.

        Args:
            name: Parameter name
            value: New parameter value
        """
        if name in ["demand_file", "supply_file", "cost_file", "wpp_file", "combinations_file"]:
            logger.debug(f"Data parameter changed: {name} = {value}")
            # Check if all required files are set
            missing_files = []
            for key in ["demand_file", "supply_file", "cost_file", "wpp_file", "combinations_file"]:
                file_path = self.data_params.get_parameter(key)
                if not file_path or not os.path.exists(file_path):
                    missing_files.append(key)
            
            if not missing_files:
                logger.debug("All required data files are set, auto-loading data")
                # Auto-load data when all files are specified
                self.load_data()
    
    def load_data(self, manual_config=None):
        """
        Load data from the files specified in parameters.

        Args:
            manual_config: Optional manual configuration dictionary
        
        Returns:
            bool: True if data was loaded successfully
        """
        try:
            # Get file paths from parameters or manual config
            if manual_config:
                config = manual_config
            else:
                config = {
                    "demand_file": self.data_params.get_parameter("demand_file", ""),
                    "supply_file": self.data_params.get_parameter("supply_file", ""),
                    "cost_file": self.data_params.get_parameter("cost_file", ""),
                    "wpp_file": self.data_params.get_parameter("wpp_file", ""),
                    "combinations_file": self.data_params.get_parameter("combinations_file", ""),
                    "constraint_config_file": self.data_params.get_parameter("constraint_config_file")
                }
            
            logger.debug(f"Loading data with configuration: {config}")
            
            # Check for missing files
            missing_files = []
            for key, file_path in config.items():
                if key != "constraint_config_file" and (not file_path or not os.path.exists(file_path)):
                    missing_files.append(key)
            
            if missing_files:
                error_msg = f"Missing data files: {', '.join(missing_files)}"
                logger.error(error_msg)
                self.data_error.emit(error_msg)
                return False
            
            # Load data using data processor
            self.data_processor.load_data(
                demand_file=config.get("demand_file", ""),
                supply_file=config.get("supply_file", ""),
                cost_file=config.get("cost_file", ""),
                wpp_file=config.get("wpp_file", ""),
                combinations_file=config.get("combinations_file", ""),
                constraint_config_file=config.get("constraint_config_file")
            )
            
            # Update derived parameters in optimization model
            constraints = self.data_processor.get_constraint_manager().get_available_constraints()
            self.optimization_params.set_parameter("available_constraints", constraints)
            
            # Get optimization dimensions
            opt_data = self.data_processor.get_optimization_data()
            
            # Set dimension parameters
            self.optimization_params.set_parameter("waffle_types", opt_data.get("waffle_types", []))
            self.optimization_params.set_parameter("pan_types", opt_data.get("pan_types", []))
            self.optimization_params.set_parameter("weeks", opt_data.get("weeks", []))
            
            # Signal successful load
            logger.debug("Data loaded successfully")
            self.data_loaded.emit()
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading data: {error_msg}")
            self.data_error.emit(error_msg)
            return False
    
    def get_data_processor(self):
        """
        Get the underlying data processor.
        
        Returns:
            DataProcessor: The data processor instance
        """
        return self.data_processor
    
    def get_optimization_data(self):
        """
        Get the current optimization data.
        
        Returns:
            dict: Optimization data dictionary or None if data not loaded
        """
        try:
            return self.data_processor.get_optimization_data()
        except Exception as e:
            logger.error(f"Error getting optimization data: {str(e)}")
            return None 