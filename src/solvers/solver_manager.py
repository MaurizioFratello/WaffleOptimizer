"""
Solver Manager Module for Waffle Production Optimization.

This module provides a centralized interface for managing solvers and constraints.
"""
from typing import Dict, Any, List, Optional, Type, Union
import logging

from src.solvers.base import SolverInterface, SolverFactory
from src.solvers.constraints import (
    Constraint,
    DemandConstraint,
    SupplyConstraint,
    AllowedCombinationsConstraint,
    ProductionRateConstraint,
    MinimumBatchConstraint,
)

# Set up logging
logger = logging.getLogger(__name__)

class SolverManager:
    """
    Manager for solvers and constraints.
    
    This class provides a centralized interface for creating solvers with appropriate
    constraints and managing constraint configurations.
    """
    
    def __init__(self):
        """Initialize the solver manager."""
        self._available_constraints = {
            'demand': DemandConstraint,
            'supply': SupplyConstraint,
            'allowed_combinations': AllowedCombinationsConstraint,
            'production_rate': ProductionRateConstraint,
            'minimum_batch': MinimumBatchConstraint,
        }
        
        # Default constraint configurations
        self._default_configs = {
            'demand': {'equality': True},
            'supply': {'cumulative': True},
            'allowed_combinations': {},
            'production_rate': {'max_rate_change': 0.2},
            'minimum_batch': {'min_batch_size': 10},
        }
        
        # Default enabled constraints
        self._enabled_constraints = {
            'demand': True,
            'supply': True,
            'allowed_combinations': True,
            'production_rate': False,
            'minimum_batch': False,
        }
        
        # Custom configurations
        self._custom_configs = {}
    
    def get_available_constraints(self) -> List[str]:
        """
        Get the list of available constraint types.
        
        Returns:
            List[str]: List of constraint type names
        """
        return list(self._available_constraints.keys())
    
    def get_constraint_class(self, constraint_type: str) -> Optional[Type[Constraint]]:
        """
        Get the constraint class for a constraint type.
        
        Args:
            constraint_type: Name of the constraint type
            
        Returns:
            Optional[Type[Constraint]]: Constraint class, or None if not found
        """
        return self._available_constraints.get(constraint_type)
    
    def get_constraint_description(self, constraint_type: str) -> str:
        """
        Get the description of a constraint type.
        
        Args:
            constraint_type: Name of the constraint type
            
        Returns:
            str: Description of the constraint type, or empty string if not found
        """
        constraint_class = self.get_constraint_class(constraint_type)
        if constraint_class:
            instance = constraint_class()
            return instance.get_description()
        return ""
    
    def get_constraint_configuration_schema(self, constraint_type: str) -> Dict:
        """
        Get the configuration schema for a constraint type.
        
        Args:
            constraint_type: Name of the constraint type
            
        Returns:
            Dict: Configuration schema, or empty dict if not found
        """
        constraint_class = self.get_constraint_class(constraint_type)
        if constraint_class:
            instance = constraint_class()
            return instance.get_configuration_schema()
        return {}
    
    def is_constraint_enabled(self, constraint_type: str) -> bool:
        """
        Check if a constraint type is enabled.
        
        Args:
            constraint_type: Name of the constraint type
            
        Returns:
            bool: True if the constraint is enabled, False otherwise
        """
        return self._enabled_constraints.get(constraint_type, False)
    
    def set_constraint_enabled(self, constraint_type: str, enabled: bool) -> None:
        """
        Enable or disable a constraint type.
        
        Args:
            constraint_type: Name of the constraint type
            enabled: True to enable, False to disable
            
        Raises:
            ValueError: If the constraint type is not valid
        """
        if constraint_type not in self._available_constraints:
            logger.error(f"Invalid constraint type: {constraint_type}")
            raise ValueError(f"Invalid constraint type: {constraint_type}")
        
        self._enabled_constraints[constraint_type] = enabled
    
    def get_constraint_configuration(self, constraint_type: str) -> Dict:
        """
        Get the configuration for a constraint type.
        
        Args:
            constraint_type: Name of the constraint type
            
        Returns:
            Dict: Configuration dictionary, or empty dict if not found or disabled
        """
        if not self.is_constraint_enabled(constraint_type):
            return {}
            
        # Start with default configuration
        config = self._default_configs.get(constraint_type, {}).copy()
        
        # Override with custom configuration if it exists
        if constraint_type in self._custom_configs:
            custom_config = self._custom_configs[constraint_type]
            config.update(custom_config)
            
        return config
    
    def set_constraint_configuration(self, constraint_type: str, config: Dict) -> None:
        """
        Set the configuration for a constraint type.
        
        Args:
            constraint_type: Name of the constraint type
            config: Configuration dictionary
        """
        if constraint_type in self._available_constraints:
            # Store the new configuration
            self._custom_configs[constraint_type] = config
            
            # Important: Clear any cached instances in constraint registry
            # This ensures that a new constraint instance will be created with the updated config
            logger.info(f"Updated configuration for constraint '{constraint_type}': {config}")
    
    def reset_constraint_configuration(self, constraint_type: str) -> None:
        """
        Reset the configuration for a constraint type to default and disable it.
        
        Args:
            constraint_type: Name of the constraint type
        """
        if constraint_type in self._custom_configs:
            del self._custom_configs[constraint_type]
        self._enabled_constraints[constraint_type] = False
    
    def create_solver(self, solver_name: str, with_constraints: bool = True, **kwargs) -> SolverInterface:
        """
        Create a solver with the currently enabled constraints.
        
        Args:
            solver_name: Name of the solver
            with_constraints: Whether to add constraints to the solver
            **kwargs: Additional arguments for the solver
            
        Returns:
            SolverInterface: Solver instance
            
        Raises:
            ValueError: If a constraint configuration is invalid
        """
        logger.debug(f"Creating solver '{solver_name}' with constraints: {with_constraints}")
        
        # Create the solver
        solver = SolverFactory.create_solver(solver_name, **kwargs)
        
        # Add constraints if requested
        if with_constraints:
            for constraint_type, enabled in self._enabled_constraints.items():
                if enabled:
                    logger.debug(f"Adding constraint '{constraint_type}' to solver")
                    
                    # Get constraint configuration
                    config = self.get_constraint_configuration(constraint_type)
                    logger.debug(f"Constraint '{constraint_type}' configuration: {config}")
                    
                    # Get constraint class
                    constraint_class = self.get_constraint_class(constraint_type)
                    if constraint_class:
                        try:
                            # Important: For supply constraint, explicitly log the cumulative parameter
                            if constraint_type == 'supply' and 'cumulative' in config:
                                logger.info(f"Creating supply constraint with cumulative={config['cumulative']}")
                                
                            # Ensure we're using a fresh copy of the config
                            constraint = constraint_class(**config.copy())
                            solver.add_constraint(constraint_type, constraint)
                            logger.debug(f"Successfully added constraint '{constraint_type}'")
                        except Exception as e:
                            logger.error(f"Failed to add constraint '{constraint_type}': {str(e)}")
                            raise ValueError(f"Invalid configuration for constraint '{constraint_type}': {str(e)}")
                    else:
                        logger.warning(f"Constraint class not found for type '{constraint_type}'")
                else:
                    logger.debug(f"Skipping disabled constraint '{constraint_type}'")
        
        return solver
    
    def get_all_enabled_constraints(self) -> Dict[str, Dict]:
        """
        Get all enabled constraints with their configurations.
        
        Returns:
            Dict[str, Dict]: Dictionary mapping constraint types to configurations
        """
        result = {}
        for constraint_type, enabled in self._enabled_constraints.items():
            if enabled:
                result[constraint_type] = self.get_constraint_configuration(constraint_type)
        return result
    
    def create_constraint(self, constraint_type: str, **config) -> Optional[Constraint]:
        """
        Create a constraint instance with the given configuration.
        
        Args:
            constraint_type: Name of the constraint type
            **config: Configuration parameters
            
        Returns:
            Optional[Constraint]: Constraint instance, or None if not found
        """
        constraint_class = self.get_constraint_class(constraint_type)
        if constraint_class:
            return constraint_class(**config)
        return None
    
    def get_serializable_configuration(self) -> Dict:
        """
        Get a serializable representation of the current configuration.
        
        Returns:
            Dict: Serializable configuration dictionary
        """
        return {
            'enabled_constraints': self._enabled_constraints.copy(),
            'custom_configs': self._custom_configs.copy(),
        }
    
    def load_configuration(self, config: Dict) -> None:
        """
        Load configuration from a serializable representation.
        
        Args:
            config: Serializable configuration dictionary
        """
        # Load enabled constraints
        if 'enabled_constraints' in config:
            for constraint_type, enabled in config['enabled_constraints'].items():
                if constraint_type in self._available_constraints:
                    self._enabled_constraints[constraint_type] = enabled
        
        # Load custom configurations from the 'custom_configs' field (old format)
        if 'custom_configs' in config:
            for constraint_type, custom_config in config['custom_configs'].items():
                if constraint_type in self._available_constraints:
                    self._custom_configs[constraint_type] = custom_config
        
        # Also load from the 'constraints' field (new format) if present
        if 'constraints' in config:
            for constraint_type, custom_config in config['constraints'].items():
                if constraint_type in self._available_constraints:
                    # Only update if the constraint type exists
                    self._custom_configs[constraint_type] = custom_config
                    logger.info(f"Loaded configuration for constraint '{constraint_type}': {custom_config}") 