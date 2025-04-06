"""
PuLP Implementation for Waffle Production Optimization.

This module provides the implementation for PuLP-based solvers including:
- CBC
- GLPK
- HiGHS (via PuLP)
- COIN_CMD
- COINMP_DLL
- CHOCO_CMD
- MIPCL_CMD
- SCIP
"""
from typing import Dict, List, Any
import time
import pulp
from src.solvers.base import SolverInterface

class PulpSolver(SolverInterface):
    """
    Implementation of the SolverInterface using PuLP.
    """
    
    def __init__(self, time_limit: int = 60, optimality_gap: float = 0.005, solver_name: str = 'HiGHS'):
        """
        Initialize the PuLP solver.
        
        Args:
            time_limit: Time limit for solving the model in seconds
            optimality_gap: Maximum allowed optimality gap (default: 0.5%)
            solver_name: Name of the underlying solver (CBC, GLPK, HiGHS, etc.)
        """
        super().__init__()  # Initialize constraint registry
        self.time_limit = time_limit
        self.optimality_gap = optimality_gap
        self.solver_name = solver_name
        self.model = None
        self.variables = {}
        self.objective = None
        self.data = None
        self.model_type = None
        self.solution_status = None
        self.start_time = None
        
    def _create_solver(self):
        """Create the appropriate PuLP solver based on solver_name."""
        if self.solver_name.lower() == 'cbc':
            return pulp.PULP_CBC_CMD(timeLimit=self.time_limit, gapRel=self.optimality_gap)
        elif self.solver_name.lower() == 'glpk':
            # GLPK uses different parameter format. The options are passed as separate arguments to glpsol
            return pulp.GLPK_CMD(timeLimit=self.time_limit, options=["--mipgap", str(self.optimality_gap)])
        elif self.solver_name.lower() == 'highs':
            # HiGHS uses different parameter names in PuLP
            return pulp.HiGHS_CMD(timeLimit=self.time_limit, options=[f'mip_rel_gap={self.optimality_gap}'])
        elif self.solver_name.lower() == 'scip':
            return pulp.SCIP_CMD(timeLimit=self.time_limit, options=[f'limits/gap={self.optimality_gap}'])
        elif self.solver_name.lower() == 'coin_cmd':
            return pulp.COIN_CMD(timeLimit=self.time_limit, gapRel=self.optimality_gap, options=[f'ratioGap={self.optimality_gap}'])
        elif self.solver_name.lower() == 'coinmp_dll':
            return pulp.COINMP_DLL(timeLimit=self.time_limit, epgap=self.optimality_gap)
        elif self.solver_name.lower() == 'choco_cmd':
            # Choco has different parameters
            return pulp.CHOCO_CMD(timeLimit=self.time_limit)
        elif self.solver_name.lower() == 'mipcl_cmd':
            # MIPCL parameters
            return pulp.MIPCL_CMD(timeLimit=self.time_limit, gapRel=self.optimality_gap)
        else:
            # Default to CBC if unknown solver name
            return pulp.PULP_CBC_CMD(timeLimit=self.time_limit, gapRel=self.optimality_gap)
        
    def apply_constraints(self) -> None:
        """
        Apply all registered constraints to the model.
        """
        if self.model is None or self.data is None:
            raise ValueError("Model has not been built. Call build_minimize_cost_model or build_maximize_output_model first.")
        
        # Apply constraints using the constraint registry
        self.constraint_registry.apply_constraints('pulp', self.model, self.variables, self.data)
        
    def build_minimize_cost_model(self, data: Dict) -> None:
        """
        Build an optimization model to minimize production cost.
        
        Args:
            data: Dictionary containing optimization data
        """
        self.data = data
        self.model_type = 'minimize_cost'
        
        # Create PuLP model
        self.model = pulp.LpProblem("WaffleOptimizer_MinCost", pulp.LpMinimize)
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        allowed = data['allowed']
        cost = data['cost']
        wpp = data['wpp']  # Waffles per waffle type
        
        # Create decision variables: x[waffle_type, pan_type, week]
        # Represents the number of pans of type pan_type used to cook waffle_type in week
        self.variables = {}
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        var_name = f'x_{w}_{p}_{t}'
                        self.variables[(w, p, t)] = pulp.LpVariable(var_name, lowBound=0, cat=pulp.LpInteger)
        
        # Objective function: minimize total cost
        # Cost is calculated as: (number of pans) * (waffles per pan) * (cost per waffle)
        objective_expr = pulp.lpSum(
            cost.get((w, p), 0) * wpp.get(w, 0) * self.variables[(w, p, t)]
            for (w, p, t) in self.variables
        )
        self.model += objective_expr
        
        # Apply constraints from constraint registry
        self.apply_constraints()
    
    def build_maximize_output_model(self, data: Dict) -> None:
        """
        Build an optimization model to maximize waffle output.
        
        Args:
            data: Dictionary containing optimization data
        """
        self.data = data
        self.model_type = 'maximize_output'
        
        # Create PuLP model
        self.model = pulp.LpProblem("WaffleOptimizer_MaxOutput", pulp.LpMaximize)
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        allowed = data['allowed']
        wpp = data['wpp']  # Waffles per waffle type
        
        # Create decision variables: x[waffle_type, pan_type, week]
        # Represents the number of pans of type pan_type used to cook waffle_type in week
        self.variables = {}
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        var_name = f'x_{w}_{p}_{t}'
                        self.variables[(w, p, t)] = pulp.LpVariable(var_name, lowBound=0, cat=pulp.LpInteger)
        
        # Objective function: maximize total waffle output
        objective_expr = pulp.lpSum(
            wpp.get(w, 0) * self.variables[(w, p, t)]
            for (w, p, t) in self.variables
        )
        self.model += objective_expr
        
        # Apply constraints from constraint registry
        self.apply_constraints()
    
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        if self.model is None:
            raise ValueError("Model has not been built. Call build_minimize_cost_model or build_maximize_output_model first.")
        
        # Create solver instance
        solver = self._create_solver()
        
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        status = self.model.solve(solver)
        
        # Map PuLP status to a human-readable string
        status_map = {
            pulp.LpStatusOptimal: "OPTIMAL",
            pulp.LpStatusNotSolved: "NOT_SOLVED",
            pulp.LpStatusInfeasible: "INFEASIBLE",
            pulp.LpStatusUnbounded: "UNBOUNDED",
            pulp.LpStatusUndefined: "UNDEFINED"
        }
        
        self.solution_status = status_map.get(status, "UNKNOWN")
        
        # Return solution information
        return {
            "status": self.solution_status,
            "solve_time": time.time() - self.start_time,
            "objective_value": pulp.value(self.model.objective) if self.solution_status == "OPTIMAL" else None,
            "model_type": self.model_type
        }
    
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        if self.model is None or self.solution_status != "OPTIMAL":
            return {
                "status": self.solution_status if self.solution_status else "NOT_SOLVED",
                "values": {},
                "objective_value": None,
                "model_type": self.model_type
            }
        
        # Extract solution values
        solution_values = {}
        for key, var in self.variables.items():
            if pulp.value(var) > 0:
                solution_values[key] = pulp.value(var)
        
        return {
            "status": self.solution_status,
            "values": solution_values,
            "objective_value": pulp.value(self.model.objective),
            "model_type": self.model_type,
            "solve_time": time.time() - self.start_time if self.start_time else None
        } 