"""
Parameter Registry Module.

Provides a singleton registry for accessing parameter models.
"""
import logging
from typing import Dict
from .parameter_model import ParameterModel

logger = logging.getLogger(__name__)

class ParameterRegistry:
    """
    Singleton registry for parameter models.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of the registry.
        
        Returns:
            ParameterRegistry: The registry instance
        """
        if cls._instance is None:
            cls._instance = ParameterRegistry()
        return cls._instance
    
    def __init__(self):
        """Initialize the parameter registry with empty model dictionary."""
        self._parameter_models: Dict[str, ParameterModel] = {}
        logger.debug("Initialized parameter registry")
    
    def get_model(self, model_name: str) -> ParameterModel:
        """
        Get a parameter model by name, creating it if it doesn't exist.
        
        Args:
            model_name: Name of the parameter model
            
        Returns:
            ParameterModel: The parameter model
        """
        if model_name not in self._parameter_models:
            logger.debug(f"Creating new parameter model: {model_name}")
            self._parameter_models[model_name] = ParameterModel(name=model_name)
        return self._parameter_models[model_name]
    
    def reset(self) -> None:
        """Reset all parameter models by creating new instances."""
        logger.debug("Resetting all parameter models")
        
        # Instead of trying to clear parameters, just create new model instances
        # This avoids Qt signal issues with deleted C++ objects
        model_names = list(self._parameter_models.keys())
        self._parameter_models = {}
        
        # Recreate models with same names
        for name in model_names:
            self.get_model(name)
            
    def get_all_model_names(self) -> list:
        """
        Get all registered model names.
        
        Returns:
            list: List of model names
        """
        return list(self._parameter_models.keys()) 