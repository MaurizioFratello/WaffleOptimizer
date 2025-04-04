"""
Optimization view for configuring and running optimizations.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFormLayout, QComboBox, 
                          QSlider, QCheckBox, QGroupBox, QSpinBox,
                          QDoubleSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QSettings

from ..controllers.optimization_controller import OptimizationController
from ..widgets.optimization_status import OptimizationStatus

class OptimizationView(QWidget):
    """
    View for configuring and running waffle production optimizations.
    """
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("WaffleOptimizer", "WaffleOptimizerGUI")
        
        # Create optimization controller
        self.optimization_controller = OptimizationController()
        
        # Connect controller signals
        self.optimization_controller.optimization_started.connect(self._on_optimization_started)
        self.optimization_controller.optimization_progress.connect(self._on_optimization_progress)
        self.optimization_controller.optimization_error.connect(self._on_optimization_error)
        self.optimization_controller.optimization_completed.connect(self._on_optimization_completed)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        header = QLabel("Optimization Configuration")
        header.setObjectName("viewHeader")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        self.layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Configure the optimization settings and run the waffle production optimizer."
        )
        description.setWordWrap(True)
        self.layout.addWidget(description)
        
        # Create settings group
        settings_group = QGroupBox("Optimization Settings")
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
        
        self.layout.addWidget(settings_group)
        
        # Output file setting
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        
        # Output file path - we can use FileSelector later if needed
        self.output_path = QComboBox()
        self.output_path.setEditable(True)
        self.output_path.addItem("data/output/waffle_solution.xlsx")
        self.output_path.addItem("data/output/optimization_results.xlsx")
        output_layout.addRow("Output File:", self.output_path)
        
        self.layout.addWidget(output_group)
        
        # Optimization status
        status_group = QGroupBox("Optimization Status")
        status_layout = QVBoxLayout(status_group)
        
        self.optimization_status = OptimizationStatus()
        self.optimization_status.cancelled.connect(self._cancel_optimization)
        
        status_layout.addWidget(self.optimization_status)
        self.layout.addWidget(status_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Optimization")
        self.run_button.clicked.connect(self._run_optimization)
        
        self.view_results_button = QPushButton("View Results")
        self.view_results_button.clicked.connect(
            lambda: self.main_window._switch_view("results"))
        self.view_results_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.view_results_button)
        
        self.layout.addLayout(button_layout)
        
        # Load saved settings
        self._load_settings()
    
    def _load_settings(self):
        """Load saved settings from QSettings."""
        # Objective
        objective_index = self.settings.value("optimization/objective_index", 0, int)
        if 0 <= objective_index < self.objective_combo.count():
            self.objective_combo.setCurrentIndex(objective_index)
        
        # Solver
        solver_index = self.settings.value("optimization/solver_index", 0, int)
        if 0 <= solver_index < self.solver_combo.count():
            self.solver_combo.setCurrentIndex(solver_index)
        
        # Time limit
        time_limit = self.settings.value("optimization/time_limit", 60, int)
        self.time_limit.setValue(time_limit)
        
        # Gap
        gap = self.settings.value("optimization/gap", 0.005, float)
        self.gap.setValue(gap)
        
        # Limit to demand
        limit_to_demand = self.settings.value("optimization/limit_to_demand", True, bool)
        self.limit_to_demand.setChecked(limit_to_demand)
        
        # Debug mode
        debug_mode = self.settings.value("optimization/debug_mode", False, bool)
        self.debug_mode.setChecked(debug_mode)
        
        # Output path
        output_path = self.settings.value("optimization/output_path", "")
        if output_path:
            index = self.output_path.findText(output_path)
            if index >= 0:
                self.output_path.setCurrentIndex(index)
            else:
                self.output_path.addItem(output_path)
                self.output_path.setCurrentIndex(self.output_path.count() - 1)
    
    def _save_settings(self):
        """Save current settings to QSettings."""
        self.settings.setValue("optimization/objective_index", self.objective_combo.currentIndex())
        self.settings.setValue("optimization/solver_index", self.solver_combo.currentIndex())
        self.settings.setValue("optimization/time_limit", self.time_limit.value())
        self.settings.setValue("optimization/gap", self.gap.value())
        self.settings.setValue("optimization/limit_to_demand", self.limit_to_demand.isChecked())
        self.settings.setValue("optimization/debug_mode", self.debug_mode.isChecked())
        self.settings.setValue("optimization/output_path", self.output_path.currentText())
    
    def _run_optimization(self):
        """Run the optimization with the current settings."""
        # Save settings
        self._save_settings()
        
        # Get data files from data view
        if not self.main_window or not hasattr(self.main_window, 'data_view'):
            QMessageBox.warning(
                self, 
                "Missing Data", 
                "Please configure data files in the Data tab first."
            )
            return
        
        data_paths = self.main_window.data_view.get_data_paths()
        
        # Check if all required data files are set
        missing_files = [key for key, path in data_paths.items() 
                       if not path or not path.strip()]
        
        if missing_files:
            missing_str = ", ".join(missing_files)
            QMessageBox.warning(
                self, 
                "Missing Files", 
                f"The following required data files are missing: {missing_str}\n"
                f"Please configure them in the Data tab."
            )
            return
        
        # Create optimization config
        config = {
            # Data files
            "demand": data_paths.get("demand", ""),
            "supply": data_paths.get("supply", ""),
            "cost": data_paths.get("cost", ""),
            "wpp": data_paths.get("wpp", ""),
            "combinations": data_paths.get("combinations", ""),
            
            # Optimization settings
            "objective": self.objective_combo.currentData(),
            "solver": self.solver_combo.currentData(),
            "time_limit": self.time_limit.value(),
            "gap": self.gap.value(),
            "limit_to_demand": self.limit_to_demand.isChecked(),
            "debug": self.debug_mode.isChecked(),
            
            # Output settings
            "output": self.output_path.currentText()
        }
        
        # Start optimization
        self.optimization_controller.start_optimization(config)
    
    def _cancel_optimization(self):
        """Cancel the running optimization."""
        self.optimization_controller.cancel_optimization()
        self.optimization_status.update_progress(0, "Optimization cancelled")
    
    def _on_optimization_started(self):
        """Handle optimization started signal."""
        self.run_button.setEnabled(False)
        self.view_results_button.setEnabled(False)
        self.optimization_status.start_optimization(self.time_limit.value())
    
    def _on_optimization_progress(self, value, status_text, gap, iterations):
        """Handle optimization progress signal."""
        self.optimization_status.update_progress(value, status_text, gap, iterations)
    
    def _on_optimization_error(self, error_msg):
        """Handle optimization error signal."""
        self.optimization_status.finish_optimization(False, "Optimization failed")
        QMessageBox.critical(
            self, 
            "Optimization Error", 
            f"An error occurred during optimization:\n{error_msg}"
        )
        self.run_button.setEnabled(True)
    
    def _on_optimization_completed(self, results):
        """Handle optimization completed signal."""
        # Update status
        gap = results.get("gap", 0)
        status = results.get("status", "Unknown")
        
        if status == "Optimal":
            message = f"Optimization complete - Optimal solution found (Gap: {gap:.2%})"
        elif status == "Feasible":
            message = f"Optimization complete - Feasible solution found (Gap: {gap:.2%})"
        else:
            message = f"Optimization complete - Status: {status}"
        
        self.optimization_status.finish_optimization(True, message)
        
        # Enable buttons
        self.run_button.setEnabled(True)
        self.view_results_button.setEnabled(True)
        
        # Show results message
        objective = self.objective_combo.currentText()
        value = results.get("objective_value", 0)
        
        QMessageBox.information(
            self,
            "Optimization Complete",
            f"The optimization has completed successfully.\n\n"
            f"Objective ({objective}): {value:.2f}\n"
            f"Status: {status}\n"
            f"Optimality Gap: {gap:.2%}\n\n"
            f"Click 'View Results' to see the detailed results."
        ) 