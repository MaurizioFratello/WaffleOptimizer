"""
Data Processing Module for Waffle Production Optimization.

This module handles loading and validating input data from Excel files.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Set, Optional, Any

from src.data.constraint_config import ConstraintConfigManager

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
        
        # Initialize constraint configuration manager
        self.constraint_manager = ConstraintConfigManager(debug_mode=debug_mode)
        
    def _debug_print(self, message: str) -> None:
        """
        Print debug message if debug mode is enabled.
        
        Args:
            message: Debug message to print
        """
        if self.debug_mode:
            print(f"[DataProcessor] {message}")

    def load_data(self, 
                  demand_file: str, 
                  supply_file: str, 
                  cost_file: str, 
                  wpp_file: str, 
                  combinations_file: str,
                  constraint_config_file: Optional[str] = None) -> None:
        """
        Load data from Excel files.
        
        Args:
            demand_file: Path to waffle demand Excel file
            supply_file: Path to pan supply Excel file
            cost_file: Path to waffle cost Excel file
            wpp_file: Path to waffles per pan Excel file
            combinations_file: Path to allowed combinations Excel file
            constraint_config_file: Path to constraint configuration JSON file (optional)
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
        
        # Load constraint configuration if provided
        if constraint_config_file:
            self._debug_print(f"Loading constraint configuration from {constraint_config_file}")
            self.constraint_manager.load_configuration(constraint_config_file)
        
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
                
        # Additional validation could be added here
        
    def _process_data(self) -> None:
        """Process the loaded data into dictionaries for optimization."""
        # Process demand data
        for _, row in self.waffle_demand.iterrows():
            waffle_type = row['WaffleType']
            for week in self.weeks:
                if week in self.waffle_demand.columns and not pd.isna(row[week]):
                    demand_value = int(row[week])
                    if demand_value > 0:
                        self.demand_dict[(waffle_type, week)] = demand_value
        
        # Process supply data
        for _, row in self.pan_supply.iterrows():
            pan_type = row['PanType']
            for week in self.weeks:
                if week in self.pan_supply.columns and not pd.isna(row[week]):
                    supply_value = int(row[week])
                    if supply_value > 0:
                        self.supply_dict[(pan_type, week)] = supply_value
        
        # Process cost data
        for _, row in self.waffle_cost.iterrows():
            waffle_type = row['WaffleType']
            pan_type = row['PanType']
            cost = row['Cost']
            if not pd.isna(cost):
                self.cost_dict[(waffle_type, pan_type)] = float(cost)
        
        # Process waffles per pan data
        for _, row in self.waffles_per_pan.iterrows():
            waffle_type = row['WaffleType']
            wpp = row['WPP']
            if not pd.isna(wpp):
                self.wpp_dict[waffle_type] = int(wpp)
        
        # Process allowed combinations data
        for _, row in self.allowed_combinations.iterrows():
            waffle_type = row['WaffleType']
            pan_type = row['PanType']
            allowed = row['Allowed']
            if not pd.isna(allowed):
                # Convert to boolean (various formats)
                if isinstance(allowed, bool):
                    self.allowed_dict[(waffle_type, pan_type)] = allowed
                elif isinstance(allowed, (int, float)):
                    self.allowed_dict[(waffle_type, pan_type)] = allowed > 0
                elif isinstance(allowed, str):
                    allowed_lower = allowed.lower()
                    self.allowed_dict[(waffle_type, pan_type)] = allowed_lower in ['yes', 'true', '1', 't', 'y']
        
    def check_data_loaded(self) -> bool:
        """
        Check if data has been loaded.
        
        Returns:
            bool: True if data is loaded, False otherwise
        """
        return (self.waffle_demand is not None and
                self.pan_supply is not None and
                self.waffle_cost is not None and
                self.waffles_per_pan is not None and
                self.allowed_combinations is not None)
                
    def get_optimization_data(self) -> Dict:
        """
        Get the data in a format suitable for optimization.
        
        Returns:
            Dict: Dictionary containing optimization data
        """
        if not self.check_data_loaded():
            raise ValueError("Data has not been loaded. Call load_data first.")
            
        # Create the optimization data dictionary
        optimization_data = {
            'waffle_types': self.waffle_types,
            'pan_types': self.pan_types,
            'weeks': self.weeks,
            'demand': self.demand_dict,
            'supply': self.supply_dict,
            'cost': self.cost_dict,
            'wpp': self.wpp_dict,
            'allowed': self.allowed_dict
        }
        
        return optimization_data
        
    def get_feasibility_data(self) -> Dict:
        """
        Get the data in a format suitable for feasibility checking.
        
        Returns:
            Dict: Dictionary containing feasibility data
        """
        # For now, the same as optimization data
        return self.get_optimization_data()
    
    def get_constraint_manager(self) -> ConstraintConfigManager:
        """
        Get the constraint configuration manager.
        
        Returns:
            ConstraintConfigManager: Constraint configuration manager
        """
        return self.constraint_manager
    
    def save_constraint_configuration(self, file_path: str) -> bool:
        """
        Save the current constraint configuration to a file.
        
        Args:
            file_path: Path to save the configuration
            
        Returns:
            bool: True if the configuration was saved successfully, False otherwise
        """
        return self.constraint_manager.save_configuration(file_path)
    
    def load_constraint_configuration(self, file_path: str) -> bool:
        """
        Load constraint configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            bool: True if the configuration was loaded successfully, False otherwise
        """
        return self.constraint_manager.load_configuration(file_path)
    
    def create_solver_with_constraints(self, solver_name: str, **kwargs) -> Any:
        """
        Create a solver with the configured constraints.
        
        Args:
            solver_name: Name of the solver
            **kwargs: Additional arguments for the solver
            
        Returns:
            Any: Solver instance
        """
        return self.constraint_manager.get_solver_manager().create_solver(solver_name, **kwargs) 