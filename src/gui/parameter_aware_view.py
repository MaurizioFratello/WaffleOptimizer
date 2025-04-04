"""
Parameter Aware View Module.

Provides a base view class with parameter binding capabilities.
"""
import logging
from PyQt6.QtWidgets import (QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, 
                           QLineEdit, QSlider, QRadioButton)
from PyQt6.QtCore import Qt
from .base_view import BaseView
from src.models.parameter_registry import ParameterRegistry

logger = logging.getLogger(__name__)

class ParameterAwareView(BaseView):
    """
    Enhanced base view with parameter binding capabilities.
    """
    
    def __init__(self, title, description, main_window=None, action_button_text="Apply", model_name="default"):
        """
        Initialize parameter aware view.
        
        Args:
            title: View title
            description: View description
            main_window: Reference to the main window
            action_button_text: Text for the action button
            model_name: Name of the parameter model to use
        """
        super().__init__(title, description, main_window, action_button_text)
        
        # Get parameter model
        self.param_registry = ParameterRegistry.get_instance()
        self.param_model = self.param_registry.get_model(model_name)
        self.model_name = model_name
        
        logger.debug(f"Initialized parameter aware view with model: {model_name}")
    
    def _bind_combo_box(self, combo_box: QComboBox, param_name: str, use_data=True):
        """
        Bind combo box to parameter model.
        
        Args:
            combo_box: The combo box to bind
            param_name: The parameter name
            use_data: Whether to use the data role (True) or text (False)
        """
        # Disconnect any existing connections to avoid duplicates
        try:
            combo_box.currentIndexChanged.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value if one exists in the parameter model
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            if use_data:
                index = combo_box.findData(value)
            else:
                index = combo_box.findText(value)
                
            if index >= 0:
                combo_box.setCurrentIndex(index)
        
        # Connect to changes
        if use_data:
            combo_box.currentIndexChanged.connect(
                lambda: self.param_model.set_parameter(param_name, combo_box.currentData())
            )
        else:
            combo_box.currentIndexChanged.connect(
                lambda: self.param_model.set_parameter(param_name, combo_box.currentText())
            )
        
        logger.debug(f"Bound combo box to parameter: {param_name}")
    
    def _bind_spin_box(self, spin_box: QSpinBox, param_name: str):
        """
        Bind spin box to parameter model.
        
        Args:
            spin_box: The spin box to bind
            param_name: The parameter name
        """
        # Disconnect any existing connections
        try:
            spin_box.valueChanged.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            spin_box.setValue(value)
        
        # Connect to changes
        spin_box.valueChanged.connect(
            lambda value: self.param_model.set_parameter(param_name, value)
        )
        
        logger.debug(f"Bound spin box to parameter: {param_name}")
    
    def _bind_double_spin_box(self, spin_box: QDoubleSpinBox, param_name: str):
        """
        Bind double spin box to parameter model.
        
        Args:
            spin_box: The double spin box to bind
            param_name: The parameter name
        """
        # Disconnect any existing connections
        try:
            spin_box.valueChanged.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            spin_box.setValue(value)
        
        # Connect to changes
        spin_box.valueChanged.connect(
            lambda value: self.param_model.set_parameter(param_name, value)
        )
        
        logger.debug(f"Bound double spin box to parameter: {param_name}")
    
    def _bind_check_box(self, check_box: QCheckBox, param_name: str):
        """
        Bind check box to parameter model.
        
        Args:
            check_box: The check box to bind
            param_name: The parameter name
        """
        # Disconnect any existing connections
        try:
            check_box.stateChanged.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            check_box.setChecked(value)
        
        # Connect to changes
        check_box.stateChanged.connect(
            lambda state: self.param_model.set_parameter(param_name, state == Qt.CheckState.Checked)
        )
        
        logger.debug(f"Bound check box to parameter: {param_name}")
        
    def _bind_line_edit(self, line_edit: QLineEdit, param_name: str):
        """
        Bind line edit to parameter model.
        
        Args:
            line_edit: The line edit to bind
            param_name: The parameter name
        """
        # Disconnect any existing connections
        try:
            line_edit.textChanged.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            line_edit.setText(value)
        
        # Connect to changes
        line_edit.textChanged.connect(
            lambda text: self.param_model.set_parameter(param_name, text)
        )
        
        logger.debug(f"Bound line edit to parameter: {param_name}")
    
    def _bind_slider(self, slider: QSlider, param_name: str):
        """
        Bind slider to parameter model.
        
        Args:
            slider: The slider to bind
            param_name: The parameter name
        """
        # Disconnect any existing connections
        try:
            slider.valueChanged.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            slider.setValue(value)
        
        # Connect to changes
        slider.valueChanged.connect(
            lambda value: self.param_model.set_parameter(param_name, value)
        )
        
        logger.debug(f"Bound slider to parameter: {param_name}")
    
    def _bind_radio_button(self, radio_button: QRadioButton, param_name: str, value):
        """
        Bind radio button to parameter model.
        
        Args:
            radio_button: The radio button to bind
            param_name: The parameter name
            value: The value to set when the radio button is checked
        """
        # Disconnect any existing connections
        try:
            radio_button.toggled.disconnect()
        except Exception:
            pass  # No connections to disconnect
        
        # Load initial value
        param_value = self.param_model.get_parameter(param_name)
        if param_value is not None:
            radio_button.setChecked(param_value == value)
        
        # Connect to changes
        radio_button.toggled.connect(
            lambda checked: self.param_model.set_parameter(param_name, value) if checked else None
        )
        
        logger.debug(f"Bound radio button to parameter: {param_name}")
    
    def _bind_file_selector(self, file_selector, param_name: str):
        """
        Bind file selector to parameter model.
        
        Args:
            file_selector: The file selector widget to bind
            param_name: The parameter name
        """
        # Commented out disconnection to preserve existing connections
        # try:
        #     file_selector.file_selected.disconnect()
        # except Exception:
        #     pass  # No connections to disconnect
        
        # Load initial value
        value = self.param_model.get_parameter(param_name)
        if value is not None:
            file_selector.set_file_path(value)
        
        # Connect to changes
        file_selector.file_selected.connect(
            lambda path: self.param_model.set_parameter(param_name, path)
        )
        
        logger.debug(f"Bound file selector to parameter: {param_name}")
    
    def _on_parameter_changed(self, name, value):
        """
        Handle parameter model changes.
        
        Args:
            name: Parameter name
            value: New parameter value
        """
        # Override in subclasses to react to parameter changes
        pass
    
    def load_from_settings(self, settings, prefix):
        """
        Load parameters from QSettings.
        
        Args:
            settings: QSettings object
            prefix: Settings prefix
        """
        # Override in subclasses
        pass
        
    def save_to_settings(self, settings, prefix):
        """
        Save parameters to QSettings.
        
        Args:
            settings: QSettings object
            prefix: Settings prefix
        """
        # Override in subclasses
        pass 