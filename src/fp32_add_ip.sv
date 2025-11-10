// Behavioral model of Xilinx FP32 Adder IP
// Implements IEEE 754 single-precision (32-bit) floating-point addition

module fp32_add_ip (
  input  logic        aclk,
  input  logic        aresetn,
  input  logic        s_axis_a_tvalid,
  input  logic [31:0] s_axis_a_tdata,
  input  logic        s_axis_b_tvalid,
  input  logic [31:0] s_axis_b_tdata,
  output logic        m_axis_result_tvalid,
  output logic [31:0] m_axis_result_tdata
);

  // Pipeline stages for realistic latency
  logic [31:0] pipe_a[2];
  logic [31:0] pipe_b[2];
  logic        pipe_valid[2];

  // Add using real for accurate IEEE 754 behavior
  shortreal a_real, b_real, result_real;
  logic [31:0] result_fp32;

  always_ff @(posedge aclk or negedge aresetn) begin
    if (!aresetn) begin
      pipe_valid[0] <= 1'b0;
      pipe_valid[1] <= 1'b0;
      m_axis_result_tvalid <= 1'b0;
      m_axis_result_tdata <= 32'h0;
    end else begin
      // Stage 0: Input
      pipe_a[0] <= s_axis_a_tdata;
      pipe_b[0] <= s_axis_b_tdata;
      pipe_valid[0] <= s_axis_a_tvalid & s_axis_b_tvalid;

      // Stage 1: Convert to real and add
      pipe_a[1] <= pipe_a[0];
      pipe_b[1] <= pipe_b[0];
      pipe_valid[1] <= pipe_valid[0];

      // Stage 2: Output
      if (pipe_valid[1]) begin
        // Convert FP32 to real and add
        a_real = $bitstoshortreal(pipe_a[1]);
        b_real = $bitstoshortreal(pipe_b[1]);
        result_real = a_real + b_real;
        result_fp32 = $shortrealtobits(result_real);

        m_axis_result_tdata <= result_fp32;
        m_axis_result_tvalid <= 1'b1;
      end else begin
        m_axis_result_tvalid <= 1'b0;
      end
    end
  end

endmodule
