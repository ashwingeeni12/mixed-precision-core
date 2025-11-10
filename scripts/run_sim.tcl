# scripts/run_sim.tcl
# Usage: PREC_SEL={0|1|2} M=4 K=4 N=4 vivado -mode batch -source scripts/run_sim.tcl
if {![info exists ::env(PREC_SEL)]} { set ::env(PREC_SEL) 0 }
if {![info exists ::env(M)]} { set ::env(M) 4 }
if {![info exists ::env(K)]} { set ::env(K) 4 }
if {![info exists ::env(N)]} { set ::env(N) 4 }

# Remove old project if it exists
if {[file exists ./mp_sim]} {
    file delete -force ./mp_sim
}

create_project mp_sim ./mp_sim -part xc7a200tsbg484-1
set_property target_language Verilog [current_project]

# Add source files
add_files -fileset sources_1 src/mp_types.sv src/dp_bram.sv src/int8_mac.sv src/fp16_mul.sv src/fp16_add.sv src/fp32_mul.sv src/fp32_add.sv src/pe_cell.sv src/systolic_array.sv src/gemm_controller.sv src/top_gemm.sv
add_files -fileset sim_1 tb/tb_top_gemm.sv
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

# Set defines
set defs [format "PREC_SEL=%s M=%s K=%s N=%s" $::env(PREC_SEL) $::env(M) $::env(K) $::env(N)]
set_property verilog_define $defs [get_filesets sources_1]
set_property verilog_define $defs [get_filesets sim_1]

# Set top for simulation
set_property top tb_top_gemm [get_filesets sim_1]

# Launch behavioral simulation
launch_simulation
run all
close_sim
