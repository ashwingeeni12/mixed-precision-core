# Test Results Statistics - Comprehensive Explanation

This document explains every statistic in `comprehensive_results.csv`.

---

## 1. Test Identification (Columns 1-7)

### `timestamp`
- **What**: Date and time when the test was run
- **Format**: YYYY-MM-DD HH:MM:SS
- **Example**: "2025-11-08 22:56:54"
- **Purpose**: Track when each test was executed

### `case_id`
- **What**: Unique identifier for the test case (0-41)
- **Range**: 0-13 (low), 14-27 (medium), 28-41 (high)
- **Purpose**: Links test to specific condition number configuration

### `category`
- **What**: Condition number difficulty level
- **Values**:
  - "low" = condition numbers 1-10
  - "medium" = condition numbers 10-100
  - "high" = condition numbers 100-1000
- **Purpose**: Group tests by numerical difficulty

### `precision`
- **What**: Data type used for computation
- **Values**: "int8", "fp16", "fp32"
- **Purpose**: Compare accuracy across different precisions

### `M`, `K`, `N`
- **What**: Matrix dimensions for C = A×B
  - A is M×K
  - B is K×N
  - C is M×N
- **Value**: 8 (for all current tests)
- **Purpose**: Track matrix sizes (allows future expansion)

---

## 2. Condition Numbers (Columns 8-11)

### `requested_cond_A`
- **What**: Target condition number for matrix A
- **Formula**: Requested value for cond(A) = σ_max/σ_min
- **Purpose**: The conditioning we asked the generator to create
- **Note**: Actual may differ slightly due to random generation

### `requested_cond_B`
- **What**: Target condition number for matrix B
- **Formula**: Requested value for cond(B) = σ_max/σ_min
- **Purpose**: The conditioning we asked the generator to create

### `actual_cond_A`
- **What**: Measured condition number of generated matrix A
- **Formula**: ratio of largest to smallest singular value
  ```
  cond(A) = σ_max(A) / σ_min(A)
  ```
- **Why important**: Higher = more numerically unstable
- **Interpretation**:
  - cond ≈ 1: Perfect conditioning (orthogonal)
  - cond < 10: Well-conditioned
  - cond 10-100: Moderately conditioned
  - cond > 100: Ill-conditioned (prone to numerical errors)

### `actual_cond_B`
- **What**: Measured condition number of generated matrix B
- **Formula**: Same as actual_cond_A but for matrix B
- **Purpose**: Verify generator achieved target conditioning

---

## 3. Input Matrix A Statistics (Columns 12-15)

### `A_min`
- **What**: Smallest value in matrix A
- **Formula**: min(A[i,j]) for all i,j
- **Purpose**: Check data range and detect outliers

### `A_max`
- **What**: Largest value in matrix A
- **Formula**: max(A[i,j]) for all i,j
- **Purpose**: Check data range and dynamic range

### `A_mean`
- **What**: Average value of all elements in A
- **Formula**:
  ```
  mean(A) = (1/(M×K)) × Σ A[i,j]
  ```
- **Purpose**: Check if matrix is centered around zero
- **Ideal**: Close to 0 for unbiased data

### `A_std`
- **What**: Standard deviation of elements in A
- **Formula**:
  ```
  std(A) = sqrt((1/(M×K)) × Σ(A[i,j] - mean(A))²)
  ```
- **Purpose**: Measure spread/variance of matrix values
- **Interpretation**: Higher = more varied values

---

## 4. Input Matrix B Statistics (Columns 16-19)

### `B_min`, `B_max`, `B_mean`, `B_std`
- **What**: Same statistics as A, but for matrix B
- **Purpose**: Characterize second input matrix

---

## 5. Reference Output Statistics (Columns 20-23)

### `C_ref_min`
- **What**: Smallest value in reference output C_ref = A×B
- **Purpose**: Expected output range (lower bound)

### `C_ref_max`
- **What**: Largest value in reference output
- **Purpose**: Expected output range (upper bound)

### `C_ref_mean`
- **What**: Average value in reference output
- **Formula**: mean(C_ref) = (1/(M×N)) × Σ C_ref[i,j]
- **Purpose**: Expected central tendency

### `C_ref_std`
- **What**: Standard deviation of reference output
- **Formula**: std(C_ref)
- **Purpose**: Expected output variance

---

## 6. Absolute Error Metrics (Columns 24-26)

### `mae` (Mean Absolute Error)
- **What**: Average magnitude of errors
- **Formula**:
  ```
  MAE = (1/(M×N)) × Σ|C_out[i,j] - C_ref[i,j]|
  ```
- **Units**: Same as matrix values
- **Interpretation**:
  - Lower is better
  - 0 = perfect match
  - Shows average error magnitude
- **Use case**: Quick overall accuracy check

### `rmse` (Root Mean Square Error)
- **What**: Root mean square of errors
- **Formula**:
  ```
  RMSE = sqrt((1/(M×N)) × Σ(C_out[i,j] - C_ref[i,j])²)
  ```
- **Units**: Same as matrix values
- **Why different from MAE**: Penalizes large errors more heavily
- **Interpretation**:
  - RMSE ≥ MAE always
  - If RMSE >> MAE, there are outlier errors
  - Lower is better

### `max_abs_error`
- **What**: Largest single error in entire output
- **Formula**:
  ```
  max|C_out[i,j] - C_ref[i,j]| for all i,j
  ```
- **Purpose**: Find worst-case error
- **Critical for**: Hardware verification (checking no catastrophic failures)

---

## 7. Relative Error Metrics (Columns 27-30)

### `rel_mae` (Relative Mean Absolute Error)
- **What**: MAE normalized by average output magnitude
- **Formula**:
  ```
  rel_MAE = MAE / mean(|C_ref|)
  ```
- **Units**: Dimensionless (percentage when ×100)
- **Why important**: Allows comparing errors across different problem scales
- **Interpretation**:
  - 0.01 = 1% average error
  - 0.10 = 10% average error

### `rel_rmse` (Relative Root Mean Square Error)
- **What**: RMSE normalized by RMS of reference
- **Formula**:
  ```
  rel_RMSE = RMSE / sqrt(mean(C_ref²))
  ```
- **Units**: Dimensionless
- **Purpose**: Scale-independent accuracy measure

### `max_rel_error`
- **What**: Largest relative error at any element
- **Formula**:
  ```
  max(|C_out[i,j] - C_ref[i,j]| / |C_ref[i,j]|)
  ```
- **Note**: Skips elements where |C_ref| < 0.001 to avoid division by ~0
- **Purpose**: Find worst relative error
- **Critical**: Can reveal precision issues in small values

### `norm_rel_error`
- **What**: Error of entire matrix normalized by matrix norm
- **Formula**:
  ```
  norm_rel_error = ||C_out - C_ref||_F / ||C_ref||_F
  ```
  where ||·||_F is Frobenius norm: sqrt(Σ values²)
- **Why important**:
  - Standard metric in numerical linear algebra
  - Treats entire matrix as single entity
  - Robust to outliers
- **Interpretation**:
  - 0 = perfect
  - 0.001 = 0.1% matrix-level error
  - < 0.01 is typically excellent

---

## 8. Hardware Output Statistics (Columns 31-33)

### `C_out_mean`
- **What**: Mean of hardware output
- **Compare to**: C_ref_mean
- **Purpose**: Check for systematic bias

### `C_out_std`
- **What**: Standard deviation of hardware output
- **Compare to**: C_ref_std
- **Purpose**: Check if variance is preserved

### `mean_bias`
- **What**: Average signed error (systematic offset)
- **Formula**:
  ```
  mean_bias = (1/(M×N)) × Σ(C_out[i,j] - C_ref[i,j])
  ```
- **Units**: Same as matrix values
- **Interpretation**:
  - Positive = hardware tends to overestimate
  - Negative = hardware tends to underestimate
  - Near 0 = unbiased (errors cancel out)
- **Different from MAE**: MAE uses absolute values, this keeps sign

---

## 9. Error Distribution (Columns 34-37)

### `p50_error` (Median Error)
- **What**: 50th percentile of absolute errors
- **Formula**: median(|C_out - C_ref|)
- **Why important**:
  - Robust to outliers (unlike mean)
  - Represents "typical" error
- **Compare to MAE**: If p50 << MAE, errors are skewed by outliers

### `p90_error` (90th Percentile Error)
- **What**: 90% of errors are smaller than this
- **Formula**: 90th percentile of |C_out - C_ref|
- **Purpose**: Understand error distribution tail
- **Interpretation**: Only 10% of values have errors larger than this

### `p95_error` (95th Percentile Error)
- **What**: 95% of errors are smaller than this
- **Purpose**: Characterize near-worst-case errors

### `p99_error` (99th Percentile Error)
- **What**: 99% of errors are smaller than this
- **Purpose**: Near-maximum error (excluding extreme outliers)
- **Compare to max_abs_error**: Shows if max is truly exceptional

---

## 10. Signal Quality Metrics (Columns 38-39)

### `snr_db` (Signal-to-Noise Ratio in dB)
- **What**: Ratio of signal power to error power
- **Formula**:
  ```
  SNR_dB = 10 × log₁₀(power_signal / power_noise)
  power_signal = mean(C_ref²)
  power_noise = mean((C_out - C_ref)²)
  ```
- **Units**: Decibels (dB)
- **Interpretation**:
  - Higher is better
  - 0 dB = error power equals signal power (50% accuracy)
  - 20 dB = signal 100× stronger than noise (good)
  - 40 dB = signal 10,000× stronger (excellent)
  - 60 dB = signal 1,000,000× stronger (near perfect)
- **Why important**:
  - Standard metric in signal processing
  - Logarithmic scale shows wide quality range
  - Negative SNR = unusable output

### `correlation`
- **What**: Pearson correlation between C_out and C_ref
- **Formula**:
  ```
  r = cov(C_out, C_ref) / (std(C_out) × std(C_ref))
  ```
- **Range**: -1 to +1
- **Interpretation**:
  - +1 = perfect positive correlation (ideal)
  - 0 = no correlation (random)
  - -1 = perfect negative correlation (inverted)
- **Purpose**: Check if output maintains relationships even if scaled/biased

---

## 11. Accuracy Thresholds (Columns 40-42)

### `acc_1pct`
- **What**: Percentage of outputs within 1% of reference
- **Formula**:
  ```
  acc_1pct = (count of |C_out - C_ref| < 0.01×|C_ref|) / (M×N) × 100
  ```
- **Range**: 0-100%
- **Interpretation**:
  - 100% = all values within 1% (excellent)
  - 0% = no values within 1% (poor)

### `acc_5pct`
- **What**: Percentage of outputs within 5% of reference
- **Purpose**: Relaxed accuracy threshold

### `acc_10pct`
- **What**: Percentage of outputs within 10% of reference
- **Purpose**: Very relaxed threshold
- **Use case**: Even low-precision should achieve high acc_10pct

---

## 12. Norm-Based Metrics (Columns 43-44)

### `norm_C_ref`
- **What**: Frobenius norm of reference output
- **Formula**:
  ```
  ||C_ref||_F = sqrt(Σ C_ref[i,j]²)
  ```
- **Purpose**:
  - Scale of the problem
  - Denominator for normalized metrics
  - Represents "energy" in the output

### `norm_diff`
- **What**: Frobenius norm of the error matrix
- **Formula**:
  ```
  ||C_out - C_ref||_F = sqrt(Σ (C_out[i,j] - C_ref[i,j])²)
  ```
- **Purpose**: Total error magnitude
- **Relation**: norm_rel_error = norm_diff / norm_C_ref

---

## 13. Runtime (Column 45)

### `sim_time_sec`
- **What**: Wall-clock time for simulation in seconds
- **Includes**:
  - Compilation
  - Elaboration
  - Simulation runtime
  - File I/O
- **Purpose**: Track performance, identify slow tests

---

## 14. Status (Column 46)

### `status`
- **What**: Test outcome
- **Values**:
  - "success" = Test completed, results valid
  - "sim_failed" = Simulation error
  - "gen_failed" = Matrix generation error
  - "parse_failed" = Output parsing error
- **Purpose**: Filter valid results

---

## Summary: Key Metrics for Different Purposes

### For Overall Accuracy:
- **norm_rel_error** - Best single metric
- **rel_mae** - Easy to interpret
- **correlation** - Relationship preservation

### For Worst-Case Analysis:
- **max_abs_error** - Absolute worst case
- **max_rel_error** - Relative worst case
- **p99_error** - Excluding extreme outliers

### For Distribution Understanding:
- **p50_error** (median) vs **mae** (mean)
- **rmse** vs **mae** (outlier sensitivity)
- **acc_1pct, acc_5pct, acc_10pct** - Accuracy bands

### For Signal Quality:
- **snr_db** - Industry standard
- **correlation** - Linear relationship

### For Hardware Debugging:
- **mean_bias** - Systematic errors
- **C_out_mean** vs **C_ref_mean** - Output centering
- **C_out_std** vs **C_ref_std** - Variance preservation

### For Numerical Stability Analysis:
- **actual_cond_A, actual_cond_B** - Problem difficulty
- **norm_rel_error** - Scaled by problem size
- **snr_db** - Overall quality degradation
