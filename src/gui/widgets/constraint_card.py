"""
Card widget for displaying constraints in a responsive grid layout.
"""
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QCheckBox, QGroupBox, QFormLayout,
                          QToolButton, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

class ConstraintCard(QFrame):
    """A card widget representing a single constraint with compact view."""
    
    # Signals
    config_clicked = pyqtSignal(dict)
    toggle_clicked = pyqtSignal(str, bool)
    
    def __init__(self, constraint_info, parent=None):
        super().__init__(parent)
        self.constraint_info = constraint_info
        self.is_expanded = False
        self.metrics_data = {}  # Store metrics data
        self.setup_ui()
        
    def setup_ui(self):
        # Set frame appearance
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setObjectName("constraintCard")
        self.setMinimumSize(250, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)
        
        # Header with title and status
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Format constraint name for display
        display_name = self.constraint_info.get('display_name', self.constraint_info['name'])
        title = QLabel(display_name)
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Status indicator
        enabled = self.constraint_info.get('enabled', False)
        self.status_label = QLabel("✓ Active" if enabled else "✗ Off")
        self.status_label.setStyleSheet(
            "color: #27ae60;" if enabled else "color: #7f8c8d;"
        )
        header_layout.addWidget(self.status_label)
        
        # Toggle button
        self.toggle_checkbox = QCheckBox()
        self.toggle_checkbox.setChecked(enabled)
        self.toggle_checkbox.stateChanged.connect(self.on_toggle_changed)
        header_layout.addWidget(self.toggle_checkbox)
        
        # Expand button
        self.expand_button = QToolButton()
        self.expand_button.setText("▼")
        self.expand_button.setToolTip("Show details")
        self.expand_button.setCheckable(True)
        self.expand_button.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.expand_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Add horizontal line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)
        
        # Status metrics (compact view)
        self.metrics_label = QLabel(self.get_status_text())
        self.metrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metrics_label.setStyleSheet("color: #555;")
        self.main_layout.addWidget(self.metrics_label)
        
        # Configuration button
        self.config_button = QPushButton("⚙ Configure")
        self.config_button.setObjectName("configureButton")
        self.config_button.clicked.connect(self.on_config_clicked)
        self.main_layout.addWidget(self.config_button)
        
        # Create expandable details container (initially hidden)
        self.details_container = QGroupBox()
        self.details_container.setObjectName("cardDetails")
        self.details_layout = QVBoxLayout(self.details_container)
        
        # Add description
        if 'description' in self.constraint_info:
            desc = QLabel(self.constraint_info['description'])
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666;")
            self.details_layout.addWidget(desc)
        
        # Add configuration summary if available
        if 'config' in self.constraint_info and self.constraint_info['config']:
            config_group = QGroupBox("Current Configuration")
            config_layout = QFormLayout(config_group)
            
            for key, value in self.constraint_info['config'].items():
                display_key = key.replace('_', ' ').title()
                label = QLabel(f"{display_key}:")
                value_label = QLabel(str(value))
                config_layout.addRow(label, value_label)
                
            self.details_layout.addWidget(config_group)
        
        # Add metrics details section (initially empty)
        self.metrics_details = QGroupBox("Performance Metrics")
        self.metrics_details_layout = QFormLayout(self.metrics_details)
        self.details_layout.addWidget(self.metrics_details)
        self.metrics_details.setVisible(False)  # Hide until we have data
        
        self.details_container.setVisible(False)
        self.main_layout.addWidget(self.details_container)
    
    def get_status_text(self):
        """Get a status text based on constraint type."""
        # Return placeholder text that will be replaced with real metrics
        constraint_type = self.constraint_info['name']
        
        if constraint_type == 'demand':
            return "N/A Met"
        elif constraint_type == 'supply':
            return "N/A Used"
        elif constraint_type == 'allowed_combinations':
            return "N/A Active"
        else:
            return "No metrics available"

    def update_metrics(self, optimization_results):
        """Update card metrics based on optimization results."""
        if not optimization_results:
            self.metrics_data = {}
            self.metrics_label.setText("No data available")
            self.metrics_details.setVisible(False)
            return
            
        constraint_type = self.constraint_info['name']
        
        # Extract real metrics from optimization results
        self.metrics_data = self._extract_metrics(optimization_results, constraint_type)
        
        # Update metrics display
        self.metrics_label.setText(self._format_metrics_text())
        
        # Update detailed metrics if expanded
        self._update_metrics_details()
        
        # Show metrics details if we have data
        self.metrics_details.setVisible(bool(self.metrics_data))
    
    def _extract_metrics(self, results, constraint_type):
        """Extract relevant metrics for this constraint type."""
        metrics = {}
        
        # This implementation would need to be customized based on actual result structure
        if 'constraints' not in results:
            return metrics
            
        constraints_data = results.get('constraints', {})
        
        if constraint_type == 'demand':
            # Extract demand satisfaction from solution
            if 'demand' in constraints_data:
                demand_data = constraints_data['demand']
                metrics['satisfaction'] = demand_data.get('satisfaction', 0)
                metrics['units_produced'] = demand_data.get('units_produced', 0)
                metrics['units_required'] = demand_data.get('units_required', 0)
        
        elif constraint_type == 'supply':
            # Extract supply utilization from solution
            if 'supply' in constraints_data:
                supply_data = constraints_data['supply']
                metrics['utilization'] = supply_data.get('utilization', 0)
                metrics['units_used'] = supply_data.get('units_used', 0)
                metrics['units_available'] = supply_data.get('units_available', 0)
        
        elif constraint_type == 'allowed_combinations':
            # Extract active combinations
            if 'allowed_combinations' in constraints_data:
                combo_data = constraints_data['allowed_combinations']
                metrics['active_count'] = combo_data.get('active_count', 0)
                metrics['total_pairs'] = combo_data.get('total_pairs', 0)
        
        return metrics
    
    def _format_metrics_text(self):
        """Format metrics data into display text."""
        if not self.metrics_data:
            return "No metrics available"
            
        constraint_type = self.constraint_info['name']
        
        if constraint_type == 'demand':
            satisfaction = self.metrics_data.get('satisfaction', 0)
            percentage = f"{satisfaction * 100:.1f}%" if isinstance(satisfaction, (int, float)) else "0%"
            return f"{percentage} Met"
            
        elif constraint_type == 'supply':
            utilization = self.metrics_data.get('utilization', 0)
            percentage = f"{utilization * 100:.1f}%" if isinstance(utilization, (int, float)) else "0%"
            return f"{percentage} Used"
            
        elif constraint_type == 'allowed_combinations':
            active = self.metrics_data.get('active_count', 0)
            return f"{active} Active"
            
        return "No metrics available"
    
    def _update_metrics_details(self):
        """Update the detailed metrics display in the expanded view."""
        # Clear existing items
        while self.metrics_details_layout.rowCount() > 0:
            self.metrics_details_layout.removeRow(0)
        
        # Add metrics details based on constraint type
        constraint_type = self.constraint_info['name']
        
        if constraint_type == 'demand':
            if 'satisfaction' in self.metrics_data:
                satisfaction = self.metrics_data['satisfaction']
                percentage = f"{satisfaction * 100:.1f}%"
                self.metrics_details_layout.addRow(QLabel("Satisfaction:"), QLabel(percentage))
            
            if 'units_produced' in self.metrics_data and 'units_required' in self.metrics_data:
                produced = self.metrics_data['units_produced']
                required = self.metrics_data['units_required']
                self.metrics_details_layout.addRow(QLabel("Units Produced:"), QLabel(f"{produced}"))
                self.metrics_details_layout.addRow(QLabel("Units Required:"), QLabel(f"{required}"))
        
        elif constraint_type == 'supply':
            if 'utilization' in self.metrics_data:
                utilization = self.metrics_data['utilization']
                percentage = f"{utilization * 100:.1f}%"
                self.metrics_details_layout.addRow(QLabel("Utilization:"), QLabel(percentage))
            
            if 'units_used' in self.metrics_data and 'units_available' in self.metrics_data:
                used = self.metrics_data['units_used']
                available = self.metrics_data['units_available']
                self.metrics_details_layout.addRow(QLabel("Units Used:"), QLabel(f"{used}"))
                self.metrics_details_layout.addRow(QLabel("Units Available:"), QLabel(f"{available}"))
        
        elif constraint_type == 'allowed_combinations':
            if 'active_count' in self.metrics_data and 'total_pairs' in self.metrics_data:
                active = self.metrics_data['active_count']
                total = self.metrics_data['total_pairs']
                self.metrics_details_layout.addRow(QLabel("Active Combinations:"), QLabel(f"{active}"))
                self.metrics_details_layout.addRow(QLabel("Total Possible:"), QLabel(f"{total}"))
                
                if total > 0:
                    percentage = f"{(active / total) * 100:.1f}%"
                    self.metrics_details_layout.addRow(QLabel("Usage:"), QLabel(percentage))
    
    def toggle_expanded(self, expanded=None):
        """Toggle the expanded state of the card."""
        if expanded is None:
            self.is_expanded = not self.is_expanded
        else:
            self.is_expanded = expanded
            
        self.details_container.setVisible(self.is_expanded)
        self.expand_button.setText("▲" if self.is_expanded else "▼")
        self.expand_button.setToolTip("Hide details" if self.is_expanded else "Show details")
        
        # Emit size change to trigger layout recalculation
        self.updateGeometry()
    
    def on_config_clicked(self):
        """Handle configuration button click."""
        self.config_clicked.emit(self.constraint_info)
    
    def on_toggle_changed(self, state):
        """Handle toggle state change."""
        enabled = state == Qt.CheckState.Checked.value
        self.toggle_clicked.emit(self.constraint_info['name'], enabled)
        
        # Update status label
        self.status_label.setText("✓ Active" if enabled else "✗ Off")
        self.status_label.setStyleSheet(
            "color: #27ae60;" if enabled else "color: #7f8c8d;"
        ) 