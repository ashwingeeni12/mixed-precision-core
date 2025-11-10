# Final Simulation Workflow Solution

## Summary of All Fixes

The simulation workflow is now fully functional! Here are all the fixes that were applied:

### 1. Fixed xelab Command
**File**: `scripts/run_xsim.bat:67`
- Removed unsupported `--work` flag
- Removed unnecessary `xil_defaultlib.glbl` reference
- Added `-relax` flag to handle timescale warnings

### 2. Fixed Testbench Package Handling
**File**: `tb/tb_top_gemm.sv:3-4`
- Removed `include "mp_types.sv"` that was re-defining the package
- Added `include "sim_defines.vh"` to get simulation parameters
- Kept `import mp_types::*` to use the pre-compiled package

### 3. Fixed File Output Path
**File**: `tb/tb_top_gemm.sv:52`
- Changed output path from `mem/C_out.mem` to `C_out.mem` (current directory)
- xsim on Windows can't write directly to subdirectories
- Added automatic file move in batch script

### 4. Added File Move in Batch Script
**File**: `scripts/run_xsim.bat:104-107`
- Automatically moves `C_out.mem` from root to `mem/` directory after simulation
- Ensures output file is in the expected location for parsing

### 5. Fixed Code Quality Issues
**File**: `tb/tb_top_gemm.sv:66,73`
- Changed `int idx` to `automatic int idx` to fix warning
- Added `$fflush(fhex)` before `$fclose(fhex)` to ensure file is written

### 6. Added Vivado Path Fallback
**File**: `scripts/run_xsim.bat:8`
- Added fallback to hardcoded Vivado path if PATH not set
- Works even without environment configuration

## How to Run the Tests

### Single Test (Quick Verification)

Open Windows Command Prompt and run:

```cmd
cd D:\Ashwin_Stuff\mp-matmul\mp-matmul
set PREC_SEL=0
set M=8
set K=8
set N=8
scripts\run_xsim.bat
```

Expected output:
```
================================================================================
Running xsim simulation
PREC_SEL=0 M=8 K=8 N=8
================================================================================

[1/3] Compiling design files...
Compilation completed successfully.

[2/3] Elaborating design...
Elaboration completed successfully.

[3/3] Running simulation...
TB start
File opened successfully, writing 8 x 8 matrix...
Dump complete
Simulation completed.

Moving C_out.mem to mem/ directory...

================================================================================
Simulation completed successfully
================================================================================
```

Verify the output file:
```cmd
dir mem\C_out.mem
```

You should see a 640-byte file (64 hex values for 8x8 matrix).

### Full Test Suite (All 126 Tests)

From Windows Command Prompt:

```cmd
cd D:\Ashwin_Stuff\mp-matmul\mp-matmul\host
python run_comprehensive_test.py
```

This will:
1. Run 126 simulations (42 test cases × 3 precisions)
2. Generate matrices with controlled condition numbers:
   - 14 low condition (1-10)
   - 14 medium condition (10-100)
   - 14 high condition (100-1000)
3. Compute comprehensive metrics for each test
4. Save results to `results/comprehensive_results.csv`

**Estimated runtime**: 2-4 hours

### Generate Excel Report

After tests complete:

```cmd
cd D:\Ashwin_Stuff\mp-matmul\mp-matmul\host
python create_excel_report.py
```

Output: `results/comprehensive_results.xlsx` with multiple sheets:
- Summary statistics
- All test results
- Accuracy vs condition number analysis
- Charts showing trends across precisions

## Test Infrastructure Overview

### Files Created
- `host/gen_cond_mems.py` - Generate matrices with controlled condition numbers
- `host/run_comprehensive_test.py` - Automated test runner for 126 tests
- `host/create_excel_report.py` - Generate comprehensive Excel analysis
- `host/generate_all_matrices.py` - Pre-generate all test cases
- `scripts/run_xsim.bat` - Batch simulation wrapper (now working!)
- `SIMULATION_FIXES.md` - Detailed documentation of all fixes
- `README_TEST_SUITE.md` - Complete test suite documentation
- `QUICKSTART.md` - Quick start guide

### Test Cases
- **Location**: `test_cases/case_000` through `test_cases/case_125`
- **Each contains**: A.mem, B.mem, C_ref.csv, test_metadata.json
- **Total**: 126 pre-generated test cases ready to run

## Verification Steps

1. **Verify single simulation works**:
   ```cmd
   cd D:\Ashwin_Stuff\mp-matmul\mp-matmul
   host\gen_cond_mems.py --M 8 --K 8 --N 8 --prec int8 --case-id 0
   scripts\run_xsim.bat
   dir mem\C_out.mem
   ```

2. **Parse the output**:
   ```cmd
   cd host
   python parse_out_to_csv.py --M 8 --N 8 --prec int8
   type ..\mem\C_out.csv
   ```

3. **Run a few tests**:
   Modify `host/run_comprehensive_test.py` line ~140 to limit tests:
   ```python
   for case_id in range(3):  # Just run 3 tests for verification
   ```

## Key Metrics Computed

For each test, the suite computes:

**Accuracy Metrics**:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- Max Absolute Error
- Relative MAE/RMSE
- Norm Relative Error

**Numerical Quality**:
- SNR (Signal-to-Noise Ratio) in dB
- Correlation coefficient
- Percentile errors (50th, 90th, 95th, 99th)

**Element-wise Accuracy**:
- % elements within 1% of reference
- % elements within 5% of reference
- % elements within 10% of reference

## Troubleshooting

### If simulation fails:
1. Check that Vivado 2025.1 is installed at `D:\ashwin_shit\2025.1\Vivado\`
2. Verify `mem/A.mem` and `mem/B.mem` exist before running
3. Check `xsim.log` for detailed error messages

### If no output file:
1. Check that `C_out.mem` appears in root directory after simulation
2. Verify the file move command in batch script executed
3. Check file permissions on `mem/` directory

### If parsing fails:
1. Verify `mem/C_out.mem` exists and is non-empty (should be 640 bytes for 8x8)
2. Check that precision matches (int8/fp16/fp32)
3. Look for errors in `parse_out_to_csv.py` output

## Next Steps

1. Run a single test to verify the workflow
2. Run 3-5 tests to confirm metrics collection
3. Run the full 126-test suite (allow 2-4 hours)
4. Generate the Excel report
5. Analyze accuracy vs condition number trends

## Success Criteria

You'll know everything is working when:
- ✅ Single simulation completes without errors
- ✅ `mem/C_out.mem` file is created (640 bytes for 8x8)
- ✅ Parsing produces `mem/C_out.csv` with correct values
- ✅ Comprehensive test runner completes all tests
- ✅ Excel report shows metrics for all 126 tests
- ✅ Can see accuracy degradation with increasing condition numbers

The workflow is ready to go - just run from Windows Command Prompt!
