@echo off
echo ================================================================================
echo Quick Single Test - Verify Setup
echo ================================================================================
echo.
echo This will run ONE simulation to verify everything is working
echo Test: Case 0, FP16 precision
echo Estimated time: 2-5 minutes
echo.
pause

echo.
echo [1/4] Generating test matrices...
cd /d "%~dp0host"
python gen_cond_mems.py --M 8 --K 8 --N 8 --prec fp16 --case-id 0

if errorlevel 1 (
    echo ERROR: Matrix generation failed!
    pause
    exit /b 1
)

echo.
echo [2/4] Running xsim simulation...
cd /d "%~dp0"
set PREC_SEL=1
set M=8
set K=8
set N=8

call scripts\run_xsim.bat

if errorlevel 1 (
    echo ERROR: Simulation failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Parsing output...
cd /d "%~dp0host"
python parse_out_to_csv.py --M 8 --N 8 --prec fp16

if errorlevel 1 (
    echo ERROR: Output parsing failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Computing metrics...
python -c "import numpy as np; C_ref = np.loadtxt('../mem/C_ref.csv', delimiter=','); C_out = np.loadtxt('../mem/C_out.csv', delimiter=','); diff = C_out - C_ref; print(f'MAE: {np.mean(np.abs(diff)):.6f}'); print(f'RMSE: {np.sqrt(np.mean(diff**2)):.6f}'); print(f'Max Error: {np.max(np.abs(diff)):.6f}')"

echo.
echo ================================================================================
echo SUCCESS! Single test completed.
echo.
echo If this worked, you can now run the full test suite:
echo   run_all_tests.bat
echo ================================================================================
pause
