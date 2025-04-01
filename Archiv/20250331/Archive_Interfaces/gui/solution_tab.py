"""
Solution tab for the waffle optimizer GUI.

This module contains the SolutionTab class which is the main tab for
displaying optimization results.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
import sys
from gui.widgets.solution_view import SolutionView


class SolutionTab(QWidget):
    """Solution tab for the waffle optimizer GUI."""
    
    def __init__(self):
        """Initialize the solution tab."""
        super().__init__()
        
        # Set up UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions label
        instructions = QLabel(
            "Run optimization from the Configuration tab to see results here."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("font-size: 14px; color: #666666; padding: 20px;")
        layout.addWidget(instructions)
        
        # Solution view
        self.solution_view = SolutionView()
        layout.addWidget(self.solution_view)
    
    def display_solution(self, solution):
        """
        Display the optimization solution.
        
        Args:
            solution: The optimization solution dictionary.
        """
        try:
            self.solution_view.display_solution(solution)
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error displaying solution: {str(e)}"
            ) 