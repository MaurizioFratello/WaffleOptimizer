"""
Tests for the SolverFactory class.
"""
import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.solvers.base import SolverFactory, SolverInterface
from src.solvers.pulp_solver import PulpSolver
from src.solvers.ortools_solver import ORToolsSolver

class TestSolverFactory(unittest.TestCase):
    """
    Test cases for the SolverFactory class.
    """
    
    def test_create_cbc_solver(self):
        """Test creating a CBC solver."""
        solver = SolverFactory.create_solver('cbc')
        self.assertIsInstance(solver, PulpSolver)
        self.assertEqual(solver.solver_name, 'CBC')
    
    def test_create_glpk_solver(self):
        """Test creating a GLPK solver."""
        solver = SolverFactory.create_solver('glpk')
        self.assertIsInstance(solver, PulpSolver)
        self.assertEqual(solver.solver_name, 'GLPK')
    
    def test_create_ortools_solver(self):
        """Test creating an OR-Tools solver."""
        solver = SolverFactory.create_solver('ortools')
        self.assertIsInstance(solver, ORToolsSolver)
    
    def test_create_invalid_solver(self):
        """Test creating an invalid solver."""
        with self.assertRaises(ValueError):
            SolverFactory.create_solver('invalid_solver')
    
    def test_solver_interface(self):
        """Test that all created solvers implement the SolverInterface."""
        available_solvers = ['cbc', 'glpk', 'ortools', 'scip', 'coin_cmd']
        
        for solver_name in available_solvers:
            solver = SolverFactory.create_solver(solver_name)
            self.assertIsInstance(solver, SolverInterface)
    
    def test_solver_with_parameters(self):
        """Test creating a solver with parameters."""
        time_limit = 120
        optimality_gap = 0.01
        solver = SolverFactory.create_solver('cbc', time_limit=time_limit, optimality_gap=optimality_gap)
        self.assertEqual(solver.time_limit, time_limit)
        self.assertEqual(solver.optimality_gap, optimality_gap)

if __name__ == '__main__':
    unittest.main() 