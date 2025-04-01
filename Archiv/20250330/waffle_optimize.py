#!/usr/bin/env python3
"""
Waffle Production Optimizer Entry Point

This script launches the optimization command-line interface.
It serves as a wrapper to maintain compatibility with existing usage.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the optimization package
from optimization.main import main

if __name__ == "__main__":
    main() 