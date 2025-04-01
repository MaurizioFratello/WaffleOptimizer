#!/usr/bin/env python
"""
Run all tests for the waffle optimizer.
"""
import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_all_tests():
    """Run all test cases in the tests directory."""
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    test_runner = unittest.TextTestRunner(verbosity=2)
    return test_runner.run(test_suite)

if __name__ == '__main__':
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1) 