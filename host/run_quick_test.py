"""
Quick test - runs just 3 test cases to verify workflow
Modified version of run_comprehensive_test.py with limited tests
"""
import os
import sys
from pathlib import Path

# Modify the test range before importing
os.environ['QUICK_TEST'] = 'true'
os.environ['MAX_CASES'] = '3'  # Only run first 3 cases

print("=" * 80)
print("QUICK TEST MODE - Running first 9 tests (cases 0-2, all precisions)")
print("This will take about 10-20 minutes")
print("=" * 80)
print()

# Now run the main test script
import run_comprehensive_test
run_comprehensive_test.main()
