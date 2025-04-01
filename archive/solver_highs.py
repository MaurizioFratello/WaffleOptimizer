"""
HiGHS Implementation for Waffle Production Optimization.

This module provides the implementation for the HiGHS solver.
"""
from typing import Dict, List, Any
import time
import numpy as np
import highspy
from solver_interface import SolverInterface

class HighsSolver(SolverInterface):
    """
    Implementation of the SolverInterface using HiGHS.
    """
    
    def __init__(self, time_limit: int = 60, optimality_gap: float = 0.005):
        """
        Initialize the HiGHS solver.
        
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
        self.solver = highspy.Highs()
        
        # Set solver parameters
        self.solver.setOptionValue('time_limit', self.time_limit)
        self.solver.setOptionValue('mip_rel_gap', self.optimality_gap)
        
        # Set objective sense to minimize
        self.solver.changeObjectiveSense(highspy.ObjSense.kMinimize)
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Waffles per waffle type
        allowed = data['allowed']
        cost = data['cost']
        
        # Create variables
        var_idx = 0
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        # Create variable and get its index
                        i = self.solver.addVar(0.0, highspy.kHighsInf, cost.get((w, p), 0) * wpp.get(w, 0))
                        # Store the index
                        self.variables[(w, p, t)] = i
                        var_idx += 1
        
        # All variables are integers - set integrality for all variables
        for i in range(var_idx):
            self.solver.changeColIntegrality(i, highspy.HighsVarType.kInteger)
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        self.constraints['demand'] = {}
        constraint_idx = 0
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    # Collect variables for this constraint
                    var_indices = []
                    var_coeffs = []
                    for p in pan_types:
                        if (w, p, t) in self.variables:
                            var_indices.append(self.variables[(w, p, t)])
                            var_coeffs.append(1.0)
                    
                    if var_indices:
                        # Add constraint: sum(x[w,p,t]) >= demand[w,t]
                        i = self.solver.addRow(float(demand[(w, t)]), highspy.kHighsInf, var_indices, var_coeffs)
                        self.constraints['demand'][(w, t)] = i
                        constraint_idx += 1
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        self.constraints['cumulative_supply'] = {}
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Collect variables for this constraint (all variables using this pan up to this week)
                var_indices = []
                var_coeffs = []
                for earlier_t in [week for week in weeks if week <= t]:
                    for w in waffle_types:
                        if (w, p, earlier_t) in self.variables:
                            var_indices.append(self.variables[(w, p, earlier_t)])
                            var_coeffs.append(1.0)
                
                if var_indices:
                    # Add constraint: sum(x[w,p,t']) <= cumulative_supply
                    i = self.solver.addRow(0.0, float(cumulative_supply), var_indices, var_coeffs)
                    self.constraints['cumulative_supply'][(p, t)] = i
                    constraint_idx += 1
    
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
        self.solver = highspy.Highs()
        
        # Set solver parameters
        self.solver.setOptionValue('time_limit', self.time_limit)
        self.solver.setOptionValue('mip_rel_gap', self.optimality_gap)
        
        # Set objective sense to maximize
        self.solver.changeObjectiveSense(highspy.ObjSense.kMaximize)
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        demand = data['demand']
        supply = data['supply']
        wpp = data['wpp']  # Waffles per waffle type
        allowed = data['allowed']
        
        # Create variables
        var_idx = 0
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        # Create variable and get its index
                        i = self.solver.addVar(0.0, highspy.kHighsInf, wpp.get(w, 0))
                        # Store the index
                        self.variables[(w, p, t)] = i
                        var_idx += 1
        
        # All variables are integers - set integrality for all variables
        for i in range(var_idx):
            self.solver.changeColIntegrality(i, highspy.HighsVarType.kInteger)
        
        # Constraint 1: Demand satisfaction for each waffle type in each week
        self.constraints['demand'] = {}
        constraint_idx = 0
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand:
                    # Collect variables for this constraint
                    var_indices = []
                    var_coeffs = []
                    for p in pan_types:
                        if (w, p, t) in self.variables:
                            var_indices.append(self.variables[(w, p, t)])
                            var_coeffs.append(1.0)
                    
                    if var_indices:
                        if limit_to_demand:
                            # Add constraint: sum(x[w,p,t]) = demand[w,t]
                            i = self.solver.addRow(float(demand[(w, t)]), float(demand[(w, t)]), var_indices, var_coeffs)
                        else:
                            # Add constraint: sum(x[w,p,t]) >= demand[w,t]
                            i = self.solver.addRow(float(demand[(w, t)]), highspy.kHighsInf, var_indices, var_coeffs)
                        self.constraints['demand'][(w, t)] = i
                        constraint_idx += 1
        
        # Constraint 2: Running pan supply - implement cumulative constraints
        self.constraints['cumulative_supply'] = {}
        for p in pan_types:
            cumulative_supply = 0
            for t in weeks:
                # Add the supply for this week to the cumulative total
                if (p, t) in supply:
                    cumulative_supply += supply[(p, t)]
                
                # Collect variables for this constraint (all variables using this pan up to this week)
                var_indices = []
                var_coeffs = []
                for earlier_t in [week for week in weeks if week <= t]:
                    for w in waffle_types:
                        if (w, p, earlier_t) in self.variables:
                            var_indices.append(self.variables[(w, p, earlier_t)])
                            var_coeffs.append(1.0)
                
                if var_indices:
                    # Add constraint: sum(x[w,p,t']) <= cumulative_supply
                    i = self.solver.addRow(0.0, float(cumulative_supply), var_indices, var_coeffs)
                    self.constraints['cumulative_supply'][(p, t)] = i
                    constraint_idx += 1
    
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        if not self.solver:
            raise ValueError("No model has been built. Call build_minimize_cost_model or build_maximize_output_model first.")
            
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        self.solver.run()
        solution_status = self.solver.getModelStatus()
        
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        
        # Map HiGHS status to our status names
        status_map = {
            highspy.HighsModelStatus.kOptimal: 'OPTIMAL',
            highspy.HighsModelStatus.kFeasible: 'FEASIBLE',
            highspy.HighsModelStatus.kInfeasible: 'INFEASIBLE',
            highspy.HighsModelStatus.kUnbounded: 'UNBOUNDED',
            highspy.HighsModelStatus.kUnboundedOrInfeasible: 'UNBOUNDED_OR_INFEASIBLE',
            highspy.HighsModelStatus.kTimeLimit: 'TIME_LIMIT',
            highspy.HighsModelStatus.kNotset: 'NOT_SOLVED'
        }
        
        self.solution_status = status_map.get(solution_status, 'UNKNOWN')
        
        # Get solver statistics
        objective_value = None
        info = self.solver.getInfo()
        best_bound = None
        nodes = None
        gap = None
        wall_time = elapsed_time
        
        if self.solution_status in ['OPTIMAL', 'FEASIBLE', 'TIME_LIMIT']:
            objective_value = self.solver.getObjectiveValue()
            best_bound = info.mip_dual_bound
            nodes = info.mip_node_count
            
            # Calculate optimality gap
            if objective_value is not None and best_bound is not None and abs(objective_value) > 1e-10:
                if self.model_type == 'minimize_cost':
                    # For minimization, the bound is lower than the objective
                    gap = abs(objective_value - best_bound) / abs(objective_value) * 100
                else:
                    # For maximization, the bound is higher than the objective
                    gap = abs(best_bound - objective_value) / abs(objective_value) * 100
        
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
        if not self.solver or self.solution_status not in ['OPTIMAL', 'FEASIBLE', 'TIME_LIMIT']:
            raise ValueError("No feasible solution is available.")
            
        # Extract solution values
        solution = self.solver.getSolution()
        solution_values = {}
        for (w, p, t), var_idx in self.variables.items():
            value = solution[var_idx]
            if value > 0:
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
            'objective_value': self.solver.getObjectiveValue(),
            'solution_values': solution_values,
            'waffles_by_type_week': waffles_by_type_week,
            'pans_by_type_week': pans_by_type_week,
            'total_waffles': total_waffles,
            'total_cost': total_cost,
            'model_type': self.model_type
        } 