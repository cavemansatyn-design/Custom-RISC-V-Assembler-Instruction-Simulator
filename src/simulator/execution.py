"""
RISC-V RV32I instruction execution.

Executes decoded instructions: updates registers and PC, performs memory access.
x0 is always zero; writes to x0 are ignored.
"""

from typing import Callable
from dataclasses import dataclass

from .decoder import DecodedInstruction
from .memory import Memory


@dataclass
class ExecutionResult:
    """Result of executing one instruction."""
    next_pc: int  # next PC (byte address)
    write_rd: bool  # whether rd was written
    rd_val: int  # value written to rd (if write_rd)
    halt: bool = False
    reset: bool = False


def to_signed32(val: int) -> int:
    """Interpret 32-bit value as signed."""
    return val - (1 << 32) if val >= (1 << 31) else val


def to_unsigned32(val: int) -> int:
    """Ensure value fits in 32 bits (unsigned)."""
    return val & 0xFFFF_FFFF


def execute(
    dec: DecodedInstruction,
    pc: int,
    regs: list[int],
    memory: Memory,
) -> ExecutionResult:
    """
    Execute one decoded instruction. regs is list of 32 ints (register values).
    Returns next PC and whether rd was written (and value). x0 is not written.
    """
    rd, rs1, rs2 = dec.rd, dec.rs1, dec.rs2
    v1 = regs[rs1]
    v2 = regs[rs2]
    v1_s = to_signed32(v1)
    v2_s = to_signed32(v2)
    imm = dec.imm

    # SYSTEM: ecall -> halt
    if dec.format_type == "SYSTEM":
        return ExecutionResult(next_pc=pc + 4, write_rd=False, rd_val=0, halt=True)

    # RST: custom reset
    if dec.format_type == "RST":
        return ExecutionResult(next_pc=0, write_rd=False, rd_val=0, reset=True)

    # R-type
    if dec.format_type == "R":
        if dec.funct3 == "000":
            if dec.funct7 == "0000000":
                result = to_unsigned32(v1_s + v2_s)  # add
            else:
                result = to_unsigned32(v1_s - v2_s)  # sub
        elif dec.funct3 == "010":
            result = 1 if v1_s < v2_s else 0  # slt
        elif dec.funct3 == "101":
            shamt = v2 & 0x1F
            result = (v1 & 0xFFFF_FFFF) >> shamt  # srl
        elif dec.funct3 == "110":
            result = (v1 | v2) & 0xFFFF_FFFF  # or
        elif dec.funct3 == "111":
            result = (v1 & v2) & 0xFFFF_FFFF  # and
        else:
            raise ValueError(f"Unknown R-type funct3: {dec.funct3}")
        return ExecutionResult(
            next_pc=pc + 4,
            write_rd=True,
            rd_val=result,
        )

    # I-type: lw, addi, jalr
    if dec.format_type == "I":
        if dec.opcode == "0000011":  # lw
            addr = v1_s + imm
            val = memory.read_word(addr)
            return ExecutionResult(next_pc=pc + 4, write_rd=True, rd_val=val)
        if dec.opcode == "0010011":  # addi
            result = to_unsigned32(v1_s + imm)
            return ExecutionResult(next_pc=pc + 4, write_rd=True, rd_val=result)
        if dec.opcode == "1100111":  # jalr
            link = pc + 4
            target = (v1_s + imm) & ~1
            return ExecutionResult(
                next_pc=target,
                write_rd=True,
                rd_val=to_unsigned32(link),
            )
        raise ValueError(f"Unknown I-type opcode: {dec.opcode}")

    # S-type: sw
    if dec.format_type == "S":
        addr = v1_s + imm
        memory.write_word(addr, v2)
        return ExecutionResult(next_pc=pc + 4, write_rd=False, rd_val=0)

    # B-type
    if dec.format_type == "B":
        take_branch = False
        if dec.funct3 == "000":
            take_branch = v1 == v2  # beq
        elif dec.funct3 == "001":
            take_branch = v1 != v2  # bne
        elif dec.funct3 == "100":
            take_branch = v1_s < v2_s  # blt
        else:
            raise ValueError(f"Unknown B-type funct3: {dec.funct3}")
        next_pc = pc + imm if take_branch else pc + 4
        return ExecutionResult(next_pc=next_pc, write_rd=False, rd_val=0)

    # J-type: jal
    if dec.format_type == "J":
        link = pc + 4
        target = pc + imm
        return ExecutionResult(
            next_pc=target,
            write_rd=True,
            rd_val=to_unsigned32(link),
        )

    raise ValueError(f"Unsupported format: {dec.format_type}")
