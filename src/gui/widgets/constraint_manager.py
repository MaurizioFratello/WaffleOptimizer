"""
Constraint Manager Widget for configuring optimization constraints.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QCheckBox, QGroupBox, QScrollArea,
                          QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox,
                          QDialog, QDialogButtonBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ConstraintConfigDialog(QDialog):
    """
    Dialog for configuring a specific constraint's parameters.
    """
    def __init__(self, constraint_info, parent=None):
        super().__init__(parent)
        self.constraint_info = constraint_info
        self.config_values = {}
        
        # Set window properties
        self.setWindowTitle(f"Configure {constraint_info['name']} Constraint")
        self.setMinimumWidth(400)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Add description
        description = QLabel(constraint_info['description'])
        description.setWordWrap(True)
        main_layout.addWidget(description)
        
        # Create form for parameters
        form_group = QGroupBox("Parameters")
        form_layout = QFormLayout(form_group)
        
        # Get schema and current configuration
        schema = constraint_info.get('schema', {})
        current_config = constraint_info.get('config', {})
        
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                # Get property details
                prop_type = prop_schema.get('type', 'string')
                prop_title = prop_schema.get('title', prop_name)
                prop_description = prop_schema.get('description', '')
                current_value = current_config.get(prop_name)
                
                # Create appropriate widget based on type
                if prop_type == 'boolean':
                    widget = QCheckBox()
                    widget.setChecked(bool(current_value))
                    self.config_values[prop_name] = widget
                
                elif prop_type == 'integer':
                    widget = QSpinBox()
                    minimum = prop_schema.get('minimum', -999999)
                    maximum = prop_schema.get('maximum', 999999)
                    widget.setRange(int(minimum), int(maximum))
                    if current_value is not None:
                        widget.setValue(int(current_value))
                    self.config_values[prop_name] = widget
                
                elif prop_type == 'number':
                    widget = QDoubleSpinBox()
                    minimum = prop_schema.get('minimum', -999999.0)
                    maximum = prop_schema.get('maximum', 999999.0)
                    widget.setRange(float(minimum), float(maximum))
                    widget.setDecimals(4)
                    widget.setSingleStep(0.01)
                    if current_value is not None:
                        widget.setValue(float(current_value))
                    self.config_values[prop_name] = widget
                
                elif prop_type == 'string' and 'enum' in prop_schema:
                    widget = QComboBox()
                    for option in prop_schema['enum']:
                        widget.addItem(str(option))
                    if current_value is not None:
                        index = widget.findText(str(current_value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    self.config_values[prop_name] = widget
                
                else:  # Default to string or unsupported types
                    continue  # Skip unsupported types for now
                
                # Add tooltip if description available
                if prop_description:
                    widget.setToolTip(prop_description)
                
                # Add row to form
                form_layout.addRow(QLabel(prop_title), widget)
        
        main_layout.addWidget(form_group)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def get_configuration(self):
        """
        Get the configuration values from the dialog.
        
        Returns:
            dict: Configuration values
        """
        config = {}
        
        for prop_name, widget in self.config_values.items():
            if isinstance(widget, QCheckBox):
                config[prop_name] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                config[prop_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                config[prop_name] = widget.value()
            elif isinstance(widget, QComboBox):
                config[prop_name] = widget.currentText()
        
        return config


class ConstraintManager(QWidget):
    """
    Widget for managing constraint configurations.
    """
    constraint_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize attributes
        self.controller = None
        self.constraints = []
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for constraints
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create widget to hold constraints
        self.constraints_widget = QWidget()
        self.constraints_layout = QVBoxLayout(self.constraints_widget)
        self.constraints_layout.setContentsMargins(0, 0, 0, 0)
        self.constraints_layout.setSpacing(10)
        
        # Add constraints widget to scroll area
        self.scroll_area.setWidget(self.constraints_widget)
        self.main_layout.addWidget(self.scroll_area)
        
        # Add button layout at the bottom
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Add save/load buttons
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self._save_configuration)
        button_layout.addWidget(self.save_button)
        
        self.load_button = QPushButton("Load Configuration")
        self.load_button.clicked.connect(self._load_configuration)
        button_layout.addWidget(self.load_button)
        
        # Add button layout to main layout
        self.main_layout.addLayout(button_layout)
    
    def set_controller(self, controller):
        """
        Set the optimization controller to use for constraint management.
        
        Args:
            controller: OptimizationController instance
        """
        self.controller = controller
        
        # Connect to constraints_updated signal if available
        if hasattr(controller, 'constraints_updated'):
            controller.constraints_updated.connect(self._update_constraints)
    
    def _update_constraints(self, constraints):
        """
        Update the constraint list with the given constraints.
        
        Args:
            constraints: List of constraint information dictionaries
        """
        # Clear existing constraints
        self._clear_constraints()
        
        # Store constraints
        self.constraints = constraints
        
        # Add constraint widgets
        for constraint_info in constraints:
            self._add_constraint_widget(constraint_info)
    
    def _clear_constraints(self):
        """Clear all constraint widgets."""
        # Remove all widgets from the layout
        while self.constraints_layout.count():
            item = self.constraints_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _add_constraint_widget(self, constraint_info):
        """
        Add a widget for a constraint.
        
        Args:
            constraint_info: Dictionary containing constraint information
        """
        # Create group box for constraint
        group = QGroupBox(constraint_info['name'])
        group_layout = QVBoxLayout(group)
        
        # Add description
        description = QLabel(constraint_info['description'])
        description.setWordWrap(True)
        group_layout.addWidget(description)
        
        # Add enabled checkbox
        enabled_layout = QHBoxLayout()
        enabled_checkbox = QCheckBox("Enabled")
        enabled_checkbox.setChecked(constraint_info.get('enabled', False))
        enabled_checkbox.stateChanged.connect(
            lambda state, name=constraint_info['name']: 
            self._toggle_constraint(name, state == Qt.CheckState.Checked.value)
        )
        enabled_layout.addWidget(enabled_checkbox)
        
        # Add configure button
        configure_button = QPushButton("Configure")
        configure_button.clicked.connect(
            lambda _, info=constraint_info: self._configure_constraint(info)
        )
        enabled_layout.addWidget(configure_button)
        enabled_layout.addStretch()
        
        group_layout.addLayout(enabled_layout)
        
        # Add to constraints layout
        self.constraints_layout.addWidget(group)
    
    def _toggle_constraint(self, constraint_name, enabled):
        """
        Toggle a constraint on or off.
        
        Args:
            constraint_name: Name of the constraint
            enabled: Whether the constraint should be enabled
        """
        if self.controller:
            self.controller.set_constraint_enabled(constraint_name, enabled)
            self.constraint_changed.emit()
    
    def _configure_constraint(self, constraint_info):
        """
        Open a dialog to configure a constraint's parameters.
        
        Args:
            constraint_info: Dictionary containing constraint information
        """
        dialog = ConstraintConfigDialog(constraint_info, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_configuration()
            
            if self.controller:
                self.controller.set_constraint_configuration(constraint_info['name'], config)
                self.constraint_changed.emit()
                
                # Update local constraint info to reflect changes
                for i, constraint in enumerate(self.constraints):
                    if constraint['name'] == constraint_info['name']:
                        self.constraints[i]['config'] = config
                        break
    
    def _save_configuration(self):
        """
        Save the current constraint configuration to a file.
        """
        if not self.controller:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Constraint Configuration",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Add .json extension if not present
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
                
            success = self.controller.save_constraint_configuration(file_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    f"Constraint configuration saved to {file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    "Failed to save constraint configuration."
                )
    
    def _load_configuration(self):
        """
        Load constraint configuration from a file.
        """
        if not self.controller:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Constraint Configuration",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            success = self.controller.load_constraint_configuration(file_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "Configuration Loaded",
                    f"Constraint configuration loaded from {file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Load Failed",
                    "Failed to load constraint configuration."
                ) 