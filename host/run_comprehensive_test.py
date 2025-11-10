"""
Comprehensive test runner for mixed-precision matrix multiplication.
Runs 42 test cases across 3 precisions (126 total simulations).
Collects extensive metrics for analysis.
"""

import os
import csv
import subprocess
import pathlib
import time
import json
import numpy as np
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOST = ROOT / "host"
MEM = ROOT / "mem"
RES = ROOT / "results"
RES.mkdir(exist_ok=True)

# Vivado wrapper script (sets up environment)
VIVADO_PATH = str(ROOT / "scripts" / "run_vivado.bat")

def run(cmd, env=None, capture=False, cwd=None):
    """Run a command and optionally capture output."""
    if cwd is None:
        cwd = ROOT
    print("$", " ".join(str(c) for c in cmd))
    if capture:
        r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True)
    else:
        r = subprocess.run(cmd, env=env, cwd=cwd)

    if r.returncode != 0:
        print(f"WARNING: Command failed with return code {r.returncode}")
        if capture and r.stderr:
            print(f"STDERR: {r.stderr}")
        return None
    return r

def read_csv(path):
    """Read a CSV file into a numpy array."""
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip():
                rows.append([float(x) for x in line.strip().split(',')])
    return np.array(rows, dtype=float)

def compute_comprehensive_metrics(C_ref, C_out, prec='fp32', sim_time=0, M=8, K=8, N=8):
    """
    Compute comprehensive accuracy, numerical quality, and hardware metrics.
    """
    # Basic error metrics
    diff = C_out - C_ref
    mae = float(np.mean(np.abs(diff)))
    rmse = float(np.sqrt(np.mean(diff**2)))
    max_abs = float(np.max(np.abs(diff)))

    # Relative error metrics
    denom = np.maximum(np.abs(C_ref), 1e-10)
    rel_mae = float(np.mean(np.abs(diff) / denom))
    rel_rmse = float(np.sqrt(np.mean((diff / denom)**2)))
    max_rel = float(np.max(np.abs(diff) / denom))

    # Frobenius norm metrics
    norm_C_ref = np.linalg.norm(C_ref, 'fro')
    norm_diff = np.linalg.norm(diff, 'fro')
    norm_rel_error = norm_diff / (norm_C_ref + 1e-10)

    # Matrix-level statistics
    C_ref_mean = float(np.mean(C_ref))
    C_out_mean = float(np.mean(C_out))
    C_ref_std = float(np.std(C_ref))
    C_out_std = float(np.std(C_out))

    # Percentile errors
    abs_errors = np.abs(diff).flatten()
    p50_error = float(np.percentile(abs_errors, 50))
    p90_error = float(np.percentile(abs_errors, 90))
    p95_error = float(np.percentile(abs_errors, 95))
    p99_error = float(np.percentile(abs_errors, 99))

    # Signal-to-noise ratio (in dB)
    signal_power = np.mean(C_ref**2)
    noise_power = np.mean(diff**2)
    snr_db = 10 * np.log10(signal_power / (noise_power + 1e-10))

    # Correlation coefficient
    try:
        corr = float(np.corrcoef(C_ref.flatten(), C_out.flatten())[0, 1])
    except:
        corr = 0.0

    # Element-wise accuracy (percentage of elements within certain thresholds)
    total_elements = C_ref.size
    acc_1pct = float(np.sum(np.abs(diff / (np.abs(C_ref) + 1e-10)) < 0.01) / total_elements * 100)
    acc_5pct = float(np.sum(np.abs(diff / (np.abs(C_ref) + 1e-10)) < 0.05) / total_elements * 100)
    acc_10pct = float(np.sum(np.abs(diff / (np.abs(C_ref) + 1e-10)) < 0.10) / total_elements * 100)

    # ========================================================================
    # HARDWARE METRICS
    # ========================================================================

    # Performance metrics
    total_ops = M * K * N * 2  # MACs = multiply-add operations
    ops_per_second = total_ops / (sim_time + 1e-10)
    gops = ops_per_second / 1e9

    # Precision quality
    effective_bits = -np.log2(norm_rel_error + 1e-10)
    if effective_bits > 32:
        effective_bits = 32.0

    # Error pattern analysis
    error_tail_concentration = p99_error / (p50_error + 1e-10)
    error_outlier_ratio = rmse / (mae + 1e-10)
    bias_fraction = abs(C_out_mean - C_ref_mean) / (mae + 1e-10)

    # Range utilization (for INT8)
    if prec == 'int8':
        output_range_3sigma = max(abs(C_out_mean - 3*C_out_std),
                                  abs(C_out_mean + 3*C_out_std))
        int8_range_util = min(100.0, 100.0 * output_range_3sigma / 127.0)
    else:
        int8_range_util = np.nan

    # Bit-level error analysis
    # Count sign bit errors (catastrophic!)
    sign_errors = np.sum(np.sign(C_ref) != np.sign(C_out))
    sign_error_pct = 100.0 * sign_errors / total_elements

    # Per-row and per-column max errors
    row_errors_max = np.max(np.abs(diff), axis=1)
    col_errors_max = np.max(np.abs(diff), axis=0)
    max_row_error = float(np.max(row_errors_max))
    max_col_error = float(np.max(col_errors_max))
    error_spatial_variance = float(np.std(row_errors_max))

    # Error distribution shape
    error_skewness = float(np.mean(((diff - diff.mean()) / (diff.std() + 1e-10))**3))
    error_kurtosis = float(np.mean(((diff - diff.mean()) / (diff.std() + 1e-10))**4))

    # Zero/near-zero detection (potential underflow)
    zero_threshold = 1e-10
    unexpected_zeros = np.sum((np.abs(C_out) < zero_threshold) & (np.abs(C_ref) > zero_threshold))
    zero_error_pct = 100.0 * unexpected_zeros / total_elements

    # Infinity/NaN detection
    inf_nan_count = np.sum(~np.isfinite(C_out))

    # ULP (Units in Last Place) error for floating point
    if prec in ['fp16', 'fp32']:
        # Approximate ULP error
        ulp_errors = np.abs(diff) / (np.abs(C_ref) + np.finfo(np.float32).eps)
        ulp_error_mean = float(np.mean(ulp_errors))
        ulp_error_max = float(np.max(ulp_errors))
    else:
        ulp_error_mean = np.nan
        ulp_error_max = np.nan

    # Additional percentiles for distribution characterization
    p75_error = float(np.percentile(abs_errors, 75))
    p25_error = float(np.percentile(abs_errors, 25))

    # Error accumulation estimate (quadrant analysis)
    # Divide matrix into quadrants and check error variance
    mid_m, mid_n = M//2, N//2
    q1_error = float(np.mean(np.abs(diff[:mid_m, :mid_n])))
    q2_error = float(np.mean(np.abs(diff[:mid_m, mid_n:])))
    q3_error = float(np.mean(np.abs(diff[mid_m:, :mid_n])))
    q4_error = float(np.mean(np.abs(diff[mid_m:, mid_n:])))
    quadrant_error_variance = float(np.var([q1_error, q2_error, q3_error, q4_error]))

    return {
        # Original metrics
        'mae': mae,
        'rmse': rmse,
        'max_abs_error': max_abs,
        'rel_mae': rel_mae,
        'rel_rmse': rel_rmse,
        'max_rel_error': max_rel,
        'norm_rel_error': norm_rel_error,
        'C_ref_mean': C_ref_mean,
        'C_out_mean': C_out_mean,
        'C_ref_std': C_ref_std,
        'C_out_std': C_out_std,
        'mean_bias': C_out_mean - C_ref_mean,
        'p50_error': p50_error,
        'p90_error': p90_error,
        'p95_error': p95_error,
        'p99_error': p99_error,
        'snr_db': snr_db,
        'correlation': corr,
        'acc_1pct': acc_1pct,
        'acc_5pct': acc_5pct,
        'acc_10pct': acc_10pct,
        'norm_C_ref': norm_C_ref,
        'norm_diff': norm_diff,
        # Hardware performance
        'total_operations': total_ops,
        'ops_per_second': ops_per_second,
        'gops': gops,
        # Precision quality
        'effective_bits': effective_bits,
        # Error patterns
        'error_tail_concentration': error_tail_concentration,
        'error_outlier_ratio': error_outlier_ratio,
        'bias_fraction': bias_fraction,
        # Range utilization
        'int8_range_utilization_pct': int8_range_util,
        # Bit-level errors
        'sign_error_count': sign_errors,
        'sign_error_pct': sign_error_pct,
        # Spatial error patterns
        'max_row_error': max_row_error,
        'max_col_error': max_col_error,
        'error_spatial_variance': error_spatial_variance,
        # Error distribution
        'error_skewness': error_skewness,
        'error_kurtosis': error_kurtosis,
        'p25_error': p25_error,
        'p75_error': p75_error,
        # Underflow/overflow detection
        'unexpected_zeros_count': unexpected_zeros,
        'zero_error_pct': zero_error_pct,
        'inf_nan_count': inf_nan_count,
        # Floating-point specific
        'ulp_error_mean': ulp_error_mean,
        'ulp_error_max': ulp_error_max,
        # Error accumulation
        'quadrant_error_variance': quadrant_error_variance,
        'q1_error': q1_error,
        'q2_error': q2_error,
        'q3_error': q3_error,
        'q4_error': q4_error,
    }

PRECODES = {"int8": 0, "fp16": 1, "fp32": 2}

def main():
    # Configuration
    M, K, N = 8, 8, 8  # Matrix dimensions
    precs = ["int8", "fp16", "fp32"]
    num_cases = 42

    # Prepare results file
    results_file = RES / "comprehensive_results.csv"
    all_results = []

    # CSV header
    header = [
        'timestamp', 'case_id', 'category', 'precision',
        'M', 'K', 'N',
        'requested_cond_A', 'requested_cond_B',
        'actual_cond_A', 'actual_cond_B',
        'A_min', 'A_max', 'A_mean', 'A_std',
        'B_min', 'B_max', 'B_mean', 'B_std',
        'C_ref_min', 'C_ref_max', 'C_ref_mean', 'C_ref_std',
        'mae', 'rmse', 'max_abs_error',
        'rel_mae', 'rel_rmse', 'max_rel_error',
        'norm_rel_error',
        'C_out_mean', 'C_out_std', 'mean_bias',
        'p50_error', 'p90_error', 'p95_error', 'p99_error',
        'snr_db', 'correlation',
        'acc_1pct', 'acc_5pct', 'acc_10pct',
        'norm_C_ref', 'norm_diff',
        # Hardware performance
        'total_operations', 'ops_per_second', 'gops',
        # Precision quality
        'effective_bits',
        # Error patterns
        'error_tail_concentration', 'error_outlier_ratio', 'bias_fraction',
        # Range utilization
        'int8_range_utilization_pct',
        # Bit-level errors
        'sign_error_count', 'sign_error_pct',
        # Spatial error patterns
        'max_row_error', 'max_col_error', 'error_spatial_variance',
        # Error distribution
        'error_skewness', 'error_kurtosis', 'p25_error', 'p75_error',
        # Underflow/overflow detection
        'unexpected_zeros_count', 'zero_error_pct', 'inf_nan_count',
        # Floating-point specific
        'ulp_error_mean', 'ulp_error_max',
        # Error accumulation
        'quadrant_error_variance', 'q1_error', 'q2_error', 'q3_error', 'q4_error',
        'sim_time_sec', 'status'
    ]

    # Check for quick test mode
    max_cases = num_cases
    if os.environ.get('QUICK_TEST') == 'true':
        max_cases = int(os.environ.get('MAX_CASES', '3'))
        print(f"QUICK TEST MODE: Running only {max_cases} cases (instead of {num_cases})")
        print()

    with open(results_file, 'w', newline='') as fc:
        w = csv.writer(fc)
        w.writerow(header)

        total_runs = max_cases * len(precs)
        run_count = 0

        for case_id in range(max_cases):
            for prec in precs:
                run_count += 1
                print(f"\n{'='*80}")
                print(f"Running test {run_count}/{total_runs}: Case {case_id}, Precision {prec}")
                print(f"{'='*80}")

                start_time = time.time()
                status = "success"

                try:
                    # Step 1: Generate test matrices with controlled condition numbers
                    print(f"\n[1/4] Generating matrices...")
                    result = run([
                        "python", "gen_cond_mems.py",
                        "--M", str(M), "--K", str(K), "--N", str(N),
                        "--prec", prec,
                        "--case-id", str(case_id)
                    ], cwd=HOST)

                    if result is None:
                        status = "gen_failed"
                        raise Exception("Matrix generation failed")

                    # Load metadata
                    with open(MEM / "test_metadata.json", 'r') as f:
                        metadata = json.load(f)

                    # Step 2: Run simulation
                    print(f"\n[2/4] Running xsim simulation...")
                    env = os.environ.copy()
                    env["PREC_SEL"] = str(PRECODES[prec])
                    env["M"], env["K"], env["N"] = str(M), str(K), str(N)

                    # Run xsim directly (simplified version without TCL batch)
                    result = run([
                        str(ROOT / "scripts" / "run_xsim_simple.bat")
                    ], env=env)

                    if result is None:
                        status = "sim_failed"
                        raise Exception("Simulation failed")

                    # Step 3: Parse output
                    print(f"\n[3/4] Parsing output...")
                    result = run([
                        "python", "parse_out_to_csv.py",
                        "--M", str(M), "--N", str(N),
                        "--prec", prec
                    ], cwd=HOST)

                    if result is None:
                        status = "parse_failed"
                        raise Exception("Output parsing failed")

                    # Step 4: Compute metrics
                    print(f"\n[4/4] Computing metrics...")
                    C_ref = read_csv(MEM / "C_ref.csv")
                    C_out = read_csv(MEM / "C_out.csv")

                    sim_time = time.time() - start_time
                    metrics = compute_comprehensive_metrics(C_ref, C_out, prec=prec, sim_time=sim_time, M=M, K=K, N=N)

                    # Prepare row
                    row = [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        case_id,
                        metadata['category'],
                        prec,
                        M, K, N,
                        metadata['requested_cond_A'],
                        metadata['requested_cond_B'],
                        metadata['actual_cond_A'],
                        metadata['actual_cond_B'],
                        metadata['A_min'], metadata['A_max'],
                        metadata['A_mean'], metadata['A_std'],
                        metadata['B_min'], metadata['B_max'],
                        metadata['B_mean'], metadata['B_std'],
                        metadata['C_ref_min'], metadata['C_ref_max'],
                        metadata['C_ref_mean'], metadata['C_ref_std'],
                        metrics['mae'], metrics['rmse'], metrics['max_abs_error'],
                        metrics['rel_mae'], metrics['rel_rmse'], metrics['max_rel_error'],
                        metrics['norm_rel_error'],
                        metrics['C_out_mean'], metrics['C_out_std'], metrics['mean_bias'],
                        metrics['p50_error'], metrics['p90_error'],
                        metrics['p95_error'], metrics['p99_error'],
                        metrics['snr_db'], metrics['correlation'],
                        metrics['acc_1pct'], metrics['acc_5pct'], metrics['acc_10pct'],
                        metrics['norm_C_ref'], metrics['norm_diff'],
                        # Hardware performance
                        metrics['total_operations'], metrics['ops_per_second'], metrics['gops'],
                        # Precision quality
                        metrics['effective_bits'],
                        # Error patterns
                        metrics['error_tail_concentration'], metrics['error_outlier_ratio'], metrics['bias_fraction'],
                        # Range utilization
                        metrics['int8_range_utilization_pct'],
                        # Bit-level errors
                        metrics['sign_error_count'], metrics['sign_error_pct'],
                        # Spatial error patterns
                        metrics['max_row_error'], metrics['max_col_error'], metrics['error_spatial_variance'],
                        # Error distribution
                        metrics['error_skewness'], metrics['error_kurtosis'], metrics['p25_error'], metrics['p75_error'],
                        # Underflow/overflow detection
                        metrics['unexpected_zeros_count'], metrics['zero_error_pct'], metrics['inf_nan_count'],
                        # Floating-point specific
                        metrics['ulp_error_mean'], metrics['ulp_error_max'],
                        # Error accumulation
                        metrics['quadrant_error_variance'], metrics['q1_error'], metrics['q2_error'],
                        metrics['q3_error'], metrics['q4_error'],
                        sim_time,
                        status
                    ]

                    print(f"\n[RESULTS]")
                    print(f"  MAE: {metrics['mae']:.6f}")
                    print(f"  RMSE: {metrics['rmse']:.6f}")
                    print(f"  Max Error: {metrics['max_abs_error']:.6f}")
                    print(f"  Rel RMSE: {metrics['rel_rmse']:.6f}")
                    print(f"  SNR: {metrics['snr_db']:.2f} dB")
                    print(f"  Correlation: {metrics['correlation']:.6f}")
                    print(f"  GOPS: {metrics['gops']:.6f}")
                    print(f"  Effective Bits: {metrics['effective_bits']:.2f}")
                    print(f"  Sim Time: {sim_time:.2f}s")

                except Exception as e:
                    print(f"\n[ERROR] {str(e)}")
                    sim_time = time.time() - start_time

                    # Write error row with NaN for metrics
                    row = [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        case_id,
                        'unknown',
                        prec,
                        M, K, N,
                    ] + [np.nan] * (len(header) - 8) + [sim_time, status]

                # Write row to CSV
                w.writerow(row)
                fc.flush()

        print(f"\n{'='*80}")
        print(f"All tests complete! Results saved to {results_file}")
        print(f"{'='*80}")

if __name__ == '__main__':
    main()
