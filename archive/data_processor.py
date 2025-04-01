"""
Data Processing Module for Waffle Production Optimization.

This module handles loading and validating input data from Excel files.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Set, Optional

class DataProcessor:
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the data processor.
        
        Args:
            debug_mode: If True, enables debug output
        """
        # Initialize debug mode
        self.debug_mode = debug_mode
        
        # Initialize data storage
        self.waffle_demand = None
        self.pan_supply = None
        self.waffle_cost = None
        self.waffles_per_pan = None
        self.allowed_combinations = None
        
        # Initialize dimensions as sets
        self.waffle_types = set()
        self.pan_types = set()
        self.weeks = set()
        
        # Initialize dictionaries
        self.demand_dict = {}
        self.supply_dict = {}
        self.cost_dict = {}
        self.wpp_dict = {}
        self.allowed_dict = {}
        
    def _debug_print(self, message: str) -> None:
        """
        Print debug message if debug mode is enabled.
        
        Args:
            message: Debug message to print
        """
        if self.debug_mode:
            print(message)

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
        # Load raw data from Excel files
        self.waffle_demand = pd.read_excel(demand_file)
        self.pan_supply = pd.read_excel(supply_file)
        self.waffle_cost = pd.read_excel(cost_file)
        self.waffles_per_pan = pd.read_excel(wpp_file)
        self.allowed_combinations = pd.read_excel(combinations_file)
        
        # Rename 'Unnamed: 0' columns to match expected column names
        if 'Unnamed: 0' in self.waffle_demand.columns:
            self.waffle_demand = self.waffle_demand.rename(columns={'Unnamed: 0': 'WaffleType'})
            
        if 'Unnamed: 0' in self.pan_supply.columns:
            self.pan_supply = self.pan_supply.rename(columns={'Unnamed: 0': 'PanType'})
            
        if 'Unnamed: 0' in self.waffles_per_pan.columns:
            # Rename to WaffleType since this file has waffles per waffle type, not per pan type
            self.waffles_per_pan = self.waffles_per_pan.rename(columns={'Unnamed: 0': 'WaffleType'})
            
        # Transform waffle_cost from wide to long format
        if 'Unnamed: 0' in self.waffle_cost.columns:
            self.waffle_cost = self.waffle_cost.rename(columns={'Unnamed: 0': 'WaffleType'})
            self.waffle_cost = self.waffle_cost.melt(
                id_vars=['WaffleType'],
                var_name='PanType',
                value_name='Cost'
            )
        
        # Transform allowed_combinations from wide to long format
        if 'Unnamed: 0' in self.allowed_combinations.columns:
            self.allowed_combinations = self.allowed_combinations.rename(columns={'Unnamed: 0': 'WaffleType'})
            self.allowed_combinations = self.allowed_combinations.melt(
                id_vars=['WaffleType'],
                var_name='PanType',
                value_name='Allowed'
            )
        
        # Process and validate data
        self._extract_dimensions()
        self._validate_data()
        self._process_data()
        
    def _extract_dimensions(self) -> None:
        """Extract dimensions (waffle types, pan types, weeks) from input data."""
        # Extract waffle types from various files
        if self.waffle_demand is not None:
            if 'WaffleType' in self.waffle_demand.columns:
                self.waffle_types.update(self.waffle_demand['WaffleType'].unique())
                
        if self.waffle_cost is not None:
            if 'WaffleType' in self.waffle_cost.columns:
                self.waffle_types.update(self.waffle_cost['WaffleType'].unique())
                
        if self.allowed_combinations is not None:
            if 'WaffleType' in self.allowed_combinations.columns:
                self.waffle_types.update(self.allowed_combinations['WaffleType'].unique())
                
        if self.waffles_per_pan is not None:
            if 'WaffleType' in self.waffles_per_pan.columns:
                self.waffle_types.update(self.waffles_per_pan['WaffleType'].unique())
        
        # Extract pan types from various files
        if self.pan_supply is not None:
            if 'PanType' in self.pan_supply.columns:
                self.pan_types.update(self.pan_supply['PanType'].unique())
                
        if self.waffle_cost is not None:
            if 'PanType' in self.waffle_cost.columns:
                self.pan_types.update(self.waffle_cost['PanType'].unique())
                
        if self.allowed_combinations is not None:
            if 'PanType' in self.allowed_combinations.columns:
                self.pan_types.update(self.allowed_combinations['PanType'].unique())
        
        # Extract weeks from demand and supply data
        demand_weeks = set()
        if self.waffle_demand is not None:
            demand_weeks = {col for col in self.waffle_demand.columns if col not in ['WaffleType']}
            
        supply_weeks = set()
        if self.pan_supply is not None:
            supply_weeks = {col for col in self.pan_supply.columns if col not in ['PanType']}
            
        # Use the union of weeks from both datasets instead of intersection
        self.weeks = demand_weeks.union(supply_weeks)
            
        # Convert to sorted lists for consistent indexing
        self.waffle_types = sorted(list(self.waffle_types))
        self.pan_types = sorted(list(self.pan_types))
        self.weeks = sorted(list(self.weeks))
        
    def _validate_data(self) -> None:
        """Validate the loaded data for consistency and completeness."""
        if not self.waffle_types:
            raise ValueError("No waffle types found in the input data.")
            
        if not self.pan_types:
            raise ValueError("No pan types found in the input data.")
            
        if not self.weeks:
            raise ValueError("No weeks found in the demand or supply data.")
        
        # Validate waffle demand data
        if self.waffle_demand is None:
            raise ValueError("Waffle demand data is missing.")
        if 'WaffleType' not in self.waffle_demand.columns:
            raise ValueError("WaffleType column is missing in waffle demand data.")
        
        # Validate pan supply data
        if self.pan_supply is None:
            raise ValueError("Pan supply data is missing.")
        if 'PanType' not in self.pan_supply.columns:
            raise ValueError("PanType column is missing in pan supply data.")
        
        # Validate waffle cost data
        if self.waffle_cost is None:
            raise ValueError("Waffle cost data is missing.")
        required_columns = ['WaffleType', 'PanType', 'Cost']
        for col in required_columns:
            if col not in self.waffle_cost.columns:
                raise ValueError(f"{col} column is missing in waffle cost data.")
        
        # Validate waffles per pan data
        if self.waffles_per_pan is None:
            raise ValueError("Waffles per pan data is missing.")
        required_columns = ['WaffleType', 'WPP']
        for col in required_columns:
            if col not in self.waffles_per_pan.columns:
                raise ValueError(f"{col} column is missing in waffles per pan data.")
        
        # Validate allowed combinations data
        if self.allowed_combinations is None:
            raise ValueError("Allowed combinations data is missing.")
        required_columns = ['WaffleType', 'PanType', 'Allowed']
        for col in required_columns:
            if col not in self.allowed_combinations.columns:
                raise ValueError(f"{col} column is missing in allowed combinations data.")
    
    def _process_data(self) -> None:
        """Process input data into a suitable format for optimization models."""
        # Create demand dictionary: {(waffle_type, week): demand}
        self.demand_dict = {}
        for _, row in self.waffle_demand.iterrows():
            waffle_type = row['WaffleType']
            for week in self.weeks:
                if week in self.waffle_demand.columns:
                    # If week exists in demand data, use it
                    self.demand_dict[(waffle_type, week)] = row[week] if week in row else 0
                else:
                    # If week doesn't exist in demand data (like Week 1-2), set demand to 0
                    self.demand_dict[(waffle_type, week)] = 0
        
        # Create supply dictionary: {(pan_type, week): supply}
        self.supply_dict = {}
        for _, row in self.pan_supply.iterrows():
            pan_type = row['PanType']
            for week in self.weeks:
                if week in self.pan_supply.columns:
                    # If week exists in supply data, use it
                    self.supply_dict[(pan_type, week)] = row[week] if week in row else 0
                else:
                    # If week doesn't exist in supply data, set supply to 0
                    self.supply_dict[(pan_type, week)] = 0
        
        # Create cost dictionary: {(waffle_type, pan_type): cost}
        self.cost_dict = {}
        for _, row in self.waffle_cost.iterrows():
            waffle_type = row['WaffleType']
            pan_type = row['PanType']
            cost = row['Cost']
            self.cost_dict[(waffle_type, pan_type)] = cost
        
        # Create waffles per waffle type dictionary: {waffle_type: wpp}
        self.wpp_dict = {}
        for _, row in self.waffles_per_pan.iterrows():
            waffle_type = row['WaffleType']
            wpp = row['WPP']
            self.wpp_dict[waffle_type] = wpp
        
        # Create allowed combinations dictionary: {(waffle_type, pan_type): allowed}
        self.allowed_dict = {}
        for _, row in self.allowed_combinations.iterrows():
            waffle_type = row['WaffleType']
            pan_type = row['PanType']
            allowed = row['Allowed']
            self.allowed_dict[(waffle_type, pan_type)] = bool(allowed)
    
    def check_data_loaded(self) -> bool:
        """Check if all required data has been loaded."""
        return (self.waffle_demand is not None and
                self.pan_supply is not None and
                self.waffle_cost is not None and
                self.waffles_per_pan is not None and
                self.allowed_combinations is not None)
    
    def get_optimization_data(self) -> Dict:
        """
        Get processed data for optimization models.
        
        Returns:
            Dict: Dictionary containing all necessary data for optimization
        """
        if not self.check_data_loaded():
            raise ValueError("Data has not been fully loaded.")
            
        return {
            'waffle_types': self.waffle_types,
            'pan_types': self.pan_types,
            'weeks': self.weeks,
            'demand': self.demand_dict,
            'supply': self.supply_dict,
            'cost': self.cost_dict,
            'wpp': self.wpp_dict,
            'allowed': self.allowed_dict
        }

    def get_feasibility_data(self) -> Dict:
        """
        Get data for feasibility checks.
        
        Returns:
            Dict: Dictionary containing data for feasibility checks
        """
        if not self.check_data_loaded():
            raise ValueError("Data has not been fully loaded.")
            
        # Debug logging
        self._debug_print("\nDebug: Starting feasibility data preparation")
        self._debug_print(f"Debug: Available weeks: {self.weeks}")
        self._debug_print(f"Debug: Available waffle types: {self.waffle_types}")
        self._debug_print(f"Debug: Available pan types: {self.pan_types}")
        
        # Calculate total demand and supply
        total_demand = {}
        for week in self.weeks:
            week_demand = sum(self.demand_dict.get((wt, week), 0) for wt in self.waffle_types)
            total_demand[week] = week_demand
            self._debug_print(f"Debug: Week {week} demand: {week_demand}")
            self._debug_print(f"Debug: Demand dict entries for week {week}:")
            for wt in self.waffle_types:
                self._debug_print(f"  {wt}: {self.demand_dict.get((wt, week), 0)}")
            
        total_supply = {}
        for week in self.weeks:
            week_supply = sum(self.supply_dict.get((pt, week), 0) for pt in self.pan_types)
            total_supply[week] = week_supply
            self._debug_print(f"Debug: Week {week} supply: {week_supply}")
            self._debug_print(f"Debug: Supply dict entries for week {week}:")
            for pt in self.pan_types:
                self._debug_print(f"  {pt}: {self.supply_dict.get((pt, week), 0)}")
        
        # Debug logging
        self._debug_print(f"Debug: Calculated total_demand: {total_demand}")
        self._debug_print(f"Debug: Calculated total_supply: {total_supply}")
        
        # Create and return the data dictionary
        data = {
            'waffle_types': self.waffle_types,
            'pan_types': self.pan_types,
            'weeks': self.weeks,
            'demand': self.demand_dict,
            'supply': self.supply_dict,
            'cost': self.cost_dict,
            'wpp': self.wpp_dict,
            'allowed': self.allowed_dict,
            'total_demand': total_demand,
            'total_supply': total_supply
        }
        
        # Debug logging
        self._debug_print(f"Debug: Final data dictionary keys: {list(data.keys())}")
        self._debug_print(f"Debug: Data dictionary contents:")
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                self._debug_print(f"  {key}: {type(value)} with {len(value)} items")
                if key in ['total_demand', 'total_supply']:
                    self._debug_print(f"    Values: {value}")
            else:
                self._debug_print(f"  {key}: {type(value)}")
        
        return data
