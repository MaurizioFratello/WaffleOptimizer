"""
Main entry point for the Waffle Optimizer GUI application.

This module contains the main entry point for the GUI application.
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main function to run the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 