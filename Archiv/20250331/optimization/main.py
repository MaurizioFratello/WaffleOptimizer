"""
Main Interactive Interface for Waffle Production Optimization.

This module provides an interactive command-line interface for the
waffle production optimization tool.
"""
import os
import sys
import matplotlib.pyplot as plt
from typing import Dict, List, Any

from data_processor import DataProcessor
from feasibility_check import FeasibilityChecker
from solver_interface import SolverFactory
from results_reporter import ResultsReporter


class WaffleOptimizer:
    """
    Main class for the Waffle Production Optimization tool.
    """
    
    def __init__(self):
        """Initialize the WaffleOptimizer."""
        self.data_processor = DataProcessor()
        self.solver = None
        self.solution = None
        self.reporter = None
        
    def load_data(self, 
                  demand_file: str, 
                  supply_file: str, 
                  cost_file: str, 
                  wpp_file: str, 
                  combinations_file: str) -> None:
        """
        Load data from Excel files.
        
        Args:
            demand_file: Path to waffle demand Excel file
            supply_file: Path to pan supply Excel file
            cost_file: Path to waffle cost Excel file
            wpp_file: Path to waffles per pan Excel file
            combinations_file: Path to allowed combinations Excel file
        """
        print("Loading data...")
        self.data_processor.load_data(
            demand_file, supply_file, cost_file, wpp_file, combinations_file
        )
        print("Data loaded successfully.")
        
    def check_feasibility(self) -> Dict:
        """
        Check the feasibility of the optimization problem.
        
        Returns:
            Dict: Dictionary containing feasibility check results
        """
        print("\nChecking feasibility...")
        data = self.data_processor.get_feasibility_data()
        checker = FeasibilityChecker(data)
        is_feasible = checker.check_feasibility()
        checker.print_report()
        
        return checker.get_result_summary()
    
    def optimize(self, objective: str, solver_name: str = 'ortools', time_limit: int = 60, limit_to_demand: bool = False) -> Dict:
        """
        Solve the optimization problem.
        
        Args:
            objective: Objective function, either 'minimize_cost' or 'maximize_output'
            solver_name: Name of the solver to use
            time_limit: Time limit for solving the model in seconds
            limit_to_demand: If True and objective is 'maximize_output', production will be
                            limited to exactly meet demand
            
        Returns:
            Dict: Dictionary containing solution information
        """
        # Validate objective
        if objective not in ['minimize_cost', 'maximize_output']:
            raise ValueError("Objective must be either 'minimize_cost' or 'maximize_output'.")
        
        print(f"\nSolving with objective: {objective}")
        print(f"Using solver: {solver_name}")
        
        if objective == 'maximize_output':
            print(f"Limit production to demand: {limit_to_demand}")
        
        # Get optimization data
        data = self.data_processor.get_optimization_data()
        
        # Create solver
        self.solver = SolverFactory.create_solver(solver_name, time_limit=time_limit)
        
        # Build and solve model
        if objective == 'minimize_cost':
            self.solver.build_minimize_cost_model(data)
        else:  # maximize_output
            self.solver.build_maximize_output_model(data, limit_to_demand=limit_to_demand)
            
        result = self.solver.solve_model()
        print(f"Solution status: {result['status']}")
        print(f"Solve time: {result['wall_time']:.2f} seconds")
        
        if result['status'] in ['OPTIMAL', 'FEASIBLE']:
            self.solution = self.solver.get_solution()
            self.reporter = ResultsReporter(self.solution, data)
            self.reporter.print_summary()
        
        return result
    
    def visualize_results(self) -> None:
        """Visualize the optimization results using matplotlib."""
        if not self.reporter:
            raise ValueError("No solution available to visualize.")
            
        print("\nGenerating visualizations...")
        
        # Waffle production over time
        fig1 = self.reporter.plot_waffle_production()
        plt.figure(fig1.number)
        plt.show()
        
        # Pan usage over time
        fig2 = self.reporter.plot_pan_usage()
        plt.figure(fig2.number)
        plt.show()
        
        # Supply vs. demand comparison
        fig3 = self.reporter.plot_supply_demand_comparison()
        plt.figure(fig3.number)
        plt.show()
    
    def export_solution(self, filename: str) -> None:
        """
        Export the solution to an Excel file.
        
        Args:
            filename: Name of the Excel file to create
        """
        if not self.reporter:
            raise ValueError("No solution available to export.")
            
        print(f"\nExporting solution to {filename}...")
        self.reporter.export_solution(filename)
        print("Solution exported successfully.")


def main():
    """Main function for interactive command-line interface."""
    print("=== Waffle Production Optimization ===")
    print("This tool helps optimize waffle production planning.")
    
    optimizer = WaffleOptimizer()
    
    # Data loading
    print("\nStep 1: Load data from Excel files")
    demand_file = input("Enter path to waffle demand file (default: WaffleDemand.xlsx): ") or "WaffleDemand.xlsx"
    supply_file = input("Enter path to pan supply file (default: PanSupply.xlsx): ") or "PanSupply.xlsx"
    cost_file = input("Enter path to waffle cost file (default: WaffleCostPerPan.xlsx): ") or "WaffleCostPerPan.xlsx"
    wpp_file = input("Enter path to waffles per pan file (default: WafflesPerPan.xlsx): ") or "WafflesPerPan.xlsx"
    combinations_file = input("Enter path to allowed combinations file (default: WafflePanCombinations.xlsx): ") or "WafflePanCombinations.xlsx"
    
    try:
        optimizer.load_data(demand_file, supply_file, cost_file, wpp_file, combinations_file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Feasibility check
    print("\nStep 2: Check feasibility")
    try:
        feasibility_result = optimizer.check_feasibility()
        if not feasibility_result['is_feasible']:
            print("\nWarning: The problem may be infeasible. Do you want to continue anyway?")
            continue_anyway = input("Continue anyway? (y/n): ").lower() == 'y'
            if not continue_anyway:
                return
    except Exception as e:
        print(f"Error checking feasibility: {e}")
        return
    
    # Optimization
    print("\nStep 3: Solve optimization problem")
    print("Available objectives:")
    print("1. Minimize production cost")
    print("2. Maximize waffle output")
    objective_choice = input("Choose objective (1/2): ")
    
    objective = "minimize_cost" if objective_choice == "1" else "maximize_output"
    
    limit_to_demand = False
    if objective == "maximize_output":
        limit_choice = input("Limit production to exactly meet demand? (y/n): ").lower()
        limit_to_demand = limit_choice == 'y'
    
    print("\nAvailable solvers:")
    print("1. OR-Tools (default)")
    # Add more solvers as they are implemented
    solver_choice = input("Choose solver (1): ") or "1"
    
    solver_map = {
        "1": "ortools",
        # Add more solvers as they are implemented
    }
    solver_name = solver_map.get(solver_choice, "ortools")
    
    time_limit = int(input("Enter time limit in seconds (default: 60): ") or "60")
    
    try:
        result = optimizer.optimize(objective, solver_name, time_limit, limit_to_demand)
        if result['status'] not in ['OPTIMAL', 'FEASIBLE']:
            print("No feasible solution found.")
            return
    except Exception as e:
        print(f"Error solving optimization problem: {e}")
        return
    
    # Visualization
    print("\nStep 4: Visualize results")
    visualize = input("Visualize results? (y/n): ").lower() == 'y'
    if visualize:
        try:
            optimizer.visualize_results()
        except Exception as e:
            print(f"Error visualizing results: {e}")
    
    # Export solution
    print("\nStep 5: Export solution")
    export = input("Export solution to Excel? (y/n): ").lower() == 'y'
    if export:
        export_file = input("Enter export filename (default: waffle_solution.xlsx): ") or "waffle_solution.xlsx"
        try:
            optimizer.export_solution(export_file)
        except Exception as e:
            print(f"Error exporting solution: {e}")


if __name__ == "__main__":
    main()
