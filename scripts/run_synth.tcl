# scripts/run_synth.tcl
# Usage: PREC_SEL={0|1|2} vivado -mode batch -source scripts/run_synth.tcl
if {![info exists ::env(PREC_SEL)]} { set ::env(PREC_SEL) 0 }
create_project mp_syn ./mp_syn_$::env(PREC_SEL) -part xc7a200tsbg484-1
set_property target_language Verilog [current_project]
set defs [format "PREC_SEL=%s" $::env(PREC_SEL)]
file mkdir results

read_verilog -sv -define $defs src/*.sv
synth_design -top top_gemm -part xc7a200tsbg484-1
report_utilization -file results/util_prec$::env(PREC_SEL).rpt
report_power -file results/power_prec$::env(PREC_SEL).rpt
