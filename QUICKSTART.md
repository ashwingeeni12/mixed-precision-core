# Quick Start Guide - Running the Test Suite

## You're Ready to Run! 🚀

Since you've added Vivado to your PATH, you can now run the comprehensive test suite.

## Step-by-Step Instructions

### Step 1: Test Single Simulation (RECOMMENDED - 5 minutes)

Run this first to verify everything works:

```
run_single_test.bat
```

This will:
- ✓ Generate one test matrix (Case 0, FP16)
- ✓ Run Vivado simulation (~2-5 minutes)
- ✓ Parse results and compute metrics
- ✓ Display MAE, RMSE, Max Error

**If this succeeds**, you're ready for the full test suite!

### Step 2: Run All 126 Tests (4-10 hours)

```
run_all_tests.bat
```

This will automatically:
- Run 42 test cases × 3 precisions = 126 simulations
- Save results to `results\comprehensive_results.csv`
- Display progress as it runs

**Tip**: Leave this running overnight or during a long break.

### Step 3: Monitor Progress (Optional)

While tests are running, open a SECOND Command Prompt and run:

```
monitor_progress.bat
```

This will show:
- Number of tests completed (e.g., "45/126")
- Success/failure counts
- Latest test results
- Estimated time remaining
- Auto-refreshes every 30 seconds

### Step 4: Generate Excel Report

After all tests complete:

```
generate_report.bat
```

This creates `results\comprehensive_analysis.xlsx` with:
- ✓ Summary statistics by precision and condition number
- ✓ Precision comparison (INT8 vs FP16 vs FP32)
- ✓ Condition number analysis
- ✓ Error distribution charts
- ✓ Best and worst cases
- ✓ Multiple formatted sheets

## Files Created

### Input (Already Generated)
- `test_cases/case_XX_PREC/` - 126 test matrix pairs ✓
- `test_cases/all_test_metadata.json` - Metadata ✓
- `results/test_inventory.xlsx` - Test inventory ✓

### Output (After Running Tests)
- `results/comprehensive_results.csv` - Raw results data
- `results/comprehensive_analysis.xlsx` - Final Excel report
- `results/test_run.log` - Detailed execution log

## What Each Test Does

For each of the 126 test cases:

1. **Load matrices**: Copy A.mem, B.mem from test_cases to mem/
2. **Set precision**: PREC_SEL = 0 (INT8), 1 (FP16), or 2 (FP32)
3. **Run simulation**: Vivado xsim behavioral simulation
4. **Save output**: Hardware result to mem/C_out.mem
5. **Parse**: Convert hex to CSV (C_out.csv)
6. **Compare**: C_out.csv vs C_ref.csv (ground truth)
7. **Compute metrics**:
   - MAE, RMSE, Max Error
   - Relative errors
   - SNR, Correlation
   - Percentile errors (P50, P90, P95, P99)
   - Accuracy rates (1%, 5%, 10%)
8. **Save**: Append row to comprehensive_results.csv

## Timeline

**Single Test**: ~2-5 minutes
- Project creation: 10s
- Compilation: 30s
- Simulation: 60-240s
- Parsing: 1s

**Full Suite (126 tests)**: ~4-10 hours
- Fast simulations: ~4 hours (120s avg)
- Typical: ~6 hours (180s avg)
- Slow system: ~10 hours (300s avg)

**Recommendation**: Run overnight

## Monitoring Your Run

### Check Progress File
```batch
type results\comprehensive_results.csv
```

### Count Completed Tests
```batch
find /c /v "" results\comprehensive_results.csv
```

Subtract 1 for header line.

### View Latest Results
```batch
powershell "Get-Content results\comprehensive_results.csv | Select-Object -Last 5"
```

## Troubleshooting

### Simulation Fails
- **Check**: Did single test work?
- **Try**: Close and restart Command Prompt
- **Verify**: `where xvlog` shows path

### Python Import Errors
```batch
pip install numpy pandas openpyxl
```

### Out of Disk Space
Each simulation creates ~50MB of temp files.
Clean up between runs:
```batch
rmdir /s /q mp_sim
```

### Vivado License Issues
Ensure Vivado license server is accessible.

## What to Expect

### Typical Results

**INT8 (Low Condition)**:
- MAE: 0.1 - 1.0
- RMSE: 0.2 - 1.5
- SNR: 35-50 dB

**FP16 (Low Condition)**:
- MAE: 0.001 - 0.01
- RMSE: 0.002 - 0.02
- SNR: 70-90 dB

**FP32 (Low Condition)**:
- MAE: 0.00001 - 0.0001
- RMSE: 0.00002 - 0.0002
- SNR: 100-120 dB

**High Condition Numbers**: Expect 10-100x larger errors

## Next Steps After Tests Complete

1. **Review Excel Report**:
   - Open `results\comprehensive_analysis.xlsx`
   - Check "Summary Statistics" sheet
   - Compare precisions in "Precision Comparison" sheet
   - Analyze condition number impact

2. **Identify Trends**:
   - How does accuracy degrade with condition number?
   - At what condition number does INT8 become unacceptable?
   - Is FP16 sufficient for your application?

3. **Make Decisions**:
   - Choose appropriate precision for your use case
   - Determine acceptable condition number range
   - Identify any design issues

## Ready to Start?

**Recommended First-Time Workflow**:

1. Run single test: `run_single_test.bat` (5 min)
2. If successful, start full suite: `run_all_tests.bat` (overnight)
3. Monitor in separate window: `monitor_progress.bat`
4. When complete, generate report: `generate_report.bat`
5. Analyze results in Excel

---

## Quick Reference

| Task | Command | Time |
|------|---------|------|
| Test one simulation | `run_single_test.bat` | 5 min |
| Run all 126 tests | `run_all_tests.bat` | 4-10 hours |
| Monitor progress | `monitor_progress.bat` | Continuous |
| Generate Excel report | `generate_report.bat` | 1 min |

**Let's go! Start with `run_single_test.bat` to verify everything works.**
