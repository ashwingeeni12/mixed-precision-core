"""
Generate matrices with controlled condition numbers for comprehensive testing.
Creates 42 test cases with varying condition numbers (low, medium, high).
"""

import argparse
import struct
import random
import numpy as np
import csv
import json
from pathlib import Path

def f16_from_float(x: float) -> int:
    return int(np.float16(x).view('H'))

def f32_from_float(x: float) -> int:
    return struct.unpack('<I', struct.pack('<f', x))[0]

def generate_matrix_with_condition(M, N, cond_number, seed=None):
    """
    Generate a matrix with specified condition number using SVD.
    cond_number: desired condition number (ratio of largest to smallest singular value)
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate random orthogonal matrices U and V
    U, _ = np.linalg.qr(np.random.randn(M, min(M, N)))
    V, _ = np.linalg.qr(np.random.randn(N, min(M, N)))

    # Create singular values with specified condition number
    min_dim = min(M, N)
    sigma_max = 10.0  # Maximum singular value
    sigma_min = sigma_max / cond_number

    # Create singular values that decay from sigma_max to sigma_min
    singular_values = np.logspace(np.log10(sigma_max), np.log10(sigma_min), min_dim)

    # Construct the matrix
    S = np.zeros((M, N))
    for i in range(min_dim):
        S[i, i] = singular_values[i]

    A = U @ S @ V.T
    return A

def generate_test_cases(M, K, N):
    """
    Generate 42 test cases with different condition number configurations.

    Categories:
    - Low condition (1-10): 14 cases
    - Medium condition (10-100): 14 cases
    - High condition (100-1000): 14 cases
    """
    test_cases = []

    # Low condition numbers (well-conditioned)
    low_conds = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 10.0, 10.0, 10.0, 10.0]

    # Medium condition numbers
    medium_conds = [15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 100.0, 100.0, 100.0]

    # High condition numbers (ill-conditioned)
    high_conds = [150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1000.0, 1000.0, 1000.0]

    case_id = 0

    # Generate low condition cases
    for i, cond in enumerate(low_conds):
        test_cases.append({
            'id': case_id,
            'category': 'low',
            'cond_A': cond,
            'cond_B': cond,
            'seed': 1000 + case_id
        })
        case_id += 1

    # Generate medium condition cases
    for i, cond in enumerate(medium_conds):
        test_cases.append({
            'id': case_id,
            'category': 'medium',
            'cond_A': cond,
            'cond_B': cond,
            'seed': 1000 + case_id
        })
        case_id += 1

    # Generate high condition cases
    for i, cond in enumerate(high_conds):
        test_cases.append({
            'id': case_id,
            'category': 'high',
            'cond_A': cond,
            'cond_B': cond,
            'seed': 1000 + case_id
        })
        case_id += 1

    return test_cases

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--M', type=int, required=True)
    p.add_argument('--K', type=int, required=True)
    p.add_argument('--N', type=int, required=True)
    p.add_argument('--prec', choices=['int8','fp16','fp32'], required=True)
    p.add_argument('--case-id', type=int, required=True, help='Test case ID (0-41)')
    p.add_argument('--output-dir', type=str, default='../mem', help='Output directory for memory files')
    args = p.parse_args()

    M, K, N = args.M, args.K, args.N

    # Generate all test cases
    test_cases = generate_test_cases(M, K, N)

    if args.case_id < 0 or args.case_id >= len(test_cases):
        raise ValueError(f"case_id must be between 0 and {len(test_cases)-1}")

    case = test_cases[args.case_id]

    # Generate matrices with specified condition numbers
    np.random.seed(case['seed'])
    random.seed(case['seed'])

    # Generate A and B with specified condition numbers
    A = generate_matrix_with_condition(M, K, case['cond_A'], seed=case['seed'])
    B = generate_matrix_with_condition(K, N, case['cond_B'], seed=case['seed']+1)

    # Scale to appropriate range for precision
    if args.prec == 'int8':
        # Scale to int8 range and round
        A = np.clip(A * 2, -5, 5).astype(np.int8)
        B = np.clip(B * 2, -5, 5).astype(np.int8)
    else:
        # Keep in reasonable floating point range
        scale = 3.0
        A = A * scale / np.max(np.abs(A))
        B = B * scale / np.max(np.abs(B))

    # Compute actual condition numbers of final matrices
    try:
        actual_cond_A = np.linalg.cond(A)
        actual_cond_B = np.linalg.cond(B)
    except:
        actual_cond_A = -1
        actual_cond_B = -1

    # Write A.mem
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    with open(output_dir / 'A.mem', 'w') as fa:
        for i in range(M):
            for k in range(K):
                if args.prec == 'int8':
                    val = int(A[i,k]) & 0xff
                elif args.prec == 'fp16':
                    val = f16_from_float(float(A[i,k]))
                else:
                    val = f32_from_float(float(A[i,k]))
                fa.write(f"{val:08x}\n")

    # Write B.mem
    with open(output_dir / 'B.mem', 'w') as fb:
        for k in range(K):
            for j in range(N):
                if args.prec == 'int8':
                    val = int(B[k,j]) & 0xff
                elif args.prec == 'fp16':
                    val = f16_from_float(float(B[k,j]))
                else:
                    val = f32_from_float(float(B[k,j]))
                fb.write(f"{val:08x}\n")

    # Ground truth (float64 for maximum accuracy)
    C = A.astype(np.float64) @ B.astype(np.float64)

    with open(output_dir / 'C_ref.csv', 'w', newline='') as fc:
        w = csv.writer(fc)
        for i in range(M):
            w.writerow([float(C[i,j]) for j in range(N)])

    # Save metadata about this test case
    metadata = {
        'case_id': args.case_id,
        'category': case['category'],
        'requested_cond_A': case['cond_A'],
        'requested_cond_B': case['cond_B'],
        'actual_cond_A': float(actual_cond_A),
        'actual_cond_B': float(actual_cond_B),
        'seed': case['seed'],
        'M': M,
        'K': K,
        'N': N,
        'precision': args.prec,
        'A_min': float(np.min(A)),
        'A_max': float(np.max(A)),
        'A_mean': float(np.mean(A)),
        'A_std': float(np.std(A)),
        'B_min': float(np.min(B)),
        'B_max': float(np.max(B)),
        'B_mean': float(np.mean(B)),
        'B_std': float(np.std(B)),
        'C_ref_min': float(np.min(C)),
        'C_ref_max': float(np.max(C)),
        'C_ref_mean': float(np.mean(C)),
        'C_ref_std': float(np.std(C)),
        'C_ref_norm': float(np.linalg.norm(C, 'fro'))
    }

    with open(output_dir / 'test_metadata.json', 'w') as fm:
        json.dump(metadata, fm, indent=2)

    print(f"Generated test case {args.case_id} ({case['category']} condition)")
    print(f"  Requested cond(A)={case['cond_A']:.1f}, cond(B)={case['cond_B']:.1f}")
    print(f"  Actual cond(A)={actual_cond_A:.2f}, cond(B)={actual_cond_B:.2f}")
    print(f"  Wrote {output_dir}/A.mem, B.mem, C_ref.csv, test_metadata.json")

if __name__ == '__main__':
    main()
