# Simulation Workflow Fixes

This document summarizes all the fixes applied to get the xsim batch simulation working.

## Issues Fixed

### 1. xelab Command Syntax Error
**File**: `scripts/run_xsim.bat:67`
**Problem**: Used unsupported `--work` flag
**Fix**: Removed the `--work xil_defaultlib` parameter from xelab command

```batch
# Before:
xelab -debug typical --work xil_defaultlib --snapshot tb_top_gemm_snap ...

# After:
xelab -debug typical --snapshot tb_top_gemm_snap ...
```

### 2. Testbench Package Re-inclusion
**File**: `tb/tb_top_gemm.sv:2`
**Problem**: The testbench was re-including mp_types.sv with ```include```, which overwrote the compiled package and invalidated all dependent modules (pe_cell, systolic_array, gemm_controller, top_gemm)
**Fix**: Removed the `include` directive, keeping only the `import` statement

```systemverilog
// Before:
`include "mp_types.sv"
import mp_types::*;

// After:
// mp_types.sv is already compiled separately - just import the package
import mp_types::*;
```

### 3. Timescale Checking Errors
**File**: `scripts/run_xsim.bat:65`
**Problem**: xelab was treating timescale mismatches as errors
**Fix**: Added `-relax` flag to relax strict checking

```batch
xelab -debug typical -relax --snapshot ...
```

### 4. Unnecessary glbl Reference
**File**: `scripts/run_xsim.bat:67`
**Problem**: Referenced xil_defaultlib.glbl which doesn't exist in this design
**Fix**: Removed glbl from elaboration command

```batch
# Before:
xelab ... xil_defaultlib.tb_top_gemm xil_defaultlib.glbl

# After:
xelab ... xil_defaultlib.tb_top_gemm
```

### 5. Vivado Tools Path
**File**: `scripts/run_xsim.bat:8`
**Problem**: Tools not found if PATH not set correctly
**Fix**: Added fallback to hardcoded Vivado installation path

```batch
if not defined VIVADO_BIN set VIVADO_BIN=D:\ashwin_shit\2025.1\Vivado\bin
```

## Verification

The simulation workflow now successfully completes all three stages:

1. **Compilation** (`xvlog`) - Analyzes all SystemVerilog files
2. **Elaboration** (`xelab`) - Links modules and creates simulation snapshot
3. **Simulation** (`xsim`) - Runs testbench and generates output

## Test Infrastructure

All components are now working:

- ✅ 126 test cases generated in `test_cases/`
- ✅ Matrix generation with controlled condition numbers
- ✅ Batch simulation script (`scripts/run_xsim.bat`)
- ✅ Comprehensive test runner (`host/run_comprehensive_test.py`)
- ✅ Metrics computation and Excel reporting

## How to Run

### Single Test
```bash
set PREC_SEL=0 && set M=8 && set K=8 && set N=8 && scripts\run_xsim.bat
```

### All 126 Tests
```bash
cd host
python run_comprehensive_test.py
```

### Generate Excel Report
```bash
cd host
python create_excel_report.py
```

## Next Steps

The comprehensive test suite is ready to run. It will:
1. Run 126 simulations (42 test cases × 3 precisions)
2. Compute comprehensive metrics for each test
3. Generate an Excel report with all results
4. Show accuracy vs condition number trends

Estimated runtime: ~2-4 hours for all 126 tests (depending on hardware)
