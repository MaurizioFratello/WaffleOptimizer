"""
Solver Interface Module for Waffle Production Optimization.

This module defines the abstract base class for solver implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

from src.solvers.constraints import Constraint, ConstraintRegistry

# Set up logging
logger = logging.getLogger(__name__)

class SolverInterface(ABC):
    """
    Abstract base class for optimization solvers.
    """
    
    def __init__(self):
        """Initialize solver with empty constraint registry."""
        self.constraint_registry = ConstraintRegistry()
        self.data = None
        self.model_type = None
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def add_constraint(self, name: str, constraint: Constraint) -> None:
        """
        Add a constraint to the solver.
        
        Args:
            name: Name of the constraint
            constraint: Constraint instance
        """
        logger.debug(f"Adding constraint '{name}' to {self.__class__.__name__}")
        self.constraint_registry.register_constraint(name, constraint)
    
    def remove_constraint(self, name: str) -> None:
        """
        Remove a constraint from the solver.
        
        Args:
            name: Name of the constraint to remove
        """
        logger.debug(f"Removing constraint '{name}' from {self.__class__.__name__}")
        self.constraint_registry.unregister_constraint(name)
    
    def get_constraint(self, name: str) -> Optional[Constraint]:
        """
        Get a constraint by name.
        
        Args:
            name: Name of the constraint
            
        Returns:
            Optional[Constraint]: The constraint instance, or None if not found
        """
        constraint = self.constraint_registry.get_constraint(name)
        if constraint is None:
            logger.debug(f"Constraint '{name}' not found in {self.__class__.__name__}")
        return constraint
    
    def get_all_constraints(self) -> Dict[str, Constraint]:
        """
        Get all constraints registered with this solver.
        
        Returns:
            Dict[str, Constraint]: Dictionary of all registered constraints
        """
        constraints = self.constraint_registry.get_all_constraints()
        logger.debug(f"Retrieved {len(constraints)} constraints from {self.__class__.__name__}")
        return constraints
    
    @abstractmethod
    def apply_constraints(self) -> None:
        """
        Apply all registered constraints to the model.
        """
        logger.info(f"Applying constraints to {self.__class__.__name__}")
        constraints = self.get_all_constraints()
        logger.debug(f"Found {len(constraints)} constraints to apply")
        
        for name, constraint in constraints.items():
            logger.debug(f"Validating data for constraint '{name}'")
            if not constraint.validate_data(self.data):
                logger.error(f"Data validation failed for constraint '{name}'")
                raise ValueError(f"Invalid data for constraint '{name}'")
            logger.debug(f"Applying constraint '{name}' to model")
    
    @abstractmethod
    def build_minimize_cost_model(self, data: Dict) -> None:
        """
        Build an optimization model to minimize production cost.
        
        Args:
            data: Dictionary containing optimization data
        """
        logger.info("Building cost minimization model")
        logger.debug(f"Input data summary: {len(data['waffle_types'])} waffle types, "
                    f"{len(data['pan_types'])} pan types, {len(data['weeks'])} weeks")
        self.data = data
        self.model_type = 'minimize_cost'
    
    @abstractmethod
    def build_maximize_output_model(self, data: Dict) -> None:
        """
        Build an optimization model to maximize waffle output.
        
        Args:
            data: Dictionary containing optimization data
        """
        logger.info("Building output maximization model")
        logger.debug(f"Input data summary: {len(data['waffle_types'])} waffle types, "
                    f"{len(data['pan_types'])} pan types, {len(data['weeks'])} weeks")
        self.data = data
        self.model_type = 'maximize_output'
    
    @abstractmethod
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        logger.info(f"Solving {self.model_type} model")
    
    @abstractmethod
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        logger.debug("Retrieving solution")


class SolverFactory:
    """
    Factory class for creating solver instances.
    """
    
    @staticmethod
    def create_solver(solver_name: str, constraints: Dict[str, Constraint] = None, **kwargs) -> SolverInterface:
        """
        Create a solver instance based on the solver name.
        
        Args:
            solver_name: Name of the solver
            constraints: Dictionary mapping constraint names to constraint instances
            **kwargs: Additional arguments for the solver
            
        Returns:
            SolverInterface: An instance of the requested solver
            
        Raises:
            ValueError: If the solver is not supported
        """
        from src.solvers.ortools_solver import ORToolsSolver
        from src.solvers.pulp_solver import PulpSolver
        
        solvers = {
            'ortools': ORToolsSolver,
            'cbc': lambda **kwargs: PulpSolver(solver_name='CBC', **kwargs),
            'glpk': lambda **kwargs: PulpSolver(solver_name='GLPK', **kwargs),
            'scip': lambda **kwargs: PulpSolver(solver_name='SCIP', **kwargs),
            'coin_cmd': lambda **kwargs: PulpSolver(solver_name='COIN_CMD', **kwargs),
            # Additional solvers can be added here
        }
        
        if solver_name.lower() not in solvers:
            raise ValueError(f"Solver '{solver_name}' is not supported.")
            
        solver = solvers[solver_name.lower()](**kwargs)
        
        # Add constraints if provided
        if constraints:
            for name, constraint in constraints.items():
                solver.add_constraint(name, constraint)
                
        return solver 