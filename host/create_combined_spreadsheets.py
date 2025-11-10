"""
Create combined spreadsheets with A, B, and C matrices side-by-side
Generates one Excel file per test case with all three matrices
"""
import os
import json
import struct
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = ROOT / "archived_matrices"
OUTPUT_DIR = ROOT / "combined_spreadsheets"

OUTPUT_DIR.mkdir(exist_ok=True)

def hex_to_float(hex_str, precision):
    """Convert hex string to float based on precision"""
    val = int(hex_str, 16)

    if precision == 'int8':
        # INT8: stored in lower 8 bits
        if val & 0x80:
            return val - 256
        return val
    elif precision == 'fp16':
        # FP16: stored in lower 16 bits
        bits = val & 0xFFFF
        # Convert to FP32 for processing (simple approach)
        return struct.unpack('!f', struct.pack('!I', bits << 16))[0]
    elif precision == 'fp32':
        # FP32: full 32 bits
        return struct.unpack('!f', struct.pack('!I', val))[0]

    return 0

def read_mem_file(mem_path, M, N, precision):
    """Read .mem file and return as matrix"""
    with open(mem_path, 'r') as f:
        hex_values = [line.strip() for line in f if line.strip()]

    # Convert hex to floats
    values = [hex_to_float(h, precision) for h in hex_values[:M*N]]

    # Reshape to matrix
    matrix = np.array(values).reshape(M, N)
    return matrix

def create_combined_spreadsheet(case_dir, output_path):
    """Create Excel file with A, B, C matrices side-by-side"""

    # Read metadata
    with open(case_dir / "metadata.json") as f:
        meta = json.load(f)

    M = meta['M']
    K = meta['K']
    N = meta['N']
    prec = meta['precision']

    # Read matrices
    A = read_mem_file(case_dir / "A.mem", M, K, prec)
    B = read_mem_file(case_dir / "B.mem", K, N, prec)
    C_ref = np.loadtxt(case_dir / "C_ref.csv", delimiter=',')

    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

        # Sheet 1: Side-by-side matrices
        df_combined = pd.DataFrame()

        # Add A matrix
        for i in range(M):
            df_combined[f'A_col{i}'] = A[:, i]

        # Add separator
        df_combined['|'] = ['|'] * M

        # Add B matrix
        for i in range(N):
            df_combined[f'B_col{i}'] = B[:, i]

        # Add separator
        df_combined['||'] = ['||'] * M

        # Add C matrix
        for i in range(N):
            df_combined[f'C_col{i}'] = C_ref[:, i]

        df_combined.to_excel(writer, sheet_name='A_B_C_Combined', index=False)

        # Sheet 2: Metadata
        df_meta = pd.DataFrame([
            ['Case ID', meta['case_id']],
            ['Category', meta['category']],
            ['Precision', meta['precision']],
            ['Matrix Size', f'{M}x{K} × {K}x{N} = {M}x{N}'],
            [''],
            ['Requested cond(A)', meta['requested_cond_A']],
            ['Requested cond(B)', meta['requested_cond_B']],
            ['Actual cond(A)', f"{meta['actual_cond_A']:.4f}"],
            ['Actual cond(B)', f"{meta['actual_cond_B']:.4f}"],
            [''],
            ['A min', f"{meta['A_min']:.6f}"],
            ['A max', f"{meta['A_max']:.6f}"],
            ['A mean', f"{meta['A_mean']:.6f}"],
            ['A std', f"{meta['A_std']:.6f}"],
            [''],
            ['B min', f"{meta['B_min']:.6f}"],
            ['B max', f"{meta['B_max']:.6f}"],
            ['B mean', f"{meta['B_mean']:.6f}"],
            ['B std', f"{meta['B_std']:.6f}"],
            [''],
            ['C_ref min', f"{meta['C_ref_min']:.6f}"],
            ['C_ref max', f"{meta['C_ref_max']:.6f}"],
            ['C_ref mean', f"{meta['C_ref_mean']:.6f}"],
            ['C_ref std', f"{meta['C_ref_std']:.6f}"],
            ['C_ref norm', f"{meta['C_ref_norm']:.6f}"],
        ], columns=['Property', 'Value'])

        df_meta.to_excel(writer, sheet_name='Metadata', index=False)

        # Sheet 3: Individual matrices (cleaner view)
        # A matrix
        df_A = pd.DataFrame(A, columns=[f'col{i}' for i in range(K)])
        df_A.to_excel(writer, sheet_name='Matrix_A', index=False)

        # B matrix
        df_B = pd.DataFrame(B, columns=[f'col{i}' for i in range(N)])
        df_B.to_excel(writer, sheet_name='Matrix_B', index=False)

        # C matrix
        df_C = pd.DataFrame(C_ref, columns=[f'col{i}' for i in range(N)])
        df_C.to_excel(writer, sheet_name='Matrix_C_ref', index=False)

print("=" * 80)
print("CREATING COMBINED SPREADSHEETS")
print(f"Reading from: {ARCHIVE_DIR}")
print(f"Writing to: {OUTPUT_DIR}")
print("=" * 80)

# Get all case directories
case_dirs = sorted([d for d in ARCHIVE_DIR.iterdir() if d.is_dir() and d.name.startswith('case_')])

count = 0
total = len(case_dirs)

for case_dir in case_dirs:
    count += 1
    case_name = case_dir.name

    try:
        output_file = OUTPUT_DIR / f"{case_name}.xlsx"
        print(f"[{count}/{total}] Creating {case_name}.xlsx...")
        create_combined_spreadsheet(case_dir, output_file)
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 80)
print(f"Created {count} spreadsheets in: {OUTPUT_DIR}")
print("=" * 80)
print("\nEach spreadsheet contains:")
print("  - Sheet 1: A, B, C matrices side-by-side")
print("  - Sheet 2: Metadata (condition numbers, statistics)")
print("  - Sheet 3-5: Individual matrices (A, B, C)")
