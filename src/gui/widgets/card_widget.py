"""
Card widget for displaying content in a card-like container.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

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
            self.action_button.clicked.connect(self.clicked)
            self.layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Set default styling
        self.setStyleSheet("""
            #card {
                background-color: white;
                border-radius: 8px;
                min-height: 120px;
                border: 1px solid #ddd;
            }
            #cardTitle {
                font-size: 16px;
                font-weight: bold;
            }
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
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit clicked signal."""
        super().mousePressEvent(event)
        self.clicked.emit() 