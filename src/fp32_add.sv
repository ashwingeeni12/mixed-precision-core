// fp32_add.sv (dual-mode wrapper)
module fp32_add(
  input  logic        clk,
  input  logic        rstn,
  input  logic        valid,
  input  logic [31:0] a,
  input  logic [31:0] b,
  output logic [31:0] y,
  output logic        ready
);
  logic        s_axis_a_tvalid, s_axis_b_tvalid;
  logic [31:0] s_axis_a_tdata,  s_axis_b_tdata;
  logic        m_axis_result_tvalid;
  logic [31:0] m_axis_result_tdata;

  assign s_axis_a_tvalid = valid;
  assign s_axis_b_tvalid = valid;
  assign s_axis_a_tdata  = a;
  assign s_axis_b_tdata  = b;

`ifdef HAVE_FP_OP
  localparam [7:0] OP_ADD = 8'h00;
  fp32_add_ip u_add (
    .aclk(clk),
    .aresetn(rstn),
    .s_axis_a_tvalid(s_axis_a_tvalid),
    .s_axis_a_tdata (s_axis_a_tdata),
    .s_axis_b_tvalid(s_axis_b_tvalid),
    .s_axis_b_tdata (s_axis_b_tdata),
    .s_axis_operation_tvalid(1'b1),
    .s_axis_operation_tdata (OP_ADD),
    .m_axis_result_tvalid(m_axis_result_tvalid),
    .m_axis_result_tdata (m_axis_result_tdata)
  );
`else
  fp32_add_ip u_add (
    .aclk(clk),
    .aresetn(rstn),
    .s_axis_a_tvalid(s_axis_a_tvalid),
    .s_axis_a_tdata (s_axis_a_tdata),
    .s_axis_b_tvalid(s_axis_b_tvalid),
    .s_axis_b_tdata (s_axis_b_tdata),
    .m_axis_result_tvalid(m_axis_result_tvalid),
    .m_axis_result_tdata (m_axis_result_tdata)
  );
`endif

  assign y     = m_axis_result_tdata;
  assign ready = m_axis_result_tvalid;
endmodule
