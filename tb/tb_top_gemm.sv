`timescale 1ns/1ps
// Include simulation defines for M, K, N, PREC_SEL parameters
`include "sim_defines.vh"
// mp_types.sv is already compiled separately - just import the package
import mp_types::*;

module tb_top_gemm;
  logic clk=0, rstn=0, start=0; always #5 clk=~clk; // 100 MHz sim

  // Allow defines from TCL to set precision and sizes
  localparam prec_e PREC = default_prec();

  `ifndef M
    localparam int M = 4;
  `else
    localparam int M = `M;
  `endif
  `ifndef K
    localparam int K = 4;
  `else
    localparam int K = `K;
  `endif
  `ifndef N
    localparam int Ncols = 4;
  `else
    localparam int Ncols = `N;
  `endif

  logic done;
  logic        c_dbg_en;
  logic [$clog2(65536)-1:0] c_dbg_addr;
  logic [31:0]              c_dbg_dout;

  top_gemm #(.PREC(PREC)) dut (
    .clk(clk), .rstn(rstn), .start(start), .M(M), .K(K), .Ncols(Ncols), .done(done),
    .c_dbg_en(c_dbg_en), .c_dbg_addr(c_dbg_addr), .c_dbg_dout(c_dbg_dout)
  );

  integer fhex, r, c;

  initial begin
    $display("TB start");
    c_dbg_en = 1'b0; c_dbg_addr = '0;
    repeat (5) @(posedge clk);
    rstn = 1;
    repeat (5) @(posedge clk);
    start = 1; @(posedge clk); start = 0;
    wait(done==1);

    // Dump C to HEX (mem/C_out.mem)
    $display("Attempting to open output file...");
    fhex = $fopen("C_out.mem","w");  // Try writing to current directory first
    if (fhex == 0) begin
      $display("ERROR: Could not open C_out.mem in current directory!");
      $display("Trying: ../mem/C_out.mem");
      fhex = $fopen("../mem/C_out.mem","w");
      if (fhex == 0) begin
        $display("ERROR: Could not open ../mem/C_out.mem!");
        $display("Trying: mem/C_out.mem");
        fhex = $fopen("mem/C_out.mem","w");
        if (fhex == 0) begin
          $display("ERROR: Could not open any path!");
          $finish;
        end
      end
    end
    $display("File opened successfully, writing %0d x %0d matrix...", M, Ncols);

    // Wait one extra cycle before first read to account for BRAM latency
    c_dbg_en   = 1'b1;
    c_dbg_addr = 0;
    @(posedge clk);

    for (r=0; r<M; r=r+1) begin
      for (c=0; c<Ncols; c=c+1) begin
        automatic int idx = r*Ncols + c;
        // Set address for next read
        if (idx < M*Ncols - 1) begin
          c_dbg_addr = idx + 1;
        end
        @(posedge clk);
        // Write current data (from previous address setup)
        $fwrite(fhex, "%08x\n", c_dbg_dout);
      end
    end
    $fflush(fhex);  // Ensure data is written
    $fclose(fhex);

    $display("Dump complete");
    $finish;
  end
endmodule
