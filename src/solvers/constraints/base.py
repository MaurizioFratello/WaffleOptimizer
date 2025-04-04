"""
Constraint System Base Module for Waffle Production Optimization.

This module defines the abstract base class for constraints and a registry system
to manage constraints across different solver implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class Constraint(ABC):
    """
    Abstract base class for optimization constraints.
    
    All constraints must implement methods for both OR-Tools and PuLP solvers
    to ensure compatibility across solver implementations.
    """
    
    @abstractmethod
    def apply_to_ortools(self, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply this constraint to an OR-Tools model.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        pass
    
    @abstractmethod
    def apply_to_pulp(self, problem: Any, variables: Dict, data: Dict) -> None:
        """
        Apply this constraint to a PuLP model.
        
        Args:
            problem: PuLP problem instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """
        Validate that required data for this constraint is present.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            bool: True if all required data is present, False otherwise
        """
        pass
    
    def get_configuration_schema(self) -> Dict:
        """
        Get the configuration schema for this constraint.
        
        Returns:
            Dict: Dictionary describing the configuration parameters for this constraint
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def get_description(self) -> str:
        """
        Get a human-readable description of this constraint.
        
        Returns:
            str: Description of the constraint
        """
        return self.__class__.__doc__ or "No description available"


class ConstraintRegistry:
    """
    Registry for managing and applying constraints.
    
    This class provides a centralized mechanism for registering, configuring,
    and applying constraints to different solver implementations.
    """
    
    def __init__(self):
        """Initialize an empty constraint registry."""
        self._constraints = {}
    
    def register_constraint(self, name: str, constraint: Constraint) -> None:
        """
        Register a constraint with the registry.
        
        Args:
            name: Name of the constraint
            constraint: Constraint instance
        """
        self._constraints[name] = constraint
    
    def unregister_constraint(self, name: str) -> None:
        """
        Remove a constraint from the registry.
        
        Args:
            name: Name of the constraint to remove
        """
        if name in self._constraints:
            del self._constraints[name]
    
    def get_constraint(self, name: str) -> Optional[Constraint]:
        """
        Get a constraint by name.
        
        Args:
            name: Name of the constraint
            
        Returns:
            Optional[Constraint]: The constraint instance, or None if not found
        """
        return self._constraints.get(name)
    
    def get_all_constraints(self) -> Dict[str, Constraint]:
        """
        Get all registered constraints.
        
        Returns:
            Dict[str, Constraint]: Dictionary of all registered constraints
        """
        return self._constraints.copy()
    
    def apply_constraints(self, solver_type: str, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply all registered constraints to the solver model.
        
        Args:
            solver_type: Type of solver ('ortools' or 'pulp')
            solver: Solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        for name, constraint in self._constraints.items():
            if not constraint.validate_data(data):
                raise ValueError(f"Invalid data for constraint '{name}'")
                
            if solver_type.lower() == 'ortools':
                constraint.apply_to_ortools(solver, variables, data)
            elif solver_type.lower() == 'pulp':
                constraint.apply_to_pulp(solver, variables, data)
            else:
                raise ValueError(f"Unsupported solver type: {solver_type}")
    
    def validate_all_data(self, data: Dict) -> Dict[str, bool]:
        """
        Validate data for all registered constraints.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            Dict[str, bool]: Dictionary mapping constraint names to validation results
        """
        return {name: constraint.validate_data(data) 
                for name, constraint in self._constraints.items()}
    
    def get_all_configuration_schemas(self) -> Dict[str, Dict]:
        """
        Get configuration schemas for all registered constraints.
        
        Returns:
            Dict[str, Dict]: Dictionary mapping constraint names to configuration schemas
        """
        return {name: constraint.get_configuration_schema() 
                for name, constraint in self._constraints.items()} 