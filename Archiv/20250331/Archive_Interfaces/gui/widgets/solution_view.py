"""
Solution view widget for the waffle optimizer GUI.

This module contains the SolutionView class which is used for visualizing
the results of the optimization.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView,
    QSplitter, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import numpy as np
import pandas as pd


class SolutionView(QWidget):
    """Widget for visualizing optimization results."""
    
    def __init__(self):
        """Initialize the solution view widget."""
        super().__init__()
        self.solution = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Summary section
        self.summary_group = QGroupBox("Solution Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QLabel("No solution available")
        self.summary_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self.summary_text)
        
        self.summary_group.setLayout(summary_layout)
        splitter.addWidget(self.summary_group)
        
        # Create tab widget for different visualizations
        self.tabs = QTabWidget()
        
        # Production allocation tab
        production_tab = QWidget()
        production_layout = QVBoxLayout(production_tab)
        
        # Chart for production allocation
        self.production_figure = plt.figure(figsize=(8, 5))
        self.production_canvas = FigureCanvasQTAgg(self.production_figure)
        production_layout.addWidget(self.production_canvas)
        
        self.tabs.addTab(production_tab, "Production Allocation")
        
        # Pan utilization tab
        pan_tab = QWidget()
        pan_layout = QVBoxLayout(pan_tab)
        
        # Chart for pan utilization
        self.pan_figure = plt.figure(figsize=(8, 5))
        self.pan_canvas = FigureCanvasQTAgg(self.pan_figure)
        pan_layout.addWidget(self.pan_canvas)
        
        self.tabs.addTab(pan_tab, "Pan Utilization")
        
        # Cost analysis tab
        cost_tab = QWidget()
        cost_layout = QVBoxLayout(cost_tab)
        
        # Chart for cost analysis
        self.cost_figure = plt.figure(figsize=(8, 5))
        self.cost_canvas = FigureCanvasQTAgg(self.cost_figure)
        cost_layout.addWidget(self.cost_canvas)
        
        self.tabs.addTab(cost_tab, "Cost Analysis")
        
        # Detailed results tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)
        
        self.results_table = QTableWidget()
        details_layout.addWidget(self.results_table)
        
        self.tabs.addTab(details_tab, "Detailed Results")
        
        splitter.addWidget(self.tabs)
        
        # Add splitter to main layout
        layout.addWidget(splitter, 1)
        
        # Export button
        self.export_button = QPushButton("Export Solution to Excel")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export_solution)
        layout.addWidget(self.export_button)
    
    def display_solution(self, solution):
        """
        Display the optimization solution.
        
        Args:
            solution: The optimization solution dictionary.
        """
        self.solution = solution
        
        # Enable export button
        self.export_button.setEnabled(True)
        
        # Update summary
        objective = solution.get('objective', 'Unknown')
        objective_value = solution.get('objective_value', 0)
        
        if objective == 'minimize_cost':
            summary_text = (f"<h3>Cost Minimization Solution</h3>"
                           f"<p>Total Cost: <b>${objective_value:.2f}</b></p>"
                           f"<p>Total Waffles Produced: {solution.get('total_waffles', 0)}</p>")
        else:
            summary_text = (f"<h3>Output Maximization Solution</h3>"
                           f"<p>Total Waffles Produced: <b>{objective_value}</b></p>"
                           f"<p>Total Cost: ${solution.get('total_cost', 0):.2f}</p>")
        
        self.summary_text.setText(summary_text)
        
        # Update charts
        self._update_production_chart()
        self._update_pan_utilization_chart()
        self._update_cost_chart()
        self._update_results_table()
    
    def _update_production_chart(self):
        """Update the production allocation chart."""
        if not self.solution:
            return
        
        self.production_figure.clear()
        ax = self.production_figure.add_subplot(111)
        
        # Get production data
        waffle_production = {}
        
        # Extract waffle production data from either assignments or waffles_by_type_week
        if 'assignments' in self.solution and self.solution['assignments']:
            # Case 1: Using assignments list
            for assignment in self.solution['assignments']:
                waffle = assignment['waffle']
                count = assignment['count']
                
                if waffle in waffle_production:
                    waffle_production[waffle] += count
                else:
                    waffle_production[waffle] = count
        elif 'waffles_by_type_week' in self.solution:
            # Case 2: Using waffles_by_type_week dictionary
            waffles_by_type_week = self.solution['waffles_by_type_week']
            # Group by waffle type, summing across weeks
            for (waffle, week), count in waffles_by_type_week.items():
                if waffle in waffle_production:
                    waffle_production[waffle] += count
                else:
                    waffle_production[waffle] = count
        
        # If no data found, show a message and return
        if not waffle_production:
            ax.text(0.5, 0.5, "No production data available", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
            plt.tight_layout()
            self.production_canvas.draw()
            return
            
        # Create bar chart
        waffles = list(waffle_production.keys())
        production = list(waffle_production.values())
        
        # Get demand data if available
        demands = []
        if 'demands' in self.solution:
            demands_data = self.solution['demands']
            # If demands is a flat dictionary, use it directly
            if not isinstance(next(iter(demands_data.keys()), None), tuple):
                demands = [demands_data.get(waffle, 0) for waffle in waffles]
            else:
                # If it's a dictionary with tuple keys like (waffle, week)
                # Sum demands across weeks for each waffle type
                demand_by_waffle = {}
                for (waffle, week), demand in demands_data.items():
                    if waffle in demand_by_waffle:
                        demand_by_waffle[waffle] += demand
                    else:
                        demand_by_waffle[waffle] = demand
                demands = [demand_by_waffle.get(waffle, 0) for waffle in waffles]
        
        # Create bar chart
        bars = ax.bar(waffles, production, width=0.6)
        
        # Add demand line if available
        if demands:
            ax.plot(waffles, demands, 'ro-', label='Demand')
            ax.legend()
        
        # Format chart
        ax.set_title('Waffle Production')
        ax.set_xlabel('Waffle Type')
        ax.set_ylabel('Quantity')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        self.production_canvas.draw()
    
    def _update_pan_utilization_chart(self):
        """Update the pan utilization chart."""
        if not self.solution:
            return
        
        self.pan_figure.clear()
        ax = self.pan_figure.add_subplot(111)
        
        # Get pan utilization data
        pan_usage = {}
        
        # Extract pan usage data from either assignments or pans_by_type_week
        if 'assignments' in self.solution and self.solution['assignments']:
            # Case 1: Using assignments list
            for assignment in self.solution['assignments']:
                pan = assignment['pan']
                count = assignment['count']
                
                if pan in pan_usage:
                    pan_usage[pan] += count
                else:
                    pan_usage[pan] = count
        elif 'pans_by_type_week' in self.solution:
            # Case 2: Using pans_by_type_week dictionary
            pans_by_type_week = self.solution['pans_by_type_week']
            # Group by pan type, summing across weeks
            for (pan, week), count in pans_by_type_week.items():
                if pan in pan_usage:
                    pan_usage[pan] += count
                else:
                    pan_usage[pan] = count
                    
        # If no data found, show a message and return
        if not pan_usage:
            ax.text(0.5, 0.5, "No pan utilization data available", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
            plt.tight_layout()
            self.pan_canvas.draw()
            return
        
        # Get supply data
        pan_supply = {}
        if 'supplies' in self.solution:
            supplies_data = self.solution['supplies']
            # If supplies is a flat dictionary, use it directly
            if not isinstance(next(iter(supplies_data.keys()), None), tuple):
                pan_supply = supplies_data
            else:
                # If it's a dictionary with tuple keys like (pan, week)
                # Sum supplies across weeks for each pan type
                for (pan, week), supply in supplies_data.items():
                    if pan in pan_supply:
                        pan_supply[pan] += supply
                    else:
                        pan_supply[pan] = supply
        
        # Create bar chart data
        pans = list(pan_usage.keys())
        usage = list(pan_usage.values())
        
        # Add supply data if available
        supplies = []
        if pan_supply:
            supplies = [pan_supply.get(pan, 0) for pan in pans]
        
        # Create stacked bar chart to show usage vs. available
        if supplies:
            unused = [max(0, supplies[i] - usage[i]) for i in range(len(pans))]
            
            # Create stacked bar chart
            ax.bar(pans, usage, label='Used')
            ax.bar(pans, unused, bottom=usage, alpha=0.5, label='Unused')
            ax.legend()
        else:
            # Simple bar chart if no supply data
            ax.bar(pans, usage)
        
        # Format chart
        ax.set_title('Pan Utilization')
        ax.set_xlabel('Pan Type')
        ax.set_ylabel('Quantity')
        
        plt.tight_layout()
        self.pan_canvas.draw()
    
    def _update_cost_chart(self):
        """Update the cost analysis chart."""
        if not self.solution:
            return
        
        self.cost_figure.clear()
        ax = self.cost_figure.add_subplot(111)
        
        # Get cost data by waffle type
        waffle_costs = {}
        
        # Extract cost data
        if 'assignments' in self.solution and self.solution['assignments']:
            # Case 1: Using assignments list
            for assignment in self.solution['assignments']:
                waffle = assignment['waffle']
                cost = assignment.get('cost', 0)
                
                if waffle in waffle_costs:
                    waffle_costs[waffle] += cost
                else:
                    waffle_costs[waffle] = cost
        elif 'solution_values' in self.solution and 'waffles_by_type_week' in self.solution:
            # Case 2: Using solution_values
            # We need to calculate costs from the solution values
            solution_values = self.solution['solution_values']
            total_cost = self.solution.get('total_cost', 0)
            waffles_by_type_week = self.solution['waffles_by_type_week']
            
            # First, summarize production by waffle type
            waffle_production = {}
            for (waffle, week), count in waffles_by_type_week.items():
                if waffle in waffle_production:
                    waffle_production[waffle] += count
                else:
                    waffle_production[waffle] = count
            
            # If we have the cost dictionary and wpp dictionary, calculate costs directly
            if 'cost' in self.solution and 'wpp' in self.solution:
                cost_dict = self.solution['cost']
                wpp_dict = self.solution['wpp']
                
                for waffle, production in waffle_production.items():
                    waffle_cost = 0
                    for (w, p, t), count in solution_values.items():
                        if w == waffle and count > 0:
                            # Calculate cost for this waffle-pan-week assignment
                            unit_cost = cost_dict.get((w, p), 0)
                            wpp = wpp_dict.get(w, 0)
                            assignment_cost = unit_cost * wpp * count
                            waffle_cost += assignment_cost
                    
                    waffle_costs[waffle] = waffle_cost
            else:
                # Calculate proportion of total production for each waffle type
                total_production = sum(waffle_production.values()) if waffle_production else 1
                for waffle, count in waffle_production.items():
                    proportion = count / total_production if total_production > 0 else 0
                    waffle_costs[waffle] = total_cost * proportion
        
        # If no data found, show a message and return
        if not waffle_costs:
            ax.text(0.5, 0.5, "No cost data available", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
            plt.tight_layout()
            self.cost_canvas.draw()
            return
            
        # Create pie chart
        waffles = list(waffle_costs.keys())
        costs = list(waffle_costs.values())
        
        # Create pie chart
        if sum(costs) > 0:
            ax.pie(costs, labels=waffles, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        else:
            ax.text(0.5, 0.5, "All costs are zero", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes)
        
        # Format chart
        ax.set_title('Cost Distribution by Waffle Type')
        
        plt.tight_layout()
        self.cost_canvas.draw()
    
    def _update_results_table(self):
        """Update the detailed results table."""
        if not self.solution:
            return
        
        # Prepare data for the table
        table_data = []
        
        if 'assignments' in self.solution and self.solution['assignments']:
            # Case 1: Using assignments list
            assignments = self.solution['assignments']
            for assignment in assignments:
                table_data.append(assignment)
        elif 'solution_values' in self.solution:
            # Case 2: Using solution_values
            solution_values = self.solution['solution_values']
            cost_dict = self.solution.get('cost', {})
            wpp_dict = self.solution.get('wpp', {})
            
            # Convert solution_values to assignments format
            for (waffle, pan, week), count in solution_values.items():
                if count > 0:
                    wpp = wpp_dict.get(waffle, 0)
                    cost = cost_dict.get((waffle, pan), 0) * wpp * count
                    
                    table_data.append({
                        'waffle': waffle,
                        'pan': pan,
                        'week': week,
                        'count': count,
                        'waffles_per_pan': wpp,
                        'cost': cost
                    })
        
        # If no data found, clear table and return
        if not table_data:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
            
        # Set up table
        self.results_table.setRowCount(len(table_data))
        
        # Determine columns based on available data
        columns = []
        if table_data and 'waffle' in table_data[0]:
            columns.append('Waffle Type')
        if table_data and 'pan' in table_data[0]:
            columns.append('Pan Type')
        if table_data and 'week' in table_data[0]:
            columns.append('Week')
        if table_data and 'count' in table_data[0]:
            columns.append('Count')
        if table_data and 'cost' in table_data[0]:
            columns.append('Cost')
        if table_data and 'waffles_per_pan' in table_data[0]:
            columns.append('Waffles per Pan')
            
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Fill table with data
        for i, row_data in enumerate(table_data):
            col = 0
            if 'Waffle Type' in columns:
                self.results_table.setItem(i, col, QTableWidgetItem(str(row_data.get('waffle', ''))))
                col += 1
            if 'Pan Type' in columns:
                self.results_table.setItem(i, col, QTableWidgetItem(str(row_data.get('pan', ''))))
                col += 1
            if 'Week' in columns:
                self.results_table.setItem(i, col, QTableWidgetItem(str(row_data.get('week', ''))))
                col += 1
            if 'Count' in columns:
                self.results_table.setItem(i, col, QTableWidgetItem(str(row_data.get('count', 0))))
                col += 1
            if 'Cost' in columns:
                cost = row_data.get('cost', 0)
                self.results_table.setItem(i, col, QTableWidgetItem(f"${cost:.2f}"))
                col += 1
            if 'Waffles per Pan' in columns:
                self.results_table.setItem(i, col, QTableWidgetItem(str(row_data.get('waffles_per_pan', 0))))
                col += 1
        
        # Resize columns to content
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def _export_solution(self):
        """Export the solution to an Excel file."""
        if not self.solution:
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Solution",
            "waffle_solution.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Ensure the file has the .xlsx extension
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        
        # Create data for Excel
        if 'assignments' in self.solution and self.solution['assignments']:
            # Case 1: Using assignments list
            assignments = self.solution['assignments']
            df = pd.DataFrame(assignments)
        else:
            # Case 2: Using solution_values
            # Create assignments-like data structure
            table_data = []
            if 'solution_values' in self.solution:
                solution_values = self.solution['solution_values']
                cost_dict = self.solution.get('cost', {})
                wpp_dict = self.solution.get('wpp', {})
                
                for (waffle, pan, week), count in solution_values.items():
                    if count > 0:
                        wpp = wpp_dict.get(waffle, 0)
                        cost = cost_dict.get((waffle, pan), 0) * wpp * count if cost_dict else 0
                        
                        table_data.append({
                            'waffle': waffle,
                            'pan': pan,
                            'week': week,
                            'count': count,
                            'waffles_per_pan': wpp,
                            'cost': cost
                        })
            df = pd.DataFrame(table_data)
        
        # Add summary information
        summary_data = {
            'Objective': [self.solution.get('objective', 'Unknown')],
            'Objective Value': [self.solution.get('objective_value', 0)],
            'Total Cost': [self.solution.get('total_cost', 0)],
            'Total Waffles': [self.solution.get('total_waffles', 0)]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Write to Excel
        with pd.ExcelWriter(file_path) as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            df.to_excel(writer, sheet_name='Assignments', index=False)
        
        # Show confirmation
        self.summary_text.setText(
            self.summary_text.text() + 
            f"<p style='color: green;'>Solution exported to {file_path}</p>"
        ) 