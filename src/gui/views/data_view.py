"""
Data configuration view for the Waffle Optimizer GUI.
"""
import os
import logging
import pandas as pd
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFormLayout, QTabWidget,
                          QGroupBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings

from ..parameter_aware_view import ParameterAwareView
from ..widgets.file_selector import FileSelector
from ..widgets.data_table import DataTable
from src.models.parameter_registry import ParameterRegistry

logger = logging.getLogger(__name__)

def format_cost_value(value):
    """
    Format a cost value to two decimal places with € symbol.
    
    Args:
        value: The value to format
        
    Returns:
        Formatted string with € symbol
    """
    try:
        # Convert to float and format
        return f"{float(value):.2f} €"
    except (ValueError, TypeError):
        # Return original value if not a number
        return str(value)

class DataView(ParameterAwareView):
    """
    View for configuring data input files and previewing data.
    """
    data_ready = pyqtSignal(dict)  # Signal when data is loaded and validated
    data_loaded = pyqtSignal()     # Signal when any data file is loaded or changed
    
    def __init__(self, main_window=None):
        super().__init__(
            title="Data Configuration",
            description="Configure the input data files for waffle production optimization. "
                      "All files should be in Excel (.xlsx) format.",
            main_window=main_window,
            action_button_text="Check Data Completeness",
            model_name="data"
        )
        
        # Connect action button
        self.action_button.clicked.connect(self._validate_data)
        
        self.settings = QSettings("WaffleOptimizer", "WaffleOptimizerGUI")
        
        # Initialize data components
        self._init_data_components()
        
        # Set up parameter bindings
        self._setup_parameter_bindings()
        
        # Connect to parameter changes
        self.param_model.parameter_changed.connect(self._on_parameter_changed)
        
        logger.debug("Initialized data view")
    
    def _init_data_components(self):
        """Initialize data view specific components."""
        # Create file selectors group
        files_group = self.create_group_box("Input Files")
        form_layout = QFormLayout(files_group)
        
        # File selectors - save references for getting values later
        self.file_selectors = {}
        
        # Excel filter
        excel_filter = "Excel Files (*.xlsx)"
        
        file_configs = [
            ("demand", "Demand Data", "Select waffle demand file"),
            ("supply", "Supply Data", "Select pan supply file"),
            ("cost", "Cost Data", "Select waffle cost per pan file"),
            ("wpp", "Waffles Per Pan", "Select waffles per pan file"),
            ("combinations", "Combinations", "Select waffle-pan combinations file")
        ]
        
        for key, label, placeholder in file_configs:
            selector = FileSelector(placeholder=placeholder, filter=excel_filter)
            self.file_selectors[key] = selector
            
            # Try to load last used path from settings
            last_path = self.settings.value(f"last_path_{key}", "")
            if last_path and os.path.exists(last_path):
                selector.set_file_path(last_path)
            
            # No longer needed - we handle connections in _setup_parameter_bindings
            # When file is selected, update preview if possible
            # selector.file_selected.connect(
            #     lambda path, k=key: self._update_preview(k, path))
            
            form_layout.addRow(label + ":", selector)
        
        self.content_layout.addWidget(files_group)
        
        # Data preview
        preview_group = self.create_group_box("Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_tabs = QTabWidget()
        
        # Create preview tabs for each data type
        self.preview_tables = {}
        for key, label, _ in file_configs:
            table = DataTable()
            # Set formatting function for cost data
            if key == "cost":
                table.set_format_function(format_cost_value)
            self.preview_tables[key] = table
            self.preview_tabs.addTab(table, label)
        
        preview_layout.addWidget(self.preview_tabs)
        self.content_layout.addWidget(preview_group)
        
        # Use default data checkbox 
        self.use_default_data = QCheckBox("Use default data from data directory")
        self.use_default_data.setChecked(False)
        self.use_default_data.toggled.connect(self._toggle_default_data)
        self.content_layout.addWidget(self.use_default_data)
        
        # Add spacer at the bottom
        self.content_layout.addStretch()
        
        # Check if data is already loaded and emit signal
        self._check_data_loaded()
    
    def _setup_parameter_bindings(self):
        """Set up bindings between UI components and parameter model."""
        logger.debug("Setting up parameter bindings")
        
        # Map keys to parameter names
        param_map = {
            "demand": "demand_file",
            "supply": "supply_file",
            "cost": "cost_file",
            "wpp": "wpp_file",
            "combinations": "combinations_file"
        }
        
        # Set up file selectors by connecting to our custom handler that handles both
        # parameter updates and preview updates
        for key, param_name in param_map.items():
            if key in self.file_selectors:
                # Clear existing connections
                try:
                    self.file_selectors[key].file_selected.disconnect()
                except Exception:
                    pass
                
                # Connect to our custom handler 
                self.file_selectors[key].file_selected.connect(
                    lambda path, k=key, pname=param_name: self._handle_file_selected(k, path, pname)
                )
                
                # Load initial value from parameter model
                value = self.param_model.get_parameter(param_name)
                if value is not None and os.path.exists(value):
                    self.file_selectors[key].set_file_path(value)
                    self._update_preview(key, value)
    
    def _handle_file_selected(self, key, path, param_name):
        """
        Handle file selection - update both parameter model and preview.
        
        Args:
            key: File selector key (demand, supply, etc.)
            path: Selected file path
            param_name: Parameter name in the model
        """
        logger.debug(f"File selected for {key}: {path}")
        
        # Update parameter model
        self.param_model.set_parameter(param_name, path)
        
        # Update preview
        self._update_preview(key, path)
    
    def _on_parameter_changed(self, name, value):
        """
        Handle parameter model changes.
        
        Args:
            name: Parameter name
            value: New value
        """
        logger.debug(f"Parameter changed: {name} = {value}")
        
        # Check if it's a file parameter change
        if name in ["demand_file", "supply_file", "cost_file", "wpp_file", "combinations_file"]:
            # Get file selector key from parameter name
            key = name.replace("_file", "")
            
            # Update UI if needed
            if key in self.file_selectors:
                file_selector = self.file_selectors[key]
                
                # Only update if different
                if file_selector.get_file_path() != value:
                    file_selector.set_file_path(value)
                    
                    # Update preview
                    if value:
                        self._update_preview(key, value)
                        
            # Check if all data is loaded now
            self._check_data_loaded()
    
    def _update_preview(self, data_type, file_path):
        """
        Update the data preview for the selected file.
        
        Args:
            data_type: Type of data (demand, supply, etc.)
            file_path: Path to the data file
        """
        # Save the path in settings
        self.settings.setValue(f"last_path_{data_type}", file_path)
        
        # Update parameter model (parameter name has _file suffix)
        param_name = f"{data_type}_file"
        self.param_model.set_parameter(param_name, file_path)
        
        # Try to load and preview the data
        try:
            if file_path and os.path.exists(file_path):
                logger.debug(f"Loading preview for {data_type} from {file_path}")
                df = pd.read_excel(file_path)
                self.preview_tables[data_type].load_dataframe(df)
                
                # Switch to the tab for this data type
                for i in range(self.preview_tabs.count()):
                    if self.preview_tabs.tabText(i).lower().startswith(data_type):
                        self.preview_tabs.setCurrentIndex(i)
                        break
                
                # Check if all required data is loaded
                self._check_data_loaded()
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading {data_type} data: {error_msg}")
            QMessageBox.warning(
                self, 
                "Error Loading Data", 
                f"Failed to load data from {file_path}:\n{error_msg}"
            )
            # Clear the preview
            self.preview_tables[data_type].clear()
    
    def _check_data_loaded(self):
        """
        Check if all required data files are loaded and emit signal if they are.
        """
        # Get file paths from parameter model
        paths = self.get_data_paths()
        required_files = ["demand", "supply", "cost", "wpp", "combinations"]
        
        # Check if all required files exist
        all_loaded = all(
            paths.get(key) and os.path.exists(paths.get(key))
            for key in required_files
        )
        
        if all_loaded:
            logger.debug("All required data files loaded, emitting data_loaded signal")
            self.data_loaded.emit()
    
    def _toggle_default_data(self, checked):
        """
        Toggle between default data and custom data selection.
        
        Args:
            checked: Whether to use default data
        """
        logger.debug(f"Toggling default data: {checked}")
        
        if checked:
            # Set the file selectors to the default data paths
            default_paths = {
                "demand": "data/input/WaffleDemand.xlsx",
                "supply": "data/input/PanSupply.xlsx", 
                "cost": "data/input/WaffleCostPerPan.xlsx",
                "wpp": "data/input/WafflesPerPan.xlsx",
                "combinations": "data/input/WafflePanCombinations.xlsx"
            }
            
            for key, path in default_paths.items():
                # Check if the default file exists
                if os.path.exists(path):
                    # Update both file selector and parameter model
                    self.file_selectors[key].set_file_path(path)
                    self.param_model.set_parameter(f"{key}_file", path)
                    
                    # Explicitly update the preview
                    self._update_preview(key, path)
                else:
                    QMessageBox.warning(
                        self,
                        "Default File Not Found",
                        f"The default file for {key} was not found at {path}"
                    )
        
        # Enable/disable file selectors based on checkbox
        for selector in self.file_selectors.values():
            selector.setEnabled(not checked)
            
        # Check if data is loaded
        self._check_data_loaded()
    
    def _validate_data(self):
        """Validate the selected data files."""
        logger.debug("Validating data files")
        
        # Get all file paths from parameter model
        file_paths = self.get_data_paths()
        
        # Check that all required files are selected
        missing_files = [key for key, path in file_paths.items() 
                       if not path or not os.path.exists(path)]
        
        if missing_files:
            missing_str = ", ".join(missing_files)
            QMessageBox.warning(
                self,
                "Missing Files",
                f"The following required files are missing: {missing_str}"
            )
            return
        
        # Basic file presence validation passed
        QMessageBox.information(
            self,
            "Basic Validation Successful",
            "All required data files are present. Go to the Validation tab for detailed analysis."
        )
        
        # Emit signal with the data paths
        self.data_ready.emit(file_paths)
        
        # Switch to validation tab if available
        if self.main_window and hasattr(self.main_window, '_switch_view'):
            self.main_window._switch_view("validation")
    
    def get_data_paths(self):
        """
        Get the current data file paths.
        
        Returns:
            dict: Dictionary of data file paths
        """
        # Get paths from parameter model rather than directly from file selectors
        return {
            "demand": self.param_model.get_parameter("demand_file", ""),
            "supply": self.param_model.get_parameter("supply_file", ""),
            "cost": self.param_model.get_parameter("cost_file", ""),
            "wpp": self.param_model.get_parameter("wpp_file", ""),
            "combinations": self.param_model.get_parameter("combinations_file", "")
        } 