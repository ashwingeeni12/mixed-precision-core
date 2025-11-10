import mp_types::*;

module top_gemm #(
  parameter int MAX_ELEMS = 65536,
  parameter prec_e PREC = PREC_INT8,
  parameter string A_INIT = "mem/A.mem",
  parameter string B_INIT = "mem/B.mem"
)(
  input  logic clk,
  input  logic rstn,
  input  logic start,
  input  logic [15:0] M, K, Ncols,
  output logic done,
  // debug readback for C
  input  logic        c_dbg_en,
  input  logic [$clog2(MAX_ELEMS)-1:0] c_dbg_addr,
  output logic [31:0] c_dbg_dout
);
  logic [$clog2(MAX_ELEMS)-1:0] addr_A, addr_B, addr_C;
  logic [31:0] data_A, data_B, data_C;
  logic we_C;

  dp_bram #(.WIDTH(32), .DEPTH(MAX_ELEMS), .INIT_FILE(A_INIT), .DBG_READ_PORT(0)) u_A (
    .clka(clk), .ena(1'b1), .wea(1'b0), .addra(addr_A), .dina('0), .douta(data_A),
    .clkb(clk), .enb(1'b0), .web(1'b0), .addrb('0), .dinb('0), .doutb(),
    .dbg_en(1'b0), .dbg_addr('0), .dbg_dout()
  );

  dp_bram #(.WIDTH(32), .DEPTH(MAX_ELEMS), .INIT_FILE(B_INIT), .DBG_READ_PORT(0)) u_B (
    .clka(clk), .ena(1'b1), .wea(1'b0), .addra(addr_B), .dina('0), .douta(data_B),
    .clkb(clk), .enb(1'b0), .web(1'b0), .addrb('0), .dinb('0), .doutb(),
    .dbg_en(1'b0), .dbg_addr('0), .dbg_dout()
  );

  dp_bram #(.WIDTH(32), .DEPTH(MAX_ELEMS), .INIT_FILE(""), .DBG_READ_PORT(1)) u_C (
    .clka(clk), .ena(1'b1), .wea(we_C), .addra(addr_C), .dina(data_C), .douta(),
    .clkb(clk), .enb(1'b0), .web(1'b0), .addrb('0), .dinb('0), .doutb(),
    .dbg_en(c_dbg_en), .dbg_addr(c_dbg_addr), .dbg_dout(c_dbg_dout)
  );

  gemm_controller #(.PREC(PREC)) u_ctrl (
    .clk(clk), .rstn(rstn), .start(start), .M(M), .K(K), .Ncols(Ncols),
    .done(done),
    .addr_A(addr_A), .data_A(data_A),
    .addr_B(addr_B), .data_B(data_B),
    .addr_C(addr_C), .data_C(data_C), .we_C(we_C)
  );
endmodule
