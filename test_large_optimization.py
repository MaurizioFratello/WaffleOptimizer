"""
Test script to run an optimization with a large dataset.
This will test the time limit and optimality gap functionality.
"""
import os
import time
import pandas as pd
import numpy as np
from src.solvers.base import SolverFactory

def generate_even_more_complex_data():
    """Generate a very complex dataset to ensure the solver hits the time limit."""
    np.random.seed(42)  # Set seed for reproducibility
    
    num_waffle_types = 200
    num_pan_types = 40
    num_weeks = 50
    
    # Generate waffle types and pan types
    waffle_types = [f"Waffle_{i+1}" for i in range(num_waffle_types)]
    pan_types = [f"Pan_{i+1}" for i in range(num_pan_types)]
    weeks = [f"Week_{i+1}" for i in range(num_weeks)]
    
    # Generate complex demand data (make it sparse)
    demand = {}
    for waffle in waffle_types:
        # Each waffle has demand in approximately 20% of weeks (reduced to make it more feasible)
        for week in weeks:
            if np.random.random() < 0.2:
                # Random demand between 10 and 200 (reduced to make it more feasible)
                demand[(waffle, week)] = np.random.randint(10, 200)
    
    # Generate supply data with very high initial supply
    supply = {}
    for pan in pan_types:
        # Initial very large supply in first week to ensure feasibility
        supply[(pan, weeks[0])] = np.random.randint(10000, 20000)
        
        # Occasional replenishments in other weeks
        for week_idx, week in enumerate(weeks[1:], 1):
            if week_idx % 5 == 0 and np.random.random() < 0.3:
                supply[(pan, week)] = np.random.randint(500, 1000)
    
    # Generate waffles per pan data
    wpp = {}
    for waffle in waffle_types:
        wpp[waffle] = np.random.randint(100, 1000)
    
    # Generate cost data (make it complex with good and bad options)
    cost = {}
    for waffle in waffle_types:
        for pan in pan_types:
            # Base cost between 0.01 and 10.0
            base_cost = np.random.uniform(0.01, 10.0)
            # Add different cost scales for different pans to make the optimization harder
            if pan.endswith('1') or pan.endswith('3') or pan.endswith('5'):
                # These pans are more expensive
                cost[(waffle, pan)] = base_cost * np.random.uniform(1.5, 3.0)
            else:
                cost[(waffle, pan)] = base_cost * np.random.uniform(0.8, 1.2)
    
    # Generate allowed combinations (less sparse matrix)
    allowed = {}
    for waffle in waffle_types:
        # Each waffle can be made in 35% of pans (increased to improve feasibility)
        allowed_pans = np.random.choice(pan_types, size=int(0.35 * num_pan_types), replace=False)
        for pan in allowed_pans:
            allowed[(waffle, pan)] = True
        
        # Ensure at least one allowed pan for each waffle
        if not any(allowed.get((waffle, p), False) for p in pan_types):
            allowed[(waffle, pan_types[0])] = True
    
    # Compile optimization data
    optimization_data = {
        'waffle_types': waffle_types,
        'pan_types': pan_types,
        'weeks': weeks,
        'demand': demand,
        'supply': supply,
        'wpp': wpp,
        'cost': cost,
        'allowed': allowed
    }
    
    return optimization_data

def load_excel_data(demand_file, supply_file, cost_file, wpp_file, combinations_file, supply_multiplier=10):
    """
    Load data from Excel files and format it for optimization.
    
    Args:
        demand_file: Path to demand file
        supply_file: Path to supply file
        cost_file: Path to cost file
        wpp_file: Path to waffles per pan file
        combinations_file: Path to combinations file
        supply_multiplier: Multiplier to increase supply (helps make model feasible)
    """
    # Load raw data
    demand_df = pd.read_excel(demand_file)
    supply_df = pd.read_excel(supply_file)
    cost_df = pd.read_excel(cost_file)
    wpp_df = pd.read_excel(wpp_file)
    combinations_df = pd.read_excel(combinations_file)
    
    # Extract and process data
    waffle_types = demand_df['Waffle Type'].tolist()
    pan_types = supply_df['Pan Type'].tolist()
    
    # Extract weeks from column names
    weeks = [col for col in demand_df.columns if col.startswith('Week_')]
    
    # Process demand data
    demand = {}
    for _, row in demand_df.iterrows():
        waffle = row['Waffle Type']
        for week in weeks:
            if pd.notna(row[week]) and row[week] > 0:  # Only include non-zero demand
                demand[(waffle, week)] = int(row[week])
    
    # Process supply data with multiplier to ensure feasibility
    supply = {}
    for _, row in supply_df.iterrows():
        pan = row['Pan Type']
        for week in weeks:
            if pd.notna(row[week]) and row[week] > 0:  # Only include non-zero supply
                # Multiply supply by the multiplier to ensure feasibility
                supply[(pan, week)] = int(row[week] * supply_multiplier)
    
    # Process waffles per pan data
    wpp = {}
    for _, row in wpp_df.iterrows():
        wpp[row['Waffle Type']] = int(row['WPP'])
    
    # Process cost data (pan-specific cost per waffle)
    cost = {}
    for _, row in cost_df.iterrows():
        waffle = row['Waffle Type']
        for pan in pan_types:
            if pan in cost_df.columns:
                cost[(waffle, pan)] = float(row[pan])
    
    # Process allowed combinations
    allowed = {}
    for _, row in combinations_df.iterrows():
        waffle = row['Waffle Type']
        for pan in pan_types:
            if pan in combinations_df.columns:
                allowed[(waffle, pan)] = bool(row[pan])
    
    # Make sure every waffle type has at least one allowed pan
    for waffle in waffle_types:
        has_allowed_pan = False
        for pan in pan_types:
            if allowed.get((waffle, pan), False):
                has_allowed_pan = True
                break
        
        if not has_allowed_pan:
            # Assign the first pan as allowed for this waffle
            allowed[(waffle, pan_types[0])] = True
            print(f"Warning: {waffle} had no allowed pans, assigned {pan_types[0]}")
    
    # Compile optimization data
    optimization_data = {
        'waffle_types': waffle_types,
        'pan_types': pan_types,
        'weeks': weeks,
        'demand': demand,
        'supply': supply,
        'wpp': wpp,
        'cost': cost,
        'allowed': allowed
    }
    
    return optimization_data

def main():
    print("Generating complex dataset...")
    
    # Configuration
    config = {
        'solver': 'ortools',  # Using OR-Tools solver
        'time_limit': 3,      # 3 second time limit - should be short enough to hit
        'gap': 0.1,           # 10% optimality gap to test gap handling
        'objective': 'cost',  # Minimize cost
        'limit_to_demand': True,
        'debug': True,
        'use_generated_data': True  # Use generated data instead of Excel files
    }
    
    # Set file paths (in case we need them)
    data_folder = "data/input"
    config['demand'] = os.path.join(data_folder, "WaffleDemand_large.xlsx")
    config['supply'] = os.path.join(data_folder, "PanSupply_large.xlsx")
    config['cost'] = os.path.join(data_folder, "WaffleCostPerPan_large.xlsx")
    config['wpp'] = os.path.join(data_folder, "WafflesPerPan_large.xlsx")
    config['combinations'] = os.path.join(data_folder, "WafflePanCombinations_large.xlsx")
    
    # Load data
    if config['use_generated_data']:
        optimization_data = generate_even_more_complex_data()
    else:
        # Load data directly with increased supply to ensure feasibility
        optimization_data = load_excel_data(
            config['demand'],
            config['supply'],
            config['cost'],
            config['wpp'],
            config['combinations'],
            supply_multiplier=20  # Increase supply to ensure feasibility
        )
    
    print(f"Loaded data with:")
    print(f"- {len(optimization_data['waffle_types'])} waffle types")
    print(f"- {len(optimization_data['pan_types'])} pan types")
    print(f"- {len(optimization_data['weeks'])} weeks")
    print(f"- {len(optimization_data['demand'])} demand entries")
    print(f"- {len(optimization_data['supply'])} supply entries")
    print(f"- {len(optimization_data['allowed'])} allowed combinations")
    
    # Run multiple tests with different time limits
    time_limits = [1, 3]  # Test 1 second and 3 seconds
    
    for time_limit in time_limits:
        print(f"\n\n{'='*60}")
        print(f"TESTING WITH TIME LIMIT: {time_limit} seconds")
        print(f"{'='*60}")
        
        # Create solver
        print("Initializing solver...")
        solver_factory = SolverFactory()
        solver = solver_factory.create_solver(
            solver_name=config.get('solver', 'ortools'),
            time_limit=time_limit,
            optimality_gap=config.get('gap', 0.01)
        )
        
        # Build model
        print("Building optimization model...")
        start_time = time.time()
        
        if config.get('objective', 'cost') == 'cost':
            solver.build_minimize_cost_model(optimization_data)
        else:
            solver.build_maximize_output_model(
                optimization_data,
                limit_to_demand=config.get('limit_to_demand', False)
            )
        
        # Solve model
        print(f"Solving with time limit of {time_limit} seconds and optimality gap of {config['gap']*100}%...")
        solution = solver.solve_model()
        
        # Get solution time
        solution_time = time.time() - start_time
        
        # Print results
        print("\nSolution Status:", solution.get('status'))
        print("Objective Value:", solution.get('objective_value'))
        print("Solution Time:", solution_time, "seconds")
        print("Time Limit Set:", time_limit, "seconds")
        print("Optimality Gap Set:", config['gap'] * 100, "%")
        print("Actual Gap:", solution.get('gap') * 100, "%")
        
        # Check if solution was found
        if solution.get('is_feasible', False):
            if solution_time < time_limit:
                print("\nSolution found BEFORE time limit!")
            else:
                print("\nTime limit reached!")
                print("Time limit functionality is working correctly.")
            
            if solution.get('gap', 1.0) <= config['gap']:
                print("Optimality gap target met!")
            else:
                print("Optimality gap target not met.")
        else:
            print("\nNo feasible solution found. Try adjusting the model parameters.")

if __name__ == "__main__":
    main() 