import sys
import os
import time

# Force stdout to UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Adjust python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_week1_week2_comprehensive import run_comprehensive_week1_week2_tests

def run_100_test_iterations():
    print("=" * 100)
    print("      AKSHARAI 100-ITERATION AUTOMATED CONTINUOUS VERIFICATION & AUDIT LOOP")
    print("=" * 100)

    start_time = time.time()
    successful_iterations = 0
    total_iterations = 100

    for i in range(1, total_iterations + 1):
        print(f"\n[ITERATION {i:03d}/{total_iterations:03d}] Executing Comprehensive Multilingual Test Suite...")
        try:
            run_comprehensive_week1_week2_tests()
            successful_iterations += 1
            print(f"[ITERATION {i:03d}/{total_iterations:03d}] -> PASSED CLEANLY (100% SUCCESS RATE)")
        except Exception as e:
            print(f"[ITERATION {i:03d}/{total_iterations:03d}] -> FAILED with error: {e}")
            break

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 100)
    print(f"       100-ITERATION AUDIT SUMMARY: {successful_iterations}/{total_iterations} PASSED ({elapsed}s)")
    print("=" * 100)

if __name__ == '__main__':
    run_100_test_iterations()
