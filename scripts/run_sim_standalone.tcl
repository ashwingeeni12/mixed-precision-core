# Standalone simulation script using xsim directly (no project mode)
# Usage: xsim -mode batch -source scripts/run_sim_standalone.tcl

# Get environment variables
if {![info exists ::env(PREC_SEL)]} { set ::env(PREC_SEL) 0 }
if {![info exists ::env(M)]} { set ::env(M) 8 }
if {![info exists ::env(K)]} { set ::env(K) 8 }
if {![info exists ::env(N)]} { set ::env(N) 8 }

set PREC_SEL $::env(PREC_SEL)
set M $::env(M)
set K $::env(K)
set N $::env(N)

puts "Running simulation with PREC_SEL=$PREC_SEL M=$M K=$K N=$N"

# Define work directory
set work_dir "./xsim_work"
file mkdir $work_dir

# Set up defines
set defines "PREC_SEL=$PREC_SEL,M=$M,K=$K,N=$N"

# Compile SystemVerilog files
puts "Compiling design files..."
exec xvlog -sv -work xil_defaultlib \
    -d $defines \
    src/mp_types.sv \
    src/dp_bram.sv \
    src/int8_mac.sv \
    src/fp16_mul.sv \
    src/fp16_add.sv \
    src/fp32_mul.sv \
    src/fp32_add.sv \
    src/pe_cell.sv \
    src/systolic_array.sv \
    src/gemm_controller.sv \
    src/top_gemm.sv \
    tb/tb_top_gemm.sv

# Elaborate design
puts "Elaborating design..."
exec xelab -debug typical -top tb_top_gemm -snapshot tb_top_gemm_snap

# Run simulation
puts "Running simulation..."
exec xsim tb_top_gemm_snap -runall

puts "Simulation complete!"
quit
