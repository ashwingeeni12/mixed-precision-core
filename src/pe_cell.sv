import mp_types::*;

module pe_cell #(
  parameter prec_e PREC = PREC_INT8
)(
  input  logic clk,
  input  logic rstn,
  input  logic valid,
  input  logic [31:0] acc_in,
  input  logic [31:0] a_in,
  input  logic [31:0] b_in,
  output logic [31:0] acc_out
);
  generate
    if (PREC == PREC_INT8) begin : g_int8
      int8_mac u_mac (
        .clk(clk), .rstn(rstn), .valid(valid),
        .a(a_in[7:0]), .b(b_in[7:0]),
        .acc_in(acc_in), .acc_out(acc_out)
      );
    end else if (PREC == PREC_FP16) begin : g_fp16
      // FP16: acc_out = acc_in + (a*b)
      logic [15:0] prod;
      logic        mready, aready;
      fp16_mul u_mul (.clk(clk), .rstn(rstn), .valid(valid), .a(a_in[15:0]), .b(b_in[15:0]), .y(prod), .ready(mready));
      logic [15:0] sum;
      fp16_add u_add (.clk(clk), .rstn(rstn), .valid(mready), .a(acc_in[15:0]), .b(prod), .y(sum), .ready(aready));
      always_ff @(posedge clk) begin
        if (!rstn) acc_out <= '0;
        else if (aready) acc_out <= {16'b0, sum};
      end
    end else begin : g_fp32
      logic [31:0] prod;
      logic        mready, aready;
      fp32_mul u_mul (.clk(clk), .rstn(rstn), .valid(valid), .a(a_in), .b(b_in), .y(prod), .ready(mready));
      fp32_add u_add (.clk(clk), .rstn(rstn), .valid(mready), .a(acc_in), .b(prod), .y(acc_out), .ready(aready));
    end
  endgenerate
endmodule
