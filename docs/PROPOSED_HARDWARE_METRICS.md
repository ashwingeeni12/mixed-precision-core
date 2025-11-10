# Proposed Hardware-Specific Metrics

Additional statistics to better characterize hardware performance and behavior.

---

## 1. PERFORMANCE METRICS

### Throughput & Latency
```
ops_per_second        - Effective operations/sec (M×K×N×2 / sim_time_sec)
gops                  - Giga-operations per second (ops_per_second / 1e9)
latency_cycles        - Clock cycles from start to first valid output
throughput_cycles     - Clock cycles for entire computation
cycles_per_mac        - Average cycles per multiply-accumulate
pipeline_efficiency   - Actual throughput / theoretical max (%)
```

**Why important:**
- Compare different precisions (INT8 should be fastest)
- Measure pipeline effectiveness
- Calculate speedup over software

### Theoretical Performance
```
theoretical_gops      - Max GOPS if fully utilized
utilization_pct       - Actual vs theoretical performance
mac_units_active      - Average number of MACs active per cycle
```

---

## 2. RESOURCE UTILIZATION

### Logic Resources (from synthesis reports)
```
lut_count            - Lookup tables used
ff_count             - Flip-flops used
dsp_count            - DSP blocks used
bram_count           - Block RAMs used
logic_efficiency     - GOPS per LUT
dsp_efficiency       - GOPS per DSP
```

### Power Metrics (if available from simulation)
```
dynamic_power_mw     - Dynamic power consumption (mW)
static_power_mw      - Static power (leakage)
total_power_mw       - Total power
energy_per_op_pj     - Pico-joules per operation
gops_per_watt        - Performance per watt
```

**Why important:**
- Area-performance tradeoff
- Power efficiency comparison
- Cost-benefit analysis per precision

---

## 3. HARDWARE ERROR PATTERNS

### Overflow/Saturation Detection
```
overflow_count       - Number of overflow events detected
saturation_count     - Number of saturated values
overflow_pct         - % of operations that overflowed
max_intermediate     - Largest intermediate value (for range analysis)
```

**Implementation:** Track saturation flags in MAC units

### Range Utilization
```
int8_range_used_pct  - % of INT8 range actually used (-128 to 127)
int8_headroom        - Unused dynamic range (dB)
signed_bit_usage     - Are negative values being used effectively?
```

**Why important:**
- Optimize precision selection
- Detect quantization inefficiency
- Guide scaling factor selection

### Bit-Level Error Analysis
```
error_msb_count      - Errors in most significant bits
error_lsb_count      - Errors in least significant bits
bit_flip_pattern     - Which bit positions have most errors
sign_bit_errors      - Number of sign flips (catastrophic!)
```

**Why important:**
- Different from magnitude errors
- Sign errors are catastrophic
- LSB errors may be acceptable

---

## 4. NUMERICAL STABILITY INDICATORS

### Accumulation Error Growth
```
accumulation_error_growth - Error increase during accumulation
                           = ||error_final|| / ||error_first_mac||
catastrophic_cancellation - Count of near-zero results from large values
loss_of_significance     - Precision lost during subtraction
```

**Example:** If A[0,0]×B[0,0] = 1e6 but final sum = 10, check for cancellation

### Denormal/Subnormal Handling (FP16/FP32)
```
denormal_count       - Number of denormal/subnormal values
denormal_flush_count - Times denormals were flushed to zero
denormal_impact      - Accuracy difference with/without denormal support
```

**Why important:**
- Hardware often flushes denormals to zero for speed
- Can cause significant errors in ill-conditioned matrices

---

## 5. PRECISION-SPECIFIC METRICS

### Quantization Analysis (INT8)
```
quantization_noise   - RMS quantization noise
effective_bits       - Effective number of bits (ENOB)
                      = -log2(norm_rel_error)
snqr_db             - Signal-to-Quantization-Noise Ratio
```

**Example:**
- 8-bit perfect = ENOB = 8
- If norm_rel_error = 0.01, ENOB = 6.64 bits

### Floating-Point Analysis (FP16/FP32)
```
fp_exception_count   - Invalid operations, div by zero, etc.
rounding_error_contrib - Error purely from rounding
ulp_error_max        - Error in Units in Last Place
ulp_error_mean       - Average ULP error
```

**Why important:**
- ULP is standard FP error metric
- 0.5 ULP = optimal rounding
- >1 ULP = precision loss

---

## 6. MEMORY & BANDWIDTH

### Memory Access Patterns
```
mem_read_bytes       - Total bytes read from memory
mem_write_bytes      - Total bytes written
mem_bandwidth_gbps   - GB/s (read+write / sim_time_sec)
mem_efficiency_pct   - Useful vs total memory accesses
cache_hit_rate       - If using caching
```

### Data Reuse
```
data_reuse_factor    - How many times each value is reused
                      = total_operations / unique_loads
arithmetic_intensity - Operations per byte transferred
                      = (M×K×N×2) / mem_bytes
```

**Why important:**
- Memory is often bottleneck
- High reuse = better performance
- Arithmetic intensity drives roofline analysis

---

## 7. DATAPATH ANALYSIS

### Pipeline Metrics
```
pipeline_stalls      - Number of pipeline stall cycles
pipeline_bubbles     - Empty pipeline stages
ipc                  - Instructions per cycle (should be ~1 for systolic)
pipeline_depth       - Measured latency in cycles
```

### Systolic Array Specific
```
pe_utilization       - % of PEs doing useful work
systolic_wavefront   - Cycles to fill/drain array
edge_waste           - Wasted cycles at array boundaries
```

---

## 8. ERROR DECOMPOSITION

### Error Source Attribution
```
rounding_error_only  - Error from rounding alone (vs infinite precision)
truncation_error     - Error from bit-width limits
algorithmic_error    - Error from algorithm (e.g., accumulation order)
total_error         - Sum of all error sources
```

**Measurement approach:**
1. Run with higher precision to isolate rounding
2. Compare different accumulation orders
3. Use arbitrary precision reference

### Per-Precision Comparison
```
int8_vs_fp16_speedup    - How much faster is INT8
int8_vs_fp16_accuracy   - Accuracy loss for speed gain
fp16_vs_fp32_speedup    - FP16 speedup over FP32
fp16_vs_fp32_accuracy   - FP16 accuracy vs FP32
pareto_efficiency       - On speed/accuracy Pareto frontier?
```

---

## 9. CONDITION NUMBER CORRELATION

### Numerical Difficulty Impact
```
error_vs_cond_slope     - How error grows with condition number
                         = d(norm_rel_error)/d(log(cond))
error_amplification     - Error increase factor vs well-conditioned case
cond_sensitivity        - Is this precision sensitive to conditioning?
```

**Analysis:**
- Plot norm_rel_error vs cond(A) for each precision
- INT8 should be less sensitive (already low precision)
- FP32 should handle high condition numbers better

---

## 10. HARDWARE ANOMALY DETECTION

### Unexpected Behavior
```
outlier_error_count     - Errors >10× median error
anomaly_locations       - Spatial pattern of large errors
error_correlation       - Do errors cluster in matrix regions?
reproducibility_check   - Same result on re-run? (detect non-determinism)
```

### Debugging Metrics
```
first_error_index       - Which matrix element first shows error
error_propagation       - Does error grow through computation?
zero_output_count       - Unexpected zero outputs (underflow?)
inf_nan_count           - Infinity or NaN results
```

---

## 11. COMPARATIVE ANALYSIS

### Cross-Precision Comparison
```
int8_mae_ratio          - INT8_mae / FP32_mae
fp16_mae_ratio          - FP16_mae / FP32_mae
precision_degradation   - Error increase per bit reduction
bits_vs_accuracy_slope  - d(accuracy)/d(bits)
```

### Performance-Accuracy Tradeoff
```
pareto_score            - Combined accuracy × speed metric
                         = (1/norm_rel_error) × gops
energy_accuracy_product - (1/norm_rel_error) × (1/energy_per_op)
```

**Use case:** Pick optimal precision for your constraints

---

## 12. REAL-TIME MONITORING METRICS

### Per-Row/Column Statistics
```
row_error_max[i]        - Max error in row i (array of M values)
col_error_max[j]        - Max error in column j (array of N values)
error_heatmap           - 2D error map (for visualization)
```

**Why important:**
- Detect spatial error patterns
- Find problematic rows/columns
- Visualize error distribution

### Temporal Error Evolution
```
error_at_25pct_complete - Error after 25% of accumulation
error_at_50pct_complete - Error at halfway point
error_at_75pct_complete - Error at 75%
error_growth_rate       - How fast error accumulates
```

**Use case:** Understand if errors accumulate linearly or accelerate

---

## IMPLEMENTATION PRIORITY

### Phase 1 (Easy to add, high value):
1. **ops_per_second, gops** - Just arithmetic on existing data
2. **overflow_count** - Add saturation flag monitoring
3. **int8_range_used_pct** - Analyze output range
4. **error_vs_cond_slope** - Post-process existing results
5. **int8_vs_fp16_speedup** - Compare sim_time_sec

### Phase 2 (Moderate effort):
1. **lut_count, dsp_count** - Parse synthesis reports
2. **pipeline_stalls** - Add cycle counter in testbench
3. **mem_bandwidth_gbps** - Count memory transactions
4. **effective_bits** - Calculate from norm_rel_error
5. **per_row/col_error** - Modify error calculation

### Phase 3 (Advanced):
1. **power metrics** - Requires power analysis tools
2. **bit_flip_pattern** - Detailed bit-level analysis
3. **ulp_error** - FP-specific analysis
4. **error_heatmap** - 2D visualization
5. **temporal error evolution** - Requires intermediate dumps

---

## EXAMPLE NEW COLUMNS TO ADD

```csv
# Performance
ops_per_second, gops, cycles_total, cycles_per_mac

# Resource (from synthesis)
lut_count, ff_count, dsp_count, bram_count

# Hardware errors
overflow_count, saturation_count, int8_range_used_pct

# Precision quality
effective_bits, snqr_db, ulp_error_mean

# Cross-precision comparison
int8_speedup_vs_fp32, int8_accuracy_vs_fp32
fp16_speedup_vs_fp32, fp16_accuracy_vs_fp32

# Numerical stability
error_growth_rate, catastrophic_cancellation_count

# Efficiency
gops_per_watt, pareto_score
```

---

## VISUALIZATION IDEAS

1. **Pareto Plot**: Speed vs Accuracy for each precision
2. **Error Heatmap**: Show which matrix elements have largest errors
3. **Condition Number Sensitivity**: Error vs cond(A) for each precision
4. **Resource Efficiency**: GOPS/LUT for each precision
5. **Bit Utilization**: Histogram of value distribution in INT8 range

