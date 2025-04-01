"""
Results Reporting Module for Waffle Production Optimization.

This module provides functionality for generating reports and visualizations
of optimization results.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from typing import Dict, List, Any

class ResultsReporter:
    """
    Class for reporting and visualizing optimization results.
    """
    
    def __init__(self, solution: Dict, data: Dict):
        """
        Initialize the results reporter.
        
        Args:
            solution: Dictionary containing the optimization solution
            data: Dictionary containing the optimization data
        """
        self.solution = solution
        self.data = data
        
    def _get_sorted_weeks(self):
        """Return weeks sorted numerically by their value."""
        # Convert weeks to integers if they're not already
        try:
            # If weeks are already integers
            return sorted(self.data['weeks'])
        except TypeError:
            # If weeks are in a string format like "Week 1" or "w01"
            # Extract the numeric part and sort by that
            def extract_number(week_str):
                match = re.search(r'\d+', str(week_str))
                return int(match.group()) if match else 0
                
            return sorted(self.data['weeks'], key=extract_number)
        
    def print_summary(self) -> None:
        """Print a summary of the optimization results."""
        if self.solution['status'] not in ['OPTIMAL', 'FEASIBLE']:
            print(f"No feasible solution found. Status: {self.solution['status']}")
            return
            
        model_type = self.solution['model_type']
        objective_value = self.solution['objective_value']
        total_waffles = self.solution['total_waffles']
        
        print("\n=== Optimization Results ===")
        print(f"Solution status: {self.solution['status']}")
        
        if model_type == 'minimize_cost':
            print(f"Total cost: {objective_value:.2f}")
            print(f"Total waffles produced: {total_waffles:.0f}")
        else:  # maximize_output
            print(f"Total waffles produced: {objective_value:.0f}")
            
            if self.solution.get('total_cost') is not None:
                print(f"Total cost: {self.solution['total_cost']:.2f}")
        
        # Summary of waffles by type
        waffles_by_type_week = self.solution['waffles_by_type_week']
        waffles_by_type = {}
        
        for (waffle_type, week), waffles in waffles_by_type_week.items():
            waffles_by_type[waffle_type] = waffles_by_type.get(waffle_type, 0) + waffles
            
        print("\nWaffles by type:")
        for waffle_type, waffles in sorted(waffles_by_type.items()):
            print(f"  {waffle_type}: {waffles:.0f}")
        
        # Summary of pans by type
        pans_by_type_week = self.solution['pans_by_type_week']
        pans_by_type = {}
        
        for (pan_type, week), pans in pans_by_type_week.items():
            pans_by_type[pan_type] = pans_by_type.get(pan_type, 0) + pans
            
        print("\nPans by type:")
        for pan_type, pans in sorted(pans_by_type.items()):
            print(f"  {pan_type}: {pans:.0f}")
    
    def plot_waffle_production(self) -> plt.Figure:
        """
        Plot the waffle production over time.
        
        Returns:
            plt.Figure: Matplotlib figure object
        """
        if self.solution['status'] not in ['OPTIMAL', 'FEASIBLE']:
            raise ValueError("No feasible solution to plot.")
            
        waffles_by_type_week = self.solution['waffles_by_type_week']
        weeks = self._get_sorted_weeks()
        waffle_types = sorted(self.data['waffle_types'])
        
        # Create a DataFrame for easier plotting
        data = []
        for w in waffle_types:
            for t in weeks:
                data.append({
                    'WaffleType': w,
                    'Week': t,
                    'Waffles': waffles_by_type_week.get((w, t), 0)
                })
        df = pd.DataFrame(data)
        
        # Pivot the DataFrame for stacked bar chart
        pivot_df = df.pivot(index='Week', columns='WaffleType', values='Waffles')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot_df.plot(kind='bar', stacked=True, ax=ax)
        
        ax.set_title('Waffle Production by Type and Week')
        ax.set_xlabel('Week')
        ax.set_ylabel('Number of Waffles')
        ax.legend(title='Waffle Type')
        
        plt.tight_layout()
        return fig
    
    def plot_pan_usage(self) -> plt.Figure:
        """
        Plot the pan usage over time.
        
        Returns:
            plt.Figure: Matplotlib figure object
        """
        if self.solution['status'] not in ['OPTIMAL', 'FEASIBLE']:
            raise ValueError("No feasible solution to plot.")
            
        pans_by_type_week = self.solution['pans_by_type_week']
        weeks = self._get_sorted_weeks()
        pan_types = sorted(self.data['pan_types'])
        
        # Create a DataFrame for easier plotting
        data = []
        for p in pan_types:
            for t in weeks:
                data.append({
                    'PanType': p,
                    'Week': t,
                    'Pans': pans_by_type_week.get((p, t), 0)
                })
        df = pd.DataFrame(data)
        
        # Pivot the DataFrame for stacked bar chart
        pivot_df = df.pivot(index='Week', columns='PanType', values='Pans')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot_df.plot(kind='bar', stacked=True, ax=ax)
        
        ax.set_title('Pan Usage by Type and Week')
        ax.set_xlabel('Week')
        ax.set_ylabel('Number of Pans')
        ax.legend(title='Pan Type')
        
        plt.tight_layout()
        return fig
    
    def plot_supply_demand_comparison(self) -> plt.Figure:
        """
        Plot the supply vs. demand comparison.
        
        Returns:
            plt.Figure: Matplotlib figure object
        """
        if self.solution['status'] not in ['OPTIMAL', 'FEASIBLE']:
            raise ValueError("No feasible solution to plot.")
            
        weeks = self._get_sorted_weeks()
        
        # Calculate total demand and supply for each week
        demand_by_week = {}
        supply_by_week = {}
        
        for (w, t), value in self.data['demand'].items():
            demand_by_week[t] = demand_by_week.get(t, 0) + value
            
        for (p, t), value in self.data['supply'].items():
            supply_by_week[t] = supply_by_week.get(t, 0) + value
        
        # Create a DataFrame for plotting
        data = []
        for t in weeks:
            data.append({
                'Week': t,
                'Demand (Pans)': demand_by_week.get(t, 0),
                'Supply (Pans)': supply_by_week.get(t, 0)
            })
        df = pd.DataFrame(data)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.bar(df['Week'], df['Demand (Pans)'], alpha=0.7, label='Demand')
        ax.bar(df['Week'], df['Supply (Pans)'], alpha=0.5, label='Supply')
        
        ax.set_title('Weekly Pan Supply vs. Demand')
        ax.set_xlabel('Week')
        ax.set_ylabel('Number of Pans')
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def generate_detailed_report(self) -> pd.DataFrame:
        """
        Generate a detailed production report.
        
        Returns:
            pd.DataFrame: DataFrame containing detailed production information
        """
        if self.solution['status'] not in ['OPTIMAL', 'FEASIBLE']:
            raise ValueError("No feasible solution to generate a report.")
            
        solution_values = self.solution['solution_values']
        wpp = self.data['wpp']  # Now this is waffles per waffle type
        cost = self.data.get('cost', {})
        
        # Create a list of dictionaries for the report
        report_data = []
        for (w, p, t), value in solution_values.items():
            # Use waffles per waffle type
            waffle_wpp = wpp.get(w, 0)
            waffles = value * waffle_wpp
            unit_cost = cost.get((w, p), 0)
            total_cost = unit_cost * waffles
            
            report_data.append({
                'Week': t,
                'WaffleType': w,
                'PanType': p,
                'PansUsed': value,
                'WafflesProduced': waffles,
                'UnitCost': unit_cost,
                'TotalCost': total_cost
            })
        
        # Convert to DataFrame and sort
        df = pd.DataFrame(report_data)
        df = df.sort_values(['Week', 'WaffleType', 'PanType'])
        
        return df
    
    def export_solution(self, filename: str) -> None:
        """
        Export the solution to an Excel file.
        
        Args:
            filename: Name of the Excel file to create
        """
        if self.solution['status'] not in ['OPTIMAL', 'FEASIBLE']:
            raise ValueError("No feasible solution to export.")
            
        # Create a detailed report
        detailed_report = self.generate_detailed_report()
        
        # Create a summary by week and waffle type
        summary_by_week_waffle = pd.pivot_table(
            detailed_report,
            values=['PansUsed', 'WafflesProduced', 'TotalCost'],
            index=['Week', 'WaffleType'],
            aggfunc='sum'
        ).reset_index()
        
        # Create a summary by week and pan type
        summary_by_week_pan = pd.pivot_table(
            detailed_report,
            values=['PansUsed', 'WafflesProduced', 'TotalCost'],
            index=['Week', 'PanType'],
            aggfunc='sum'
        ).reset_index()
        
        # Create an overall summary
        overall_summary = pd.DataFrame([{
            'TotalPansUsed': detailed_report['PansUsed'].sum(),
            'TotalWafflesProduced': detailed_report['WafflesProduced'].sum(),
            'TotalCost': detailed_report['TotalCost'].sum(),
            'ModelType': self.solution['model_type'],
            'ObjectiveValue': self.solution['objective_value']
        }])
        
        # Export to Excel
        with pd.ExcelWriter(filename) as writer:
            detailed_report.to_excel(writer, sheet_name='DetailedReport', index=False)
            summary_by_week_waffle.to_excel(writer, sheet_name='SummaryByWaffle', index=False)
            summary_by_week_pan.to_excel(writer, sheet_name='SummaryByPan', index=False)
            overall_summary.to_excel(writer, sheet_name='OverallSummary', index=False)
