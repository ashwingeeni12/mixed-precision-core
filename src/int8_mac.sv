module int8_mac (
  input  logic         clk,
  input  logic         rstn,
  input  logic         valid,
  input  logic  [7:0]  a,
  input  logic  [7:0]  b,
  input  logic  [31:0] acc_in,
  output logic  [31:0] acc_out
);
  logic signed [15:0] prod;
  assign prod = $signed(a) * $signed(b);

  always_ff @(posedge clk) begin
    if (!rstn) acc_out <= '0;
    else if (valid) acc_out <= acc_in + $signed(prod);
  end
endmodule
