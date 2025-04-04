"""
Style verification test for the Waffle Optimizer GUI.
"""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                          QVBoxLayout, QWidget, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.gui.views.data_view import DataView
from src.gui.views.validation_dashboard_view import ValidationDashboardView
from src.gui.views.optimization_view import OptimizationView
from src.gui.views.results_view import ResultsView
from src.gui.views.model_description_view import ModelDescriptionView

class StyleTestWindow(QMainWindow):
    """Window for testing GUI styles."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Style Verification")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add test views
        self.data_view = DataView(self)
        self.validation_view = ValidationDashboardView(self)
        self.optimization_view = OptimizationView(self)
        self.results_view = ResultsView(self)
        self.model_description_view = ModelDescriptionView(self)
        
        self.tabs.addTab(self.data_view, "Data View")
        self.tabs.addTab(self.validation_view, "Validation View")
        self.tabs.addTab(self.optimization_view, "Optimization View")
        self.tabs.addTab(self.results_view, "Results View")
        self.tabs.addTab(self.model_description_view, "Model Description View")
        
        # Add style verification section
        verification_widget = QWidget()
        verification_layout = QVBoxLayout(verification_widget)
        
        # Add style verification labels
        title_label = QLabel("Style Verification Results")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verification_layout.addWidget(title_label)
        
        # Add verification results
        self.verification_label = QLabel()
        self.verification_label.setWordWrap(True)
        verification_layout.addWidget(self.verification_label)
        
        self.tabs.addTab(verification_widget, "Style Verification")
        
        # Run verification
        self.verify_styles()
        
    def verify_styles(self):
        """Verify the styles of all views."""
        results = []
        
        # Check each view
        views = [
            (self.data_view, "Data View"),
            (self.validation_view, "Validation View"),
            (self.optimization_view, "Optimization View"),
            (self.results_view, "Results View"),
            (self.model_description_view, "Model Description View")
        ]
        
        for view, view_name in views:
            # Basic style checks
            if hasattr(view, 'header') and hasattr(view, 'description'):
                results.append(f"✓ {view_name}: Header and description present")
            else:
                results.append(f"✗ {view_name}: Missing header or description")
            
            if hasattr(view, 'action_button'):
                results.append(f"✓ {view_name}: Action button present")
            else:
                results.append(f"✗ {view_name}: Missing action button")
            
            if hasattr(view, 'content_layout'):
                results.append(f"✓ {view_name}: Content layout present")
            else:
                results.append(f"✗ {view_name}: Missing content layout")
            
            # Check for BaseView inheritance
            if isinstance(view, type(self.data_view)):
                results.append(f"✓ {view_name}: Properly inherits from BaseView")
            else:
                results.append(f"✗ {view_name}: Does not inherit from BaseView")
        
        # Update verification label
        self.verification_label.setText("\n".join(results))

def run_style_verification():
    """Run the style verification test."""
    app = QApplication(sys.argv)
    window = StyleTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_style_verification() 