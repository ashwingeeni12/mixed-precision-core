# create_fp_ip_min.tcl
# Version-tolerant FP IP creation for Vivado 2025.1 and nearby versions.
# - Only sets parameters that exist across versions.
# - For adders, uses Operation_Type {Add_Subtract} and leaves "Add" vs "Subtract"
#   selection to the AXIS operation input (if present).
# - Your HDL wrapper will tie operation to 'Add' when the port exists.

create_project mp_mm_min ./mp_mm_min -part xc7a200tsbg484-1 -force
set_property target_language Verilog [current_project]

# FP16 Multiply
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp16_mul_ip
set_property -dict [list \
  CONFIG.Operation_Type {Multiply} \
  CONFIG.A_Precision_Type {Half} \
  CONFIG.Result_Precision_Type {Half} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp16_mul_ip]

# FP16 Add/Subtract
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp16_add_ip
set_property -dict [list \
  CONFIG.Operation_Type {Add_Subtract} \
  CONFIG.A_Precision_Type {Half} \
  CONFIG.Result_Precision_Type {Half} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp16_add_ip]

# FP32 Multiply
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp32_mul_ip
set_property -dict [list \
  CONFIG.Operation_Type {Multiply} \
  CONFIG.A_Precision_Type {Single} \
  CONFIG.Result_Precision_Type {Single} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp32_mul_ip]

# FP32 Add/Subtract
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp32_add_ip
set_property -dict [list \
  CONFIG.Operation_Type {Add_Subtract} \
  CONFIG.A_Precision_Type {Single} \
  CONFIG.Result_Precision_Type {Single} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp32_add_ip]

generate_target all [get_ips]

puts "FP IP created with minimal settings. If the adder exposes s_axis_operation, your wrapper must tie it to 'Add'."
