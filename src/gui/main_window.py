"""
Main window implementation for the Waffle Optimizer GUI.
"""
import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, 
                           QStackedWidget, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os

from .views.dashboard_view import DashboardView
from .views.data_view import DataView
from .views.validation_dashboard_view import ValidationDashboardView
from .views.optimization_view import OptimizationView
from .views.results_view import ResultsView
from .views.model_description_view import ModelDescriptionView
from .styles import AppStyles
from src.models.parameter_registry import ParameterRegistry
from src.models.data_model_service import DataModelService

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waffle Production Optimizer")
        self.setMinimumSize(1024, 768)
        
        # Initialize parameter registry
        self.param_registry = ParameterRegistry.get_instance()
        logger.debug("Parameter registry initialized")
        
        # Create data model service
        self.data_model_service = DataModelService()
        
        # Connect data service signals
        self.data_model_service.data_loaded.connect(self._on_data_loaded)
        self.data_model_service.data_error.connect(self._on_data_error)
        logger.debug("Data model service initialized")
        
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
        self._apply_stylesheet()
        
        logger.debug("Main window initialized")
    
    def _on_data_loaded(self):
        """Handle data loading completion."""
        logger.debug("Data loaded successfully")
        
        # Update views that depend on data
        if hasattr(self, 'validation_view'):
            logger.debug("Updating validation view")
            self.validation_view.update_validation_status()
        
        if hasattr(self, 'optimization_view'):
            logger.debug("Updating optimization view constraints")
            self.optimization_view.update_constraint_options()
    
    def _on_data_error(self, error_msg):
        """Handle data loading errors."""
        logger.error(f"Data loading error: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Data Loading Error",
            f"Error loading data: {error_msg}"
        )
    
    def _create_sidebar(self):
        """Create the sidebar navigation widget."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(int(AppStyles.SIDEBAR_WIDTH.replace("px", "")))
        sidebar.setStyleSheet(f"""
            #sidebar {{
                background-color: {AppStyles.TEXT_PRIMARY};
                border-right: 1px solid #34495e;
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/title
        logo = QLabel("Waffle Optimizer")
        logo.setStyleSheet(f"""
            color: white;
            font-size: 18px;
            padding: 20px;
            background-color: #243342;
        """)
        layout.addWidget(logo)
        
        # Navigation buttons
        nav_buttons = [
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
        
        return sidebar
    
    def _init_views(self):
        """Initialize the main content views."""
        logger.debug("Initializing views")
        
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
        
        # Connect data_view signals to data model service
        if hasattr(self.data_view, 'data_loaded'):
            self.data_view.data_loaded.connect(self._handle_data_view_loaded)
        
        # Set initial view
        self._switch_view("data")
    
    def _handle_data_view_loaded(self):
        """Handle data loaded signal from data view."""
        logger.debug("Data files selected in data view")
        
        # This is a bridge function to maintain backward compatibility
        # The data_view.data_loaded signal is now also listened to by the data model service
        pass
    
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
            logger.debug(f"Switching to view: {view_name}")
            self.content_stack.setCurrentIndex(view_map[view_name])
            
            # Special handling for model description view to ensure it's visible
            if view_name == "model_description":
                logger.debug("Model description view selected")
                # No need to reload, just ensure it's visible
                self.model_description_view.setFocus()
            
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
    
    def _apply_stylesheet(self):
        """
        Apply the base application style sheet.
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            
            QPushButton {
                padding: 8px 15px;
                border-radius: 3px;
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """) 