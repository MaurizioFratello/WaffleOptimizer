"""
Feasibility view widget for the waffle optimizer GUI.

This module contains the FeasibilityView class which is used for visualizing
the results of the feasibility check.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QPushButton,
    QScrollArea, QTextEdit, QGridLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import seaborn as sns
import pandas as pd
import numpy as np


class FeasibilityView(QWidget):
    """Widget for visualizing feasibility check results."""
    
    run_optimization = pyqtSignal()
    
    def __init__(self):
        """Initialize the feasibility view widget."""
        super().__init__()
        self.feasibility_result = None
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_theme(style="whitegrid")
        sns.set_palette("husl")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Status section
        self.status_group = QGroupBox("Feasibility Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Feasibility check not run yet")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # Key metrics section
        self.metrics_layout = QGridLayout()
        self.total_supply_label = QLabel("Total Supply: -")
        self.total_demand_label = QLabel("Total Demand: -")
        self.buffer_label = QLabel("Buffer: -")
        self.issues_label = QLabel("Critical Issues: -")
        self.warnings_label = QLabel("Warnings: -")
        
        self.metrics_layout.addWidget(self.total_supply_label, 0, 0)
        self.metrics_layout.addWidget(self.total_demand_label, 0, 1)
        self.metrics_layout.addWidget(self.buffer_label, 1, 0)
        self.metrics_layout.addWidget(self.issues_label, 1, 1)
        self.metrics_layout.addWidget(self.warnings_label, 2, 0)
        
        status_layout.addLayout(self.metrics_layout)
        self.status_group.setLayout(status_layout)
        layout.addWidget(self.status_group)
        
        # Create tab widget for different views
        self.tabs = QTabWidget()
        
        # Graphs tab
        self.graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(self.graphs_widget)
        
        # Supply vs Demand plot
        self.supply_demand_figure = plt.figure(figsize=(8, 4))
        self.supply_demand_canvas = FigureCanvasQTAgg(self.supply_demand_figure)
        graphs_layout.addWidget(self.supply_demand_canvas)
        
        # Cumulative plot
        self.cumulative_figure = plt.figure(figsize=(8, 4))
        self.cumulative_canvas = FigureCanvasQTAgg(self.cumulative_figure)
        graphs_layout.addWidget(self.cumulative_canvas)
        
        # Compatibility matrix plot
        self.compatibility_figure = plt.figure(figsize=(8, 4))
        self.compatibility_canvas = FigureCanvasQTAgg(self.compatibility_figure)
        graphs_layout.addWidget(self.compatibility_canvas)
        
        self.tabs.addTab(self.graphs_widget, "Visualizations")
        
        # Table tab
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)
        
        self.supply_demand_table = QTableWidget()
        self.supply_demand_table.setColumnCount(5)
        self.supply_demand_table.setHorizontalHeaderLabels(
            ["Week", "Supply", "Demand", "Buffer %", "Status"]
        )
        header = self.supply_demand_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.supply_demand_table)
        
        self.tabs.addTab(self.table_widget, "Details")
        
        # Issues tab
        self.issues_widget = QWidget()
        issues_layout = QVBoxLayout(self.issues_widget)
        
        self.issues_text = QTextEdit()
        self.issues_text.setReadOnly(True)
        issues_layout.addWidget(self.issues_text)
        
        self.tabs.addTab(self.issues_widget, "Issues & Recommendations")
        
        layout.addWidget(self.tabs)
        
        # Optimization button
        self.optimize_button = QPushButton("Run Optimization")
        self.optimize_button.setEnabled(False)
        self.optimize_button.clicked.connect(self.run_optimization.emit)
        layout.addWidget(self.optimize_button)
    
    def display_feasibility_result(self, result):
        """
        Display the feasibility check result.
        
        Args:
            result: The feasibility check result dictionary.
        """
        self.feasibility_result = result
        
        # Update status and metrics
        is_feasible = result.get('is_feasible', False)
        
        # Handle missing data safely
        if 'total_supply' not in result or 'total_demand' not in result:
            print("Error: Missing total_supply or total_demand in feasibility result")
            self.status_label.setText("⚠️ Error displaying results")
            self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 16px;")
            self.optimize_button.setEnabled(False)
            return
            
        # Get total values safely
        try:
            if isinstance(result['total_supply'], dict) and isinstance(result['total_demand'], dict):
                total_supply = sum(result['total_supply'].values())
                total_demand = sum(result['total_demand'].values())
            else:
                print("Error: total_supply or total_demand is not a dictionary")
                self.status_label.setText("⚠️ Error in data format")
                self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 16px;")
                self.optimize_button.setEnabled(False)
                return
                
            buffer_percentage = (total_supply / total_demand * 100) if total_demand > 0 else float('inf')
        except Exception as e:
            print(f"Error calculating totals: {str(e)}")
            self.status_label.setText("⚠️ Error in calculations")
            self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 16px;")
            self.optimize_button.setEnabled(False)
            return
        
        if is_feasible:
            self.status_label.setText("✅ Problem is FEASIBLE")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
            self.optimize_button.setEnabled(True)
        else:
            self.status_label.setText("❌ Problem is INFEASIBLE")
            self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
            self.optimize_button.setEnabled(False)
        
        # Update metrics
        self.total_supply_label.setText(f"Total Supply: {total_supply:,.0f} pans")
        self.total_demand_label.setText(f"Total Demand: {total_demand:,.0f} pans")
        self.buffer_label.setText(f"Buffer: {buffer_percentage:.1f}%")
        self.issues_label.setText(f"Critical Issues: {len(result.get('issues', []))}")
        self.warnings_label.setText(f"Warnings: {len(result.get('warnings', []))}")
        
        # Update visualizations
        self._plot_supply_vs_demand(result)
        self._plot_cumulative_supply_demand(result)
        self._plot_compatibility_matrix(result)
        
        # Update table
        self._update_table(result)
        
        # Update issues text
        self._update_issues_text(result)
    
    def _plot_supply_vs_demand(self, result):
        """Plot total supply vs demand bar chart."""
        try:
            self.supply_demand_figure.clear()
            ax = self.supply_demand_figure.add_subplot(111)
            
            # Get data safely
            if not isinstance(result.get('total_demand'), dict) or not isinstance(result.get('total_supply'), dict):
                ax.text(0.5, 0.5, "Error: Missing or invalid data for visualization",
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=12,
                       color='red')
                self.supply_demand_canvas.draw()
                return
            
            total_demand = sum(result['total_demand'].values())
            total_supply = sum(result['total_supply'].values())
            buffer_percentage = (total_supply / total_demand * 100) if total_demand > 0 else float('inf')
            
            x = ['Total Supply', 'Total Demand']
            y = [total_supply, total_demand]
            colors = ['green', 'red'] if total_supply >= total_demand else ['red', 'green']
            
            bars = ax.bar(x, y, color=colors)
            
            # Add data labels
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
            
            self.supply_demand_canvas.draw()
            
        except Exception as e:
            print(f"Error in _plot_supply_vs_demand: {str(e)}")
            self.supply_demand_figure.clear()
            ax = self.supply_demand_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Error plotting data: {str(e)}",
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12,
                   color='red')
            self.supply_demand_canvas.draw()
    
    def _plot_cumulative_supply_demand(self, result):
        """Plot cumulative supply and demand over weeks."""
        try:
            self.cumulative_figure.clear()
            ax = self.cumulative_figure.add_subplot(111)
            
            # Check for required keys
            if 'weeks' not in result or 'total_demand' not in result or 'total_supply' not in result:
                ax.text(0.5, 0.5, "Error: Missing data for cumulative chart",
                      horizontalalignment='center',
                      verticalalignment='center',
                      transform=ax.transAxes,
                      fontsize=12,
                      color='red')
                self.cumulative_canvas.draw()
                return
                
            # Validate data types
            if not isinstance(result['total_demand'], dict) or not isinstance(result['total_supply'], dict):
                ax.text(0.5, 0.5, "Error: Invalid data format for cumulative chart",
                      horizontalalignment='center',
                      verticalalignment='center',
                      transform=ax.transAxes,
                      fontsize=12,
                      color='red')
                self.cumulative_canvas.draw()
                return
            
            weeks = sorted(result['weeks'])
            cumulative_supply = []
            cumulative_demand = []
            current_supply = 0
            current_demand = 0
            
            for week in weeks:
                # Get values with fallback to 0
                week_supply = result['total_supply'].get(week, 0)
                week_demand = result['total_demand'].get(week, 0)
                
                # Ensure values are numeric
                if not isinstance(week_supply, (int, float)):
                    week_supply = 0
                if not isinstance(week_demand, (int, float)):
                    week_demand = 0
                
                current_supply += week_supply
                current_demand += week_demand
                cumulative_supply.append(current_supply)
                cumulative_demand.append(current_demand)
            
            # Plot with improved visibility
            ax.plot(weeks, cumulative_supply, marker='o', color='blue', label='Cumulative Supply', linewidth=2)
            ax.plot(weeks, cumulative_demand, marker='x', color='red', label='Cumulative Demand', linewidth=2)
            
            # Add running average trendlines
            if len(weeks) >= 3:  # Only add trendlines if we have enough data
                window_size = min(3, len(weeks))
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
            
            self.cumulative_figure.tight_layout()
            self.cumulative_canvas.draw()
            
        except Exception as e:
            print(f"Error in _plot_cumulative_supply_demand: {str(e)}")
            self.cumulative_figure.clear()
            ax = self.cumulative_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Error plotting cumulative data: {str(e)}",
                  horizontalalignment='center',
                  verticalalignment='center',
                  transform=ax.transAxes,
                  fontsize=12,
                  color='red')
            self.cumulative_canvas.draw()
    
    def _plot_compatibility_matrix(self, result):
        """Plot waffle-pan compatibility matrix."""
        try:
            self.compatibility_figure.clear()
            ax = self.compatibility_figure.add_subplot(111)
            
            # Check for required keys
            if 'waffle_types' not in result or 'pan_types' not in result or 'allowed' not in result:
                ax.text(0.5, 0.5, "Error: Missing data for compatibility matrix",
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=12,
                       color='red')
                self.compatibility_canvas.draw()
                return
            
            waffle_types = result['waffle_types']
            pan_types = result['pan_types']
            allowed = result['allowed']
            
            # Validate data types
            if not isinstance(allowed, dict) or not waffle_types or not pan_types:
                ax.text(0.5, 0.5, "Error: Invalid data format for compatibility matrix",
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=12,
                       color='red')
                self.compatibility_canvas.draw()
                return
            
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
            
            self.compatibility_figure.tight_layout()
            self.compatibility_canvas.draw()
            
        except Exception as e:
            print(f"Error in _plot_compatibility_matrix: {str(e)}")
            self.compatibility_figure.clear()
            ax = self.compatibility_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"Error plotting compatibility matrix: {str(e)}",
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12,
                   color='red')
            self.compatibility_canvas.draw()
    
    def _update_table(self, result):
        """Update the supply-demand table."""
        try:
            # Check for required keys
            if 'weeks' not in result or 'total_demand' not in result or 'total_supply' not in result:
                print("Error: Missing required data for table")
                return
                
            weeks = sorted(result['weeks'])
            self.supply_demand_table.setRowCount(len(weeks) + 1)  # +1 for total row
            
            # Validate data types
            if not isinstance(result['total_demand'], dict) or not isinstance(result['total_supply'], dict):
                print("Error: Invalid data format for table")
                return
                
            cumulative_supply = 0
            cumulative_demand = 0
            
            for i, week in enumerate(weeks):
                week_supply = result['total_supply'].get(week, 0)
                week_demand = result['total_demand'].get(week, 0)
                
                # Ensure values are numeric
                if not isinstance(week_supply, (int, float)):
                    week_supply = 0
                if not isinstance(week_demand, (int, float)):
                    week_demand = 0
                
                cumulative_supply += week_supply
                cumulative_demand += week_demand
                
                buffer_percentage = (cumulative_supply / cumulative_demand * 100) if cumulative_demand > 0 else float('inf')
                status = "✓" if cumulative_supply >= cumulative_demand else "✗"
                
                self.supply_demand_table.setItem(i, 0, QTableWidgetItem(str(week)))
                self.supply_demand_table.setItem(i, 1, QTableWidgetItem(f"{week_supply:,.0f}"))
                self.supply_demand_table.setItem(i, 2, QTableWidgetItem(f"{week_demand:,.0f}"))
                self.supply_demand_table.setItem(i, 3, QTableWidgetItem(f"{buffer_percentage:.1f}%"))
                self.supply_demand_table.setItem(i, 4, QTableWidgetItem(status))
            
            # Add total row
            total_supply = sum(result['total_supply'].values())
            total_demand = sum(result['total_demand'].values())
            total_buffer = (total_supply / total_demand * 100) if total_demand > 0 else float('inf')
            
            last_row = len(weeks)
            self.supply_demand_table.setItem(last_row, 0, QTableWidgetItem("TOTAL"))
            self.supply_demand_table.setItem(last_row, 1, QTableWidgetItem(f"{total_supply:,.0f}"))
            self.supply_demand_table.setItem(last_row, 2, QTableWidgetItem(f"{total_demand:,.0f}"))
            self.supply_demand_table.setItem(last_row, 3, QTableWidgetItem(f"{total_buffer:.1f}%"))
            self.supply_demand_table.setItem(last_row, 4, QTableWidgetItem("✓" if total_supply >= total_demand else "✗"))
            
        except Exception as e:
            print(f"Error in _update_table: {str(e)}")
    
    def _update_issues_text(self, result):
        """Update the issues and recommendations text."""
        try:
            text = "Feasibility Analysis Summary\n\n"
            
            if 'issues' not in result or 'warnings' not in result:
                text += "Error: Missing issues or warnings data in the result\n"
                self.issues_text.setText(text)
                return
            
            if result.get('issues'):
                text += "Critical Issues:\n"
                for issue in result['issues']:
                    text += f"✗ {issue}\n"
                text += "\n"
            
            if result.get('warnings'):
                text += "Warnings:\n"
                for warning in result['warnings']:
                    text += f"⚠ {warning}\n"
                text += "\n"
            
            if not result.get('issues') and not result.get('warnings'):
                text += "✓ No issues detected. The problem appears to be feasible.\n\n"
            
            # Add recommendations if there are issues
            if result.get('issues'):
                text += "Recommendations to Resolve Issues:\n"
                issues_text = ' '.join([str(issue) for issue in result['issues']])
                
                if "Insufficient total pan supply" in issues_text:
                    text += "• Increase total pan supply\n"
                    text += "• Reduce overall demand\n"
                
                if "no compatible pan types" in issues_text:
                    text += "• Add pan compatibility for problematic waffle types\n"
                
                if "Insufficient cumulative supply by week" in issues_text:
                    text += "• Adjust weekly production schedule\n"
                    text += "• Front-load pan supplies to earlier weeks\n"
            
            self.issues_text.setText(text)
            
        except Exception as e:
            print(f"Error in _update_issues_text: {str(e)}")
            self.issues_text.setText(f"Error updating issues text: {str(e)}") 