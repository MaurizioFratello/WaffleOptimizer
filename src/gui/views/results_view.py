"""
Results view for displaying optimization results.
"""
import os
import pandas as pd
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QGridLayout, QTabWidget,
                          QGroupBox, QComboBox, QFileDialog, QMessageBox, QWidget,
                          QStackedWidget)
from PyQt6.QtCore import Qt

from ..base_view import BaseView
from ..widgets.card_widget import CardWidget
from ..widgets.data_table import DataTable
from ..controllers.optimization_controller import OptimizationController

class ResultsView(BaseView):
    """
    View for displaying optimization results and exports.
    """
    
    def __init__(self, main_window=None):
        super().__init__(
            title="Optimization Results",
            description="View and export the results of your waffle production optimization.",
            main_window=main_window
        )
        
        # Reference to the optimization controller
        if main_window and hasattr(main_window, 'optimization_view'):
            self.optimization_controller = main_window.optimization_view.optimization_controller
        else:
            self.optimization_controller = OptimizationController()
        
        # Initialize results components
        self._init_results_components()
        
        # Connect to optimization controller
        if hasattr(self.optimization_controller, 'optimization_completed'):
            self.optimization_controller.optimization_completed.connect(self._on_optimization_completed)
    
    def _init_results_components(self):
        """Initialize results view specific components."""
        # Message when no results are available
        self.no_results_label = QLabel(
            "No optimization results available. Run an optimization in the Optimization tab first."
        )
        self.no_results_label.setWordWrap(True)
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setStyleSheet("font-size: 16px; color: #777; margin: 50px;")
        
        # Results container - will be populated when results are available
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        
        # Initially hide results container
        self.results_container.setVisible(False)
        self.content_layout.addWidget(self.no_results_label)
        self.content_layout.addWidget(self.results_container)
        
        # Create results view
        self._setup_results_view()
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self._export_results)
        self.export_button.setEnabled(False)
        
        self.back_button = QPushButton("Back to Optimization")
        self.back_button.clicked.connect(
            lambda: self.main_window._switch_view("optimization"))
        
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.back_button)
        
        self.content_layout.addLayout(button_layout)
    
    def _setup_results_view(self):
        """Set up the results display widgets."""
        # Summary cards
        summary_layout = QGridLayout()
        summary_layout.setSpacing(10)
        
        # Create metric cards
        self.objective_card = self._create_metric_card("Objective Value", "0")
        self.status_card = self._create_metric_card("Status", "Not Available")
        self.time_card = self._create_metric_card("Solve Time", "0 seconds")
        self.gap_card = self._create_metric_card("Optimality Gap", "0%")
        
        # Add cards to grid
        summary_layout.addWidget(self.objective_card, 0, 0)
        summary_layout.addWidget(self.status_card, 0, 1)
        summary_layout.addWidget(self.time_card, 1, 0)
        summary_layout.addWidget(self.gap_card, 1, 1)
        
        self.results_layout.addLayout(summary_layout)
        
        # Detailed results tabs
        self.results_tabs = QTabWidget()
        
        # Production table
        self.production_tab = QWidget()
        production_layout = QVBoxLayout(self.production_tab)
        self.production_table = DataTable()
        production_layout.addWidget(self.production_table)
        
        # Metrics table
        self.metrics_tab = QWidget()
        metrics_layout = QVBoxLayout(self.metrics_tab)
        self.metrics_table = DataTable()
        metrics_layout.addWidget(self.metrics_table)
        
        # Export options
        self.export_tab = QWidget()
        export_layout = QVBoxLayout(self.export_tab)
        
        export_form = self.create_group_box("Export Options")
        export_form_layout = QVBoxLayout(export_form)
        
        # Export format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        
        self.export_format = QComboBox()
        self.export_format.addItem("Excel (.xlsx)", "xlsx")
        self.export_format.addItem("CSV (.csv)", "csv")
        format_layout.addWidget(self.export_format)
        format_layout.addStretch()
        
        # Export path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path:"))
        
        self.export_path = QComboBox()
        self.export_path.setEditable(True)
        path_layout.addWidget(self.export_path, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_export_path)
        path_layout.addWidget(self.browse_button)
        
        # Export button
        export_button_layout = QHBoxLayout()
        export_button_layout.addStretch()
        
        self.export_tab_button = QPushButton("Export Now")
        self.export_tab_button.clicked.connect(self._export_results)
        export_button_layout.addWidget(self.export_tab_button)
        
        # Add layouts to form
        export_form_layout.addLayout(format_layout)
        export_form_layout.addLayout(path_layout)
        export_form_layout.addLayout(export_button_layout)
        
        export_layout.addWidget(export_form)
        export_layout.addStretch()
        
        # Add tabs
        self.results_tabs.addTab(self.production_tab, "Production Schedule")
        self.results_tabs.addTab(self.metrics_tab, "Optimization Metrics")
        self.results_tabs.addTab(self.export_tab, "Export Options")
        
        self.results_layout.addWidget(self.results_tabs)
    
    def _create_metric_card(self, title, value):
        """Create a card displaying a metric."""
        card = CardWidget(title=title)
        
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2980b9;
            margin: 10px 0;
        """)
        
        card.add_widget(value_label)
        card.setProperty("value_label", value_label)
        
        return card
    
    def _update_metric_card(self, card, value):
        """Update the value displayed in a metric card."""
        value_label = card.property("value_label")
        if value_label:
            value_label.setText(str(value))
    
    def _on_optimization_completed(self, results):
        """
        Update the view with the new optimization results.
        
        Args:
            results: Dictionary containing optimization results
        """
        # No more results available message
        self.no_results_label.setVisible(False)
        self.results_container.setVisible(True)
        
        # Enable export button
        self.export_button.setEnabled(True)
        
        # Get status first to determine how to handle other metrics
        status = results.get('status', 'Unknown')
        self._update_metric_card(self.status_card, status)
        
        # Update metric cards
        objective_value = results.get('objective_value', None)
        objective_type = results.get('objective_type', 'cost')
        
        # Handle objective value based on status
        if status in ['INFEASIBLE', 'UNBOUNDED', 'ABNORMAL', 'ERROR']:
            # For these statuses, there's no valid objective value
            objective_text = "N/A"
        else:
            # Only try to format the objective value if we have a valid status and value
            if objective_value is not None:
                # Format objective value with appropriate units
                if objective_type == 'cost':
                    objective_text = f"{objective_value:.2f} EUR"
                else:  # 'output' or any other type
                    objective_text = f"{objective_value:.0f} units"
            else:
                objective_text = "0.00 EUR"
            
        self._update_metric_card(self.objective_card, objective_text)
        
        solve_time = results.get('solve_time', 0)
        self._update_metric_card(self.time_card, f"{solve_time:.2f} seconds")
        
        gap = results.get('gap', 0)
        self._update_metric_card(self.gap_card, f"{gap * 100:.2f}%")
        
        # Update production table
        if "production" in results:
            self.production_table.load_dataframe(results["production"])
        else:
            # Clear the table if no production data
            self.production_table.load_dataframe(pd.DataFrame())
        
        # Update metrics table
        if "metrics" in results:
            # Convert metrics dict to DataFrame for display
            metrics_df = pd.DataFrame([results["metrics"]])
            self.metrics_table.load_dataframe(metrics_df)
        else:
            # Clear the table if no metrics data
            self.metrics_table.load_dataframe(pd.DataFrame())
        
        # Update export path
        output_path = results.get("output_path", "")
        if output_path:
            # Set as first item
            self.export_path.insertItem(0, output_path)
            self.export_path.setCurrentIndex(0)
            
            # Remove duplicates
            for i in range(1, self.export_path.count()):
                if self.export_path.itemText(i) == output_path:
                    self.export_path.removeItem(i)
                    break
    
    def set_results(self, results):
        """
        Set the optimization results to display in the view.
        This is called from the optimization view after optimization completes.
        
        Args:
            results: Dictionary containing optimization results
        """
        self._on_optimization_completed(results)
    
    def _browse_export_path(self):
        """Open a file dialog to select an export path."""
        file_format = self.export_format.currentData()
        
        if file_format == "xlsx":
            file_filter = "Excel Files (*.xlsx)"
        elif file_format == "csv":
            file_filter = "CSV Files (*.csv)"
        else:
            file_filter = "All Files (*)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Export File", "", file_filter
        )
        
        if file_path:
            self.export_path.setCurrentText(file_path)
    
    def _export_results(self):
        """Export the optimization results to a file."""
        # Get export path
        export_path = self.export_path.currentText()
        if not export_path:
            QMessageBox.warning(
                self, 
                "Export Error", 
                "Please specify an export file path."
            )
            return
        
        # Get export format
        export_format = self.export_format.currentData()
        
        # Call controller to export results
        success = self.optimization_controller.export_results(
            export_path, export_format
        )
        
        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"Results have been exported to {export_path}"
            )
        else:
            QMessageBox.warning(
                self,
                "Export Failed",
                "Failed to export results. Please check the path and try again."
            ) 