//============================================================
//  mixed_precision_pipeline_top.sv 
//  Ashwin Geeni  |  July 2025
//============================================================
`timescale 1ns / 1ps

package mp_isa_pkg;
    typedef enum logic [1:0] {
        PREC_INT8 = 2'b00,
        PREC_FP16 = 2'b01,
        PREC_FP32 = 2'b10
    } prec_e;

    typedef enum logic [3:0] {
        OP_ADD   = 4'b0000,
        OP_SUB   = 4'b0001,
        OP_MUL   = 4'b0010,
        OP_MAC   = 4'b0011,
        OP_LOGIC = 4'b0100,
        OP_LOAD  = 4'b0101,
        OP_STORE = 4'b0110,
        OP_BR    = 4'b0111,
        OP_NOP   = 4'b1111
    } opcode_e;
endpackage : mp_isa_pkg

// ------------------------------------------------------------
// 1. Global structs & constants
// ------------------------------------------------------------
localparam int DATA_W      = 32;
localparam int REG_ADDR_W  = 5;

typedef struct packed { logic [DATA_W-1:0] instr; logic [31:0] pc; } if_id_t;

typedef struct packed {
    logic [DATA_W-1:0] instr;
    logic [31:0]       pc;
    logic [DATA_W-1:0] rs1_data;
    logic [DATA_W-1:0] rs2_data;
    logic [REG_ADDR_W-1:0] rd;
} id_ex_t;

typedef struct packed { logic [DATA_W-1:0] alu_result; logic [REG_ADDR_W-1:0] rd; logic rd_we; } ex_mem_t;

typedef struct packed { logic [DATA_W-1:0] wb_data; logic [REG_ADDR_W-1:0] rd; logic rd_we; } mem_wb_t;

// ------------------------------------------------------------
// 2. Register File with byte-lane enables (INT8/FP16 aware)
// ------------------------------------------------------------
module reg_file #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic                 clk,
    input  logic                 rst,

    // Write port
    input  logic                 we,
    input  logic [REG_ADDR_W-1:0] waddr,
    input  logic [DATA_W-1:0]     wdata,
    input  logic [3:0]            byte_en,   // 1 bit per byte

    // Two read ports
    input  logic [REG_ADDR_W-1:0] raddr1,
    input  logic [REG_ADDR_W-1:0] raddr2,
    output logic [DATA_W-1:0]     rdata1,
    output logic [DATA_W-1:0]     rdata2
);
    logic [7:0] mem [0:(1<<REG_ADDR_W)-1][0:3]; // 32 regs × 4 bytes

    // Write
    always_ff @(posedge clk) begin
        if (we) begin
            if (byte_en[0]) mem[waddr][0] <= wdata[7:0];
            if (byte_en[1]) mem[waddr][1] <= wdata[15:8];
            if (byte_en[2]) mem[waddr][2] <= wdata[23:16];
            if (byte_en[3]) mem[waddr][3] <= wdata[31:24];
        end
    end

    // Read (combinational)
    always_comb begin
        rdata1 = {mem[raddr1][3], mem[raddr1][2], mem[raddr1][1], mem[raddr1][0]};
        rdata2 = {mem[raddr2][3], mem[raddr2][2], mem[raddr2][1], mem[raddr2][0]};
    end

endmodule : reg_file

// ------------------------------------------------------------
// 3. Top-level core - now includes RF instance & WB stage wiring
// ------------------------------------------------------------
import mp_isa_pkg::*;

module mixed_precision_core #(
    parameter IMEM_DEPTH = 1024,
    parameter DMEM_DEPTH = 1024
)(
    input  logic                         clk,
    input  logic                         rst,

    // Simple memory ports
    output logic [$clog2(IMEM_DEPTH)-1:0] imem_addr,
    input  logic [DATA_W-1:0]             imem_rdata,

    output logic [$clog2(DMEM_DEPTH)-1:0] dmem_addr,
    output logic                          dmem_we,
    output logic [DATA_W-1:0]             dmem_wdata,
    input  logic [DATA_W-1:0]             dmem_rdata
);

    // Pipeline regs
    if_id_t  if_id_q,  if_id_d;
    id_ex_t  id_ex_q,  id_ex_d;
    ex_mem_t ex_mem_q, ex_mem_d;
    mem_wb_t mem_wb_q, mem_wb_d;

    // --------------------------------------------------------
    // Register file instance
    // --------------------------------------------------------
    logic rf_we;
    logic [3:0] rf_byte_en;
    reg_file #( .DATA_W(DATA_W), .REG_ADDR_W(REG_ADDR_W) ) u_rf (
        .clk    (clk),
        .rst    (rst),
        .we     (rf_we),
        .waddr  (mem_wb_q.rd),
        .wdata  (mem_wb_q.wb_data),
        .byte_en(rf_byte_en),
        .raddr1 (if_id_q.instr[20:16]), // rs1 index
        .raddr2 (if_id_q.instr[15:11]), // rs2 index
        .rdata1 (id_ex_d.rs1_data),
        .rdata2 (id_ex_d.rs2_data)
    );

    // ---- IF stage ----
    if_stage #(
        .DATA_W(DATA_W),
        .IMEM_DEPTH(IMEM_DEPTH)
    ) u_if (
        .clk        (clk),
        .rst        (rst),
        .stall      (1'b0),          // no stalling yet
        .pc_next    ('0),            // branch unit not implemented
        .imem_addr  (imem_addr),
        .imem_rdata (imem_rdata),
        .if_id_d    (if_id_d)
    );

    // ---- ID stage (updated for RF) ----
    id_stage #(
        .DATA_W(DATA_W),
        .REG_ADDR_W(REG_ADDR_W)
    ) u_id (
        .clk      (clk),
        .rst      (rst),
        .if_id_q  (if_id_q),
        .id_ex_d  (id_ex_d)
    );

    // ---- EX stage (intact from Phase 2) ----
    ex_stage #(
        .DATA_W(DATA_W),
        .REG_ADDR_W(REG_ADDR_W)
    ) u_ex (
        .clk      (clk),
        .rst      (rst),
        .id_ex_q  (id_ex_q),
        .ex_mem_d (ex_mem_d)
    );

    // ---- MEM stage (pass-through) ----
    mem_stage #(
        .DATA_W(DATA_W),
        .DMEM_DEPTH(DMEM_DEPTH)
    ) u_mem (
        .clk        (clk),
        .rst        (rst),
        .ex_mem_q   (ex_mem_q),
        .dmem_addr  (dmem_addr),
        .dmem_we    (dmem_we),
        .dmem_wdata (dmem_wdata),
        .dmem_rdata (dmem_rdata),
        .mem_wb_d   (mem_wb_d)
    );

    // ---- WB stage - new ----
    wb_stage #(
        .DATA_W(DATA_W),
        .REG_ADDR_W(REG_ADDR_W)
    ) u_wb (
        .clk        (clk),
        .rst        (rst),
        .mem_wb_q   (mem_wb_q),
        .rf_we      (rf_we),
        .rf_byte_en (rf_byte_en)
    );

    // ---- Sequential pipeline registers ----
    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            if_id_q  <= '0; id_ex_q  <= '0; ex_mem_q <= '0; mem_wb_q <= '0;
        end else begin
            if_id_q  <= if_id_d;
            id_ex_q  <= id_ex_d;
            ex_mem_q <= ex_mem_d;
            mem_wb_q <= mem_wb_d;
        end
    end
endmodule : mixed_precision_core

// ------------------------------------------------------------
// 4. ID stage - now passes rd field
// ------------------------------------------------------------
module id_stage #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic   clk,
    input  logic   rst,
    input  if_id_t if_id_q,
    output id_ex_t id_ex_d
);
    assign id_ex_d.instr    = if_id_q.instr;
    assign id_ex_d.pc       = if_id_q.pc;
    assign id_ex_d.rd       = if_id_q.instr[25:21];
    // rs1_data / rs2_data come from RF combinationally via top-level wiring
endmodule : id_stage

// ------------------------------------------------------------
// 5. EX stage
// ------------------------------------------------------------
module ex_stage #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic   clk,
    input  logic   rst,
    input  id_ex_t id_ex_q,
    output ex_mem_t ex_mem_d
);
    import mp_isa_pkg::*;

    logic [1:0]  prec;    assign prec  = id_ex_q.instr[31:30];
    logic [3:0]  major;   assign major = id_ex_q.instr[29:26];

    // INT8 ALU slice
    logic [7:0] op_a8 = id_ex_q.rs1_data[7:0];
    logic [7:0] op_b8 = id_ex_q.rs2_data[7:0];
    logic [DATA_W-1:0] result_int8;
    always_comb begin
        unique case (major)
            OP_ADD: result_int8 = {{24{1'b0}}, op_a8 + op_b8};
            OP_SUB: result_int8 = {{24{1'b0}}, op_a8 - op_b8};
            OP_MUL: result_int8 = {{16{1'b0}}, op_a8 * op_b8};
            OP_MAC: result_int8 = id_ex_q.rs1_data + {{24{1'b0}}, op_a8 * op_b8};
            default: result_int8 = '0;
        endcase
    end
    logic [DATA_W-1:0] alu_res = (prec == PREC_INT8) ? result_int8 : '0;

    assign ex_mem_d = '{ alu_result : alu_res,
                         rd         : id_ex_q.rd,
                         rd_we      : 1'b1 };
endmodule : ex_stage

// 6. MEM stage - simple pass-through with write-back packaging
// ------------------------------------------------------------
module mem_stage #(parameter DATA_W = 32, parameter DMEM_DEPTH = 1024)(
    input  logic                         clk,
    input  logic                         rst,
    input  ex_mem_t                      ex_mem_q,
    output logic [$clog2(DMEM_DEPTH)-1:0] dmem_addr,
    output logic                         dmem_we,
    output logic [DATA_W-1:0]            dmem_wdata,
    input  logic [DATA_W-1:0]            dmem_rdata,
    output mem_wb_t                      mem_wb_d
);
    // No real memory yet - just pass ALU result forward
    assign dmem_addr  = '0;
    assign dmem_we    = 1'b0;
    assign dmem_wdata = '0;

    assign mem_wb_d = '{ wb_data : ex_mem_q.alu_result,
                         rd      : ex_mem_q.rd,
                         rd_we   : ex_mem_q.rd_we };
endmodule : mem_stage

// ------------------------------------------------------------
// 7. WB stage - writes back to register file
// ------------------------------------------------------------
module wb_stage #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic      clk,
    input  logic      rst,
    input  mem_wb_t   mem_wb_q,
    output logic      rf_we,
    output logic [3:0] rf_byte_en
);
    // For INT8 path, enable only byte 0; later we'll widen for FP16/32.
    assign rf_we      = mem_wb_q.rd_we;
    assign rf_byte_en = 4'b0001;
endmodule : wb_stage