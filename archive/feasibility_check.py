"""
Feasibility Checking Module for Waffle Production Optimization.

This module checks if the optimization problem is likely to be feasible
based on the input data from WaffleDemand.xlsx and WafflePanCombinations.xlsx.
"""
from typing import Dict, List, Any


class FeasibilityChecker:
    def __init__(self, data: Dict):
        """
        Initialize the feasibility checker.
        
        Args:
            data: Dictionary containing data for feasibility checks
        """
        # Validate required keys
        required_keys = ['waffle_types', 'pan_types', 'weeks', 'demand', 'supply', 'allowed']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise ValueError(f"Missing required keys in data: {missing_keys}")
        
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
        
        try:
            # Check for waffle types with compatible pans available before demand is scheduled
            self._check_waffle_compatibility_timing()
            
            # Check if cumulative demand can be met with available pan supply
            self._check_cumulative_demand_feasibility()
            
            # Return True if no critical issues found
            return len(self.feasibility_issues) == 0
            
        except Exception as e:
            raise
    
    def _check_waffle_compatibility_timing(self) -> None:
        """
        Check if each waffle type in demand has at least one compatible pan type
        and that the pan is available at least one week before the demand is scheduled.
        """
        try:
            # Get the data with fallbacks
            waffle_types = self.data.get('waffle_types', [])
            pan_types = self.data.get('pan_types', [])
            weeks = sorted(self.data.get('weeks', []))  # Sort weeks chronologically
            demand = self.data.get('demand', {})
            supply = self.data.get('supply', {})
            allowed = self.data.get('allowed', {})
            
            if not isinstance(allowed, dict):
                allowed = {}
            
            # First check: For each waffle in demand, check if it has compatible pans
            waffles_in_demand = set(w for w, _ in demand.keys())
            
            for waffle in waffles_in_demand:
                compatible_pans = [p for p in pan_types if allowed.get((waffle, p), False)]
                
                if not compatible_pans:
                    self.feasibility_issues.append(
                        f"BOTTLENECK: Waffle type '{waffle}' has no compatible pan types in the compatibility matrix."
                    )
                    continue
                
                # Second check: For each week with demand, check if compatible pans are available in earlier weeks
                for week in weeks:
                    if (waffle, week) in demand and demand[(waffle, week)] > 0:
                        # Check if any compatible pan is available before this week
                        pan_available_before = False
                        earliest_pan_week = None
                        available_pan_types = []
                        
                        for p in compatible_pans:
                            for w in [w for w in weeks if w < week]:  # Only check earlier weeks
                                if (p, w) in supply and supply[(p, w)] > 0:
                                    pan_available_before = True
                                    if earliest_pan_week is None or w < earliest_pan_week:
                                        earliest_pan_week = w
                                    if p not in available_pan_types:
                                        available_pan_types.append(p)
                        
                        if not pan_available_before:
                            self.feasibility_issues.append(
                                f"BOTTLENECK: Waffle '{waffle}' has demand of {demand[(waffle, week)]} in week {week}, "
                                f"but no compatible pan is available in any earlier week."
                            )

        except Exception as e:
            self.feasibility_issues.append(f"Error checking waffle compatibility with timing: {str(e)}")
    
    def _check_cumulative_demand_feasibility(self) -> None:
        """
        Check if the cumulative demand of each waffle type can be met with available compatible pan supply,
        considering the time-dependent nature of both demand and supply.
        """
        try:
            # Get data with fallbacks
            waffle_types = self.data.get('waffle_types', [])
            pan_types = self.data.get('pan_types', [])
            weeks = sorted(self.data.get('weeks', []))  # Sort weeks chronologically
            demand = self.data.get('demand', {})
            supply = self.data.get('supply', {})
            allowed = self.data.get('allowed', {})
            
            # Track cumulative values per waffle type
            cumulative_status = {}  # {waffle_type: {week: (cum_demand, cum_supply)}}
            
            # For each waffle type
            for waffle in set(w for w, _ in demand.keys()):
                compatible_pans = [p for p in pan_types if allowed.get((waffle, p), False)]
                if not compatible_pans:
                    continue  # Already handled by compatibility check
                    
                cum_demand = 0
                cum_supply = 0
                cumulative_status[waffle] = {}
                
                # Calculate running totals for each week
                for week in weeks:
                    # Add this week's demand
                    cum_demand += demand.get((waffle, week), 0)
                    
                    # Add this week's compatible pan supply
                    week_supply = sum(supply.get((p, week), 0) for p in compatible_pans)
                    cum_supply += week_supply
                    
                    cumulative_status[waffle][week] = (cum_demand, cum_supply)
                    
                    # Check if running short
                    if cum_supply < cum_demand:
                        self.feasibility_issues.append(
                            f"BOTTLENECK: Waffle '{waffle}' - Cumulative shortage in week {week}:\n"
                            f"  - Cumulative demand up to week {week}: {cum_demand}\n"
                            f"  - Cumulative available compatible pan supply: {cum_supply}\n"
                            f"  - Current shortage: {cum_demand - cum_supply}"
                        )
            
            # Generate summary report
            self._generate_supply_shortage_summary(cumulative_status)
                    
        except Exception as e:
            self.feasibility_issues.append(f"Error checking cumulative demand feasibility: {str(e)}")

    def _generate_supply_shortage_summary(self, cumulative_status: Dict) -> None:
        """
        Generate a clear summary of supply shortages.
        """
        summary = []
        summary.append("\nSupply Shortage Summary:")
        
        has_shortages = False
        for waffle, week_status in cumulative_status.items():
            shortages = []
            for week, (cum_demand, cum_supply) in week_status.items():
                if cum_supply < cum_demand:
                    has_shortages = True
                    shortages.append({
                        'week': week,
                        'shortage': cum_demand - cum_supply,
                        'cum_demand': cum_demand,
                        'cum_supply': cum_supply
                    })
            
            if shortages:
                summary.append(f"\nWaffle '{waffle}':")
                for shortage in shortages:
                    summary.append(
                        f"  Week {shortage['week']}: Short by {shortage['shortage']} pans "
                        f"(Cumulative Demand: {shortage['cum_demand']}, "
                        f"Cumulative Supply: {shortage['cum_supply']})"
                    )
        
        if has_shortages:
            self.warnings.append('\n'.join(summary))
    
    def get_result_summary(self) -> Dict:
        """
        Get a summary of the feasibility check results.
        
        Returns:
            Dict: Dictionary containing feasibility check results
        """
        is_feasible = len(self.feasibility_issues) == 0
        
        # Create result summary with all necessary visualization data
        result = {
            'is_feasible': is_feasible,
            'issues': self.feasibility_issues,
            'warnings': self.warnings
        }
        
        # Add original data needed for visualization
        required_keys = [
            'waffle_types', 'pan_types', 'weeks', 'demand', 'supply', 'allowed'
        ]
        
        # Add all available keys from the original data
        for key in required_keys:
            if key in self.data:
                result[key] = self.data[key]
        
        return result
    
    def print_report(self) -> None:
        """Print a detailed feasibility report."""
        is_feasible = len(self.feasibility_issues) == 0
        
        print("\n=== Feasibility Check Report ===")
        print(f"Overall feasibility: {'LIKELY FEASIBLE' if is_feasible else 'INFEASIBLE'}")
        
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
