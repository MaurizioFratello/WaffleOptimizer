"""
Main window implementation for the Waffle Optimizer GUI.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, 
                           QStackedWidget, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os

from .views.dashboard_view import DashboardView
from .views.data_view import DataView
from .views.validation_dashboard_view import ValidationDashboardView
from .views.optimization_view import OptimizationView
from .views.results_view import ResultsView
from .views.model_description_view import ModelDescriptionView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waffle Production Optimizer")
        self.setMinimumSize(1024, 768)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # Create main content area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
        
        # Initialize views
        self._init_views()
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #2980b9;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """)
    
    def _create_sidebar(self):
        """Create the sidebar navigation widget."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            #sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/title
        logo = QLabel("Waffle Optimizer")
        logo.setStyleSheet("""
            color: white;
            font-size: 18px;
            padding: 20px;
            background-color: #243342;
        """)
        layout.addWidget(logo)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "dashboard"),
            ("Data", "data"),
            ("Validation", "validation"),
            ("Optimization", "optimization"),
            ("Results", "results"),
            ("Model Description", "model_description")
        ]
        
        for text, name in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(f"nav_{name}")
            btn.setStyleSheet("""
                text-align: left;
                padding: 12px 15px;
                border: none;
                color: #ecf0f1;
                background-color: transparent;
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self._switch_view(n))
            layout.addWidget(btn)
        
        # Add stretch to push remaining items to bottom
        layout.addStretch()
        
        # Settings button at bottom
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("""
            text-align: left;
            padding: 12px 15px;
            border: none;
            color: #ecf0f1;
            background-color: transparent;
        """)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(settings_btn)
        
        return sidebar
    
    def _init_views(self):
        """Initialize the main content views."""
        # Create views - passing self allows views to access main window methods
        self.dashboard_view = DashboardView(self)
        self.data_view = DataView(self)
        self.validation_view = ValidationDashboardView(self)
        self.optimization_view = OptimizationView(self)
        self.results_view = ResultsView(self)
        self.model_description_view = ModelDescriptionView(self)
        
        # Add views to stack
        self.content_stack.addWidget(self.dashboard_view)
        self.content_stack.addWidget(self.data_view)
        self.content_stack.addWidget(self.validation_view)
        self.content_stack.addWidget(self.optimization_view)
        self.content_stack.addWidget(self.results_view)
        self.content_stack.addWidget(self.model_description_view)
        
        # Set initial view
        self._switch_view("dashboard")
    
    def _switch_view(self, view_name):
        """Switch to the specified view."""
        view_map = {
            "dashboard": 0,
            "data": 1,
            "validation": 2,
            "optimization": 3,
            "results": 4,
            "model_description": 5
        }
        
        if view_name in view_map:
            print(f"Switching to view: {view_name}")
            self.content_stack.setCurrentIndex(view_map[view_name])
            
            # Special handling for model description view to ensure it's visible
            if view_name == "model_description":
                print("Model description view selected")
                # No need to reload, just ensure it's visible
                self.model_description_view.setFocus()
            
            # Special handling for validation view - Only load the data, don't run validation
            if view_name == "validation" and hasattr(self, 'validation_view'):
                # Just load current data paths for reference
                self.validation_view.data_paths = self.data_view.get_data_paths()
            
            # Update button styles
            for i in range(self.sidebar.layout().count()):
                widget = self.sidebar.layout().itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    widget.setStyleSheet("""
                        text-align: left;
                        padding: 12px 15px;
                        border: none;
                        color: #ecf0f1;
                        background-color: transparent;
                    """)
            
            # Highlight active button
            active_btn = self.sidebar.findChild(QPushButton, f"nav_{view_name}")
            if active_btn:
                active_btn.setStyleSheet("""
                    text-align: left;
                    padding: 12px 15px;
                    border: none;
                    color: #ecf0f1;
                    background-color: #34495e;
                """) 