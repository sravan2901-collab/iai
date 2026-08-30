"""
Master Test Runner for TC01 - TC20 Test Suite.
Executes all 20 test cases and outputs formatted summary table matching user specifications.
"""

import sys
import os
import unittest
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    print("=" * 110)
    print("AKSHARAI PLATFORM - TC01 TO TC20 EXHAUSTIVE TEST SUITE EXECUTION")
    print("=" * 110)

    start_time = time.time()

    suite = unittest.defaultTestLoader.discover(
        start_dir=os.path.dirname(__file__),
        pattern="test_tc01_tc20_suite.py"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total_time = time.time() - start_time
    print("\n" + "=" * 110)
    print("TC01 TO TC20 TEST SUITE SUMMARY & RESULT MATRIX")
    print("=" * 110)
    print(f"Total Test Cases Executed : {result.testsRun}")
    print(f"Passed Test Cases         : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed Test Cases         : {len(result.failures)}")
    print(f"Execution Errors          : {len(result.errors)}")
    print(f"Total Execution Time      : {total_time:.2f} seconds")
    print("=" * 110)

    if result.wasSuccessful():
        print("🎉 ALL 20 TEST CASES (TC01 - TC20) PASSED 100% SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ TEST MATRIX FAILED WITH ERRORS.")
        sys.exit(1)

if __name__ == "__main__":
    main()
