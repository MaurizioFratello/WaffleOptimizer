"""
Dashboard view for the Waffle Optimizer GUI.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt

from ..widgets.card_widget import CardWidget

class DashboardView(QWidget):
    """
    Dashboard view with quick access cards to main features.
    """
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Welcome header
        header = QLabel("Waffle Production Optimizer Dashboard")
        header.setObjectName("viewHeader")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        self.layout.addWidget(header)
        
        # Welcome message
        welcome = QLabel(
            "Welcome to the Waffle Production Optimizer. "
            "This tool helps optimize waffle production planning using "
            "mathematical optimization techniques."
        )
        welcome.setWordWrap(True)
        self.layout.addWidget(welcome)
        
        # Grid layout for cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        # Create cards
        self.data_card = CardWidget(
            title="Configure Data",
            action_text="Open Data View"
        )
        desc_label = QLabel(
            "Set up input data files for demand, supply, cost, and other parameters."
        )
        desc_label.setWordWrap(True)
        self.data_card.add_widget(desc_label)
        self.data_card.clicked.connect(lambda: self._navigate_to("data"))
        
        self.optimization_card = CardWidget(
            title="Run Optimization",
            action_text="Open Optimization View"
        )
        desc_label = QLabel(
            "Configure and run waffle production optimization with different objectives and solvers."
        )
        desc_label.setWordWrap(True)
        self.optimization_card.add_widget(desc_label)
        self.optimization_card.clicked.connect(lambda: self._navigate_to("optimization"))
        
        self.results_card = CardWidget(
            title="View Results",
            action_text="Open Results View"
        )
        desc_label = QLabel(
            "View optimization results including production schedules, metrics, and export options."
        )
        desc_label.setWordWrap(True)
        self.results_card.add_widget(desc_label)
        self.results_card.clicked.connect(lambda: self._navigate_to("results"))
        
        self.model_desc_card = CardWidget(
            title="Model Description",
            action_text="View Model Details"
        )
        desc_label = QLabel(
            "Learn about the mathematical optimization model used in this application."
        )
        desc_label.setWordWrap(True)
        self.model_desc_card.add_widget(desc_label)
        self.model_desc_card.clicked.connect(lambda: self._navigate_to("model_description"))
        
        # Add cards to grid
        cards_layout.addWidget(self.data_card, 0, 0)
        cards_layout.addWidget(self.optimization_card, 0, 1)
        cards_layout.addWidget(self.results_card, 1, 0)
        cards_layout.addWidget(self.model_desc_card, 1, 1)
        
        # Add cards layout to main layout
        self.layout.addLayout(cards_layout, 1)  # 1 = stretch factor
    
    def _navigate_to(self, view_name):
        """Navigate to the specified view."""
        if self.main_window:
            self.main_window._switch_view(view_name) 