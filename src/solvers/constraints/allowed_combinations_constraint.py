"""
Allowed Combinations Constraint Module for Waffle Production Optimization.

This module implements the allowed combinations constraint for the optimization model.
"""
from typing import Dict, Any

from src.solvers.constraints.base import Constraint


class AllowedCombinationsConstraint(Constraint):
    """
    Constraint to enforce allowed combinations of waffle types and pan types.
    
    This constraint ensures that only allowed combinations of waffle types and pan types
    are used in the optimization model.
    """
    
    def __init__(self):
        """Initialize the allowed combinations constraint."""
        pass
    
    def apply_to_ortools(self, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply allowed combinations constraint to an OR-Tools model.
        
        Note: This constraint is implicitly enforced during variable creation,
        where variables are only created for allowed combinations. This method
        is a no-op for OR-Tools, but is included for completeness.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        # No explicit constraint needed - already enforced by variable creation
        pass
    
    def apply_to_pulp(self, problem: Any, variables: Dict, data: Dict) -> None:
        """
        Apply allowed combinations constraint to a PuLP model.
        
        Note: This constraint is implicitly enforced during variable creation,
        where variables are only created for allowed combinations. This method
        is a no-op for PuLP, but is included for completeness.
        
        Args:
            problem: PuLP problem instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        # No explicit constraint needed - already enforced by variable creation
        pass
    
    def validate_data(self, data: Dict) -> bool:
        """
        Validate that required data for this constraint is present.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            bool: True if all required data is present, False otherwise
        """
        required_fields = ['waffle_types', 'pan_types', 'allowed']
        return all(field in data for field in required_fields)
    
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