"""
OR-Tools Implementation for Waffle Production Optimization.

This module provides the implementation for the Google OR-Tools solver.
"""
from typing import Dict, List, Any
from ortools.linear_solver import pywraplp
from solver_interface import SolverInterface
import time

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
        self.constraints = {}
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
        
        # Create solver instance
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            raise ValueError("Could not create SCIP solver")
            
        # Set time limit
        self.solver.set_time_limit(self.time_limit * 1000)  # Convert to milliseconds
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Now this is waffles per waffle type, not per pan
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
                        self.variables[(w, p, t)] = self.solver.IntVar(0, self.solver.infinity(), var_name)
        
        # Objective function: minimize total cost
        self.objective = self.solver.Objective()
        self.objective.SetMinimization()
        
        for (w, p, t), var in self.variables.items():
            waffle_cost = cost.get((w, p), 0)
            # Use waffles per waffle type (not per pan)
            waffle_wpp = wpp.get(w, 0)
            # Set coefficient directly
            self.objective.SetCoefficient(var, waffle_cost * waffle_wpp)
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        self.constraints['demand'] = {}
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    constraint = self.solver.Constraint(demand[(w, t)], self.solver.infinity())
                    for p in pan_types:
                        if (w, p, t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, t)], 1)
                    self.constraints['demand'][(w, t)] = constraint
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        # This allows unused pans from earlier weeks to be used in later weeks
        self.constraints['cumulative_supply'] = {}
        
        # For each pan type, create cumulative supply constraints for each week
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Create a constraint: cumulative usage <= cumulative supply
                constraint = self.solver.Constraint(0, cumulative_supply)
                
                # Add all variables for this pan type up to and including the current week
                for earlier_t in [week for week in weeks if week <= t]:
                    for w in waffle_types:
                        if (w, p, earlier_t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, earlier_t)], 1)
                
                self.constraints['cumulative_supply'][(p, t)] = constraint
    
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
        
        # Create solver instance
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            raise ValueError("Could not create SCIP solver")
            
        # Set time limit
        self.solver.set_time_limit(self.time_limit * 1000)  # Convert to milliseconds
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Now this is waffles per waffle type, not per pan
        allowed = data['allowed']
        
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
        self.objective = self.solver.Objective()
        self.objective.SetMaximization()
        
        for (w, p, t), var in self.variables.items():
            # Use waffles per waffle type (not per pan)
            waffle_wpp = wpp.get(w, 0)
            # Set coefficient directly
            self.objective.SetCoefficient(var, waffle_wpp)
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        self.constraints['demand'] = {}
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    if limit_to_demand:
                        # Limit production to exactly meet demand (equality constraint)
                        constraint = self.solver.Constraint(demand[(w, t)], demand[(w, t)])
                    else:
                        # Allow production to exceed demand (lower bound constraint)
                        constraint = self.solver.Constraint(demand[(w, t)], self.solver.infinity())
                    
                    for p in pan_types:
                        if (w, p, t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, t)], 1)
                    self.constraints['demand'][(w, t)] = constraint
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        # This allows unused pans from earlier weeks to be used in later weeks
        self.constraints['cumulative_supply'] = {}
        
        # For each pan type, create cumulative supply constraints for each week
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Create a constraint: cumulative usage <= cumulative supply
                constraint = self.solver.Constraint(0, cumulative_supply)
                
                # Add all variables for this pan type up to and including the current week
                for earlier_t in [week for week in weeks if week <= t]:
                    for w in waffle_types:
                        if (w, p, earlier_t) in self.variables:
                            constraint.SetCoefficient(self.variables[(w, p, earlier_t)], 1)
                
                self.constraints['cumulative_supply'][(p, t)] = constraint
    
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        if not self.solver:
            raise ValueError("No model has been built. Call build_minimize_cost_model or build_maximize_output_model first.")
            
        # Set solver parameters
        self.solver.set_time_limit(self.time_limit * 1000)  # Convert to milliseconds
        
        # Set optimality gap for SCIP solver
        if isinstance(self.solver, pywraplp.Solver) and self.solver.SolverVersion() == "SCIP":
            self.solver.SetSolverSpecificParametersAsString(f"limits/gap = {self.optimality_gap}")
        
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        status = self.solver.Solve()
        
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        
        status_map = {
            pywraplp.Solver.OPTIMAL: 'OPTIMAL',
            pywraplp.Solver.FEASIBLE: 'FEASIBLE',
            pywraplp.Solver.INFEASIBLE: 'INFEASIBLE',
            pywraplp.Solver.UNBOUNDED: 'UNBOUNDED',
            pywraplp.Solver.ABNORMAL: 'ABNORMAL',
            pywraplp.Solver.NOT_SOLVED: 'NOT_SOLVED'
        }
        
        self.solution_status = status_map.get(status, 'UNKNOWN')
        
        # Get solver statistics
        objective_value = self.objective.Value() if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else None
        wall_time = self.solver.wall_time() / 1000  # Convert to seconds
        nodes = self.solver.nodes() if hasattr(self.solver, 'nodes') else None
        best_bound = self.solver.Objective().BestBound() if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else None
        
        # Calculate optimality gap
        gap = None
        if objective_value is not None and best_bound is not None and abs(objective_value) > 1e-10:
            gap = abs(objective_value - best_bound) / abs(objective_value) * 100
        
        # Print progress information
        print(f"\nSolver Progress:")
        print(f"Status: {self.solution_status}")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")
        if objective_value is not None:
            print(f"Objective Value: {objective_value:.2f}")
        if gap is not None:
            print(f"Optimality Gap: {gap:.2f}%")
        if nodes is not None:
            print(f"Nodes Explored: {nodes}")
        
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
        if not self.solver or self.solution_status not in ['OPTIMAL', 'FEASIBLE']:
            raise ValueError("No feasible solution is available.")
            
        # Extract solution values
        solution_values = {}
        for (w, p, t), var in self.variables.items():
            if var.solution_value() > 0:
                solution_values[(w, p, t)] = var.solution_value()
        
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
            'objective_value': self.objective.Value(),
            'solution_values': solution_values,
            'waffles_by_type_week': waffles_by_type_week,
            'pans_by_type_week': pans_by_type_week,
            'total_waffles': total_waffles,
            'total_cost': total_cost,
            'model_type': self.model_type
        }
