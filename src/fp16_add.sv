// fp16_add.sv (dual-mode wrapper)
// If your IP exposes s_axis_operation, define HAVE_FP_OP (add +define+HAVE_FP_OP in Vivado)
// We'll tie operation to 'Add' (00 per PG060 convention; adjust if needed).
module fp16_add(
  input  logic        clk,
  input  logic        rstn,
  input  logic        valid,
  input  logic [15:0] a,
  input  logic [15:0] b,
  output logic [15:0] y,
  output logic        ready
);
  logic        s_axis_a_tvalid, s_axis_b_tvalid;
  logic [31:0] s_axis_a_tdata,  s_axis_b_tdata;
  logic        m_axis_result_tvalid;
  logic [31:0] m_axis_result_tdata;

  assign s_axis_a_tvalid = valid;
  assign s_axis_b_tvalid = valid;
  assign s_axis_a_tdata  = {16'b0, a};
  assign s_axis_b_tdata  = {16'b0, b};

`ifdef HAVE_FP_OP
  // Some versions expose an operation port: 0 = Add, 1 = Sub (check your IP doc)
  localparam [7:0] OP_ADD = 8'h00;
  fp16_add_ip u_add (
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
  // No operation port on this IP version
  fp16_add_ip u_add (
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

  assign y     = m_axis_result_tdata[15:0];
  assign ready = m_axis_result_tvalid;
endmodule
