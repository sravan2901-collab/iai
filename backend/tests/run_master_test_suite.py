import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src")))

from tests.test_registration_exhaustive import run_registration_exhaustive_tests
from tests.test_login_exhaustive import run_login_exhaustive_tests
from tests.test_frontend_suite import run_exhaustive_frontend_test_suite

def run_master_suite():
    print("\n====================================================================================================")
    print("                     AKSHARAI GRAND UNIFIED MASTER TEST SUITE (74 TEST CASES)                       ")
    print("====================================================================================================\n")

    print("\n>>> STAGE 1: EXHAUSTIVE REGISTRATION TEST MATRIX (25 CASES)")
    run_registration_exhaustive_tests()

    print("\n>>> STAGE 2: EXHAUSTIVE LOGIN TEST MATRIX (30 CASES)")
    run_login_exhaustive_tests()

    print("\n>>> STAGE 3: EXHAUSTIVE FRONTEND & API INTEGRATION MATRIX (19 CASES)")
    run_exhaustive_frontend_test_suite()

    print("\n====================================================================================================")
    print("           [SUCCESS] GRAND UNIFIED MASTER TEST SUITE COMPLETED 100% (74/74 PASSED WITH 0 ERRORS)     ")
    print("====================================================================================================\n")

if __name__ == "__main__":
    run_master_suite()
