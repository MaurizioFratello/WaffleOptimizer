"""
Script to generate increased versions of the input data files.
"""
import pandas as pd
import numpy as np
from pathlib import Path

def scale_data_with_randomness(input_file: str, output_file: str, scale_factor: float, add_randomness: bool = False):
    """
    Scale the data by a given factor while maintaining proportions, optionally adding randomness.
    
    Args:
        input_file: Input Excel file path
        output_file: Output Excel file path
        scale_factor: Factor to scale the data by
        add_randomness: If True, adds ±10% random variation to numeric values
    """
    df = pd.read_excel(input_file)
    
    # Special handling for WafflePanCombinations matrix
    if 'WafflePanCombinations' in input_file:
        # Keep the first column (waffle names) as is
        waffle_names = df.iloc[:, 0]
        
        # For pan columns, randomly flip some values
        pan_columns = df.iloc[:, 1:].copy()
        # Create a random mask for flipping values
        flip_mask = np.random.random(pan_columns.shape) < 0.2  # 20% chance to flip each value
        # Convert to numpy array for easier manipulation
        pan_array = pan_columns.values
        # Flip values where mask is True
        pan_array[flip_mask] = 1 - pan_array[flip_mask]
        # Convert back to DataFrame
        pan_columns = pd.DataFrame(pan_array, columns=pan_columns.columns)
        
        # Reconstruct the dataframe
        df = pd.concat([waffle_names, pan_columns], axis=1)
    else:
        # Original scaling logic for other files
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols] * scale_factor
        
        if add_randomness:
            # Add ±10% random variation
            random_factors = np.random.uniform(0.9, 1.1, size=df[numeric_cols].shape)
            df[numeric_cols] = df[numeric_cols] * random_factors
            # Round to integers where needed
            df[numeric_cols] = df[numeric_cols].round(0)
    
    df.to_excel(output_file, index=False)

def generate_increased_dataset(scale_factor: float = 2.0, suffix: str = "_increased"):
    """
    Generate increased versions of all input data files.
    
    Args:
        scale_factor: The factor by which to multiply the numeric values
        suffix: The suffix to append to the output filenames
    """
    # Define input and output files with flags for randomness
    files = {
        'WaffleDemand.xlsx': (f'WaffleDemand{suffix}.xlsx', True),  # Add randomness
        'PanSupply.xlsx': (f'PanSupply{suffix}.xlsx', False),
        'WaffleCostPerPan.xlsx': (f'WaffleCostPerPan{suffix}.xlsx', False),
        'WafflesPerPan.xlsx': (f'WafflesPerPan{suffix}.xlsx', False),
        'WafflePanCombinations.xlsx': (f'WafflePanCombinations{suffix}.xlsx', True)  # Add randomness
    }
    
    # Process each file
    for input_file, (output_file, add_randomness) in files.items():
        print(f"Processing {input_file}...")
        scale_data_with_randomness(input_file, output_file, scale_factor, add_randomness)
        print(f"Created {output_file}")

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate 8x dataset with randomness
    print("Generating 8x dataset with randomness...")
    generate_increased_dataset(scale_factor=8.0, suffix="_increased_8") 