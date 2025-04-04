"""
Simple script to run the Waffle Optimizer application for testing.

This script provides a convenient way to start the application from the tests directory.
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def run_application():
    """Run the Waffle Optimizer application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_application() 