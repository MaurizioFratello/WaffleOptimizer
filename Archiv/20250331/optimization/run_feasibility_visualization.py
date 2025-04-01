"""
Run Feasibility Visualization with Actual Data

This script loads the actual Excel data files and runs the feasibility visualization
using the FeasibilityVisualizer.
"""
import os
from data_processor import DataProcessor
from feasibility_check import FeasibilityChecker
from visualize_feasibility import FeasibilityVisualizer

def main():
    # Define the Excel file paths
    demand_file = "WaffleDemand.xlsx"
    supply_file = "PanSupply.xlsx"
    cost_file = "WaffleCostPerPan.xlsx"
    wpp_file = "WafflesPerPan.xlsx"
    combinations_file = "WafflePanCombinations.xlsx"
    
    # Check if files exist
    for file in [demand_file, supply_file, cost_file, wpp_file, combinations_file]:
        if not os.path.exists(file):
            print(f"Error: {file} not found. Please ensure the file exists in the current directory.")
            return
    
    print("Loading data from Excel files...")
    
    # Load and process data
    data_processor = DataProcessor()
    data_processor.load_data(
        demand_file, supply_file, cost_file, wpp_file, combinations_file
    )
    
    # Get data for feasibility check
    print("Getting feasibility data...")
    feasibility_data = data_processor.get_feasibility_data()
    
    # Run feasibility check
    print("Running feasibility check...")
    checker = FeasibilityChecker(feasibility_data)
    is_feasible = checker.check_feasibility()
    
    # Print the text report
    checker.print_report()
    
    # Create and run the visualizer
    print("Generating visualizations...")
    visualizer = FeasibilityVisualizer(checker)
    visualizer.visualize_results("feasibility_visualizations.png")
    
    # Generate HTML report
    visualizer.save_visualizations_to_html("feasibility_analysis.html")
    
    # Generate and display the supply-demand table
    table = visualizer.generate_supply_demand_table()
    print("\nSupply-Demand Table:")
    print(table)
    
    print("\nVisualization process completed!")
    print("- Visualizations shown and saved to feasibility_visualizations.png")
    print("- HTML report saved to feasibility_analysis.html")


if __name__ == "__main__":
    main() 