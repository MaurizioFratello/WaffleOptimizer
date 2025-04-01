"""
Configuration tab for the waffle optimizer GUI.

This module contains the ConfigurationTab class which is the main tab for
configuring the waffle optimizer.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton,
    QScrollArea, QRadioButton, QCheckBox, QComboBox, QGridLayout, QSplitter,
    QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
import sys
import os

# Import core functionality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_processor import DataProcessor
from core.feasibility_check import FeasibilityChecker
from core.solver_interface import SolverFactory

# Import custom widgets
from gui.widgets.data_upload import DataUploadWidget
from gui.widgets.feasibility_view import FeasibilityView


class ConfigurationTab(QWidget):
    """Configuration tab for the waffle optimizer GUI."""
    
    # Signal emitted when a solution is ready
    solution_ready = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the configuration tab."""
        super().__init__()
        
        # Initialize core components
        self.data_processor = DataProcessor()
        self.feasibility_checker = None
        self.solver = None
        
        # Initialize data
        self.data_loaded = False
        self.feasibility_result = None
        
        # Set up UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Create horizontal splitter for the main layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Config panel
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # Data upload section
        self.data_upload = DataUploadWidget()
        self.data_upload.files_updated.connect(self._on_files_updated)
        config_layout.addWidget(self.data_upload)
        
        # Model configuration section
        model_group = QGroupBox("Model Configuration")
        model_layout = QGridLayout()
        
        # Objective selection
        model_layout.addWidget(QLabel("Optimization Objective:"), 0, 0)
        
        self.objective_cost = QRadioButton("Minimize Cost")
        self.objective_cost.setChecked(True)
        model_layout.addWidget(self.objective_cost, 0, 1)
        
        self.objective_output = QRadioButton("Maximize Output")
        model_layout.addWidget(self.objective_output, 1, 1)
        
        # Demand constraint
        model_layout.addWidget(QLabel("Demand Handling:"), 2, 0)
        
        self.demand_constraint = QCheckBox("Limit production to demand")
        self.demand_constraint.setChecked(True)
        model_layout.addWidget(self.demand_constraint, 2, 1)
        
        # Solver selection
        model_layout.addWidget(QLabel("Solver:"), 3, 0)
        
        self.solver_selector = QComboBox()
        self.solver_selector.addItems(["OR-Tools"])
        model_layout.addWidget(self.solver_selector, 3, 1)
        
        model_group.setLayout(model_layout)
        config_layout.addWidget(model_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self._load_data)
        action_layout.addWidget(self.load_button)
        
        self.check_button = QPushButton("Check Feasibility")
        self.check_button.setEnabled(False)
        self.check_button.clicked.connect(self._check_feasibility)
        action_layout.addWidget(self.check_button)
        
        config_layout.addLayout(action_layout)
        
        # Debug log section
        debug_group = QGroupBox("Debug Log")
        debug_layout = QVBoxLayout()
        self.debug_log = QTextEdit()
        self.debug_log.setReadOnly(True)
        self.debug_log.setMaximumHeight(200)  # Limit height to not take too much space
        debug_layout.addWidget(self.debug_log)
        debug_group.setLayout(debug_layout)
        config_layout.addWidget(debug_group)
        
        # Add stretch to push everything to the top
        config_layout.addStretch()
        
        # Add left side to splitter
        main_splitter.addWidget(config_widget)
        
        # Right side - Feasibility visualization
        self.feasibility_view = FeasibilityView()
        self.feasibility_view.run_optimization.connect(self._run_optimization)
        main_splitter.addWidget(self.feasibility_view)
        
        # Set initial splitter sizes (40% left, 60% right)
        main_splitter.setSizes([400, 600])
        
        # Add the splitter to the main layout
        layout.addWidget(main_splitter)
    
    def _log_debug(self, message: str):
        """Add a debug message to the log window."""
        self.debug_log.append(message)
    
    def _on_files_updated(self, file_paths):
        """
        Handle updates to file paths.
        
        Args:
            file_paths: Dictionary of file paths.
        """
        # Reset data loaded flag
        self.data_loaded = False
        self.check_button.setEnabled(False)
        self._log_debug("Files updated, data loaded flag reset")
    
    def _load_data(self):
        """Load data from selected files."""
        file_paths = self.data_upload.get_file_paths()
        
        try:
            # Show loading cursor
            self.setCursor(Qt.CursorShape.WaitCursor)
            
            # Clear debug log
            self.debug_log.clear()
            self._log_debug("Starting data load...")
            
            # Load data
            self.data_processor.load_data(
                file_paths["demand"], 
                file_paths["supply"], 
                file_paths["cost"], 
                file_paths["wpp"], 
                file_paths["combinations"]
            )
            
            # Reset cursor
            self.unsetCursor()
            
            # Update flags and UI
            self.data_loaded = True
            self.check_button.setEnabled(True)
            
            # Create feasibility checker
            self._log_debug("Creating feasibility checker...")
            feasibility_data = self.data_processor.get_feasibility_data()
            self._log_debug(f"Feasibility data keys: {list(feasibility_data.keys())}")
            self.feasibility_checker = FeasibilityChecker(feasibility_data)
            
            # Show success message
            QMessageBox.information(self, "Data Loaded", "Data loaded successfully!")
            
        except Exception as e:
            # Reset cursor
            self.unsetCursor()
            
            # Show error message
            error_msg = f"Error loading data: {str(e)}"
            self._log_debug(f"ERROR: {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def _check_feasibility(self):
        """Check the feasibility of the problem."""
        if not self.data_loaded or self.feasibility_checker is None:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return
        
        try:
            # Show loading cursor
            self.setCursor(Qt.CursorShape.WaitCursor)
            
            self._log_debug("Starting feasibility check...")
            
            # Check feasibility and get result summary
            self.feasibility_checker.check_feasibility()
            self.feasibility_result = self.feasibility_checker.get_result_summary()
            
            # Add additional data needed for visualization if not already present
            self._log_debug(f"Processing feasibility data for visualization...")
            
            # Only update with additional data if needed
            if 'total_demand' not in self.feasibility_result or 'total_supply' not in self.feasibility_result:
                self._log_debug("Missing core data for visualization, retrieving from data processor")
                data = self.data_processor.get_feasibility_data()
                
                # Add missing data
                if 'total_demand' not in self.feasibility_result:
                    self.feasibility_result['total_demand'] = data['total_demand']
                if 'total_supply' not in self.feasibility_result:
                    self.feasibility_result['total_supply'] = data['total_supply']
                if 'weeks' not in self.feasibility_result:
                    self.feasibility_result['weeks'] = data['weeks']
                if 'waffle_types' not in self.feasibility_result:
                    self.feasibility_result['waffle_types'] = data['waffle_types']
                if 'pan_types' not in self.feasibility_result:
                    self.feasibility_result['pan_types'] = data['pan_types']
            
            # Add additional computed data for visualization
            waffle_types = self.feasibility_result.get('waffle_types', self.data_processor.waffle_types)
            pan_types = self.feasibility_result.get('pan_types', self.data_processor.pan_types)
            weeks = self.feasibility_result.get('weeks', self.data_processor.weeks)
            
            # Get the needed dictionaries from data processor for computed values
            demand_dict = self.data_processor.demand_dict
            supply_dict = self.data_processor.supply_dict
            allowed_dict = self.data_processor.allowed_dict
            
            self.feasibility_result['total_potential_production'] = sum(self.feasibility_result.get('total_supply', {}).values())
            
            # Add waffle analysis
            self.feasibility_result['waffle_analysis'] = {
                wt: {
                    'demand': sum(demand_dict.get((wt, week), 0) for week in weeks),
                    'potential_production': sum(supply_dict.get((pt, week), 0) 
                                              for pt in pan_types 
                                              for week in weeks 
                                              if allowed_dict.get((wt, pt), False)),
                    'feasible': any(allowed_dict.get((wt, pt), False) for pt in pan_types)
                }
                for wt in waffle_types
            }
            
            # Add pan allocation
            self.feasibility_result['pan_allocation'] = {
                pt: sum(supply_dict.get((pt, week), 0) for week in weeks)
                for pt in pan_types
            }
            
            # Add waffle-pan mappings
            self.feasibility_result['waffle_pan_mappings'] = {
                wt: [pt for pt in pan_types if allowed_dict.get((wt, pt), False)]
                for wt in waffle_types
            }
            
            # Reset cursor
            self.unsetCursor()
            
            # Display results
            self.feasibility_view.display_feasibility_result(self.feasibility_result)
            self._log_debug("Feasibility check completed successfully")
            
        except Exception as e:
            # Reset cursor
            self.unsetCursor()
            
            # Show error message
            error_msg = f"Error checking feasibility: {str(e)}"
            self._log_debug(f"ERROR: {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def _run_optimization(self):
        """Run the optimization based on configuration."""
        if not self.data_loaded:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return
        
        if self.feasibility_result is None:
            QMessageBox.warning(self, "Warning", "Please check feasibility first.")
            return
        
        # Get optimization parameters
        objective = "minimize_cost" if self.objective_cost.isChecked() else "maximize_output"
        limit_to_demand = self.demand_constraint.isChecked()
        solver_name = self.solver_selector.currentText()
        
        try:
            # Show loading cursor
            self.setCursor(Qt.CursorShape.WaitCursor)
            
            # Convert solver name to the expected format
            if solver_name == "OR-Tools":
                solver_name = "ortools"
            else:
                solver_name = solver_name.lower().replace("-", "_")
            
            # Create solver
            self.solver = SolverFactory.create_solver(solver_name)
            
            # Get optimization data
            data = self.data_processor.get_optimization_data()
            
            # Build and solve model
            if objective == "minimize_cost":
                self.solver.build_minimize_cost_model(data)
            else:  # maximize_output
                self.solver.build_maximize_output_model(data, limit_to_demand=limit_to_demand)
            
            # Solve the problem
            solution = self.solver.solve_model()
            
            # Reset cursor
            self.unsetCursor()
            
            # Emit the solution
            if solution and solution['status'] in ['OPTIMAL', 'FEASIBLE']:
                # Get the solution details
                solution_details = self.solver.get_solution()
                
                # Add some extra information to the solution
                solution_details['demands'] = data['demand']
                solution_details['supplies'] = data['supply']
                solution_details['objective'] = objective
                solution_details['status'] = solution['status']
                solution_details['wall_time'] = solution['wall_time']
                
                # Add cost and wpp data to the solution for detailed cost analysis
                solution_details['cost'] = data['cost']
                solution_details['wpp'] = data['wpp']
                
                # Emit the solution
                self.solution_ready.emit(solution_details)
                
                # Show success message
                QMessageBox.information(
                    self, 
                    "Optimization Complete", 
                    "Optimization completed successfully!"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Warning", 
                    "The solver could not find a solution."
                )
            
        except Exception as e:
            # Reset cursor
            self.unsetCursor()
            
            # Show error message
            QMessageBox.critical(self, "Error", f"Error running optimization: {str(e)}") 