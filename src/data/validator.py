"""
Data Validation Module for Waffle Production Optimization.

This module provides classes and functions for validating optimization data and results.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

class DataValidator:
    """
    Class for validating optimization data and feasibility.
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the data validator.
        
        Args:
            debug_mode: If True, enables debug output
        """
        self.debug_mode = debug_mode
        
    def _debug_print(self, message: str) -> None:
        """
        Print debug message if debug mode is enabled.
        
        Args:
            message: Debug message to print
        """
        if self.debug_mode:
            print(message)
    
    def check_basic_feasibility(self, data: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Perform basic feasibility checks on the optimization data.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            Tuple[bool, List[str], List[str]]: (is_feasible, list of critical issues, list of warnings)
        """
        critical_issues = []
        warnings = []
        
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        supply = data.get('supply', {})
        wpp = data.get('wpp', {})
        allowed = data.get('allowed', {})
        
        # Check if any waffle types, pan types, or weeks are missing
        if not waffle_types:
            critical_issues.append("No waffle types found.")
        if not pan_types:
            critical_issues.append("No pan types found.")
        if not weeks:
            critical_issues.append("No weeks found.")
        
        # Check if there is any demand data
        if not demand:
            critical_issues.append("No demand data found.")
        
        # Check if there is any supply data
        if not supply:
            critical_issues.append("No supply data found.")
        
        # Check if there is any waffles per pan data
        if not wpp:
            critical_issues.append("No waffles per pan data found.")
        
        # Check if there is any allowed combinations data
        if not allowed:
            critical_issues.append("No allowed combinations data found.")
        
        # Check if all waffle types have corresponding wpp values
        for w in waffle_types:
            if w not in wpp:
                critical_issues.append(f"Waffle type '{w}' is missing a waffles per pan value.")
        
        # Check if all waffle types have at least one allowed pan type
        for w in waffle_types:
            has_allowed_pan = False
            for p in pan_types:
                if allowed.get((w, p), False):
                    has_allowed_pan = True
                    break
            if not has_allowed_pan:
                critical_issues.append(f"Waffle type '{w}' has no allowed pan types.")
        
        # Check if each pan type is used for at least one waffle type
        for p in pan_types:
            has_allowed_waffle = False
            for w in waffle_types:
                if allowed.get((w, p), False):
                    has_allowed_waffle = True
                    break
            if not has_allowed_waffle:
                warnings.append(f"Pan type '{p}' is not used for any waffle type.")
        
        # Check for unsatisfiable demand (no allowed combinations)
        for (w, t), d in demand.items():
            if w in waffle_types and t in weeks:
                has_allowed_pan = False
                for p in pan_types:
                    if allowed.get((w, p), False):
                        has_allowed_pan = True
                        break
                if not has_allowed_pan:
                    critical_issues.append(f"Demand for waffle type '{w}' in week '{t}' cannot be satisfied (no allowed pan types).")
        
        # Check if there is any supply for each pan type with demand
        used_pan_types = set()
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand and demand[(w, t)] > 0:
                    for p in pan_types:
                        if allowed.get((w, p), False):
                            used_pan_types.add(p)
        
        for p in used_pan_types:
            total_supply = sum(supply.get((p, t), 0) for t in weeks)
            if total_supply <= 0:
                critical_issues.append(f"Pan type '{p}' is needed but has no supply.")
        
        # Calculate total theoretical capacity per waffle type
        total_capacity = {}
        for w in waffle_types:
            total_capacity[w] = 0
            for p in pan_types:
                if allowed.get((w, p), False):
                    for t in weeks:
                        if (p, t) in supply:
                            total_capacity[w] += supply[(p, t)] * wpp.get(w, 0)
        
        # Compare total capacity to total demand
        for w in waffle_types:
            total_demand = sum(demand.get((w, t), 0) for t in weeks)
            if total_demand > total_capacity.get(w, 0):
                critical_issues.append(f"Total demand for waffle type '{w}' ({total_demand}) exceeds maximum theoretical capacity ({total_capacity.get(w, 0)}).")
                
        # Check if total theoretical demand exceeds total theoretical capacity
        total_all_demand = sum(demand.values())
        total_all_capacity = sum(
            supply.get((p, t), 0) * wpp.get(w, 0)
            for p in pan_types
            for t in weeks
            for w in waffle_types
            if allowed.get((w, p), False) and (p, t) in supply
        )
        if total_all_demand > total_all_capacity:
            critical_issues.append(f"Total demand ({total_all_demand}) exceeds maximum theoretical capacity ({total_all_capacity}).")
                
        # Check the result
        is_feasible = len(critical_issues) == 0
        return is_feasible, critical_issues, warnings
    
    def check_weekly_feasibility(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Check feasibility on a weekly basis.
        
        Args:
            data: Dictionary containing optimization data
            
        Returns:
            Tuple[bool, List[str]]: (is_feasible, list of issues)
        """
        issues = []
        
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        supply = data.get('supply', {})
        wpp = data.get('wpp', {})
        allowed = data.get('allowed', {})
        
        # Check weekly feasibility
        for t in weeks:
            # Calculate weekly demand per waffle type
            weekly_demand = {}
            for w in waffle_types:
                if (w, t) in demand:
                    weekly_demand[w] = demand[(w, t)]
            
            # Calculate weekly supply per pan type
            weekly_supply = {}
            for p in pan_types:
                if (p, t) in supply:
                    weekly_supply[p] = supply[(p, t)]
            
            # Check if all pans were used in previous weeks
            # Assume carry-over is allowed for this basic check
            
            # Calculate total weekly capacity per waffle type
            weekly_capacity = {}
            for w in waffle_types:
                weekly_capacity[w] = 0
                for p in pan_types:
                    if allowed.get((w, p), False) and p in weekly_supply:
                        weekly_capacity[w] += weekly_supply[p] * wpp.get(w, 0)
            
            # Compare weekly capacity to weekly demand
            for w in waffle_types:
                if w in weekly_demand and weekly_demand[w] > weekly_capacity.get(w, 0):
                    issues.append(f"Week {t}: Demand for waffle type '{w}' ({weekly_demand[w]}) exceeds maximum theoretical capacity ({weekly_capacity.get(w, 0)}).")
        
        # Check the result
        is_feasible = len(issues) == 0
        return is_feasible, issues
    
    def check_solution_feasibility(self, data: Dict, solution: Dict) -> Tuple[bool, List[str]]:
        """
        Check if a given solution is feasible.
        
        Args:
            data: Dictionary containing optimization data
            solution: Dictionary containing solution variables
            
        Returns:
            Tuple[bool, List[str]]: (is_feasible, list of issues)
        """
        issues = []
        
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        supply = data.get('supply', {})
        wpp = data.get('wpp', {})
        allowed = data.get('allowed', {})
        
        # Extract solution variables
        variables = solution.get('variables', {})
        
        # Check if all variables represent valid waffle-pan-week combinations
        for (w, p, t), value in variables.items():
            if w not in waffle_types:
                issues.append(f"Variable includes invalid waffle type: {w}")
            if p not in pan_types:
                issues.append(f"Variable includes invalid pan type: {p}")
            if t not in weeks:
                issues.append(f"Variable includes invalid week: {t}")
            if not allowed.get((w, p), False):
                issues.append(f"Variable uses disallowed combination: waffle '{w}' on pan '{p}'")
        
        # Check if all values are non-negative integers
        for (w, p, t), value in variables.items():
            if not isinstance(value, (int, float)) or value < 0:
                issues.append(f"Variable x_{w}_{p}_{t} has invalid value: {value}")
            if isinstance(value, float) and not value.is_integer():
                issues.append(f"Variable x_{w}_{p}_{t} has non-integer value: {value}")
        
        # Check demand satisfaction
        production = {}
        for (w, p, t), value in variables.items():
            if w in waffle_types and p in pan_types and t in weeks:
                if (w, t) not in production:
                    production[(w, t)] = 0
                production[(w, t)] += value * wpp.get(w, 0)
        
        for (w, t), d in demand.items():
            if (w, t) not in production:
                if d > 0:
                    issues.append(f"No production for waffle type '{w}' in week '{t}' (demand: {d})")
            elif production[(w, t)] < d:
                issues.append(f"Production of waffle type '{w}' in week '{t}' ({production[(w, t)]}) is less than demand ({d})")
        
        # Check supply constraints
        usage = {}
        for (w, p, t), value in variables.items():
            if w in waffle_types and p in pan_types and t in weeks:
                if (p, t) not in usage:
                    usage[(p, t)] = 0
                usage[(p, t)] += value
        
        # Check weekly supply constraints
        for p in pan_types:
            for t in weeks:
                if (p, t) in usage and (p, t) in supply:
                    if usage[(p, t)] > supply[(p, t)]:
                        issues.append(f"Usage of pan type '{p}' in week '{t}' ({usage[(p, t)]}) exceeds supply ({supply[(p, t)]})")
        
        # Check cumulative supply constraints (accounting for carry-over)
        for p in pan_types:
            cumulative_supply = 0
            cumulative_usage = 0
            for t in sorted(weeks):
                cumulative_supply += supply.get((p, t), 0)
                for w in waffle_types:
                    cumulative_usage += variables.get((w, p, t), 0)
                if cumulative_usage > cumulative_supply:
                    issues.append(f"Cumulative usage of pan type '{p}' up to week '{t}' ({cumulative_usage}) exceeds cumulative supply ({cumulative_supply})")
        
        # Check the result
        is_feasible = len(issues) == 0
        return is_feasible, issues
    
    def validate_solution(self, data: Dict, solution: Dict) -> Dict:
        """
        Validate a solution and return validation metrics.
        
        Args:
            data: Dictionary containing optimization data
            solution: Dictionary containing solution variables
            
        Returns:
            Dict: Dictionary containing validation metrics
        """
        # Check basic solution feasibility
        is_feasible, critical_issues, warnings = self.check_basic_feasibility(data)
        
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        supply = data.get('supply', {})
        wpp = data.get('wpp', {})
        allowed = data.get('allowed', {})
        cost = data.get('cost', {})
        
        # Extract solution variables
        variables = solution.get('variables', {})
        
        # Calculate total production per waffle type and week
        production = {}
        for (w, p, t), value in variables.items():
            if (w, t) not in production:
                production[(w, t)] = 0
            production[(w, t)] += value * wpp.get(w, 0)
        
        # Calculate total production per waffle type
        total_production = {}
        for (w, t), value in production.items():
            if w not in total_production:
                total_production[w] = 0
            total_production[w] += value
        
        # Calculate total cost per waffle type
        total_cost = {}
        for (w, p, t), value in variables.items():
            if w not in total_cost:
                total_cost[w] = 0
            total_cost[w] += value * wpp.get(w, 0) * cost.get((w, p), 0)
        
        # Calculate total demand per waffle type
        total_demand = {}
        for (w, t), value in demand.items():
            if w not in total_demand:
                total_demand[w] = 0
            total_demand[w] += value
        
        # Calculate total pan usage per pan type
        total_usage = {}
        for (w, p, t), value in variables.items():
            if p not in total_usage:
                total_usage[p] = 0
            total_usage[p] += value
        
        # Calculate total supply per pan type
        total_supply = {}
        for (p, t), value in supply.items():
            if p not in total_supply:
                total_supply[p] = 0
            total_supply[p] += value
        
        # Calculate pan utilization rates
        utilization = {}
        for p in pan_types:
            if p in total_supply and total_supply[p] > 0:
                utilization[p] = total_usage.get(p, 0) / total_supply[p] * 100
            else:
                utilization[p] = 0.0
        
        # Calculate demand satisfaction rates
        satisfaction = {}
        for w in waffle_types:
            if w in total_demand and total_demand[w] > 0:
                satisfaction[w] = min(total_production.get(w, 0) / total_demand[w] * 100, 100.0)
            else:
                satisfaction[w] = 100.0  # No demand means 100% satisfaction
        
        # Calculate average cost per waffle
        avg_cost = {}
        for w in waffle_types:
            if w in total_production and total_production[w] > 0:
                avg_cost[w] = total_cost.get(w, 0) / total_production[w]
            else:
                avg_cost[w] = 0.0
        
        # Calculate surplus (production above demand)
        surplus = {}
        for w in waffle_types:
            surplus[w] = max(0, total_production.get(w, 0) - total_demand.get(w, 0))
        
        # Return validation metrics
        return {
            'is_feasible': is_feasible,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'production': production,
            'total_production': total_production,
            'total_cost': total_cost,
            'total_demand': total_demand,
            'total_usage': total_usage,
            'total_supply': total_supply,
            'utilization': utilization,
            'satisfaction': satisfaction,
            'avg_cost': avg_cost,
            'surplus': surplus
        } 