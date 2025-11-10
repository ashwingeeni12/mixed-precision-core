SIZES?=4x4x4 8x8x8
PRECS?=int8 fp16 fp32

ip:
	vivado -mode batch -source scripts/create_fp_ip.tcl

run-batch:
	python3 host/run_batch.py

synth-int8:
	PREC_SEL=0 vivado -mode batch -source scripts/run_synth.tcl
synth-fp16:
	PREC_SEL=1 vivado -mode batch -source scripts/run_synth.tcl
synth-fp32:
	PREC_SEL=2 vivado -mode batch -source scripts/run_synth.tcl
