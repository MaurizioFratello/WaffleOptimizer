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
from solver_interface import SolverInterface

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
        objective_expr = pulp.lpSum(
            cost.get((w, p), 0) * wpp.get(w, 0) * self.variables[(w, p, t)]
            for (w, p, t) in self.variables
        )
        self.model += objective_expr
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    constraint_expr = pulp.lpSum(
                        self.variables.get((w, p, t), 0) for p in pan_types if (w, p, t) in self.variables
                    )
                    self.model += constraint_expr >= demand[(w, t)], f"demand_{w}_{t}"
        
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
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    constraint_expr = pulp.lpSum(
                        self.variables.get((w, p, t), 0) for p in pan_types if (w, p, t) in self.variables
                    )
                    if limit_to_demand:
                        # Equality constraint (exactly meet demand)
                        self.model += constraint_expr == demand[(w, t)], f"demand_{w}_{t}"
                    else:
                        # Inequality constraint (at least meet demand)
                        self.model += constraint_expr >= demand[(w, t)], f"demand_{w}_{t}"
        
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
        if not self.model:
            raise ValueError("No model has been built. Call build_minimize_cost_model or build_maximize_output_model first.")
            
        # Create solver
        solver = self._create_solver()
        
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        self.model.solve(solver)
        
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        
        # Map PuLP status to our status names
        status_map = {
            pulp.LpStatusOptimal: 'OPTIMAL',
            pulp.LpStatusNotSolved: 'NOT_SOLVED',
            pulp.LpStatusInfeasible: 'INFEASIBLE',
            pulp.LpStatusUnbounded: 'UNBOUNDED',
            pulp.LpStatusUndefined: 'UNDEFINED'
        }
        
        self.solution_status = status_map.get(self.model.status, 'UNKNOWN')
        
        # Get solver statistics
        objective_value = pulp.value(self.model.objective) if self.model.status == pulp.LpStatusOptimal else None
        best_bound = None  # PuLP doesn't provide this directly
        nodes = None  # PuLP doesn't provide this directly
        gap = None  # PuLP doesn't provide this directly
        wall_time = elapsed_time
        
        # Print progress information
        print(f"\nSolver Progress:")
        print(f"Status: {self.solution_status}")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")
        if objective_value is not None:
            print(f"Objective Value: {objective_value:.2f}")
        
        return {
            'status': self.solution_status,
            'objective_value': objective_value,
            'wall_time': wall_time,
            'nodes': nodes,
            'best_bound': best_bound,
            'gap': gap
        }
    
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        if not self.model or self.solution_status not in ['OPTIMAL']:
            raise ValueError("No feasible solution is available.")
            
        # Extract solution values
        solution_values = {}
        for (w, p, t), var in self.variables.items():
            value = var.value()
            if value and value > 0:
                solution_values[(w, p, t)] = value
        
        # Calculate additional metrics
        waffle_types = self.data['waffle_types']
        pan_types = self.data['pan_types']
        weeks = self.data['weeks']
        wpp = self.data['wpp']
        
        # Total waffles produced by type and week
        waffles_by_type_week = {}
        for w in waffle_types:
            for t in weeks:
                waffles_by_type_week[(w, t)] = 0
                # Use waffles per waffle type (not per pan)
                waffle_wpp = wpp.get(w, 0)
                for p in pan_types:
                    if (w, p, t) in solution_values:
                        waffles_by_type_week[(w, t)] += solution_values[(w, p, t)] * waffle_wpp
        
        # Total pans used by type and week
        pans_by_type_week = {}
        for p in pan_types:
            for t in weeks:
                pans_by_type_week[(p, t)] = 0
                for w in waffle_types:
                    if (w, p, t) in solution_values:
                        pans_by_type_week[(p, t)] += solution_values[(w, p, t)]
        
        # Total waffles produced
        total_waffles = sum(waffles_by_type_week.values())
        
        # Calculate total cost for all optimization types
        cost = self.data['cost']
        total_cost = 0
        for (w, p, t), value in solution_values.items():
            waffle_cost = cost.get((w, p), 0)
            waffle_wpp = wpp.get(w, 0)  # Use waffles per waffle type
            total_cost += waffle_cost * waffle_wpp * value
        
        return {
            'status': self.solution_status,
            'objective_value': pulp.value(self.model.objective),
            'solution_values': solution_values,
            'waffles_by_type_week': waffles_by_type_week,
            'pans_by_type_week': pans_by_type_week,
            'total_waffles': total_waffles,
            'total_cost': total_cost,
            'model_type': self.model_type
        } 