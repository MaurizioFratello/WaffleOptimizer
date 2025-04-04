"""
Validation Dashboard view for the Waffle Optimizer GUI.
This view provides comprehensive data validation and visualization.
"""
import os
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFormLayout, QGridLayout,
                          QGroupBox, QMessageBox, QScrollArea, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal

# Import matplotlib for charts
import matplotlib
matplotlib.use('QtAgg')  # Use Qt backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ..widgets.card_widget import CardWidget
from src.data.processor import DataProcessor
from src.data.validator import DataValidator

class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding charts in PyQt."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                  QSizePolicy.Policy.Expanding,
                                  QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)

class ValidationDashboardView(QWidget):
    """
    Dashboard view for visualizing data validation results and analysis.
    """
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        
        # Data storage
        self.data_paths = {}
        self.optimization_data = None
        self.is_validated = False  # Track if validation has been run
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        
        # Header
        header = QLabel("Validation Dashboard")
        header.setObjectName("viewHeader")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        self.content_layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Comprehensive analysis of data quality and optimization feasibility."
        )
        description.setWordWrap(True)
        self.content_layout.addWidget(description)
        
        # Create status cards
        self.status_cards = self._create_status_cards()
        self.content_layout.addLayout(self.status_cards)
        
        # Supply vs Demand Chart
        supply_demand_group = QGroupBox("Supply vs Demand Analysis")
        supply_demand_layout = QVBoxLayout(supply_demand_group)
        
        self.supply_demand_canvas = MatplotlibCanvas(width=8, height=4)
        supply_demand_layout.addWidget(self.supply_demand_canvas)
        
        # Add initial message to empty chart
        ax = self.supply_demand_canvas.axes
        ax.text(0.5, 0.5, "Click 'Run Validation' to analyze data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='#777777')
        ax.set_xticks([])
        ax.set_yticks([])
        self.supply_demand_canvas.draw()
        
        description = QLabel(
            "This chart compares the total demand for each waffle type with the maximum "
            "theoretical production capacity based on available pans and WPP values."
        )
        description.setWordWrap(True)
        supply_demand_layout.addWidget(description)
        
        self.content_layout.addWidget(supply_demand_group)
        
        # Weekly Feasibility Chart
        weekly_group = QGroupBox("Weekly Feasibility Check")
        weekly_layout = QVBoxLayout(weekly_group)
        
        self.weekly_canvas = MatplotlibCanvas(width=8, height=4)
        weekly_layout.addWidget(self.weekly_canvas)
        
        # Add initial message to empty chart
        ax = self.weekly_canvas.axes
        ax.text(0.5, 0.5, "Click 'Run Validation' to analyze data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='#777777')
        ax.set_xticks([])
        ax.set_yticks([])
        self.weekly_canvas.draw()
        
        description = QLabel(
            "This heatmap shows the feasibility status for each waffle type in each week. "
            "Green indicates sufficient capacity, yellow indicates tight capacity, "
            "and red indicates insufficient capacity."
        )
        description.setWordWrap(True)
        weekly_layout.addWidget(description)
        
        self.content_layout.addWidget(weekly_group)
        
        # Combinations Matrix
        combinations_group = QGroupBox("Allowed Combinations Matrix")
        combinations_layout = QVBoxLayout(combinations_group)
        
        self.combinations_canvas = MatplotlibCanvas(width=8, height=4)
        combinations_layout.addWidget(self.combinations_canvas)
        
        # Add initial message to empty chart
        ax = self.combinations_canvas.axes
        ax.text(0.5, 0.5, "Click 'Run Validation' to analyze data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='#777777')
        ax.set_xticks([])
        ax.set_yticks([])
        self.combinations_canvas.draw()
        
        description = QLabel(
            "This matrix shows which waffle types can be produced on which pan types. "
            "A filled cell indicates an allowed combination."
        )
        description.setWordWrap(True)
        combinations_layout.addWidget(description)
        
        self.content_layout.addWidget(combinations_group)
        
        # Recommendations
        self.recommendations_box = QGroupBox("Recommendations")
        recommendations_layout = QVBoxLayout(self.recommendations_box)
        self.recommendations_label = QLabel("Run validation to see recommendations.")
        self.recommendations_label.setWordWrap(True)
        recommendations_layout.addWidget(self.recommendations_label)
        
        self.content_layout.addWidget(self.recommendations_box)
        
        # Add action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self._refresh_data)
        
        self.validate_button = QPushButton("Run Validation")
        self.validate_button.clicked.connect(self._run_validation)
        
        self.go_to_optimization_button = QPushButton("Continue to Optimization")
        self.go_to_optimization_button.clicked.connect(
            lambda: self.main_window._switch_view("optimization"))
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.validate_button)
        button_layout.addWidget(self.go_to_optimization_button)
        
        self.content_layout.addLayout(button_layout)
        
        # Set up scroll area
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Initialize data validator
        self.data_validator = DataValidator(debug_mode=False)
        
    def _create_status_cards(self):
        """Create status card widgets."""
        status_layout = QGridLayout()
        status_layout.setSpacing(15)
        
        # Feasibility status card
        self.feasibility_card = CardWidget(title="Overall Status")
        feasibility_label = QLabel("Not Validated")
        feasibility_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feasibility_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #777777;
            margin: 10px 0;
        """)
        self.feasibility_card.add_widget(feasibility_label)
        self.feasibility_card.setProperty("status_label", feasibility_label)
        status_layout.addWidget(self.feasibility_card, 0, 0)
        
        # Critical issues card
        self.critical_card = CardWidget(title="Critical Issues")
        critical_label = QLabel("0")
        critical_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        critical_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #777777;
            margin: 10px 0;
        """)
        self.critical_card.add_widget(critical_label)
        self.critical_card.setProperty("status_label", critical_label)
        status_layout.addWidget(self.critical_card, 0, 1)
        
        # Warnings card
        self.warnings_card = CardWidget(title="Warnings")
        warnings_label = QLabel("0")
        warnings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warnings_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #777777;
            margin: 10px 0;
        """)
        self.warnings_card.add_widget(warnings_label)
        self.warnings_card.setProperty("status_label", warnings_label)
        status_layout.addWidget(self.warnings_card, 0, 2)
        
        return status_layout
        
    def _update_status_card(self, card, value, color):
        """Update a status card with a new value and color."""
        label = card.property("status_label")
        if label:
            # Replace special character ✓ with + in the value if present
            if isinstance(value, str) and "✓" in value:
                value = value.replace("✓", "+")
            # Replace special character ❌ with X in the value if present
            if isinstance(value, str) and "❌" in value:
                value = value.replace("❌", "X")
                
            label.setText(str(value))
            label.setStyleSheet(f"""
                font-size: 20px;
                font-weight: bold;
                color: {color};
                margin: 10px 0;
            """)
            
    def _create_supply_demand_chart(self, data):
        """Create the supply vs demand chart."""
        if not data:
            return
            
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        demand = data.get('demand', {})
        supply = data.get('supply', {})
        wpp = data.get('wpp', {})
        allowed = data.get('allowed', {})
        
        # Calculate total demand per waffle type
        total_demand = {}
        for w in waffle_types:
            total_demand[w] = sum(demand.get((w, t), 0) for t in weeks)
        
        # Calculate theoretical capacity per waffle type
        total_capacity = {}
        for w in waffle_types:
            total_capacity[w] = 0
            for p in pan_types:
                if allowed.get((w, p), False):
                    for t in weeks:
                        if (p, t) in supply:
                            total_capacity[w] += supply[(p, t)] * wpp.get(w, 0)
        
        # Prepare plot
        ax = self.supply_demand_canvas.axes
        ax.clear()
        
        # Create bar positions
        x = np.arange(len(waffle_types))
        width = 0.35
        
        # Create bars
        demand_bars = ax.bar(x - width/2, [total_demand.get(w, 0) for w in waffle_types], 
                            width, label='Demand', color='#3498db')
        capacity_bars = ax.bar(x + width/2, [total_capacity.get(w, 0) for w in waffle_types], 
                            width, label='Available Capacity', color='#2ecc71')
        
        # Add labels and legend
        ax.set_ylabel('Quantity')
        ax.set_title('Supply vs Demand by Waffle Type')
        ax.set_xticks(x)
        ax.set_xticklabels(waffle_types)
        ax.legend()
        
        # Highlight infeasible cases
        for i, w in enumerate(waffle_types):
            if total_demand.get(w, 0) > total_capacity.get(w, 0):
                demand_bars[i].set_color('#e74c3c')  # Red for excess demand
        
        # Redraw
        self.supply_demand_canvas.draw()
        
    def _create_weekly_feasibility_chart(self, data, weekly_issues):
        """Create the weekly feasibility heatmap."""
        if not data:
            return
            
        # Extract data
        waffle_types = data.get('waffle_types', [])
        weeks = data.get('weeks', [])
        
        # Create a grid of feasibility values
        # 0: No demand, 1: Feasible, 0.5: Warning, 0: Critical
        grid = np.ones((len(waffle_types), len(weeks)))
        
        # Set values based on weekly_issues
        for issue in weekly_issues:
            if "exceeds maximum theoretical capacity" in issue:
                # Parse the issue message to get week and waffle type
                parts = issue.split(":")
                if len(parts) >= 2:
                    week_str = parts[0].strip().replace("Week ", "")
                    waffle_str = parts[1].strip().split("'")[1]
                    
                    try:
                        week_idx = weeks.index(week_str)
                        waffle_idx = waffle_types.index(waffle_str)
                        
                        # Check if it's a warning or critical issue
                        if "exceeds maximum theoretical capacity" in issue:
                            grid[waffle_idx, week_idx] = 0  # Critical
                    except (ValueError, IndexError):
                        pass
        
        # Prepare plot
        ax = self.weekly_canvas.axes
        ax.clear()
        
        # Create colormap: green for feasible, yellow for warning, red for critical
        cmap = plt.cm.RdYlGn
        
        # Create heatmap
        im = ax.imshow(grid, cmap=cmap, aspect='auto', vmin=0, vmax=1)
        
        # Add labels
        ax.set_xticks(np.arange(len(weeks)))
        ax.set_xticklabels(weeks)
        ax.set_yticks(np.arange(len(waffle_types)))
        ax.set_yticklabels(waffle_types)
        
        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add title
        ax.set_title("Weekly Feasibility Check")
        
        # Add text annotations in each cell with ASCII characters
        for i in range(len(waffle_types)):
            for j in range(len(weeks)):
                text = "+" if grid[i, j] == 1 else "!" if grid[i, j] == 0.5 else "X"
                ax.text(j, i, text, ha="center", va="center", color="black")
        
        # Add legend explanation with ASCII characters
        ax.text(0, len(waffle_types) + 0.8, "+ Sufficient Capacity   ! Tight Capacity   X Insufficient Capacity", 
               ha="left", va="center", color="black", fontsize=9)
        
        # Adjust layout
        self.weekly_canvas.fig.tight_layout()
        
        # Redraw
        self.weekly_canvas.draw()
        
    def _create_combinations_matrix(self, data):
        """Create the allowed combinations matrix."""
        if not data:
            return
            
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        allowed = data.get('allowed', {})
        
        # Create matrix of allowed combinations
        grid = np.zeros((len(waffle_types), len(pan_types)))
        
        # Fill in allowed combinations
        for i, w in enumerate(waffle_types):
            for j, p in enumerate(pan_types):
                if allowed.get((w, p), False):
                    grid[i, j] = 1
        
        # Prepare plot
        ax = self.combinations_canvas.axes
        ax.clear()
        
        # Create heatmap
        im = ax.imshow(grid, cmap='Blues', aspect='auto', vmin=0, vmax=1)
        
        # Add labels
        ax.set_xticks(np.arange(len(pan_types)))
        ax.set_xticklabels(pan_types)
        ax.set_yticks(np.arange(len(waffle_types)))
        ax.set_yticklabels(waffle_types)
        
        # Add title
        ax.set_title("Allowed Combinations Matrix")
        
        # Add text annotations in each cell - keep filled/empty box chars as they seem to be supported
        for i in range(len(waffle_types)):
            for j in range(len(pan_types)):
                text = "#" if grid[i, j] == 1 else "-"
                ax.text(j, i, text, ha="center", va="center", color="black")
        
        # Add legend explanation with ASCII characters
        ax.text(0, len(waffle_types) + 0.8, "# Allowed Combination   - Not Allowed", 
               ha="left", va="center", color="black", fontsize=9)
        
        # Check for unused pan types
        unused_pans = []
        for j, p in enumerate(pan_types):
            if not any(grid[i, j] == 1 for i in range(len(waffle_types))):
                unused_pans.append(p)
        
        # Add warning for unused pans
        if unused_pans:
            unused_str = ", ".join(unused_pans)
            ax.text(0, len(waffle_types) + 1.3, f"Warning: {unused_str} {'is' if len(unused_pans) == 1 else 'are'} not used for any waffle type", 
                   ha="left", va="center", color="#e74c3c", fontsize=9)
        
        # Adjust layout
        self.combinations_canvas.fig.tight_layout()
        
        # Redraw
        self.combinations_canvas.draw()
        
    def _generate_recommendations(self, data, critical_issues, warnings, weekly_issues):
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Extract data
        waffle_types = data.get('waffle_types', [])
        pan_types = data.get('pan_types', [])
        weeks = data.get('weeks', [])
        allowed = data.get('allowed', {})
        
        # Add recommendations for unused pan types
        for p in pan_types:
            if not any(allowed.get((w, p), False) for w in waffle_types):
                recommendations.append(f"● Consider removing pan type '{p}' as it's not used for any waffle type")
        
        # Add recommendations for weekly capacity issues
        week_waffle_issues = {}
        for issue in weekly_issues:
            if "exceeds maximum theoretical capacity" in issue:
                parts = issue.split(":")
                if len(parts) >= 2:
                    week_str = parts[0].strip().replace("Week ", "")
                    waffle_str = parts[1].strip().split("'")[1]
                    recommendations.append(f"● {week_str} has insufficient capacity for {waffle_str} - consider increasing supply")
        
        # Add recommendations for critical issues
        for issue in critical_issues:
            if "total demand" in issue.lower() and "exceeds" in issue.lower():
                recommendations.append(f"● {issue} - consider increasing overall supply or reducing demand")
        
        # If no specific recommendations, add general ones
        if not recommendations:
            if warnings:
                recommendations.append("● No critical issues found, but review warnings for potential improvements")
            else:
                recommendations.append("● All validation checks passed - data is well-structured for optimization")
        
        return recommendations
        
    def _run_validation(self, show_popup=True):
        """
        Run validation checks and update the dashboard.
        
        Args:
            show_popup: Whether to show a popup with validation results
        """
        # Get data from DataView if not already stored
        if not self.data_paths and self.main_window and hasattr(self.main_window, 'data_view'):
            self.data_paths = self.main_window.data_view.get_data_paths()
        
        # Check if all required data files are set
        missing_files = [key for key, path in self.data_paths.items() 
                       if not path or not path.strip()]
        
        if missing_files:
            missing_str = ", ".join(missing_files)
            if show_popup:
                QMessageBox.warning(
                    self, 
                    "Missing Files", 
                    f"The following required data files are missing: {missing_str}\n"
                    f"Please configure them in the Data tab."
                )
            return
        
        try:
            # Process data
            data_processor = DataProcessor()
            data_processor.load_data(
                demand_file=self.data_paths.get("demand", ""),
                supply_file=self.data_paths.get("supply", ""),
                cost_file=self.data_paths.get("cost", ""),
                wpp_file=self.data_paths.get("wpp", ""),
                combinations_file=self.data_paths.get("combinations", "")
            )
            
            # Get optimization data
            self.optimization_data = data_processor.get_optimization_data()
            
            # Run validation
            is_feasible, critical_issues, warnings = self.data_validator.check_basic_feasibility(self.optimization_data)
            weekly_feasible, weekly_issues = self.data_validator.check_weekly_feasibility(self.optimization_data)
            
            # Update status cards
            if is_feasible:
                self._update_status_card(self.feasibility_card, "+ FEASIBLE", "#2ecc71")  # Green
            else:
                self._update_status_card(self.feasibility_card, "X INFEASIBLE", "#e74c3c")  # Red
                
            self._update_status_card(self.critical_card, len(critical_issues), 
                                    "#e74c3c" if critical_issues else "#2ecc71")
            self._update_status_card(self.warnings_card, len(warnings), 
                                    "#f39c12" if warnings else "#2ecc71")
            
            # Create charts
            self._create_supply_demand_chart(self.optimization_data)
            self._create_weekly_feasibility_chart(self.optimization_data, weekly_issues)
            self._create_combinations_matrix(self.optimization_data)
            
            # Generate and display recommendations
            recommendations = self._generate_recommendations(
                self.optimization_data, critical_issues, warnings, weekly_issues
            )
            
            # Update recommendations label
            self.recommendations_label.setText("\n".join(recommendations))
            
            # Mark as validated
            self.is_validated = True
            
            # Show message with validation results only if requested
            if show_popup:
                status = "passed" if is_feasible else "failed"
                message = f"Validation {status}.\n\n"
                
                if critical_issues:
                    message += "Critical Issues:\n"
                    for issue in critical_issues:
                        message += f"• {issue}\n"
                    message += "\n"
                    
                if warnings:
                    message += "Warnings:\n"
                    for warning in warnings:
                        message += f"• {warning}\n"
                
                if not critical_issues and not warnings:
                    message += "No issues or warnings found."
                    
                QMessageBox.information(self, "Validation Results", message)
            
        except Exception as e:
            if show_popup:
                QMessageBox.critical(self, "Validation Error", f"An error occurred during validation: {str(e)}")

    def _refresh_data(self):
        """Refresh data from the data view without running validation."""
        # Get data from DataView
        if not self.main_window or not hasattr(self.main_window, 'data_view'):
            QMessageBox.warning(
                self, 
                "Missing Data", 
                "Please configure data files in the Data tab first."
            )
            return
            
        self.data_paths = self.main_window.data_view.get_data_paths()
        
        # Check if all required data files are set
        missing_files = [key for key, path in self.data_paths.items() 
                      if not path or not path.strip()]
        
        if missing_files:
            missing_str = ", ".join(missing_files)
            QMessageBox.warning(
                self, 
                "Missing Files", 
                f"The following required data files are missing: {missing_str}\n"
                f"Please configure them in the Data tab."
            )
            return
        
        # Clear validation status
        self.is_validated = False
        
        # Reset status cards to default state
        self._update_status_card(self.feasibility_card, "Not Validated", "#777777")
        self._update_status_card(self.critical_card, "0", "#777777")
        self._update_status_card(self.warnings_card, "0", "#777777")
        
        # Clear charts
        if hasattr(self, 'supply_demand_canvas') and self.supply_demand_canvas:
            self.supply_demand_canvas.axes.clear()
            self.supply_demand_canvas.draw()
            
        if hasattr(self, 'weekly_canvas') and self.weekly_canvas:
            self.weekly_canvas.axes.clear()
            self.weekly_canvas.draw()
            
        if hasattr(self, 'combinations_canvas') and self.combinations_canvas:
            self.combinations_canvas.axes.clear()
            self.combinations_canvas.draw()
        
        # Reset recommendations
        self.recommendations_label.setText("Run validation to see recommendations.")
        
        QMessageBox.information(
            self,
            "Data Refreshed",
            "Data has been refreshed from the Data tab. Click 'Run Validation' to analyze the data."
        ) 