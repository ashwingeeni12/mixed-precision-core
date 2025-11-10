# Mixed-Precision Matrix Multiplication Test Suite

## Overview

This test suite comprehensively evaluates a mixed-precision matrix multiplication accelerator across **126 test cases** (42 matrix pairs × 3 precisions):

- **Precisions**: INT8, FP16, FP32
- **Condition Numbers**: Low (1-10), Medium (10-100), High (100-1000)
- **Matrix Size**: 8×8×8 (M×K×N)

## Generated Test Cases

All 126 test matrix pairs have been pre-generated in `test_cases/` directory:

```
test_cases/
├── case_00_int8/      # Case 0, INT8 precision
│   ├── A.mem         # Matrix A in hex format
│   ├── B.mem         # Matrix B in hex format
│   ├── C_ref.csv     # Ground truth reference (float64)
│   └── test_metadata.json  # Test case metadata
├── case_00_fp16/      # Case 0, FP16 precision
├── case_00_fp32/      # Case 0, FP32 precision
...
└── case_41_fp32/      # Case 41, FP32 precision
```

### Test Case Distribution

| Category | Condition Number Range | Cases per Precision | Total Cases |
|----------|----------------------|-------------------|-------------|
| Low      | 1 - 10               | 14                | 42          |
| Medium   | 10 - 100             | 14                | 42          |
| High     | 100 - 1000           | 14                | 42          |

## Test Inventory

**Excel File**: `results/test_inventory.xlsx`

Contains:
- **All Test Cases**: Complete list with input characteristics
- **Summary**: Statistics by category and precision
- **Results Template**: Ready to fill with simulation data
- **By Precision**: Separate sheets for INT8, FP16, FP32

## Running Simulations

### Method 1: Vivado GUI (Recommended for Troubleshooting)

1. **Open Vivado**:
   ```
   D:\ashwin_shit\2025.1\Vivado\bin\vivado.bat
   ```

2. **Create Project**:
   - Tools → Run Tcl Script → `scripts/run_sim.tcl`
   - OR manually create project and add source files from `src/` and `tb/`

3. **Set Test Parameters**:
   Before simulation, set these Verilog defines:
   - `PREC_SEL`: 0 (INT8), 1 (FP16), or 2 (FP32)
   - `M`, `K`, `N`: Matrix dimensions (8, 8, 8)

4. **Load Test Data**:
   - Copy desired test case files to `mem/`:
     ```
     copy test_cases\case_00_int8\*.mem mem\
     copy test_cases\case_00_int8\C_ref.csv mem\
     ```

5. **Run Simulation**:
   - Simulation → Run Behavioral Simulation
   - Run → Run All

6. **Collect Results**:
   - Output: `mem/C_out.mem`
   - Parse to CSV: `python host/parse_out_to_csv.py --M 8 --N 8 --prec int8`
   - Compare: `mem/C_out.csv` vs `mem/C_ref.csv`

### Method 2: Batch Mode (Requires Environment Setup)

**Prerequisites**:
- Vivado bin directory in PATH
- Vivado settings64.bat sourced

**Run Single Test**:
```bash
# Set environment
set PREC_SEL=0
set M=8
set K=8
set N=8

# Copy test data
copy test_cases\case_00_int8\*.mem mem\
copy test_cases\case_00_int8\C_ref.csv mem\

# Run simulation
vivado -mode batch -source scripts/run_sim.tcl

# Parse results
python host/parse_out_to_csv.py --M 8 --N 8 --prec int8
```

### Method 3: Automated (After Fixing Environment)

Once Vivado environment is properly configured:

```bash
cd host
python run_comprehensive_test.py
```

## Metrics Collected

### Accuracy Metrics
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **Max Abs Error**: Maximum absolute difference
- **Rel MAE**: Relative Mean Absolute Error
- **Rel RMSE**: Relative Root Mean Square Error
- **Norm Rel Error**: Frobenius norm relative error

### Distribution Metrics
- **P50/P90/P95/P99 Error**: Error percentiles
- **SNR (dB)**: Signal-to-Noise Ratio
- **Correlation**: Pearson correlation coefficient

### Accuracy Rates
- **Acc 1%**: % elements within 1% relative error
- **Acc 5%**: % elements within 5% relative error
- **Acc 10%**: % elements within 10% relative error

### Performance
- **Sim Time**: Simulation runtime

## Scripts Reference

### Matrix Generation
```bash
# Generate specific test case
python host/gen_cond_mems.py --M 8 --K 8 --N 8 --prec fp16 --case-id 0

# Generate all 126 test cases
python host/generate_all_matrices.py
```

### Results Processing
```bash
# Parse simulation output
python host/parse_out_to_csv.py --M 8 --N 8 --prec fp16

# Create Excel inventory
python host/create_test_inventory.py

# Check progress (during batch run)
python host/check_progress.py
```

## Files Structure

```
mp-matmul/
├── src/                    # RTL source files
│   ├── mp_types.sv         # Type definitions
│   ├── top_gemm.sv         # Top module
│   ├── gemm_controller.sv  # Controller FSM
│   ├── pe_cell.sv          # Processing element
│   ├── int8_mac.sv         # INT8 MAC unit
│   ├── fp16_*.sv           # FP16 units
│   ├── fp32_*.sv           # FP32 units
│   └── dp_bram.sv          # Dual-port BRAM
├── tb/                     # Testbenches
│   └── tb_top_gemm.sv
├── scripts/                # TCL scripts
│   ├── run_sim.tcl         # Simulation script
│   ├── run_synth.tcl       # Synthesis script
│   └── run_vivado.bat      # Vivado wrapper (Windows)
├── host/                   # Python scripts
│   ├── gen_cond_mems.py    # Generate matrices with condition numbers
│   ├── generate_all_matrices.py  # Generate all 126 cases
│   ├── run_comprehensive_test.py # Automated test runner
│   ├── parse_out_to_csv.py # Parse output
│   ├── create_test_inventory.py  # Create Excel inventory
│   ├── create_excel_report.py    # Create results report
│   └── check_progress.py   # Monitor progress
├── test_cases/             # Generated test matrices (126 cases)
├── mem/                    # Working directory for simulations
└── results/                # Output results
    ├── test_inventory.xlsx # Test case inventory
    └── comprehensive_results.csv  # Results (when available)
```

## Workflow

1. **[DONE]** Generate test matrices → `test_cases/`
2. **[DONE]** Create test inventory → `results/test_inventory.xlsx`
3. **[TODO]** Run simulations for each test case
4. **[TODO]** Collect metrics
5. **[TODO]** Generate comprehensive Excel report

## Troubleshooting

### Vivado Simulation Fails

**Issue**: "The system cannot find the file specified" when running xsim

**Solution**:
1. Source Vivado settings:
   ```
   call "D:\ashwin_shit\2025.1\Vivado\settings64.bat"
   ```

2. Verify xsim is accessible:
   ```
   where xvlog
   where xelab
   where xsim
   ```

3. If using Git Bash, use cmd.exe or PowerShell instead

### Missing IP Cores

**Issue**: FP16/FP32 IP cores not found

**Solution**:
1. Run `scripts/create_fp_ip.tcl` to generate IP cores
2. Or use existing Vivado project with IP already generated

### Memory File Format

- **Format**: One hex value per line
- **Width**: 32 bits (8 hex digits)
- **Order**: Row-major (A[i,k] then A[i,k+1]...)

Example (INT8):
```
000000ff  # -1 (sign-extended to 32 bits)
00000005  # 5
```

Example (FP16):
```
00003c00  # 1.0 in FP16
0000c000  # -2.0 in FP16
```

## Next Steps

1. **Fix Vivado Environment**: Ensure xsim tools are accessible
2. **Run Test Subset**: Start with 3-5 cases to verify workflow
3. **Automate**: Use batch runner once environment is confirmed
4. **Analyze**: Generate comprehensive Excel report with all metrics
5. **Compare**: Analyze accuracy vs condition number, precision tradeoffs

## Contact

For issues with:
- **Test generation**: Check `host/gen_cond_mems.py`
- **Simulation**: Check `scripts/run_sim.tcl`
- **Results processing**: Check `host/parse_out_to_csv.py`
- **Excel reports**: Check `host/create_excel_report.py`

---

Generated: 2025-11-08
Test Suite Version: 1.0
