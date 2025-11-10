"""
Comprehensive visualization of mixed-precision matrix multiplication results
Generates 10+ insightful plots from comprehensive_results.csv
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Setup paths
ROOT = Path(__file__).parent.parent
RESULTS_FILE = ROOT / "results" / "comprehensive_results.csv"
PLOTS_DIR = ROOT / "results" / "plots"

# Create plots directory
PLOTS_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("MIXED PRECISION MATMUL - VISUALIZATION SUITE")
print("=" * 80)

# Load data
print(f"\nLoading data from: {RESULTS_FILE}")
df = pd.read_csv(RESULTS_FILE)
df_success = df[df['status'] == 'success'].copy()

print(f"Total tests: {len(df)}")
print(f"Successful: {len(df_success)}")
print(f"\nTests by precision:")
print(df_success['precision'].value_counts())

if len(df_success) == 0:
    print("\n[ERROR] No successful tests found! Cannot generate plots.")
    exit(1)

print(f"\nGenerating plots in: {PLOTS_DIR}")
print("=" * 80)

# ============================================================================
# PLOT 1: PERFORMANCE vs ACCURACY PARETO
# ============================================================================
print("\n[1/10] Generating Pareto Plot (Speed vs Accuracy)...")

plt.figure(figsize=(10, 6))
colors = {'int8': 'red', 'fp16': 'green', 'fp32': 'blue'}
markers = {'int8': 'o', 'fp16': 's', 'fp32': '^'}

for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        plt.scatter(data['gops'], data['norm_rel_error'],
                    label=prec.upper(), s=100, alpha=0.6,
                    color=colors[prec], marker=markers[prec])

plt.xlabel('Performance (GOPS)', fontsize=12)
plt.ylabel('Normalized Relative Error', fontsize=12)
plt.yscale('log')
plt.legend(fontsize=12)
plt.title('Speed vs Accuracy Tradeoff\n(Lower-Right is Better: Fast AND Accurate)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / '01_pareto_plot.png', dpi=300)
plt.close()
print("    Saved: 01_pareto_plot.png")

# ============================================================================
# PLOT 2: EFFECTIVE BITS BY PRECISION
# ============================================================================
print("[2/10] Generating Effective Bits Analysis...")

fig, ax = plt.subplots(figsize=(10, 6))
df_success.boxplot(column='effective_bits', by='precision', ax=ax, grid=False)
plt.suptitle('')
plt.title('Effective Number of Bits (ENOB) by Precision\nHigher is Better', fontsize=14, fontweight='bold')
plt.xlabel('Precision', fontsize=12)
plt.ylabel('Effective Bits', fontsize=12)

# Add reference lines
plt.axhline(y=8, color='red', linestyle='--', alpha=0.5, linewidth=2, label='INT8 theoretical (8 bits)')
plt.axhline(y=11, color='green', linestyle='--', alpha=0.5, linewidth=2, label='FP16 mantissa (11 bits)')
plt.axhline(y=24, color='blue', linestyle='--', alpha=0.5, linewidth=2, label='FP32 mantissa (24 bits)')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(PLOTS_DIR / '02_effective_bits.png', dpi=300)
plt.close()
print("    Saved: 02_effective_bits.png")

# ============================================================================
# PLOT 3: ERROR GROWTH WITH CONDITION NUMBER
# ============================================================================
print("[3/10] Generating Condition Number Sensitivity...")

plt.figure(figsize=(12, 6))

for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        plt.scatter(data['actual_cond_A'], data['norm_rel_error'],
                    label=prec.upper(), alpha=0.6, s=60,
                    color=colors[prec], marker=markers[prec])

plt.xlabel('Condition Number of Matrix A', fontsize=12)
plt.ylabel('Normalized Relative Error', fontsize=12)
plt.xscale('log')
plt.yscale('log')
plt.legend(fontsize=12)
plt.title('Error Sensitivity to Ill-Conditioning\n(Flat line = robust to conditioning)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / '03_condition_sensitivity.png', dpi=300)
plt.close()
print("    Saved: 03_condition_sensitivity.png")

# ============================================================================
# PLOT 4: INT8 RANGE UTILIZATION HISTOGRAM
# ============================================================================
print("[4/10] Generating INT8 Range Utilization...")

int8_data = df_success[df_success['precision'] == 'int8']
if len(int8_data) > 0:
    plt.figure(figsize=(10, 6))
    range_util = int8_data['int8_range_utilization_pct'].dropna()

    if len(range_util) > 0:
        plt.hist(range_util, bins=20, edgecolor='black', alpha=0.7, color='coral')
        plt.axvline(x=50, color='orange', linestyle='--', linewidth=2,
                    label='Underutilized (<50%)')
        plt.axvline(x=90, color='red', linestyle='--', linewidth=2,
                    label='Risk of overflow (>90%)')

        mean_util = range_util.mean()
        plt.axvline(x=mean_util, color='blue', linestyle='-', linewidth=2,
                   label=f'Mean = {mean_util:.1f}%')

        plt.xlabel('INT8 Range Utilization (%)', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.title('INT8 Dynamic Range Usage\nTarget: 50-90% (Good utilization without overflow risk)',
                 fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / '04_int8_range_util.png', dpi=300)
        plt.close()
        print("    Saved: 04_int8_range_util.png")
    else:
        print("    Skipped: No INT8 range utilization data")
else:
    print("    Skipped: No INT8 data available")

# ============================================================================
# PLOT 5: ERROR DISTRIBUTION SHAPE ANALYSIS
# ============================================================================
print("[5/10] Generating Error Distribution Shape Analysis...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[idx].scatter(data['error_skewness'], data['error_kurtosis'],
                         alpha=0.6, s=80, color=colors[prec])
        axes[idx].axhline(y=3, color='red', linestyle='--', alpha=0.5, linewidth=2,
                         label='Gaussian (kurtosis=3)')
        axes[idx].axvline(x=0, color='green', linestyle='--', alpha=0.5, linewidth=2,
                         label='Symmetric (skew=0)')
        axes[idx].set_xlabel('Skewness', fontsize=10)
        axes[idx].set_ylabel('Kurtosis', fontsize=10)
        axes[idx].set_title(f'{prec.upper()} Error Distribution', fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3)
        axes[idx].legend(fontsize=8)

fig.suptitle('Error Distribution Shape: Skewness vs Kurtosis\n(Near origin = well-behaved Gaussian errors)',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / '05_error_distribution_shape.png', dpi=300)
plt.close()
print("    Saved: 05_error_distribution_shape.png")

# ============================================================================
# PLOT 6: SIGN ERROR DETECTION
# ============================================================================
print("[6/10] Generating Sign Error Analysis...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Sign error percentage by precision
sign_errors = df_success.groupby('precision')['sign_error_pct'].agg(['mean', 'max'])
x = np.arange(len(sign_errors))
width = 0.35

ax1.bar(x - width/2, sign_errors['mean'], width, label='Mean', color='skyblue', alpha=0.8)
ax1.bar(x + width/2, sign_errors['max'], width, label='Max', color='red', alpha=0.8)
ax1.set_ylabel('Sign Error (%)', fontsize=12)
ax1.set_title('Sign Bit Errors (CATASTROPHIC!)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Precision', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(sign_errors.index.str.upper())
ax1.axhline(y=1.0, color='red', linestyle='--', linewidth=2,
            label='Danger threshold (1%)')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# Plot 2: Cases with sign errors
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax2.scatter(data['norm_rel_error'], data['sign_error_pct'],
                   label=prec.upper(), alpha=0.6, s=60,
                   color=colors[prec], marker=markers[prec])

ax2.set_xlabel('Normalized Relative Error', fontsize=12)
ax2.set_ylabel('Sign Error (%)', fontsize=12)
ax2.set_xscale('log')
ax2.set_title('Sign Errors vs Overall Error', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(PLOTS_DIR / '06_sign_errors.png', dpi=300)
plt.close()
print("    Saved: 06_sign_errors.png")

# ============================================================================
# PLOT 7: PERFORMANCE SCALING BY MATRIX SIZE
# ============================================================================
print("[7/10] Generating Performance Scaling Analysis...")

df_success['matrix_ops'] = df_success['M'] * df_success['K'] * df_success['N']

plt.figure(figsize=(12, 6))

for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        plt.scatter(data['matrix_ops'], data['gops'],
                   label=prec.upper(), alpha=0.6, s=60,
                   color=colors[prec], marker=markers[prec])

plt.xlabel('Matrix Operations (M×K×N)', fontsize=12)
plt.ylabel('GOPS (Giga-Operations Per Second)', fontsize=12)
plt.xscale('log')
plt.legend(fontsize=12)
plt.title('Performance Scaling with Problem Size\n(Should scale linearly for efficient implementation)',
         fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / '07_performance_scaling.png', dpi=300)
plt.close()
print("    Saved: 07_performance_scaling.png")

# ============================================================================
# PLOT 8: SPATIAL ERROR HEATMAP
# ============================================================================
print("[8/10] Generating Spatial Error Heatmap...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec]

    if len(data) > 0:
        # Quadrant error analysis
        quadrant_means = data[['q1_error', 'q2_error', 'q3_error', 'q4_error']].mean()
        heatmap_data = [[quadrant_means['q1_error'], quadrant_means['q2_error']],
                        [quadrant_means['q3_error'], quadrant_means['q4_error']]]

        im = axes[idx].imshow(heatmap_data, cmap='hot', interpolation='nearest')
        axes[idx].set_title(f'{prec.upper()} Quadrant Errors', fontsize=12, fontweight='bold')
        axes[idx].set_xticks([0, 1])
        axes[idx].set_yticks([0, 1])
        axes[idx].set_xticklabels(['Left', 'Right'])
        axes[idx].set_yticklabels(['Top', 'Bottom'])

        # Add text annotations
        for i in range(2):
            for j in range(2):
                text = axes[idx].text(j, i, f'{heatmap_data[i][j]:.2e}',
                                    ha="center", va="center", color="white", fontsize=10)

        plt.colorbar(im, ax=axes[idx])

fig.suptitle('Spatial Error Distribution (Matrix Quadrants)\n(Uniform colors = spatially uniform errors)',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / '08_spatial_error_heatmap.png', dpi=300)
plt.close()
print("    Saved: 08_spatial_error_heatmap.png")

# ============================================================================
# PLOT 9: ULP ERROR FOR FLOATING POINT
# ============================================================================
print("[9/10] Generating ULP Error Analysis (FP16/FP32)...")

fp_data = df_success[df_success['precision'].isin(['fp16', 'fp32'])]

if len(fp_data) > 0:
    fig, ax = plt.subplots(figsize=(10, 6))
    fp_data.boxplot(column='ulp_error_mean', by='precision', ax=ax, grid=False)
    plt.suptitle('')
    plt.title('ULP Error (Units in Last Place)\nMeasure of FP Rounding Quality',
             fontsize=14, fontweight='bold')
    plt.xlabel('Precision', fontsize=12)
    plt.ylabel('Mean ULP Error', fontsize=12)
    plt.axhline(y=0.5, color='green', linestyle='--', linewidth=2, label='Optimal rounding (0.5 ULP)')
    plt.axhline(y=1.0, color='orange', linestyle='--', linewidth=2, label='Acceptable (1 ULP)')
    plt.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Poor (>2 ULP)')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / '09_ulp_errors.png', dpi=300)
    plt.close()
    print("    Saved: 09_ulp_errors.png")
else:
    print("    Skipped: No floating-point data available")

# ============================================================================
# PLOT 10: COMPREHENSIVE DASHBOARD
# ============================================================================
print("[10/10] Generating Comprehensive Dashboard...")

fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. Pareto (top-left, large)
ax1 = fig.add_subplot(gs[0, :2])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax1.scatter(data['gops'], data['norm_rel_error'],
                   label=prec.upper(), s=80, alpha=0.6,
                   color=colors[prec], marker=markers[prec])
ax1.set_xlabel('GOPS', fontsize=10)
ax1.set_ylabel('Norm Rel Error', fontsize=10)
ax1.set_yscale('log')
ax1.legend()
ax1.set_title('Speed vs Accuracy (Pareto)', fontweight='bold', fontsize=11)
ax1.grid(True, alpha=0.3)

# 2. Effective bits
ax2 = fig.add_subplot(gs[0, 2])
df_success.boxplot(column='effective_bits', by='precision', ax=ax2, grid=False)
ax2.set_title('Effective Bits', fontweight='bold', fontsize=11)
ax2.set_xlabel('')
plt.sca(ax2)
plt.xticks(rotation=0)

# 3. Condition sensitivity
ax3 = fig.add_subplot(gs[1, :])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax3.scatter(data['actual_cond_A'], data['norm_rel_error'],
                   label=prec.upper(), alpha=0.5, s=40,
                   color=colors[prec], marker=markers[prec])
ax3.set_xscale('log')
ax3.set_yscale('log')
ax3.set_xlabel('Condition Number', fontsize=10)
ax3.set_ylabel('Norm Rel Error', fontsize=10)
ax3.legend()
ax3.set_title('Condition Number Sensitivity', fontweight='bold', fontsize=11)
ax3.grid(True, alpha=0.3)

# 4. Sign errors
ax4 = fig.add_subplot(gs[2, 0])
sign_err = df_success.groupby('precision')['sign_error_pct'].mean()
sign_err.plot(kind='bar', ax=ax4, color=['red', 'green', 'blue'], alpha=0.7)
ax4.set_ylabel('Sign Error %', fontsize=10)
ax4.set_title('Sign Errors (Catastrophic)', fontweight='bold', fontsize=11)
ax4.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_xlabel('')
plt.sca(ax4)
plt.xticks(rotation=0)

# 5. INT8 range
ax5 = fig.add_subplot(gs[2, 1])
int8_data = df_success[df_success['precision'] == 'int8']
if len(int8_data) > 0:
    range_data = int8_data['int8_range_utilization_pct'].dropna()
    if len(range_data) > 0:
        ax5.hist(range_data, bins=15, edgecolor='black', alpha=0.7, color='coral')
        ax5.set_xlabel('Range Util %', fontsize=10)
        ax5.set_title('INT8 Range Usage', fontweight='bold', fontsize=11)
        ax5.axvline(x=50, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
        ax5.axvline(x=90, color='red', linestyle='--', linewidth=1.5, alpha=0.7)

# 6. Performance summary
ax6 = fig.add_subplot(gs[2, 2])
perf_summary = df_success.groupby('precision')['gops'].mean()
perf_summary.plot(kind='bar', ax=ax6, color=['red', 'green', 'blue'], alpha=0.7)
ax6.set_ylabel('GOPS', fontsize=10)
ax6.set_title('Avg Performance', fontweight='bold', fontsize=11)
ax6.grid(True, alpha=0.3, axis='y')
ax6.set_xlabel('')
plt.sca(ax6)
plt.xticks(rotation=0)

plt.suptitle('Mixed Precision Matrix Multiplication - Performance Dashboard',
            fontsize=16, fontweight='bold', y=0.995)
plt.savefig(PLOTS_DIR / '10_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()
print("    Saved: 10_comprehensive_dashboard.png")

# ============================================================================
# BONUS PLOT 11: ERROR PATTERN ANALYSIS
# ============================================================================
print("[BONUS 11] Generating Error Pattern Analysis...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Subplot 1: Error Tail Concentration
for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[0].scatter(data.index, data['error_tail_concentration'],
                       label=prec.upper(), alpha=0.6, s=40,
                       color=colors[prec], marker=markers[prec])
axes[0].set_xlabel('Test Index', fontsize=10)
axes[0].set_ylabel('p99/p50 Ratio', fontsize=10)
axes[0].set_title('Error Tail Concentration\n(High = outliers dominate)', fontweight='bold', fontsize=11)
axes[0].axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Heavy tail (>10)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Subplot 2: Outlier Ratio (RMSE/MAE)
for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[1].scatter(data.index, data['error_outlier_ratio'],
                       label=prec.upper(), alpha=0.6, s=40,
                       color=colors[prec], marker=markers[prec])
axes[1].set_xlabel('Test Index', fontsize=10)
axes[1].set_ylabel('RMSE/MAE', fontsize=10)
axes[1].set_title('Error Outlier Ratio\n(>1.4 = significant outliers)', fontweight='bold', fontsize=11)
axes[1].axhline(y=1.4, color='red', linestyle='--', alpha=0.5, label='Outlier threshold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Subplot 3: Bias Fraction
for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[2].scatter(data.index, data['bias_fraction'],
                       label=prec.upper(), alpha=0.6, s=40,
                       color=colors[prec], marker=markers[prec])
axes[2].set_xlabel('Test Index', fontsize=10)
axes[2].set_ylabel('|Bias|/MAE', fontsize=10)
axes[2].set_title('Bias Fraction\n(High = systematic offset)', fontweight='bold', fontsize=11)
axes[2].axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Significant bias (>0.5)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

fig.suptitle('Error Pattern Analysis: Tail, Outliers, and Bias',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / '11_error_patterns.png', dpi=300)
plt.close()
print("    Saved: 11_error_patterns.png")

# ============================================================================
# BONUS PLOT 12: NUMERICAL ANOMALIES
# ============================================================================
print("[BONUS 12] Generating Numerical Anomaly Detection...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Unexpected Zeros (Underflow)
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[0, 0].scatter(data.index, data['zero_error_pct'],
                          label=prec.upper(), alpha=0.6, s=50,
                          color=colors[prec], marker=markers[prec])
axes[0, 0].set_xlabel('Test Index', fontsize=10)
axes[0, 0].set_ylabel('Unexpected Zeros (%)', fontsize=10)
axes[0, 0].set_title('Underflow Detection\n(Zeros where reference is non-zero)', fontweight='bold')
axes[0, 0].axhline(y=5, color='red', linestyle='--', alpha=0.5, label='Warning (>5%)')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Subplot 2: Inf/NaN Count
inf_nan_summary = df_success.groupby('precision')['inf_nan_count'].sum()
if inf_nan_summary.sum() > 0:
    inf_nan_summary.plot(kind='bar', ax=axes[0, 1], color=['red', 'green', 'blue'], alpha=0.7)
    axes[0, 1].set_ylabel('Total Inf/NaN Count', fontsize=10)
    axes[0, 1].set_title('Overflow/Invalid Operation Detection\n(Should be ZERO!)', fontweight='bold')
    axes[0, 1].set_xlabel('')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    plt.sca(axes[0, 1])
    plt.xticks(rotation=0)
else:
    axes[0, 1].text(0.5, 0.5, 'NO Inf/NaN DETECTED\n(GOOD!)',
                   ha='center', va='center', fontsize=16, color='green', fontweight='bold',
                   transform=axes[0, 1].transAxes)
    axes[0, 1].set_title('Overflow/Invalid Operation Detection', fontweight='bold')

# Subplot 3: Spatial Error Variance
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[1, 0].scatter(data.index, data['error_spatial_variance'],
                          label=prec.upper(), alpha=0.6, s=50,
                          color=colors[prec], marker=markers[prec])
axes[1, 0].set_xlabel('Test Index', fontsize=10)
axes[1, 0].set_ylabel('Spatial Error Variance', fontsize=10)
axes[1, 0].set_title('Error Spatial Non-Uniformity\n(High = errors cluster in regions)', fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].set_yscale('log')

# Subplot 4: Quadrant Error Variance
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        axes[1, 1].scatter(data.index, data['quadrant_error_variance'],
                          label=prec.upper(), alpha=0.6, s=50,
                          color=colors[prec], marker=markers[prec])
axes[1, 1].set_xlabel('Test Index', fontsize=10)
axes[1, 1].set_ylabel('Quadrant Error Variance', fontsize=10)
axes[1, 1].set_title('Error Accumulation Patterns\n(High = accumulation effects)', fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_yscale('log')

fig.suptitle('Numerical Anomaly Detection: Underflow, Overflow, Spatial Patterns',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / '12_numerical_anomalies.png', dpi=300)
plt.close()
print("    Saved: 12_numerical_anomalies.png")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

print("\n--- PERFORMANCE BY PRECISION ---")
perf_stats = df_success.groupby('precision')['gops'].agg(['mean', 'std', 'min', 'max'])
print(perf_stats)

print("\n--- ACCURACY BY PRECISION ---")
acc_stats = df_success.groupby('precision')['norm_rel_error'].agg(['mean', 'std', 'min', 'max'])
print(acc_stats)

print("\n--- EFFECTIVE BITS BY PRECISION ---")
bits_stats = df_success.groupby('precision')['effective_bits'].agg(['mean', 'std', 'min', 'max'])
print(bits_stats)

print("\n--- SIGN ERRORS BY PRECISION ---")
sign_stats = df_success.groupby('precision')['sign_error_pct'].agg(['mean', 'max'])
print(sign_stats)

print("\n--- INT8 RANGE UTILIZATION ---")
int8_range = df_success[df_success['precision'] == 'int8']['int8_range_utilization_pct'].dropna()
if len(int8_range) > 0:
    print(f"Mean: {int8_range.mean():.2f}%")
    print(f"Std:  {int8_range.std():.2f}%")
    print(f"Min:  {int8_range.min():.2f}%")
    print(f"Max:  {int8_range.max():.2f}%")
else:
    print("No data available")

print("\n" + "=" * 80)
print(f"ALL PLOTS SAVED TO: {PLOTS_DIR}")
print("=" * 80)
print("\nGenerated 12 visualization plots:")
print("  01_pareto_plot.png              - Speed vs Accuracy tradeoff")
print("  02_effective_bits.png           - Precision quality analysis")
print("  03_condition_sensitivity.png    - Robustness to ill-conditioning")
print("  04_int8_range_util.png          - INT8 dynamic range usage")
print("  05_error_distribution_shape.png - Statistical error characterization")
print("  06_sign_errors.png              - Catastrophic error detection")
print("  07_performance_scaling.png      - Performance vs matrix size")
print("  08_spatial_error_heatmap.png    - Spatial error patterns")
print("  09_ulp_errors.png               - Floating-point rounding quality")
print("  10_comprehensive_dashboard.png  - All-in-one overview")
print("  11_error_patterns.png           - Tail, outliers, bias analysis")
print("  12_numerical_anomalies.png      - Underflow, overflow, spatial issues")
print("\nDone!")
