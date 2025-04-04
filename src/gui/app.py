"""
Main application class for the Waffle Optimizer GUI.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .main_window import MainWindow

class WaffleOptimizerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')  # Modern look across platforms
        
        # Set application metadata
        self.app.setApplicationName("Waffle Production Optimizer")
        self.app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        self.main_window = MainWindow()
        self.main_window.show()
    
    def run(self):
        """Start the application event loop."""
        return self.app.exec() 