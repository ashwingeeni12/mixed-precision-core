module dp_bram #(
  parameter WIDTH = 32,
  parameter DEPTH = 16384,
  parameter INIT_FILE = "",
  parameter DBG_READ_PORT = 0
)(
  input  logic               clka, ena, wea,
  input  logic [$clog2(DEPTH)-1:0] addra,
  input  logic [WIDTH-1:0]   dina,
  output logic [WIDTH-1:0]   douta,

  input  logic               clkb, enb, web,
  input  logic [$clog2(DEPTH)-1:0] addrb,
  input  logic [WIDTH-1:0]   dinb,
  output logic [WIDTH-1:0]   doutb,

  // Optional third debug read port for simulation-only readback (C buffer dump)
  input  logic               dbg_en,
  input  logic [$clog2(DEPTH)-1:0] dbg_addr,
  output logic [WIDTH-1:0]   dbg_dout
);
  logic [WIDTH-1:0] mem [0:DEPTH-1];

  initial begin
    if (INIT_FILE != "") begin
      $readmemh(INIT_FILE, mem);
    end
  end

  // Port A
  always_ff @(posedge clka) begin
    if (ena) begin
      if (wea) mem[addra] <= dina;
      douta <= mem[addra];
    end
  end
  // Port B
  always_ff @(posedge clkb) begin
    if (enb) begin
      if (web) mem[addrb] <= dinb;
      doutb <= mem[addrb];
    end
  end

  // Debug read port
  generate if (DBG_READ_PORT) begin : g_dbg
    always_ff @(posedge clka) begin
      if (dbg_en) dbg_dout <= mem[dbg_addr];
    end
  end else begin : g_nodbg
    assign dbg_dout = '0;
  end endgenerate
endmodule
