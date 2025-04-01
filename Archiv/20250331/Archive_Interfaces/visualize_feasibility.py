"""
Visualization module for Waffle Optimization Feasibility Checks.

This module visualizes the results of feasibility checks without modifying
the original FeasibilityChecker class.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from feasibility_check import FeasibilityChecker


class FeasibilityVisualizer:
    def __init__(self, checker: FeasibilityChecker):
        """
        Initialize the visualizer with a FeasibilityChecker.
        
        Args:
            checker: An initialized FeasibilityChecker instance
        """
        self.checker = checker
        # Set style for better visualizations
        plt.style.use('seaborn-v0_8')  # Updated style name
        sns.set_theme(style="whitegrid")
        sns.set_palette("husl")
        
    def visualize_results(self, output_path: Optional[str] = None) -> None:
        """
        Generate and display visualizations of the feasibility check results.
        
        Args:
            output_path: Optional path to save visualizations
        """
        is_feasible = len(self.checker.feasibility_issues) == 0
        
        # Create a figure with subplots
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Feasibility Analysis - {'FEASIBLE' if is_feasible else 'INFEASIBLE'}", 
                    fontsize=16, color='green' if is_feasible else 'red')
        
        # Add visualizations
        self._plot_supply_vs_demand(fig, 221)
        self._plot_cumulative_supply_demand(fig, 222)
        self._plot_waffle_pan_compatibility(fig, 223)
        self._plot_issues_summary(fig, 224)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _plot_supply_vs_demand(self, fig, position):
        """Plot total supply vs demand as bar chart with improved clarity."""
        ax = fig.add_subplot(position)
        
        total_demand = sum(self.checker.data['total_demand'].values())
        total_supply = sum(self.checker.data['total_supply'].values())
        
        # Calculate buffer percentage
        buffer_percentage = (total_supply / total_demand * 100) if total_demand > 0 else float('inf')
        
        x = ['Total Supply', 'Total Demand']
        y = [total_supply, total_demand]
        colors = ['green', 'red'] if total_supply >= total_demand else ['red', 'green']
        
        bars = ax.bar(x, y, color=colors)
        
        # Add data labels with buffer percentage
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # Add buffer threshold lines
        ax.axhline(y=total_demand, color='black', linestyle='--', alpha=0.7, label='Demand')
        ax.axhline(y=total_demand * 1.1, color='orange', linestyle=':', alpha=0.7, label='10% Buffer')
        
        # Add buffer percentage annotation
        buffer_text = f"Buffer: {buffer_percentage:.1f}%"
        ax.text(0.5, 0.02, buffer_text,
                horizontalalignment='center',
                verticalalignment='bottom',
                transform=ax.transAxes,
                fontsize=12,
                color='green' if buffer_percentage >= 110 else 'red',
                bbox=dict(facecolor='white', alpha=0.8))
        
        ax.set_title('Total Supply vs. Demand')
        ax.set_ylabel('Number of Pans')
        ax.legend()
        
        # Use scientific notation for large numbers
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    def _plot_cumulative_supply_demand(self, fig, position):
        """Plot cumulative supply and demand over weeks with improved clarity."""
        ax = fig.add_subplot(position)
        
        weeks = sorted(self.checker.data['weeks'])
        cumulative_supply = []
        cumulative_demand = []
        current_supply = 0
        current_demand = 0
        
        for week in weeks:
            current_supply += self.checker.data['total_supply'].get(week, 0)
            current_demand += self.checker.data['total_demand'].get(week, 0)
            cumulative_supply.append(current_supply)
            cumulative_demand.append(current_demand)
        
        # Plot with improved visibility
        ax.plot(weeks, cumulative_supply, marker='o', color='blue', label='Cumulative Supply', linewidth=2)
        ax.plot(weeks, cumulative_demand, marker='x', color='red', label='Cumulative Demand', linewidth=2)
        
        # Add running average trendlines
        window_size = 3
        supply_avg = pd.Series(cumulative_supply).rolling(window=window_size).mean()
        demand_avg = pd.Series(cumulative_demand).rolling(window=window_size).mean()
        ax.plot(weeks, supply_avg, '--', color='blue', alpha=0.5, label=f'Supply {window_size}-week avg')
        ax.plot(weeks, demand_avg, '--', color='red', alpha=0.5, label=f'Demand {window_size}-week avg')
        
        # Highlight deficit regions
        for i in range(len(weeks)):
            if cumulative_supply[i] < cumulative_demand[i]:
                ax.fill_between([weeks[i-1] if i > 0 else weeks[0], weeks[i]], 
                                [cumulative_supply[i-1] if i > 0 else 0, cumulative_supply[i]],
                                [cumulative_demand[i-1] if i > 0 else 0, cumulative_demand[i]],
                                color='red', alpha=0.3)
                
                # Add deficit annotation
                deficit = cumulative_demand[i] - cumulative_supply[i]
                ax.annotate(f'Deficit: {deficit:,.0f}', 
                           xy=(weeks[i], (cumulative_supply[i] + cumulative_demand[i])/2),
                           xytext=(10, 0),
                           textcoords="offset points",
                           ha='left', va='center',
                           arrowprops=dict(arrowstyle="->", color='black'))
        
        ax.set_title('Cumulative Supply vs. Demand by Week')
        ax.set_xlabel('Week')
        ax.set_ylabel('Cumulative Number of Pans')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Use scientific notation for large numbers
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    def _plot_waffle_pan_compatibility(self, fig, position):
        """Plot heatmap of waffle-pan compatibility with improved clarity."""
        ax = fig.add_subplot(position)
        
        waffle_types = self.checker.data['waffle_types']
        pan_types = self.checker.data['pan_types']
        allowed = self.checker.data['allowed']
        
        # Create compatibility matrix
        compatibility_matrix = []
        for waffle in waffle_types:
            row = []
            for pan in pan_types:
                row.append(1 if allowed.get((waffle, pan), False) else 0)
            compatibility_matrix.append(row)
        
        df = pd.DataFrame(compatibility_matrix, index=waffle_types, columns=pan_types)
        
        # Only show waffle types with compatibility issues
        problematic_waffles = [i for i, row in enumerate(compatibility_matrix) if sum(row) == 0]
        if problematic_waffles:
            df = df.iloc[problematic_waffles]
            # Plot heatmap with improved visibility
            sns.heatmap(df, annot=True, cmap="YlGnBu", cbar=False, linewidths=0.5, ax=ax)
            
            # Highlight incompatible waffle types
            for i in range(len(df.index)):
                ax.add_patch(plt.Rectangle((0, i), len(pan_types), 1, fill=False, 
                                          edgecolor='red', lw=2, clip_on=False))
                ax.text(-0.5, i + 0.5, "✗", color='red', fontsize=15, ha='center', va='center')
            
            ax.set_title('Waffle-Pan Compatibility Matrix\n(Showing only problematic combinations)')
        else:
            ax.text(0.5, 0.5, "No compatibility issues found", 
                    ha='center', va='center', fontsize=12)
            ax.set_title('Waffle-Pan Compatibility Matrix')
        
        ax.set_ylabel('Waffle Types')
        ax.set_xlabel('Pan Types')
    
    def _plot_issues_summary(self, fig, position):
        """Create a text summary of feasibility issues with improved clarity."""
        ax = fig.add_subplot(position)
        ax.axis('off')
        
        is_feasible = len(self.checker.feasibility_issues) == 0
        
        # Create summary text with improved formatting
        summary = f"Feasibility Status: {'FEASIBLE' if is_feasible else 'INFEASIBLE'}\n\n"
        
        if self.checker.feasibility_issues:
            summary += "Critical Issues:\n"
            for i, issue in enumerate(self.checker.feasibility_issues, 1):
                summary += f"✗ {issue}\n"
            summary += "\n"
        
        if self.checker.warnings:
            summary += "Warnings:\n"
            for i, warning in enumerate(self.checker.warnings, 1):
                summary += f"⚠ {warning}\n"
            summary += "\n"
        
        if is_feasible and not self.checker.warnings:
            summary += "✓ No issues detected. The problem appears to be feasible."
        
        # Add recommendations if infeasible
        if not is_feasible:
            summary += "\nRecommendations to Resolve Issues:\n"
            if any("Insufficient total pan supply" in issue for issue in self.checker.feasibility_issues):
                summary += "• Increase total pan supply\n"
                summary += "• Reduce overall demand\n"
            
            if any("no compatible pan types" in issue for issue in self.checker.feasibility_issues):
                summary += "• Add pan compatibility for problematic waffle types\n"
            
            if any("Insufficient cumulative supply by week" in issue for issue in self.checker.feasibility_issues):
                summary += "• Adjust weekly production schedule\n"
                summary += "• Front-load pan supplies to earlier weeks\n"
        
        ax.text(0, 1, summary, va='top', ha='left', wrap=True)
        ax.set_title('Feasibility Summary & Recommendations')
    
    def generate_supply_demand_table(self) -> pd.DataFrame:
        """
        Generate a table showing weekly supply, demand, and cumulative totals.
        
        Returns:
            pd.DataFrame: Table with supply/demand data
        """
        weeks = sorted(self.checker.data['weeks'])
        data = []
        
        cumulative_supply = 0
        cumulative_demand = 0
        
        for week in weeks:
            week_supply = self.checker.data['total_supply'].get(week, 0)
            week_demand = self.checker.data['total_demand'].get(week, 0)
            
            cumulative_supply += week_supply
            cumulative_demand += week_demand
            
            # Calculate buffer percentage
            buffer_percentage = (cumulative_supply / cumulative_demand * 100) if cumulative_demand > 0 else float('inf')
            
            status = "✓" if cumulative_supply >= cumulative_demand else "✗"
            
            data.append({
                'Week': week,
                'Supply': week_supply,
                'Demand': week_demand,
                'Buffer %': f"{buffer_percentage:.1f}%",
                'Status': status
            })
        
        df = pd.DataFrame(data)
        
        # Add total row
        total_supply = sum(self.checker.data['total_supply'].values())
        total_demand = sum(self.checker.data['total_demand'].values())
        total_buffer = (total_supply / total_demand * 100) if total_demand > 0 else float('inf')
        
        df.loc[len(df)] = {
            'Week': 'TOTAL',
            'Supply': total_supply,
            'Demand': total_demand,
            'Buffer %': f"{total_buffer:.1f}%",
            'Status': "✓" if total_supply >= total_demand else "✗"
        }
        
        # Format numbers with thousands separator
        df['Supply'] = df['Supply'].apply(lambda x: f"{x:,.0f}")
        df['Demand'] = df['Demand'].apply(lambda x: f"{x:,.0f}")
        
        return df
    
    def save_visualizations_to_html(self, output_path: str) -> None:
        """
        Save all visualizations to an HTML report.
        
        Args:
            output_path: Path to save the HTML report
        """
        # Generate the supply-demand table
        supply_demand_table = self.generate_supply_demand_table()
        
        # Create HTML content with improved styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Feasibility Check Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {'green' if len(self.checker.feasibility_issues) == 0 else 'red'}; 
                          color: white; padding: 10px; text-align: center; }}
                .section {{ margin: 20px 0; }}
                .critical {{ background-color: #ffcccc; padding: 10px; border-radius: 5px; }}
                .warning {{ background-color: #ffffcc; padding: 10px; border-radius: 5px; }}
                .table {{ border-collapse: collapse; width: 100%; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .table th {{ padding-top: 12px; padding-bottom: 12px; background-color: #4CAF50; color: white; }}
                .infeasible {{ color: red; font-weight: bold; }}
                .feasible {{ color: green; font-weight: bold; }}
                .buffer-low {{ color: orange; }}
                .buffer-critical {{ color: red; }}
                .summary-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .metric {{ font-size: 1.2em; margin: 5px 0; }}
                .status-icon {{ font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Feasibility Check Report</h1>
                <h2>{'FEASIBLE' if len(self.checker.feasibility_issues) == 0 else 'INFEASIBLE'}</h2>
            </div>
            
            <div class="summary-box">
                <h3>Key Metrics</h3>
                <div class="metric">Total Supply: {sum(self.checker.data['total_supply'].values()):,.0f} pans</div>
                <div class="metric">Total Demand: {sum(self.checker.data['total_demand'].values()):,.0f} pans</div>
                <div class="metric">Overall Buffer: {(sum(self.checker.data['total_supply'].values()) / sum(self.checker.data['total_demand'].values()) * 100):.1f}%</div>
                <div class="metric">Critical Issues: {len(self.checker.feasibility_issues)}</div>
                <div class="metric">Warnings: {len(self.checker.warnings)}</div>
            </div>
            
            <div class="section">
                <h2>Supply vs. Demand Summary</h2>
                {supply_demand_table.to_html(classes='table', index=False)}
            </div>
        """
        
        # Add issues and warnings
        if self.checker.feasibility_issues:
            html_content += """
            <div class="section critical">
                <h2>Critical Issues</h2>
                <ul>
            """
            for issue in self.checker.feasibility_issues:
                html_content += f"<li class='status-icon'>✗ {issue}</li>"
            html_content += """
                </ul>
            </div>
            """
        
        if self.checker.warnings:
            html_content += """
            <div class="section warning">
                <h2>Warnings</h2>
                <ul>
            """
            for warning in self.checker.warnings:
                html_content += f"<li class='status-icon'>⚠ {warning}</li>"
            html_content += """
                </ul>
            </div>
            """
        
        # Close HTML
        html_content += """
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report saved to {output_path}")


# Example usage and demo
if __name__ == "__main__":
    # Sample data for the feasibility check
    data = {
        'weeks': [1, 2, 3, 4],
        'waffle_types': ['Regular', 'Belgian', 'Mini', 'Chocolate'],
        'pan_types': ['Type A', 'Type B', 'Type C'],
        'total_demand': {1: 100, 2: 150, 3: 200, 4: 150},
        'total_supply': {1: 120, 2: 120, 3: 180, 4: 140},
        'allowed': {
            ('Regular', 'Type A'): True,
            ('Regular', 'Type B'): True,
            ('Belgian', 'Type B'): True,
            ('Belgian', 'Type C'): True,
            ('Mini', 'Type A'): True,
            ('Mini', 'Type C'): False,
            ('Chocolate', 'Type A'): False,
            ('Chocolate', 'Type B'): False,
            ('Chocolate', 'Type C'): False,
        }
    }
    
    # Initialize the feasibility checker with the data
    checker = FeasibilityChecker(data)
    
    # Run the feasibility check
    checker.check_feasibility()
    
    # Print the text report
    checker.print_report()
    
    # Create the visualizer and show the visualizations
    visualizer = FeasibilityVisualizer(checker)
    visualizer.visualize_results()
    
    # Save the visualizations to an HTML file
    visualizer.save_visualizations_to_html("feasibility_report.html")
    
    # Generate and display the supply-demand table
    table = visualizer.generate_supply_demand_table()
    print("\nSupply-Demand Table:")
    print(table) 