"""
Production Rate Constraint Module for Waffle Production Optimization.

This module implements the production rate change constraint for the optimization model.
"""
from typing import Dict, Any

from src.solvers.constraints.base import Constraint


class ProductionRateConstraint(Constraint):
    """
    Constraint to limit production rate changes between consecutive weeks.
    
    This constraint ensures that the production rate for each waffle type does not change
    too drastically between consecutive weeks, providing production stability.
    """
    
    def __init__(self, max_rate_change: float = 0.2):
        """
        Initialize the production rate constraint.
        
        Args:
            max_rate_change: Maximum allowed proportional change in production rate
                            between consecutive weeks (default: 0.2 = 20%)
        """
        self.max_rate_change = max_rate_change
    
    def apply_to_ortools(self, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply production rate constraint to an OR-Tools model.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])
        
        # Skip if only one week
        if len(weeks) < 2:
            return
        
        for w in waffle_types:
            for i in range(1, len(weeks)):
                prev_week = weeks[i-1]
                curr_week = weeks[i]
                
                # Calculate total production for each week
                # We need to check which variables exist first
                prev_vars = [(w, p, prev_week) for p in pan_types if (w, p, prev_week) in variables]
                curr_vars = [(w, p, curr_week) for p in pan_types if (w, p, curr_week) in variables]
                
                # Skip if no variables for this waffle type in either week
                if not prev_vars or not curr_vars:
                    continue
                
                # Create linear expressions for total production in each week
                prev_prod = solver.Sum([variables[var] for var in prev_vars])
                curr_prod = solver.Sum([variables[var] for var in curr_vars])
                
                # Create dummy variable for previous week production to handle case where it's zero
                # This avoids division by zero in the constraint
                prev_prod_dummy = solver.IntVar(1, solver.infinity(), f"prev_prod_dummy_{w}_{prev_week}")
                
                # Force prev_prod_dummy to be at least 1 and at least as large as prev_prod
                solver.Add(prev_prod_dummy >= prev_prod)
                
                # Enforce maximum increase: curr_prod <= prev_prod_dummy * (1 + max_rate_change)
                solver.Add(curr_prod <= prev_prod_dummy * (1 + self.max_rate_change))
                
                # Enforce maximum decrease: curr_prod >= prev_prod * (1 - max_rate_change)
                # Only apply if prev_prod is positive (to avoid infeasibility)
                # We create a conditional constraint using a big-M approach
                big_m = sum(data.get('supply', {}).get((p, t), 0) for p in pan_types for t in weeks)
                has_prev_prod = solver.IntVar(0, 1, f"has_prev_prod_{w}_{prev_week}")
                
                # has_prev_prod = 1 if prev_prod > 0, else 0
                solver.Add(prev_prod <= big_m * has_prev_prod)
                solver.Add(prev_prod >= has_prev_prod)
                
                # Only apply decrease constraint if has_prev_prod = 1
                solver.Add(curr_prod >= prev_prod * (1 - self.max_rate_change) - 
                         big_m * (1 - has_prev_prod))
    
    def apply_to_pulp(self, problem: Any, variables: Dict, data: Dict) -> None:
        """
        Apply production rate constraint to a PuLP model.
        
        Args:
            problem: PuLP problem instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        import pulp
        
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])
        
        # Skip if only one week
        if len(weeks) < 2:
            return
        
        for w in waffle_types:
            for i in range(1, len(weeks)):
                prev_week = weeks[i-1]
                curr_week = weeks[i]
                
                # Calculate total production for each week
                # We need to check which variables exist first
                prev_vars = [variables[(w, p, prev_week)] for p in pan_types 
                           if (w, p, prev_week) in variables]
                curr_vars = [variables[(w, p, curr_week)] for p in pan_types 
                           if (w, p, curr_week) in variables]
                
                # Skip if no variables for this waffle type in either week
                if not prev_vars or not curr_vars:
                    continue
                
                # Create expressions for total production in each week
                prev_prod = pulp.lpSum(prev_vars)
                curr_prod = pulp.lpSum(curr_vars)
                
                # Create dummy variable for previous week production
                prev_prod_dummy = pulp.LpVariable(f"prev_prod_dummy_{w}_{prev_week}", 
                                               lowBound=1, cat=pulp.LpInteger)
                
                # Force prev_prod_dummy to be at least as large as prev_prod
                problem += prev_prod_dummy >= prev_prod, f"PrevProdDummy_{w}_{prev_week}"
                
                # Enforce maximum increase: curr_prod <= prev_prod_dummy * (1 + max_rate_change)
                problem += curr_prod <= prev_prod_dummy * (1 + self.max_rate_change), \
                         f"MaxIncrease_{w}_{prev_week}_to_{curr_week}"
                
                # Enforce maximum decrease: curr_prod >= prev_prod * (1 - max_rate_change)
                # Only apply if prev_prod is positive (to avoid infeasibility)
                big_m = sum(data.get('supply', {}).get((p, t), 0) for p in pan_types for t in weeks)
                has_prev_prod = pulp.LpVariable(f"has_prev_prod_{w}_{prev_week}", 
                                             cat=pulp.LpBinary)
                
                # has_prev_prod = 1 if prev_prod > 0, else 0
                problem += prev_prod <= big_m * has_prev_prod, \
                         f"HasPrevProd1_{w}_{prev_week}"
                problem += prev_prod >= has_prev_prod, \
                         f"HasPrevProd2_{w}_{prev_week}"
                
                # Only apply decrease constraint if has_prev_prod = 1
                problem += curr_prod >= prev_prod * (1 - self.max_rate_change) - \
                         big_m * (1 - has_prev_prod), \
                         f"MaxDecrease_{w}_{prev_week}_to_{curr_week}"
    
    def validate_data(self, data: Dict) -> bool:
        """
        Validate that required data for this constraint is present.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            bool: True if all required data is present, False otherwise
        """
        required_fields = ['waffle_types', 'pan_types', 'weeks']
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
                "max_rate_change": {
                    "type": "number",
                    "description": "Maximum allowed proportional change in production rate between consecutive weeks",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 0.2
                }
            },
            "required": []
        } 