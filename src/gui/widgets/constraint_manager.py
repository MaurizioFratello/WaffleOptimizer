"""
Constraint Manager Widget for configuring optimization constraints.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QCheckBox, QGroupBox, QScrollArea,
                          QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox,
                          QDialog, QDialogButtonBox, QFileDialog, QMessageBox,
                          QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

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


class ConstraintTab(QWidget):
    """A tab containing related constraints."""
    
    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setObjectName("constraintTab")
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        
        # Add header
        header = QLabel(title)
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        self.layout.addWidget(header)
        
        # Add description
        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666;")
            self.layout.addWidget(desc)
        
        # Create scroll area for constraints
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create widget to hold constraints
        self.constraints_widget = QWidget()
        self.constraints_layout = QVBoxLayout(self.constraints_widget)
        self.constraints_layout.setContentsMargins(0, 0, 0, 0)
        self.constraints_layout.setSpacing(10)
        
        # Add constraints widget to scroll area
        self.scroll.setWidget(self.constraints_widget)
        self.layout.addWidget(self.scroll)
        
        # Add stretch at the bottom
        self.layout.addStretch()
    
    def add_constraint(self, constraint_info):
        """Add a constraint to this tab."""
        # Skip production-related constraints
        if constraint_info['name'] in ['production_rate', 'minimum_batch']:
            return
            
        # Create group box for constraint
        group = QGroupBox()
        group.setObjectName("constraintGroup")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(15, 15, 15, 15)
        
        # Format constraint name for display (convert from technical name to display name)
        display_name = constraint_info['name']
        if display_name == 'demand':
            display_name = "Demand Constraint"
        elif display_name == 'supply':
            display_name = "Supply Constraint"
        elif display_name == 'allowed_combinations':
            display_name = "Allowed Combinations Constraint"
        
        # Add title
        title = QLabel(display_name)
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        group_layout.addWidget(title)
        
        # Add description
        description = QLabel(constraint_info['description'])
        description.setWordWrap(True)
        description.setStyleSheet("color: #666; margin-bottom: 10px;")
        group_layout.addWidget(description)
        
        # Add controls layout
        controls = QHBoxLayout()
        
        # Add enabled checkbox
        enabled_checkbox = QCheckBox("Enable Constraint")
        enabled_checkbox.setChecked(constraint_info.get('enabled', False))
        enabled_checkbox.stateChanged.connect(
            lambda state, name=constraint_info['name']: 
            self.parent().parent().parent()._toggle_constraint(
                name, state == Qt.CheckState.Checked.value
            )
        )
        controls.addWidget(enabled_checkbox)
        
        # Add configure button
        configure_button = QPushButton("Configure")
        configure_button.setObjectName("configureButton")
        configure_button.clicked.connect(
            lambda _, info=constraint_info: 
            self.parent().parent().parent()._configure_constraint(info)
        )
        controls.addWidget(configure_button)
        
        # Add validation status
        validation = QLabel("✓ Valid")  # Can be updated based on validation state
        validation.setStyleSheet("color: #2ecc71;")
        controls.addWidget(validation)
        
        controls.addStretch()
        group_layout.addLayout(controls)
        
        # Add to constraints layout
        self.constraints_layout.addWidget(group)


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
        self.main_layout.setSpacing(0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("constraintTabs")
        
        # Create tabs for different constraint categories (excluding Production)
        self.demand_tab = ConstraintTab(
            "Demand Constraints",
            "Configure constraints for fulfilling waffle demand requirements."
        )
        self.supply_tab = ConstraintTab(
            "Supply Constraints",
            "Configure constraints for pan supply availability and usage."
        )
        self.combinations_tab = ConstraintTab(
            "Combinations",
            "Configure allowed combinations of waffle types and pan types."
        )
        
        # Add tabs
        self.tabs.addTab(self.demand_tab, "Demand")
        self.tabs.addTab(self.supply_tab, "Supply")
        self.tabs.addTab(self.combinations_tab, "Combinations")
        
        # Add tabs to layout
        self.main_layout.addWidget(self.tabs)
        
        # Add button layout at the bottom
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add save/load buttons
        self.save_button = QPushButton("Save Configuration")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self._save_configuration)
        button_layout.addWidget(self.save_button)
        
        self.load_button = QPushButton("Load Configuration")
        self.load_button.setObjectName("loadButton")
        self.load_button.clicked.connect(self._load_configuration)
        button_layout.addWidget(self.load_button)
        
        # Add button layout to main layout
        self.main_layout.addLayout(button_layout)
        
        # Apply styles
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
            }
            
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background: #f5f5f5;
            }
            
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            
            #constraintGroup {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
            }
            
            #configureButton {
                padding: 4px 12px;
                border: 1px solid #3498db;
                border-radius: 3px;
                color: #3498db;
                background: white;
            }
            
            #configureButton:hover {
                background: #3498db;
                color: white;
            }
            
            #saveButton, #loadButton {
                padding: 6px 16px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: white;
            }
            
            #saveButton:hover, #loadButton:hover {
                background: #f5f5f5;
            }
        """)
    
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
        # Store constraints
        self.constraints = constraints
        
        # Clear existing constraints
        self._clear_constraints()
        
        # First disable any production-related constraints
        if self.controller:
            for constraint_info in constraints:
                if constraint_info['name'] in ['production_rate', 'minimum_batch']:
                    # Disable production constraints
                    self.controller.toggle_constraint(constraint_info['name'], False)
        
        # Add constraint widgets to appropriate tabs (excluding production constraints)
        for constraint_info in constraints:
            if constraint_info['name'] not in ['production_rate', 'minimum_batch']:
                self._add_constraint_widget(constraint_info)
    
    def _clear_constraints(self):
        """Clear all constraint widgets from all tabs."""
        for tab in [self.demand_tab, self.supply_tab, self.combinations_tab]:
            layout = tab.constraints_layout
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
    
    def _add_constraint_widget(self, constraint_info):
        """
        Add a widget for a constraint.
        
        Args:
            constraint_info: Dictionary containing constraint information
        """
        # Determine which tab to add to based on constraint type
        constraint_name = constraint_info['name']
        
        # Map constraint names to their respective tabs
        if constraint_name == 'demand':
            tab = self.demand_tab
        elif constraint_name == 'supply':
            tab = self.supply_tab
        elif constraint_name == 'allowed_combinations':
            tab = self.combinations_tab
        else:
            # Log unknown constraint type and default to demand tab
            logger.warning(f"Unknown constraint type: {constraint_name}. Defaulting to Demand tab.")
            tab = self.demand_tab
        
        # Add constraint to tab
        tab.add_constraint(constraint_info)
    
    def _toggle_constraint(self, name, enabled):
        """
        Toggle a constraint on or off.
        
        Args:
            name: Name of the constraint
            enabled: Whether the constraint should be enabled
        """
        if self.controller:
            try:
                self.controller.toggle_constraint(name, enabled)
                # Automatically save configuration after toggling enabled state
                try:
                    self.controller.save_current_constraint_configuration()
                    logger.debug(f"Auto-saved configuration after toggling '{name}' constraint.")
                except Exception as e:
                    logger.error(f"Failed to auto-save configuration after toggling '{name}': {e}")
                self.constraint_changed.emit()
            except Exception as e:
                logger.error(f"Error toggling constraint '{name}': {e}")
    
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
                try:
                    self.controller.configure_constraint(constraint_info['name'], config)
                    # Automatically save configuration after applying changes
                    try:
                        self.controller.save_current_constraint_configuration()
                        logger.debug(f"Auto-saved configuration after configuring '{constraint_info['name']}' constraint.")
                    except Exception as e:
                        logger.error(f"Failed to auto-save configuration after configuring '{constraint_info['name']}': {e}")
                    self.constraint_changed.emit()
                    
                    # Update local constraint info to reflect changes
                    for i, constraint in enumerate(self.constraints):
                        if constraint['name'] == constraint_info['name']:
                            self.constraints[i]['config'] = config
                            break
                except Exception as e:
                    logger.error(f"Error configuring constraint '{constraint_info['name']}': {e}")
    
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
            try:
                self.controller.save_constraint_configuration(file_path)
                QMessageBox.information(
                    self,
                    "Success",
                    "Configuration saved successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save configuration: {str(e)}"
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
            try:
                self.controller.load_constraint_configuration(file_path)
                QMessageBox.information(
                    self,
                    "Success",
                    "Configuration loaded successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load configuration: {str(e)}"
                ) 