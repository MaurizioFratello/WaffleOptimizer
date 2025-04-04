"""
Demand Constraint Module for Waffle Production Optimization.

This module implements the demand satisfaction constraint for the optimization model.
"""
from typing import Dict, Any

from src.solvers.constraints.base import Constraint


class DemandConstraint(Constraint):
    """
    Constraint to ensure demand satisfaction for each waffle type in each week.
    
    This constraint ensures that the production for each waffle type in each week
    exactly meets the demand specified in the input data.
    """
    
    def __init__(self, equality: bool = True):
        """
        Initialize the demand constraint.
        
        Args:
            equality: If True, demand must be exactly met
                     If False, production can exceed demand (>=)
        """
        self.equality = equality
    
    def apply_to_ortools(self, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply demand constraint to an OR-Tools model.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        waffle_types = data['waffle_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    if self.equality:
                        # Equality constraint (exactly meet demand)
                        constraint = solver.Constraint(demand[(w, t)], demand[(w, t)])
                    else:
                        # Inequality constraint (meet or exceed demand)
                        constraint = solver.Constraint(demand[(w, t)], solver.infinity())
                        
                    for p in data['pan_types']:
                        if (w, p, t) in variables:
                            constraint.SetCoefficient(variables[(w, p, t)], 1)
    
    def apply_to_pulp(self, problem: Any, variables: Dict, data: Dict) -> None:
        """
        Apply demand constraint to a PuLP model.
        
        Args:
            problem: PuLP problem instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        import pulp
        
        waffle_types = data['waffle_types']
        weeks = sorted(data['weeks'])
        demand = data['demand']
        
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    # Create expression for sum of production for this waffle type and week
                    prod_sum = pulp.lpSum(variables[(w, p, t)] for p in data['pan_types'] 
                                      if (w, p, t) in variables)
                    
                    if self.equality:
                        # Equality constraint (exactly meet demand)
                        problem += prod_sum == demand[(w, t)], f"Demand_{w}_{t}"
                    else:
                        # Inequality constraint (meet or exceed demand)
                        problem += prod_sum >= demand[(w, t)], f"Demand_{w}_{t}"
    
    def validate_data(self, data: Dict) -> bool:
        """
        Validate that required data for this constraint is present.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            bool: True if all required data is present, False otherwise
        """
        required_fields = ['waffle_types', 'pan_types', 'weeks', 'demand']
        return all(field in data for field in required_fields)
    
    def get_configuration_schema(self) -> Dict:
        """
        Get the configuration schema for this constraint.
        
        Returns:
            Dict: Dictionary describing the configuration parameters for this constraint
        """
        return {
            "type": "object",
            "properties": {
                "equality": {
                    "type": "boolean",
                    "description": "If True, demand must be exactly met. If False, production can exceed demand."
                }
            },
            "required": []
        } 