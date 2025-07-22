`timescale 1ns/1ps
module tb_core;
   //------------------------------------------------------------------
   // 1. Clock & reset
   //------------------------------------------------------------------
   logic clk = 0;
   logic rst = 1;
   always  #5 clk = ~clk;          // 100 MHz square wave

   //------------------------------------------------------------------
   // 2. ROM
   //------------------------------------------------------------------
   localparam int IMDEP = 1024;    // depth (= words) of dummy ROM
   logic [$clog2(IMDEP)-1:0] imem_addr;
   logic [31:0]              imem_rdata;

   always_comb begin
      unique case (imem_addr)
         0 : imem_rdata = 32'b00_0000_00001_00000_00000_000000; // INT8 ADD R1←R0+R0
         default : imem_rdata = 32'hF000_0000;                  // INT8 NOP
      endcase
   end

   //------------------------------------------------------------------
   // 3. Dummy data-memory interface
   //------------------------------------------------------------------
   logic [$clog2(IMDEP)-1:0] dmem_addr;
   logic                     dmem_we;
   logic [31:0]              dmem_wdata;
   logic [31:0]              dmem_rdata = 32'h0;  // tie reads to zero

   //------------------------------------------------------------------
   // 4. DUT instance
   //------------------------------------------------------------------
   mixed_precision_core #(
       .IMEM_DEPTH(IMDEP),
       .DMEM_DEPTH(IMDEP)
   ) DUT (
       .clk        (clk),
       .rst        (rst),
       .imem_addr  (imem_addr),
       .imem_rdata (imem_rdata),
       .dmem_addr  (dmem_addr),
       .dmem_we    (dmem_we),
       .dmem_wdata (dmem_wdata),
       .dmem_rdata (dmem_rdata)
   );

   //------------------------------------------------------------------
   // 5. Reset release and simulation end
   //------------------------------------------------------------------
   initial begin
      #20  rst = 0;        // release reset at 20 ns
      #500 $finish;        // run for 500 ns total
   end
endmodule
