@echo off
REM Simplified xsim simulation - runs without TCL batch file
REM Expects PREC_SEL, M, K, N environment variables to be set

setlocal

REM Vivado tools path - fallback if not in PATH
if not defined VIVADO_BIN set VIVADO_BIN=D:\ashwin_shit\2025.1\Vivado\bin

REM Check environment variables
if not defined PREC_SEL set PREC_SEL=0
if not defined M set M=8
if not defined K set K=8
if not defined N set N=8

echo ================================================================================
echo Running xsim simulation (SIMPLE MODE)
echo PREC_SEL=%PREC_SEL% M=%M% K=%K% N=%N%
echo ================================================================================

REM Clean up old simulation files
if exist xsim.dir rmdir /s /q xsim.dir
if exist xsim.log del /q xsim.log
if exist xvlog.log del /q xvlog.log
if exist xelab.log del /q xelab.log
if exist C_out.mem del /q C_out.mem

REM Create defines header file
echo // Auto-generated defines > src\sim_defines.vh
echo `define PREC_SEL %PREC_SEL% >> src\sim_defines.vh
echo `define M %M% >> src\sim_defines.vh
echo `define K %K% >> src\sim_defines.vh
echo `define N %N% >> src\sim_defines.vh

REM Create project file
echo sv xil_defaultlib src\mp_types.sv > compile.prj
echo sv xil_defaultlib src\fp16_mul_ip.sv >> compile.prj
echo sv xil_defaultlib src\fp16_add_ip.sv >> compile.prj
echo sv xil_defaultlib src\fp32_mul_ip.sv >> compile.prj
echo sv xil_defaultlib src\fp32_add_ip.sv >> compile.prj
echo sv xil_defaultlib src\dp_bram.sv >> compile.prj
echo sv xil_defaultlib src\int8_mac.sv >> compile.prj
echo sv xil_defaultlib src\fp16_mul.sv >> compile.prj
echo sv xil_defaultlib src\fp16_add.sv >> compile.prj
echo sv xil_defaultlib src\fp32_mul.sv >> compile.prj
echo sv xil_defaultlib src\fp32_add.sv >> compile.prj
echo sv xil_defaultlib src\pe_cell.sv >> compile.prj
echo sv xil_defaultlib src\systolic_array.sv >> compile.prj
echo sv xil_defaultlib src\gemm_controller.sv >> compile.prj
echo sv xil_defaultlib src\top_gemm.sv >> compile.prj
echo sv xil_defaultlib tb\tb_top_gemm.sv >> compile.prj

echo.
echo [1/3] Compiling design files...
call "%VIVADO_BIN%\xvlog.bat" -sv -i src --work xil_defaultlib --prj compile.prj 2>&1

if errorlevel 1 (
    echo ERROR: Compilation failed!
    if exist xvlog.log type xvlog.log
    exit /b 1
)

echo Compilation completed successfully.

echo.
echo [2/3] Elaborating design...
call "%VIVADO_BIN%\xelab.bat" -debug typical ^
    -relax ^
    --snapshot tb_top_gemm_snap ^
    xil_defaultlib.tb_top_gemm 2>&1

if errorlevel 1 (
    echo ERROR: Elaboration failed!
    if exist xelab.log (
        echo.
        echo === Elaboration Log ===
        type xelab.log
    )
    exit /b 1
)

echo Elaboration completed successfully.

echo.
echo [3/3] Running simulation...
echo Running: xsim tb_top_gemm_snap -runall
call "%VIVADO_BIN%\xsim.bat" tb_top_gemm_snap -runall

set XSIM_ERROR=%ERRORLEVEL%
echo Simulation exited with code: %XSIM_ERROR%

if %XSIM_ERROR% NEQ 0 (
    echo ERROR: Simulation failed!
    exit /b 1
)

echo Simulation completed.

REM Move output file from root to mem/ directory
if exist C_out.mem (
    echo Moving C_out.mem to mem/ directory...
    move /Y C_out.mem mem\C_out.mem >nul
)

REM Check if output was created
if not exist mem\C_out.mem (
    echo WARNING: mem\C_out.mem was not created
    echo Simulation may not have completed properly
    exit /b 1
)

echo.
echo ================================================================================
echo Simulation completed successfully
echo Output file: mem\C_out.mem
echo ================================================================================
endlocal
