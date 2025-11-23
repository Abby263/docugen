#!/usr/bin/env python3
"""
Test Runner

Run all unit and integration tests
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a test command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} - PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"✗ {description} - FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        return result.returncode == 0
    except Exception as e:
        print(f"✗ {description} - ERROR: {str(e)}")
        return False

def main():
    """Main test runner function"""
    print("Test Runner - Running All Tests")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    success_count = 0
    total_count = 0
    
    # Run unit tests
    print("\nRunning unit tests...")
    unit_tests = [
        ("python tests/unit/minimal_test.py", "Minimal Test"),
        ("python tests/unit/simple_test.py", "Simple Test"),
        ("python tests/unit/test_agents.py", "Agent Tests"),
        ("python tests/unit/test_simple_search.py", "Simple Search Test"),
    ]
    
    for cmd, desc in unit_tests:
        total_count += 1
        if run_command(cmd, desc):
            success_count += 1
    
    # Run integration tests
    print("\nRunning integration tests...")
    integration_tests = [
        ("python tests/integration/basic_test.py", "Basic Integration Test"),
        ("python tests/integration/basic_test_fixed.py", "Basic Test Fixed"),
        ("python tests/integration/debug_search.py", "Debug Search Test"),
        ("python tests/integration/test_deepsearch.py", "Deep Search Test"),
        ("python tests/integration/test_fixed_search.py", "Fixed Search Test"),
        ("python tests/integration/test_headless_issue.py", "Headless Issue Test"),
        ("python tests/integration/test_system_integration.py", "System Integration Test"),
    ]
    
    for cmd, desc in integration_tests:
        total_count += 1
        if run_command(cmd, desc):
            success_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    print(f"Total tests: {total_count}")
    print(f"Passed: {success_count}")
    print(f"Failed: {total_count - success_count}")
    print(f"Success rate: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())