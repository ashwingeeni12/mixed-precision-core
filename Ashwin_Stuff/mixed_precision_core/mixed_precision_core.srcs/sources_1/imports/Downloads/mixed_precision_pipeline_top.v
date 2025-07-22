
`timescale 1ns / 1ps

package mp_isa_pkg;
    typedef enum logic [1:0] {
        PREC_INT8  = 2'b00,
        PREC_FP16  = 2'b01,
        PREC_FP32  = 2'b10
    } prec_e;

    typedef enum logic [3:0] {
        OP_ADD  = 4'b0000,
        OP_SUB  = 4'b0001,
        OP_MUL  = 4'b0010,
        OP_AND  = 4'b0011,
        OP_OR   = 4'b0100,
        OP_XOR  = 4'b0101,
        OP_CMP  = 4'b0110,
        OP_NOP  = 4'b1111
    } opcode_e;
endpackage : mp_isa_pkg

import mp_isa_pkg::*;

module mixed_precision_core #(
    parameter DATA_W         = 32,
    parameter REG_ADDR_W     = 5,
    parameter IMEM_DEPTH     = 1024,
    parameter DMEM_DEPTH     = 1024
)(
    input  logic              clk,
    input  logic              rst,
    output logic [REG_ADDR_W-1:0] imem_addr,
    input  logic [DATA_W-1:0]      imem_rdata,
    output logic [REG_ADDR_W-1:0] dmem_addr,
    output logic                  dmem_we,
    output logic [DATA_W-1:0]      dmem_wdata,
    input  logic [DATA_W-1:0]      dmem_rdata
);

    typedef struct packed {
        logic [DATA_W-1:0] instr;
        logic [31:0]       pc;
    } if_id_t;

    typedef struct packed {
        logic [DATA_W-1:0] instr;
        logic [31:0]       pc;
        logic [DATA_W-1:0] rs1_data;
        logic [DATA_W-1:0] rs2_data;
    } id_ex_t;

    typedef struct packed {
        logic [DATA_W-1:0] alu_result;
        logic [REG_ADDR_W-1:0] rd;
        logic              rd_we;
    } ex_mem_t;

    typedef struct packed {
        logic [DATA_W-1:0] mem_data;
        logic [DATA_W-1:0] alu_result;
        logic [REG_ADDR_W-1:0] rd;
        logic              rd_we;
    } mem_wb_t;

    if_id_t  if_id_q,  if_id_d;
    id_ex_t  id_ex_q,  id_ex_d;
    ex_mem_t ex_mem_q, ex_mem_d;
    mem_wb_t mem_wb_q, mem_wb_d;

    if_stage #( .DATA_W(DATA_W), .IMEM_DEPTH(IMEM_DEPTH) ) u_if (
        .clk       (clk),
        .rst       (rst),
        .stall     (1'b0),
        .pc_next   (),
        .imem_addr (imem_addr),
        .imem_rdata(imem_rdata),
        .if_id_d   (if_id_d)
    );

    id_stage #(
        .DATA_W(DATA_W), .REG_ADDR_W(REG_ADDR_W)
    ) u_id (
        .clk       (clk),
        .rst       (rst),
        .if_id_q   (if_id_q),
        .id_ex_d   (id_ex_d)
    );

    ex_stage #(
        .DATA_W(DATA_W), .REG_ADDR_W(REG_ADDR_W)
    ) u_ex (
        .clk       (clk),
        .rst       (rst),
        .id_ex_q   (id_ex_q),
        .ex_mem_d  (ex_mem_d)
    );

    mem_stage #(
        .DATA_W(DATA_W), .DMEM_DEPTH(DMEM_DEPTH)
    ) u_mem (
        .clk       (clk),
        .rst       (rst),
        .ex_mem_q  (ex_mem_q),
        .dmem_addr (dmem_addr),
        .dmem_we   (dmem_we),
        .dmem_wdata(dmem_wdata),
        .dmem_rdata(dmem_rdata),
        .mem_wb_d  (mem_wb_d)
    );

    wb_stage #(
        .DATA_W(DATA_W), .REG_ADDR_W(REG_ADDR_W)
    ) u_wb (
        .clk      (clk),
        .rst      (rst),
        .mem_wb_q (mem_wb_q)
    );

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            if_id_q  <= '0;
            id_ex_q  <= '0;
            ex_mem_q <= '0;
            mem_wb_q <= '0;
        end else begin
            if_id_q  <= if_id_d;
            id_ex_q  <= id_ex_d;
            ex_mem_q <= ex_mem_d;
            mem_wb_q <= mem_wb_d;
        end
    end

endmodule : mixed_precision_core

module if_stage #(parameter DATA_W = 32, parameter IMEM_DEPTH = 1024)(
    input  logic                 clk,
    input  logic                 rst,
    input  logic                 stall,
    input  logic [31:0]          pc_next,
    output logic [$clog2(IMEM_DEPTH)-1:0] imem_addr,
    input  logic [DATA_W-1:0]    imem_rdata,
    output mixed_precision_core.if_id_t if_id_d
);

endmodule : if_stage

module id_stage #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic                 clk,
    input  logic                 rst,
    input  mixed_precision_core.if_id_t if_id_q,
    output mixed_precision_core.id_ex_t id_ex_d
);

endmodule : id_stage

module ex_stage #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic                 clk,
    input  logic                 rst,
    input  mixed_precision_core.id_ex_t id_ex_q,
    output mixed_precision_core.ex_mem_t ex_mem_d
);

endmodule : ex_stage

module mem_stage #(parameter DATA_W = 32, parameter DMEM_DEPTH = 1024)(
    input  logic                 clk,
    input  logic                 rst,
    input  mixed_precision_core.ex_mem_t ex_mem_q,
    output logic [$clog2(DMEM_DEPTH)-1:0] dmem_addr,
    output logic                 dmem_we,
    output logic [DATA_W-1:0]    dmem_wdata,
    input  logic [DATA_W-1:0]    dmem_rdata,
    output mixed_precision_core.mem_wb_t mem_wb_d
);

endmodule : mem_stage

module wb_stage #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic                 clk,
    input  logic                 rst,
    input  mixed_precision_core.mem_wb_t mem_wb_q
);

endmodule : wb_stage

module reg_file #(parameter DATA_W = 32, parameter REG_ADDR_W = 5)(
    input  logic                 clk,
    input  logic                 rst,
    input  logic                 we,
    input  logic [REG_ADDR_W-1:0] waddr,
    input  logic [DATA_W-1:0]     wdata,
    input  logic [REG_ADDR_W-1:0] raddr1,
    input  logic [REG_ADDR_W-1:0] raddr2,
    output logic [DATA_W-1:0]     rdata1,
    output logic [DATA_W-1:0]     rdata2
);
endmodule : reg_file
