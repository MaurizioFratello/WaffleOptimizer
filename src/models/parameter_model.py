"""
Parameter Model Module.

Provides a centralized parameter storage with signal-slot mechanism for updates.
"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any, Optional, Set, Callable
import logging

logger = logging.getLogger(__name__)

class ParameterModel(QObject):
    """
    Model for storing and managing parameters with change notification.
    """
    parameter_changed = pyqtSignal(str, object)  # name, value
    parameters_changed = pyqtSignal(dict)  # multiple parameters
    
    def __init__(self, name: str = ""):
        """
        Initialize a parameter model.
        
        Args:
            name: Optional name for this parameter model (for logging)
        """
        super().__init__()
        self._name = name
        self._parameters = {}
        self._validators = {}
        self._locked_parameters = set()
        logger.debug(f"Initialized parameter model: {name}")
        
    def set_parameter(self, name: str, value: Any, emit_signal: bool = True) -> bool:
        """
        Set a parameter value with optional validation.
        
        Args:
            name: Parameter name
            value: Parameter value
            emit_signal: Whether to emit change signal
            
        Returns:
            bool: True if the parameter was changed, False otherwise
        """
        # Check if parameter is locked
        if name in self._locked_parameters:
            logger.debug(f"Parameter '{name}' is locked, ignoring set attempt")
            return False
            
        # Validate if validator exists
        if name in self._validators and not self._validators[name](value):
            logger.debug(f"Parameter '{name}' validation failed for value: {value}")
            return False
            
        old_value = self._parameters.get(name)
        if old_value != value:
            self._parameters[name] = value
            logger.debug(f"Parameter '{name}' changed from {old_value} to {value}")
            if emit_signal:
                self.parameter_changed.emit(name, value)
            return True
        return False
        
    def set_parameters(self, param_dict: Dict[str, Any], emit_signal: bool = True) -> bool:
        """
        Set multiple parameters at once.
        
        Args:
            param_dict: Dictionary of parameter names to values
            emit_signal: Whether to emit change signals
            
        Returns:
            bool: True if any parameters were changed
        """
        changed = False
        for name, value in param_dict.items():
            if self.set_parameter(name, value, emit_signal=False):
                changed = True
        
        if changed and emit_signal:
            self.parameters_changed.emit(param_dict)
        return changed
        
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        Get a parameter value.
        
        Args:
            name: Parameter name
            default: Default value if parameter doesn't exist
            
        Returns:
            Parameter value or default
        """
        return self._parameters.get(name, default)
        
    def register_validator(self, name: str, validator_func: Callable[[Any], bool]) -> None:
        """
        Register a validation function for a parameter.
        
        Args:
            name: Parameter name
            validator_func: Function that takes a value and returns True if valid
        """
        logger.debug(f"Registering validator for parameter '{name}'")
        self._validators[name] = validator_func
        
    def lock_parameter(self, name: str) -> None:
        """
        Lock a parameter to prevent changes.
        
        Args:
            name: Parameter name
        """
        logger.debug(f"Locking parameter '{name}'")
        self._locked_parameters.add(name)
        
    def unlock_parameter(self, name: str) -> None:
        """
        Unlock a parameter.
        
        Args:
            name: Parameter name
        """
        if name in self._locked_parameters:
            logger.debug(f"Unlocking parameter '{name}'")
            self._locked_parameters.remove(name)
            
    def clear_parameters(self) -> None:
        """Clear all parameter values."""
        old_params = self._parameters.copy()
        self._parameters = {}
        logger.debug(f"Cleared all parameters in model {self._name}")
        self.parameters_changed.emit(old_params)
        
    def has_parameter(self, name: str) -> bool:
        """
        Check if a parameter exists.
        
        Args:
            name: Parameter name
            
        Returns:
            bool: True if parameter exists
        """
        return name in self._parameters
        
    def get_all_parameters(self) -> Dict[str, Any]:
        """
        Get all parameters.
        
        Returns:
            dict: Dictionary of all parameters
        """
        return self._parameters.copy() 