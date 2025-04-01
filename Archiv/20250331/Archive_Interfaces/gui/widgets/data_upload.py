"""
Data upload widget for the waffle optimizer GUI.

This module contains the DataUploadWidget class which is used for uploading
and managing data files for the waffle optimizer.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QGroupBox, QGridLayout, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
import os


class DataUploadWidget(QWidget):
    """Widget for uploading and managing data files."""
    
    # Signal emitted when file paths are updated
    files_updated = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the data upload widget."""
        super().__init__()
        
        # Initial file paths (defaults)
        self.file_paths = {
            "demand": "WaffleDemand.xlsx",
            "supply": "PanSupply.xlsx",
            "cost": "WaffleCostPerPan.xlsx",
            "wpp": "WafflesPerPan.xlsx",
            "combinations": "WafflePanCombinations.xlsx"
        }
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Create group box
        group_box = QGroupBox("Data Files")
        group_layout = QGridLayout()
        
        # File sections
        file_types = {
            "demand": "Waffle Demand",
            "supply": "Pan Supply",
            "cost": "Waffle Cost",
            "wpp": "Waffles Per Pan",
            "combinations": "Waffle-Pan Combinations"
        }
        
        # Create file input widgets
        self.file_inputs = {}
        
        for i, (key, label) in enumerate(file_types.items()):
            # Label
            group_layout.addWidget(QLabel(f"{label}:"), i, 0)
            
            # Text field
            text_field = QLineEdit(self.file_paths[key])
            text_field.setReadOnly(True)
            self.file_inputs[key] = text_field
            group_layout.addWidget(text_field, i, 1)
            
            # Browse button
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(lambda checked, k=key: self._browse_file(k))
            group_layout.addWidget(browse_button, i, 2)
        
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        # Load defaults button
        defaults_button = QPushButton("Load Default Files")
        defaults_button.clicked.connect(self._load_defaults)
        layout.addWidget(defaults_button)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def _browse_file(self, file_key):
        """
        Open a file dialog to select a file.
        
        Args:
            file_key: The key of the file to select (e.g., "demand", "supply").
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {file_key.capitalize()} File",
            "",  # Start in the current directory
            "Excel Files (*.xlsx *.xls);;All Files (*)",
            options=options
        )
        
        if file_path:
            self.file_paths[file_key] = file_path
            self.file_inputs[file_key].setText(file_path)
            self.files_updated.emit(self.file_paths)
    
    def _load_defaults(self):
        """Load the default file paths."""
        defaults = {
            "demand": "WaffleDemand.xlsx",
            "supply": "PanSupply.xlsx",
            "cost": "WaffleCostPerPan.xlsx",
            "wpp": "WafflesPerPan.xlsx",
            "combinations": "WafflePanCombinations.xlsx"
        }
        
        self.file_paths = defaults.copy()
        
        for key, path in defaults.items():
            self.file_inputs[key].setText(path)
        
        self.files_updated.emit(self.file_paths)
    
    def get_file_paths(self):
        """
        Get the current file paths.
        
        Returns:
            dict: A dictionary containing file paths.
        """
        return self.file_paths 