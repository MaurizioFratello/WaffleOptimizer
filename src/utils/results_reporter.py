"""
Results Reporting Module for Waffle Production Optimization.

This module provides functions for reporting and exporting optimization results.
"""
import pandas as pd
from typing import Dict, List, Tuple, Any

class ResultsReporter:
    """
    Class for reporting and exporting optimization results.
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the results reporter.
        
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
            
    def print_summary(self, solution: Dict) -> None:
        """
        Print a summary of the optimization results.
        
        Args:
            solution: Dictionary containing solution information
        """
        # Check if the solution is available
        if not solution or 'variables' not in solution:
            print("No solution available.")
            return
            
        # Print solution status
        print(f"\nSolution Status: {solution.get('status', 'Unknown')}")
        
        # Print objective value
        if 'objective_value' in solution:
            print(f"Objective Value: {solution['objective_value']:.2f}")
            
        # Print solution time
        if 'solution_time' in solution:
            print(f"Solution Time: {solution['solution_time']:.2f} seconds")
            
        # Print metrics if available
        if 'metrics' in solution:
            metrics = solution['metrics']
            print("\nMetrics:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"- {key}: {value:.2f}")
                else:
                    print(f"- {key}: {value}")
                    
        # Print variable count
        if 'variables' in solution:
            print(f"\nNumber of Variables: {len(solution['variables'])}")
            
    def print_detailed_results(self, data: Dict, solution: Dict, validation: Dict = None) -> None:
        """
        Print detailed results of the optimization.
        
        Args:
            data: Dictionary containing optimization data
            solution: Dictionary containing solution information
            validation: Optional dictionary containing validation metrics
        """
        # Check if the solution is available
        if not solution or 'variables' not in solution:
            print("No solution available.")
            return
            
        # Print solution status
        print(f"\nSolution Status: {solution.get('status', 'Unknown')}")
        print(f"Model Type: {solution.get('model_type', 'Unknown')}")
        
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        wpp = data.get('wpp', {})
        
        # Extract solution variables
        variables = solution.get('variables', {})
        
        # Calculate production by waffle type and week
        production = {}
        for (w, p, t), value in variables.items():
            if (w, t) not in production:
                production[(w, t)] = 0
            production[(w, t)] += value * wpp.get(w, 0)
            
        # Print demand vs. production by waffle type and week
        print("\nDemand vs. Production:")
        print(f"{'Waffle Type':<15} {'Week':<10} {'Demand':<10} {'Production':<15} {'Diff':<10}")
        print("-" * 60)
        
        for w in waffle_types:
            for t in weeks:
                if (w, t) in demand or (w, t) in production:
                    d = demand.get((w, t), 0)
                    p = production.get((w, t), 0)
                    diff = p - d
                    diff_str = f"{diff:+.0f}"
                    print(f"{w:<15} {t:<10} {d:<10.0f} {p:<15.0f} {diff_str:<10}")
                    
        # Print pan usage by pan type, waffle type, and week
        print("\nPan Usage:")
        print(f"{'Pan Type':<12} {'Waffle Type':<15} {'Week':<10} {'Usage':<10}")
        print("-" * 50)
        
        for (w, p, t), value in sorted(variables.items()):
            if value > 0:
                print(f"{p:<12} {w:<15} {t:<10} {value:<10.0f}")
                
        # Print summary statistics by waffle type
        print("\nSummary by Waffle Type:")
        print(f"{'Waffle Type':<15} {'Total Demand':<15} {'Total Production':<20} {'Satisfaction %':<15}")
        print("-" * 70)
        
        for w in waffle_types:
            total_demand = sum(demand.get((w, t), 0) for t in weeks)
            total_production = sum(production.get((w, t), 0) for t in weeks)
            if total_demand > 0:
                satisfaction = min(total_production / total_demand * 100, 100.0)
            else:
                satisfaction = 100.0
            print(f"{w:<15} {total_demand:<15.0f} {total_production:<20.0f} {satisfaction:<15.2f}%")
            
        # Print objective value and solution time
        if 'objective_value' in solution:
            print(f"\nObjective Value: {solution['objective_value']:.2f}")
            
        if 'solution_time' in solution:
            print(f"Solution Time: {solution['solution_time']:.2f} seconds")
            
        # Print validation results if available
        if validation:
            print("\nValidation Results:")
            print(f"Feasible: {validation.get('is_feasible', False)}")
            
            issues = validation.get('issues', [])
            if issues:
                print("\nIssues:")
                for issue in issues:
                    print(f"- {issue}")
                    
            # Print utilization rates
            if 'utilization' in validation:
                print("\nPan Utilization Rates:")
                print(f"{'Pan Type':<12} {'Utilization %':<15}")
                print("-" * 30)
                
                for p, rate in sorted(validation['utilization'].items()):
                    print(f"{p:<12} {rate:<15.2f}%")
                    
            # Print average costs
            if 'avg_cost' in validation:
                print("\nAverage Cost per Waffle:")
                print(f"{'Waffle Type':<15} {'Avg Cost':<15}")
                print("-" * 30)
                
                for w, cost in sorted(validation['avg_cost'].items()):
                    print(f"{w:<15} {cost:<15.4f}")
    
    def export_to_excel(self, data: Dict, solution: Dict, file_path: str) -> None:
        """
        Export solution to Excel file.
        
        Args:
            data: Dictionary containing optimization data
            solution: Dictionary containing solution information
            file_path: Path to the output Excel file
        """
        # Check if the solution is available
        if not solution or 'variables' not in solution:
            print("No solution available to export.")
            return
            
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        supply = data.get('supply', {})
        wpp = data.get('wpp', {})
        cost = data.get('cost', {})
        
        # Extract solution variables
        variables = solution.get('variables', {})
        
        # Create Excel writer
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Create summary sheet
            summary_data = {
                'Model Type': [solution.get('model_type', 'Unknown')],
                'Status': [solution.get('status', 'Unknown')],
                'Objective Value': [solution.get('objective_value', 0)],
                'Solution Time (s)': [solution.get('solution_time', 0)]
            }
            
            # Add metrics if available
            if 'metrics' in solution:
                for key, value in solution['metrics'].items():
                    summary_data[key] = [value]
                    
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create production plan sheet
            plan_data = []
            for (w, p, t), value in variables.items():
                if value > 0:
                    output = value * wpp.get(w, 0)
                    plan_cost = value * wpp.get(w, 0) * cost.get((w, p), 0)
                    plan_data.append({
                        'Waffle Type': w,
                        'Pan Type': p,
                        'Week': t,
                        'Pans Used': value,
                        'Waffles Produced': output,
                        'Cost': plan_cost
                    })
                    
            if plan_data:
                plan_df = pd.DataFrame(plan_data)
                plan_df.to_excel(writer, sheet_name='Production Plan', index=False)
                
            # Create demand vs. production sheet
            comparison_data = []
            for w in waffle_types:
                for t in weeks:
                    d = demand.get((w, t), 0)
                    
                    # Calculate production for this waffle type and week
                    p = 0
                    for p_type in pan_types:
                        p += variables.get((w, p_type, t), 0) * wpp.get(w, 0)
                        
                    comparison_data.append({
                        'Waffle Type': w,
                        'Week': t,
                        'Demand': d,
                        'Production': p,
                        'Difference': p - d
                    })
                    
            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)
                comparison_df.to_excel(writer, sheet_name='Demand vs Production', index=False)
                
            # Create summary by waffle type sheet
            waffle_summary_data = []
            for w in waffle_types:
                total_demand = sum(demand.get((w, t), 0) for t in weeks)
                
                # Calculate total production for this waffle type
                total_production = 0
                total_cost = 0
                for p in pan_types:
                    for t in weeks:
                        pans_used = variables.get((w, p, t), 0)
                        total_production += pans_used * wpp.get(w, 0)
                        total_cost += pans_used * wpp.get(w, 0) * cost.get((w, p), 0)
                        
                if total_demand > 0:
                    satisfaction = min(total_production / total_demand * 100, 100.0)
                else:
                    satisfaction = 100.0
                    
                if total_production > 0:
                    avg_cost = total_cost / total_production
                else:
                    avg_cost = 0.0
                    
                waffle_summary_data.append({
                    'Waffle Type': w,
                    'Total Demand': total_demand,
                    'Total Production': total_production,
                    'Satisfaction (%)': satisfaction,
                    'Total Cost': total_cost,
                    'Avg Cost per Waffle': avg_cost
                })
                
            if waffle_summary_data:
                waffle_summary_df = pd.DataFrame(waffle_summary_data)
                waffle_summary_df.to_excel(writer, sheet_name='Waffle Summary', index=False)
                
            # Create summary by pan type sheet
            pan_summary_data = []
            for p in pan_types:
                total_supply = sum(supply.get((p, t), 0) for t in weeks)
                
                # Calculate total usage for this pan type
                total_usage = 0
                for w in waffle_types:
                    for t in weeks:
                        total_usage += variables.get((w, p, t), 0)
                        
                if total_supply > 0:
                    utilization = total_usage / total_supply * 100
                else:
                    utilization = 0.0
                    
                pan_summary_data.append({
                    'Pan Type': p,
                    'Total Supply': total_supply,
                    'Total Usage': total_usage,
                    'Utilization (%)': utilization
                })
                
            if pan_summary_data:
                pan_summary_df = pd.DataFrame(pan_summary_data)
                pan_summary_df.to_excel(writer, sheet_name='Pan Summary', index=False)
                
        # Notify completion
        self._debug_print(f"Solution exported to {file_path}")
        
    def export_validation_to_excel(self, validation: Dict, file_path: str) -> None:
        """
        Export validation results to Excel file.
        
        Args:
            validation: Dictionary containing validation metrics
            file_path: Path to the output Excel file
        """
        # Check if validation data is available
        if not validation:
            print("No validation data available to export.")
            return
            
        # Create Excel writer
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Create summary sheet
            summary_data = {
                'Is Feasible': [validation.get('is_feasible', False)]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create issues sheet
            issues = validation.get('issues', [])
            if issues:
                issues_df = pd.DataFrame({'Issue': issues})
                issues_df.to_excel(writer, sheet_name='Issues', index=False)
                
            # Create utilization sheet
            utilization = validation.get('utilization', {})
            if utilization:
                util_data = []
                for p, rate in utilization.items():
                    util_data.append({
                        'Pan Type': p,
                        'Utilization (%)': rate
                    })
                    
                util_df = pd.DataFrame(util_data)
                util_df.to_excel(writer, sheet_name='Utilization', index=False)
                
            # Create satisfaction sheet
            satisfaction = validation.get('satisfaction', {})
            if satisfaction:
                sat_data = []
                for w, rate in satisfaction.items():
                    sat_data.append({
                        'Waffle Type': w,
                        'Satisfaction (%)': rate
                    })
                    
                sat_df = pd.DataFrame(sat_data)
                sat_df.to_excel(writer, sheet_name='Satisfaction', index=False)
                
            # Create cost sheet
            avg_cost = validation.get('avg_cost', {})
            if avg_cost:
                cost_data = []
                for w, cost in avg_cost.items():
                    cost_data.append({
                        'Waffle Type': w,
                        'Avg Cost per Waffle': cost
                    })
                    
                cost_df = pd.DataFrame(cost_data)
                cost_df.to_excel(writer, sheet_name='Cost', index=False)
                
            # Create surplus sheet
            surplus = validation.get('surplus', {})
            if surplus:
                surplus_data = []
                for w, amount in surplus.items():
                    surplus_data.append({
                        'Waffle Type': w,
                        'Surplus': amount
                    })
                    
                surplus_df = pd.DataFrame(surplus_data)
                surplus_df.to_excel(writer, sheet_name='Surplus', index=False)
                
        # Notify completion
        self._debug_print(f"Validation results exported to {file_path}") 