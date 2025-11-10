"""
Add hardware-specific metrics to existing test results
Computes performance and efficiency metrics from existing data
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_FILE = ROOT / "results" / "comprehensive_results.csv"
OUTPUT_FILE = ROOT / "results" / "comprehensive_results_with_hw_metrics.csv"

print("=" * 80)
print("ADDING HARDWARE METRICS TO TEST RESULTS")
print("=" * 80)

# Load existing results
df = pd.read_csv(RESULTS_FILE)
print(f"\nLoaded {len(df)} test results")

# Filter only successful tests
df_success = df[df['status'] == 'success'].copy()
print(f"Processing {len(df_success)} successful tests")

# ============================================================================
# 1. PERFORMANCE METRICS
# ============================================================================

# Operations count: M×K×N multiply-adds = M×K×N×2 operations
df_success['total_operations'] = df_success['M'] * df_success['K'] * df_success['N'] * 2

# Operations per second
df_success['ops_per_second'] = df_success['total_operations'] / df_success['sim_time_sec']

# GOPS (Giga-operations per second)
df_success['gops'] = df_success['ops_per_second'] / 1e9

# Operations per second per output element
df_success['ops_per_elem_per_sec'] = df_success['ops_per_second'] / (df_success['M'] * df_success['N'])

print("\n[OK] Computed performance metrics")

# ============================================================================
# 2. PRECISION QUALITY METRICS
# ============================================================================

# Effective Number of Bits (ENOB)
# ENOB = -log2(norm_rel_error), capped at precision bits
df_success['effective_bits'] = -np.log2(df_success['norm_rel_error'].replace(0, 1e-10))
df_success.loc[df_success['effective_bits'] > 32, 'effective_bits'] = 32  # Cap at FP32

# Signal-to-Quantization-Noise Ratio (SNQR) in dB
# Similar to SNR but specifically for quantization noise
df_success['snqr_db'] = df_success['snr_db']  # Alias for now

print("[OK] Computed precision quality metrics")

# ============================================================================
# 3. CROSS-PRECISION COMPARISON
# ============================================================================

# For each case_id, compute speedup and accuracy ratios
def compute_cross_precision_metrics(group):
    """Compute metrics comparing precisions within same case_id"""

    # Reference precision: FP32
    fp32 = group[group['precision'] == 'fp32']
    fp16 = group[group['precision'] == 'fp16']
    int8 = group[group['precision'] == 'int8']

    # Initialize new columns
    for col in ['int8_speedup_vs_fp32', 'int8_accuracy_vs_fp32',
                'fp16_speedup_vs_fp32', 'fp16_accuracy_vs_fp32']:
        group[col] = np.nan

    if len(fp32) > 0:
        fp32_time = fp32.iloc[0]['sim_time_sec']
        fp32_error = fp32.iloc[0]['norm_rel_error']

        # INT8 vs FP32
        if len(int8) > 0:
            int8_idx = int8.index[0]
            group.loc[int8_idx, 'int8_speedup_vs_fp32'] = fp32_time / int8.iloc[0]['sim_time_sec']
            group.loc[int8_idx, 'int8_accuracy_vs_fp32'] = int8.iloc[0]['norm_rel_error'] / fp32_error if fp32_error > 0 else np.nan

        # FP16 vs FP32
        if len(fp16) > 0:
            fp16_idx = fp16.index[0]
            group.loc[fp16_idx, 'fp16_speedup_vs_fp32'] = fp32_time / fp16.iloc[0]['sim_time_sec']
            group.loc[fp16_idx, 'fp16_accuracy_vs_fp32'] = fp16.iloc[0]['norm_rel_error'] / fp32_error if fp32_error > 0 else np.nan

    return group

df_success = df_success.groupby('case_id').apply(compute_cross_precision_metrics).reset_index(drop=True)

print("[OK] Computed cross-precision comparisons")

# ============================================================================
# 4. EFFICIENCY METRICS
# ============================================================================

# Pareto score: Balance of speed and accuracy
# Higher is better (fast AND accurate)
df_success['pareto_score'] = (1.0 / df_success['norm_rel_error'].replace(0, 1e-10)) * df_success['gops']

# Normalize pareto score to 0-100 range for easier interpretation
pareto_max = df_success['pareto_score'].max()
df_success['pareto_score_normalized'] = 100 * df_success['pareto_score'] / pareto_max

print("[OK] Computed efficiency metrics")

# ============================================================================
# 5. RANGE UTILIZATION (INT8 only)
# ============================================================================

# For INT8, compute what percentage of -128 to 127 range is used
def compute_int8_range_utilization(row):
    if row['precision'] != 'int8':
        return np.nan

    # Output range
    output_range = max(abs(row['C_out_mean'] - 3*row['C_out_std']),
                      abs(row['C_out_mean'] + 3*row['C_out_std']))

    # INT8 range is -128 to 127
    int8_max = 127
    utilization = min(100.0, 100.0 * output_range / int8_max)

    return utilization

df_success['int8_range_utilization_pct'] = df_success.apply(compute_int8_range_utilization, axis=1)

print("[OK] Computed INT8 range utilization")

# ============================================================================
# 6. ERROR PATTERN ANALYSIS
# ============================================================================

# Error concentration: How much error is in the tail?
# If p99/median is large, errors are concentrated in outliers
df_success['error_tail_concentration'] = df_success['p99_error'] / df_success['p50_error'].replace(0, 1e-10)

# Outlier ratio: RMSE/MAE (>1.4 means significant outliers)
df_success['error_outlier_ratio'] = df_success['rmse'] / df_success['mae'].replace(0, 1e-10)

# Bias significance: How much of MAE is systematic bias?
df_success['bias_fraction'] = abs(df_success['mean_bias']) / df_success['mae'].replace(0, 1e-10)

print("[OK] Computed error pattern metrics")

# ============================================================================
# 7. CONDITION NUMBER SENSITIVITY
# ============================================================================

# Error amplification: How much does conditioning affect error?
# Compare error to best-case (lowest condition number) for same precision
def compute_cond_sensitivity(group):
    """Compute how error grows with condition number for each precision"""

    group['error_amplification'] = np.nan

    if len(group) < 2:
        return group

    # Find lowest condition number case
    min_cond_idx = group['actual_cond_A'].idxmin()
    baseline_error = group.loc[min_cond_idx, 'norm_rel_error']

    if baseline_error > 0:
        group['error_amplification'] = group['norm_rel_error'] / baseline_error

    return group

df_success = df_success.groupby('precision').apply(compute_cond_sensitivity).reset_index(drop=True)

print("[OK] Computed condition number sensitivity")

# ============================================================================
# SAVE RESULTS
# ============================================================================

# Merge back with original dataframe (including failed tests)
df_all = df.copy()

# Add new columns to failed tests as NaN
new_cols = [col for col in df_success.columns if col not in df.columns]
for col in new_cols:
    df_all[col] = np.nan

# Update successful test rows
df_all.update(df_success)

# Save enhanced results
df_all.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 80)
print(f"Enhanced results saved to:")
print(f"  {OUTPUT_FILE}")
print("=" * 80)

# Print summary statistics
print("\n--- PERFORMANCE SUMMARY ---")
print(f"Average GOPS by precision:")
for prec in ['int8', 'fp16', 'fp32']:
    gops_mean = df_success[df_success['precision'] == prec]['gops'].mean()
    print(f"  {prec:5s}: {gops_mean:.4f} GOPS")

print("\n--- QUALITY SUMMARY ---")
print(f"Average Effective Bits by precision:")
for prec in ['int8', 'fp16', 'fp32']:
    enob_mean = df_success[df_success['precision'] == prec]['effective_bits'].mean()
    print(f"  {prec:5s}: {enob_mean:.2f} bits")

print("\n--- SPEEDUP SUMMARY ---")
int8_speedup = df_success['int8_speedup_vs_fp32'].mean()
fp16_speedup = df_success['fp16_speedup_vs_fp32'].mean()
print(f"  INT8 vs FP32: {int8_speedup:.2f}× faster (avg)")
print(f"  FP16 vs FP32: {fp16_speedup:.2f}× faster (avg)")

print("\n--- NEW COLUMNS ADDED ---")
for col in sorted(new_cols):
    print(f"  - {col}")

print("\n" + "=" * 80)
