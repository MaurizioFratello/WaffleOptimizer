"""
Minimum Batch Constraint Module for Waffle Production Optimization.

This module implements the minimum batch size constraint for the optimization model.
"""
from typing import Dict, Any, Union

from src.solvers.constraints.base import Constraint


class MinimumBatchConstraint(Constraint):
    """
    Constraint to enforce minimum batch sizes for production.
    
    This constraint ensures that if a particular waffle type is produced on a particular
    pan type in a given week, the quantity must be at least a specified minimum batch size.
    This prevents impractical small production batches.
    """
    
    def __init__(self, min_batch_size: Union[int, Dict] = 10):
        """
        Initialize the minimum batch constraint.
        
        Args:
            min_batch_size: Minimum batch size for production
                           Can be a single value for all combinations,
                           or a dictionary mapping (waffle_type, pan_type) to minimum batch size
        """
        self.min_batch_size = min_batch_size
    
    def get_min_batch_size(self, waffle_type: str, pan_type: str) -> int:
        """
        Get the minimum batch size for a specific waffle type and pan type.
        
        Args:
            waffle_type: Waffle type
            pan_type: Pan type
            
        Returns:
            int: Minimum batch size for the specified combination
        """
        if isinstance(self.min_batch_size, dict):
            return self.min_batch_size.get((waffle_type, pan_type), 
                                         self.min_batch_size.get('default', 10))
        return self.min_batch_size
    
    def apply_to_ortools(self, solver: Any, variables: Dict, data: Dict) -> None:
        """
        Apply minimum batch constraint to an OR-Tools model.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])
        
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if (w, p, t) in variables:
                        # Get minimum batch size for this combination
                        min_batch = self.get_min_batch_size(w, p)
                        
                        # Create a binary variable to indicate if this combination is used
                        is_used = solver.IntVar(0, 1, f"is_used_{w}_{p}_{t}")
                        
                        # Get a large upper bound (big-M) for this variable
                        # We use the supply for this pan type in this week if available,
                        # otherwise use a sufficiently large number
                        big_m = data.get('supply', {}).get((p, t), 1000)
                        
                        # If x > 0 then is_used = 1
                        solver.Add(variables[(w, p, t)] <= big_m * is_used)
                        
                        # If is_used = 1 then x >= min_batch
                        solver.Add(variables[(w, p, t)] >= min_batch * is_used)
    
    def apply_to_pulp(self, problem: Any, variables: Dict, data: Dict) -> None:
        """
        Apply minimum batch constraint to a PuLP model.
        
        Args:
            problem: PuLP problem instance
            variables: Dictionary of decision variables
            data: Dictionary containing optimization data
        """
        import pulp
        
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])
        
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if (w, p, t) in variables:
                        # Get minimum batch size for this combination
                        min_batch = self.get_min_batch_size(w, p)
                        
                        # Create a binary variable to indicate if this combination is used
                        is_used = pulp.LpVariable(f"is_used_{w}_{p}_{t}", cat=pulp.LpBinary)
                        
                        # Get a large upper bound (big-M) for this variable
                        big_m = data.get('supply', {}).get((p, t), 1000)
                        
                        # If x > 0 then is_used = 1
                        problem += variables[(w, p, t)] <= big_m * is_used, \
                                f"MinBatch_IsUsed1_{w}_{p}_{t}"
                        
                        # If is_used = 1 then x >= min_batch
                        problem += variables[(w, p, t)] >= min_batch * is_used, \
                                f"MinBatch_IsUsed2_{w}_{p}_{t}"
    
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
                "min_batch_size": {
                    "oneOf": [
                        {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Minimum batch size for all combinations"
                        },
                        {
                            "type": "object",
                            "additionalProperties": {
                                "type": "integer",
                                "minimum": 1
                            },
                            "description": "Dictionary mapping (waffle_type, pan_type) to minimum batch size"
                        }
                    ],
                    "default": 10
                }
            },
            "required": []
        } 