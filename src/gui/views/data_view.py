"""
Data configuration view for the Waffle Optimizer GUI.
"""
import os
import pandas as pd
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFormLayout, QTabWidget,
                          QGroupBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings

from ..base_view import BaseView
from ..widgets.file_selector import FileSelector
from ..widgets.data_table import DataTable

class DataView(BaseView):
    """
    View for configuring data input files and previewing data.
    """
    data_ready = pyqtSignal(dict)  # Signal when data is loaded and validated
    
    def __init__(self, main_window=None):
        super().__init__(
            title="Data Configuration",
            description="Configure the input data files for waffle production optimization. "
                       "All files should be in Excel (.xlsx) format.",
            main_window=main_window
        )
        
        self.settings = QSettings("WaffleOptimizer", "WaffleOptimizerGUI")
        
        # Initialize data components
        self._init_data_components()
        
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
            
            # When file is selected, update preview if possible
            selector.file_selected.connect(
                lambda path, k=key: self._update_preview(k, path))
            
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
    
    def _update_preview(self, data_type, file_path):
        """
        Update the data preview for the selected file.
        
        Args:
            data_type: Type of data (demand, supply, etc.)
            file_path: Path to the data file
        """
        # Save the path in settings
        self.settings.setValue(f"last_path_{data_type}", file_path)
        
        # Try to load and preview the data
        try:
            if file_path and os.path.exists(file_path):
                df = pd.read_excel(file_path)
                self.preview_tables[data_type].load_dataframe(df)
                
                # Switch to the tab for this data type
                for i in range(self.preview_tabs.count()):
                    if self.preview_tabs.tabText(i).lower().startswith(data_type):
                        self.preview_tabs.setCurrentIndex(i)
                        break
                
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Error Loading Data", 
                f"Failed to load data from {file_path}:\n{str(e)}"
            )
            # Clear the preview
            self.preview_tables[data_type].clear()
    
    def _toggle_default_data(self, checked):
        """
        Toggle between default data and custom data selection.
        
        Args:
            checked: Whether to use default data
        """
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
                    self.file_selectors[key].set_file_path(path)
                else:
                    QMessageBox.warning(
                        self,
                        "Default File Not Found",
                        f"The default file for {key} was not found at {path}"
                    )
        
        # Enable/disable file selectors based on checkbox
        for selector in self.file_selectors.values():
            selector.setEnabled(not checked)
    
    def _validate_data(self):
        """Validate the selected data files."""
        # Get all file paths
        file_paths = {key: selector.get_file_path() 
                     for key, selector in self.file_selectors.items()}
        
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
    
    def get_data_paths(self):
        """
        Get the current data file paths.
        
        Returns:
            dict: Dictionary of data file paths
        """
        return {key: selector.get_file_path() 
                for key, selector in self.file_selectors.items()} 