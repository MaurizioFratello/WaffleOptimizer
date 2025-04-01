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
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Waffles per waffle type
        allowed = data['allowed']
        cost = data['cost']
        
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
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        # Using equality constraint (==) to use exactly the demanded number of pans
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    constraint_expr = pulp.lpSum(
                        self.variables.get((w, p, t), 0) for p in pan_types if (w, p, t) in self.variables
                    )
                    self.model += constraint_expr == demand[(w, t)], f"demand_{w}_{t}"
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        # This allows unused pans from earlier weeks to be used in later weeks
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Create a constraint: cumulative usage <= cumulative supply
                constraint_expr = pulp.lpSum(
                    self.variables.get((w, p, earlier_t), 0)
                    for w in waffle_types
                    for earlier_t in [week for week in weeks if week <= t]
                    if (w, p, earlier_t) in self.variables
                )
                self.model += constraint_expr <= cumulative_supply, f"supply_{p}_{t}"
    
    def build_maximize_output_model(self, data: Dict, limit_to_demand: bool = False) -> None:
        """
        Build an optimization model to maximize waffle output.
        
        Args:
            data: Dictionary containing optimization data
            limit_to_demand: If True, production will be limited to exactly meet demand
                             If False (default), production can exceed demand
        """
        self.data = data
        self.model_type = 'maximize_output'
        
        # Create PuLP model
        self.model = pulp.LpProblem("WaffleOptimizer_MaxOutput", pulp.LpMaximize)
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Waffles per waffle type
        allowed = data['allowed']
        
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
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        # For maximizing output, we always use limit_to_demand=True to ensure we use exactly
        # the number of pans demanded (not more or less)
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    constraint_expr = pulp.lpSum(
                        self.variables.get((w, p, t), 0) for p in pan_types if (w, p, t) in self.variables
                    )
                    # Always use equality constraint to use exactly the demanded number of pans
                    self.model += constraint_expr == demand[(w, t)], f"demand_{w}_{t}"
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        # This allows unused pans from earlier weeks to be used in later weeks
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Create a constraint: cumulative usage <= cumulative supply
                constraint_expr = pulp.lpSum(
                    self.variables.get((w, p, earlier_t), 0)
                    for w in waffle_types
                    for earlier_t in [week for week in weeks if week <= t]
                    if (w, p, earlier_t) in self.variables
                )
                self.model += constraint_expr <= cumulative_supply, f"supply_{p}_{t}"
    
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        if self.model is None:
            raise ValueError("Model has not been built. Call build_minimize_cost_model or build_maximize_output_model first.")
            
        # Create appropriate solver
        solver = self._create_solver()
        
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        self.model.solve(solver)
        
        # Calculate solution time
        solution_time = time.time() - self.start_time
        
        # Get solution status
        status = pulp.LpStatus[self.model.status]
        self.solution_status = status
        
        # Check if the solution is optimal or feasible
        is_optimal = status == "Optimal"
        is_feasible = is_optimal or status == "Feasible"
        
        # Get the objective value if the problem is feasible
        objective_value = None
        if is_feasible:
            objective_value = pulp.value(self.model.objective)
        
        # Prepare solution information
        solution_info = {
            'status': status,
            'is_optimal': is_optimal,
            'is_feasible': is_feasible,
            'objective_value': objective_value,
            'solution_time': solution_time,
            'solver_name': f"PuLP_{self.solver_name}"
        }
        
        return solution_info
    
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        if self.model is None or self.solution_status is None:
            raise ValueError("Model has not been solved. Call solve_model first.")
            
        # Check if the solution is feasible
        if self.solution_status not in ["Optimal", "Feasible"]:
            raise ValueError(f"Cannot get solution: problem status is '{self.solution_status}'")
        
        # Extract solution variables and their values
        solution_variables = {}
        for var_key, var in self.variables.items():
            value = pulp.value(var)
            # Only include non-zero values to keep the solution compact
            if value is not None and abs(value) > 1e-6:
                solution_variables[var_key] = int(round(value))  # Round to nearest integer
        
        # Get the objective value
        objective_value = pulp.value(self.model.objective)
        
        # Calculate solution metrics based on model type
        if self.model_type == 'minimize_cost':
            total_cost = objective_value
            total_output = sum(
                self.data['wpp'].get(w, 0) * count
                for (w, p, t), count in solution_variables.items()
            )
            metrics = {
                'total_cost': total_cost,
                'total_output': total_output,
                'average_cost_per_waffle': total_cost / total_output if total_output > 0 else float('inf')
            }
        else:  # maximize_output
            total_output = objective_value
            total_cost = sum(
                self.data['cost'].get((w, p), 0) * self.data['wpp'].get(w, 0) * count
                for (w, p, t), count in solution_variables.items()
            )
            metrics = {
                'total_output': total_output,
                'total_cost': total_cost,
                'average_cost_per_waffle': total_cost / total_output if total_output > 0 else float('inf')
            }
        
        # Prepare full solution
        solution = {
            'variables': solution_variables,
            'objective_value': objective_value,
            'metrics': metrics,
            'model_type': self.model_type,
            'solution_time': time.time() - self.start_time,
            'status': self.solution_status
        }
        
        return solution 