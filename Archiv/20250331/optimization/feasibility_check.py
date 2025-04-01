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
        # Debug logging
        print("\nDebug: Initializing FeasibilityChecker")
        print(f"Debug: Received data keys: {list(data.keys())}")
        
        # Validate required keys
        required_keys = ['waffle_types', 'pan_types', 'weeks', 'demand', 'supply', 
                        'cost', 'wpp', 'allowed', 'total_demand', 'total_supply']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise ValueError(f"Missing required keys in data: {missing_keys}")
        
        self.data = data
        self.feasibility_issues = []
        self.warnings = []
        
        # Debug logging
        print("Debug: FeasibilityChecker initialized successfully")
        
    def check_feasibility(self) -> bool:
        """
        Check if the optimization problem appears to be feasible.
        
        Returns:
            bool: True if the problem appears feasible, False otherwise
        """
        print("\nDebug: Starting feasibility check")
        self.feasibility_issues = []
        self.warnings = []
        
        try:
            # Check total supply vs. demand
            print("Debug: Checking total supply vs. demand")
            self._check_total_supply()
            
            # Check for waffle types with no compatible pans
            print("Debug: Checking waffle compatibility")
            self._check_waffle_compatibility()
            
            # Check week-by-week supply vs. demand
            print("Debug: Checking weekly supply")
            self._check_weekly_supply()
            
            # Check if production capacity is sufficient
            print("Debug: Checking production capacity")
            self._check_waffle_production_capacity()
            
            # Check compatibility-constrained supply vs. demand
            print("Debug: Checking compatibility-constrained supply vs. demand")
            self._check_compatibility_constrained_supply()
            
            # Return True if no critical issues found
            is_feasible = len(self.feasibility_issues) == 0
            print(f"Debug: Feasibility check completed. Feasible: {is_feasible}")
            return is_feasible
            
        except Exception as e:
            print(f"Debug: Error during feasibility check: {str(e)}")
            raise
    
    def _check_total_supply(self) -> None:
        """Check if total pan supply is sufficient for total demand."""
        try:
            print("Debug: Starting total supply check")
            
            # Check if total_demand and total_supply exist and are dictionaries
            if 'total_demand' not in self.data:
                raise ValueError("Missing 'total_demand' key in data dictionary")
            if 'total_supply' not in self.data:
                raise ValueError("Missing 'total_supply' key in data dictionary")
                
            print(f"Debug: total_demand type: {type(self.data['total_demand'])}")
            print(f"Debug: total_supply type: {type(self.data['total_supply'])}")
            print(f"Debug: total_demand values: {self.data['total_demand']}")
            print(f"Debug: total_supply values: {self.data['total_supply']}")
            
            # Convert to empty dict if they're not dictionaries
            total_demand = self.data['total_demand'] if isinstance(self.data['total_demand'], dict) else {}
            total_supply = self.data['total_supply'] if isinstance(self.data['total_supply'], dict) else {}
            
            # Ensure all values are numeric
            for week, value in list(total_demand.items()):
                if not isinstance(value, (int, float)):
                    print(f"Debug: Invalid demand value for week {week}: {value}, setting to 0")
                    total_demand[week] = 0
                    
            for week, value in list(total_supply.items()):
                if not isinstance(value, (int, float)):
                    print(f"Debug: Invalid supply value for week {week}: {value}, setting to 0")
                    total_supply[week] = 0
            
            # Now sum the values safely
            total_demand_value = sum(total_demand.values())
            total_supply_value = sum(total_supply.values())
            
            print(f"Debug: Total demand: {total_demand_value}, Total supply: {total_supply_value}")
            
            # Check if supply is sufficient
            if total_supply_value < total_demand_value:
                self.feasibility_issues.append(
                    f"Insufficient total pan supply: {total_supply_value} pans available, "
                    f"but {total_demand_value} pans required for demand."
                )
            elif total_supply_value < total_demand_value * 1.1:  # 10% margin
                self.warnings.append(
                    f"Supply is tight: only {total_supply_value} pans available for "
                    f"{total_demand_value} pans demand (less than 10% margin)."
                )
                
        except Exception as e:
            print(f"Debug: Error in _check_total_supply: {str(e)}")
            self.feasibility_issues.append(f"Error checking total supply: {str(e)}")
    
    def _check_waffle_compatibility(self) -> None:
        """Check if each waffle type has at least one compatible pan type."""
        try:
            print("Debug: Starting waffle compatibility check")
            
            # Get the data with fallbacks
            waffle_types = self.data.get('waffle_types', [])
            pan_types = self.data.get('pan_types', [])
            allowed = self.data.get('allowed', {})
            
            if not isinstance(allowed, dict):
                print("Debug: allowed is not a dictionary, using empty dict")
                allowed = {}
            
            for waffle in waffle_types:
                compatible_pans = [p for p in pan_types if allowed.get((waffle, p), False)]
                print(f"Debug: Waffle {waffle} has {len(compatible_pans)} compatible pans")
                
                if not compatible_pans:
                    self.feasibility_issues.append(
                        f"Waffle type '{waffle}' has no compatible pan types."
                    )
                    
        except Exception as e:
            print(f"Debug: Error in _check_waffle_compatibility: {str(e)}")
            self.feasibility_issues.append(f"Error checking waffle compatibility: {str(e)}")
    
    def _check_weekly_supply(self) -> None:
        """Check if weekly pan supply is sufficient for weekly demand."""
        try:
            print("Debug: Starting weekly supply check")
            
            # Get the data, with fallbacks for missing keys
            weeks = self.data.get('weeks', [])
            total_demand = self.data.get('total_demand', {})
            total_supply = self.data.get('total_supply', {})
            
            if not isinstance(total_demand, dict):
                print("Debug: total_demand is not a dictionary, using empty dict")
                total_demand = {}
                
            if not isinstance(total_supply, dict):
                print("Debug: total_supply is not a dictionary, using empty dict")
                total_supply = {}
            
            cumulative_demand = 0
            cumulative_supply = 0
            
            for week in weeks:
                # Get values with fallback to 0 for missing weeks
                week_demand = total_demand.get(week, 0)
                week_supply = total_supply.get(week, 0)
                
                # Ensure values are numeric
                if not isinstance(week_demand, (int, float)):
                    print(f"Debug: Non-numeric demand for week {week}: {week_demand}, using 0")
                    week_demand = 0
                    
                if not isinstance(week_supply, (int, float)):
                    print(f"Debug: Non-numeric supply for week {week}: {week_supply}, using 0")
                    week_supply = 0
                
                cumulative_demand += week_demand
                cumulative_supply += week_supply
                
                print(f"Debug: Week {week} - Demand: {week_demand}, Supply: {week_supply}")
                print(f"Debug: Cumulative - Demand: {cumulative_demand}, Supply: {cumulative_supply}")
                
                if cumulative_supply < cumulative_demand:
                    self.feasibility_issues.append(
                        f"Insufficient cumulative supply by week {week}: "
                        f"{cumulative_supply} pans available, but {cumulative_demand} pans required."
                    )
                    
        except Exception as e:
            print(f"Debug: Error in _check_weekly_supply: {str(e)}")
            self.feasibility_issues.append(f"Error checking weekly supply: {str(e)}")
    
    def _check_waffle_production_capacity(self) -> None:
        """Check if there's enough production capacity given waffles-per-pan rates."""
        try:
            print("Debug: Starting waffle production capacity check")
            
            # Get required data with fallbacks for safety
            waffle_types = self.data.get('waffle_types', [])
            pan_types = self.data.get('pan_types', [])
            weeks = self.data.get('weeks', [])
            demand = self.data.get('demand', {})
            wpp = self.data.get('wpp', {})
            allowed = self.data.get('allowed', {})
            
            if not isinstance(wpp, dict):
                print("Debug: wpp is not a dictionary, using empty dict")
                wpp = {}
            
            if not isinstance(demand, dict):
                print("Debug: demand is not a dictionary, using empty dict")
                demand = {}
            
            if not isinstance(allowed, dict):
                print("Debug: allowed is not a dictionary, using empty dict")
                allowed = {}
            
            # Check each waffle type
            for waffle in waffle_types:
                waffle_capacity = wpp.get(waffle, 0)
                
                # Ensure value is numeric
                if not isinstance(waffle_capacity, (int, float)):
                    print(f"Debug: Non-numeric capacity for waffle {waffle}: {waffle_capacity}, using 0")
                    waffle_capacity = 0
                
                # Calculate total demand for this waffle type
                total_demand = 0
                for week in weeks:
                    week_demand = demand.get((waffle, week), 0)
                    if not isinstance(week_demand, (int, float)):
                        print(f"Debug: Non-numeric demand for waffle {waffle}, week {week}: {week_demand}, using 0")
                        week_demand = 0
                    total_demand += week_demand
                
                # Check if any compatible pans exist
                compatible_pans = [p for p in pan_types if allowed.get((waffle, p), False)]
                
                # Check if production capacity issues exist
                if waffle_capacity <= 0 and total_demand > 0:
                    self.feasibility_issues.append(
                        f"Waffle type '{waffle}' has demand of {total_demand} pans but production capacity "
                        f"is zero or negative ({waffle_capacity} waffles per pan)."
                    )
                
                # Check if demand can reasonably be satisfied with the capacity
                if waffle_capacity > 0 and len(compatible_pans) > 0 and total_demand > 0:
                    # Calculate the maximum theoretical production with all compatible pans
                    max_production = 0
                    for pan in compatible_pans:
                        # Sum up supply for this pan type across all weeks
                        pan_supply = sum(self.data.get('supply', {}).get((pan, week), 0) for week in weeks)
                        max_production += pan_supply * waffle_capacity
                    
                    # Check if maximum production capacity is significantly less than demand
                    total_waffle_demand = total_demand * waffle_capacity
                    if max_production < total_waffle_demand * 0.9:  # Less than 90% of demand
                        self.feasibility_issues.append(
                            f"Insufficient production capacity for waffle type '{waffle}': Maximum possible "
                            f"production is {max_production:.1f} waffles, but demand is {total_waffle_demand:.1f} waffles "
                            f"(only {max_production / total_waffle_demand * 100:.1f}% of demand can be met)."
                        )
                
        except Exception as e:
            print(f"Debug: Error in _check_waffle_production_capacity: {str(e)}")
            self.feasibility_issues.append(f"Error checking waffle production capacity: {str(e)}")
    
    def _check_compatibility_constrained_supply(self) -> None:
        """
        Check if there's enough compatible pan supply for each waffle type's demand by week.
        This is a more detailed check that considers waffle-pan compatibility constraints.
        """
        try:
            print("Debug: Starting compatibility-constrained supply check")
            
            # Get required data with fallbacks for safety
            waffle_types = self.data.get('waffle_types', [])
            pan_types = self.data.get('pan_types', [])
            weeks = self.data.get('weeks', [])
            demand = self.data.get('demand', {})
            supply = self.data.get('supply', {})
            allowed = self.data.get('allowed', {})
            wpp = self.data.get('wpp', {})
            
            # Track used pan supply to account for competition
            available_pan_supply = {week: {pan: 0 for pan in pan_types} for week in weeks}
            
            # Initialize available supply with original supply values
            for week in weeks:
                for pan in pan_types:
                    pan_supply = supply.get((pan, week), 0)
                    if not isinstance(pan_supply, (int, float)):
                        pan_supply = 0
                    available_pan_supply[week][pan] = pan_supply
            
            # Track waffle types with insufficient compatible supply by week
            insufficient_waffles = {}
            
            # Check each waffle type's demand against compatible pan supply
            for waffle in waffle_types:
                compatible_pans = [p for p in pan_types if allowed.get((waffle, p), False)]
                
                if not compatible_pans:
                    # Skip waffles with no compatible pans (already reported in _check_waffle_compatibility)
                    continue
                
                # Get waffles per pan for this waffle type
                waffle_capacity = wpp.get(waffle, 0)
                if not isinstance(waffle_capacity, (int, float)) or waffle_capacity <= 0:
                    continue  # Skip if invalid capacity (already reported in _check_waffle_production_capacity)
                
                for week in weeks:
                    # Get demand for this waffle in this week
                    waffle_demand = demand.get((waffle, week), 0)
                    if not isinstance(waffle_demand, (int, float)) or waffle_demand <= 0:
                        continue  # Skip if no demand
                    
                    # Calculate how many pans we need for this waffle's demand
                    pans_needed = waffle_demand / waffle_capacity
                    
                    # Check if compatible pans have enough supply
                    total_compatible_supply = sum(available_pan_supply[week][pan] for pan in compatible_pans)
                    
                    if total_compatible_supply < pans_needed:
                        # Record the shortage
                        if waffle not in insufficient_waffles:
                            insufficient_waffles[waffle] = []
                        
                        deficit_percentage = (pans_needed - total_compatible_supply) / pans_needed * 100
                        insufficient_waffles[waffle].append({
                            'week': week,
                            'pans_needed': pans_needed,
                            'compatible_supply': total_compatible_supply,
                            'deficit_percentage': deficit_percentage
                        })
                        
                        # Don't allocate supply here since this is just a check, not the actual allocation
            
            # Report issues for waffles with insufficient compatible supply
            for waffle, deficits in insufficient_waffles.items():
                # Group consecutive weeks for more concise reporting
                grouped_deficits = self._group_consecutive_weeks(deficits)
                
                for group in grouped_deficits:
                    if len(group) == 1:
                        deficit = group[0]
                        self.feasibility_issues.append(
                            f"Insufficient compatible pan supply for waffle '{waffle}' in week {deficit['week']}: "
                            f"Need {deficit['pans_needed']:.1f} pans but only {deficit['compatible_supply']:.1f} "
                            f"compatible pans available ({deficit['deficit_percentage']:.1f}% shortage)."
                        )
                    else:
                        # Report a range of weeks
                        start_week = group[0]['week']
                        end_week = group[-1]['week']
                        avg_deficit = sum(d['deficit_percentage'] for d in group) / len(group)
                        
                        self.feasibility_issues.append(
                            f"Insufficient compatible pan supply for waffle '{waffle}' in weeks {start_week}-{end_week}: "
                            f"Average {avg_deficit:.1f}% shortage of compatible pans."
                        )
        
        except Exception as e:
            print(f"Debug: Error in _check_compatibility_constrained_supply: {str(e)}")
            self.feasibility_issues.append(f"Error checking compatibility-constrained supply: {str(e)}")
    
    def _group_consecutive_weeks(self, deficits: List[Dict]) -> List[List[Dict]]:
        """Group consecutive weeks for more concise reporting."""
        if not deficits:
            return []
        
        # Sort deficits by week
        sorted_deficits = sorted(deficits, key=lambda d: str(d['week']))
        
        groups = []
        current_group = [sorted_deficits[0]]
        
        for i in range(1, len(sorted_deficits)):
            current_deficit = sorted_deficits[i]
            last_deficit = current_group[-1]
            
            # Try to extract week numbers for comparison
            try:
                current_week = str(current_deficit['week'])
                last_week = str(last_deficit['week'])
                
                # Extract numeric part if week format is "Week X"
                if "Week" in current_week and "Week" in last_week:
                    current_num = int(current_week.split(' ')[-1])
                    last_num = int(last_week.split(' ')[-1])
                    
                    if current_num == last_num + 1:
                        # Consecutive weeks
                        current_group.append(current_deficit)
                    else:
                        # Non-consecutive, start a new group
                        groups.append(current_group)
                        current_group = [current_deficit]
                else:
                    # If not in "Week X" format, compare as strings
                    if current_week != last_week:
                        groups.append(current_group)
                        current_group = [current_deficit]
                    else:
                        current_group.append(current_deficit)
            except:
                # If we can't parse week numbers, treat as non-consecutive
                groups.append(current_group)
                current_group = [current_deficit]
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
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
            'waffle_types', 'pan_types', 'weeks', 'demand', 'supply', 
            'cost', 'wpp', 'allowed', 'total_demand', 'total_supply'
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
