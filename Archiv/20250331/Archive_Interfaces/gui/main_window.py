"""
Main window for the waffle optimizer GUI.

This module contains the MainWindow class which is the main GUI component
for the waffle optimizer application.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from gui.config_tab import ConfigurationTab
from gui.solution_tab import SolutionTab


class MainWindow(QMainWindow):
    """Main window for the waffle optimizer GUI."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("Waffle Production Optimizer")
        self.setMinimumSize(1000, 700)
        
        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.config_tab = ConfigurationTab()
        self.solution_tab = SolutionTab()
        
        self.tabs.addTab(self.config_tab, "Configuration")
        self.tabs.addTab(self.solution_tab, "Solution")
        
        layout.addWidget(self.tabs)
        
        # Connect signals and slots for communication between tabs
        self.config_tab.solution_ready.connect(self.solution_tab.display_solution)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 6px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 