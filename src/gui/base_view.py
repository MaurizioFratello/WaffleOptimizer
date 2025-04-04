"""
BaseView class to standardize the layout and styling of all application views.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QGroupBox)
from PyQt6.QtCore import Qt
from .styles import AppStyles

class BaseView(QWidget):
    """Base class for all application views with standardized styling and layout."""
    
    def __init__(self, title, description, main_window=None, action_button_text=None):
        """
        Initialize the base view with standard layout elements.
        
        Args:
            title (str): The title of the view
            description (str): Description text for the view
            main_window: Reference to the main window
            action_button_text (str, optional): Text for primary action button
        """
        super().__init__()
        self.main_window = main_window
        self._setup_base_layout(title, description, action_button_text)
        self.apply_styles()
        
    def _setup_base_layout(self, title, description, action_button_text):
        """Set up the standardized base layout for all views."""
        # Main layout with standardized margins
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            int(AppStyles.MARGIN.replace("px", "")),
            int(AppStyles.MARGIN.replace("px", "")),
            int(AppStyles.MARGIN.replace("px", "")),
            int(AppStyles.MARGIN.replace("px", ""))
        )
        self.layout.setSpacing(int(AppStyles.SPACING.replace("px", "")))
        
        # Top section layout
        self.top_layout = QHBoxLayout()
        
        # Header and description layout
        self.header_layout = QVBoxLayout()
        
        # Standard header
        self.header = QLabel(title)
        self.header.setObjectName("viewHeader")
        
        # Standard description
        self.description = QLabel(description)
        self.description.setWordWrap(True)
        self.description.setObjectName("viewDescription")
        
        # Add to header layout
        self.header_layout.addWidget(self.header)
        self.header_layout.addWidget(self.description)
        
        # Add to top layout
        self.top_layout.addLayout(self.header_layout, 1)
        
        # Action button (if applicable)
        if action_button_text:
            self.action_button = QPushButton(action_button_text)
            self.action_button.setObjectName("primaryActionButton")
            self.action_button.setMinimumWidth(
                int(AppStyles.BUTTON_MIN_WIDTH.replace("px", ""))
            )
            self.top_layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignRight)
        else:
            self.action_button = None
        
        # Add top layout to main layout
        self.layout.addLayout(self.top_layout)
        
        # Content area (to be implemented by child classes)
        self.content_layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout, 1)
        
    def create_group_box(self, title):
        """
        Create a standardized group box.
        
        Args:
            title (str): The title of the group box
            
        Returns:
            QGroupBox: A styled group box widget
        """
        group = QGroupBox(title)
        group.setObjectName("standardGroupBox")
        return group
        
    def apply_styles(self):
        """Apply the standardized styles to the view."""
        self.setStyleSheet(self._get_base_style_sheet())
        
    def _get_base_style_sheet(self):
        """Return the standardized style sheet."""
        return f"""
            #viewHeader {{
                {AppStyles.get_header_style()}
            }}
            #viewDescription {{
                {AppStyles.get_description_style()}
            }}
            #primaryActionButton {{
                {AppStyles.get_button_style(primary=True)}
            }}
            #primaryActionButton:hover {{
                background-color: {AppStyles.PRIMARY_DARK};
            }}
            #primaryActionButton:pressed {{
                background-color: {AppStyles.PRIMARY_DARKER};
            }}
            QGroupBox#standardGroupBox {{
                {AppStyles.get_group_box_style()}
            }}
            QGroupBox#standardGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: {AppStyles.TEXT_PRIMARY};
            }}
        """ 