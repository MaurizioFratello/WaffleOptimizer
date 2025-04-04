"""
Optimization view for configuring and running optimizations.
"""
import logging
import os
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFormLayout, QComboBox, 
                          QSlider, QCheckBox, QGroupBox, QSpinBox,
                          QDoubleSpinBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QSettings, QCoreApplication

from ..parameter_aware_view import ParameterAwareView
from ..controllers.optimization_controller import OptimizationController
from ..widgets.optimization_status import OptimizationStatus
from ..widgets.constraint_manager import ConstraintManager
from src.models.parameter_registry import ParameterRegistry

logger = logging.getLogger(__name__)

class OptimizationView(ParameterAwareView):
    """
    View for configuring and running waffle production optimizations.
    """
    
    def __init__(self, main_window=None):
        super().__init__(
            title="Optimization Configuration",
            description="Configure the optimization settings and run the waffle production optimizer.",
            main_window=main_window,
            action_button_text="Run Optimization",
            model_name="optimization"
        )
        
        # Connect action button
        self.action_button.clicked.connect(self._run_optimization)
        
        self.settings = QSettings("WaffleOptimizer", "WaffleOptimizerGUI")
        
        # Create optimization controller
        self.optimization_controller = OptimizationController()
        
        # Connect controller signals
        self.optimization_controller.optimization_started.connect(self._on_optimization_started)
        self.optimization_controller.optimization_progress.connect(self._on_optimization_progress)
        self.optimization_controller.optimization_error.connect(self._on_optimization_error)
        self.optimization_controller.optimization_completed.connect(self._on_optimization_completed)
        
        # Initialize optimization components
        self._init_optimization_components()
        
        # Initialize constraint components
        self._init_constraint_components()
        
        # Set up parameter bindings
        self._setup_parameter_bindings()
        
        # Load saved settings
        self._load_settings()
        
        # Connect to data view's data_loaded signal if available
        if self.main_window and hasattr(self.main_window, 'data_view') and hasattr(self.main_window.data_view, 'data_loaded'):
            self.main_window.data_view.data_loaded.connect(self._load_data)
        
        # Connect to parameter changes
        self.param_model.parameter_changed.connect(self._on_parameter_changed)
        
        logger.debug("Initialized optimization view")
    
    def _setup_parameter_bindings(self):
        """Set up bindings between UI components and parameter model."""
        logger.debug("Setting up parameter bindings")
        
        # For combo boxes
        self._bind_combo_box(self.objective_combo, "objective")
        self._bind_combo_box(self.solver_combo, "solver")
        
        # For spin boxes
        self._bind_spin_box(self.time_limit, "time_limit")
        self._bind_double_spin_box(self.gap, "gap")
        
        # For checkboxes
        self._bind_check_box(self.limit_to_demand, "limit_to_demand")
        self._bind_check_box(self.debug_mode, "debug_mode")
        
        # For output path (text)
        self._bind_combo_box(self.output_path, "output_path", use_data=False)
    
    def _on_parameter_changed(self, name, value):
        """
        Handle parameter model changes.
        
        Args:
            name: Parameter name
            value: New value
        """
        logger.debug(f"Parameter changed: {name} = {value}")
        
        # Update UI components based on parameter changes as needed
        if name == "solver" and value:
            # React to solver change
            logger.debug(f"Solver changed to {value}")
            # Any solver-specific UI updates would go here
            
        elif name == "available_constraints" and value:
            # Update constraint manager with new constraints
            logger.debug(f"Available constraints updated: {len(value)} constraints")
            if hasattr(self, 'constraint_manager'):
                self.constraint_manager._update_constraints(value)
                
        elif name == "results" and value:
            # New results available
            logger.debug("New optimization results available")
            # Any results-specific handling could go here
    
    def _init_optimization_components(self):
        """Initialize optimization view specific components."""
        # Create settings group
        settings_group = self.create_group_box("Optimization Settings")
        form_layout = QFormLayout(settings_group)
        
        # Objective selector
        self.objective_combo = QComboBox()
        self.objective_combo.addItem("Minimize Cost", "cost")
        self.objective_combo.addItem("Maximize Output", "output")
        form_layout.addRow("Optimization Objective:", self.objective_combo)
        
        # Solver selector
        self.solver_combo = QComboBox()
        solvers = [
            ("OR-Tools", "ortools"),
            ("CBC", "cbc"),
            ("GLPK", "glpk"),
            ("SCIP", "scip"),
            ("COIN-OR", "coin_cmd")
        ]
        for label, value in solvers:
            self.solver_combo.addItem(label, value)
        form_layout.addRow("Solver:", self.solver_combo)
        
        # Time limit
        self.time_limit = QSpinBox()
        self.time_limit.setRange(1, 3600)  # 1 second to 1 hour
        self.time_limit.setValue(60)
        self.time_limit.setSuffix(" seconds")
        form_layout.addRow("Time Limit:", self.time_limit)
        
        # Optimality gap
        self.gap = QDoubleSpinBox()
        self.gap.setRange(0.0001, 0.1)  # 0.01% to 10%
        self.gap.setDecimals(4)
        self.gap.setSingleStep(0.001)
        self.gap.setValue(0.005)  # 0.5% default
        form_layout.addRow("Optimality Gap:", self.gap)
        
        # Additional options
        self.limit_to_demand = QCheckBox("Limit production to demand")
        self.limit_to_demand.setChecked(True)
        form_layout.addRow("Options:", self.limit_to_demand)
        
        # Debug mode
        self.debug_mode = QCheckBox("Enable debug output")
        self.debug_mode.setChecked(False)
        form_layout.addRow("Debug:", self.debug_mode)
        
        self.content_layout.addWidget(settings_group)
        
        # Output file setting
        output_group = self.create_group_box("Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        # Output file path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Output File:"))
        
        self.output_path = QComboBox()
        self.output_path.setEditable(True)
        self.output_path.addItem("data/output/waffle_solution.xlsx")
        self.output_path.addItem("data/output/optimization_results.xlsx")
        path_layout.addWidget(self.output_path, 1)
        
        # Browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_output_path)
        path_layout.addWidget(self.browse_button)
        
        # Export format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        
        self.export_format = QComboBox()
        self.export_format.addItem("Excel (.xlsx)", "xlsx")
        self.export_format.addItem("CSV (.csv)", "csv")
        format_layout.addWidget(self.export_format)
        format_layout.addStretch()
        
        # Add to output layout
        output_layout.addLayout(path_layout)
        output_layout.addLayout(format_layout)
        
        self.content_layout.addWidget(output_group)
        
        # Optimization status
        status_group = self.create_group_box("Optimization Status")
        status_layout = QVBoxLayout(status_group)
        
        self.optimization_status = OptimizationStatus()
        self.optimization_status.cancelled.connect(self._cancel_optimization)
        
        status_layout.addWidget(self.optimization_status)
        self.content_layout.addWidget(status_group)
    
    def _init_constraint_components(self):
        """Initialize constraint management components."""
        # Create constraint group
        constraint_group = self.create_group_box("Constraint Management")
        constraint_layout = QVBoxLayout(constraint_group)
        
        # Add description
        description = QLabel("Configure optimization constraints to control the behavior of the solver.")
        description.setWordWrap(True)
        constraint_layout.addWidget(description)
        
        # Create constraint manager widget
        self.constraint_manager = ConstraintManager()
        self.constraint_manager.set_controller(self.optimization_controller)
        
        # Add to layout
        constraint_layout.addWidget(self.constraint_manager)
        
        # Add to content layout
        self.content_layout.addWidget(constraint_group)
    
    def _load_settings(self):
        """Load saved settings from QSettings and update parameter model."""
        logger.debug("Loading settings from QSettings")
        
        # Optimization objective
        objective_index = self.settings.value("optimization/objective_index", 0, int)
        if 0 <= objective_index < self.objective_combo.count():
            objective_value = self.objective_combo.itemData(objective_index)
            self.param_model.set_parameter("objective", objective_value, emit_signal=False)
        
        # Solver
        solver_index = self.settings.value("optimization/solver_index", 0, int)
        if 0 <= solver_index < self.solver_combo.count():
            solver_value = self.solver_combo.itemData(solver_index)
            self.param_model.set_parameter("solver", solver_value, emit_signal=False)
        
        # Time limit
        time_limit = self.settings.value("optimization/time_limit", 60, int)
        self.param_model.set_parameter("time_limit", time_limit, emit_signal=False)
        
        # Gap
        gap = self.settings.value("optimization/gap", 0.005, float)
        self.param_model.set_parameter("gap", gap, emit_signal=False)
        
        # Limit to demand
        limit_to_demand = self.settings.value("optimization/limit_to_demand", True, bool)
        self.param_model.set_parameter("limit_to_demand", limit_to_demand, emit_signal=False)
        
        # Debug mode
        debug_mode = self.settings.value("optimization/debug_mode", False, bool)
        self.param_model.set_parameter("debug_mode", debug_mode, emit_signal=False)
        
        # Output path
        output_path = self.settings.value("optimization/output_path", "")
        if output_path:
            # Don't use the parameter model yet, handle combo box directly
            index = self.output_path.findText(output_path)
            if index >= 0:
                self.output_path.setCurrentIndex(index)
            else:
                self.output_path.addItem(output_path)
                self.output_path.setCurrentIndex(self.output_path.count() - 1)
                
            # Now set parameter
            self.param_model.set_parameter("output_path", output_path, emit_signal=False)
        
        # Constraint configuration file
        constraint_config = self.settings.value("optimization/constraint_config", "")
        if constraint_config and os.path.exists(constraint_config):
            self.optimization_controller.load_constraint_configuration(constraint_config)
    
    def _save_settings(self):
        """Save current settings to QSettings."""
        logger.debug("Saving settings to QSettings")
        
        # Save from widget state, not parameter model, to ensure we have the latest values
        self.settings.setValue("optimization/objective_index", self.objective_combo.currentIndex())
        self.settings.setValue("optimization/solver_index", self.solver_combo.currentIndex())
        self.settings.setValue("optimization/time_limit", self.time_limit.value())
        self.settings.setValue("optimization/gap", self.gap.value())
        self.settings.setValue("optimization/limit_to_demand", self.limit_to_demand.isChecked())
        self.settings.setValue("optimization/debug_mode", self.debug_mode.isChecked())
        self.settings.setValue("optimization/output_path", self.output_path.currentText())
        self.settings.setValue("optimization/export_format", self.export_format.currentIndex())
    
    def _run_optimization(self):
        """Run the optimization with the current settings."""
        logger.debug("Running optimization")
        
        # Save settings
        self._save_settings()
        
        # Get data files from data view or from parameter model
        data_params = self.param_registry.get_model("data")
        
        # Check if all required data files are set
        missing_files = []
        for key in ["demand_file", "supply_file", "cost_file", "wpp_file", "combinations_file"]:
            if not data_params.get_parameter(key):
                missing_files.append(key)
        
        if missing_files:
            missing_str = ", ".join(missing_files)
            QMessageBox.warning(
                self, 
                "Missing Files", 
                f"The following required data files are missing: {missing_str}\n"
                f"Please configure them in the Data tab."
            )
            return
        
        # Start optimization using parameter model values
        self.optimization_controller.start_optimization()
    
    def _load_data(self):
        """
        Load data from the data view and configure constraints.
        """
        logger.debug("Loading data from data view")
        
        # Get data parameters
        data_params = self.param_registry.get_model("data")
        
        # Check if all required data files are set
        missing_files = []
        for key in ["demand_file", "supply_file", "cost_file", "wpp_file", "combinations_file"]:
            file_path = data_params.get_parameter(key)
            if not file_path or not os.path.exists(file_path):
                missing_files.append(key)
        
        if missing_files:
            logger.debug(f"Missing data files: {missing_files}")
            return  # Don't attempt to load incomplete data
        
        # Load data through controller to ensure consistent handling
        self.optimization_controller.load_data()
    
    def _cancel_optimization(self):
        """Cancel the running optimization."""
        logger.debug("Cancelling optimization")
        self.optimization_controller.cancel_optimization()
    
    def _on_optimization_started(self):
        """Handle optimization started event."""
        logger.debug("Optimization started")
        self.optimization_status.start_optimization(self.time_limit.value())
        self.action_button.setEnabled(False)
    
    def _on_optimization_progress(self, value, status_text, gap, iterations):
        """Handle optimization progress event."""
        logger.debug(f"Optimization progress: {value}%, status: {status_text}, gap: {gap}")
        
        # Direct handling of special status messages
        if status_text == "OPTIMIZATION COMPLETE - OPTIMAL SOLUTION FOUND":
            # For final optimal status, ensure 100% progress
            self.optimization_status.progress_bar.setValue(100)
            self.optimization_status.status_label.setText(status_text)
            # Force immediate event processing
            QCoreApplication.processEvents()
        else:
            # Normal progress update
            self.optimization_status.update_progress(value, status_text, gap, iterations)
    
    def _on_optimization_error(self, error_msg):
        """Handle optimization error event."""
        logger.error(f"Optimization error: {error_msg}")
        
        # First ensure UI is updated consistently
        error_message = f"Error: {error_msg}"
        
        # Atomic update: Update both progress and status together
        self.optimization_status.update_progress(
            self.optimization_status.progress_bar.value(),  # Keep current value
            error_message,
            None,  # Don't update gap
            None   # Don't update iterations
        )
        
        # Then finish optimization with failure status
        self.optimization_status.finish_optimization(False, error_message)
        
        # Reset UI state to allow new optimization
        self.action_button.setEnabled(True)
        
        # Notify user
        QMessageBox.critical(
            self,
            "Optimization Error",
            f"An error occurred during optimization:\n{error_msg}\n\n"
            f"You can try adjusting optimization parameters or check input data."
        )
    
    def _on_optimization_completed(self, results):
        """Handle optimization completed event."""
        logger.debug(f"Optimization completed with status: {results.get('status', 'unknown')}")
        
        status = results.get('status', 'unknown')
        objective_value = results.get('objective_value', 0)
        objective_type = self.objective_combo.currentText().lower()
        gap = results.get('gap', 0)
        
        # Save results in parameter model
        self.param_model.set_parameter("results", results, emit_signal=False)
        
        # Always enable the action button first to prevent UI lockup
        self.action_button.setEnabled(True)
        
        # Force the UI to update by directly manipulating the status widget based on optimization status
        if status.upper() == 'OPTIMAL':
            # For optimal solutions, force 100% progress and success message
            message = f"Optimization complete - Optimal solution found (Gap: {gap:.2%})"
            
            # Direct widget manipulation to ensure consistent state
            logger.debug("Setting optimization to complete state with 100% progress")
            self.optimization_status.progress_bar.setValue(100)
            self.optimization_status.status_label.setText(message)
            self.optimization_status.cancel_button.setEnabled(False)
            self.optimization_status.timer.stop()
            
            # Force immediate event processing
            QCoreApplication.processEvents()
            
            logger.debug("Displaying success message box")
            QMessageBox.information(
                self,
                "Optimization Complete",
                f"Optimization completed successfully!\n"
                f"Objective ({objective_type}): {objective_value}\n"
                f"Solution status: {status}\n"
                f"Solve time: {results.get('solve_time', 0):.2f} seconds"
            )
            
            # Switch to results view
            if self.main_window:
                logger.debug("Switching to results view")
                self.main_window._switch_view("results")
                
                # Update results view if possible
                if hasattr(self.main_window, 'results_view'):
                    self.main_window.results_view.set_results(results)
        else:
            # For non-optimal solutions, ensure consistent state
            message = f"Optimization incomplete - Status: {status}"
            
            # Direct widget manipulation to ensure consistent state
            logger.debug(f"Setting optimization to incomplete state with current progress")
            self.optimization_status.status_label.setText(message)
            self.optimization_status.cancel_button.setEnabled(False)
            self.optimization_status.timer.stop()
            
            # Force immediate event processing
            QCoreApplication.processEvents()
            
            logger.debug("Displaying warning message box")
            QMessageBox.warning(
                self,
                "Optimization Incomplete",
                f"Optimization did not find an optimal solution.\n"
                f"Status: {status}\n"
                f"Message: {results.get('message', 'No additional information')}"
            )
    
    def _browse_output_path(self):
        """Open file dialog to select output file path."""
        current_path = self.output_path.currentText()
        start_dir = os.path.dirname(current_path) if current_path else "data/output"
        
        # Create directory if it doesn't exist
        os.makedirs(start_dir, exist_ok=True)
        
        # Get file format from export format combo
        file_format = self.export_format.currentData()
        filter_text = "Excel Files (*.xlsx)" if file_format == "xlsx" else "CSV Files (*.csv)"
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Optimization Results",
            os.path.join(start_dir, f"waffle_optimization.{file_format}"),
            filter_text
        )
        
        if file_path:
            # Update combo box
            index = self.output_path.findText(file_path)
            if index >= 0:
                self.output_path.setCurrentIndex(index)
            else:
                self.output_path.addItem(file_path)
                self.output_path.setCurrentIndex(self.output_path.count() - 1)
                
            # Update parameter model
            self.param_model.set_parameter("output_path", file_path)
            
    def update_constraint_options(self):
        """
        Update the constraint options based on the available constraints from the parameter model.
        """
        try:
            # Get data model from parameter registry
            data_model = self.param_registry.get_model('data')
            
            # Get available constraints from the parameter model
            constraints = data_model.get_parameter('available_constraints')
            
            if constraints:
                # Update the constraint manager with the new constraints
                self.constraint_manager._update_constraints(constraints) 
                
                # Update the constraint selection widget
                self._populate_constraint_selection()
                
                logger.debug(f"Updated constraint options with {len(constraints)} constraints")
        except Exception as e:
            logger.error(f"Error updating constraint options: {e}")
            QMessageBox.critical(
                self,
                "Error Updating Constraints",
                f"Failed to update constraint options: {str(e)}"
            ) 