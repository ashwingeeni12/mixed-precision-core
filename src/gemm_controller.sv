import mp_types::*;

module gemm_controller #(
  parameter int MAX_ELEMS = 16384,
  parameter prec_e PREC = PREC_INT8
)(
  input  logic        clk,
  input  logic        rstn,
  input  logic        start,
  input  logic [15:0] M, K, Ncols,   // A(MxK) * B(KxN) = C(MxN)
  output logic        done,

  // BRAM ports (one read port each for A and B; one write for C)
  output logic [$clog2(MAX_ELEMS)-1:0] addr_A,
  input  logic [31:0]                  data_A,
  output logic [$clog2(MAX_ELEMS)-1:0] addr_B,
  input  logic [31:0]                  data_B,
  output logic [$clog2(MAX_ELEMS)-1:0] addr_C,
  output logic [31:0]                  data_C,
  output logic                         we_C
);
  typedef enum logic [2:0] {S_IDLE, S_LOAD, S_READ, S_MAC, S_STORE, S_NEXT, S_DONE} state_e;
  state_e s;

  logic [31:0] acc;
  logic [15:0] i,j,k;
  logic [31:0] a_reg, b_reg;
  logic [31:0] acc_next;

  // Row-major A(MxK), B(KxN), C(MxN)
  function automatic [$clog2(MAX_ELEMS)-1:0] idx_A(input int r, input int c);
    return r*K + c;
  endfunction
  function automatic [$clog2(MAX_ELEMS)-1:0] idx_B(input int r, input int c);
    return r*Ncols + c;
  endfunction
  function automatic [$clog2(MAX_ELEMS)-1:0] idx_C(input int r, input int c);
    return r*Ncols + c;
  endfunction

  pe_cell #(.PREC(PREC)) u_pe (
    .clk(clk), .rstn(rstn), .valid(s==S_MAC),
    .acc_in(acc), .a_in(a_reg), .b_in(b_reg), .acc_out(acc_next)
  );

  always_ff @(posedge clk) begin
    if (!rstn) begin
      s    <= S_IDLE; done <= 1'b0; we_C <= 1'b0;
      i<='0; j<='0; k<='0; acc<='0; a_reg<='0; b_reg<='0;
    end else begin
      we_C <= 1'b0; done <= 1'b0;
      unique case (s)
        S_IDLE: if (start) begin i<=0; j<=0; k<=0; acc<='0; s<=S_LOAD; end
        S_LOAD: begin
          addr_A <= idx_A(i,k);
          addr_B <= idx_B(k,j);
          s <= S_READ;
        end
        S_READ: begin
          // capture outputs from BRAMs (1-cycle sync read)
          a_reg <= data_A;
          b_reg <= data_B;
          s <= S_MAC;
        end
        S_MAC: begin
          acc <= acc_next;
          if (k+1 < K) begin
            k <= k+1;
            s <= S_LOAD;
          end else begin
            s <= S_STORE;
          end
        end
        S_STORE: begin
          addr_C <= idx_C(i,j);
          data_C <= acc_next;
          we_C   <= 1'b1;
          s <= S_NEXT;
        end
        S_NEXT: begin
          acc <= '0; k <= 0;
          if (j+1 < Ncols) begin j <= j+1; s <= S_LOAD; end
          else if (i+1 < M) begin j <= 0; i <= i+1; s <= S_LOAD; end
          else begin s <= S_DONE; end
        end
        S_DONE: begin done <= 1'b1; s <= S_IDLE; end
      endcase
    end
  end
endmodule
