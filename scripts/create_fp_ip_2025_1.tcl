# create_fp_ip_2025_1.tcl
# Vivado 2025.1–compatible Floating-Point IP creation
# - Uses Operation_Type {Multiply} for mul
# - Uses Operation_Type {Add_Subtract} for add (fixed 'Add' mode)
# - Avoids setting disabled C_Latency parameters (Vivado chooses pipeline automatically)
# - Keeps AXIS style, NonBlocking flow, aresetn enabled

create_project mp_mm_2025_1 ./mp_mm_2025_1 -part xc7a200tsbg484-1 -force
set_property target_language Verilog [current_project]

# ---------- FP16 cores ----------
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp16_mul_ip
set_property -dict [list \
  CONFIG.Operation_Type {Multiply} \
  CONFIG.A_Precision_Type {Half} \
  CONFIG.Result_Precision_Type {Half} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp16_mul_ip]

create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp16_add_ip
# In 2025.1, addition is 'Add_Subtract'. We'll fix it to Add and avoid an operation input.
set_property -dict [list \
  CONFIG.Operation_Type {Add_Subtract} \
  CONFIG.Add_Sub_Value {Add} \
  CONFIG.Has_ADD {true} \
  CONFIG.Has_SUB {false} \
  CONFIG.Has_OPERATION {false} \
  CONFIG.A_Precision_Type {Half} \
  CONFIG.Result_Precision_Type {Half} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp16_add_ip]

# ---------- FP32 cores ----------
create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp32_mul_ip
set_property -dict [list \
  CONFIG.Operation_Type {Multiply} \
  CONFIG.A_Precision_Type {Single} \
  CONFIG.Result_Precision_Type {Single} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp32_mul_ip]

create_ip -name floating_point -vendor xilinx.com -library ip -module_name fp32_add_ip
set_property -dict [list \
  CONFIG.Operation_Type {Add_Subtract} \
  CONFIG.Add_Sub_Value {Add} \
  CONFIG.Has_ADD {true} \
  CONFIG.Has_SUB {false} \
  CONFIG.Has_OPERATION {false} \
  CONFIG.A_Precision_Type {Single} \
  CONFIG.Result_Precision_Type {Single} \
  CONFIG.Flow_Control {NonBlocking} \
  CONFIG.Has_ARESETn {true}] [get_ips fp32_add_ip]

generate_target all [get_ips]
puts "Floating-point IP generated for Vivado 2025.1."
