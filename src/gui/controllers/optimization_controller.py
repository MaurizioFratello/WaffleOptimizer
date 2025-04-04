"""
Controller for managing optimization processes.
"""
import os
import logging
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import time

from src.data.processor import DataProcessor
from src.data.validator import DataValidator
from src.models.parameter_registry import ParameterRegistry

logger = logging.getLogger(__name__)

class OptimizationWorker(QObject):
    """
    Worker thread for running optimization processes.
    """
    progress = pyqtSignal(int, str, float, int)  # value, status, gap, iterations
    error = pyqtSignal(str)
    result = pyqtSignal(dict)
    finished = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.cancelled = False
    
    def run(self):
        """Execute the optimization process."""
        try:
            # Create data processor
            data_processor = DataProcessor(debug_mode=self.config.get('debug', False))
            
            # Load data
            self.progress.emit(10, "Loading input data...", 0, 0)
            data_processor.load_data(
                demand_file=self.config.get('demand', ''),
                supply_file=self.config.get('supply', ''),
                cost_file=self.config.get('cost', ''),
                wpp_file=self.config.get('wpp', ''),
                combinations_file=self.config.get('combinations', ''),
                constraint_config_file=self.config.get('constraint_config', None)
            )
            
            # Check if cancelled
            if self.cancelled:
                self.finished.emit()
                return
            
            # Get optimization data
            self.progress.emit(30, "Preparing optimization model...", 0, 0)
            optimization_data = data_processor.get_optimization_data()
            
            # Validate data
            data_validator = DataValidator(debug_mode=self.config.get('debug', False))
            is_feasible, critical_issues, warnings = data_validator.check_basic_feasibility(optimization_data)
            
            if not is_feasible:
                error_msg = "Data validation failed: " + "; ".join(critical_issues)
                self.error.emit(error_msg)
                self.finished.emit()
                return
            
            # Check if cancelled
            if self.cancelled:
                self.finished.emit()
                return
            
            # Create solver with constraints
            self.progress.emit(40, "Initializing solver with constraints...", 0, 0)
            
            # Use the constraint manager to create a solver with constraints
            solver = data_processor.create_solver_with_constraints(
                solver_name=self.config.get('solver', 'ortools'),
                time_limit=self.config.get('time_limit', 60),
                optimality_gap=self.config.get('gap', 0.01)
            )
            
            # Set up the model
            self.progress.emit(50, "Building optimization model...", 0, 0)
            # Choose which model to build based on the objective
            if self.config.get('objective', 'cost') == 'cost':
                solver.build_minimize_cost_model(optimization_data)
            else:
                solver.build_maximize_output_model(
                    optimization_data,
                    limit_to_demand=self.config.get('limit_to_demand', False)
                )
            
            # Check if cancelled
            if self.cancelled:
                self.finished.emit()
                return
            
            # Solve the model
            self.progress.emit(60, "Solving optimization model...", 0, 0)
            solution = solver.solve_model()
            
            # Process results
            self.progress.emit(90, "Processing results...", solution.get('gap', 0), 
                              solution.get('iterations', 0))
            
            # Get the full solution
            full_solution = solver.get_solution()
            
            # Normalize status to uppercase for consistent comparison
            status = full_solution.get('status', 'unknown').upper()
            gap = full_solution.get('gap', 0)
            iterations = full_solution.get('iterations', 0)
            
            # Critical status update based on optimization status
            if status == 'OPTIMAL':
                # For optimal solutions, always ensure 100% progress and clear status message
                self.progress.emit(100, "OPTIMIZATION COMPLETE - OPTIMAL SOLUTION FOUND", gap, iterations)
            else:
                # For non-optimal solutions, ensure consistent status message
                self.progress.emit(90, f"Optimization incomplete - Status: {status}", gap, iterations)
            
            # Ensure the status field is standardized in the solution
            full_solution['status'] = status
            
            # Return results after a slight delay to ensure UI updates
            time.sleep(0.1)  # Small delay to ensure UI thread processes the progress signal
            self.result.emit(full_solution)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()
    
    def cancel(self):
        """Cancel the optimization process."""
        self.cancelled = True


class OptimizationController(QObject):
    """
    Controller for managing the optimization process between GUI and backend.
    """
    # Signals for updating UI
    optimization_started = pyqtSignal()
    optimization_progress = pyqtSignal(int, str, float, int)  # value, status, gap, iterations
    optimization_error = pyqtSignal(str)
    optimization_completed = pyqtSignal(dict)  # results dictionary
    constraints_updated = pyqtSignal(list)  # list of available constraints
    data_updated = pyqtSignal()  # new signal for data updates
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.thread = None
        self.results = None
        
        # Get parameter models
        self.param_registry = ParameterRegistry.get_instance()
        self.optimization_params = self.param_registry.get_model("optimization")
        self.data_params = self.param_registry.get_model("data")
        
        # Initialize data processor
        self.data_processor = DataProcessor()
        
        # Connect to parameter changes
        self.optimization_params.parameter_changed.connect(self._on_parameter_changed)
        self.data_params.parameter_changed.connect(self._on_data_parameter_changed)
        
        logger.debug("Initialized optimization controller with parameter models")
    
    def _on_parameter_changed(self, name, value):
        """
        Handle optimization parameter changes.
        
        Args:
            name: Parameter name
            value: Parameter value
        """
        logger.debug(f"Optimization parameter changed: {name} = {value}")
        # React to specific parameter changes as needed
        # For now, just log the change
    
    def _on_data_parameter_changed(self, name, value):
        """
        Handle data parameter changes.
        
        Args:
            name: Parameter name
            value: Parameter value
        """
        if name in ["demand_file", "supply_file", "cost_file", "wpp_file", "combinations_file"]:
            logger.debug(f"Data parameter changed: {name} = {value}")
            # Signal that data path has changed
            self.data_updated.emit()
    
    def start_optimization(self, config=None):
        """
        Start an optimization process with the given configuration.
        
        Args:
            config: Dictionary of configuration options (optional)
        """
        # Get parameters from model if config not provided
        if config is None:
            config = {
                # Data files
                "demand": self.data_params.get_parameter("demand_file", ""),
                "supply": self.data_params.get_parameter("supply_file", ""),
                "cost": self.data_params.get_parameter("cost_file", ""),
                "wpp": self.data_params.get_parameter("wpp_file", ""),
                "combinations": self.data_params.get_parameter("combinations_file", ""),
                "constraint_config": self.data_params.get_parameter("constraint_config_file"),
                
                # Optimization settings
                "objective": self.optimization_params.get_parameter("objective", "cost"),
                "solver": self.optimization_params.get_parameter("solver", "ortools"),
                "time_limit": self.optimization_params.get_parameter("time_limit", 60),
                "gap": self.optimization_params.get_parameter("gap", 0.005),
                "limit_to_demand": self.optimization_params.get_parameter("limit_to_demand", True),
                "debug": self.optimization_params.get_parameter("debug_mode", False),
                
                # Output settings
                "output": self.optimization_params.get_parameter("output_path", "")
            }
        
        logger.debug(f"Starting optimization with config: {config}")
        
        # Create worker and thread
        self.thread = QThread()
        self.worker = OptimizationWorker(config)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.optimization_progress)
        self.worker.error.connect(self.optimization_error)
        self.worker.result.connect(self._store_results)
        self.worker.finished.connect(self.thread.quit)
        
        # Clean up when done
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.optimization_started.emit()
        self.thread.start()
    
    def cancel_optimization(self):
        """Cancel the current optimization process."""
        if self.worker:
            logger.debug("Cancelling optimization")
            self.worker.cancel()
    
    def _store_results(self, results):
        """Store the optimization results and emit completion signal."""
        self.results = results
        
        # Store results in parameter model for accessibility
        self.optimization_params.set_parameter("results", results)
        
        # Emit completion signal
        self.optimization_completed.emit(results)
        
        logger.debug(f"Optimization completed with status: {results.get('status', 'unknown')}")
    
    def load_data(self, config=None):
        """
        Load data from files without running optimization.
        
        Args:
            config: Dictionary of configuration options (optional)
            
        Returns:
            bool: True if data was loaded successfully
        """
        try:
            # Get config from parameters if not provided
            if config is None:
                config = {
                    "demand": self.data_params.get_parameter("demand_file", ""),
                    "supply": self.data_params.get_parameter("supply_file", ""),
                    "cost": self.data_params.get_parameter("cost_file", ""),
                    "wpp": self.data_params.get_parameter("wpp_file", ""),
                    "combinations": self.data_params.get_parameter("combinations_file", ""),
                    "constraint_config": self.data_params.get_parameter("constraint_config_file"),
                    "debug": self.optimization_params.get_parameter("debug_mode", False)
                }
            
            logger.debug(f"Loading data with config: {config}")
            
            # Create new data processor
            self.data_processor = DataProcessor(debug_mode=config.get('debug', False))
            
            # Load data
            self.data_processor.load_data(
                demand_file=config.get('demand', ''),
                supply_file=config.get('supply', ''),
                cost_file=config.get('cost', ''),
                wpp_file=config.get('wpp', ''),
                combinations_file=config.get('combinations', ''),
                constraint_config_file=config.get('constraint_config', None)
            )
            
            # Update available constraints in parameter model
            constraints = self.data_processor.get_constraint_manager().get_available_constraints()
            self.optimization_params.set_parameter("available_constraints", constraints)
            
            # Store dimensions in parameter model
            opt_data = self.data_processor.get_optimization_data()
            self.optimization_params.set_parameter("waffle_types", opt_data.get("waffle_types", []))
            self.optimization_params.set_parameter("pan_types", opt_data.get("pan_types", []))
            self.optimization_params.set_parameter("weeks", opt_data.get("weeks", []))
            
            # Emit signal with available constraints (for backward compatibility)
            self.constraints_updated.emit(constraints)
            
            logger.debug("Data loaded successfully")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading data: {error_msg}")
            self.optimization_error.emit(error_msg)
            return False
    
    def get_available_constraints(self):
        """
        Get a list of available constraints.
        
        Returns:
            list: List of constraint information dictionaries
        """
        # First check if available in parameter model
        constraints = self.optimization_params.get_parameter("available_constraints")
        if constraints:
            return constraints
            
        # Otherwise get from data processor
        return self.data_processor.get_constraint_manager().get_available_constraints()
    
    def set_constraint_enabled(self, constraint_type, enabled):
        """
        Enable or disable a constraint.
        
        Args:
            constraint_type: Name of the constraint
            enabled: Whether the constraint should be enabled
        """
        logger.debug(f"Setting constraint '{constraint_type}' enabled={enabled}")
        self.data_processor.get_constraint_manager().set_constraint_enabled(constraint_type, enabled)
        
        # Update parameter model with constraint state
        constraint_states = self.optimization_params.get_parameter("constraint_states", {})
        constraint_states[constraint_type] = enabled
        self.optimization_params.set_parameter("constraint_states", constraint_states)
    
    def set_constraint_configuration(self, constraint_type, config):
        """
        Set the configuration for a constraint.
        
        Args:
            constraint_type: Name of the constraint
            config: Configuration dictionary
        """
        logger.debug(f"Setting configuration for constraint '{constraint_type}': {config}")
        self.data_processor.get_constraint_manager().set_constraint_configuration(constraint_type, config)
        
        # Update parameter model with constraint configuration
        constraint_configs = self.optimization_params.get_parameter("constraint_configs", {})
        constraint_configs[constraint_type] = config
        self.optimization_params.set_parameter("constraint_configs", constraint_configs)
    
    def save_constraint_configuration(self, file_path):
        """
        Save the current constraint configuration to a file.
        
        Args:
            file_path: Path to save the configuration
            
        Returns:
            bool: True if the configuration was saved successfully
        """
        logger.debug(f"Saving constraint configuration to {file_path}")
        result = self.data_processor.save_constraint_configuration(file_path)
        
        # Store the path in parameter model
        if result:
            self.data_params.set_parameter("constraint_config_file", file_path)
            
        return result
    
    def load_constraint_configuration(self, file_path):
        """
        Load constraint configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            bool: True if the configuration was loaded successfully
        """
        logger.debug(f"Loading constraint configuration from {file_path}")
        result = self.data_processor.load_constraint_configuration(file_path)
        
        if result:
            # Update parameters
            self.data_params.set_parameter("constraint_config_file", file_path)
            
            # Update constraint data in parameter model
            constraints = self.data_processor.get_constraint_manager().get_available_constraints()
            self.optimization_params.set_parameter("available_constraints", constraints)
            
            # Emit signal for backward compatibility
            self.constraints_updated.emit(constraints)
            
        return result
    
    def export_results(self, file_path, format='xlsx'):
        """
        Export the optimization results to a file.
        
        Args:
            file_path: Path to save the results
            format: File format (xlsx, csv)
            
        Returns:
            bool: True if the results were exported successfully
        """
        if not self.results:
            logger.warning("Cannot export results: No results available")
            return False
        
        try:
            logger.debug(f"Exporting results to {file_path} (format={format})")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Export the results
            if format == 'xlsx':
                # Create a Pandas Excel writer
                writer = pd.ExcelWriter(file_path, engine='openpyxl')
                
                # Write each DataFrame to a different worksheet
                if 'production' in self.results:
                    self.results['production'].to_excel(writer, sheet_name='Production')
                
                if 'metrics' in self.results:
                    pd.DataFrame([self.results['metrics']]).to_excel(writer, sheet_name='Metrics')
                
                # Save the Excel file
                writer.close()
                
            elif format == 'csv':
                # Export as CSV
                if 'production' in self.results:
                    self.results['production'].to_csv(file_path)
                
            # Store export path in parameter model
            self.optimization_params.set_parameter("last_export_path", file_path)
                
            return True
            
        except Exception as e:
            error_msg = f"Error exporting results: {str(e)}"
            logger.error(error_msg)
            self.optimization_error.emit(error_msg)
            return False 