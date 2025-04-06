"""
Constraint Manager Widget for configuring optimization constraints.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QCheckBox, QGroupBox, QScrollArea,
                          QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox,
                          QDialog, QDialogButtonBox, QFileDialog, QMessageBox,
                          QTabWidget, QGridLayout, QFrame)
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
                
                # Store a reference to the widget for later use
                widget.setObjectName(f"config_{constraint_info['name']}_{prop_name}")
                
                # Connect widget signals to auto-save function
                if isinstance(widget, QCheckBox):
                    widget.stateChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                elif isinstance(widget, QSpinBox):
                    widget.valueChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                elif isinstance(widget, QDoubleSpinBox):
                    widget.valueChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                elif isinstance(widget, QComboBox):
                    widget.currentIndexChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                
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
    """A tab containing constraints with direct configuration controls."""
    
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
        
        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create container widget with vertical layout
        self.constraints_widget = QWidget()
        self.constraints_layout = QVBoxLayout(self.constraints_widget)
        self.constraints_layout.setContentsMargins(10, 10, 10, 10)
        self.constraints_layout.setSpacing(20)
        
        # Add constraints widget to scroll area
        self.scroll.setWidget(self.constraints_widget)
        self.layout.addWidget(self.scroll)
    
    def add_constraint(self, constraint_info):
        """Add a constraint with direct configuration controls."""
        # Skip production-related constraints
        if constraint_info['name'] in ['production_rate', 'minimum_batch']:
            return
        
        # Create constraint container
        constraint_container = QWidget()
        container_layout = QVBoxLayout(constraint_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        
        # Add Active checkbox
        enabled_checkbox = QCheckBox("Active")
        enabled_checkbox.setChecked(constraint_info.get('enabled', False))
        enabled_checkbox.stateChanged.connect(
            lambda state, name=constraint_info['name']: 
            self.parent().parent().parent()._toggle_constraint(
                name, state == Qt.CheckState.Checked.value
            )
        )
        container_layout.addWidget(enabled_checkbox)
        
        # Add Constraint parameters section
        params_label = QLabel("Constraint parameters:")
        params_label.setProperty("class", "section-header")
        container_layout.addWidget(params_label)
        
        # Add configuration parameters
        params_container = QWidget()
        params_layout = QVBoxLayout(params_container)
        params_layout.setContentsMargins(20, 0, 0, 0)  # Add left indent
        params_layout.setSpacing(10)
        
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
                    widget = QCheckBox(prop_title)
                    widget.setChecked(bool(current_value))
                
                elif prop_type == 'integer':
                    widget = QSpinBox()
                    minimum = prop_schema.get('minimum', -999999)
                    maximum = prop_schema.get('maximum', 999999)
                    widget.setRange(int(minimum), int(maximum))
                    if current_value is not None:
                        widget.setValue(int(current_value))
                
                elif prop_type == 'number':
                    widget = QDoubleSpinBox()
                    minimum = prop_schema.get('minimum', -999999.0)
                    maximum = prop_schema.get('maximum', 999999.0)
                    widget.setRange(float(minimum), float(maximum))
                    widget.setDecimals(4)
                    widget.setSingleStep(0.01)
                    if current_value is not None:
                        widget.setValue(float(current_value))
                
                elif prop_type == 'string' and 'enum' in prop_schema:
                    widget = QComboBox()
                    for option in prop_schema['enum']:
                        widget.addItem(str(option))
                    if current_value is not None:
                        index = widget.findText(str(current_value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                
                else:  # Default to string or unsupported types
                    continue  # Skip unsupported types for now
                
                # Add tooltip if description available
                if prop_description:
                    widget.setToolTip(prop_description)
                
                # Store a reference to the widget for later use
                widget.setObjectName(f"config_{constraint_info['name']}_{prop_name}")
                
                # Connect widget signals to auto-save function
                if isinstance(widget, QCheckBox):
                    widget.stateChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                elif isinstance(widget, QSpinBox):
                    widget.valueChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                elif isinstance(widget, QDoubleSpinBox):
                    widget.valueChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                elif isinstance(widget, QComboBox):
                    widget.currentIndexChanged.connect(
                        lambda _, info=constraint_info: self._save_constraint_configuration(info)
                    )
                
                # Add widget to params layout
                params_layout.addWidget(widget)
        
        container_layout.addWidget(params_container)
        
        # Add description
        description = QLabel("Description:")
        description.setProperty("class", "section-header")
        container_layout.addWidget(description)
        
        desc_text = QLabel(constraint_info['description'])
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("color: #666; margin-left: 20px;")  # Add left indent
        container_layout.addWidget(desc_text)
        
        # Add horizontal separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setProperty("class", "separator")
        separator.setStyleSheet("margin-top: 20px; margin-bottom: 20px;")
        container_layout.addWidget(separator)
        
        # Add constraint to layout
        self.constraints_layout.addWidget(constraint_container)
    
    def _save_constraint_configuration(self, constraint_info):
        """Save the configuration for a constraint."""
        # Get all configuration values from widgets
        config = {}
        
        # Get schema properties
        schema = constraint_info.get('schema', {})
        if 'properties' in schema:
            for prop_name in schema['properties'].keys():
                # Find the widget
                widget_name = f"config_{constraint_info['name']}_{prop_name}"
                widget = self.findChild(QWidget, widget_name)
                
                if widget:
                    # Get value based on widget type
                    if isinstance(widget, QCheckBox):
                        config[prop_name] = widget.isChecked()
                    elif isinstance(widget, QSpinBox):
                        config[prop_name] = widget.value()
                    elif isinstance(widget, QDoubleSpinBox):
                        config[prop_name] = widget.value()
                    elif isinstance(widget, QComboBox):
                        config[prop_name] = widget.currentText()
        
        # Apply configuration
        if config:
            self.parent().parent().parent()._configure_constraint_directly(
                constraint_info['name'], config
            )


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
        self.optimization_results = None  # Store optimization results
        
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
            
            QCheckBox {
                spacing: 8px;
                min-height: 20px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            QLabel {
                margin-top: 5px;
            }
            
            QLabel[class="section-header"] {
                font-weight: bold;
                margin-top: 15px;
            }
            
            QFrame[class="separator"] {
                color: #ddd;
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
    
    def set_optimization_results(self, results):
        """Store optimization results and update constraint cards."""
        logger.info("Received optimization results - updating constraint metrics")
        self.optimization_results = results
        self._update_constraint_metrics()
    
    def _update_constraint_metrics(self):
        """Update metrics in all constraint cards."""
        # Iterate through all tabs and update cards
        for tab in [self.demand_tab, self.supply_tab, self.combinations_tab]:
            for i in range(tab.constraints_layout.count()):
                item = tab.constraints_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'update_metrics'):
                        widget.update_metrics(self.optimization_results)
    
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
            
        # Connect to optimization_completed signal if available
        if hasattr(controller, 'optimization_completed'):
            controller.optimization_completed.connect(self.set_optimization_results)
    
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
        logger.info(f"Toggling constraint '{name}' to {enabled}")
        
        if not self.controller:
            logger.warning(f"Cannot toggle constraint '{name}': No controller available")
            return
            
        try:
            # Update the enabled state in the controller
            self.controller.toggle_constraint(name, enabled)
            
            # Update the local state to reflect change
            for i, constraint in enumerate(self.constraints):
                if constraint['name'] == name:
                    self.constraints[i]['enabled'] = enabled
                    logger.debug(f"Updated local constraint state for '{name}': enabled={enabled}")
                    break
            
            # Notify about constraint change
            self.constraint_changed.emit()
            
            # Log the state change
            logger.info(f"Constraint '{name}' enabled state set to {enabled}")
        except Exception as e:
            logger.error(f"Error toggling constraint '{name}': {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to toggle constraint '{name}': {str(e)}"
            )
    
    def _configure_constraint(self, constraint_info):
        """
        Open a dialog to configure a constraint's parameters.
        
        Args:
            constraint_info: Dictionary containing constraint information
        """
        logger.info(f"Opening configuration dialog for constraint '{constraint_info['name']}'")
        
        dialog = ConstraintConfigDialog(constraint_info, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_configuration()
            logger.debug(f"New configuration for '{constraint_info['name']}': {config}")
            
            if not self.controller:
                logger.warning(f"Cannot configure constraint '{constraint_info['name']}': No controller available")
                return
                
            try:
                # Apply the configuration to the controller
                self.controller.configure_constraint(constraint_info['name'], config)
                
                # Update local constraint info to reflect changes
                for i, constraint in enumerate(self.constraints):
                    if constraint['name'] == constraint_info['name']:
                        self.constraints[i]['config'] = config
                        logger.debug(f"Updated local configuration for '{constraint_info['name']}'")
                        break
                
                # Notify about constraint change
                self.constraint_changed.emit()
                
                # Log the change
                logger.info(f"Configuration for constraint '{constraint_info['name']}' updated successfully")
            except Exception as e:
                logger.error(f"Error configuring constraint '{constraint_info['name']}': {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to configure constraint '{constraint_info['name']}': {str(e)}"
                )
    
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

    def _configure_constraint_directly(self, constraint_name, config):
        """
        Configure a constraint without a dialog.
        
        Args:
            constraint_name: Name of the constraint
            config: Dictionary containing configuration values
        """
        logger.info(f"Directly configuring constraint '{constraint_name}'")
        
        if not self.controller:
            logger.warning(f"Cannot configure constraint '{constraint_name}': No controller available")
            return
            
        try:
            # Apply the configuration to the controller
            self.controller.configure_constraint(constraint_name, config)
            
            # Update local constraint info to reflect changes
            for i, constraint in enumerate(self.constraints):
                if constraint['name'] == constraint_name:
                    self.constraints[i]['config'] = config
                    logger.debug(f"Updated local configuration for '{constraint_name}'")
                    break
            
            # Notify about constraint change
            self.constraint_changed.emit()
            
            # Success notification removed for automatic saving
            
            # Log the change
            logger.info(f"Configuration for constraint '{constraint_name}' updated successfully")
        except Exception as e:
            logger.error(f"Error configuring constraint '{constraint_name}': {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to configure constraint '{constraint_name}': {str(e)}"
            )

def test_grid_layout():
    """Simple test function for the grid layout."""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create constraint manager
    manager = ConstraintManager()
    
    # Create sample constraints
    sample_constraints = [
        {
            'name': 'demand',
            'description': 'Ensures that waffle production meets minimum demand requirements.',
            'enabled': True,
            'config': {
                'target_value': 1000,
                'time_window': 'week'
            }
        },
        {
            'name': 'supply',
            'description': 'Ensures that waffle production does not exceed available supply.',
            'enabled': True,
            'config': {
                'max_usage': 500,
                'consider_inventory': True
            }
        },
        {
            'name': 'allowed_combinations',
            'description': 'Restricts which waffle types can be produced on which pans.',
            'enabled': False,
            'config': {
                'enforce_strict': True
            }
        }
    ]
    
    # Update constraints
    manager._update_constraints(sample_constraints)
    
    # Show manager
    manager.show()
    
    return app.exec()

def test_constraint_metrics():
    """Test constraint cards with simulated optimization results."""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create constraint manager
    manager = ConstraintManager()
    
    # Create sample constraints
    sample_constraints = [
        {
            'name': 'demand',
            'description': 'Ensures that waffle production meets minimum demand requirements.',
            'enabled': True,
            'config': {
                'target_value': 1000,
                'time_window': 'week'
            }
        },
        {
            'name': 'supply',
            'description': 'Ensures that waffle production does not exceed available supply.',
            'enabled': True,
            'config': {
                'max_usage': 500,
                'consider_inventory': True
            }
        },
        {
            'name': 'allowed_combinations',
            'description': 'Restricts which waffle types can be produced on which pans.',
            'enabled': False,
            'config': {
                'enforce_strict': True
            }
        }
    ]
    
    # Update constraints
    manager._update_constraints(sample_constraints)
    
    # Simulate optimization results
    simulated_results = {
        'status': 'OPTIMAL',
        'objective_value': 12500.75,
        'constraints': {
            'demand': {
                'satisfaction': 0.85,
                'units_produced': 850,
                'units_required': 1000
            },
            'supply': {
                'utilization': 0.92,
                'units_used': 460,
                'units_available': 500
            },
            'allowed_combinations': {
                'active_count': 8,
                'total_pairs': 24
            }
        }
    }
    
    # Update metrics with simulated results
    manager.set_optimization_results(simulated_results)
    
    # Show manager
    manager.show()
    
    return app.exec()

def test_simplified_constraints():
    """Test simplified constraint interface."""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create constraint manager
    manager = ConstraintManager()
    
    # Create sample constraints
    sample_constraints = [
        {
            'name': 'demand',
            'description': 'Ensures that waffle production meets minimum demand requirements.',
            'enabled': True,
            'schema': {
                'properties': {
                    'target_value': {
                        'type': 'integer',
                        'title': 'Target Value',
                        'description': 'Minimum demand to be satisfied',
                        'minimum': 0,
                        'maximum': 10000
                    },
                    'time_window': {
                        'type': 'string',
                        'title': 'Time Window',
                        'enum': ['day', 'week', 'month']
                    },
                    'strict': {
                        'type': 'boolean',
                        'title': 'Strict Enforcement',
                        'description': 'Whether to strictly enforce the demand constraint'
                    }
                }
            },
            'config': {
                'target_value': 1000,
                'time_window': 'week',
                'strict': True
            }
        },
        {
            'name': 'supply',
            'description': 'Ensures that waffle production does not exceed available supply.',
            'enabled': True,
            'schema': {
                'properties': {
                    'max_usage': {
                        'type': 'integer',
                        'title': 'Maximum Usage',
                        'description': 'Maximum supply that can be used',
                        'minimum': 0,
                        'maximum': 10000
                    },
                    'consider_inventory': {
                        'type': 'boolean',
                        'title': 'Consider Inventory',
                        'description': 'Whether to consider existing inventory'
                    }
                }
            },
            'config': {
                'max_usage': 500,
                'consider_inventory': True
            }
        },
        {
            'name': 'allowed_combinations',
            'description': 'Restricts which waffle types can be produced on which pans.',
            'enabled': False,
            'schema': {
                'properties': {
                    'enforce_strict': {
                        'type': 'boolean',
                        'title': 'Strict Enforcement',
                        'description': 'Whether to strictly enforce allowed combinations'
                    },
                    'priority_level': {
                        'type': 'integer',
                        'title': 'Priority Level',
                        'description': 'Priority level for combinations constraint',
                        'minimum': 1,
                        'maximum': 10
                    }
                }
            },
            'config': {
                'enforce_strict': True,
                'priority_level': 5
            }
        }
    ]
    
    # Update constraints
    manager._update_constraints(sample_constraints)
    
    # Show manager
    manager.show()
    
    return app.exec()

if __name__ == '__main__':
    # Choose which test to run
    import sys
    run_metrics_test = False
    run_simplified_test = True
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'metrics':
                run_metrics_test = True
                run_simplified_test = False
            elif sys.argv[1] == 'simplified':
                run_simplified_test = True
                run_metrics_test = False
    except Exception:
        pass
        
    if run_metrics_test:
        test_constraint_metrics()
    elif run_simplified_test:
        test_simplified_constraints()
    else:
        test_grid_layout() 