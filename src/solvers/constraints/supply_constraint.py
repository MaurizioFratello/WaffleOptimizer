"""
Supply Constraint Module for Waffle Production Optimization.

This module implements the supply limitation constraint for the optimization model.
"""
from typing import Dict, Any, List

from src.solvers.constraints.base import Constraint


class SupplyConstraint(Constraint):
    """
    Constraint to enforce pan supply limitations.
    
    This constraint ensures that the total usage of each pan type across all waffle types
    does not exceed the available supply in each week. It can optionally implement
    cumulative constraints where unused pans from earlier weeks can be used in later weeks.
    """
    
    def __init__(self, cumulative: bool = True):
        """
        Initialize the supply constraint.
        
        Args:
            cumulative: If True, unused pans from earlier weeks can be used in later weeks
                        If False, unused pans from earlier weeks cannot be used
        """
        self.cumulative = cumulative
    
    def apply_to_ortools(self, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply supply constraint to an OR-Tools model.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])
        supply = data['supply']
        
        if self.cumulative:
            # Cumulative supply constraints - allow unused pans to carry over
            for p in pan_types:
                cumulative_supply = 0
                for t in weeks:
                    # Add the supply for this week to the cumulative total
                    if (p, t) in supply:
                        cumulative_supply += supply[(p, t)]
                    
                    # Create a constraint: cumulative usage <= cumulative supply
                    constraint = solver.Constraint(-solver.infinity(), cumulative_supply)
                    for w in data['waffle_types']:
                        for earlier_t in [week for week in weeks if week <= t]:
                            if (w, p, earlier_t) in variables:
                                constraint.SetCoefficient(variables[(w, p, earlier_t)], 1)
        else:
            # Weekly supply constraints - no carry over
            for p in pan_types:
                for t in weeks:
                    if (p, t) in supply:
                        # Create a constraint: usage <= supply for this week
                        constraint = solver.Constraint(-solver.infinity(), supply[(p, t)])
                        for w in data['waffle_types']:
                            if (w, p, t) in variables:
                                constraint.SetCoefficient(variables[(w, p, t)], 1)
    
    def apply_to_pulp(self, problem: Any, variables: Dict, data: Dict) -> None:
        """
        Apply supply constraint to a PuLP model.
        
        Args:
            problem: PuLP problem instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        import pulp
        
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])
        supply = data['supply']
        
        if self.cumulative:
            # Cumulative supply constraints - allow unused pans to carry over
            for p in pan_types:
                cumulative_supply = 0
                for t in weeks:
                    # Add the supply for this week to the cumulative total
                    if (p, t) in supply:
                        cumulative_supply += supply[(p, t)]
                    
                    # Create variables for all waffle types and weeks up to current week
                    usage_vars = [variables[(w, p, earlier_t)] 
                                for w in data['waffle_types'] 
                                for earlier_t in weeks if earlier_t <= t
                                if (w, p, earlier_t) in variables]
                    
                    # Create constraint: cumulative usage <= cumulative supply
                    problem += pulp.lpSum(usage_vars) <= cumulative_supply, f"CumulativeSupply_{p}_{t}"
        else:
            # Weekly supply constraints - no carry over
            for p in pan_types:
                for t in weeks:
                    if (p, t) in supply:
                        # Create variables for all waffle types in this week
                        usage_vars = [variables[(w, p, t)] 
                                    for w in data['waffle_types'] 
                                    if (w, p, t) in variables]
                        
                        # Create constraint: usage <= supply for this week
                        problem += pulp.lpSum(usage_vars) <= supply[(p, t)], f"Supply_{p}_{t}"
    
    def validate_data(self, data: Dict) -> bool:
        """
        Validate that required data for this constraint is present.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            bool: True if all required data is present, False otherwise
        """
        required_fields = ['waffle_types', 'pan_types', 'weeks', 'supply']
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
                "cumulative": {
                    "type": "boolean",
                    "description": "If True, unused pans from earlier weeks can be used in later weeks."
                }
            },
            "required": []
        } 