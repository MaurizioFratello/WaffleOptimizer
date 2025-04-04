"""
GUI entry point for the Waffle Production Optimizer.
"""
import sys
from src.gui import WaffleOptimizerApp

def main():
    """Main entry point for the GUI application."""
    app = WaffleOptimizerApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main() 