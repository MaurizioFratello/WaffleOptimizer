"""
OR-Tools Implementation for Waffle Production Optimization.

This module provides the implementation of SolverInterface using Google OR-Tools.
"""
from typing import Dict, Any
import time
import logging
from ortools.linear_solver import pywraplp
from src.solvers.base import SolverInterface

# Set up logging
logger = logging.getLogger(__name__)

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
        super().__init__()  # Initialize constraint registry
        self.time_limit = time_limit
        self.optimality_gap = optimality_gap
        self.solver = None
        self.variables = {}
        self.objective = None
        self.data = None
        self.model_type = None
        self.solution_status = None
        self.start_time = None
        logger.debug(f"Initialized OR-Tools solver with time_limit={time_limit}, optimality_gap={optimality_gap}")
    
    def apply_constraints(self) -> None:
        """
        Apply all registered constraints to the model.
        """
        if self.solver is None or self.data is None:
            logger.error("Cannot apply constraints: model not built")
            raise ValueError("Model has not been built. Call build_minimize_cost_model or build_maximize_output_model first.")
        
        logger.info("Applying constraints to OR-Tools model")
        # Apply constraints using the constraint registry
        self.constraint_registry.apply_constraints('ortools', self.solver, self.variables, self.data)
        logger.debug("Constraints applied successfully")
    
    def build_minimize_cost_model(self, data: Dict) -> None:
        """
        Build an optimization model to minimize production cost.
        
        Args:
            data: Dictionary containing optimization data
        """
        logger.info("Building cost minimization model")
        self.data = data
        self.model_type = 'minimize_cost'
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        allowed = data['allowed']
        cost = data['cost']
        wpp = data['wpp']  # Waffles per waffle type
        
        logger.debug(f"Model dimensions: {len(waffle_types)} waffle types, {len(pan_types)} pan types, {len(weeks)} weeks")
        
        # Create solver (use CBC by default, but use SCIP if available)
        try:
            self.solver = pywraplp.Solver.CreateSolver('SCIP')
            if self.solver is None:
                logger.debug("SCIP solver not available, falling back to CBC")
                self.solver = pywraplp.Solver.CreateSolver('CBC')
        except Exception as e:
            logger.warning(f"Error creating SCIP solver: {str(e)}, falling back to CBC")
            self.solver = pywraplp.Solver.CreateSolver('CBC')
        
        logger.debug(f"Using solver: {self.solver.SolverVersion()}")
        
        # Create decision variables: x[waffle_type, pan_type, week]
        logger.debug("Creating decision variables")
        self.variables = {}
        var_count = 0
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        var_name = f'x_{w}_{p}_{t}'
                        self.variables[(w, p, t)] = self.solver.IntVar(0, self.solver.infinity(), var_name)
                        var_count += 1
        logger.debug(f"Created {var_count} decision variables")
        
        # Objective function: minimize total cost
        logger.debug("Setting up objective function")
        objective_expr = self.solver.Objective()
        for (w, p, t), var in self.variables.items():
            coeff = cost.get((w, p), 0) * wpp.get(w, 0)
            objective_expr.SetCoefficient(var, coeff)
        objective_expr.SetMinimization()
        self.objective = objective_expr
        logger.debug("Objective function set up complete")
        
        # Apply constraints from constraint registry
        self.apply_constraints()
        logger.info("Cost minimization model built successfully")
    
    def build_maximize_output_model(self, data: Dict, limit_to_demand: bool = False) -> None:
        """
        Build an optimization model to maximize waffle output.
        
        Args:
            data: Dictionary containing optimization data
            limit_to_demand: If True, production will be limited to exactly meet demand
                             If False (default), production can exceed demand
        """
        logger.info("Building output maximization model")
        logger.debug(f"Limit to demand: {limit_to_demand}")
        
        self.data = data
        self.model_type = 'maximize_output'
        
        # Extract data
        waffle_types = data['waffle_types']
        pan_types = data['pan_types']
        weeks = sorted(data['weeks'])  # Sort weeks to ensure chronological order
        allowed = data['allowed']
        wpp = data['wpp']  # Waffles per waffle type
        
        logger.debug(f"Model dimensions: {len(waffle_types)} waffle types, {len(pan_types)} pan types, {len(weeks)} weeks")
        
        # Create solver (use CBC by default, but use SCIP if available)
        try:
            self.solver = pywraplp.Solver.CreateSolver('SCIP')
            if self.solver is None:
                logger.debug("SCIP solver not available, falling back to CBC")
                self.solver = pywraplp.Solver.CreateSolver('CBC')
        except Exception as e:
            logger.warning(f"Error creating SCIP solver: {str(e)}, falling back to CBC")
            self.solver = pywraplp.Solver.CreateSolver('CBC')
        
        logger.debug(f"Using solver: {self.solver.SolverVersion()}")
        
        # Create decision variables: x[waffle_type, pan_type, week]
        logger.debug("Creating decision variables")
        self.variables = {}
        var_count = 0
        for w in waffle_types:
            for p in pan_types:
                for t in weeks:
                    if allowed.get((w, p), False):
                        var_name = f'x_{w}_{p}_{t}'
                        self.variables[(w, p, t)] = self.solver.IntVar(0, self.solver.infinity(), var_name)
                        var_count += 1
        logger.debug(f"Created {var_count} decision variables")
        
        # Objective function: maximize total waffle output
        logger.debug("Setting up objective function")
        objective_expr = self.solver.Objective()
        for (w, p, t), var in self.variables.items():
            objective_expr.SetCoefficient(var, wpp.get(w, 0))
        objective_expr.SetMaximization()
        self.objective = objective_expr
        logger.debug("Objective function set up complete")
        
        # Apply constraints from constraint registry
        self.apply_constraints()
        logger.info("Output maximization model built successfully")
    
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        if self.solver is None:
            logger.error("Cannot solve model: model not built")
            raise ValueError("Model has not been built. Call build_minimize_cost_model or build_maximize_output_model first.")
        
        logger.info(f"Solving {self.model_type} model")
        logger.debug(f"Time limit: {self.time_limit}s, Optimality gap: {self.optimality_gap}")
            
        # Set time limit (in milliseconds)
        self.solver.SetTimeLimit(self.time_limit * 1000)
        
        # Set optimality gap for SCIP solver
        if self.solver.SolverVersion() == "SCIP":
            logger.debug(f"Setting SCIP optimality gap to {self.optimality_gap}")
            self.solver.SetSolverSpecificParametersAsString(f"limits/gap = {self.optimality_gap}")
        
        # Record start time
        self.start_time = time.time()
        
        # Solve the model
        logger.debug("Starting solver")
        status = self.solver.Solve()
        solve_time = time.time() - self.start_time
        
        # Map the status to a human-readable string
        status_map = {
            pywraplp.Solver.OPTIMAL: "OPTIMAL",
            pywraplp.Solver.FEASIBLE: "FEASIBLE",
            pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
            pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
            pywraplp.Solver.ABNORMAL: "ABNORMAL",
            pywraplp.Solver.MODEL_INVALID: "MODEL_INVALID",
            pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED"
        }
        self.solution_status = status_map.get(status, "UNKNOWN")
        
        # Log solution information
        logger.info(f"Solver finished with status: {self.solution_status}")
        logger.debug(f"Solve time: {solve_time:.2f}s")
        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            logger.debug(f"Objective value: {self.objective.Value()}")
        
        # Return solution information
        return {
            "status": self.solution_status,
            "solve_time": solve_time,
            "objective_value": self.objective.Value() if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else None,
            "model_type": self.model_type
        }
    
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        logger.debug("Retrieving solution")
        
        if self.solver is None or self.solution_status not in ["OPTIMAL", "FEASIBLE"]:
            logger.warning(f"Cannot retrieve solution: status is {self.solution_status}")
            return {
                "status": self.solution_status if self.solution_status else "NOT_SOLVED",
                "values": {},
                "objective_value": None,
                "model_type": self.model_type
            }
        
        # Extract solution values
        logger.debug("Extracting non-zero variable values")
        solution_values = {}
        non_zero_count = 0
        for key, var in self.variables.items():
            if var.solution_value() > 0:
                solution_values[key] = var.solution_value()
                non_zero_count += 1
        
        logger.debug(f"Found {non_zero_count} non-zero variables")
        return {
            "status": self.solution_status,
            "values": solution_values,
            "objective_value": self.objective.Value(),
            "model_type": self.model_type
        } 