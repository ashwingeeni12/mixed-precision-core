"""
Archive all test matrices for all 126 test cases
Saves A, B, C_ref for each case_id and precision
"""
import os
import json
import shutil
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = ROOT / "archived_matrices"

# Create archive directory structure
ARCHIVE_DIR.mkdir(exist_ok=True)

# Test configuration
precisions = ['int8', 'fp16', 'fp32']
num_cases = 42

print("=" * 80)
print("ARCHIVING ALL TEST MATRICES")
print(f"Generating and saving {num_cases * len(precisions)} test matrices")
print(f"Output directory: {ARCHIVE_DIR}")
print("=" * 80)

os.chdir(ROOT / "host")

total = num_cases * len(precisions)
count = 0

for case_id in range(num_cases):
    for prec in precisions:
        count += 1
        print(f"\n[{count}/{total}] Archiving Case {case_id}, Precision {prec}...")

        # Generate matrices
        ret = os.system(f'python gen_cond_mems.py --M 8 --K 8 --N 8 --prec {prec} --case-id {case_id} >nul 2>&1')
        if ret != 0:
            print(f"  ERROR: Failed to generate matrices")
            continue

        # Create archive subdirectory
        archive_case_dir = ARCHIVE_DIR / f"case_{case_id:03d}_{prec}"
        archive_case_dir.mkdir(exist_ok=True)

        # Copy files
        try:
            shutil.copy(ROOT / "mem" / "A.mem", archive_case_dir / "A.mem")
            shutil.copy(ROOT / "mem" / "B.mem", archive_case_dir / "B.mem")
            shutil.copy(ROOT / "mem" / "C_ref.csv", archive_case_dir / "C_ref.csv")
            shutil.copy(ROOT / "mem" / "test_metadata.json", archive_case_dir / "metadata.json")

            # Also save in numpy format for easy loading
            with open(ROOT / "mem" / "test_metadata.json") as f:
                meta = json.load(f)

            # Read C_ref.csv and save as .npy
            C_ref = np.loadtxt(ROOT / "mem" / "C_ref.csv", delimiter=',')
            np.save(archive_case_dir / "C_ref.npy", C_ref)

            print(f"  Saved to {archive_case_dir.name}/")

        except Exception as e:
            print(f"  ERROR: {e}")

print("\n" + "=" * 80)
print(f"Archive complete!")
print(f"Saved {count} test cases to: {ARCHIVE_DIR}")
print("=" * 80)

# Create README
readme_path = ARCHIVE_DIR / "README.md"
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(f"""# Archived Test Matrices

This directory contains all {num_cases * len(precisions)} test matrices used in the comprehensive test suite.

## Directory Structure

```
archived_matrices/
├── case_000_int8/    # Case 0, INT8 precision
│   ├── A.mem         # Input matrix A (hex format)
│   ├── B.mem         # Input matrix B (hex format)
│   ├── C_ref.csv     # Reference output (CSV)
│   ├── C_ref.npy     # Reference output (NumPy)
│   └── metadata.json # Test metadata
├── case_000_fp16/    # Case 0, FP16 precision
│   └── ...
├── case_000_fp32/    # Case 0, FP32 precision
│   └── ...
...
└── case_041_fp32/    # Case 41, FP32 precision (high condition)
    └── ...
```

## Test Cases

- Cases 0-13: Low condition number (1-10)
- Cases 14-27: Medium condition number (10-100)
- Cases 28-41: High condition number (100-1000)

Each case tests 3 precisions: INT8, FP16, FP32

## File Formats

- `.mem` files: Hexadecimal format for hardware simulation
- `.csv` files: Comma-separated values (human readable)
- `.npy` files: NumPy binary format (for Python analysis)
- `.json` files: Test metadata including actual condition numbers

## Loading Matrices in Python

```python
import numpy as np
import json

# Load reference output
C_ref = np.load('case_000_fp32/C_ref.npy')

# Load metadata
with open('case_000_fp32/metadata.json') as f:
    meta = json.load(f)
    print(f"Condition number A: {{meta['actual_cond_A']}}")
    print(f"Condition number B: {{meta['actual_cond_B']}}")
```
""")

print(f"\nCreated {readme_path}")
