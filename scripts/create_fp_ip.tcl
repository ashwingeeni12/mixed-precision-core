# Create Floating-Point IP cores for FP16/FP32 add/mul.
# Adjust IP version if Vivado warns; names are set to match the HDL wrappers.

create_project mp_mm ./mp_mm -part xc7a200tsbg484-1
set_property target_language Verilog [current_project]

# FP16 Multiplier
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp16_mul_ip
set_property -dict [list \
  CONFIG.Operation_Type {Multiply} \
  CONFIG.A_Precision_Type {Half} \
  CONFIG.C_Latency {3} \
  CONFIG.Has_ARESETn {true} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Result_Precision_Type {Half}] [get_ips fp16_mul_ip]

# FP16 Adder
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp16_add_ip
set_property -dict [list \
  CONFIG.Operation_Type {Add} \
  CONFIG.A_Precision_Type {Half} \
  CONFIG.C_Latency {3} \
  CONFIG.Has_ARESETn {true} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Result_Precision_Type {Half}] [get_ips fp16_add_ip]

# FP32 Multiplier
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp32_mul_ip
set_property -dict [list \
  CONFIG.Operation_Type {Multiply} \
  CONFIG.A_Precision_Type {Single} \
  CONFIG.C_Latency {4} \
  CONFIG.Has_ARESETn {true} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Result_Precision_Type {Single}] [get_ips fp32_mul_ip]

# FP32 Adder
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp32_add_ip
set_property -dict [list \
  CONFIG.Operation_Type {Add} \
  CONFIG.A_Precision_Type {Single} \
  CONFIG.C_Latency {4} \
  CONFIG.Has_ARESETn {true} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Result_Precision_Type {Single}] [get_ips fp32_add_ip]

generate_target all [get_ips]
puts "Floating-point IP generated."
