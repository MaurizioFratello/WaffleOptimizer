"""
Validation Dashboard view for the Waffle Optimizer GUI.
This view provides comprehensive data validation and visualization.
"""
import os
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFormLayout, QGridLayout,
                          QGroupBox, QMessageBox, QScrollArea, QSizePolicy, QFrame, QTabWidget,
                          QWidget)
from PyQt6.QtCore import Qt, pyqtSignal

# Import matplotlib for charts
import matplotlib
matplotlib.use('QtAgg')  # Use Qt backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ..base_view import BaseView
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

class ValidationDashboardView(BaseView):
    """
    Dashboard view for visualizing data validation results and analysis.
    """
    
    def __init__(self, main_window=None):
        super().__init__(
            title="Validation Dashboard",
            description="Comprehensive analysis of data quality and optimization feasibility.",
            main_window=main_window,
            action_button_text="Run Validation"
        )
        
        # Connect action button
        self.action_button.clicked.connect(self._run_validation)
        
        # Data storage
        self.data_paths = {}
        self.optimization_data = None
        self.is_validated = False  # Track if validation has been run
        
        # Initialize validation components
        self._init_validation_components()
        
        # Initialize data validator
        self.data_validator = DataValidator(debug_mode=False)
        
    def _init_validation_components(self):
        """Initialize validation dashboard specific components."""
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        scroll_content_layout = QVBoxLayout(content_widget)
        scroll_content_layout.setSpacing(20)
        
        # Create status cards
        self.status_cards = self._create_status_cards()
        scroll_content_layout.addLayout(self.status_cards)
        
        # Recommendations
        self.recommendations_box = self.create_group_box("Recommendations")
        recommendations_layout = QVBoxLayout(self.recommendations_box)
        self.recommendations_label = QLabel("Run validation to see recommendations.")
        self.recommendations_label.setWordWrap(True)
        recommendations_layout.addWidget(self.recommendations_label)
        
        scroll_content_layout.addWidget(self.recommendations_box)
        
        # Supply vs Demand Chart
        supply_demand_group = self.create_group_box("Supply vs Demand Analysis")
        supply_demand_layout = QVBoxLayout(supply_demand_group)
        
        # Create tab widget for validation checks
        self.validation_tabs = QTabWidget()
        
        # Tab 1: Supply vs Demand
        supply_demand_tab = QWidget()
        supply_demand_tab_layout = QVBoxLayout(supply_demand_tab)
        
        self.supply_demand_canvas = MatplotlibCanvas(width=8, height=4)
        # Add initial message to empty chart
        ax = self.supply_demand_canvas.axes
        ax.text(0.5, 0.5, "Click 'Run Validation' to analyze data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='#777777')
        ax.set_xticks([])
        ax.set_yticks([])
        self.supply_demand_canvas.draw()
        
        supply_demand_tab_layout.addWidget(self.supply_demand_canvas)
        self.validation_tabs.addTab(supply_demand_tab, "Supply vs Demand")
        
        # Tab 2: Weekly Feasibility
        weekly_tab = QWidget()
        weekly_tab_layout = QVBoxLayout(weekly_tab)
        
        self.weekly_canvas = MatplotlibCanvas(width=8, height=4)
        # Add initial message to empty chart
        ax = self.weekly_canvas.axes
        ax.text(0.5, 0.5, "Click 'Run Validation' to analyze data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='#777777')
        ax.set_xticks([])
        ax.set_yticks([])
        self.weekly_canvas.draw()
        
        weekly_tab_layout.addWidget(self.weekly_canvas)
        self.validation_tabs.addTab(weekly_tab, "Weekly Feasibility")
        
        # Tab 3: Combinations Matrix
        combinations_tab = QWidget()
        combinations_tab_layout = QVBoxLayout(combinations_tab)
        
        self.combinations_canvas = MatplotlibCanvas(width=8, height=4)
        # Add initial message to empty chart
        ax = self.combinations_canvas.axes
        ax.text(0.5, 0.5, "Click 'Run Validation' to analyze data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='#777777')
        ax.set_xticks([])
        ax.set_yticks([])
        self.combinations_canvas.draw()
        
        combinations_tab_layout.addWidget(self.combinations_canvas)
        self.validation_tabs.addTab(combinations_tab, "Combinations Matrix")
        
        supply_demand_layout.addWidget(self.validation_tabs)
        
        description = QLabel(
            "These charts provide different validation perspectives on the data. "
            "Click 'Run Validation' to analyze all data and populate these views."
        )
        description.setWordWrap(True)
        supply_demand_layout.addWidget(description)
        
        scroll_content_layout.addWidget(supply_demand_group)
        
        # Set up scroll area
        scroll_area.setWidget(content_widget)
        self.content_layout.addWidget(scroll_area)
        
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
        """)
        self.feasibility_card.set_content(feasibility_label)
        self.feasibility_card.set_status("neutral")
        self.feasibility_card.setProperty("status_label", feasibility_label)
        status_layout.addWidget(self.feasibility_card, 0, 0)
        
        # Issues card
        self.issues_card = CardWidget(title="Critical Issues")
        issues_label = QLabel("0")
        issues_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        issues_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)
        self.issues_card.set_content(issues_label)
        self.issues_card.set_status("success")
        self.issues_card.setProperty("status_label", issues_label)
        status_layout.addWidget(self.issues_card, 0, 1)
        
        # Warnings card
        self.warnings_card = CardWidget(title="Warnings")
        warnings_label = QLabel("0")
        warnings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warnings_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)
        self.warnings_card.set_content(warnings_label)
        self.warnings_card.set_status("success")
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
        
    def _run_validation(self):
        """Run validation checks on the data."""
        # Get data files from the data view
        if self.main_window and hasattr(self.main_window, 'data_view'):
            self.data_paths = self.main_window.data_view.get_data_paths()
        
        # Check that all data files are available
        missing_files = [key for key, path in self.data_paths.items() 
                        if not path or not os.path.exists(path)]
        
        if missing_files:
            missing_list = "\n".join([f"- {key}" for key in missing_files])
            QMessageBox.warning(
                self,
                "Missing Data Files",
                f"The following data files are missing or invalid:\n{missing_list}\n\n"
                f"Please configure data files in the Data view."
            )
            return
        
        try:
            # Process the data
            print("Loading data for validation...")
            processor = DataProcessor(debug_mode=False)
            
            # Load data using the proper method
            processor.load_data(
                demand_file=self.data_paths.get("demand", ""),
                supply_file=self.data_paths.get("supply", ""),
                cost_file=self.data_paths.get("cost", ""),
                wpp_file=self.data_paths.get("wpp", ""),
                combinations_file=self.data_paths.get("combinations", "")
            )
            
            # Get optimization data
            self.optimization_data = processor.get_optimization_data()
            
            # Run validation
            print("Running validation...")
            
            # Use the correct validation methods
            is_feasible, critical_issues, warnings = self.data_validator.check_basic_feasibility(self.optimization_data)
            weekly_feasible, weekly_issues = self.data_validator.check_weekly_feasibility(self.optimization_data)
            
            # Store results on the validator for access by other methods
            self.data_validator.is_feasible = is_feasible
            self.data_validator.critical_issues = critical_issues
            self.data_validator.warnings = warnings
            self.data_validator.weekly_issues = []
            
            # Parse weekly issues into a list of (week_idx, waffle_idx, severity) tuples
            for issue in weekly_issues:
                if "Week " in issue and "exceeds maximum theoretical capacity" in issue:
                    parts = issue.split(":")
                    if len(parts) >= 2:
                        week_str = parts[0].strip().replace("Week ", "")
                        waffle_str = parts[1].strip().split("'")[1]
                        
                        try:
                            week_idx = self.optimization_data['weeks'].index(week_str)
                            waffle_idx = self.optimization_data['waffle_types'].index(waffle_str)
                            
                            # 0 = critical issue (infeasible), 1 = warning (tight)
                            severity = 0  # Assume critical for now
                            
                            self.data_validator.weekly_issues.append((week_idx, waffle_idx, severity))
                        except (ValueError, IndexError):
                            print(f"Could not parse weekly issue: {issue}")
            
            # Update status cards
            self._update_status_cards(self.data_validator)
            
            # Update charts based on validation results
            self._update_supply_demand_chart()
            self._update_weekly_feasibility_chart()
            self._update_combinations_matrix()
            
            # Switch to the first tab to show results
            self.validation_tabs.setCurrentIndex(0)
            
            # Update recommendations
            self._update_recommendations()
            
            # Mark as validated
            self.is_validated = True
            
            print("Validation completed successfully")
            
            # Show success message
            QMessageBox.information(
                self,
                "Validation Complete",
                "Data validation completed successfully.\n"
                "You can view the results in the different tabs."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Validation Error",
                f"An error occurred during validation:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()

    def _refresh_data(self):
        """
        Refresh data from the data model service.
        Returns True if all required data is available, False otherwise.
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Get parameter registry from main window if available
            if hasattr(self, 'main_window') and self.main_window:
                if hasattr(self.main_window, 'param_registry'):
                    param_registry = self.main_window.param_registry
                    
                    # Get the data parameter model
                    data_model = param_registry.get_model('data')
                    
                    # Get paths for all data files
                    demand_file = data_model.get_parameter('demand_file')
                    supply_file = data_model.get_parameter('supply_file')
                    cost_file = data_model.get_parameter('cost_file')
                    wpp_file = data_model.get_parameter('wpp_file')
                    combinations_file = data_model.get_parameter('combinations_file')
                    
                    # Check if any required file is missing
                    missing_files = []
                    if not demand_file:
                        missing_files.append("Demand file")
                    if not supply_file:
                        missing_files.append("Supply file")
                    if not cost_file:
                        missing_files.append("Cost file")
                    if not wpp_file:
                        missing_files.append("Waffles per pan file")
                    if not combinations_file:
                        missing_files.append("Combinations file")
                    
                    if missing_files:
                        logger.warning(f"Missing data files: {', '.join(missing_files)}")
                        self.data_paths = {}
                        return False
                    
                    # Store data file paths
                    self.data_paths = {
                        'demand': demand_file,
                        'supply': supply_file,
                        'cost': cost_file,
                        'wpp': wpp_file,
                        'combinations': combinations_file
                    }
                    
                    # Try to get other required data
                    self.waffle_types = data_model.get_parameter('waffle_types')
                    self.pan_types = data_model.get_parameter('pan_types')
                    self.weeks = data_model.get_parameter('weeks')
                    
                    # Check if essential data is missing
                    if not self.waffle_types or not self.pan_types or not self.weeks:
                        logger.warning("Missing essential data (waffle types, pan types, or weeks)")
                        return False
                    
                    return True
                else:
                    logger.warning("Parameter registry not available in main window")
            else:
                logger.warning("Main window not available or invalid")
                
            return False
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            return False

    def _update_status_cards(self, validator):
        """Update status cards based on validation results."""
        # Get validation results from the validator
        is_feasible = validator.is_feasible
        critical_issues = validator.critical_issues
        warnings = validator.warnings
        
        # Update status cards
        if is_feasible:
            self._update_status_card(self.feasibility_card, "+ FEASIBLE", "#2ecc71")  # Green
        else:
            self._update_status_card(self.feasibility_card, "X INFEASIBLE", "#e74c3c")  # Red
            
        self._update_status_card(self.issues_card, len(critical_issues), 
                                "#e74c3c" if critical_issues else "#2ecc71")
        self._update_status_card(self.warnings_card, len(warnings), 
                                "#f39c12" if warnings else "#2ecc71")
    
    def _update_supply_demand_chart(self):
        """Update the supply vs demand chart with validation data."""
        self.supply_demand_canvas.axes.clear()
        
        try:
            data = self.optimization_data
            waffle_types = data['waffle_types']
            
            # Calculate total demand per waffle type
            total_demand = {}
            for waffle in waffle_types:
                total_demand[waffle] = 0
                for week in data['weeks']:
                    total_demand[waffle] += data['demand'].get((waffle, week), 0)
            
            # Calculate maximum production capacity per waffle type
            max_production = {}
            for waffle in waffle_types:
                max_production[waffle] = 0
                wpp = data['wpp'].get(waffle, 0)
                for pan in data['pan_types']:
                    if data['allowed'].get((waffle, pan), False):
                        for week in data['weeks']:
                            max_production[waffle] += data['supply'].get((pan, week), 0) * wpp
            
            # Extract values in the same order as waffle_types
            demand_values = [total_demand.get(w, 0) for w in waffle_types]
            production_values = [max_production.get(w, 0) for w in waffle_types]
            
            # Get x position for bars
            x = range(len(waffle_types))
            width = 0.35
            
            # Plot bars
            self.supply_demand_canvas.axes.bar(
                [p - width/2 for p in x], 
                production_values, 
                width, 
                label='Max Production Capacity', 
                color='#3498db'
            )
            self.supply_demand_canvas.axes.bar(
                [p + width/2 for p in x], 
                demand_values, 
                width, 
                label='Total Demand', 
                color='#e74c3c'
            )
            
            # Add labels and legend
            self.supply_demand_canvas.axes.set_xlabel('Waffle Types')
            self.supply_demand_canvas.axes.set_ylabel('Quantity')
            self.supply_demand_canvas.axes.set_title('Supply vs Demand Analysis')
            self.supply_demand_canvas.axes.set_xticks(x)
            self.supply_demand_canvas.axes.set_xticklabels(waffle_types, rotation=45, ha='right')
            self.supply_demand_canvas.axes.legend()
            
            # Add grid and adjust layout
            self.supply_demand_canvas.axes.grid(True, axis='y', linestyle='--', alpha=0.7)
            self.supply_demand_canvas.fig.tight_layout()
            self.supply_demand_canvas.draw()
            
        except Exception as e:
            print(f"Error updating supply demand chart: {e}")
            # Clear the chart and display error message
            self.supply_demand_canvas.axes.clear()
            self.supply_demand_canvas.axes.text(
                0.5, 0.5, f"Error creating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=self.supply_demand_canvas.axes.transAxes, color='red'
            )
            self.supply_demand_canvas.draw()
    
    def _update_weekly_feasibility_chart(self):
        """Update the weekly feasibility chart with validation data."""
        self.weekly_canvas.axes.clear()
        
        try:
            data = self.optimization_data
            weeks = data['weeks']
            waffles = data['waffle_types']
            weekly_issues = self.data_validator.weekly_issues
            
            # Create a matrix of feasibility values
            # 0 = infeasible (red), 1 = tight capacity (yellow), 2 = feasible (green)
            feasibility_matrix = np.ones((len(weeks), len(waffles))) * 2  # Initialize as feasible
            
            # Mark issues in the matrix
            for week_idx, waffle_idx, severity in weekly_issues:
                # severity: 0 = critical (infeasible), 1 = warning (tight)
                feasibility_matrix[week_idx, waffle_idx] = severity
            
            # Create heatmap
            cmap = plt.cm.get_cmap('RdYlGn', 3)  # Red, Yellow, Green
            im = self.weekly_canvas.axes.imshow(
                feasibility_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=2
            )
            
            # Add labels
            self.weekly_canvas.axes.set_xticks(range(len(waffles)))
            self.weekly_canvas.axes.set_yticks(range(len(weeks)))
            self.weekly_canvas.axes.set_xticklabels(waffles, rotation=45, ha='right')
            self.weekly_canvas.axes.set_yticklabels(weeks)
            self.weekly_canvas.axes.set_xlabel('Waffle Types')
            self.weekly_canvas.axes.set_ylabel('Weeks')
            self.weekly_canvas.axes.set_title('Weekly Feasibility Analysis')
            
            # Add colorbar
            cbar = self.weekly_canvas.fig.colorbar(im, ticks=[0, 1, 2])
            cbar.ax.set_yticklabels(['Infeasible', 'Tight Capacity', 'Feasible'])
            
            # Adjust layout
            self.weekly_canvas.fig.tight_layout()
            self.weekly_canvas.draw()
            
        except Exception as e:
            print(f"Error updating weekly feasibility chart: {e}")
            # Clear the chart and display error message
            self.weekly_canvas.axes.clear()
            self.weekly_canvas.axes.text(
                0.5, 0.5, f"Error creating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=self.weekly_canvas.axes.transAxes, color='red'
            )
            self.weekly_canvas.draw()
    
    def _update_combinations_matrix(self):
        """Update the combinations matrix chart with validation data."""
        self.combinations_canvas.axes.clear()
        
        try:
            data = self.optimization_data
            waffles = data['waffle_types']
            pans = data['pan_types']
            allowed = data['allowed']
            
            # Create binary matrix for combinations (1 = allowed, 0 = not allowed)
            combinations_matrix = np.zeros((len(waffles), len(pans)))
            
            # Fill in allowed combinations
            for waffle_idx, waffle in enumerate(waffles):
                for pan_idx, pan in enumerate(pans):
                    if allowed.get((waffle, pan), False):
                        combinations_matrix[waffle_idx, pan_idx] = 1
            
            # Create heatmap
            cmap = plt.cm.Blues
            im = self.combinations_canvas.axes.imshow(
                combinations_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=1
            )
            
            # Add labels
            self.combinations_canvas.axes.set_xticks(range(len(pans)))
            self.combinations_canvas.axes.set_yticks(range(len(waffles)))
            self.combinations_canvas.axes.set_xticklabels(pans, rotation=45, ha='right')
            self.combinations_canvas.axes.set_yticklabels(waffles)
            self.combinations_canvas.axes.set_xlabel('Pan Types')
            self.combinations_canvas.axes.set_ylabel('Waffle Types')
            self.combinations_canvas.axes.set_title('Allowed Waffle-Pan Combinations')
            
            # Add cell text (1 for allowed, empty for not allowed)
            for i in range(len(waffles)):
                for j in range(len(pans)):
                    if combinations_matrix[i, j] > 0:
                        self.combinations_canvas.axes.text(
                            j, i, '✓', ha='center', va='center', color='white'
                        )
            
            # Adjust layout
            self.combinations_canvas.fig.tight_layout()
            self.combinations_canvas.draw()
            
        except Exception as e:
            print(f"Error updating combinations matrix: {e}")
            # Clear the chart and display error message
            self.combinations_canvas.axes.clear()
            self.combinations_canvas.axes.text(
                0.5, 0.5, f"Error creating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=self.combinations_canvas.axes.transAxes, color='red'
            )
            self.combinations_canvas.draw()
    
    def _update_recommendations(self):
        """Update the recommendations based on validation results."""
        try:
            # Generate recommendations based on validation results
            recommendations = []
            
            # Get validation results
            is_feasible = self.data_validator.is_feasible
            critical_issues = self.data_validator.critical_issues
            warnings = self.data_validator.warnings
            weekly_issues = self.data_validator.weekly_issues
            
            # Overall feasibility recommendation
            if is_feasible:
                recommendations.append("✅ The optimization problem is feasible and ready for optimization.")
            else:
                recommendations.append("❌ The optimization problem is currently infeasible. Review critical issues below.")
            
            # Add critical issues
            if critical_issues:
                recommendations.append("\nCritical Issues:")
                for issue in critical_issues:
                    recommendations.append(f"❌ {issue}")
            
            # Add warnings
            if warnings:
                recommendations.append("\nWarnings:")
                for warning in warnings:
                    recommendations.append(f"⚠️ {warning}")
            
            # Add weekly issues if any
            if weekly_issues:
                recommendations.append("\nWeekly Feasibility Issues:")
                for week_idx, waffle_idx, severity in weekly_issues[:5]:  # Limit to first 5 issues
                    week = self.optimization_data['weeks'][week_idx]
                    waffle = self.optimization_data['waffles'][waffle_idx]
                    issue_type = "insufficient capacity" if severity == 0 else "tight capacity"
                    recommendations.append(f"{'❌' if severity == 0 else '⚠️'} Week {week}, {waffle}: {issue_type}")
                
                if len(weekly_issues) > 5:
                    recommendations.append(f"... and {len(weekly_issues) - 5} more issues. See the Weekly Feasibility tab.")
            
            # Add suggestion for optimization if feasible
            if is_feasible:
                recommendations.append("\nSuggestion: Proceed to Optimization to solve the model.")
            else:
                recommendations.append("\nSuggestion: Address the issues above before proceeding to optimization.")
            
            # Update the recommendations label
            self.recommendations_label.setText("\n".join(recommendations))
            
        except Exception as e:
            print(f"Error updating recommendations: {e}")
            self.recommendations_label.setText(f"Error generating recommendations: {str(e)}")

    def update_validation_status(self):
        """
        Update the validation status based on current data.
        This method is called from the main window when data is loaded.
        """
        try:
            # Check if data is available by trying to refresh data
            data_available = self._refresh_data()
            if data_available:
                # If data is available, run validation
                self._run_validation()
            else:
                # If data is not available, reset the validation status
                self.feasibility_card.set_status("neutral")
                feasibility_label = self.feasibility_card.property("status_label")
                if feasibility_label:
                    feasibility_label.setText("Not Validated")
                
                # Reset other cards
                issues_label = self.issues_card.property("status_label")
                warnings_label = self.warnings_card.property("status_label")
                
                if issues_label:
                    issues_label.setText("0")
                    self.issues_card.set_status("success")
                    
                if warnings_label:
                    warnings_label.setText("0")
                    self.warnings_card.set_status("success")
                    
                # Reset recommendations
                self.recommendations_label.setText("Run validation to see recommendations.")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in update_validation_status: {e}")
            # Reset to a safe state
            self.feasibility_card.set_status("neutral")
            self.recommendations_label.setText("An error occurred during validation. Please try again.") 