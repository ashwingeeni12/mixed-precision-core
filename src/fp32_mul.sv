module fp32_mul(
  input  logic        clk,
  input  logic        rstn,
  input  logic        valid,
  input  logic [31:0] a,
  input  logic [31:0] b,
  output logic [31:0] y,
  output logic        ready
);
  // Xilinx Floating-Point Multiplier IP with AXIS interfaces
  // IP core name assumed: fp32_mul_ip
  logic        s_axis_a_tvalid, s_axis_b_tvalid;
  logic [31:0] s_axis_a_tdata,  s_axis_b_tdata;
  logic        m_axis_result_tvalid;
  logic [31:0] m_axis_result_tdata;

  assign s_axis_a_tvalid = valid;
  assign s_axis_b_tvalid = valid;
  assign s_axis_a_tdata  = a;
  assign s_axis_b_tdata  = b;

  fp32_mul_ip u_mul (
    .aclk(clk),
    .aresetn(rstn),
    .s_axis_a_tvalid(s_axis_a_tvalid),
    .s_axis_a_tdata (s_axis_a_tdata),
    .s_axis_b_tvalid(s_axis_b_tvalid),
    .s_axis_b_tdata (s_axis_b_tdata),
    .m_axis_result_tvalid(m_axis_result_tvalid),
    .m_axis_result_tdata (m_axis_result_tdata)
  );

  assign y     = m_axis_result_tdata;
  assign ready = m_axis_result_tvalid;
endmodule
