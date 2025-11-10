# Archived Test Matrices

This directory contains all 126 test matrices used in the comprehensive test suite.

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
    print(f"Condition number A: {meta['actual_cond_A']}")
    print(f"Condition number B: {meta['actual_cond_B']}")
```
