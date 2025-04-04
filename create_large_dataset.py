import pandas as pd
import numpy as np
import os

# Configuration
num_waffle_types = 100
num_pan_types = 30
num_weeks = 40
output_folder = "data/input"

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)

print("Generating large dataset...")

# Generate waffle types and pan types
waffle_types = [f"Waffle_{i+1}" for i in range(num_waffle_types)]
pan_types = [f"Pan_{i+1}" for i in range(num_pan_types)]
weeks = [f"Week_{i+1}" for i in range(num_weeks)]

# 1. Waffle Demand - each waffle type has demand in 30-50% of the weeks
demand_data = {'Waffle Type': waffle_types}
for week in weeks:
    demands = np.zeros(num_waffle_types)
    # Randomly select 30-50% of waffle types to have demand this week
    selection_mask = np.random.rand(num_waffle_types) < np.random.uniform(0.3, 0.5)
    # Generate random demand values between 10 and 200
    selected_demands = np.random.randint(10, 200, size=np.sum(selection_mask))
    demands[selection_mask] = selected_demands
    demand_data[week] = demands

demand_df = pd.DataFrame(demand_data)
demand_df.to_excel(f"{output_folder}/WaffleDemand_large.xlsx", index=False)
print("Generated waffle demand data")

# 2. Pan Supply - mostly available in the first week with some replenishments
supply_data = {'Pan Type': pan_types}
for week_idx, week in enumerate(weeks):
    supplies = np.zeros(num_pan_types)
    if week_idx == 0:
        # Initial large supply in first week
        supplies = np.random.randint(1000, 5000, size=num_pan_types)
    elif week_idx % 5 == 0:
        # Replenishment every 5 weeks for some pans
        selection_mask = np.random.rand(num_pan_types) < 0.3
        selected_supplies = np.random.randint(100, 500, size=np.sum(selection_mask))
        supplies[selection_mask] = selected_supplies
    supply_data[week] = supplies

supply_df = pd.DataFrame(supply_data)
supply_df.to_excel(f"{output_folder}/PanSupply_large.xlsx", index=False)
print("Generated pan supply data")

# 3. Waffles Per Pan - how many waffles of each type can be made in one pan
wpp_data = {
    'Waffle Type': waffle_types,
    'WPP': np.random.randint(50, 1000, size=num_waffle_types)
}
wpp_df = pd.DataFrame(wpp_data)
wpp_df.to_excel(f"{output_folder}/WafflesPerPan_large.xlsx", index=False)
print("Generated waffles per pan data")

# 4. Waffle Cost Per Pan - cost of producing each waffle type in each pan
cost_data = {'Waffle Type': waffle_types}
for pan in pan_types:
    # Base costs between 0.01 and 10.0
    base_costs = np.random.uniform(0.01, 10.0, size=num_waffle_types)
    # Add random variation to create a more complex cost structure
    variation = np.random.uniform(0.8, 1.2, size=num_waffle_types)
    cost_data[pan] = base_costs * variation

cost_df = pd.DataFrame(cost_data)
cost_df.to_excel(f"{output_folder}/WaffleCostPerPan_large.xlsx", index=False)
print("Generated waffle cost per pan data")

# 5. Waffle Pan Combinations - which waffle types can be made in which pans
# Make this sparse to increase complexity (only 30% of combinations are valid)
combinations_data = {'Waffle Type': waffle_types}
for pan in pan_types:
    # Each waffle can be made in approximately 30% of pans
    combinations_data[pan] = np.random.choice([0, 1], size=num_waffle_types, p=[0.7, 0.3])
    
    # Ensure at least one pan can make each waffle type
    for i in range(num_waffle_types):
        waffle_has_pan = False
        for p in pan_types:
            if p in combinations_data and combinations_data[p][i] == 1:
                waffle_has_pan = True
                break
        if not waffle_has_pan and pan == pan_types[-1]:
            combinations_data[pan][i] = 1

combinations_df = pd.DataFrame(combinations_data)
combinations_df.to_excel(f"{output_folder}/WafflePanCombinations_large.xlsx", index=False)
print("Generated waffle pan combinations data")

print("Dataset generation complete!") 