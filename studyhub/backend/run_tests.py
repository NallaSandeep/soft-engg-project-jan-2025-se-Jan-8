"""Test runner script."""
import os
import sys
import pytest

def run_tests():
    """Run all tests."""
    # Set test environment
    os.environ['FLASK_ENV'] = 'testing'
    
    # Run tests with coverage
    args = [
        '--verbose',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html:coverage_report',
        'app/tests'
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == '__main__':
    sys.exit(run_tests()) 