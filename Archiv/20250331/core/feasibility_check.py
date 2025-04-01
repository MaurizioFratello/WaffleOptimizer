"""
Feasibility Checking Module for Waffle Production Optimization.

This module checks if the optimization problem is likely to be feasible
based on the input data.
"""
from typing import Dict, List, Any


class FeasibilityChecker:
    def __init__(self, data: Dict):
        """
        Initialize the feasibility checker.
        
        Args:
            data: Dictionary containing data for feasibility checks
        """
        self.data = data
        self.feasibility_issues = []
        self.warnings = []
        
    def check_feasibility(self) -> bool:
        """
        Check if the optimization problem appears to be feasible.
        
        Returns:
            bool: True if the problem appears feasible, False otherwise
        """
        self.feasibility_issues = []
        self.warnings = []
        
        # Check total supply vs. demand
        self._check_total_supply()
        
        # Check for waffle types with no compatible pans
        self._check_waffle_compatibility()
        
        # Check week-by-week supply vs. demand
        self._check_weekly_supply()
        
        # Return True if no critical issues found
        return len(self.feasibility_issues) == 0
    
    def _check_total_supply(self) -> None:
        """Check if total pan supply is sufficient for total demand."""
        total_demand = sum(self.data['total_demand'].values())
        total_supply = sum(self.data['total_supply'].values())
        
        if total_supply < total_demand:
            self.feasibility_issues.append(
                f"Insufficient total pan supply: {total_supply} pans available, "
                f"but {total_demand} pans required for demand."
            )
        elif total_supply < total_demand * 1.1:  # 10% margin
            self.warnings.append(
                f"Supply is tight: only {total_supply} pans available for "
                f"{total_demand} pans demand (less than 10% margin)."
            )
    
    def _check_waffle_compatibility(self) -> None:
        """Check if each waffle type has at least one compatible pan type."""
        waffle_types = self.data['waffle_types']
        pan_types = self.data['pan_types']
        allowed = self.data['allowed']
        
        for waffle in waffle_types:
            compatible_pans = [p for p in pan_types if allowed.get((waffle, p), False)]
            if not compatible_pans:
                self.feasibility_issues.append(
                    f"Waffle type '{waffle}' has no compatible pan types."
                )
    
    def _check_weekly_supply(self) -> None:
        """Check if weekly pan supply is sufficient for weekly demand."""
        weeks = self.data['weeks']
        total_demand = self.data['total_demand']
        total_supply = self.data['total_supply']
        
        cumulative_demand = 0
        cumulative_supply = 0
        
        for week in weeks:
            week_demand = total_demand.get(week, 0)
            week_supply = total_supply.get(week, 0)
            
            cumulative_demand += week_demand
            cumulative_supply += week_supply
            
            if cumulative_supply < cumulative_demand:
                self.feasibility_issues.append(
                    f"Insufficient cumulative supply by week {week}: "
                    f"{cumulative_supply} pans available, but {cumulative_demand} pans required."
                )
                
    def get_result_summary(self) -> Dict:
        """
        Get a summary of the feasibility check results.
        
        Returns:
            Dict: Dictionary containing feasibility check results
        """
        is_feasible = len(self.feasibility_issues) == 0
        
        return {
            'is_feasible': is_feasible,
            'issues': self.feasibility_issues,
            'warnings': self.warnings
        }
    
    def print_report(self) -> None:
        """Print a detailed feasibility report."""
        is_feasible = len(self.feasibility_issues) == 0
        
        print("\n=== Feasibility Check Report ===")
        print(f"Overall feasibility: {'FEASIBLE' if is_feasible else 'INFEASIBLE'}")
        
        if self.feasibility_issues:
            print("\nCritical Issues:")
            for i, issue in enumerate(self.feasibility_issues, 1):
                print(f"  {i}. {issue}")
        
        if self.warnings:
            print("\nWarnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
                
        if is_feasible and not self.warnings:
            print("\nNo issues detected. The problem appears to be feasible.")
