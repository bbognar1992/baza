#!/usr/bin/env python3
"""
Test runner script for ÉpítAI Construction Management System
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def discover_tests(test_dir="tests", pattern="test_*.py"):
    """Discover all test files in the test directory"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), test_dir)
    suite = loader.discover(start_dir, pattern=pattern)
    return suite

def discover_simple_tests():
    """Discover simple test files that don't use FastAPI TestClient"""
    loader = unittest.TestLoader()
    test_files = [
        "tests.test_user_service"
    ]
    
    suite = unittest.TestSuite()
    for test_file in test_files:
        try:
            suite.addTests(loader.loadTestsFromName(test_file))
        except Exception as e:
            print(f"Warning: Could not load {test_file}: {e}")
    
    return suite

def run_tests(test_pattern=None, verbosity=2, failfast=False, simple_only=False):
    """Run tests with specified options"""
    print("🧪 Running ÉpítAI Construction Management System Tests")
    print("=" * 60)
    
    # Discover tests
    if simple_only:
        suite = discover_simple_tests()
    elif test_pattern:
        suite = discover_tests(pattern=f"test_{test_pattern}.py")
    else:
        # Try to run both simple and complex tests
        suite = discover_simple_tests()
        try:
            complex_suite = discover_tests()
            suite.addTests(complex_suite)
        except Exception as e:
            print(f"Note: Some tests may not be available due to dependencies: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=True
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {len(result.failures + result.errors)} test(s) failed!")
        return 1

def run_specific_test(test_module, test_class=None, test_method=None):
    """Run a specific test"""
    print(f"🎯 Running specific test: {test_module}")
    if test_class:
        print(f"  Class: {test_class}")
    if test_method:
        print(f"  Method: {test_method}")
    print("=" * 60)
    
    # Import the test module
    try:
        module = __import__(f"tests.{test_module}", fromlist=[test_class or ""])
    except ImportError as e:
        print(f"❌ Error importing test module: {e}")
        return 1
    
    # Get the test class
    if test_class:
        try:
            test_class_obj = getattr(module, test_class)
        except AttributeError:
            print(f"❌ Test class '{test_class}' not found in module")
            return 1
    else:
        # Find the first test class in the module
        test_classes = [name for name in dir(module) if name.startswith('Test')]
        if not test_classes:
            print("❌ No test classes found in module")
            return 1
        test_class_obj = getattr(module, test_classes[0])
    
    # Create test suite
    if test_method:
        suite = unittest.TestSuite()
        suite.addTest(test_class_obj(test_method))
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class_obj)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for ÉpítAI Construction Management System")
    parser.add_argument(
        "--pattern", "-p",
        help="Run tests matching pattern (e.g., 'users' for test_users.py)"
    )
    parser.add_argument(
        "--module", "-m",
        help="Run specific test module (e.g., 'api.v1.endpoints.test_users')"
    )
    parser.add_argument(
        "--class", "-c",
        dest="test_class",
        help="Run specific test class"
    )
    parser.add_argument(
        "--method", "-t",
        help="Run specific test method"
    )
    parser.add_argument(
        "--verbosity", "-v",
        type=int,
        default=2,
        choices=[0, 1, 2],
        help="Test verbosity level (0=quiet, 1=normal, 2=verbose)"
    )
    parser.add_argument(
        "--failfast", "-f",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--simple", "-s",
        action="store_true",
        help="Run only simple tests (service layer tests)"
    )
    
    args = parser.parse_args()
    
    # Check if we're running a specific test
    if args.module:
        return run_specific_test(args.module, args.test_class, args.method)
    
    # Run all tests or filtered tests
    return run_tests(args.pattern, args.verbosity, args.failfast, args.simple)

if __name__ == "__main__":
    sys.exit(main())
