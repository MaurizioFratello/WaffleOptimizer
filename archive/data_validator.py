"""
Data Validation Module for Waffle Production Optimization.

This module performs pre-processing validation checks on all input Excel files
to ensure data integrity and prevent duplicate entries.
"""
import pandas as pd
from typing import List, Dict, Tuple
import os

class DataValidator:
    def __init__(self):
        """Initialize the data validator."""
        self.validation_issues = []
        
    def validate_all_files(self) -> Tuple[bool, List[str]]:
        """
        Validate all input files for duplicates and data integrity.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        self.validation_issues = []
        
        # Validate each file
        self._validate_waffle_pan_combinations()
        self._validate_waffle_demand()
        self._validate_pan_supply()
        self._validate_waffles_per_pan()
        self._validate_waffle_cost_per_pan()
        
        return len(self.validation_issues) == 0, self.validation_issues
    
    def validate_loaded_data(self, data_processor) -> Tuple[bool, List[str]]:
        """
        Validate already loaded data from the DataProcessor.
        This is more efficient than validating files directly.
        
        Args:
            data_processor: The DataProcessor instance with loaded data
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        self.validation_issues = []
        
        # Validate data from the data processor
        self._validate_loaded_waffle_pan_combinations(data_processor.allowed_combinations)
        self._validate_loaded_waffle_demand(data_processor.waffle_demand)
        self._validate_loaded_pan_supply(data_processor.pan_supply)
        self._validate_loaded_waffles_per_pan(data_processor.waffles_per_pan)
        self._validate_loaded_waffle_cost(data_processor.waffle_cost)
        
        # Validate data consistency between different datasets
        self._validate_data_consistency(data_processor)
        
        return len(self.validation_issues) == 0, self.validation_issues
    
    def _validate_loaded_waffle_pan_combinations(self, combinations_df) -> None:
        """Validate loaded waffle-pan combinations data for duplicates."""
        if combinations_df is None:
            self.validation_issues.append("ERROR: Waffle-pan combinations data is missing")
            return
            
        try:
            # Check for duplicate waffle-pan combinations
            duplicates = combinations_df[combinations_df.duplicated(subset=['WaffleType', 'PanType'], keep=False)]
            if not duplicates.empty:
                for waffle in duplicates['WaffleType'].unique():
                    for pan in duplicates[duplicates['WaffleType'] == waffle]['PanType'].unique():
                        rows = duplicates[
                            (duplicates['WaffleType'] == waffle) & 
                            (duplicates['PanType'] == pan)
                        ].index.tolist()
                        self.validation_issues.append(
                            f"ERROR: Duplicate combination entries found in waffle-pan combinations data\n"
                            f"Duplicate entries for:\n"
                            f"- Waffle: {waffle}, Pan: {pan} (appears in rows {[row + 1 for row in rows]})\n"
                            f"Please ensure each waffle-pan combination appears only once."
                        )
        except Exception as e:
            self.validation_issues.append(f"Error validating waffle-pan combinations data: {str(e)}")
    
    def _validate_loaded_waffle_demand(self, demand_df) -> None:
        """Validate loaded waffle demand data for duplicates."""
        if demand_df is None:
            self.validation_issues.append("ERROR: Waffle demand data is missing")
            return
            
        try:
            # Check for duplicate waffle types
            duplicates = demand_df[demand_df.duplicated(subset=['WaffleType'], keep=False)]
            if not duplicates.empty:
                for waffle in duplicates['WaffleType'].unique():
                    rows = duplicates[duplicates['WaffleType'] == waffle].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate waffle entries found in waffle demand data\n"
                        f"Duplicate entries for:\n"
                        f"- Waffle: {waffle} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each waffle type appears only once."
                    )
        except Exception as e:
            self.validation_issues.append(f"Error validating waffle demand data: {str(e)}")
    
    def _validate_loaded_pan_supply(self, supply_df) -> None:
        """Validate loaded pan supply data for duplicates."""
        if supply_df is None:
            self.validation_issues.append("ERROR: Pan supply data is missing")
            return
            
        try:
            # Check for duplicate pan types
            duplicates = supply_df[supply_df.duplicated(subset=['PanType'], keep=False)]
            if not duplicates.empty:
                for pan in duplicates['PanType'].unique():
                    rows = duplicates[duplicates['PanType'] == pan].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate pan entries found in pan supply data\n"
                        f"Duplicate entries for:\n"
                        f"- Pan: {pan} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each pan type appears only once."
                    )
        except Exception as e:
            self.validation_issues.append(f"Error validating pan supply data: {str(e)}")
    
    def _validate_loaded_waffles_per_pan(self, wpp_df) -> None:
        """Validate loaded waffles per pan data for duplicates."""
        if wpp_df is None:
            self.validation_issues.append("ERROR: Waffles per pan data is missing")
            return
            
        try:
            # Check for duplicate waffle types
            duplicates = wpp_df[wpp_df.duplicated(subset=['WaffleType'], keep=False)]
            if not duplicates.empty:
                for waffle in duplicates['WaffleType'].unique():
                    rows = duplicates[duplicates['WaffleType'] == waffle].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate waffle entries found in waffles per pan data\n"
                        f"Duplicate entries for:\n"
                        f"- Waffle: {waffle} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each waffle type appears only once."
                    )
        except Exception as e:
            self.validation_issues.append(f"Error validating waffles per pan data: {str(e)}")
    
    def _validate_loaded_waffle_cost(self, cost_df) -> None:
        """Validate loaded waffle cost data for duplicates."""
        if cost_df is None:
            self.validation_issues.append("ERROR: Waffle cost data is missing")
            return
            
        try:
            # Check for duplicate waffle-pan combinations
            duplicates = cost_df[cost_df.duplicated(subset=['WaffleType', 'PanType'], keep=False)]
            if not duplicates.empty:
                for waffle in duplicates['WaffleType'].unique():
                    for pan in duplicates[duplicates['WaffleType'] == waffle]['PanType'].unique():
                        rows = duplicates[
                            (duplicates['WaffleType'] == waffle) & 
                            (duplicates['PanType'] == pan)
                        ].index.tolist()
                        self.validation_issues.append(
                            f"ERROR: Duplicate cost entries found in waffle cost data\n"
                            f"Duplicate entries for:\n"
                            f"- Waffle: {waffle}, Pan: {pan} (appears in rows {[row + 1 for row in rows]})\n"
                            f"Please ensure each waffle-pan combination appears only once."
                        )
        except Exception as e:
            self.validation_issues.append(f"Error validating waffle cost data: {str(e)}")
    
    def _validate_data_consistency(self, data_processor) -> None:
        """Validate consistency between different datasets."""
        try:
            # Check if all waffle types in cost data exist in demand data
            cost_waffles = set()
            if data_processor.waffle_cost is not None and 'WaffleType' in data_processor.waffle_cost.columns:
                cost_waffles = set(data_processor.waffle_cost['WaffleType'].unique())
                
            demand_waffles = set()
            if data_processor.waffle_demand is not None and 'WaffleType' in data_processor.waffle_demand.columns:
                demand_waffles = set(data_processor.waffle_demand['WaffleType'].unique())
                
            missing_in_demand = cost_waffles - demand_waffles
            if missing_in_demand:
                self.validation_issues.append(
                    f"WARNING: Some waffle types in cost data are missing from demand data:\n"
                    f"- Missing waffles: {', '.join(sorted(missing_in_demand))}\n"
                    f"This might cause issues in optimization."
                )
                
            # Check if all pan types in supply data exist in cost data
            supply_pans = set()
            if data_processor.pan_supply is not None and 'PanType' in data_processor.pan_supply.columns:
                supply_pans = set(data_processor.pan_supply['PanType'].unique())
                
            cost_pans = set()
            if data_processor.waffle_cost is not None and 'PanType' in data_processor.waffle_cost.columns:
                cost_pans = set(data_processor.waffle_cost['PanType'].unique())
                
            missing_in_cost = supply_pans - cost_pans
            if missing_in_cost:
                self.validation_issues.append(
                    f"WARNING: Some pan types in supply data are missing from cost data:\n"
                    f"- Missing pans: {', '.join(sorted(missing_in_cost))}\n"
                    f"This might cause issues in optimization."
                )
        except Exception as e:
            self.validation_issues.append(f"Error validating data consistency: {str(e)}")
    
    # Keep the original validation methods for backward compatibility
    def _validate_waffle_pan_combinations(self) -> None:
        """Validate WafflePanCombinations.xlsx for duplicates."""
        try:
            df = pd.read_excel('WafflePanCombinations.xlsx')
            
            # Check for duplicate waffles
            waffle_duplicates = df[df.duplicated(subset=['Unnamed: 0'], keep=False)]
            if not waffle_duplicates.empty:
                for waffle in waffle_duplicates['Unnamed: 0'].unique():
                    rows = waffle_duplicates[waffle_duplicates['Unnamed: 0'] == waffle].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate waffle entries found in WafflePanCombinations.xlsx\n"
                        f"File: WafflePanCombinations.xlsx\n"
                        f"Duplicate entries for:\n"
                        f"- {waffle} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each waffle appears only once in the first column."
                    )
            
            # Check for duplicate weeks (columns)
            week_columns = [col for col in df.columns if col != 'Unnamed: 0']
            week_duplicates = []
            seen_weeks = set()
            
            for col in week_columns:
                if col in seen_weeks:
                    week_duplicates.append(col)
                seen_weeks.add(col)
            
            if week_duplicates:
                self.validation_issues.append(
                    f"ERROR: Duplicate week columns found in WafflePanCombinations.xlsx\n"
                    f"File: WafflePanCombinations.xlsx\n"
                    f"Duplicate columns for:\n"
                    f"- Weeks: {', '.join(week_duplicates)}\n"
                    f"Please ensure each week appears only once in the column headers."
                )
                
        except Exception as e:
            self.validation_issues.append(f"Error validating WafflePanCombinations.xlsx: {str(e)}")
    
    def _validate_waffle_demand(self) -> None:
        """Validate WaffleDemand.xlsx for duplicates."""
        try:
            df = pd.read_excel('WaffleDemand.xlsx')
            
            # Check for duplicate waffle-week combinations
            demand_duplicates = df[df.duplicated(subset=['Unnamed: 0'], keep=False)]
            if not demand_duplicates.empty:
                for waffle in demand_duplicates['Unnamed: 0'].unique():
                    rows = demand_duplicates[demand_duplicates['Unnamed: 0'] == waffle].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate demand entries found in WaffleDemand.xlsx\n"
                        f"File: WaffleDemand.xlsx\n"
                        f"Duplicate entries for:\n"
                        f"- {waffle} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each waffle appears only once in the first column."
                    )
                    
        except Exception as e:
            self.validation_issues.append(f"Error validating WaffleDemand.xlsx: {str(e)}")
    
    def _validate_pan_supply(self) -> None:
        """Validate PanSupply.xlsx for duplicates."""
        try:
            df = pd.read_excel('PanSupply.xlsx')
            
            # Check for duplicate pan-week combinations
            supply_duplicates = df[df.duplicated(subset=['Unnamed: 0'], keep=False)]
            if not supply_duplicates.empty:
                for pan in supply_duplicates['Unnamed: 0'].unique():
                    rows = supply_duplicates[supply_duplicates['Unnamed: 0'] == pan].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate supply entries found in PanSupply.xlsx\n"
                        f"File: PanSupply.xlsx\n"
                        f"Duplicate entries for:\n"
                        f"- {pan} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each pan appears only once in the first column."
                    )
                    
        except Exception as e:
            self.validation_issues.append(f"Error validating PanSupply.xlsx: {str(e)}")
    
    def _validate_waffles_per_pan(self) -> None:
        """Validate WafflesPerPan.xlsx for duplicates."""
        try:
            df = pd.read_excel('WafflesPerPan.xlsx')
            
            # Check for duplicate waffle entries
            wpp_duplicates = df[df.duplicated(subset=['Unnamed: 0'], keep=False)]
            if not wpp_duplicates.empty:
                for waffle in wpp_duplicates['Unnamed: 0'].unique():
                    rows = wpp_duplicates[wpp_duplicates['Unnamed: 0'] == waffle].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate waffle entries found in WafflesPerPan.xlsx\n"
                        f"File: WafflesPerPan.xlsx\n"
                        f"Duplicate entries for:\n"
                        f"- {waffle} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each waffle appears only once in the first column."
                    )
                    
        except Exception as e:
            self.validation_issues.append(f"Error validating WafflesPerPan.xlsx: {str(e)}")
    
    def _validate_waffle_cost_per_pan(self) -> None:
        """Validate WaffleCostPerPan.xlsx for duplicates."""
        try:
            df = pd.read_excel('WaffleCostPerPan.xlsx')
            
            # Check for duplicate waffle entries
            cost_duplicates = df[df.duplicated(subset=['Unnamed: 0'], keep=False)]
            if not cost_duplicates.empty:
                for waffle in cost_duplicates['Unnamed: 0'].unique():
                    rows = cost_duplicates[cost_duplicates['Unnamed: 0'] == waffle].index.tolist()
                    self.validation_issues.append(
                        f"ERROR: Duplicate waffle entries found in WaffleCostPerPan.xlsx\n"
                        f"File: WaffleCostPerPan.xlsx\n"
                        f"Duplicate entries for:\n"
                        f"- {waffle} (appears in rows {[row + 1 for row in rows]})\n"
                        f"Please ensure each waffle appears only once in the first column."
                    )
                    
        except Exception as e:
            self.validation_issues.append(f"Error validating WaffleCostPerPan.xlsx: {str(e)}")
    
    def print_validation_report(self) -> None:
        """Print a formatted validation report."""
        if not self.validation_issues:
            print("\nValidation successful! No duplicate entries found.")
            return
            
        print("\n=== Data Validation Report ===")
        print(f"Found {len(self.validation_issues)} validation issues:\n")
        
        for i, issue in enumerate(self.validation_issues, 1):
            print(f"Issue {i}:")
            print(issue)
            print("-" * 80) 