"""
File selector widget for choosing files with browse button.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal

class FileSelector(QWidget):
    """Widget for selecting a file with a browse button."""
    file_selected = pyqtSignal(str)
    
    def __init__(self, placeholder="Select a file...", filter="All Files (*)", parent=None):
        super().__init__(parent)
        
        self.filter = filter
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # File path input
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText(placeholder)
        self.file_path.setReadOnly(True)
        
        # Browse button
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._browse_file)
        
        # Add widgets to layout
        self.layout.addWidget(self.file_path, 3)
        self.layout.addWidget(self.browse_button, 1)
    
    def _browse_file(self):
        """Open file dialog to select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.filter
        )
        
        if file_path:
            self.file_path.setText(file_path)
            self.file_selected.emit(file_path)
    
    def get_file_path(self):
        """Get the selected file path."""
        return self.file_path.text()
    
    def set_file_path(self, path):
        """Set the file path programmatically."""
        self.file_path.setText(path)
        self.file_selected.emit(path) 