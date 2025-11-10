"""
Comprehensive Condition Number Analysis
Deep dive into how matrix conditioning affects different precisions
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

# Setup paths
ROOT = Path(__file__).parent.parent
RESULTS_FILE = ROOT / "results" / "comprehensive_results.csv"
PLOTS_DIR = ROOT / "results" / "plots"

# Create plots directory
PLOTS_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("CONDITION NUMBER ANALYSIS - DEEP DIVE")
print("=" * 80)

# Load data
print(f"\nLoading data from: {RESULTS_FILE}")
df = pd.read_csv(RESULTS_FILE)
df_success = df[df['status'] == 'success'].copy()

print(f"Total tests: {len(df)}")
print(f"Successful: {len(df_success)}")

if len(df_success) == 0:
    print("\n[ERROR] No successful tests found! Cannot generate plots.")
    exit(1)

# Colors and markers
colors = {'int8': 'red', 'fp16': 'green', 'fp32': 'blue'}
markers = {'int8': 'o', 'fp16': 's', 'fp32': '^'}

print(f"\nGenerating condition number analysis plots in: {PLOTS_DIR}")
print("=" * 80)

# ============================================================================
# PLOT 1: MULTI-PANEL CONDITION NUMBER DASHBOARD
# ============================================================================
print("\n[1/7] Generating Condition Number Dashboard...")

fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)

# Panel 1: Error vs Condition Number (classic plot)
ax1 = fig.add_subplot(gs[0, :])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax1.scatter(data['actual_cond_A'], data['norm_rel_error'],
                   label=prec.upper(), alpha=0.6, s=80,
                   color=colors[prec], marker=markers[prec])

        # Fit a line in log-log space to show trend
        valid_data = data[(data['actual_cond_A'] > 0) & (data['norm_rel_error'] > 0)]
        valid_data = valid_data[np.isfinite(valid_data['actual_cond_A']) &
                                np.isfinite(valid_data['norm_rel_error'])]

        if len(valid_data) > 5:
            try:
                log_cond = np.log10(valid_data['actual_cond_A'])
                log_error = np.log10(valid_data['norm_rel_error'])

                # Check for valid log values
                valid_mask = np.isfinite(log_cond) & np.isfinite(log_error)
                log_cond = log_cond[valid_mask]
                log_error = log_error[valid_mask]

                if len(log_cond) > 5 and np.std(log_cond) > 1e-10:
                    slope, intercept = np.polyfit(log_cond, log_error, 1)

                    # Plot trend line
                    cond_range = np.logspace(np.log10(valid_data['actual_cond_A'].min()),
                                             np.log10(valid_data['actual_cond_A'].max()), 100)
                    trend_line = 10**(slope * np.log10(cond_range) + intercept)
                    ax1.plot(cond_range, trend_line, '--', color=colors[prec], alpha=0.5,
                            linewidth=2, label=f'{prec.upper()} trend (slope={slope:.2f})')
            except (np.linalg.LinAlgError, ValueError) as e:
                print(f"    Warning: Could not fit trend line for {prec}: {e}")

ax1.set_xlabel('Condition Number of Matrix A', fontsize=12)
ax1.set_ylabel('Normalized Relative Error', fontsize=12)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.legend(fontsize=9, ncol=2)
ax1.set_title('Error vs Condition Number with Trend Lines\n(Slope shows sensitivity to conditioning)',
             fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, which='both')

# Panel 2: Effective Bits vs Condition Number
ax2 = fig.add_subplot(gs[1, 0])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax2.scatter(data['actual_cond_A'], data['effective_bits'],
                   label=prec.upper(), alpha=0.6, s=60,
                   color=colors[prec], marker=markers[prec])

ax2.set_xlabel('Condition Number', fontsize=11)
ax2.set_ylabel('Effective Bits (ENOB)', fontsize=11)
ax2.set_xscale('log')
ax2.legend(fontsize=9)
ax2.set_title('Precision Loss with Ill-Conditioning', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Panel 3: Sign Errors vs Condition Number
ax3 = fig.add_subplot(gs[1, 1])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        # Only plot points with sign errors > 0
        sign_data = data[data['sign_error_pct'] > 0]
        if len(sign_data) > 0:
            ax3.scatter(sign_data['actual_cond_A'], sign_data['sign_error_pct'],
                       label=prec.upper(), alpha=0.6, s=60,
                       color=colors[prec], marker=markers[prec])

ax3.set_xlabel('Condition Number', fontsize=11)
ax3.set_ylabel('Sign Error (%)', fontsize=11)
ax3.set_xscale('log')
ax3.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Danger (1%)')
ax3.legend(fontsize=9)
ax3.set_title('Catastrophic Errors vs Conditioning', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Panel 4: Error Outlier Ratio vs Condition Number
ax4 = fig.add_subplot(gs[2, 0])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax4.scatter(data['actual_cond_A'], data['error_outlier_ratio'],
                   label=prec.upper(), alpha=0.6, s=60,
                   color=colors[prec], marker=markers[prec])

ax4.set_xlabel('Condition Number', fontsize=11)
ax4.set_ylabel('Error Outlier Ratio (RMSE/MAE)', fontsize=11)
ax4.set_xscale('log')
ax4.axhline(y=1.4, color='red', linestyle='--', alpha=0.5, label='Outlier threshold')
ax4.legend(fontsize=9)
ax4.set_title('Error Distribution Shape vs Conditioning', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)

# Panel 5: Spatial Error Variance vs Condition Number
ax5 = fig.add_subplot(gs[2, 1])
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax5.scatter(data['actual_cond_A'], data['error_spatial_variance'],
                   label=prec.upper(), alpha=0.6, s=60,
                   color=colors[prec], marker=markers[prec])

ax5.set_xlabel('Condition Number', fontsize=11)
ax5.set_ylabel('Spatial Error Variance', fontsize=11)
ax5.set_xscale('log')
ax5.set_yscale('log')
ax5.legend(fontsize=9)
ax5.set_title('Spatial Error Patterns vs Conditioning', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, which='both')

plt.suptitle('Condition Number Impact Analysis - Comprehensive Dashboard',
            fontsize=15, fontweight='bold', y=0.995)
plt.savefig(PLOTS_DIR / 'cond_01_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()
print("    Saved: cond_01_comprehensive_dashboard.png")

# ============================================================================
# PLOT 2: ERROR AMPLIFICATION (Normalized to Well-Conditioned Case)
# ============================================================================
print("[2/7] Generating Error Amplification Analysis...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec].copy()

    if len(data) > 0:
        # Find the best-conditioned case (lowest condition number)
        best_cond_idx = data['actual_cond_A'].idxmin()
        baseline_error = data.loc[best_cond_idx, 'norm_rel_error']

        # Compute error amplification
        data['error_amplification'] = data['norm_rel_error'] / baseline_error

        # Plot
        axes[idx].scatter(data['actual_cond_A'], data['error_amplification'],
                         alpha=0.6, s=80, color=colors[prec], marker=markers[prec])

        axes[idx].set_xlabel('Condition Number', fontsize=11)
        axes[idx].set_ylabel('Error Amplification Factor', fontsize=11)
        axes[idx].set_xscale('log')
        axes[idx].set_yscale('log')
        axes[idx].set_title(f'{prec.upper()} Error Amplification\n(Normalized to best-conditioned case)',
                           fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, which='both')
        axes[idx].axhline(y=1.0, color='green', linestyle='--', alpha=0.7,
                         linewidth=2, label='Baseline')

        # Fit power law: amplification ~ cond^alpha
        valid_data = data[(data['actual_cond_A'] > 0) & (data['error_amplification'] > 0)]
        valid_data = valid_data[np.isfinite(valid_data['actual_cond_A']) &
                                np.isfinite(valid_data['error_amplification'])]

        if len(valid_data) > 5:
            try:
                log_cond = np.log10(valid_data['actual_cond_A'])
                log_amp = np.log10(valid_data['error_amplification'])

                valid_mask = np.isfinite(log_cond) & np.isfinite(log_amp)
                log_cond = log_cond[valid_mask]
                log_amp = log_amp[valid_mask]

                if len(log_cond) > 5 and np.std(log_cond) > 1e-10:
                    slope, intercept = np.polyfit(log_cond, log_amp, 1)

                    cond_range = np.logspace(np.log10(valid_data['actual_cond_A'].min()),
                                             np.log10(valid_data['actual_cond_A'].max()), 100)
                    fit_line = 10**(slope * np.log10(cond_range) + intercept)
                    axes[idx].plot(cond_range, fit_line, '--', color='black', alpha=0.7,
                                  linewidth=2, label=f'Fit: amp ∝ cond^{slope:.2f}')
            except (np.linalg.LinAlgError, ValueError) as e:
                print(f"    Warning: Could not fit amplification curve for {prec}: {e}")

        axes[idx].legend(fontsize=9)

fig.suptitle('Error Amplification with Ill-Conditioning\n(How much worse than best case?)',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cond_02_error_amplification.png', dpi=300)
plt.close()
print("    Saved: cond_02_error_amplification.png")

# ============================================================================
# PLOT 3: CONDITION NUMBER BINS - HEATMAP ANALYSIS
# ============================================================================
print("[3/7] Generating Condition Number Bin Analysis...")

# Create condition number bins (filter out inf/nan first)
df_binning = df_success[np.isfinite(df_success['actual_cond_A']) & (df_success['actual_cond_A'] > 0)].copy()

if len(df_binning) > 10:
    df_binning['cond_bin'] = pd.cut(np.log10(df_binning['actual_cond_A']),
                                    bins=5,
                                    labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])

    # Metrics to analyze
    metrics = ['norm_rel_error', 'effective_bits', 'sign_error_pct', 'error_outlier_ratio']
    metric_labels = ['Norm Rel Error', 'Effective Bits', 'Sign Error %', 'Outlier Ratio']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
        # Create pivot table: condition bins vs precision
        pivot = df_binning.pivot_table(values=metric,
                                       index='cond_bin',
                                       columns='precision',
                                       aggfunc='mean')

        # Reorder columns (only include available precisions)
        available_cols = [c for c in ['int8', 'fp16', 'fp32'] if c in pivot.columns]
        pivot = pivot[available_cols]

        # Plot heatmap
        im = axes[idx].imshow(pivot.values, cmap='YlOrRd', aspect='auto', interpolation='nearest')

        axes[idx].set_xticks(np.arange(len(pivot.columns)))
        axes[idx].set_yticks(np.arange(len(pivot.index)))
        axes[idx].set_xticklabels([c.upper() for c in pivot.columns])
        axes[idx].set_yticklabels(pivot.index)
        axes[idx].set_xlabel('Precision', fontsize=10)
        axes[idx].set_ylabel('Condition Number Bin', fontsize=10)
        axes[idx].set_title(f'{label}\n(Darker = Worse)', fontsize=11, fontweight='bold')

        # Add text annotations
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                if not np.isnan(val):
                    text = axes[idx].text(j, i, f'{val:.2e}' if val < 0.01 else f'{val:.2f}',
                                        ha="center", va="center",
                                        color="white" if val > pivot.values.max()/2 else "black",
                                        fontsize=9)

        plt.colorbar(im, ax=axes[idx])

    fig.suptitle('Condition Number Impact by Precision - Binned Analysis',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'cond_03_binned_heatmap.png', dpi=300)
    plt.close()
    print("    Saved: cond_03_binned_heatmap.png")
else:
    print("    Skipped: Not enough valid data for binning")

# ============================================================================
# PLOT 4: ERROR GROWTH SLOPE COMPARISON
# ============================================================================
print("[4/7] Generating Error Growth Slope Analysis...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

slopes = {}
r_squared = {}

# Calculate slopes for each precision
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]

    if len(data) > 5:
        # Filter valid data
        valid_data = data[(data['actual_cond_A'] > 0) & (data['norm_rel_error'] > 0)]
        valid_data = valid_data[np.isfinite(valid_data['actual_cond_A']) &
                                np.isfinite(valid_data['norm_rel_error'])]

        if len(valid_data) > 5:
            try:
                log_cond = np.log10(valid_data['actual_cond_A'])
                log_error = np.log10(valid_data['norm_rel_error'])

                # Check for valid log values
                valid_mask = np.isfinite(log_cond) & np.isfinite(log_error)
                log_cond = log_cond[valid_mask]
                log_error = log_error[valid_mask]

                if len(log_cond) > 5 and np.std(log_cond) > 1e-10:
                    # Linear regression in log-log space
                    slope, intercept = np.polyfit(log_cond, log_error, 1)

                    # Calculate R-squared
                    predicted = slope * log_cond + intercept
                    ss_res = np.sum((log_error - predicted) ** 2)
                    ss_tot = np.sum((log_error - log_error.mean()) ** 2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                    slopes[prec] = slope
                    r_squared[prec] = r2

                    # Plot data and fit
                    ax1.scatter(valid_data['actual_cond_A'], valid_data['norm_rel_error'],
                               label=f'{prec.upper()} data', alpha=0.4, s=50,
                               color=colors[prec], marker=markers[prec])

                    # Plot trend line
                    cond_range = np.logspace(np.log10(valid_data['actual_cond_A'].min()),
                                             np.log10(valid_data['actual_cond_A'].max()), 100)
                    fit_line = 10**(slope * np.log10(cond_range) + intercept)
                    ax1.plot(cond_range, fit_line, '-', color=colors[prec], alpha=0.8,
                            linewidth=3, label=f'{prec.upper()} fit: slope={slope:.3f}')
            except (np.linalg.LinAlgError, ValueError) as e:
                print(f"    Warning: Could not fit slope for {prec}: {e}")

ax1.set_xlabel('Condition Number', fontsize=12)
ax1.set_ylabel('Normalized Relative Error', fontsize=12)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.legend(fontsize=9, ncol=2)
ax1.set_title('Error Growth Rate Analysis\n(Slope = d(log error)/d(log cond))',
             fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, which='both')

# Bar chart of slopes
if slopes:
    prec_list = list(slopes.keys())
    slope_values = [slopes[p] for p in prec_list]
    r2_values = [r_squared[p] for p in prec_list]

    x = np.arange(len(prec_list))
    width = 0.35

    bars1 = ax2.bar(x - width/2, slope_values, width, label='Slope',
                    color=[colors[p] for p in prec_list], alpha=0.8)

    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar(x + width/2, r2_values, width, label='R²',
                        color='gray', alpha=0.6)

    ax2.set_xlabel('Precision', fontsize=12)
    ax2.set_ylabel('Error Growth Slope', fontsize=12, color='black')
    ax2_twin.set_ylabel('R² (Fit Quality)', fontsize=12, color='gray')
    ax2.set_title('Condition Sensitivity Comparison\n(Lower slope = more robust)',
                 fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([p.upper() for p in prec_list])
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for i, (slope, r2) in enumerate(zip(slope_values, r2_values)):
        ax2.text(i - width/2, slope, f'{slope:.3f}',
                ha='center', va='bottom' if slope > 0 else 'top', fontsize=9)
        ax2_twin.text(i + width/2, r2, f'{r2:.3f}',
                     ha='center', va='bottom', fontsize=9, color='gray')

    # Legends
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')

plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cond_04_error_growth_slope.png', dpi=300)
plt.close()
print("    Saved: cond_04_error_growth_slope.png")

# ============================================================================
# PLOT 5: CONDITION NUMBER vs ALL ERROR METRICS (Multi-subplot)
# ============================================================================
print("[5/7] Generating Comprehensive Error Metrics vs Condition Number...")

error_metrics = [
    ('mae', 'Mean Absolute Error'),
    ('rmse', 'Root Mean Square Error'),
    ('max_abs_error', 'Maximum Absolute Error'),
    ('p99_error', '99th Percentile Error'),
    ('error_tail_concentration', 'Tail Concentration (p99/p50)'),
    ('bias_fraction', 'Bias Fraction')
]

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for idx, (metric, label) in enumerate(error_metrics):
    for prec in ['int8', 'fp16', 'fp32']:
        data = df_success[df_success['precision'] == prec]
        if len(data) > 0 and metric in data.columns:
            axes[idx].scatter(data['actual_cond_A'], data[metric],
                            label=prec.upper(), alpha=0.6, s=50,
                            color=colors[prec], marker=markers[prec])

    axes[idx].set_xlabel('Condition Number', fontsize=10)
    axes[idx].set_ylabel(label, fontsize=10)
    axes[idx].set_xscale('log')
    if metric not in ['error_tail_concentration', 'bias_fraction']:
        axes[idx].set_yscale('log')
    axes[idx].legend(fontsize=8)
    axes[idx].set_title(label, fontsize=11, fontweight='bold')
    axes[idx].grid(True, alpha=0.3, which='both')

fig.suptitle('All Error Metrics vs Condition Number',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cond_05_all_error_metrics.png', dpi=300)
plt.close()
print("    Saved: cond_05_all_error_metrics.png")

# ============================================================================
# PLOT 6: PERFORMANCE vs CONDITION NUMBER
# ============================================================================
print("[6/7] Generating Performance vs Condition Number...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: GOPS vs Condition Number
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax1.scatter(data['actual_cond_A'], data['gops'],
                   label=prec.upper(), alpha=0.6, s=80,
                   color=colors[prec], marker=markers[prec])

ax1.set_xlabel('Condition Number', fontsize=12)
ax1.set_ylabel('Performance (GOPS)', fontsize=12)
ax1.set_xscale('log')
ax1.legend(fontsize=11)
ax1.set_title('Does Conditioning Affect Performance?\n(Should be independent)',
             fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Plot 2: Simulation Time vs Condition Number
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        ax2.scatter(data['actual_cond_A'], data['sim_time_sec'],
                   label=prec.upper(), alpha=0.6, s=80,
                   color=colors[prec], marker=markers[prec])

ax2.set_xlabel('Condition Number', fontsize=12)
ax2.set_ylabel('Simulation Time (seconds)', fontsize=12)
ax2.set_xscale('log')
ax2.legend(fontsize=11)
ax2.set_title('Simulation Time vs Conditioning\n(Hardware should be independent)',
             fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cond_06_performance_vs_cond.png', dpi=300)
plt.close()
print("    Saved: cond_06_performance_vs_cond.png")

# ============================================================================
# PLOT 7: 3D SURFACE PLOT - Condition vs Matrix Size vs Error
# ============================================================================
print("[7/7] Generating 3D Analysis (Condition × Size × Error)...")

fig = plt.figure(figsize=(16, 12))

for idx, prec in enumerate(['int8', 'fp16', 'fp32']):
    data = df_success[df_success['precision'] == prec].copy()

    if len(data) > 5:
        # 3D scatter plot
        ax = fig.add_subplot(2, 3, idx + 1, projection='3d')

        data['matrix_size'] = data['M'] * data['K'] * data['N']

        scatter = ax.scatter(np.log10(data['actual_cond_A']),
                           np.log10(data['matrix_size']),
                           np.log10(data['norm_rel_error']),
                           c=np.log10(data['norm_rel_error']),
                           cmap='hot',
                           s=80,
                           alpha=0.6)

        ax.set_xlabel('log₁₀(Condition Number)', fontsize=9)
        ax.set_ylabel('log₁₀(Matrix Size)', fontsize=9)
        ax.set_zlabel('log₁₀(Error)', fontsize=9)
        ax.set_title(f'{prec.upper()} - 3D Error Landscape', fontsize=11, fontweight='bold')
        plt.colorbar(scatter, ax=ax, shrink=0.5)

        # 2D projection: Condition vs Error (colored by size)
        ax2 = fig.add_subplot(2, 3, idx + 4)

        scatter2 = ax2.scatter(data['actual_cond_A'],
                              data['norm_rel_error'],
                              c=data['matrix_size'],
                              cmap='viridis',
                              s=100,
                              alpha=0.6,
                              edgecolors='black',
                              linewidths=0.5)

        ax2.set_xlabel('Condition Number', fontsize=10)
        ax2.set_ylabel('Normalized Relative Error', fontsize=10)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_title(f'{prec.upper()} - Colored by Matrix Size', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        cbar = plt.colorbar(scatter2, ax=ax2)
        cbar.set_label('Matrix Size (M×K×N)', fontsize=9)

fig.suptitle('3D Error Analysis: Condition Number × Matrix Size × Error',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cond_07_3d_analysis.png', dpi=300)
plt.close()
print("    Saved: cond_07_3d_analysis.png")

# ============================================================================
# STATISTICAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("CONDITION NUMBER SENSITIVITY - STATISTICAL SUMMARY")
print("=" * 80)

print("\n--- ERROR GROWTH SLOPES (d(log error)/d(log cond)) ---")
if slopes:
    for prec in ['int8', 'fp16', 'fp32']:
        if prec in slopes:
            print(f"{prec.upper():5s}: slope = {slopes[prec]:7.4f}, R² = {r_squared[prec]:.4f}")
            if slopes[prec] < 0.1:
                print(f"       → Very robust to conditioning (slope ≈ 0)")
            elif slopes[prec] < 0.5:
                print(f"       → Moderately sensitive to conditioning")
            else:
                print(f"       → Highly sensitive to conditioning")
else:
    print("Insufficient data for slope calculation")

print("\n--- CONDITION NUMBER RANGES ---")
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 0:
        cond_min = data['actual_cond_A'].min()
        cond_max = data['actual_cond_A'].max()
        cond_mean = data['actual_cond_A'].mean()
        print(f"{prec.upper():5s}: min={cond_min:.2e}, max={cond_max:.2e}, mean={cond_mean:.2e}")

print("\n--- ERROR AMPLIFICATION FACTORS ---")
print("(Worst case error / Best case error)")
for prec in ['int8', 'fp16', 'fp32']:
    data = df_success[df_success['precision'] == prec]
    if len(data) > 5:
        best_error = data['norm_rel_error'].min()
        worst_error = data['norm_rel_error'].max()
        amplification = worst_error / best_error
        print(f"{prec.upper():5s}: {amplification:.2f}× amplification")

print("\n" + "=" * 80)
print(f"ALL PLOTS SAVED TO: {PLOTS_DIR}")
print("=" * 80)
print("\nGenerated 7 condition number analysis plots:")
print("  cond_01_comprehensive_dashboard.png - Multi-panel overview")
print("  cond_02_error_amplification.png     - Normalized error growth")
print("  cond_03_binned_heatmap.png          - Condition bins vs precision")
print("  cond_04_error_growth_slope.png      - Sensitivity quantification")
print("  cond_05_all_error_metrics.png       - All error types vs conditioning")
print("  cond_06_performance_vs_cond.png     - Speed vs conditioning")
print("  cond_07_3d_analysis.png             - 3D error landscape")
print("\nDone!")
