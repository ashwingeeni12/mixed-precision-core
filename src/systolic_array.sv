import mp_types::*;

module systolic_array #(
  parameter int N = 4,
  parameter prec_e PREC = PREC_INT8
)(
  input  logic clk,
  input  logic rstn,
  input  logic valid,
  input  logic [N*32-1:0] a_row,   // N lanes (each 32 bits holding the active precision)
  input  logic [N*32-1:0] b_col,   // N lanes
  input  logic [N*32-1:0] acc_in [N],
  output logic [N*32-1:0] acc_out[N]
);
  genvar i,j;
  for (i=0;i<N;i++) begin: row
    for (j=0;j<N;j++) begin: col
      pe_cell #(.PREC(PREC)) u_pe (
        .clk(clk), .rstn(rstn), .valid(valid),
        .acc_in(acc_in[i][(j+1)*32-1 -: 32]),
        .a_in(a_row[(j+1)*32-1 -: 32]),
        .b_in(b_col[(i+1)*32-1 -: 32]),
        .acc_out(acc_out[i][(j+1)*32-1 -: 32])
      );
    end
  end
endmodule
