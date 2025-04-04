"""
GUI entry point for the Waffle Production Optimizer.
"""
import sys
import os
import logging
from datetime import datetime
from pathlib import Path
from src.gui import WaffleOptimizerApp

def setup_logging():
    """Set up logging configuration for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"waffle_optimizer_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with DEBUG level
            logging.FileHandler(log_file),
            # Console handler with INFO level
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('src.solvers').setLevel(logging.DEBUG)
    logging.getLogger('src.data').setLevel(logging.DEBUG)
    logging.getLogger('src.gui').setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")
    logger.debug(f"Log file: {log_file}")

def main():
    """Main entry point for the GUI application."""
    # Set up logging
    setup_logging()
    
    # Create and run application
    logger = logging.getLogger(__name__)
    logger.info("Starting Waffle Production Optimizer")
    
    try:
        app = WaffleOptimizerApp()
        return_code = app.run()
        logger.info(f"Application exited with code {return_code}")
        sys.exit(return_code)
    except Exception as e:
        logger.error(f"Application crashed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 