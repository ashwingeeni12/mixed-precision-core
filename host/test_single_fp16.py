"""
Test a single FP16 simulation
"""
import os
import sys
from pathlib import Path

# Change to project root
ROOT = Path(__file__).parent.parent
os.chdir(ROOT)

# Set environment variables
os.environ['PREC_SEL'] = '1'  # FP16
os.environ['M'] = '8'
os.environ['K'] = '8'
os.environ['N'] = '8'

print("=" * 80)
print("Testing single FP16 simulation")
print("=" * 80)

# Generate test matrices
print("\n1. Generating FP16 test matrices...")
os.chdir(ROOT / "host")
ret = os.system('python gen_cond_mems.py --M 8 --K 8 --N 8 --prec fp16 --case-id 0')
if ret != 0:
    print(f"ERROR: Matrix generation failed with code {ret}")
    sys.exit(1)

print("\n2. Running xsim simulation...")
os.chdir(ROOT)
ret = os.system('scripts\\run_xsim_simple.bat')
if ret != 0:
    print(f"ERROR: Simulation failed with code {ret}")
    sys.exit(1)

print("\n3. Parsing output...")
os.chdir(ROOT / "host")
ret = os.system('python parse_out_to_csv.py --M 8 --N 8 --prec fp16')
if ret != 0:
    print(f"ERROR: Parsing failed with code {ret}")
    sys.exit(1)

print("\n" + "=" * 80)
print("FP16 test completed successfully!")
print("=" * 80)
