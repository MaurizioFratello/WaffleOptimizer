"""
OR-Tools Implementation for Waffle Production Optimization.

This module provides the implementation of SolverInterface using Google OR-Tools.
"""
from typing import Dict, Any
import time
from ortools.linear_solver import pywraplp
from src.solvers.base import SolverInterface

class ORToolsSolver(SolverInterface):
    """
    Implementation of the SolverInterface using Google OR-Tools.
    """
    
    def __init__(self, time_limit: int = 60, optimality_gap: float = 0.005):
        """
        Initialize the OR-Tools solver.
        
        Args:
            time_limit: Time limit for solving the model in seconds
            optimality_gap: Maximum allowed optimality gap (default: 0.5%)
        """
        self.time_limit = time_limit
        self.optimality_gap = optimality_gap
        self.solver = None
        self.variables = {}
        self.objective = None
        self.data = None
        self.model_type = None
        self.solution_status = None
        self.start_time = None
    
    def build_minimize_cost_model(self, data: Dict) -> None:
        """
        Build an optimization model to minimize production cost.
        
        Args:
            data: Dictionary containing optimization data
        """
        self.data = data
        self.model_type = 'minimize_cost'
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Waffles per waffle type
        allowed = data['allowed']
        cost = data['cost']
        
        # Create solver (use CBC by default, but use SCIP if available)
        try:
            self.solver = pywraplp.Solver.CreateSolver('SCIP')
            if self.solver is None:
                self.solver = pywraplp.Solver.CreateSolver('CBC')
        except:
            self.solver = pywraplp.Solver.CreateSolver('CBC')
        
        # Time limit and optimality gap are now set in solve_model()
        
        # Create decision variables: x[waffle_type, pan_type, week]
        # Represents the number of pans of type pan_type used to cook waffle_type in week
        self.variables = {}
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        var_name = f'x_{w}_{p}_{t}'
                        self.variables[(w, p, t)] = self.solver.IntVar(0, self.solver.infinity(), var_name)
        
        # Objective function: minimize total cost
        # Cost is calculated as: (number of pans) * (waffles per pan) * (cost per waffle)
        objective_expr = self.solver.Objective()
        for (w, p, t), var in self.variables.items():
            objective_expr.SetCoefficient(var, cost.get((w, p), 0) * wpp.get(w, 0))
        objective_expr.SetMinimization()
        self.objective = objective_expr
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        # Using equality constraint (==) to use exactly the demanded number of pans
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    constraint = self.solver.Constraint(demand[(w, t)], demand[(w, t)])
                    for p in pan_types:
                        if (w, p, t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, t)], 1)
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        # This allows unused pans from earlier weeks to be used in later weeks
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Create a constraint: cumulative usage <= cumulative supply
                constraint = self.solver.Constraint(-self.solver.infinity(), cumulative_supply)
                for w in waffle_types:
                    for earlier_t in [week for week in weeks if week <= t]:
                        if (w, p, earlier_t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, earlier_t)], 1)
    
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
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Waffles per waffle type
        allowed = data['allowed']
        
        # Create solver (use CBC by default, but use SCIP if available)
        try:
            self.solver = pywraplp.Solver.CreateSolver('SCIP')
            if self.solver is None:
                self.solver = pywraplp.Solver.CreateSolver('CBC')
        except:
            self.solver = pywraplp.Solver.CreateSolver('CBC')
        
        # Time limit and optimality gap are now set in solve_model()
        
        # Create decision variables: x[waffle_type, pan_type, week]
        # Represents the number of pans of type pan_type used to cook waffle_type in week
        self.variables = {}
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        var_name = f'x_{w}_{p}_{t}'
                        self.variables[(w, p, t)] = self.solver.IntVar(0, self.solver.infinity(), var_name)
        
        # Objective function: maximize total waffle output
        objective_expr = self.solver.Objective()
        for (w, p, t), var in self.variables.items():
            objective_expr.SetCoefficient(var, wpp.get(w, 0))
        objective_expr.SetMaximization()
        self.objective = objective_expr
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        # For maximizing output, we always use equality constraints to ensure we use exactly
        # the number of pans demanded (not more or less)
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    # Equality constraint (exactly meet demand)
                    constraint = self.solver.Constraint(demand[(w, t)], demand[(w, t)])
                        
                    for p in pan_types:
                        if (w, p, t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, t)], 1)
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        # This allows unused pans from earlier weeks to be used in later weeks
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Create a constraint: cumulative usage <= cumulative supply
                constraint = self.solver.Constraint(-self.solver.infinity(), cumulative_supply)
                for w in waffle_types:
                    for earlier_t in [week for week in weeks if week <= t]:
                        if (w, p, earlier_t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, earlier_t)], 1)
    
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        if self.solver is None:
            raise ValueError("Model has not been built. Call build_minimize_cost_model or build_maximize_output_model first.")
            
        # Set time limit (in milliseconds)
        self.solver.SetTimeLimit(self.time_limit * 1000)
        
        # Set optimality gap for SCIP solver
        if self.solver.SolverVersion() == "SCIP":
            self.solver.SetSolverSpecificParametersAsString(f"limits/gap = {self.optimality_gap}")
        elif self.solver.SolverVersion() == "CBC_MIXED_INTEGER_PROGRAMMING":
            # For CBC, set relative gap tolerance
            self.solver.SetSolverSpecificParametersAsString(f"ratioGap {self.optimality_gap}")
        
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        status = self.solver.Solve()
        
        # Calculate solution time
        solution_time = time.time() - self.start_time
        
        # Get solution status
        status_map = {
            pywraplp.Solver.OPTIMAL: "Optimal",
            pywraplp.Solver.FEASIBLE: "Feasible",
            pywraplp.Solver.INFEASIBLE: "Infeasible",
            pywraplp.Solver.UNBOUNDED: "Unbounded",
            pywraplp.Solver.ABNORMAL: "Abnormal",
            pywraplp.Solver.NOT_SOLVED: "NotSolved",
            pywraplp.Solver.MODEL_INVALID: "ModelInvalid"
        }
        
        status_str = status_map.get(status, f"Unknown ({status})")
        self.solution_status = status_str
        
        # Check if the solution is optimal or feasible
        is_optimal = status == pywraplp.Solver.OPTIMAL
        is_feasible = is_optimal or status == pywraplp.Solver.FEASIBLE
        
        # Get the objective value if the problem is feasible
        objective_value = None
        if is_feasible:
            objective_value = self.solver.Objective().Value()
        
        # Get best bound and calculate optimality gap
        best_bound = None
        gap = 0.0  # Default to 0
        
        if is_feasible:
            try:
                best_bound = self.solver.Objective().BestBound()
                if best_bound is not None and abs(objective_value) > 1e-10:
                    if self.model_type == 'minimize_cost':
                        # For minimization, bound is lower than objective
                        gap = abs(objective_value - best_bound) / abs(objective_value)
                    else:
                        # For maximization, bound is higher than objective
                        gap = abs(best_bound - objective_value) / abs(objective_value)
            except:
                # Some solvers might not support BestBound
                pass
        
        # Prepare solution information
        solution_info = {
            'status': status_str,
            'is_optimal': is_optimal,
            'is_feasible': is_feasible,
            'objective_value': objective_value,
            'solution_time': solution_time,
            'solver_name': 'OR-Tools',
            'best_bound': best_bound,
            'gap': gap
        }
        
        return solution_info
    
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        if self.solver is None or self.solution_status is None:
            raise ValueError("Model has not been solved. Call solve_model first.")
            
        # Check if the solution is feasible
        if self.solution_status not in ["Optimal", "Feasible"]:
            raise ValueError(f"Cannot get solution: problem status is '{self.solution_status}'")
        
        # Extract solution variables and their values
        solution_variables = {}
        for var_key, var in self.variables.items():
            value = var.solution_value()
            # Only include non-zero values to keep the solution compact
            if value is not None and abs(value) > 1e-6:
                solution_variables[var_key] = int(round(value))  # Round to nearest integer
        
        # Get the objective value
        objective_value = self.solver.Objective().Value()
        
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