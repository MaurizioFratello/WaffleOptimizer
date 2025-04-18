"""
Solver Interface Module for Waffle Production Optimization.

This module defines the abstract base class for solver implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class SolverInterface(ABC):
    """
    Abstract base class for optimization solvers.
    """
    
    @abstractmethod
    def build_minimize_cost_model(self, data: Dict) -> None:
        """
        Build an optimization model to minimize production cost.
        
        Args:
            data: Dictionary containing optimization data
        """
        pass
    
    @abstractmethod
    def build_maximize_output_model(self, data: Dict, limit_to_demand: bool = False) -> None:
        """
        Build an optimization model to maximize waffle output.
        
        Args:
            data: Dictionary containing optimization data
            limit_to_demand: If True, production will be limited to exactly meet demand
                             If False (default), production can exceed demand
        """
        pass
    
    @abstractmethod
    def solve_model(self) -> Dict:
        """
        Solve the current optimization model.
        
        Returns:
            Dict: Dictionary containing solution information
        """
        pass
    
    @abstractmethod
    def get_solution(self) -> Dict:
        """
        Get the solution of the optimization model.
        
        Returns:
            Dict: Dictionary containing the solution variables and objective value
        """
        pass


class SolverFactory:
    """
    Factory class for creating solver instances.
    """
    
    @staticmethod
    def create_solver(solver_name: str, **kwargs) -> SolverInterface:
        """
        Create a solver instance based on the solver name.
        
        Args:
            solver_name: Name of the solver
            **kwargs: Additional arguments for the solver
            
        Returns:
            SolverInterface: An instance of the requested solver
            
        Raises:
            ValueError: If the solver is not supported
        """
        from solver_ortools import ORToolsSolver
        
        solvers = {
            'ortools': ORToolsSolver,
            # Additional solvers can be added here
        }
        
        if solver_name.lower() not in solvers:
            raise ValueError(f"Solver '{solver_name}' is not supported.")
            
        return solvers[solver_name.lower()](**kwargs)
