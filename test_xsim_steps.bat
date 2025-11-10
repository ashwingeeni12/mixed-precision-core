@echo off
echo ===== Testing xsim steps manually =====
echo.

set PREC_SEL=1
set M=8
set K=8
set N=8

echo Step 1: Create defines header
echo // Auto-generated defines > src\sim_defines.vh
echo `define PREC_SEL %PREC_SEL% >> src\sim_defines.vh
echo `define M %M% >> src\sim_defines.vh
echo `define K %K% >> src\sim_defines.vh
echo `define N %N% >> src\sim_defines.vh
echo Created src\sim_defines.vh
type src\sim_defines.vh
echo.

echo Step 2: Check if xsim.dir exists
if exist xsim.dir (
    echo Found xsim.dir from previous run
    dir xsim.dir
) else (
    echo No xsim.dir found
)
echo.

echo Step 3: Try elaboration directly
echo Running: xelab -debug typical --work xil_defaultlib --snapshot tb_top_gemm_snap xil_defaultlib.tb_top_gemm xil_defaultlib.glbl
xelab -debug typical --work xil_defaultlib --snapshot tb_top_gemm_snap xil_defaultlib.tb_top_gemm xil_defaultlib.glbl

echo.
echo Elaboration exit code: %ERRORLEVEL%
echo.

if %ERRORLEVEL% EQU 0 (
    echo Step 4: Try simulation
    echo Running: xsim tb_top_gemm_snap --tclbatch scripts\run_xsim.tcl --log xsim.log
    xsim tb_top_gemm_snap --tclbatch scripts\run_xsim.tcl --log xsim.log
    echo.
    echo Simulation exit code: %ERRORLEVEL%
    echo.

    if exist mem\C_out.mem (
        echo SUCCESS! Output file created
        dir mem\C_out.mem
    ) else (
        echo FAILED: Output file not found
        if exist xsim.log (
            echo === Simulation Log ===
            type xsim.log
        )
    )
) else (
    echo Elaboration failed!
    if exist xelab.log (
        echo === Elaboration Log ===
        type xelab.log
    )
)

pause
