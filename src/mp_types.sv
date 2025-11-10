// Include simulation defines (created by run_xsim.bat)
`include "sim_defines.vh"

package mp_types;
  // Optional external override for default precision via +define+PREC_SEL={0,1,2}
  // 0=INT8, 1=FP16, 2=FP32
  `ifndef PREC_SEL
    `define PREC_SEL 0
  `endif

  typedef enum logic [1:0] {
    PREC_INT8  = 2'b00,
    PREC_FP16  = 2'b01,
    PREC_FP32  = 2'b10
  } prec_e;

  // Map define to enum for easy parameter defaulting
  function automatic prec_e default_prec();
    case (`PREC_SEL)
      0: return PREC_INT8;
      1: return PREC_FP16;
      default: return PREC_FP32;
    endcase
  endfunction

  // Data widths per precision mode
  localparam int W_INT8 = 8;
  localparam int W_FP16 = 16; // IEEE 754 half
  localparam int W_FP32 = 32; // IEEE 754 single

  // Accumulator width for INT8
  localparam int W_ACC_INT8 = 32; // safe for moderate K
endpackage
