"""
Card widget for displaying content in a card-like container.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ..styles import AppStyles

class CardWidget(QFrame):
    """
    A card-like widget with optional title, icon, content, and action button.
    """
    clicked = pyqtSignal()
    
    def __init__(self, title=None, icon=None, action_text=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Setup layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Add header if title is provided
        if title or icon:
            header_layout = QHBoxLayout()
            
            if icon:
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(icon).pixmap(24, 24))
                header_layout.addWidget(icon_label)
            
            if title:
                title_label = QLabel(title)
                title_label.setObjectName("cardTitle")
                header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            self.layout.addLayout(header_layout)
        
        # Content container (will be filled by the user)
        self.content_container = QVBoxLayout()
        self.layout.addLayout(self.content_container)
        
        # Add action button if provided
        if action_text:
            self.action_button = QPushButton(action_text)
            self.action_button.setObjectName("cardActionButton")
            self.action_button.clicked.connect(self.clicked)
            self.layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Set default styling
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply the standardized styles to the card widget."""
        self.setStyleSheet(f"""
            #card {{
                background-color: {AppStyles.GROUP_BACKGROUND};
                border-radius: 8px;
                min-height: 120px;
                border: 1px solid {AppStyles.BORDER_COLOR};
            }}
            #cardTitle {{
                font-size: {AppStyles.GROUP_TITLE_SIZE};
                font-weight: {AppStyles.GROUP_TITLE_WEIGHT};
                color: {AppStyles.TEXT_PRIMARY};
            }}
            #cardActionButton {{
                {AppStyles.get_button_style(primary=False)}
            }}
            #cardActionButton:hover {{
                background-color: #f5f5f5;
            }}
        """)
    
    def add_widget(self, widget):
        """Add a widget to the card's content area."""
        self.content_container.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the card's content area."""
        self.content_container.addLayout(layout)
    
    def add_spacing(self, spacing):
        """Add spacing to the card's content area."""
        self.content_container.addSpacing(spacing)
    
    def clear_content(self):
        """Clear all content from the card."""
        while self.content_container.count():
            item = self.content_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_content(self, widget):
        """Set the content of the card, clearing any existing content."""
        self.clear_content()
        self.add_widget(widget)
    
    def set_status(self, status):
        """
        Set visual status of the card.
        
        Args:
            status (str): Status value ('success', 'warning', 'error', 'neutral')
        """
        status_colors = {
            'success': '#2ecc71',  # Green
            'warning': '#f39c12',  # Orange
            'error': '#e74c3c',    # Red
            'neutral': '#7f8c8d',  # Gray
        }
        color = status_colors.get(status, status_colors['neutral'])
        
        self.setStyleSheet(f"""
            #card {{
                background-color: {AppStyles.GROUP_BACKGROUND};
                border-radius: 8px;
                min-height: 120px;
                border: 1px solid {color};
                border-left: 4px solid {color};
            }}
            #cardTitle {{
                font-size: {AppStyles.GROUP_TITLE_SIZE};
                font-weight: {AppStyles.GROUP_TITLE_WEIGHT};
                color: {AppStyles.TEXT_PRIMARY};
            }}
            #cardActionButton {{
                {AppStyles.get_button_style(primary=False)}
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit clicked signal."""
        super().mousePressEvent(event)
        self.clicked.emit() 