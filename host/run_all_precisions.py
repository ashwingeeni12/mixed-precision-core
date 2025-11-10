"""
Run comprehensive test with all precisions (INT8, FP16, FP32)
This will run all 126 test cases (42 cases × 3 precisions)
"""
print("=" * 80)
print("FULL COMPREHENSIVE TEST - ALL PRECISIONS")
print("Running 126 test cases (42 cases × INT8, FP16, FP32)")
print("This will take approximately 2-4 hours")
print("=" * 80)
print()

import run_comprehensive_test
run_comprehensive_test.main()
