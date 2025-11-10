"""
Run comprehensive test with INT8 precision only (FP16/FP32 require IP cores)
This will run 42 test cases with INT8 precision
"""
import os
os.environ['TEST_PRECISIONS'] = 'int8'  # Only test INT8

print("=" * 80)
print("INT8-ONLY TEST MODE")
print("Running 42 test cases with INT8 precision only")
print("(FP16 and FP32 require Xilinx IP cores that haven't been generated)")
print("=" * 80)
print()

import run_comprehensive_test
run_comprehensive_test.main()
